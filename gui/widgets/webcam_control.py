from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox, QPushButton
from ..utils.styles import FONT_CONTENT


class WebcamControlWidget(QWidget):
    """摄像头控制控件 - 纯UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QGridLayout()
        
        # 设备选择
        layout.addWidget(QLabel("选择设备:"), 0, 0)
        self.webcam_combo = QComboBox()
        self.webcam_combo.setMinimumWidth(150)
        layout.addWidget(self.webcam_combo, 0, 1)
        
        # 刷新按钮
        self.refresh_webcam_btn = QPushButton("刷新")
        self.refresh_webcam_btn.setFont(FONT_CONTENT)
        layout.addWidget(self.refresh_webcam_btn, 0, 2)
        
        # 连接/断开按钮
        self.webcam_connect_btn = QPushButton("连接")
        self.webcam_connect_btn.setFont(FONT_CONTENT)
        layout.addWidget(self.webcam_connect_btn, 0, 3)
        
        # 开始/停止预览按钮
        self.webcam_preview_btn = QPushButton("开始预览")
        self.webcam_preview_btn.setFont(FONT_CONTENT)
        self.webcam_preview_btn.setEnabled(False)
        layout.addWidget(self.webcam_preview_btn, 1, 0, 1, 2)
        
        # 拍照按钮
        self.webcam_snapshot_btn = QPushButton("拍照")
        self.webcam_snapshot_btn.setFont(FONT_CONTENT)
        self.webcam_snapshot_btn.setEnabled(False)
        layout.addWidget(self.webcam_snapshot_btn, 1, 2, 1, 2)
        
        self.setLayout(layout) 