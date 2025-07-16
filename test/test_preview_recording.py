#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试webcam预览框录制功能

这个脚本专门用于测试新的webcam预览框录制功能：
1. 验证预览框录制与屏幕录制的同步性
2. 验证两种录制模式的选择
3. 验证录制时长的一致性
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow

def show_preview_test_info():
    """显示预览录制测试信息"""
    info = """
=== Webcam预览框录制测试 ===

新功能特点：
1. 新增"录制预览框区域"模式，与屏幕录制使用相同的录制机制
2. 两种录制模式可选：
   - 直接录制摄像头（原有功能）
   - 录制预览框区域（新功能，推荐使用）

测试目标：
1. 验证预览框录制与屏幕录制时长完全一致
2. 验证两种录制模式的选择功能
3. 验证录制过程的同步性

测试步骤：
1. 连接webcam设备
2. 选择录制模式（建议选择"录制预览框区域"）
3. 点击"开始"按钮
4. 观察是否自动开启预览
5. 输入答案（建议输入较长的内容，如20-30秒）
6. 点击"提交"按钮
7. 检查生成的视频文件时长

预期结果：
- 选择"录制预览框区域"时，两个视频文件时长应该完全一致
- 选择"直接录制摄像头"时，时长可能仍有差异
- 点击开始时应该自动开启webcam预览
- 录制过程中webcam录制按钮应该显示"录制中..."

推荐设置：
- 录制模式：录制预览框区域
- 录制帧率：15fps（与屏幕录制一致）
- 录制时长：20-30秒（便于观察差异）

技术说明：
- "录制预览框区域"使用与屏幕录制相同的mss库
- 两个录制器使用相同的帧率控制和时序机制
- 确保录制区域都是界面上的固定区域
    """
    print(info)

def main():
    app = QApplication(sys.argv)
    
    # 显示测试信息
    show_preview_test_info()
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 显示测试指导
    QMessageBox.information(window, "预览框录制测试", 
                           "欢迎测试webcam预览框录制功能！\n\n"
                           "测试重点：\n"
                           "1. 选择'录制预览框区域'模式\n"
                           "2. 观察点击'开始'时是否自动开启预览\n"
                           "3. 录制较长时间（建议20-30秒）\n"
                           "4. 检查两个视频文件时长是否完全一致\n\n"
                           "推荐使用'录制预览框区域'模式以获得最佳同步效果。")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 