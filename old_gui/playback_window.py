import cv2
import json
import threading
import time
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider,
    QTextEdit, QSplitter, QGroupBox, QGridLayout, QScrollArea, QFrame, QSizePolicy,
    QFormLayout
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QRect, QEasingCurve, QPropertyAnimation
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from .styles import FONT_TITLE, FONT_CONTENT, STYLE_SHEET

logging.basicConfig(level=logging.DEBUG)

class VideoPlayer(QThread):
    """视频播放线程"""
    frame_ready = pyqtSignal(QPixmap, int)  # 帧图像, 时间戳(毫秒)
    video_finished = pyqtSignal()
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.cap = None
        self.fps = 0
        self.total_frames = 0
        self.current_frame = 0
        self.is_playing = False
        self.is_paused = False
        self.seek_position = -1
        self.start_time = 0  # 播放开始时间
        
    def run(self):
        """运行播放线程"""
        if not self.video_path or not self.cap:
            return
            
        # 确保从第一帧开始播放
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.current_frame = 0
        self.start_time = time.time()
        
        while self.is_playing:
            if self.is_paused:
                time.sleep(0.1)
                continue
                
            # 处理跳转
            if self.seek_position >= 0:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_position)
                self.current_frame = self.seek_position
                self.seek_position = -1
                self.start_time = time.time() - (self.current_frame / self.fps)
            
            ret, frame = self.cap.read()
            if not ret:
                self.is_playing = False
                self.video_finished.emit()
                break
                
            # 转换帧格式
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # 计算时间戳
            timestamp_ms = int(self.current_frame / self.fps * 1000)
            
            # 发送帧
            self.frame_ready.emit(pixmap, timestamp_ms)
            self.current_frame += 1
            
            # 控制播放速度 - 每帧之间的延迟
            frame_delay = 1.0 / self.fps
            time.sleep(frame_delay)
    
    def open_video(self):
        """打开视频"""
        self.cap = cv2.VideoCapture(self.video_path)
        if self.cap.isOpened():
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # 确保从第一帧开始
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.current_frame = 0
            return True
        return False
    
    def play(self):
        """开始播放"""
        self.is_playing = True
        self.is_paused = False
        if not self.isRunning():
            self.start()
    
    def pause(self):
        """暂停播放"""
        self.is_paused = True
    
    def resume(self):
        """恢复播放"""
        self.is_paused = False
        if not self.isRunning():
            self.start()
    
    def stop(self):
        """停止播放"""
        self.is_playing = False
        self.wait()
    
    def seek(self, frame_position):
        """跳转到指定帧"""
        self.seek_position = frame_position
    
    def close(self):
        """关闭视频"""
        self.stop()
        if self.cap:
            self.cap.release()


