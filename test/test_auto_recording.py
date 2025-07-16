#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动录制功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    print("测试说明:")
    print("1. 连接webcam设备")
    print("2. 点击'开始'按钮")
    print("3. 系统会自动同时开始屏幕录制和webcam录制")
    print("4. 输入答案后点击'提交'")
    print("5. 检查data目录中是否生成了两个视频文件")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 