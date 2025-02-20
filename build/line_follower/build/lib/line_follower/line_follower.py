#視覺巡線gazebo
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge, CvBridgeError
import numpy as np  # 用於處理數組（顏色範圍）

class LineFollower(Node):
    def __init__(self):
        super().__init__("line_follower_node")
        # 訂閱影像主題
        self.subscription = self.create_subscription(
            Image,
            "/rgbd_camera/image",  # 影像主題
            self.image_callback,
            10)
        self.bridge = CvBridge()

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.deviation = 0  # 偏移量
        self.timer = self.create_timer(0.1, self.timer_callback)  # 定時器

    def timer_callback(self):
        # 根據偏移量計算速度
        msg = Twist()
         # 根據偏移量決定轉向（這裡是簡單邏輯，可改進）
        if self.deviation <= -30:   # 黑線在左邊，左轉
            msg.angular.z = 0.2
        elif self.deviation >= 30:  # 黑線在右邊，右轉
            msg.angular.z = -0.2
        else:                      # 對準黑線，直行
            msg.linear.x = 0.25

        self.publisher.publish(msg)

    def image_callback(self, msg):
        try:
            # 將 ROS 的影像訊息轉換為 OpenCV 格式
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # 將影像轉換為 HSV 色彩空間
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 定義黃色的 HSV 值範圍
            lower_yellow = np.array([20, 100, 100])  # 下界 (Hue, Saturation, Value)
            upper_yellow = np.array([30, 255, 255])  # 上界 (Hue, Saturation, Value)

            # 過濾出黃色物體的遮罩
            mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

            # 找出遮罩中的輪廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) > 0:
                # 找到最大的輪廓
                max_contour = max(contours, key=cv2.contourArea)

                # 計算輪廓的矩
                M = cv2.moments(max_contour)
                if M["m00"] > 0:
                    # 計算輪廓的中心點
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # 繪製中心點
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                    # 繪製輪廓
                    cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)

                    # 計算偏移量（畫面中心為目標）
                    height, width = frame.shape[:2]
                    center_x = width // 2
                    self.deviation = cx - center_x

                    # 在終端輸出偏移量
                    self.get_logger().info(f"偏移量: {self.deviation}")
            
            # 顯示遮罩與處理後的影像
            cv2.imshow("Yellow Mask", mask)
            cv2.imshow("Result Frame", frame)
            cv2.waitKey(1)

        except CvBridgeError as e:
            self.get_logger().error(f"CV Bridge Error: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = LineFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
