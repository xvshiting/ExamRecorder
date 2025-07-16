from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient, QPainter
from ...utils.styles import FONT_TITLE, FONT_CONTENT, STYLE_SHEET

class ModernButton(QPushButton):
    """现代化按钮"""
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon_text
        self.setMinimumSize(200, 80)
        self.setFont(QFont('Arial', 16, QFont.Bold))
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5BA0F2, stop:1 #4A90E2);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #357ABD, stop:1 #2A5F9E);
            }
        """)

class MainSelector(QWidget):
    """主界面选择器"""
    select_collect = pyqtSignal()
    select_playback = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('数据采集系统 - 选择系统')
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                background: transparent;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(40)
        layout.setContentsMargins(60, 80, 60, 80)

        # 标题区域
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(10)
        
        # 主标题
        title_label = QLabel('数据采集系统')
        title_label.setFont(QFont('Arial', 32, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
            }
        """)
        title_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel('Data Collection System')
        subtitle_label.setFont(QFont('Arial', 14))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #b0b0b0; background: transparent;")
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_container)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #4A90E2; max-height: 2px; min-height: 2px;")
        layout.addWidget(line)

        # 说明文字
        desc_label = QLabel('请选择要进入的功能模块')
        desc_label.setFont(QFont('Arial', 16))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #e0e0e0; background: transparent; margin: 20px;")
        layout.addWidget(desc_label)

        # 按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(40)
        button_layout.setContentsMargins(0, 20, 0, 20)

        # 采集按钮
        collect_btn = ModernButton('📊 数据采集', '📊')
        collect_btn.clicked.connect(self.select_collect.emit)
        button_layout.addWidget(collect_btn)

        # 回放按钮
        playback_btn = ModernButton('🎬 数据回放', '🎬')
        playback_btn.clicked.connect(self.select_playback.emit)
        button_layout.addWidget(playback_btn)

        layout.addWidget(button_container)
        layout.addStretch()
        
        # 底部信息
        footer_label = QLabel('© 2024 数据采集系统 - 重构版本')
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #808080; background: transparent; font-size: 12px;")
        layout.addWidget(footer_label)

        self.setLayout(layout) 