#!/usr/bin/env python3
"""
测试键盘监听器
"""

import time
import logging
from gui.keyboard_listener import KeyboardRecorder

# 设置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_keyboard_listener():
    """测试键盘监听器"""
    print("开始测试键盘监听器...")
    print("请按任意键，按 'q' 退出")
    
    recorder = KeyboardRecorder()
    recorder.connect_signals()
    
    try:
        # 开始记录
        recorder.start_recording()
        
        # 等待用户按键
        while True:
            time.sleep(0.1)
            keystrokes = recorder.get_keystrokes()
            if keystrokes:
                latest = keystrokes[-1]
                print(f"按键: {latest['key']} ({latest['text']}) 时间: {latest['timestamp']:.3f}s")
                
                # 如果按下 'q' 键，退出
                if latest['key'] == 'Q':
                    break
    
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        # 停止记录
        recorder.stop_recording()
        
        # 显示所有记录的按键
        all_keystrokes = recorder.get_keystrokes()
        print(f"\n总共记录了 {len(all_keystrokes)} 个按键:")
        for i, keystroke in enumerate(all_keystrokes):
            print(f"{i+1}. {keystroke['key']} ({keystroke['text']}) - {keystroke['timestamp']:.3f}s")

if __name__ == '__main__':
    test_keyboard_listener() 