from PyQt5.QtCore import QEvent, QObject


class InputEventHandler(QObject):
    """输入事件处理器"""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.last_content = ""  # 记录上次的内容，用于检测变化
    
    def eventFilter(self, obj, event):
        if obj == self.controller.main_view.get_input_box() and self.controller.data_model.is_collecting():
            if event.type() == QEvent.KeyPress:
                # 记录物理按键
                key = event.key()
                text = event.text()
                current_content = self.controller.main_view.get_input_content()
                
                # 记录按键信息
                self.controller.add_keystroke(key, text, current_content)
                
            elif event.type() == QEvent.InputMethod:
                # 记录中文输入法事件
                current_content = self.controller.main_view.get_input_content()
                
                # 如果内容有变化，记录输入法上屏
                if current_content != self.last_content:
                    self.controller.add_keystroke('IME', '', current_content)
                    self.last_content = current_content
                    
            elif event.type() == QEvent.KeyRelease:
                # 记录按键释放（可选，用于更精确的按键记录）
                key = event.key()
                if key not in [16777216, 16777217, 16777218]:  # 排除一些特殊键
                    current_content = self.controller.main_view.get_input_content()
                    self.controller.add_keystroke(f'RELEASE_{key}', '', current_content)
                    
        return False 