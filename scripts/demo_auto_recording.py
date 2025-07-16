#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动录制功能演示

这个脚本演示了如何使用新增的自动录制功能：
1. 点击"开始"按钮自动同时录制屏幕和webcam
2. 生成两个等长的视频文件
3. 保存对应的数据文件
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow

def show_demo_info():
    """显示演示信息"""
    info = """
=== 自动录制功能演示 ===

功能特点：
1. 点击"开始"按钮自动同时录制屏幕和webcam
2. 两个视频使用相同时间戳，确保文件名对应
3. 录制时长完全一致
4. 自动保存到data目录

使用步骤：
1. 连接webcam设备（可选）
2. 点击"开始"按钮
3. 在输入框中输入答案
4. 点击"提交"按钮
5. 检查data目录中的文件

生成的文件：
- data/sample_{timestamp}.mp4 (屏幕录制)
- data/webcam_{timestamp}.mp4 (webcam录制)
- data/sample_{timestamp}.json (数据文件)

注意事项：
- 如果webcam未连接，仅录制屏幕
- 录制过程中webcam录制按钮会被禁用
- 两个视频文件时长完全一致
    """
    print(info)

def main():
    app = QApplication(sys.argv)
    
    # 显示演示信息
    show_demo_info()
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 显示欢迎消息
    QMessageBox.information(window, "自动录制演示", 
                           "欢迎使用自动录制功能演示！\n\n"
                           "请按照以下步骤操作：\n"
                           "1. 连接webcam设备（可选）\n"
                           "2. 点击'开始'按钮\n"
                           "3. 输入答案后点击'提交'\n"
                           "4. 检查data目录中的文件")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 