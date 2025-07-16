import time
import logging
from PyQt5.QtCore import QObject, QEvent, QTimer, Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QKeyEvent
from keyboard_sdk.keyboard_listener_process import KeyboardListenerProcess

# 新增pynput导入
try:
    from pynput import keyboard as pynput_keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

class KeyboardListenerQt(QObject):
    """基于PyQt事件的底层键盘监听器"""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.raw_keystrokes = []
        self.is_listening = False
        
    def start_listening(self):
        """开始监听"""
        if not self.is_listening:
            self.is_listening = True
            self.raw_keystrokes = []
            QApplication.instance().installEventFilter(self)
            logging.debug("KeyboardListenerQt已启动")
    
    def stop_listening(self):
        """停止监听"""
        if self.is_listening:
            self.is_listening = False
            QApplication.instance().removeEventFilter(self)
            logging.debug("KeyboardListenerQt已停止")
    
    def eventFilter(self, obj, event):
        """全局事件过滤器，捕获所有按键事件"""
        if not self.is_listening or not self.controller.data_model.is_collecting():
            return False
            
        if event.type() == QEvent.KeyPress:
            # 记录所有按键按下事件
            self._record_raw_keystroke(event, 'PRESS')
        elif event.type() == QEvent.KeyRelease:
            # 记录所有按键释放事件
            self._record_raw_keystroke(event, 'RELEASE')
            
        return False  # 不阻止事件传播
    
    def _record_raw_keystroke(self, event, event_type):
        """记录原始按键事件"""
        if not isinstance(event, QKeyEvent):
            return
            
        current_time = time.time()
        
        # 获取按键信息
        key = event.key()
        text = event.text()
        modifiers = event.modifiers()
        
        # 构建修饰键字符串
        modifier_list = []
        if modifiers & Qt.ShiftModifier:
            modifier_list.append('SHIFT')
        if modifiers & Qt.ControlModifier:
            modifier_list.append('CTRL')
        if modifiers & Qt.AltModifier:
            modifier_list.append('ALT')
        if modifiers & Qt.MetaModifier:
            modifier_list.append('META')
            
        modifier_str = '+'.join(modifier_list) if modifier_list else ''
        
        # 获取输入框内容
        input_content = self.controller.main_view.get_input_content()
        
        # 创建原始按键记录 - 统一字段名
        raw_keystroke = {
            'type': event_type,
            'key_code': key,  # 统一使用key_code
            'key_text': text,  # 统一使用key_text
            'modifiers': modifier_str,
            'timestamp': current_time,
            'absolute_timestamp': current_time,
            'input_content': input_content
        }
        
        # 如果有录制开始时间，计算相对时间
        if self.controller.data_model.recording_start_time is not None:
            raw_keystroke['timestamp'] = current_time - self.controller.data_model.recording_start_time
        
        self.raw_keystrokes.append(raw_keystroke)
        
        # 同时添加到数据模型
        self.controller.add_raw_keystroke(raw_keystroke)
        
        logging.debug(f"KeyboardListenerQt原始按键记录: {raw_keystroke}")
    
    def get_raw_keystrokes(self):
        """获取原始按键记录"""
        return self.raw_keystrokes.copy()
    
    def clear_raw_keystrokes(self):
        """清空原始按键记录"""
        self.raw_keystrokes = []

