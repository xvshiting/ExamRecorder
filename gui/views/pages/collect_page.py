from PyQt5.QtWidgets import QWidget, QVBoxLayout
from ...controllers.collect_controller import CollectController
from ..collect_view import CollectView

class CollectPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = CollectView()
        self.controller = None  # 延迟初始化
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
    
    def showEvent(self, event):
        """页面显示时初始化控制器"""
        super().showEvent(event)
        if self.controller is None:
            self.controller = CollectController(self, self.view)
    
    def hideEvent(self, event):
        """页面隐藏时清理控制器"""
        super().hideEvent(event)
        if self.controller:
            if hasattr(self.controller, 'webcam_manager'):
                self.controller.webcam_manager.disconnect_webcam()
            self.controller = None 