#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np

class DepthChecker(Node):
    def __init__(self):
        super().__init__('depth_checker')
        self.sub = self.create_subscription(
            Image,
            '/rgbd_camera/depth_image',
            self.callback, 
            10)

    def callback(self, msg):
        arr = np.frombuffer(msg.data, dtype=np.float32)
    
        # 檢查異常值
        nan_count = np.isnan(arr).sum()
        inf_count = np.isinf(arr).sum()
        
        self.get_logger().warning(
            f'異常值統計 - NaN: {nan_count} | Inf: {inf_count}'
        )
        
        # 過濾異常值後的統計
        valid = arr[(arr > 0.1) & (arr < 10.0) & (~np.isnan(arr)) & (~np.isinf(arr))]
        if len(valid) > 0:
            self.get_logger().info(
                f'有效深度範圍: {np.min(valid):.2f}m - {np.max(valid):.2f}m'
            )

def main():
    rclpy.init()
    node = DepthChecker()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
