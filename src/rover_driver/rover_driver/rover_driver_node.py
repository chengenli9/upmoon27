#!/usr/bin/env python3
"""
rover_driver: differential-drive base driver for the 4-wheel UPR rover.

Subscribes
  /cmd_vel              geometry_msgs/Twist  linear.x [m/s], angular.z [rad/s]
  /sensor/encoder/left  std_msgs/Int32       raw quadrature counts (arduino_driver)
  /sensor/encoder/right std_msgs/Int32
  /imu/data             sensor_msgs/Imu      optional; used when yaw_source == 'imu'

Publishes
  /odom                 nav_msgs/Odometry    frame odom -> child base_link
  TF odom -> base_link  (if publish_tf)

Motor output follows upmoon25 frontend/drive_motors.py: one Sabertooth per side,
channel 1 = +speed and channel 2 = -speed (mirrored mounting).
"""

import math
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Quaternion, Twist, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from std_msgs.msg import Int32
from tf2_ros import TransformBroadcaster
from pysabertooth import Sabertooth
from serial import SerialException

CONTROL_HZ = 20.0
ODOM_HZ = 30.0
IMU_STALE_SEC = 0.5


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def wrap_angle(a):
    return math.atan2(math.sin(a), math.cos(a))


def yaw_to_quat(yaw):
    q = Quaternion()
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


class SabertoothSide:
    """One Sabertooth controlling one side of the rover."""

    def __init__(self, logger, name, port, address=128):
        self.logger = logger
        self.name = name
        self.port = port
        self.address = address
        self.saber = None
        self.last_sent = None
        self.last_send_t = 0.0
        self._connect()

    def _connect(self):
        try:
            self.saber = Sabertooth(self.port, baudrate=9600, address=self.address, timeout=0.1)
            self.logger.info(f'[{self.name}] Sabertooth on {self.port}')
        except Exception as e:
            self.saber = None
            self.logger.error(f'[{self.name}] cannot open {self.port}: {e}')

    def set_percent(self, pct, force=False):
        # Resend only on change or as a 0.2 s heartbeat to stay within 9600 baud.
        now = time.monotonic()
        if not force and self.last_sent is not None \
                and abs(pct - self.last_sent) < 0.5 and now - self.last_send_t < 0.2:
            return
        if self.saber is None:
            self._connect()
            if self.saber is None:
                return
        try:
            self.saber.drive(1, pct)
            self.saber.drive(2, -pct)
            self.last_sent = pct
            self.last_send_t = now
        except SerialException as e:
            self.logger.warn(f'[{self.name}] serial error: {e}; will reconnect')
            self.saber = None

    def stop(self):
        self.set_percent(0.0, force=True)


