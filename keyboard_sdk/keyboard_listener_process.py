import time
import logging
from multiprocessing import Process, Queue, Event
import threading

class KeyboardListenerProcess:
    """
    可复用的全局键盘监听SDK（pynput子进程实现）
    主进程通过 start/stop/get_keystrokes 控制和获取数据
    """
    def __init__(self):
        self.queue = Queue()
        self.process = None
        self.stop_event = Event()
        self._buffer = []
        self._poll_thread = None
        self._running = False

    def start(self):
        if self.process is not None and self.process.is_alive():
            return
        self.stop_event.clear()
        self.process = Process(target=self._run_listener, args=(self.queue, self.stop_event))
        self.process.start()
        self._buffer = []
        self._running = True
        self._poll_thread = threading.Thread(target=self._poll_queue, daemon=True)
        self._poll_thread.start()
        logging.info("KeyboardListenerProcess started.")

    def stop(self):
        if self.process is not None and self.process.is_alive():
            self.stop_event.set()
            self.process.join(timeout=2)
        self._running = False
        logging.info("KeyboardListenerProcess stopped.")

    def get_keystrokes(self):
        """获取并清空已监听到的按键数据"""
        data = self._buffer[:]
        self._buffer.clear()
        return data

    def _poll_queue(self):
        """后台线程：不断从队列取数据，放入本地buffer"""
        while self._running:
            try:
                while not self.queue.empty():
                    item = self.queue.get_nowait()
                    self._buffer.append(item)
                time.sleep(0.01)
            except Exception as e:
                logging.error(f"KeyboardListenerProcess _poll_queue error: {e}")

    @staticmethod
    def _run_listener(queue, stop_event):
        """子进程：用pynput监听所有按键，数据写入queue"""
        try:
            from pynput import keyboard
        except ImportError:
            queue.put({'error': 'pynput not installed'})
            return

        def on_press(key):
            KeyboardListenerProcess._record_key(queue, key, 'PRESS')

        def on_release(key):
            KeyboardListenerProcess._record_key(queue, key, 'RELEASE')

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        while not stop_event.is_set():
            time.sleep(0.05)
        listener.stop()

    @staticmethod
    def _record_key(queue, key, event_type):
        current_time = time.time()
        key_code = None
        key_text = ''
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
        keystroke = {
            'type': event_type,
            'key_code': key_code,
            'key_text': key_text,
            'modifiers': '',  # pynput不直接支持修饰键状态
            'absolute_timestamp': current_time
        }
        try:
            queue.put(keystroke)
        except Exception as e:
            pass  # 队列已关闭等异常忽略 