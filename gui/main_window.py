from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout
from PyQt5.QtCore import QEvent
from .utils.styles import STYLE_SHEET
from .views.pages.main_selector import MainSelector
from .views.pages.collect_page import CollectPage
from .views.pages.playback_page import PlaybackPage

class MainWindow(QWidget):
    """主窗口，支持页面切换"""
    def __init__(self, textlib_path='textlib/questions.json'):
        super().__init__()
        self.setWindowTitle('数据采集系统')
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        self.resize(1200, 700)
        self.setStyleSheet(STYLE_SHEET)

        self.stack = QStackedWidget()
        self.selector = MainSelector()
        self.collect_view = None  # 延迟创建
        self.playback_view = None  # 延迟创建

        self.stack.addWidget(self.selector)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.selector.select_collect.connect(self.show_collect)
        self.selector.select_playback.connect(self.show_playback)
        self.show_selector()

    def show_selector(self):
        self.stack.setCurrentWidget(self.selector)

    def show_collect(self):
        """显示采集页面"""
        if self.collect_view is None:
            self.collect_view = CollectPage()
            self.stack.addWidget(self.collect_view)
            # 为采集页面安装事件过滤器
            self.collect_view.installEventFilter(self)
        self.stack.setCurrentWidget(self.collect_view)

    def show_playback(self):
        """显示回放页面"""
        if self.playback_view is None:
            self.playback_view = PlaybackPage()
            self.stack.addWidget(self.playback_view)
            # 为回放页面安装事件过滤器
            self.playback_view.installEventFilter(self)
        self.stack.setCurrentWidget(self.playback_view)

    def eventFilter(self, obj, event):
        """事件过滤器，监听关闭事件"""
        if event.type() == QEvent.Close:
            if obj == self.collect_view or obj == self.playback_view:
                self.show_selector()
                event.ignore()  # 阻止窗口关闭
                return True
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        # 如果当前不是选择界面，拦截关闭，切回选择界面
        if self.stack.currentWidget() != self.selector:
            self.show_selector()
            event.ignore()
        else:
            event.accept() 