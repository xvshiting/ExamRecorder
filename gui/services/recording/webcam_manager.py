import cv2
import threading
import time
import sys
import logging
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel

class WebcamManager(QObject):
    """Webcam管理器，负责发现、连接和获取webcam影像"""
    
    # 信号定义
    frame_ready = pyqtSignal(QImage)  # 当有新帧时发出信号
    webcam_connected = pyqtSignal(str)  # 当webcam连接成功时发出信号
    webcam_disconnected = pyqtSignal()  # 当webcam断开连接时发出信号
    error_occurred = pyqtSignal(str)  # 当发生错误时发出信号
    
    def __init__(self):
        super().__init__()
        self.cap = None
        self.is_running = False
        self.thread = None
        self.current_device = None
        self.available_devices = []
        
    def discover_webcams(self):
        """发现可用的webcam设备"""
        self.available_devices = []
        
        # 在macOS上，先检查权限
        if sys.platform == "darwin":
            try:
                # 尝试打开默认摄像头来检查权限
                test_cap = cv2.VideoCapture(0)
                if not test_cap.isOpened():
                    self.error_occurred.emit("摄像头权限被拒绝。请在系统偏好设置中允许应用程序访问摄像头。")
                    return self.available_devices
                test_cap.release()
            except Exception as e:
                self.error_occurred.emit(f"摄像头权限检查失败: {str(e)}")
                return self.available_devices
        
        # 尝试连接前10个设备索引
        for i in range(10):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    # 尝试读取一帧来确认设备可用
                    ret, frame = cap.read()
                    if ret:
                        # 获取设备信息
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        
                        device_info = {
                            'index': i,
                            'name': f'Camera {i}',
                            'resolution': f'{width}x{height}',
                            'fps': fps
                        }
                        self.available_devices.append(device_info)
                    cap.release()
            except Exception as e:
                # 静默处理单个设备错误，继续检查其他设备
                continue
                
        return self.available_devices
    
    def connect_webcam(self, device_index=0):
        """连接到指定的webcam设备"""
        try:
            if self.cap is not None:
                self.disconnect_webcam()
                
            self.cap = cv2.VideoCapture(device_index)
            if not self.cap.isOpened():
                raise Exception(f"无法打开摄像头设备 {device_index}")
            
            # 设置一些默认参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # 验证摄像头是否真的可以读取帧
            ret, test_frame = self.cap.read()
            if not ret or test_frame is None:
                raise Exception(f"摄像头设备 {device_index} 无法读取帧")
                
            # 获取实际的分辨率和帧率
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logging.info(f"摄像头 {device_index} 连接成功，分辨率: {actual_width}x{actual_height}, FPS: {actual_fps}")
                
            self.current_device = device_index
            self.webcam_connected.emit(f"摄像头 {device_index} 连接成功")
            return True
            
        except Exception as e:
            logging.error(f"连接摄像头失败: {str(e)}")
            self.error_occurred.emit(f"连接摄像头失败: {str(e)}")
            return False
    
    def disconnect_webcam(self):
        """断开webcam连接"""
        self.stop_capture()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.current_device = None
        self.webcam_disconnected.emit()
    
    def start_capture(self):
        """开始捕获webcam影像"""
        if self.cap is None or not self.cap.isOpened():
            self.error_occurred.emit("摄像头未连接")
            return False
            
        if self.is_running:
            return True
            
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop_capture(self):
        """停止捕获webcam影像"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
    
    def _capture_loop(self):
        """捕获循环"""
        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                break
                
            try:
                ret, frame = self.cap.read()
                if ret:
                    # 转换OpenCV图像为QImage
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_frame.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    self.frame_ready.emit(qt_image)
                else:
                    self.error_occurred.emit("读取摄像头帧失败")
                    break
            except Exception as e:
                self.error_occurred.emit(f"捕获过程中出错: {str(e)}")
                break
                
            time.sleep(0.033)  # 约30fps
    
    def get_snapshot(self):
        """获取单张快照"""
        if self.cap is None or not self.cap.isOpened():
            return None
            
        try:
            ret, frame = self.cap.read()
            if ret:
                return frame
        except Exception as e:
            self.error_occurred.emit(f"拍照失败: {str(e)}")
        return None
    
    def set_resolution(self, width, height):
        """设置摄像头分辨率"""
        if self.cap is not None and self.cap.isOpened():
            try:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                return True
            except Exception as e:
                self.error_occurred.emit(f"设置分辨率失败: {str(e)}")
                return False
        return False
    
    def get_resolution(self):
        """获取当前分辨率"""
        if self.cap is not None and self.cap.isOpened():
            try:
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                return width, height
            except Exception:
                pass
        return None, None
    
    @property
    def is_connected(self):
        """检查是否已连接"""
        return self.cap is not None and self.cap.isOpened() 