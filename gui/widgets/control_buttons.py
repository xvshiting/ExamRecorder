from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from ..utils.styles import FONT_CONTENT


class ControlButtonsWidget(QWidget):
    """控制按钮控件 - 纯UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout()
        
        self.start_btn = QPushButton('开始')
        self.start_btn.setFont(FONT_CONTENT)
        layout.addWidget(self.start_btn)
        
        self.next_btn = QPushButton('下一题')
        self.next_btn.setFont(FONT_CONTENT)
        layout.addWidget(self.next_btn)
        
        self.setLayout(layout) 