from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from vision_msgs.msg import Detection2DArray, ObjectHypothesisWithPose, Detection2D
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import yaml
import numpy as np
import os

class YoloV5Ros2(Node):
    def __init__(self):
        super().__init__('yolov5_ros2')
        
        # 參數聲明
        self.declare_parameters(
            namespace='',
            parameters=[
                ('device', 'cpu'),
                ('model', 'best'),
                ('image_topic', '/rgbd_camera/image'),
                ('camera_info_topic', '/camera/camera_info'),
                ('camera_info_file', os.path.join(get_package_share_directory('yolov5_ros2'), 'config/camera_info.yaml')),
                ('show_result', True),
                ('pub_result_img', False)
            ]
        )

        # 初始化模型
        model_path = os.path.join(
            get_package_share_directory('yolov5_ros2'),
            'config',
            self.get_parameter('model').value + '.pt'
        )
        self.model = YOLO(model_path).to(self.get_parameter('device').value)

        # 初始化OpenCV窗口
        if self.get_parameter('show_result').value:
            cv2.namedWindow('Fall Detection', cv2.WINDOW_NORMAL)
            # 顯示初始黑色背景
            cv2.imshow('Fall Detection', np.zeros((480, 640, 3), dtype=np.uint8))
            cv2.waitKey(1)

        # 初始化ROS組件
        self.bridge = CvBridge()
        self.result_msg = Detection2DArray()
        
        # 訂閱者
        self.image_sub = self.create_subscription(
            Image,
            self.get_parameter('image_topic').value,
            self.image_callback,
            10
        )
        
        # 發布者
        self.yolo_result_pub = self.create_publisher(Detection2DArray, 'yolo_result', 10)
        
        # 加載相機參數
        with open(self.get_parameter('camera_info_file').value) as f:
            self.camera_info = yaml.safe_load(f)
            self.get_logger().info(f"Camera Info Loaded: {self.camera_info['k']}")

    def image_callback(self, msg):
        try:
            # 轉換ROS圖像到OpenCV格式
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # YOLOv5推理
            results = self.model.predict(cv_image, conf=0.5, verbose=False)
            
            # 處理檢測結果
            if results and len(results[0].boxes) > 0:
                # 繪製檢測框
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    label = results[0].names[int(box.cls[0])]
                    confidence = box.conf[0].item()
                    
                    # 繪製矩形和文字
                    cv2.rectangle(cv_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    if label == '0':
                        cv2.putText(cv_image, 
                                f"{label} {confidence:.2f} {'Fall Down'}",
                                (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                0.5, (0, 0, 255), 2)
            
            # 顯示結果
            if self.get_parameter('show_result').value:
                # 確保圖像數據類型正確
                if cv_image.dtype != np.uint8:
                    cv_image = cv_image.astype(np.uint8)
                
                cv2.imshow('Fall Detection', cv_image)
                key = cv2.waitKey(1)
                if key == 27:  # ESC鍵退出
                    self.destroy_node()

        except Exception as e:
            self.get_logger().error(f"Image processing error: {str(e)}")

    def __del__(self):
        if self.get_parameter('show_result').value:
            cv2.destroyAllWindows()

def main():
    rclpy.init()
    node = YoloV5Ros2()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()