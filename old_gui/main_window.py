from PyQt5.QtWidgets import QWidget
from .styles import STYLE_SHEET
from .controllers import MainController


class MainWindow(QWidget):
    def __init__(self, textlib_path='textlib/questions.json'):
        super().__init__()
        self.setWindowTitle('数据采集系统')
        self.setMinimumWidth(800)
        self.setStyleSheet(STYLE_SHEET)
        
        # 初始化控制器
        self.controller = MainController(self) 