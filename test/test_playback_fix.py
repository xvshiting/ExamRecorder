#!/usr/bin/env python3
"""
测试回放功能修复
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_selector import MainSelector

def test_playback_fix():
    """测试回放功能修复"""
    print("启动数据采集系统...")
    print("1. 选择'内容管理'进入管理模式")
    print("2. 在数据列表中找到有视频文件的记录")
    print("3. 点击'回放'按钮")
    print("4. 检查以下功能:")
    print("   - 视频是否从0秒开始播放")
    print("   - 缩略图区域是否足够大")
    print("   - 播放控制是否正常工作")
    print("   - 时间轴是否显示正确")
    
    app = QApplication(sys.argv)
    selector = MainSelector()
    selector.show()
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(test_playback_fix()) 