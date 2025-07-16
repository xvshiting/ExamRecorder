import os
import json
import glob
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QLabel, QLineEdit, QDateEdit, QTimeEdit, QMessageBox,
    QHeaderView, QSplitter, QTextEdit, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QDate, QTime, QDateTime
from PyQt5.QtGui import QFont
from .styles import FONT_TITLE, FONT_CONTENT, STYLE_SHEET
from .playback_window import PlaybackWindow


class DataManagerWindow(QWidget):
    """数据管理窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('数据采集系统 - 内容管理')
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(STYLE_SHEET)
        
        self.data_dir = 'data'
        self.records = []
        self.filtered_records = []
        self.playback_window = None
        
        self.init_ui()
        self.load_records()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel('采集内容管理')
        title_label.setFont(FONT_TITLE)
        layout.addWidget(title_label)
        
        # 搜索区域
        search_group = self.create_search_group()
        layout.addWidget(search_group)
        
        # 数据表格
        self.create_data_table()
        layout.addWidget(self.table)
        
        # 按钮区域
        button_layout = self.create_button_layout()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_search_group(self):
        """创建搜索组"""
        group = QGroupBox("搜索筛选")
        group.setFont(FONT_CONTENT)
        layout = QGridLayout(group)
        
        # 时间范围搜索
        layout.addWidget(QLabel("开始时间:"), 0, 0)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        layout.addWidget(self.start_date, 0, 1)
        
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(0, 0))
        layout.addWidget(self.start_time, 0, 2)
        
        layout.addWidget(QLabel("结束时间:"), 0, 3)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        layout.addWidget(self.end_date, 0, 4)
        
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(23, 59))
        layout.addWidget(self.end_time, 0, 5)
        
        # 关键词搜索
        layout.addWidget(QLabel("关键词:"), 1, 0)
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText("输入题目内容关键词")
        layout.addWidget(self.keyword_edit, 1, 1, 1, 3)
        
        # 搜索按钮
        search_btn = QPushButton("搜索")
        search_btn.setFont(FONT_CONTENT)
        search_btn.clicked.connect(self.search_records)
        layout.addWidget(search_btn, 1, 4)
        
        # 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.setFont(FONT_CONTENT)
        reset_btn.clicked.connect(self.reset_search)
        layout.addWidget(reset_btn, 1, 5)
        
        return group
    
    def create_data_table(self):
        """创建数据表格"""
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            '时间', '题目', '答案', '屏幕录制', '摄像头录制', '操作'
        ])
        
        # 设置表格属性
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 时间
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # 题目
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 答案
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 屏幕录制
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 摄像头录制
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 操作
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
    
    def create_button_layout(self):
        """创建按钮布局"""
        layout = QHBoxLayout()
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新数据")
        refresh_btn.setFont(FONT_CONTENT)
        refresh_btn.clicked.connect(self.load_records)
        layout.addWidget(refresh_btn)
        
        # 统计信息
        self.stats_label = QLabel("共 0 条记录")
        self.stats_label.setFont(FONT_CONTENT)
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
        
        return layout
    
    def load_records(self):
        """加载记录"""
        self.records = []
        
        if not os.path.exists(self.data_dir):
            return
        
        # 查找所有JSON文件
        json_files = glob.glob(os.path.join(self.data_dir, '*.json'))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取时间戳
                timestamp = data.get('timestamp', 0)
                record_time = datetime.fromtimestamp(timestamp)
                
                # 检查对应的视频文件是否存在
                screen_video = data.get('screen_video_path', '')
                webcam_video = data.get('webcam_video_path', '')
                
                screen_exists = os.path.exists(screen_video) if screen_video else False
                webcam_exists = os.path.exists(webcam_video) if webcam_video else False
                
                record = {
                    'json_file': json_file,
                    'timestamp': timestamp,
                    'record_time': record_time,
                    'question': data.get('question', {}),
                    'user_input': data.get('user_input', ''),
                    'keystrokes': data.get('keystrokes', []),  # 原有的input_tool_keystrokes
                    'raw_keystrokes': data.get('raw_keystrokes', []),  # 新增的底层keystrokes
                    'recording_start_time': data.get('recording_start_time', timestamp),  # 添加录制开始时间
                    'screen_video': screen_video,
                    'webcam_video': webcam_video,
                    'screen_exists': screen_exists,
                    'webcam_exists': webcam_exists
                }
                
                self.records.append(record)
                
            except Exception as e:
                print(f"加载记录失败 {json_file}: {e}")
        
        # 按时间倒序排序
        self.records.sort(key=lambda x: x['timestamp'], reverse=True)
        self.filtered_records = self.records.copy()
        
        self.update_table()
    
    def update_table(self):
        """更新表格"""
        self.table.setRowCount(len(self.filtered_records))
        
        for row, record in enumerate(self.filtered_records):
            # 时间
            time_str = record['record_time'].strftime('%Y-%m-%d %H:%M:%S')
            self.table.setItem(row, 0, QTableWidgetItem(time_str))
            
            # 题目
            question_content = record['question'].get('content', '')[:50] + '...' if len(record['question'].get('content', '')) > 50 else record['question'].get('content', '')
            self.table.setItem(row, 1, QTableWidgetItem(question_content))
            
            # 答案
            answer = record['question'].get('answer', '无')
            self.table.setItem(row, 2, QTableWidgetItem(answer))
            
            # 屏幕录制
            screen_status = "✓" if record['screen_exists'] else "✗"
            self.table.setItem(row, 3, QTableWidgetItem(screen_status))
            
            # 摄像头录制
            webcam_status = "✓" if record['webcam_exists'] else "✗"
            self.table.setItem(row, 4, QTableWidgetItem(webcam_status))
            
            # 操作按钮
            if record['screen_exists'] or record['webcam_exists']:
                play_btn = QPushButton("回放")
                play_btn.setFont(FONT_CONTENT)
                play_btn.clicked.connect(lambda checked, r=record: self.open_playback(r))
                self.table.setCellWidget(row, 5, play_btn)
        
        self.stats_label.setText(f"共 {len(self.filtered_records)} 条记录")
    
    def search_records(self):
        """搜索记录"""
        start_datetime = QDateTime(self.start_date.date(), self.start_time.time())
        end_datetime = QDateTime(self.end_date.date(), self.end_time.time())
        keyword = self.keyword_edit.text().strip().lower()
        
        self.filtered_records = []
        
        for record in self.records:
            # 时间过滤
            record_datetime = QDateTime.fromSecsSinceEpoch(int(record['timestamp']))
            if record_datetime < start_datetime or record_datetime > end_datetime:
                continue
            
            # 关键词过滤
            if keyword:
                question_content = record['question'].get('content', '').lower()
                user_input = record['user_input'].lower()
                if keyword not in question_content and keyword not in user_input:
                    continue
            
            self.filtered_records.append(record)
        
        self.update_table()
    
    def reset_search(self):
        """重置搜索"""
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_time.setTime(QTime(0, 0))
        self.end_date.setDate(QDate.currentDate())
        self.end_time.setTime(QTime(23, 59))
        self.keyword_edit.clear()
        
        self.filtered_records = self.records.copy()
        self.update_table()
    
    def open_playback(self, record):
        """打开回放窗口"""
        if not record['screen_exists'] and not record['webcam_exists']:
            QMessageBox.warning(self, "警告", "没有可播放的视频文件")
            return
        
        if not self.playback_window:
            self.playback_window = PlaybackWindow()
        
        self.playback_window.load_record(record)
        self.playback_window.show() 