class RoverDriver(Node):

    def __init__(self):
        super().__init__('rover_driver')

        # Geometry comes from backend/description/robot_properties.xacro.
        # counts_per_rev and max_wheel_speed are NOT known from the repo; measure them.
        self.declare_parameter('wheel_radius', 0.19)        # m
        self.declare_parameter('track_width', 1.44)         # m, left-to-right wheel centre spacing
        self.declare_parameter('counts_per_rev', 0)         # encoder counts per wheel revolution
        self.declare_parameter('max_wheel_speed', 0.5)      # m/s at 100 % throttle
        self.declare_parameter('left_encoder_sign', 1)      # set -1 if a side counts backwards
        self.declare_parameter('right_encoder_sign', 1)
        self.declare_parameter('left_port', '/dev/ttyACM0')
        self.declare_parameter('right_port', '/dev/ttyACM1')
        self.declare_parameter('max_wheel_accel', 1.0)      # m/s^2 ramp per wheel
        self.declare_parameter('cmd_timeout', 0.5)          # s, zero the command after this
        self.declare_parameter('yaw_source', 'encoders')    # 'encoders' or 'imu'
        self.declare_parameter('publish_tf', True)
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')

        gp = lambda name: self.get_parameter(name).value
        self.r = float(gp('wheel_radius'))
        self.track = float(gp('track_width'))
        self.cpr = int(gp('counts_per_rev'))
        self.max_speed = float(gp('max_wheel_speed'))
        self.enc_sign = {'left': int(gp('left_encoder_sign')), 'right': int(gp('right_encoder_sign'))}
        self.max_accel = float(gp('max_wheel_accel'))
        self.cmd_timeout = float(gp('cmd_timeout'))
        self.yaw_source = str(gp('yaw_source'))
        self.publish_tf = bool(gp('publish_tf'))
        self.odom_frame = str(gp('odom_frame'))
        self.base_frame = str(gp('base_frame'))

        if self.cpr <= 0:
            raise RuntimeError('counts_per_rev must be set (measure it: spin one wheel N turns by hand)')
        if self.max_speed <= 0.0:
            raise RuntimeError('max_wheel_speed must be > 0 (measure it at 100 % throttle)')
        if self.yaw_source not in ('encoders', 'imu'):
            raise RuntimeError("yaw_source must be 'encoders' or 'imu'")

        self.left = SabertoothSide(self.get_logger(), 'Left', str(gp('left_port')))
        self.right = SabertoothSide(self.get_logger(), 'Right', str(gp('right_port')))

        # Command state
        self.target_v = 0.0
        self.target_w = 0.0
        self.last_cmd_t = time.monotonic()
        self.wheel_v = {'left': 0.0, 'right': 0.0}

        # Encoder state
        self.enc_raw = {'left': None, 'right': None}
        self.enc_prev = {'left': None, 'right': None}

        # IMU state (optional)
        self.imu_yaw = None        # yaw relative to the first IMU sample
        self.imu_yaw0 = None
        self.imu_gz = None
        self.imu_t = 0.0

        # Odometry state
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.v_meas = 0.0
        self.w_meas = 0.0
        self.last_odom_t = self.get_clock().now().nanoseconds * 1e-9

        self.create_subscription(Twist, '/cmd_vel', self.on_cmd, 10)
        self.create_subscription(Int32, '/sensor/encoder/left', lambda m: self.on_enc('left', m), 10)
        self.create_subscription(Int32, '/sensor/encoder/right', lambda m: self.on_enc('right', m), 10)
        self.create_subscription(Imu, '/imu/data', self.on_imu, 10)

        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.create_timer(1.0 / CONTROL_HZ, self.control_tick)
        self.create_timer(1.0 / ODOM_HZ, self.odom_tick)

        self.get_logger().info(
            f'rover_driver up: r={self.r} m track={self.track} m cpr={self.cpr} '
            f'vmax={self.max_speed} m/s yaw_source={self.yaw_source}')

    # ---------------- subscriptions ----------------

    def on_cmd(self, msg):
        self.target_v = float(msg.linear.x)
        self.target_w = float(msg.angular.z)
        self.last_cmd_t = time.monotonic()

    def on_enc(self, side, msg):
        self.enc_raw[side] = int(msg.data)

    def on_imu(self, msg):
        q = msg.orientation
        # orientation_covariance[0] == -1 means the IMU does not provide orientation
        if msg.orientation_covariance[0] != -1.0:
            yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
            if self.imu_yaw0 is None:
                self.imu_yaw0 = yaw
            self.imu_yaw = wrap_angle(yaw - self.imu_yaw0)
        self.imu_gz = float(msg.angular_velocity.z)
        self.imu_t = time.monotonic()

    def imu_fresh(self):
        return self.imu_gz is not None and (time.monotonic() - self.imu_t) < IMU_STALE_SEC

    # ---------------- motor control ----------------

    def control_tick(self):
        if time.monotonic() - self.last_cmd_t > self.cmd_timeout:
            v_cmd, w_cmd = 0.0, 0.0
        else:
            v_cmd, w_cmd = self.target_v, self.target_w

        # Differential-drive inverse kinematics: wheel linear speeds in m/s.
        # Positive angular.z (CCW) makes the right side faster than the left.
        v_l = v_cmd - w_cmd * self.track / 2.0
        v_r = v_cmd + w_cmd * self.track / 2.0

        step = self.max_accel / CONTROL_HZ
        for side, tgt in (('left', v_l), ('right', v_r)):
            cur = self.wheel_v[side]
            self.wheel_v[side] = cur + clamp(tgt - cur, -step, step)

        pl = self.wheel_v['left'] / self.max_speed * 100.0
        pr = self.wheel_v['right'] / self.max_speed * 100.0
        peak = max(abs(pl), abs(pr))
        if peak > 100.0:  # keep the turn ratio when one side saturates
            pl *= 100.0 / peak
            pr *= 100.0 / peak

        self.left.set_percent(pl)
        self.right.set_percent(pr)

    # ---------------- odometry ----------------

    def odom_tick(self):
        now = self.get_clock().now()
        t = now.nanoseconds * 1e-9
        dt = t - self.last_odom_t
        if dt <= 0.0:
            return
        self.last_odom_t = t

        # Wheel travel since last tick, from encoder counts.
        dist = {'left': 0.0, 'right': 0.0}
        for side in ('left', 'right'):
            raw = self.enc_raw[side]
            if raw is None:
                continue
            prev = self.enc_prev[side]
            self.enc_prev[side] = raw
            if prev is None:
                continue
            ticks = (raw - prev) * self.enc_sign[side]
            dist[side] = ticks / self.cpr * 2.0 * math.pi * self.r

        ds = 0.5 * (dist['left'] + dist['right'])
        dth_enc = (dist['right'] - dist['left']) / self.track

        th_old = self.th
        if self.yaw_source == 'imu' and self.imu_yaw is not None and self.imu_fresh():
            self.th = self.imu_yaw
            dth = wrap_angle(self.th - th_old)
        else:
            dth = dth_enc
            self.th = wrap_angle(th_old + dth)

        th_mid = th_old + dth / 2.0
        self.x += ds * math.cos(th_mid)
        self.y += ds * math.sin(th_mid)

        self.v_meas = ds / dt
        self.w_meas = self.imu_gz if self.imu_fresh() else dth / dt

        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        q = yaw_to_quat(self.th)
        odom.pose.pose.orientation = q
        odom.twist.twist.linear.x = self.v_meas
        odom.twist.twist.angular.z = self.w_meas

        # Covariance: encoders alone are poor on a skid-steer base (wheels scrub),
        # so yaw variance is much larger than it would be for a car-like robot.
        yaw_var = 0.05 if (self.yaw_source == 'imu' and self.imu_yaw is not None) else 0.5
        pose_cov = [0.0] * 36
        pose_cov[0] = pose_cov[7] = 0.02
        pose_cov[35] = yaw_var
        odom.pose.covariance = pose_cov
        twist_cov = [0.0] * 36
        twist_cov[0] = 0.02
        twist_cov[35] = 0.05 if self.imu_fresh() else 0.5
        odom.twist.covariance = twist_cov

        self.odom_pub.publish(odom)

        if self.publish_tf:
            tf = TransformStamped()
            tf.header = odom.header
            tf.child_frame_id = self.base_frame
            tf.transform.translation.x = self.x
            tf.transform.translation.y = self.y
            tf.transform.rotation = q
            self.tf_broadcaster.sendTransform(tf)


def main(args=None):
    rclpy.init(args=args)
    node = RoverDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.left.stop()
        node.right.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()