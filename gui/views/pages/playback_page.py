from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QPushButton
import os
import json
from .playback_view import PlaybackView

class RecordSelectorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel('请选择要回放的记录：'))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
        self.load_records()
    def load_records(self):
        self.list_widget.clear()
        data_dir = 'data'
        if not os.path.exists(data_dir):
            return
        for fname in os.listdir(data_dir):
            if fname.endswith('.json'):
                self.list_widget.addItem(fname)

class PlaybackPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selector = RecordSelectorWidget()
        self.view = None
        self.controller = None
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.selector)
        self.setLayout(self.layout)
        self.selector.list_widget.itemDoubleClicked.connect(self.on_record_selected)
    def on_record_selected(self, item):
        record_path = os.path.join('data', item.text())
        with open(record_path, 'r', encoding='utf-8') as f:
            record = json.load(f)
        # 切换到PlaybackView
        if self.view:
            self.layout.removeWidget(self.view)
            self.view.deleteLater()
        self.view = PlaybackView()
        self.layout.addWidget(self.view)
        self.selector.hide()
        self.view.load_record(record)
        # 可选：加载视频文件
        screen_video = record.get('screen_video_path')
        webcam_video = record.get('webcam_video_path')
        self.view.load_videos(screen_video, webcam_video)
        # 删除底部返回按钮相关代码
        # back_btn = QPushButton('返回记录选择')
        # back_btn.clicked.connect(self.show_selector)
        # self.layout.addWidget(back_btn)
        # self.back_btn = back_btn
        # 建议在PlaybackView的top bar绑定回退信号
        self.view.back_btn.clicked.connect(self.show_selector)
    def show_selector(self):
        if self.view:
            self.layout.removeWidget(self.view)
            self.view.deleteLater()
            self.view = None
        # 删除底部返回按钮相关代码
        # if hasattr(self, 'back_btn'):
        #     self.layout.removeWidget(self.back_btn)
        #     self.back_btn.deleteLater()
        #     del self.back_btn
        self.selector.show()
    def showEvent(self, event):
        super().showEvent(event)
        if self.controller is None and self.view:
            from .playback_page import PlaybackController
            self.controller = PlaybackController(self.view)
    def hideEvent(self, event):
        super().hideEvent(event)
        if self.controller:
            self.controller = None 