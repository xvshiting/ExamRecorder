from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from ..utils.styles import FONT_CONTENT


class WebcamDisplay(QLabel):
    """Webcam显示控件 - 纯UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 240)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #232A34;
                color: #7EC8E3;
                border: 2px solid #2D3748;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        self.setText("摄像头未连接")
    
    def update_frame(self, image):
        """更新帧图像"""
        if image is not None:
            # 检查图像类型
            if hasattr(image, 'shape'):  # OpenCV图像
                if len(image.shape) == 3:
                    height, width, channel = image.shape
                    bytes_per_line = 3 * width
                    q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_image)
                    
                    # 缩放以适应显示区域
                    scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.setPixmap(scaled_pixmap)
            else:  # QImage
                pixmap = QPixmap.fromImage(image)
                
                # 缩放以适应显示区域
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setPixmap(scaled_pixmap)
    
    def set_text(self, text):
        """设置显示文本"""
        self.setText(text)
        self.setPixmap(QPixmap())
    
    def set_recording_style(self, is_recording):
        """设置录制样式"""
        if is_recording:
            self.setStyleSheet("""
                QLabel {
                    background-color: #232A34;
                    color: #7EC8E3;
                    border: 3px solid #FF3B30;
                    border-radius: 8px;
                    font-size: 14px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: #232A34;
                    color: #7EC8E3;
                    border: 2px solid #2D3748;
                    border-radius: 8px;
                    font-size: 14px;
                }
            """)


class WebcamDisplayWidget(QWidget):
    """摄像头显示控件 - 纯UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        self.webcam_display = WebcamDisplay()
        layout.addWidget(self.webcam_display)
        
        # Webcam状态
        self.webcam_status_label = QLabel("摄像头状态: 未连接")
        self.webcam_status_label.setFont(FONT_CONTENT)
        layout.addWidget(self.webcam_status_label)
        
        self.setLayout(layout)
    
    def update_frame(self, image):
        """更新帧图像"""
        self.webcam_display.update_frame(image)
    
    def set_text(self, text):
        """设置显示文本"""
        self.webcam_display.set_text(text)
    
    def set_recording_style(self, is_recording):
        """设置录制样式"""
        self.webcam_display.set_recording_style(is_recording)
    
    def set_status(self, status):
        """设置状态文本"""
        self.webcam_status_label.setText(status) 