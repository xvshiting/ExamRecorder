#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试webcam预览框边框变化效果

这个脚本专门用于测试webcam预览框在录制时的边框变化效果：
1. 验证录制开始时边框变为蓝色
2. 验证录制结束时边框恢复正常
3. 验证与输入框边框效果的一致性
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow

def show_border_test_info():
    """显示边框测试信息"""
    info = """
=== Webcam预览框边框变化测试 ===

测试目标：
1. 验证录制开始时webcam预览框边框变为蓝色
2. 验证录制结束时边框恢复正常
3. 验证与输入框边框效果的一致性

边框效果说明：
- 正常状态：灰色边框 (2px solid #ccc)
- 录制状态：蓝色边框 (3px solid #00BFFF)，圆角效果
- 与输入框录制时的边框效果完全一致

测试步骤：
1. 连接webcam设备
2. 确保选择"录制预览框区域"模式
3. 点击"开始"按钮
4. 观察webcam预览框边框是否变为蓝色
5. 观察输入框边框是否也变为蓝色
6. 输入答案后点击"提交"
7. 观察两个边框是否都恢复正常

预期结果：
- 录制开始时，两个区域边框都变为蓝色
- 录制结束时，两个区域边框都恢复正常
- 边框效果完全一致，视觉体验统一

注意事项：
- 确保webcam预览框在录制时不被遮挡
- 观察边框变化的时机是否正确
- 验证边框样式的视觉效果
    """
    print(info)

def main():
    app = QApplication(sys.argv)
    
    # 显示测试信息
    show_border_test_info()
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 显示测试指导
    QMessageBox.information(window, "边框变化测试", 
                           "欢迎测试webcam预览框边框变化效果！\n\n"
                           "测试重点：\n"
                           "1. 观察录制开始时边框变化\n"
                           "2. 对比输入框和webcam预览框的边框效果\n"
                           "3. 验证录制结束时边框恢复正常\n\n"
                           "请按照控制台中的说明进行操作。")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 