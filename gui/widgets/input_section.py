from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox, QSizePolicy
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QTextCursor
from ..utils.styles import FONT_CONTENT, FONT_INPUT


class InputSectionWidget(QWidget):
    """输入区域控件 - 纯UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
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
        
        # 底层按键监听方式选择
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
        # 确保光标在开头
        cursor = self.input_box.textCursor()
        cursor.setPosition(0)
        self.input_box.setTextCursor(cursor)
    
    def set_readonly(self, readonly):
        """设置只读状态"""
        self.input_box.setReadOnly(readonly)
        if not readonly:
            # 当设置为可编辑时，确保光标在正确位置
            cursor = self.input_box.textCursor()
            if cursor.position() == 0:
                # 如果光标在开头，移动到文本末尾
                cursor.movePosition(QTextCursor.End)
                self.input_box.setTextCursor(cursor)
    
    def set_focus(self):
        """设置焦点"""
        self.input_box.setFocus()
        # 确保光标在正确位置
        if not self.input_box.isReadOnly():
            cursor = self.input_box.textCursor()
            if cursor.position() == 0 and self.input_box.toPlainText():
                # 如果光标在开头但有文本，移动到末尾
                cursor.movePosition(QTextCursor.End)
                self.input_box.setTextCursor(cursor)
    
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
    
    def get_cursor_position(self):
        """获取当前光标位置"""
        return self.input_box.textCursor().position()
    
    def set_cursor_position(self, position):
        """设置光标位置"""
        cursor = self.input_box.textCursor()
        cursor.setPosition(position)
        self.input_box.setTextCursor(cursor) 