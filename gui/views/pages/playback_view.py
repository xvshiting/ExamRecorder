from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QComboBox,  # 新增QSlider、QComboBox
    QSplitter, QGroupBox, QGridLayout, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
import cv2
from PyQt5.QtGui import QImage, QPixmap

from ...utils.styles import STYLE_SHEET
from ...widgets.timeline_widget import TimelineWidget
from ...widgets.virtual_keyboard import VirtualKeyboardWindow
from ...widgets.record_info_panel import RecordInfoPanel
from ...services.playback.video_player_service import VideoPlayerService


class PlaybackView(QWidget):
    """回放页面视图 - 业务组件"""
    
    # 信号定义
    timeline_clicked = pyqtSignal(str, int)  # 视频类型, 帧位置
    thumbnail_clicked = pyqtSignal(str, int)  # 视频类型, 帧位置
    indicator_dragged = pyqtSignal(str, int)  # 视频类型, 帧位置
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('数据采集系统 - 回放')
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(STYLE_SHEET)
        
        # 业务状态
        self.current_record = None
        self.screen_player = None
        self.webcam_player = None
        self.sync_mode = True  # 联动模式开关
        self.virtual_keyboard_window = None
        self.screen_cap = None
        self.webcam_cap = None
        self.play_timer = None
        self.is_playing = False
        self.screen_video_path = None
        self.webcam_video_path = None
        
        # 初始化UI
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化UI - VSCode风格，整体侧边栏布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 顶部状态栏
        self.create_status_bar(main_layout)

        # 主Splitter：左侧边栏、主内容区、右侧信息侧边栏
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setStyleSheet("QSplitter::handle { background-color: #404040; }")
        
        # 左侧边栏
        self.create_left_panel(main_splitter)
        
        # 主内容区
        self.create_main_content(main_splitter)
        
        # 右侧信息侧边栏
        self.create_right_panel(main_splitter)
        
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 8)
        main_splitter.setStretchFactor(2, 2)
        main_layout.addWidget(main_splitter)
    
    def create_status_bar(self, main_layout):
        """创建状态栏"""
        status_bar = QWidget()
        status_bar.setFixedHeight(32)
        status_bar.setStyleSheet("background: #23272e; border-bottom: 1px solid #222; color: #fff;")
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(8, 0, 8, 0)
        status_layout.setSpacing(8)
        
        self.left_toggle_btn = QPushButton("≡")
        self.left_toggle_btn.setFixedSize(28, 28)
        self.left_toggle_btn.setStyleSheet("QPushButton { background: #23272e; color: #fff; border: none; font-size: 18px; }")
        
        # 键盘按钮
        self.keyboard_btn = QPushButton("⌨")
        self.keyboard_btn.setFixedSize(28, 28)
        self.keyboard_btn.setStyleSheet("QPushButton { background: #23272e; color: #fff; border: none; font-size: 18px; }")
        
        self.right_toggle_btn = QPushButton("→")
        self.right_toggle_btn.setFixedSize(28, 28)
        self.right_toggle_btn.setStyleSheet("QPushButton { background: #23272e; color: #fff; border: none; font-size: 18px; }")
        
        self.back_btn = QPushButton("⟵ 返回记录选择")
        self.back_btn.setFixedSize(120, 28)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #23272e;
                color: #fff;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                padding: 0 8px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        status_layout.addWidget(self.back_btn)
        status_layout.addStretch()
        status_layout.addWidget(QLabel("数据采集系统 - 回放"))
        status_layout.addStretch()
        status_layout.addWidget(self.keyboard_btn)
        status_layout.addWidget(self.right_toggle_btn)
        
        main_layout.addWidget(status_bar)
    
    def create_left_panel(self, main_splitter):
        """创建左侧面板"""
        self.left_panel = QWidget()
        self.left_panel.setMinimumWidth(120)
        self.left_panel.setMaximumWidth(220)
        self.left_panel.setStyleSheet("background: #23272e; border-right: 1px solid #222;")
        self.left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_splitter.addWidget(self.left_panel)
        self.left_panel.setVisible(False)
    
    def create_main_content(self, main_splitter):
        """创建主内容区"""
        main_content = QWidget()
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setSpacing(0)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 视频区
        self.video_splitter = self.create_video_area(main_content_layout)
        
        # 控制区
        self.control_widget = self.create_control_area(main_content_layout)
        
        # 联动区
        self.sync_widget = self.create_sync_area(main_content_layout)
        
        # 时间轴区
        self.timeline_splitter = self.create_timeline_area(main_content_layout)
        
        # 设置stretch比例
        main_content_layout.setStretchFactor(self.video_splitter, 8)
        main_content_layout.setStretchFactor(self.control_widget, 1)
        main_content_layout.setStretchFactor(self.sync_widget, 1)
        main_content_layout.setStretchFactor(self.timeline_splitter, 2)
        main_splitter.addWidget(main_content)
    
    def create_video_area(self, main_content_layout):
        """创建视频区域"""
        video_splitter = QSplitter(Qt.Horizontal)
        video_splitter.setStyleSheet("QSplitter::handle { background-color: #404040; }")
        video_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 屏幕录制视频组
        screen_group = self.create_video_group("屏幕录制", "screen_video_label")
        video_splitter.addWidget(screen_group)
        
        # 摄像头录制视频组
        webcam_group = self.create_video_group("摄像头录制", "webcam_video_label")
        video_splitter.addWidget(webcam_group)
        
        video_splitter.setSizes([800, 800])
        main_content_layout.addWidget(video_splitter)
        main_content_layout.setSpacing(0)
        return video_splitter
    
    def create_video_group(self, title, label_name):
        """创建视频组"""
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 视频标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(25)
        title_bar.setStyleSheet("background-color: #2d2d2d; border-bottom: 1px solid #404040;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 11px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addWidget(title_bar)
        
        # 视频显示区域
        video_widget = QWidget()
        video_widget.setStyleSheet("background-color: #1e1e1e; border: none;")
        video_layout = QVBoxLayout(video_widget)
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 视频标签
        video_label = QLabel()
        video_label.setAlignment(Qt.AlignCenter)
        video_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #666666;
                border: 2px dashed #404040;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        video_label.setText("暂无视频")
        video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        setattr(self, label_name, video_label)
        video_layout.addWidget(video_label)
        
        layout.addWidget(video_widget)
        layout.addStretch()
        
        return group
    
    def create_control_area(self, main_content_layout):
        """创建控制区域"""
        control_widget = QWidget()
        control_widget.setFixedHeight(48)
        control_widget.setStyleSheet("background-color: #23272e; border-top: none;")
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(6, 0, 6, 0)
        control_layout.setSpacing(6)

        # 播放控制按钮
        self.play_btn = QPushButton("播放")
        self.play_btn.setMinimumWidth(48)
        self.play_btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 0 6px;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
        """)
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setMinimumWidth(48)
        self.stop_btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF3B30;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 0 6px;
            }
            QPushButton:hover {
                background-color: #CC2E26;
            }
        """)

        # 播放速度拖动条
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(5)   # 0.5x
        self.speed_slider.setMaximum(20)  # 2.0x
        self.speed_slider.setSingleStep(1)
        self.speed_slider.setValue(10)    # 默认1.0x
        self.speed_slider.setFixedWidth(100)
        self.speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 8px;
                background: #23272e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #007AFF;
                border: 1px solid #007AFF;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
        """)
        self.speed_label = QLabel("1.0x")
        self.speed_label.setStyleSheet("color: #fff; font-weight: bold; font-size: 12px; padding: 0 2px;")
        # 时间显示
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
                font-weight: bold;
                font-size: 12px;
                padding: 0 4px;
            }
        """)
        self.time_label.setFixedWidth(90)
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.time_label)
        control_layout.addWidget(QLabel("速度:"))
        control_layout.addWidget(self.speed_slider)
        control_layout.addWidget(self.speed_label)
        control_layout.addStretch()
        main_content_layout.addWidget(control_widget)
        return control_widget
    
    def create_sync_area(self, main_content_layout):
        """创建联动控制区域"""
        sync_widget = QWidget()
        sync_widget.setFixedHeight(40)
        sync_widget.setStyleSheet("background-color: #2d2d2d; border-top: 1px solid #404040;")
        sync_layout = QHBoxLayout(sync_widget)
        sync_layout.setContentsMargins(10, 5, 10, 5)
        
        # 联动模式开关
        self.sync_btn = QPushButton("联动模式: 开启")
        self.sync_btn.setCheckable(True)
        self.sync_btn.setChecked(True)
        self.sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:checked {
                background-color: #28A745;
            }
            QPushButton:!checked {
                background-color: #6C757D;
            }
        """)
        
        sync_layout.addWidget(self.sync_btn)
        sync_layout.addStretch()
        
        main_content_layout.addWidget(sync_widget)
        return sync_widget
    
    def create_timeline_area(self, main_content_layout):
        """创建时间轴区域"""
        timeline_splitter = QSplitter(Qt.Horizontal)
        timeline_splitter.setStyleSheet("QSplitter::handle { background-color: #404040; }")
        timeline_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        timeline_splitter.setFixedHeight(120)
        # 屏幕录制时间轴
        screen_timeline_panel = QWidget()
        screen_timeline_panel.setStyleSheet("background-color: #1e1e1e; border-right: 1px solid #404040;")
        screen_timeline_layout = QVBoxLayout(screen_timeline_panel)
        screen_timeline_layout.setSpacing(0)
        screen_timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.screen_timeline = TimelineWidget()
        self.screen_timeline.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        screen_timeline_layout.addWidget(self.screen_timeline)
        timeline_splitter.addWidget(screen_timeline_panel)
        # 摄像头录制时间轴
        webcam_timeline_panel = QWidget()
        webcam_timeline_panel.setStyleSheet("background-color: #1e1e1e;")
        webcam_timeline_layout = QVBoxLayout(webcam_timeline_panel)
        webcam_timeline_layout.setSpacing(0)
        webcam_timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.webcam_timeline = TimelineWidget()
        self.webcam_timeline.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        webcam_timeline_layout.addWidget(self.webcam_timeline)
        timeline_splitter.addWidget(webcam_timeline_panel)
        timeline_splitter.setSizes([800, 800])
        main_content_layout.addWidget(timeline_splitter)
        main_content_layout.setSpacing(0)
        return timeline_splitter
    
    def create_right_panel(self, main_splitter):
        """创建右侧面板"""
        self.info_panel = RecordInfoPanel()
        self.info_panel.setMinimumWidth(300)
        self.info_panel.setMaximumWidth(400)
        self.info_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_splitter.addWidget(self.info_panel)
        self.info_panel.setVisible(False)
    
    def connect_signals(self):
        """连接信号"""
        # 侧边栏切换
        self.left_toggle_btn.clicked.connect(self.toggle_left_panel)
        self.right_toggle_btn.clicked.connect(self.toggle_right_panel)
        
        # 键盘按钮
        self.keyboard_btn.clicked.connect(self.toggle_virtual_keyboard)
        
        # 播放控制
        self.play_btn.clicked.connect(self.toggle_play)
        self.stop_btn.clicked.connect(self.stop_video)
        
        # 联动模式
        self.sync_btn.clicked.connect(self.toggle_sync_mode)
        
        # 时间轴信号
        self.screen_timeline.timeline_clicked.connect(lambda pos: self.timeline_clicked.emit('screen', pos))
        self.screen_timeline.thumbnail_clicked.connect(lambda pos: self.handle_timeline_jump('screen', pos))
        self.screen_timeline.indicator_dragged.connect(lambda pos: self.handle_timeline_drag('screen', pos))
        
        self.webcam_timeline.timeline_clicked.connect(lambda pos: self.timeline_clicked.emit('webcam', pos))
        self.webcam_timeline.thumbnail_clicked.connect(lambda pos: self.handle_timeline_jump('webcam', pos))
        self.webcam_timeline.indicator_dragged.connect(lambda pos: self.handle_timeline_drag('webcam', pos))

        self.speed_slider.valueChanged.connect(self.on_speed_slider_changed)
        # 移除progress_slider和speed_box相关信号
    
    def toggle_left_panel(self):
        """切换左侧面板"""
        self.left_panel.setVisible(not self.left_panel.isVisible())
    
    def toggle_right_panel(self):
        """切换右侧面板"""
        self.info_panel.setVisible(not self.info_panel.isVisible())
    
    def toggle_virtual_keyboard(self):
        """切换虚拟键盘"""
        if not self.virtual_keyboard_window:
            self.virtual_keyboard_window = VirtualKeyboardWindow(self)
            self.virtual_keyboard_window.show()
        else:
            if self.virtual_keyboard_window.isVisible():
                self.virtual_keyboard_window.hide()
            else:
                self.virtual_keyboard_window.show()
    
    def toggle_play(self):
        if not self.is_playing:
            if self.screen_player:
                self.screen_player.play()
            if self.webcam_player:
                self.webcam_player.play()
            self.is_playing = True
            self.play_btn.setText("暂停")
        else:
            if self.screen_player:
                self.screen_player.pause()
            if self.webcam_player:
                self.webcam_player.pause()
            self.is_playing = False
            self.play_btn.setText("播放")

    def stop_video(self):
        if self.screen_player:
            self.screen_player.stop()
        if self.webcam_player:
            self.webcam_player.stop()
        self.is_playing = False
        self.play_btn.setText("播放")
        # 回到首帧
        if self.screen_player:
            self.screen_player.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.screen_player.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.screen_video_label.setPixmap(pixmap.scaled(self.screen_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.webcam_player:
            self.webcam_player.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.webcam_player.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.webcam_video_label.setPixmap(pixmap.scaled(self.webcam_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def play_next_frame(self):
        # 屏幕视频
        if self.screen_cap:
            ret, frame = self.screen_cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.screen_video_label.setPixmap(pixmap.scaled(self.screen_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.stop_video()
        # 摄像头视频
        if self.webcam_cap:
            ret, frame = self.webcam_cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.webcam_video_label.setPixmap(pixmap.scaled(self.webcam_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def toggle_sync_mode(self):
        """切换联动模式"""
        self.sync_mode = self.sync_btn.isChecked()
        if self.sync_mode:
            self.sync_btn.setText("联动模式: 开启")
            self.sync_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28A745;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 5px 15px;
                }
            """)
        else:
            self.sync_btn.setText("联动模式: 关闭")
            self.sync_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6C757D;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 5px 15px;
                }
            """)
    
    def load_record(self, record):
        """加载记录数据"""
        self.current_record = record
        # 设置记录信息
        question = record.get('question', {})
        question_content = question.get('content', '') if isinstance(question, dict) else str(question)
        self.info_panel.set_info(
            record.get('id', 'Unknown'),
            question_content,
            record.get('user_input', '')
        )
    
    def load_videos(self, screen_video_path, webcam_video_path):
        print("加载视频路径：", screen_video_path, webcam_video_path)
        self.screen_video_path = screen_video_path
        self.webcam_video_path = webcam_video_path
        # 关闭旧player
        if self.screen_player:
            self.screen_player.stop()
            self.screen_player.wait()
            self.screen_player = None
        if self.webcam_player:
            self.webcam_player.stop()
            self.webcam_player.wait()
            self.webcam_player = None
        # 新建player
        if screen_video_path:
            self.screen_player = VideoPlayerService(screen_video_path)
            if self.screen_player.open_video():
                self.screen_player.frame_ready.connect(self.update_screen_frame)
                self.screen_player.video_finished.connect(self.stop_video)
        if webcam_video_path:
            self.webcam_player = VideoPlayerService(webcam_video_path)
            if self.webcam_player.open_video():
                self.webcam_player.frame_ready.connect(self.update_webcam_frame)
                self.webcam_player.video_finished.connect(self.stop_video)
        # 显示首帧
        if self.screen_player:
            self.screen_player.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.screen_player.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.screen_video_label.setPixmap(pixmap.scaled(self.screen_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.webcam_player:
            self.webcam_player.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.webcam_player.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.webcam_video_label.setPixmap(pixmap.scaled(self.webcam_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # 加载时间轴缩略图
        if hasattr(self, 'screen_timeline') and screen_video_path:
            self.screen_timeline.load_thumbnails(screen_video_path)
        if hasattr(self, 'webcam_timeline') and webcam_video_path:
            self.webcam_timeline.load_thumbnails(webcam_video_path)

    def update_screen_frame(self, pixmap, timestamp_ms):
        self.screen_video_label.setPixmap(pixmap.scaled(self.screen_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.screen_player and not getattr(self, 'slider_is_dragging', False):
            total = self.screen_player.get_total_frames()
            pos = self.screen_player.get_current_frame()
            if total > 0:
                self.screen_timeline.update_position(pos)
        # 更新时间显示
        self.update_time_display(timestamp_ms)

    def update_webcam_frame(self, pixmap, timestamp_ms):
        self.webcam_video_label.setPixmap(pixmap.scaled(self.webcam_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.webcam_player and not getattr(self, 'slider_is_dragging', False):
            total = self.webcam_player.get_total_frames()
            pos = self.webcam_player.get_current_frame()
            if total > 0:
                self.webcam_timeline.update_position(pos)
        # 更新时间显示
        self.update_time_display(timestamp_ms)
    
    def update_time_display(self, timestamp_ms):
        """更新时间显示"""
        current_time = timestamp_ms / 1000
        total_time = 0
        if self.screen_player:
            total_time = self.screen_player.get_total_frames() / self.screen_player.get_fps()
        current_minutes = int(current_time) // 60
        current_seconds = int(current_time) % 60
        total_minutes = int(total_time) // 60
        total_seconds = int(total_time) % 60
        self.time_label.setText(f"{current_minutes:02d}:{current_seconds:02d} / {total_minutes:02d}:{total_seconds:02d}")
    
    def update_keyboard_highlight(self, keys):
        """更新键盘高亮"""
        if self.virtual_keyboard_window and self.virtual_keyboard_window.isVisible():
            self.virtual_keyboard_window.highlight_keys(keys)
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.virtual_keyboard_window:
            self.virtual_keyboard_window.close()
        event.accept() 

    def on_speed_slider_changed(self, value):
        speed = round(value / 10, 1)
        self.speed_label.setText(f"{speed:.1f}x")
        if self.screen_player:
            self.screen_player.set_playback_speed(speed)
        if self.webcam_player:
            self.webcam_player.set_playback_speed(speed)

    def handle_timeline_jump(self, video_type, frame_pos):
        if self.screen_player:
            self.screen_player.seek(frame_pos)
        if self.webcam_player:
            self.webcam_player.seek(frame_pos)
        self.screen_timeline.update_position(frame_pos)
        self.webcam_timeline.update_position(frame_pos) 

    def handle_timeline_drag(self, video_type, frame_pos):
        """拖动时间轴竖轴时的联动与画面刷新"""
        if self.sync_mode:
            # 联动：两个视频都seek
            if self.screen_player:
                self.screen_player.pause()
                self.screen_player.seek(frame_pos)
                self.screen_player.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = self.screen_player.cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimg)
                    self.screen_video_label.setPixmap(pixmap.scaled(self.screen_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            if self.webcam_player:
                self.webcam_player.pause()
                self.webcam_player.seek(frame_pos)
                self.webcam_player.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = self.webcam_player.cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimg)
                    self.webcam_video_label.setPixmap(pixmap.scaled(self.webcam_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.screen_timeline.update_position(frame_pos)
            self.webcam_timeline.update_position(frame_pos)
        else:
            # 非联动：只操作当前视频
            if video_type == 'screen' and self.screen_player:
                self.screen_player.pause()
                self.screen_player.seek(frame_pos)
                self.screen_player.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = self.screen_player.cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimg)
                    self.screen_video_label.setPixmap(pixmap.scaled(self.screen_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.screen_timeline.update_position(frame_pos)
            elif video_type == 'webcam' and self.webcam_player:
                self.webcam_player.pause()
                self.webcam_player.seek(frame_pos)
                self.webcam_player.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = self.webcam_player.cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimg)
                    self.webcam_video_label.setPixmap(pixmap.scaled(self.webcam_video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.webcam_timeline.update_position(frame_pos) 