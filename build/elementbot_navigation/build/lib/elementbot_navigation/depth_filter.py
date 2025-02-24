#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np
import cv2
from cv_bridge import CvBridge

class DepthFilter(Node):
    def __init__(self):
        super().__init__('depth_filter')
        self.bridge = CvBridge()
        self.sub = self.create_subscription(
            Image, 
            '/rgbd_camera/depth_image',
            self.filter_callback, 
            10)
        self.pub = self.create_publisher(
            Image, 
            '/depth/filtered', 
            10)

    def filter_callback(self, msg):
        try:
            cv_depth = self.bridge.imgmsg_to_cv2(msg, '32FC1')
            
            # 清洗異常值 (NaN/inf)
            cv_depth = np.nan_to_num(cv_depth, nan=0.0, posinf=0.0, neginf=0.0)
            
            # 應用深度範圍過濾
            cv_depth[(cv_depth < 0.15) | (cv_depth > 10.0)] = 0.0
            
            filtered_msg = self.bridge.cv2_to_imgmsg(
                cv_depth, 
                encoding='32FC1',
                header=msg.header)
            self.pub.publish(filtered_msg)
            
        except Exception as e:
            self.get_logger().error(f'數據處理錯誤: {str(e)}')

def main():
    rclpy.init()
    node = DepthFilter()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
