from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt5.QtCore import Qt
from .styles import FONT_TITLE, FONT_CONTENT, STYLE_SHEET
from .main_window import MainWindow
from .data_manager_window import DataManagerWindow


class MainSelector(QWidget):
    """主界面选择器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('数据采集系统 - 主界面')
        self.setMinimumSize(600, 400)
        self.setStyleSheet(STYLE_SHEET)
        
        self.main_window = None
        self.data_manager_window = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # 标题
        title_label = QLabel('数据采集系统')
        title_label.setFont(FONT_TITLE)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 分隔线
        line = QFrame()
        line.setObjectName('Line')
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)
        
        # 说明文字
        desc_label = QLabel('请选择要进入的功能模块：')
        desc_label.setFont(FONT_CONTENT)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        
        # 采集按钮
        collect_btn = QPushButton('数据采集')
        collect_btn.setFont(FONT_CONTENT)
        collect_btn.setMinimumSize(150, 60)
        collect_btn.clicked.connect(self.open_collection_mode)
        button_layout.addWidget(collect_btn)
        
        # 管理按钮
        manage_btn = QPushButton('内容管理')
        manage_btn.setFont(FONT_CONTENT)
        manage_btn.setMinimumSize(150, 60)
        manage_btn.clicked.connect(self.open_management_mode)
        button_layout.addWidget(manage_btn)
        
        layout.addLayout(button_layout)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.setLayout(layout)
    
    def open_collection_mode(self):
        """打开采集模式"""
        if not self.main_window:
            self.main_window = MainWindow()
        
        self.main_window.show()
        self.hide()
        
        # 监听主窗口关闭事件
        self.main_window.destroyed.connect(self.on_collection_window_closed)
    
    def open_management_mode(self):
        """打开管理模式"""
        if not self.data_manager_window:
            self.data_manager_window = DataManagerWindow()
        
        self.data_manager_window.show()
        self.hide()
        
        # 监听管理窗口关闭事件
        self.data_manager_window.destroyed.connect(self.on_management_window_closed)
    
    def on_collection_window_closed(self):
        """采集窗口关闭事件"""
        self.main_window = None
        self.show()
    
    def on_management_window_closed(self):
        """管理窗口关闭事件"""
        self.data_manager_window = None
        self.show() 