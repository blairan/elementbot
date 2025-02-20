from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription

#包含launch檔案的python檔案

def generate_launch_description():

    # 定義節點
    line_follower_node = Node(
        package='line_follower',
        executable='line_follower',
        name='line_follower_node',
        output='screen'
    )

    # 啟動launch檔案
    display_4w_launch = IncludeLaunchDescription(
        launch_description_source = 'src/elementbot_gazebo/launch/display_4w_diff_urdf_into_gz.launch.py'
    )
    return LaunchDescription([
        line_follower_node,
        display_4w_launch
    ])