class KeyboardListenerPynput:
    """基于pynput的全局键盘监听器"""
    def __init__(self, controller):
        self.controller = controller
        self.raw_keystrokes = []
        self.is_listening = False
        self.listener = None
        
    def start_listening(self):
        if not HAS_PYNPUT:
            logging.warning('未安装pynput，无法使用全局监听')
            return
        if not self.is_listening:
            try:
                self.is_listening = True
                self.raw_keystrokes = []
                self.listener = pynput_keyboard.Listener(
                    on_press=self._on_press,
                    on_release=self._on_release
                )
                self.listener.start()
                logging.debug("KeyboardListenerPynput已启动")
            except Exception as e:
                logging.error(f'pynput监听启动失败: {e}')
                self.is_listening = False
                
    def stop_listening(self):
        if self.is_listening and self.listener:
            try:
                self.is_listening = False
                self.listener.stop()
                self.listener = None
                logging.debug("KeyboardListenerPynput已停止")
            except Exception as e:
                logging.error(f'pynput监听停止失败: {e}')
                
    def _on_press(self, key):
        try:
            self._record_raw_keystroke(key, 'PRESS')
        except Exception as e:
            logging.error(f'pynput按键按下回调异常: {e}')
            
    def _on_release(self, key):
        try:
            self._record_raw_keystroke(key, 'RELEASE')
        except Exception as e:
            logging.error(f'pynput按键释放回调异常: {e}')
            
    def _record_raw_keystroke(self, key, event_type):
        if not self.controller.data_model.is_collecting():
            return
        current_time = time.time()
        key_code = None
        key_text = ''
        modifiers = []
        try:
            if hasattr(key, 'vk'):
                key_code = key.vk
            elif hasattr(key, 'value'):
                key_code = key.value.vk
            if hasattr(key, 'char') and key.char:
                key_text = key.char
            else:
                key_text = str(key)
        except Exception:
            key_text = str(key)
        raw_keystroke = {
            'type': event_type,
            'key_code': key_code,
            'key_text': key_text,
            'modifiers': '+'.join(modifiers),
            'timestamp': current_time,
            'absolute_timestamp': current_time,
            'input_content': self.controller.main_view.get_input_content()
        }
        if self.controller.data_model.recording_start_time is not None:
            raw_keystroke['timestamp'] = current_time - self.controller.data_model.recording_start_time
        self.raw_keystrokes.append(raw_keystroke)
        self.controller.add_raw_keystroke(raw_keystroke)
        logging.debug(f"KeyboardListenerPynput原始按键记录: {raw_keystroke}")
        
    def get_raw_keystrokes(self):
        return self.raw_keystrokes.copy()
        
    def clear_raw_keystrokes(self):
        self.raw_keystrokes = []

class KeyboardListenerPynputProcess:
    """包装KeyboardListenerProcess，适配主控制器接口"""
    def __init__(self, controller):
        self.controller = controller
        self.listener = KeyboardListenerProcess()
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self._poll_keystrokes)
        self.is_listening = False

    def start_listening(self):
        if not self.is_listening:
            try:
                self.is_listening = True
                self.listener.start()
                self.timer.start()
                logging.debug("KeyboardListenerPynputProcess已启动")
            except Exception as e:
                logging.error(f'KeyboardListenerPynputProcess启动失败: {e}')
                self.is_listening = False

    def stop_listening(self):
        if self.is_listening:
            try:
                self.is_listening = False
                self.timer.stop()
                self.listener.stop()
                logging.debug("KeyboardListenerPynputProcess已停止")
            except Exception as e:
                logging.error(f'KeyboardListenerPynputProcess停止失败: {e}')

    def _poll_keystrokes(self):
        """轮询获取按键事件"""
        if not self.is_listening:
            return
            
        try:
            keystrokes = self.listener.get_keystrokes()
            for keystroke in keystrokes:
                # 统一字段名
                if 'key_code' not in keystroke and 'key' in keystroke:
                    keystroke['key_code'] = keystroke.pop('key')
                if 'key_text' not in keystroke and 'text' in keystroke:
                    keystroke['key_text'] = keystroke.pop('text')
                
                # 添加输入框内容
                keystroke['input_content'] = self.controller.main_view.get_input_content()
                
                self.controller.add_raw_keystroke(keystroke)
        except Exception as e:
            logging.error(f'轮询按键事件失败: {e}')

    def get_raw_keystrokes(self):
        return []

    def clear_raw_keystrokes(self):
        pass 