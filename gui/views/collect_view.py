from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, 
    QSizePolicy, QFrame, QComboBox, QGroupBox, QGridLayout, QSpinBox, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPixmap

from ..utils.styles import FONT_TITLE, FONT_CONTENT, FONT_INPUT
from ..widgets.question_display import QuestionDisplayWidget
from ..widgets.input_section import InputSectionWidget
from ..widgets.control_buttons import ControlButtonsWidget
from ..widgets.webcam_control import WebcamControlWidget
from ..widgets.recording_control import RecordingControlWidget
from ..widgets.webcam_display import WebcamDisplayWidget


class CollectView(QWidget):
    """采集视图 - 业务组件"""
    
    # 信号定义
    start_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    webcam_refresh_clicked = pyqtSignal()
    webcam_connect_clicked = pyqtSignal()
    webcam_preview_clicked = pyqtSignal()
    webcam_snapshot_clicked = pyqtSignal()
    webcam_record_clicked = pyqtSignal()
    keystroke_mode_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化UI"""
        # 左侧：题目+输入+按钮
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)
        left_layout.setContentsMargins(20, 20, 10, 20)
        self.question_display = QuestionDisplayWidget()
        left_layout.addWidget(self.question_display)
        self.input_section = InputSectionWidget()
        left_layout.addWidget(self.input_section)
        self.control_buttons = ControlButtonsWidget()
        left_layout.addWidget(self.control_buttons)
        # 不加addStretch(1)
        left_widget.setLayout(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 右侧：摄像头相关
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(10, 20, 20, 20)
        self.webcam_control = WebcamControlWidget()
        right_layout.addWidget(self.webcam_control)
        self.recording_control = RecordingControlWidget()
        right_layout.addWidget(self.recording_control)
        self.webcam_display = WebcamDisplayWidget()
        right_layout.addWidget(self.webcam_display)
        # 不加addStretch(1)
        right_widget.setLayout(right_layout)
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 水平分割
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([8, 2])  # 初始比例8:2，题目区更大

        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
    def connect_signals(self):
        """连接信号"""
        # 控制按钮信号
        self.control_buttons.start_btn.clicked.connect(self.start_clicked.emit)
        self.control_buttons.next_btn.clicked.connect(self.next_clicked.emit)
        
        # Webcam控制信号
        self.webcam_control.refresh_webcam_btn.clicked.connect(self.webcam_refresh_clicked.emit)
        self.webcam_control.webcam_connect_btn.clicked.connect(self.webcam_connect_clicked.emit)
        self.webcam_control.webcam_preview_btn.clicked.connect(self.webcam_preview_clicked.emit)
        self.webcam_control.webcam_snapshot_btn.clicked.connect(self.webcam_snapshot_clicked.emit)
        
        # 录制控制信号
        self.recording_control.webcam_record_btn.clicked.connect(self.webcam_record_clicked.emit)
        
        # 按键监听方式切换
        self.input_section.keystroke_mode_combo.currentIndexChanged.connect(
            lambda: self.keystroke_mode_changed.emit(self.input_section.get_keystroke_mode())
        )
    
    # 题目显示相关方法
    def update_question(self, question_content, answer_content):
        """更新题目和答案显示"""
        self.question_display.update_question(question_content, answer_content)
    
    # 输入区域相关方法
    def get_input_content(self):
        """获取输入内容"""
        return self.input_section.get_input_content()
    
    def clear_input(self):
        """清空输入"""
        self.input_section.clear_input()
    
    def set_input_readonly(self, readonly):
        """设置输入框只读状态"""
        self.input_section.set_readonly(readonly)
    
    def set_input_focus(self):
        """设置输入框焦点"""
        self.input_section.set_focus()
    
    def set_input_recording_style(self, is_recording):
        """设置输入框录制样式"""
        self.input_section.set_recording_style(is_recording)
    
    def update_input_content(self, content):
        """更新输入内容并将光标移到末尾"""
        input_box = self.input_section.input_box
        input_box.setPlainText(content)
        cursor = input_box.textCursor()
        cursor.movePosition(cursor.End)
        input_box.setTextCursor(cursor)
    
    def get_input_box(self):
        """获取输入框对象"""
        return self.input_section.input_box
    
    def install_input_event_filter(self, event_filter_object):
        """安装输入框事件过滤器"""
        self.input_section.install_event_filter(event_filter_object)
    
    def get_input_widget(self):
        return self.input_section
    
    # 控制按钮相关方法
    def set_start_button_text(self, text):
        """设置开始按钮文本"""
        self.control_buttons.start_btn.setText(text)
    
    def set_start_button_enabled(self, enabled):
        """设置开始按钮启用状态"""
        self.control_buttons.start_btn.setEnabled(enabled)
    
    def set_next_button_enabled(self, enabled):
        """设置下一题按钮启用状态"""
        self.control_buttons.next_btn.setEnabled(enabled)
    
    # Webcam控制相关方法
    def clear_webcam_devices(self):
        """清空webcam设备列表"""
        self.webcam_control.webcam_combo.clear()
    
    def add_webcam_device(self, text, data):
        """添加webcam设备"""
        self.webcam_control.webcam_combo.addItem(text, data)
    
    def get_selected_webcam_device(self):
        """获取选中的webcam设备"""
        return self.webcam_control.webcam_combo.currentData()
    
    def set_webcam_connect_button_text(self, text):
        """设置webcam连接按钮文本"""
        self.webcam_control.webcam_connect_btn.setText(text)
    
    def set_webcam_preview_button_text(self, text):
        """设置webcam预览按钮文本"""
        self.webcam_control.webcam_preview_btn.setText(text)
    
    def set_webcam_preview_button_enabled(self, enabled):
        """设置webcam预览按钮启用状态"""
        self.webcam_control.webcam_preview_btn.setEnabled(enabled)
    
    def set_webcam_snapshot_button_enabled(self, enabled):
        """设置webcam拍照按钮启用状态"""
        self.webcam_control.webcam_snapshot_btn.setEnabled(enabled)
    
    # 录制控制相关方法
    def get_recording_mode(self):
        """获取录制模式"""
        return self.recording_control.recording_mode_combo.currentText()
    
    def get_recording_fps(self):
        """获取录制帧率"""
        return self.recording_control.recording_fps_spin.value()
    
    def set_webcam_record_button_text(self, text):
        """设置webcam录制按钮文本"""
        self.recording_control.webcam_record_btn.setText(text)
    
    def set_webcam_record_button_style(self, style):
        """设置webcam录制按钮样式"""
        self.recording_control.webcam_record_btn.setStyleSheet(style)
    
    def set_webcam_record_button_enabled(self, enabled):
        """设置webcam录制按钮启用状态"""
        self.recording_control.webcam_record_btn.setEnabled(enabled)
    
    def set_recording_fps_enabled(self, enabled):
        """设置录制帧率启用状态"""
        self.recording_control.recording_fps_spin.setEnabled(enabled)
    
    def set_recording_mode_enabled(self, enabled):
        """设置录制模式启用状态"""
        self.recording_control.recording_mode_combo.setEnabled(enabled)
    
    def set_recording_status(self, status):
        """设置录制状态"""
        self.recording_control.recording_status_label.setText(status)
    
    def set_recording_info(self, info):
        """设置录制信息"""
        self.recording_control.recording_info_label.setText(info)
    
    # Webcam显示相关方法
    def update_webcam_frame(self, image):
        """更新webcam帧"""
        self.webcam_display.update_frame(image)
    
    def set_webcam_display_text(self, text):
        """设置webcam显示文本"""
        self.webcam_display.set_text(text)
    
    def set_webcam_recording_style(self, is_recording):
        """设置webcam录制样式"""
        self.webcam_display.set_recording_style(is_recording)
    
    def set_webcam_status(self, status):
        """设置webcam状态"""
        self.webcam_display.set_status(status)
    
    # 区域获取方法
    def get_input_box_region(self):
        """获取输入框区域"""
        # 获取输入框在屏幕上的位置
        input_box = self.input_section.input_box
        global_pos = input_box.mapToGlobal(input_box.rect().topLeft())
        size = input_box.size()
        
        return QRect(
            global_pos.x(),
            global_pos.y(),
            size.width(),
            size.height()
        )
    
    def get_webcam_display_widget(self):
        """获取webcam显示组件"""
        return self.webcam_display.webcam_display if hasattr(self, 'webcam_display') else None

    def get_webcam_display_region(self):
        """获取webcam显示区域"""
        # 获取webcam显示区域在屏幕上的位置
        webcam_display = self.webcam_display.webcam_display
        global_pos = webcam_display.mapToGlobal(webcam_display.rect().topLeft())
        size = webcam_display.size()
        
        return {
            'left': global_pos.x(),
            'top': global_pos.y(),
            'width': size.width(),
            'height': size.height()
        } 