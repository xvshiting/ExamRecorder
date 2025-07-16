#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试同步录制功能

这个脚本专门用于测试屏幕录制和webcam录制的同步性：
1. 验证两个视频的时长是否一致
2. 验证录制开始时间是否同步
3. 验证预览功能是否正常工作
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow

def show_sync_test_info():
    """显示同步测试信息"""
    info = """
=== 同步录制测试 ===

测试目标：
1. 验证屏幕录制和webcam录制时长一致
2. 验证点击开始时自动开启预览
3. 验证两个视频文件同步开始和结束

测试步骤：
1. 连接webcam设备
2. 点击"开始"按钮
3. 观察是否自动开启预览
4. 输入答案（建议输入较长的内容，如20-30秒）
5. 点击"提交"按钮
6. 检查生成的视频文件时长

预期结果：
- 两个视频文件时长应该基本一致（误差<1秒）
- 点击开始时应该自动开启webcam预览
- 录制过程中webcam录制按钮应该显示"录制中..."

注意事项：
- 请确保webcam设备正常工作
- 建议录制时间不少于10秒以便观察差异
- 如果时长仍有差异，可能需要进一步调整同步机制
    """
    print(info)

def main():
    app = QApplication(sys.argv)
    
    # 显示测试信息
    show_sync_test_info()
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 显示测试指导
    QMessageBox.information(window, "同步录制测试", 
                           "欢迎进行同步录制测试！\n\n"
                           "测试重点：\n"
                           "1. 观察点击'开始'时是否自动开启预览\n"
                           "2. 录制较长时间（建议20-30秒）\n"
                           "3. 检查两个视频文件时长是否一致\n\n"
                           "请按照控制台中的说明进行操作。")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 