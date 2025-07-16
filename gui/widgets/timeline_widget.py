import cv2
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage


class TimelineWidget(QWidget):
    """时间轴UI控件 - 纯UI组件"""
    
    # 信号定义
    timeline_clicked = pyqtSignal(int)  # 点击时间轴位置
    thumbnail_clicked = pyqtSignal(int)  # 点击缩略图位置
    indicator_dragged = pyqtSignal(int)  # 指示器拖动位置
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thumbnails = []
        self.current_position = 0
        self.total_duration = 0
        self.current_frame = 0
        self.fps = 0
        self.is_dragging = False
        self.init_ui()
    
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
        
        self.current_time_label = QLabel("00:00.00")
        self.current_time_label.setStyleSheet(time_label_style)
        self.current_time_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.current_time_label)
        
        self.total_time_label = QLabel("00:00.00")
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
        # 添加时间轴指示器（初始化就显示在0）
        if not hasattr(self, 'timeline_indicator'):
            self.timeline_indicator = QLabel(self.timeline_widget)
            self.timeline_indicator.setFixedSize(6, 70)
            self.timeline_indicator.setStyleSheet("""
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00c3ff, stop:1 #007AFF);
                border: none;
                border-radius: 3px;
                box-shadow: 0px 0px 8px #007AFF;
            """)
            self.timeline_indicator.move(0, 0)
            self.timeline_indicator.show()
            self.timeline_indicator.raise_()
            self.timeline_indicator.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.timeline_indicator.mousePressEvent = self.on_indicator_press
            self.timeline_indicator.mouseMoveEvent = self.on_indicator_drag
            self.timeline_indicator.mouseReleaseEvent = self.on_indicator_release
    
    def load_thumbnails(self, video_path):
        """加载缩略图"""
        if not video_path:
            return
            
        # 清空之前的缩略图
        self.clear_thumbnails()
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return
            
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.total_duration = total_frames / self.fps
        
        # 更新总时间显示
        total_minutes = int(self.total_duration) // 60
        total_seconds = int(self.total_duration) % 60
        total_ms = int((self.total_duration - int(self.total_duration)) * 100)
        self.total_time_label.setText(f"{total_minutes:02d}:{total_seconds:02d}.{total_ms:02d}")
        
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
                time_sec = i / self.fps
                m = int(time_sec) // 60
                s = int(time_sec) % 60
                ms = int((time_sec - int(time_sec)) * 100)
                time_label = QLabel(f"{m:02d}:{s:02d}.{ms:02d}", container)
                time_label.setAlignment(Qt.AlignCenter)
                time_label.setGeometry(2, 52, 76, 16)
                time_label.setStyleSheet("""
                    background-color: #1a1a1a;
                    color: #ffffff;
                    font-size: 10px;
                    font-weight: bold;
                    border: none;
                """)
                
                # 支持点击和双击
                def mousePressEvent(event, frame_pos=i):
                    if event.type() == event.MouseButtonDblClick:
                        self.thumbnail_clicked.emit(frame_pos)
                    elif event.type() == event.MouseButtonPress:
                        self.on_thumbnail_click(frame_pos)
                container.mousePressEvent = mousePressEvent
                
                self.thumbnail_layout.addWidget(container)
                self.thumbnails.append((i, container))
        
        cap.release()
        self.timeline_indicator.show()
        self.update_timeline_indicator(0)
    
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
            self.drag_start_x = event.globalX()
    
    def on_indicator_drag(self, event):
        """指示器拖动事件"""
        if self.is_dragging and hasattr(self, 'fps') and self.total_duration > 0:
            # 鼠标在timeline_widget中的绝对x
            global_pos = self.timeline_widget.mapFromGlobal(event.globalPos())
            current_x = global_pos.x()
            timeline_width = self.timeline_widget.width()
            current_x = max(0, min(current_x, timeline_width - self.timeline_indicator.width()))
            # 计算对应的时间位置
            progress = current_x / timeline_width
            frame_position = int(progress * self.total_duration * self.fps)
            # 更新指示器位置（始终在缩略图上方）
            self.timeline_indicator.move(current_x, 2)
            self.timeline_indicator.raise_()
            # 发送拖动信号
            self.indicator_dragged.emit(frame_position)
    
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
            
            # 发送点击信号
            self.timeline_clicked.emit(frame_position)
    
    def on_thumbnail_click(self, frame_position):
        """缩略图点击事件"""
        self.current_position = frame_position
        # 发送缩略图点击信号
        self.thumbnail_clicked.emit(frame_position)
    
    def update_position(self, frame_position):
        """更新播放位置"""
        self.current_position = frame_position
        
        # 更新当前时间显示
        if self.fps > 0:
            current_time = frame_position / self.fps
            minutes = int(current_time) // 60
            seconds = int(current_time) % 60
            ms = int((current_time - int(current_time)) * 100)
            self.current_time_label.setText(f"{minutes:02d}:{seconds:02d}.{ms:02d}")
        
        # 更新指示器位置
        self.update_timeline_indicator(frame_position)
    
    def update_timeline_indicator(self, frame_position):
        """更新时间轴指示器位置"""
        if hasattr(self, 'timeline_indicator') and self.total_duration > 0:
            # 计算指示器位置
            progress = frame_position / (self.total_duration * self.fps)
            timeline_width = self.timeline_widget.width()
            indicator_x = int(progress * timeline_width)
            indicator_x = max(0, min(indicator_x, timeline_width - self.timeline_indicator.width()))
            self.timeline_indicator.move(indicator_x, 2)
            self.timeline_indicator.raise_()
            self.timeline_indicator.show()
    
    def set_fps(self, fps):
        """设置帧率"""
        self.fps = fps 