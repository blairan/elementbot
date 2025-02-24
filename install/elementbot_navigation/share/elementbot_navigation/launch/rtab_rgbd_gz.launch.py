from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    qos = LaunchConfiguration('qos')
    localization = LaunchConfiguration('localization')

    parameters = {
        'frame_id': 'base_footprint',
        'use_sim_time': use_sim_time,
        'subscribe_depth': True,
        'subscribe_rgb': True,
        'use_action_for_goal': True,
        'qos_image': qos,
        'qos_imu': qos,
        'Reg/Force3DoF': 'true',
        'Optimizer/GravitySigma': '0',
        
        # 同步強化參數
        'approx_sync': True,
        'approx_sync_max_interval': 0.3,
        'queue_size': 100,
        'sync_queue_size': 100,
        'topic_queue_size': 30,
        'wait_for_transform': 0.5, # 增加等待变换的时间
        
        # 時間戳處理
        'use_odom_topic_stamp': False,
        'stamp_ignore_threshold': 0.5,
        'odom_sensor_sync_max_interval': 1.0,
        
        # 點雲處理
        'Grid/MaxGroundAngle': '45',
        'Grid/NormalSegmentation': 'true',
        'Cloud/MaxDepth': '10.0',
        'Cloud/RemoveNaN': 'true',
        
        # 系統調優
        'Mem/NotLinkedNodesKept': 'false',
        'Mem/STMSize': '15',
        'Kp/DetectorStrategy': '6',
        'Vis/CorGuessMatchToProjection': 'true',
        
        # 診斷配置
        'log_quiet': 'false',
        'log_debug': 'false',
        'StatisticLogsEnabled': 'true'
    }


    remappings = [
        ('rgb/image', '/rgbd_camera/image'),
        ('depth/image', '/depth/filtered'),
        ('rgb/camera_info', '/rgbd_camera/camera_info')
    ]

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use simulation (Gazebo) clock if true'),
        
        DeclareLaunchArgument(
            'qos', default_value='2',
            description='QoS used for input sensor topics'),
            
        DeclareLaunchArgument(
            'localization', default_value='false',
            description='Launch in localization mode.'),

        Node(
            condition=UnlessCondition(localization),
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=[parameters],
            remappings=remappings,
            arguments=['-d']),
            
        Node(
            condition=IfCondition(localization),
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=[parameters,
              {'Mem/IncrementalMemory': 'False',
               'Mem/InitWMWithAllNodes': 'True'}],
            remappings=remappings,
        ),

        Node(
            package='rtabmap_viz', executable='rtabmap_viz', output='screen',
            parameters=[parameters],
            remappings=remappings,
        )
    ])
