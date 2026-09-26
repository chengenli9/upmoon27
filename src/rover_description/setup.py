from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'rover_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'description'), glob('description/*.xacro')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='URDF and Xacro descriptions for the rover.',
    license='Apache-2.0',
    extras_require={
        'test': ['pytest'],
    },
)