class TimelineWidget(QWidget):
    """时间轴组件 - 结合时间轴和缩略图"""
    
    def __init__(self, video_path, video_type, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.video_type = video_type
        self.thumbnails = []
        self.current_position = 0
        self.total_duration = 0
        self.playback_window = None
        self.current_frame = 0
        self.fps = 0
        self.init_ui()
        self.load_thumbnails()
    
    def init_ui(self):
        """初始化UI - Final Cut Pro风格"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 时间轴标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(25)
        title_bar.setStyleSheet("background-color: #2d2d2d; border-bottom: 1px solid #404040;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        title_label = QLabel("时间轴")
        title_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 11px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 时间显示
        time_label_style = """
            QLabel {
                background-color: #1a1a1a;
                color: #ffffff;
                padding: 3px 8px;
                border: 1px solid #404040;
                border-radius: 3px;
                font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
                font-weight: bold;
                font-size: 10px;
                min-width: 60px;
            }
        """
        
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setStyleSheet(time_label_style)
        self.current_time_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.current_time_label)
        
        self.total_time_label = QLabel("00:00")
        self.total_time_label.setStyleSheet(time_label_style)
        self.total_time_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.total_time_label)
        
        layout.addWidget(title_bar)
        
        # 缩略图时间轴区域
        self.timeline_widget = QWidget()
        self.timeline_widget.setFixedHeight(80)
        self.timeline_widget.setStyleSheet("background-color: #1e1e1e; border: none;")
        
        # 添加时间轴点击事件
        self.timeline_widget.mousePressEvent = self.on_timeline_click
        
        # 缩略图布局
        self.thumbnail_layout = QHBoxLayout(self.timeline_widget)
        self.thumbnail_layout.setSpacing(1)
        self.thumbnail_layout.setContentsMargins(5, 5, 5, 5)
        
        layout.addWidget(self.timeline_widget)
        
        self.setLayout(layout)
    
    def load_thumbnails(self):
        """加载缩略图"""
        if not self.video_path:
            return
            
        # 清空之前的缩略图
        self.clear_thumbnails()
            
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            return
            
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.total_duration = total_frames / self.fps
        
        # 更新总时间显示
        total_minutes = int(self.total_duration) // 60
        total_seconds = int(self.total_duration) % 60
        self.total_time_label.setText(f"{total_minutes:02d}:{total_seconds:02d}")
        
        # 生成缩略图（每2秒一张，从0秒开始）
        thumbnail_interval = int(self.fps * 2)
        
        for i in range(0, total_frames, thumbnail_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                # 缩放缩略图
                frame = cv2.resize(frame, (100, 56))
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                
                # 创建缩略图容器
                container = QWidget()
                container.setFixedSize(80, 70)
                container.setStyleSheet("""
                    QWidget {
                        border: 1px solid #404040;
                        background-color: #2a2a2a;
                    }
                    QWidget:hover {
                        border: 1px solid #007AFF;
                        background-color: #333333;
                    }
                """)
                
                # 缩略图标签
                thumbnail_label = QLabel(container)
                thumbnail_label.setPixmap(pixmap)
                thumbnail_label.setGeometry(2, 2, 76, 50)
                thumbnail_label.setStyleSheet("border: none;")
                
                # 时间标签
                time_label = QLabel(f"{i/self.fps:.0f}s", container)
                time_label.setAlignment(Qt.AlignCenter)
                time_label.setGeometry(2, 52, 76, 16)
                time_label.setStyleSheet("""
                    background-color: #1a1a1a;
                    color: #ffffff;
                    font-size: 9px;
                    font-weight: bold;
                    border: none;
                """)
                
                # 添加点击事件
                container.mousePressEvent = lambda event, frame_pos=i: self.on_thumbnail_click(frame_pos)
                
                self.thumbnail_layout.addWidget(container)
                self.thumbnails.append((i, container))
        
        cap.release()
        
        # 添加时间轴指示器
        if not hasattr(self, 'timeline_indicator'):
            self.timeline_indicator = QLabel(self.timeline_widget)
            self.timeline_indicator.setFixedSize(3, 70)
            self.timeline_indicator.setStyleSheet("""
                background-color: #007AFF;
                border: none;
            """)
            # 确保指示器在最顶层
            self.timeline_indicator.raise_()
            self.timeline_indicator.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            
            # 添加鼠标事件支持拖动
            self.timeline_indicator.mousePressEvent = self.on_indicator_press
            self.timeline_indicator.mouseMoveEvent = self.on_indicator_drag
            self.timeline_indicator.mouseReleaseEvent = self.on_indicator_release
            self.is_dragging = False
        self.timeline_indicator.hide()
    
    def clear_thumbnails(self):
        """清空缩略图"""
        # 清空缩略图列表
        self.thumbnails = []
        
        # 清空布局中的所有缩略图组件
        while self.thumbnail_layout.count():
            child = self.thumbnail_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 隐藏时间轴指示器
        if hasattr(self, 'timeline_indicator'):
            self.timeline_indicator.hide()
    
    def on_indicator_press(self, event):
        """指示器按下事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_x = event.x()
    
    def on_indicator_drag(self, event):
        """指示器拖动事件"""
        if self.is_dragging and hasattr(self, 'fps') and self.total_duration > 0:
            # 计算拖动距离
            delta_x = event.x() - self.drag_start_x
            current_x = self.timeline_indicator.x() + delta_x
            
            # 限制在时间轴范围内
            timeline_width = self.timeline_widget.width()
            current_x = max(0, min(current_x, timeline_width - 3))
            
            # 计算对应的时间位置
            progress = current_x / timeline_width
            frame_position = int(progress * self.total_duration * self.fps)
            
            # 更新指示器位置
            self.timeline_indicator.move(current_x, 0)
            self.drag_start_x = event.x()
            
            # 发送跳转信号
            if self.playback_window:
                if self.video_type == 'screen':
                    self.playback_window.seek_screen_video(frame_position)
                elif self.video_type == 'webcam':
                    self.playback_window.seek_webcam_video(frame_position)
    
    def on_indicator_release(self, event):
        """指示器释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
    
    def on_timeline_click(self, event):
        """时间轴点击事件"""
        if hasattr(self, 'fps') and self.total_duration > 0:
            # 计算点击位置对应的时间
            timeline_width = self.timeline_widget.width()
            click_x = event.x()
            progress = click_x / timeline_width
            frame_position = int(progress * self.total_duration * self.fps)
            
            # 发送跳转信号
            if self.playback_window:
                if self.video_type == 'screen':
                    self.playback_window.seek_screen_video(frame_position)
                elif self.video_type == 'webcam':
                    self.playback_window.seek_webcam_video(frame_position)
    
    def on_thumbnail_click(self, frame_position):
        """缩略图点击事件"""
        self.current_position = frame_position
        
        # 更新当前时间显示
        current_seconds = frame_position / self.fps
        current_minutes = int(current_seconds) // 60
        current_seconds = int(current_seconds) % 60
        self.current_time_label.setText(f"{current_minutes:02d}:{current_seconds:02d}")
        
        # 发送跳转信号
        if self.playback_window:
            if self.video_type == 'screen':
                self.playback_window.seek_screen_video(frame_position)
            elif self.video_type == 'webcam':
                self.playback_window.seek_webcam_video(frame_position)
    
    def update_position(self, frame_position):
        """更新当前位置"""
        if not hasattr(self, 'fps') or not self.thumbnails:
            return
            
        self.current_frame = frame_position
        
        # 更新当前时间显示
        current_seconds = frame_position / self.fps
        current_minutes = int(current_seconds) // 60
        current_seconds = int(current_seconds) % 60
        self.current_time_label.setText(f"{current_minutes:02d}:{current_seconds:02d}")
        
        # 更新时间轴指示器位置
        self.update_timeline_indicator(frame_position)
    
    def update_timeline_indicator(self, frame_position):
        """更新时间轴指示器位置"""
        if not hasattr(self, 'timeline_indicator') or not self.thumbnails:
            return
            
        # 计算指示器位置
        total_duration = self.total_duration
        if total_duration <= 0:
            return
            
        # 计算当前时间在总时间中的比例
        current_time = frame_position / self.fps
        progress = current_time / total_duration
        
        # 计算指示器在时间轴上的位置
        timeline_width = self.timeline_widget.width()
        indicator_x = int(progress * timeline_width)
        
        # 设置指示器位置并确保在最顶层
        self.timeline_indicator.move(indicator_x, 0)
        self.timeline_indicator.raise_()
        self.timeline_indicator.show()
    
    def set_fps(self, fps):
        """设置帧率"""
        self.fps = fps


class RecordInfoPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: #23272e;
                border-radius: 10px;
                border: 1px solid #444;
                color: #fff;
                padding: 18px 20px;
            }
            QLabel {
                color: #fff;
                font-size: 14px;
            }
            QPushButton {
                background: #23272e;
                color: #fff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background: #007AFF;
                color: #fff;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # 顶部：ID + toggle
        top_row = QHBoxLayout()
        self.id_label = QLabel("记录ID: ")
        self.id_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        top_row.addWidget(self.id_label)
        top_row.addStretch()
        self.toggle_btn = QPushButton("详情 ∨")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.clicked.connect(self.toggle_detail)
        top_row.addWidget(self.toggle_btn)
        layout.addLayout(top_row)

        # 详细内容区
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        detail_widget = QWidget()
        detail_layout = QFormLayout(detail_widget)
        detail_layout.setLabelAlignment(Qt.AlignRight)
        detail_layout.setFormAlignment(Qt.AlignTop)
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.input_label = QLabel()
        self.input_label.setWordWrap(True)
        detail_layout.addRow("题目：", self.question_label)
        detail_layout.addRow("用户输入：", self.input_label)
        self.detail_area.setWidget(detail_widget)
        layout.addWidget(self.detail_area)

    def toggle_detail(self):
        show = self.toggle_btn.isChecked()
        self.detail_area.setVisible(show)
        self.toggle_btn.setText("收起 ∧" if show else "详情 ∨")

    def set_info(self, record_id, question, user_input):
        self.id_label.setText(f"记录ID: {record_id}")
        self.question_label.setText(question)
        self.input_label.setText(user_input)


class VirtualKeyboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.key_buttons = {}
        layout = QGridLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        # QWERTY布局
        keys = [
            ['Esc', '', '', '', '', '', '', '', '', '', '', '', 'Backspace'],
            ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
            ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'Enter'],
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
            ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Fn', 'Menu', 'Ctrl']
        ]
        for row, row_keys in enumerate(keys):
            col = 0
            for key in row_keys:
                if key:
                    btn = QPushButton(key)
                    btn.setEnabled(False)
                    btn.setFixedHeight(32)
                    if key == 'Space':
                        btn.setFixedWidth(180)
                    else:
                        btn.setFixedWidth(36)
                    btn.setStyleSheet(self.default_style())
                    self.key_buttons[key.upper()] = btn
                    layout.addWidget(btn, row, col, 1, 1)
                col += 1
        self.setLayout(layout)
        self.setStyleSheet("background: #23272e; border-radius: 8px;")

    def default_style(self):
        return "QPushButton { background: #23272e; color: #fff; border: 1px solid #444; border-radius: 4px; }"

    def highlight_style(self):
        return "QPushButton { background: #007AFF; color: #fff; border: 2px solid #007AFF; border-radius: 4px; }"

    def highlight_keys(self, keys):
        # keys: List[str]，如['A', 'S', 'D']
        keyset = set(k.upper() for k in keys)
        logging.debug(f'VirtualKeyboard.highlight_keys: {keyset}')
        for k, btn in self.key_buttons.items():
            if k in keyset:
                btn.setStyleSheet(self.highlight_style())
            else:
                btn.setStyleSheet(self.default_style())


class VirtualKeyboardWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.85)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.keyboard = VirtualKeyboard()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.keyboard)
        self.setFixedSize(700, 220)


class PlaybackWindow(QWidget):
    """回放窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('数据采集系统 - 回放')
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(STYLE_SHEET)
        
        self.current_record = None
        self.screen_player = None
        self.webcam_player = None
        self.sync_mode = True  # 联动模式开关
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI - VSCode风格，整体侧边栏布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 顶部状态栏
        status_bar = QWidget()
        status_bar.setFixedHeight(32)
        status_bar.setStyleSheet("background: #23272e; border-bottom: 1px solid #222; color: #fff;")
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(8, 0, 8, 0)
        status_layout.setSpacing(8)
        self.left_toggle_btn = QPushButton("≡")
        self.left_toggle_btn.setFixedSize(28, 28)
        self.left_toggle_btn.setStyleSheet("QPushButton { background: #23272e; color: #fff; border: none; font-size: 18px; }")
        self.right_toggle_btn = QPushButton("→")
        self.right_toggle_btn.setFixedSize(28, 28)
        self.right_toggle_btn.setStyleSheet("QPushButton { background: #23272e; color: #fff; border: none; font-size: 18px; }")
        # 新增键盘按钮
        self.keyboard_btn = QPushButton("⌨")
        self.keyboard_btn.setFixedSize(28, 28)
        self.keyboard_btn.setStyleSheet("QPushButton { background: #23272e; color: #fff; border: none; font-size: 18px; }")
        self.keyboard_btn.clicked.connect(self.toggle_virtual_keyboard)
        status_layout.addWidget(self.left_toggle_btn)
        status_layout.addStretch()
        status_layout.addWidget(QLabel("数据采集系统 - 回放"))
        status_layout.addStretch()
        status_layout.addWidget(self.keyboard_btn)
        status_layout.addWidget(self.right_toggle_btn)
        main_layout.addWidget(status_bar)

        # 主Splitter(Qt.Horizontal)：左侧边栏、主内容区、右侧信息侧边栏
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setStyleSheet("QSplitter::handle { background-color: #404040; }")
        # 左侧边栏
        self.left_panel = QWidget()
        self.left_panel.setMinimumWidth(120)
        self.left_panel.setMaximumWidth(220)
        self.left_panel.setStyleSheet("background: #23272e; border-right: 1px solid #222;")
        self.left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_splitter.addWidget(self.left_panel)
        self.left_panel.setVisible(False)
        # 主内容区
        main_content = QWidget()
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setSpacing(0)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 视频区
        video_splitter = QSplitter(Qt.Horizontal)
        video_splitter.setStyleSheet("QSplitter::handle { background-color: #404040; }")
        screen_group = self.create_video_group("屏幕录制", "screen_video_label")
        video_splitter.addWidget(screen_group)
        webcam_group = self.create_video_group("摄像头录制", "webcam_video_label")
        video_splitter.addWidget(webcam_group)
        video_splitter.setSizes([800, 800])
        main_content_layout.addWidget(video_splitter)
        # 控制区
        control_layout = self.create_control_layout()
        main_content_layout.addWidget(control_layout)
        # 联动区
        sync_layout = self.create_sync_control_layout()
        main_content_layout.addWidget(sync_layout)
        # 时间轴区
        self.screen_timeline = None
        self.webcam_timeline = None
        timeline_splitter = QSplitter(Qt.Horizontal)
        timeline_splitter.setStyleSheet("QSplitter::handle { background-color: #404040; }")
        screen_timeline_panel = QWidget()
        screen_timeline_panel.setStyleSheet("background-color: #1e1e1e; border-right: 1px solid #404040;")
        screen_timeline_layout = QVBoxLayout(screen_timeline_panel)
        screen_timeline_layout.setSpacing(0)
        screen_timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.screen_timeline = TimelineWidget(None, 'screen')
        self.screen_timeline.playback_window = self
        screen_timeline_layout.addWidget(self.screen_timeline)
        timeline_splitter.addWidget(screen_timeline_panel)
        webcam_timeline_panel = QWidget()
        webcam_timeline_panel.setStyleSheet("background-color: #1e1e1e;")
        webcam_timeline_layout = QVBoxLayout(webcam_timeline_panel)
        webcam_timeline_layout.setSpacing(0)
        webcam_timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.webcam_timeline = TimelineWidget(None, 'webcam')
        self.webcam_timeline.playback_window = self
        webcam_timeline_layout.addWidget(self.webcam_timeline)
        timeline_splitter.addWidget(webcam_timeline_panel)
        timeline_splitter.setSizes([800, 800])
        main_content_layout.addWidget(timeline_splitter)
        main_splitter.addWidget(main_content)
        # 右侧信息侧边栏
        self.info_panel = RecordInfoPanel()
        self.info_panel.setMinimumWidth(300)
        self.info_panel.setMaximumWidth(400)
        self.info_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_splitter.addWidget(self.info_panel)
        self.info_panel.setVisible(False)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 8)
        main_splitter.setStretchFactor(2, 2)
        main_layout.addWidget(main_splitter)

        # toggle逻辑
        def toggle_left():
            self.left_panel.setVisible(not self.left_panel.isVisible())
        def toggle_right():
            self.info_panel.setVisible(not self.info_panel.isVisible())
        self.left_toggle_btn.clicked.connect(toggle_left)
        self.right_toggle_btn.clicked.connect(toggle_right)

        self.virtual_keyboard_window = None

    def create_video_group(self, title, label_name):
        """创建视频组 - Final Cut Pro风格（优化布局）"""
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 视频标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("background-color: #2d2d2d; border-bottom: 1px solid #404040;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #fff; font-weight: bold; font-size: 12px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addWidget(title_bar)
        
        # 视频显示区域
        video_label = QLabel("无视频文件")
        video_label.setAlignment(Qt.AlignCenter)
        video_label.setStyleSheet("background-color: #000; color: #666; font-size: 14px; border: none;")
        video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        setattr(self, label_name, video_label)
        layout.addWidget(video_label, 1)
        
        return group
    
    def create_control_layout(self):
        """创建控制布局 - Final Cut Pro风格"""
        control_panel = QWidget()
        control_panel.setFixedHeight(60)
        control_panel.setStyleSheet("background-color: #2d2d2d; border-top: 1px solid #404040;")
        
        layout = QHBoxLayout(control_panel)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # 播放控制按钮
        button_style = """
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 70px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #555555;
                border-color: #404040;
            }
        """
        
        self.play_btn = QPushButton("播放")
        self.play_btn.setStyleSheet(button_style)
        self.play_btn.clicked.connect(self.toggle_play)
        layout.addWidget(self.play_btn)
        
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setStyleSheet(button_style)
        self.pause_btn.clicked.connect(self.pause_video)
        self.pause_btn.setEnabled(False)
        layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setStyleSheet(button_style)
        self.stop_btn.clicked.connect(self.stop_video)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        # 时间显示
        time_style = """
            QLabel {
                background-color: #1a1a1a;
                color: #ffffff;
                padding: 8px 12px;
                border: 1px solid #404040;
                border-radius: 4px;
                font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
                font-weight: bold;
                min-width: 120px;
                font-size: 12px;
            }
        """
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet(time_style)
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        layout.addStretch()
        
        return control_panel
    
    def create_sync_control_layout(self):
        """创建联动控制布局 - Final Cut Pro风格"""
        sync_panel = QWidget()
        sync_panel.setFixedHeight(40)
        sync_panel.setStyleSheet("background-color: #2d2d2d; border-top: 1px solid #404040;")
        
        layout = QHBoxLayout(sync_panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 5, 20, 5)
        
        # 联动模式开关
        sync_label = QLabel("联动模式:")
        sync_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
        layout.addWidget(sync_label)
        
        sync_button_style = """
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px 12px;
                border-radius: 3px;
                font-weight: bold;
                min-width: 50px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #666666;
            }
            QPushButton:checked {
                background-color: #007AFF;
                border-color: #0056CC;
            }
            QPushButton:checked:hover {
                background-color: #0056CC;
            }
        """
        
        self.sync_btn = QPushButton("开启")
        self.sync_btn.setCheckable(True)
        self.sync_btn.setChecked(True)
        self.sync_btn.setStyleSheet(sync_button_style)
        self.sync_btn.clicked.connect(self.toggle_sync_mode)
        layout.addWidget(self.sync_btn)
        
        # 说明文字
        sync_desc = QLabel("(联动模式下，调整任一视频时间，其他视频同步调整)")
        sync_desc.setStyleSheet("color: #999999; font-size: 11px;")
        layout.addWidget(sync_desc)
        
        layout.addStretch()
        
        return sync_panel
    
    def load_record(self, record):
        self.current_record = record
        # 设置采集信息卡片内容
        record_id = record.get('id', '')
        question_content = record['question'].get('content', '')
        user_input = record.get('user_input', '')
        self.info_panel.set_info(record_id, question_content, user_input)
        # 记录录制起始时间戳 - 使用录制开始时间而不是数据保存时间
        self.record_start_timestamp = record.get('recording_start_time', record.get('timestamp', 0))
        logging.debug(f'load_record: record_start_timestamp={self.record_start_timestamp}, recording_start_time={record.get("recording_start_time")}, timestamp={record.get("timestamp")}')
        # 预处理keystrokes区间
        self.preprocess_keystroke_intervals()
        # 加载视频
        self.load_videos()

    def preprocess_keystroke_intervals(self):
        self.keystroke_intervals = []
        self.raw_keystroke_intervals = []
        
        # 添加调试信息
        logging.debug(f'preprocess_keystroke_intervals: current_record exists = {hasattr(self, "current_record")}')
        if hasattr(self, 'current_record'):
            logging.debug(f'preprocess_keystroke_intervals: current_record keys = {list(self.current_record.keys())}')
            logging.debug(f'preprocess_keystroke_intervals: keystrokes in record = {"keystrokes" in self.current_record}')
            logging.debug(f'preprocess_keystroke_intervals: raw_keystrokes in record = {"raw_keystrokes" in self.current_record}')
            if 'keystrokes' in self.current_record:
                logging.debug(f'preprocess_keystroke_intervals: keystrokes length = {len(self.current_record["keystrokes"])}')
            if 'raw_keystrokes' in self.current_record:
                logging.debug(f'preprocess_keystroke_intervals: raw_keystrokes length = {len(self.current_record["raw_keystrokes"])}')
        
        # 处理原有的input_tool_keystrokes
        if (hasattr(self, 'current_record') and 'keystrokes' in self.current_record 
            and self.current_record['keystrokes']):
            keystrokes = self.current_record['keystrokes']
            for i, k in enumerate(keystrokes):
                start = k['timestamp']
                end = keystrokes[i+1]['timestamp'] if i+1 < len(keystrokes) else self.current_record.get('timestamp', start+2)
                self.keystroke_intervals.append({'key': k['text'].upper(), 'start': start, 'end': end})
            logging.debug(f'Input tool keystroke intervals: {self.keystroke_intervals}')
        else:
            logging.warning('当前记录无input_tool_keystrokes数据')
        
        # 处理新增的raw_keystrokes
        if (hasattr(self, 'current_record') and 'raw_keystrokes' in self.current_record 
            and self.current_record['raw_keystrokes']):
            raw_keystrokes = self.current_record['raw_keystrokes']
            for i, k in enumerate(raw_keystrokes):
                # 跳过RELEASE类型
                if k.get('type') == 'RELEASE':
                    continue
                start = k['timestamp']
                end = raw_keystrokes[i+1]['timestamp'] if i+1 < len(raw_keystrokes) else self.current_record.get('timestamp', start+2)
                key_name = self._get_key_name( k['key'],k.get('text'))
                self.raw_keystroke_intervals.append({
                    'key': k.get('text').upper(), 
                    'type': k.get('type').upper(),
                    'modifiers': k.get('modifiers', ''),
                    'start': start, 
                    'end': end
                })
            logging.debug(f'Raw keystroke intervals: {self.raw_keystroke_intervals}')
        else:
            logging.warning('当前记录无raw_keystrokes数据')
    
    def _get_key_name(self, key_code, text):
        """将按键代码转换为可读的按键名称"""
        # 常用按键映射
        key_map = {
            32: 'SPACE',  # 空格
            13: 'ENTER',  # 回车
            8: 'BACKSPACE',  # 退格
            9: 'TAB',  # Tab
            27: 'ESC',  # Esc
            16: 'SHIFT',  # Shift
            17: 'CTRL',  # Ctrl
            18: 'ALT',  # Alt
            20: 'CAPSLOCK',  # Caps Lock
            37: 'LEFT',  # 左箭头
            38: 'UP',  # 上箭头
            39: 'RIGHT',  # 右箭头
            40: 'DOWN',  # 下箭头
        }
        
        # 字母键 (65-90)
        if 65 <= key_code <= 90:
            return chr(key_code)
        
        # 数字键 (48-57)
        if 48 <= key_code <= 57:
            return str(key_code - 48)
        
        # 功能键 (112-123)
        if 112 <= key_code <= 123:
            return f'F{key_code - 111}'
        
        # 其他按键
        return key_map.get(key_code, f'KEY_{key_code}')

    def load_videos(self):
        """加载视频"""
        # 停止当前播放
        self.stop_video()
        
        # 加载屏幕录制
        if self.current_record['screen_exists']:
            self.screen_player = VideoPlayer(self.current_record['screen_video'])
            if self.screen_player.open_video():
                self.screen_player.frame_ready.connect(self.on_screen_frame_ready)
                self.screen_player.video_finished.connect(self.on_video_finished)
                
                # 更新时间轴
                self.screen_timeline.video_path = self.current_record['screen_video']
                self.screen_timeline.playback_window = self
                self.screen_timeline.load_thumbnails()
                self.screen_timeline.set_fps(self.screen_player.fps)
                
                # 初始化时间轴位置
                self.screen_timeline.update_position(0)
            else:
                self.screen_video_label.setText("屏幕录制加载失败")
        else:
            self.screen_video_label.setText("无屏幕录制文件")
        
        # 加载摄像头录制
        if self.current_record['webcam_exists']:
            self.webcam_player = VideoPlayer(self.current_record['webcam_video'])
            if self.webcam_player.open_video():
                self.webcam_player.frame_ready.connect(self.on_webcam_frame_ready)
                self.webcam_player.video_finished.connect(self.on_video_finished)
                
                # 更新时间轴
                self.webcam_timeline.video_path = self.current_record['webcam_video']
                self.webcam_timeline.playback_window = self
                self.webcam_timeline.load_thumbnails()
                self.webcam_timeline.set_fps(self.webcam_player.fps)
                
                # 初始化时间轴位置
                self.webcam_timeline.update_position(0)
            else:
                self.webcam_video_label.setText("摄像头录制加载失败")
        else:
            self.webcam_video_label.setText("无摄像头录制文件")
    
    def toggle_play(self):
        """切换播放状态"""
        if self.play_btn.text() == "播放":
            self.play_video()
        else:
            self.pause_video()
    
    def play_video(self):
        """播放视频"""
        # 确保两个视频同时开始播放
        if self.screen_player:
            self.screen_player.play()
        if self.webcam_player:
            self.webcam_player.play()
        
        self.play_btn.setText("暂停")
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        
        # 重置时间显示
        self.time_label.setText("00:00 / 00:00")
    
    def pause_video(self):
        """暂停视频"""
        if self.screen_player:
            self.screen_player.pause()
        if self.webcam_player:
            self.webcam_player.pause()
        
        self.play_btn.setText("播放")
    
    def stop_video(self):
        """停止视频"""
        if self.screen_player:
            self.screen_player.stop()
        if self.webcam_player:
            self.webcam_player.stop()
        
        self.play_btn.setText("播放")
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        # 重置显示
        self.screen_video_label.setText("屏幕录制")
        self.webcam_video_label.setText("摄像头录制")
        self.time_label.setText("00:00 / 00:00")
    
    def seek_video(self, frame_position):
        """跳转视频"""
        if self.screen_player:
            self.screen_player.seek(frame_position)
        if self.webcam_player and self.sync_mode:
            self.webcam_player.seek(frame_position)
    
    def seek_screen_video(self, frame_position):
        """跳转屏幕录制视频"""
        if self.screen_player:
            self.screen_player.seek(frame_position)
        if self.webcam_player and self.sync_mode:
            self.webcam_player.seek(frame_position)
    
    def seek_webcam_video(self, frame_position):
        """跳转摄像头录制视频"""
        if self.webcam_player:
            self.webcam_player.seek(frame_position)
        if self.screen_player and self.sync_mode:
            self.screen_player.seek(frame_position)
    
    def toggle_sync_mode(self):
        """切换联动模式"""
        self.sync_mode = self.sync_btn.isChecked()
        if self.sync_mode:
            self.sync_btn.setText("开启")
        else:
            self.sync_btn.setText("关闭")
    
    def on_screen_frame_ready(self, pixmap, timestamp_ms):
        """屏幕录制帧就绪"""
        # 等比例缩放，保证画面不变形
        scaled_pixmap = pixmap.scaled(
            self.screen_video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.screen_video_label.setPixmap(scaled_pixmap)
        # 更新时间显示
        self.update_time_display(timestamp_ms)
        # 更新时间轴位置
        if self.screen_timeline:
            self.screen_timeline.update_position(self.screen_player.current_frame)
        # 同步虚拟键盘高亮
        current_time = timestamp_ms / 1000.0
        self.update_keyboard_highlight(current_time)
    
    def on_webcam_frame_ready(self, pixmap, timestamp_ms):
        """摄像头录制帧就绪"""
        # 等比例缩放，保证画面不变形
        scaled_pixmap = pixmap.scaled(
            self.webcam_video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.webcam_video_label.setPixmap(scaled_pixmap)
        # 更新时间轴位置
        if self.webcam_timeline:
            self.webcam_timeline.update_position(self.webcam_player.current_frame)
        # 同步虚拟键盘高亮
        current_time = timestamp_ms / 1000.0
        self.update_keyboard_highlight(current_time)
    
    def on_video_finished(self):
        """视频播放完成"""
        self.play_btn.setText("播放")
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
    
    def update_time_display(self, timestamp_ms):
        """更新时间显示"""
        current_seconds = timestamp_ms // 1000
        current_minutes = current_seconds // 60
        current_seconds %= 60
        
        # 计算总时长（以屏幕录制为准）
        if self.screen_player:
            total_frames = self.screen_player.total_frames
            total_seconds = int(total_frames / self.screen_player.fps)
            total_minutes = total_seconds // 60
            total_seconds %= 60
        else:
            total_minutes = 0
            total_seconds = 0
        
        time_text = f"{current_minutes:02d}:{current_seconds:02d} / {total_minutes:02d}:{total_seconds:02d}"
        self.time_label.setText(time_text)
    
    def closeEvent(self, event):
        """关闭事件"""
        self.stop_video()
        if self.screen_player:
            self.screen_player.close()
        if self.webcam_player:
            self.webcam_player.close()
        event.accept()

    def toggle_virtual_keyboard(self):
        if self.virtual_keyboard_window is None:
            self.virtual_keyboard_window = VirtualKeyboardWindow(self)
        if self.virtual_keyboard_window.isVisible():
            self.virtual_keyboard_window.hide()
        else:
            self.virtual_keyboard_window.show()
            self.virtual_keyboard_window.raise_()
            self.virtual_keyboard_window.activateWindow()

    def update_keyboard_highlight(self, current_time):
        # 区间高亮，current_time为回放进度（秒）
        global_time = current_time
        highlight = []
        
        # 优先使用raw_keystrokes（更底层的记录）
        if hasattr(self, 'raw_keystroke_intervals') and self.raw_keystroke_intervals:
            for interval in self.raw_keystroke_intervals:
                if interval['start'] <= global_time < interval['end']:
                    highlight = [interval['key']]
                    logging.debug(f'Raw keystroke highlight: {interval}')
                    break
        # 如果没有raw_keystrokes，则使用原有的keystrokes
        elif hasattr(self, 'keystroke_intervals') and self.keystroke_intervals:
            for interval in self.keystroke_intervals:
                if interval['start'] <= global_time < interval['end']:
                    highlight = [interval['key']]
                    logging.debug(f'Input tool keystroke highlight: {interval}')
                    break
        else:
            logging.warning('当前记录无按键数据（keystrokes 和 raw_keystrokes 都为空）')
            logging.debug(f'update_keyboard_highlight: keystroke_intervals exists = {hasattr(self, "keystroke_intervals")}')
            logging.debug(f'update_keyboard_highlight: raw_keystroke_intervals exists = {hasattr(self, "raw_keystroke_intervals")}')
            if hasattr(self, 'keystroke_intervals'):
                logging.debug(f'update_keyboard_highlight: keystroke_intervals length = {len(self.keystroke_intervals)}')
            if hasattr(self, 'raw_keystroke_intervals'):
                logging.debug(f'update_keyboard_highlight: raw_keystroke_intervals length = {len(self.raw_keystroke_intervals)}')
        
        logging.debug(f'update_keyboard_highlight: current_time={current_time}, global_time={global_time}, highlight={highlight}')
        if self.virtual_keyboard_window and self.virtual_keyboard_window.isVisible():
            self.virtual_keyboard_window.keyboard.highlight_keys(highlight) 