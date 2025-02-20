import os
import xacro

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

def generate_launch_description():

    #package_name, pkg_path, xacro_file, wolrd_file, robot_description_config
    package_name = 'elementbot_gazebo'
    pkg_path = os.path.join(get_package_share_directory(package_name))
    xacro_file = os.path.join(pkg_path, 'urdf', 'elementbot_4w_diff.xacro')
    world_file = os.path.join(pkg_path, 'world', 'line_follower.sdf')
    robot_description_config = xacro.process_file(xacro_file)

    # Pose where we want to spawn the robot
    spawn_x_val = '2.0'
    spawn_y_val = '-0.1'
    spawn_z_val = '0.0'
    spawn_yaw_val = '0.0'

    # Gazebo Sim
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r ' + world_file}.items(),
    )

    # Run the spawner node from the gazebo_ros package
    spawn_entity = Node(package='ros_gz_sim', 
                        executable='create',
                        arguments=[
                                   '-topic', 'robot_description',
                                   '-name', 'elementbot_4w_diff',
                                   '-x', spawn_x_val,
                                   '-y', spawn_y_val,
                                   '-z', spawn_z_val,
                                   '-Y', spawn_yaw_val,
                                   ],
                        output='screen')
    
     # Create a robot_state_publisher node
    params = {'robot_description': robot_description_config.toxml(), 'use_sim_time': True}
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )
    
    # ros gz bridge
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(get_package_share_directory(package_name), 'config', 'ros_gz_bridge_elementbot_4w_integrate.yaml'),
            'qos_overrides./tf_static.publisher.durability': 'transient_local',
        }],
        output='screen'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
    )

    return LaunchDescription([
        gazebo,
        node_robot_state_publisher,
        joint_state_publisher,
        ros_gz_bridge,
        spawn_entity,
        rviz
    ])