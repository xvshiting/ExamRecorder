import logging
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt


class VirtualKeyboard(QWidget):
    """虚拟键盘控件 - 纯UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.key_buttons = {}
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QGridLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # QWERTY布局
        keys = [
            ['Esc', '', '', '', '', '', '', '', '', '', '', '', 'Backspace'],
            ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
            ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'Enter'],
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
            ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Fn', 'Menu', 'Ctrl']
        ]
        
        for row, row_keys in enumerate(keys):
            col = 0
            for key in row_keys:
                if key:
                    btn = QPushButton(key)
                    btn.setEnabled(False)
                    btn.setFixedHeight(32)
                    if key == 'Space':
                        btn.setFixedWidth(180)
                    else:
                        btn.setFixedWidth(36)
                    btn.setStyleSheet(self.default_style())
                    self.key_buttons[key.upper()] = btn
                    layout.addWidget(btn, row, col, 1, 1)
                col += 1
        
        self.setLayout(layout)
        self.setStyleSheet("background: #23272e; border-radius: 8px;")
    
    def default_style(self):
        """默认样式"""
        return "QPushButton { background: #23272e; color: #fff; border: 1px solid #444; border-radius: 4px; }"
    
    def highlight_style(self):
        """高亮样式"""
        return "QPushButton { background: #007AFF; color: #fff; border: 2px solid #007AFF; border-radius: 4px; }"
    
    def highlight_keys(self, keys):
        """高亮指定按键
        Args:
            keys: List[str]，如['A', 'S', 'D']
        """
        keyset = set(k.upper() for k in keys)
        logging.debug(f'VirtualKeyboard.highlight_keys: {keyset}')
        for k, btn in self.key_buttons.items():
            if k in keyset:
                btn.setStyleSheet(self.highlight_style())
            else:
                btn.setStyleSheet(self.default_style())


class VirtualKeyboardWindow(QWidget):
    """虚拟键盘窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.85)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.keyboard = VirtualKeyboard()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.keyboard)
        self.setFixedSize(700, 220)
    
    def highlight_keys(self, keys):
        """高亮指定按键"""
        self.keyboard.highlight_keys(keys) 