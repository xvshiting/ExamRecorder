from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox, 
    QSizePolicy, QHBoxLayout, QFrame, QComboBox, QGroupBox, QGridLayout, QSpinBox
)
from PyQt5.QtCore import QEvent
from .styles import FONT_TITLE, FONT_CONTENT, FONT_INPUT
from .webcam_manager import WebcamDisplay


class QuestionDisplayWidget(QWidget):
    """题目显示组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)
        
        self.question_label = QLabel('题目：')
        self.question_label.setFont(FONT_TITLE)
        layout.addWidget(self.question_label)
        
        self.answer_label = QLabel('参考答案：')
        self.answer_label.setFont(FONT_CONTENT)
        layout.addWidget(self.answer_label)
        
        line = QFrame()
        line.setObjectName('Line')
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)
        
        self.setLayout(layout)
    
    def update_question(self, question_content, answer_content):
        """更新题目和答案显示"""
        self.question_label.setText(f"题目：{question_content}")
        if answer_content:
            self.answer_label.setText(f"参考答案：{answer_content}")
        else:
            self.answer_label.setText("参考答案：无")


class InputSectionWidget(QWidget):
    """输入区域组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)
        
        self.input_label = QLabel('请输入你的答案：')
        self.input_label.setFont(FONT_CONTENT)
        layout.addWidget(self.input_label)
        
        self.input_box = QTextEdit()
        self.input_box.setFont(FONT_INPUT)
        self.input_box.setMinimumHeight(120)
        self.input_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.input_box.setReadOnly(True)
        layout.addWidget(self.input_box)
        
        # 新增：底层按键监听方式选择
        self.keystroke_mode_combo = QComboBox()
        self.keystroke_mode_combo.addItems(['PyQt事件监听', 'pynput全局监听'])
        self.keystroke_mode_combo.setToolTip('选择底层按键监听方式')
        layout.addWidget(QLabel('底层按键监听方式：'))
        layout.addWidget(self.keystroke_mode_combo)
        
        self.setLayout(layout)
    
    def get_input_content(self):
        """获取输入内容"""
        return self.input_box.toPlainText()
    
    def clear_input(self):
        """清空输入"""
        self.input_box.clear()
    
    def set_readonly(self, readonly):
        """设置只读状态"""
        self.input_box.setReadOnly(readonly)
    
    def set_focus(self):
        """设置焦点"""
        self.input_box.setFocus()
    
    def set_recording_style(self, is_recording):
        """设置录制样式"""
        if is_recording:
            self.input_box.setStyleSheet(
                'border: 3px solid #00BFFF; background-color: #232A34; '
                'color: #E6EAF3; border-radius: 8px; font-size: 16px; padding: 8px;'
            )
        else:
            self.input_box.setStyleSheet("")
    
    def install_event_filter(self, event_filter_object):
        """安装事件过滤器"""
        self.input_box.installEventFilter(event_filter_object)
    
    def get_keystroke_mode(self):
        """获取底层按键监听方式"""
        return self.keystroke_mode_combo.currentText()


class ControlButtonsWidget(QWidget):
    """控制按钮组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        self.start_btn = QPushButton('开始')
        self.start_btn.setFont(FONT_CONTENT)
        layout.addWidget(self.start_btn)
        
        self.next_btn = QPushButton('下一题')
        self.next_btn.setFont(FONT_CONTENT)
        layout.addWidget(self.next_btn)
        
        self.setLayout(layout)


class WebcamControlWidget(QWidget):
    """摄像头控制组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout()
        
        # 设备选择
        layout.addWidget(QLabel("选择设备:"), 0, 0)
        self.webcam_combo = QComboBox()
        self.webcam_combo.setMinimumWidth(150)
        layout.addWidget(self.webcam_combo, 0, 1)
        
        # 刷新按钮
        self.refresh_webcam_btn = QPushButton("刷新")
        self.refresh_webcam_btn.setFont(FONT_CONTENT)
        layout.addWidget(self.refresh_webcam_btn, 0, 2)
        
        # 连接/断开按钮
        self.webcam_connect_btn = QPushButton("连接")
        self.webcam_connect_btn.setFont(FONT_CONTENT)
        layout.addWidget(self.webcam_connect_btn, 0, 3)
        
        # 开始/停止预览按钮
        self.webcam_preview_btn = QPushButton("开始预览")
        self.webcam_preview_btn.setFont(FONT_CONTENT)
        self.webcam_preview_btn.setEnabled(False)
        layout.addWidget(self.webcam_preview_btn, 1, 0, 1, 2)
        
        # 拍照按钮
        self.webcam_snapshot_btn = QPushButton("拍照")
        self.webcam_snapshot_btn.setFont(FONT_CONTENT)
        self.webcam_snapshot_btn.setEnabled(False)
        layout.addWidget(self.webcam_snapshot_btn, 1, 2, 1, 2)
        
        self.setLayout(layout)


class RecordingControlWidget(QWidget):
    """录制控制组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout()
        
        # 录制模式选择
        layout.addWidget(QLabel("录制模式:"), 0, 0)
        self.recording_mode_combo = QComboBox()
        self.recording_mode_combo.addItem("直接录制摄像头")
        self.recording_mode_combo.addItem("录制预览框区域")
        self.recording_mode_combo.setCurrentText("录制预览框区域")
        self.recording_mode_combo.setEnabled(False)
        layout.addWidget(self.recording_mode_combo, 0, 1)
        
        # 录制帧率设置
        layout.addWidget(QLabel("录制帧率:"), 1, 0)
        self.recording_fps_spin = QSpinBox()
        self.recording_fps_spin.setRange(1, 60)
        self.recording_fps_spin.setValue(30)
        self.recording_fps_spin.setEnabled(False)
        layout.addWidget(self.recording_fps_spin, 1, 1)
        
        # 开始/停止录制按钮
        self.webcam_record_btn = QPushButton("开始录制")
        self.webcam_record_btn.setFont(FONT_CONTENT)
        self.webcam_record_btn.setEnabled(False)
        layout.addWidget(self.webcam_record_btn, 0, 2, 2, 2)
        
        # 录制状态显示
        self.recording_status_label = QLabel("录制状态: 未录制")
        self.recording_status_label.setFont(FONT_CONTENT)
        layout.addWidget(self.recording_status_label, 2, 0, 1, 2)
        
        # 录制信息显示
        self.recording_info_label = QLabel("录制信息: -")
        self.recording_info_label.setFont(FONT_CONTENT)
        layout.addWidget(self.recording_info_label, 2, 2, 1, 2)
        
        self.setLayout(layout)


class WebcamDisplayWidget(QWidget):
    """摄像头显示组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.webcam_display = WebcamDisplay()
        layout.addWidget(self.webcam_display)
        
        # Webcam状态
        self.webcam_status_label = QLabel("摄像头状态: 未连接")
        self.webcam_status_label.setFont(FONT_CONTENT)
        layout.addWidget(self.webcam_status_label)
        
        self.setLayout(layout) 