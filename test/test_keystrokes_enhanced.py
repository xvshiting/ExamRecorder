#!/usr/bin/env python3
"""
测试增强的keystrokes记录功能
"""

import sys
import logging
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QEvent, QObject

# 设置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TestInputEventHandler(QObject):
    """测试输入事件处理器"""
    
    def __init__(self, collecting_callback):
        super().__init__()
        self.collecting_callback = collecting_callback
        self.keystrokes = []
        self.last_content = ""
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and self.collecting_callback():
            key = event.key()
            text = event.text()
            current_content = obj.toPlainText()
            
            # 记录按键信息
            current_time = time.time()
            keystroke_record = {
                'key': key,
                'text': text,
                'timestamp': current_time,
                'absolute_timestamp': current_time,
                'input_content': current_content
            }
            self.keystrokes.append(keystroke_record)
            print(f"按键: {key} ({text}) 时间: {current_time:.3f}s 内容: {current_content}")
            
        elif event.type() == QEvent.InputMethod and self.collecting_callback():
            current_content = obj.toPlainText()
            if current_content != self.last_content:
                current_time = time.time()
                keystroke_record = {
                    'key': 'IME',
                    'text': '',
                    'timestamp': current_time,
                    'absolute_timestamp': current_time,
                    'input_content': current_content
                }
                self.keystrokes.append(keystroke_record)
                print(f"输入法: IME 时间: {current_time:.3f}s 内容: {current_content}")
                self.last_content = current_content
        
        return False

class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.collecting = False
        self.init_ui()
        
        # 创建事件处理器
        self.event_handler = TestInputEventHandler(lambda: self.collecting)
        self.text_edit.installEventFilter(self.event_handler)
    
    def init_ui(self):
        self.setWindowTitle('增强Keystrokes测试')
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 状态标签
        self.status_label = QLabel('状态: 未开始采集')
        layout.addWidget(self.status_label)
        
        # 文本编辑框
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # 控制按钮
        self.toggle_btn = QPushButton('开始采集')
        self.toggle_btn.clicked.connect(self.toggle_collecting)
        layout.addWidget(self.toggle_btn)
        
        # 显示keystrokes按钮
        self.show_btn = QPushButton('显示keystrokes')
        self.show_btn.clicked.connect(self.show_keystrokes)
        layout.addWidget(self.show_btn)
        
        # 说明文字
        info_label = QLabel('说明：\n1. 点击"开始采集"后可以输入文字\n2. 支持中英文输入法\n3. 按"q"退出程序')
        layout.addWidget(info_label)
    
    def toggle_collecting(self):
        self.collecting = not self.collecting
        if self.collecting:
            self.status_label.setText('状态: 正在采集')
            self.toggle_btn.setText('停止采集')
            self.text_edit.setReadOnly(False)
            self.text_edit.setFocus()
            print("开始采集keystrokes")
        else:
            self.status_label.setText('状态: 未开始采集')
            self.toggle_btn.setText('开始采集')
            self.text_edit.setReadOnly(True)
            print("停止采集keystrokes")
    
    def show_keystrokes(self):
        print(f"\n总共记录了 {len(self.event_handler.keystrokes)} 个按键:")
        for i, keystroke in enumerate(self.event_handler.keystrokes):
            print(f"{i+1}. 按键:{keystroke['key']} 文本:'{keystroke['text']}' 时间:{keystroke['timestamp']:.3f}s 内容:'{keystroke['input_content']}'")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    print("测试窗口已显示，点击'开始采集'进行测试")
    sys.exit(app.exec_()) 