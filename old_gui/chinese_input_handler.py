import time
import logging
from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtGui import QInputMethodEvent


class ChineseInputHandler(QObject):
    """中文输入法处理器"""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.last_content = ""
        self.pending_chars = []  # 待上屏的字符
        self.composition_text = ""  # 当前组合文本
        
    def eventFilter(self, obj, event):
        """增强的事件过滤器，专门处理中文输入法"""
        if obj == self.controller.components['input_section'].input_box and self.controller.data_model.is_collecting():
            
            if event.type() == QEvent.KeyPress:
                # 记录所有按键，包括中文输入法的按键
                key = event.key()
                text = event.text()
                current_content = self.controller.components['input_section'].input_box.toPlainText()
                
                # 记录按键信息
                self.controller.add_keystroke(key, text, current_content)
                
                # 如果是中文输入法的候选键（数字键1-9）
                if key >= 49 and key <= 57:  # 数字键1-9
                    self.controller.add_keystroke(f'CANDIDATE_{text}', text, current_content)
                
            elif event.type() == QEvent.InputMethod:
                # 处理输入法事件
                self._handle_input_method_event(event)
                
            elif event.type() == QEvent.KeyRelease:
                # 记录按键释放
                key = event.key()
                if key not in [16777216, 16777217, 16777218]:  # 排除特殊键
                    current_content = self.controller.components['input_section'].input_box.toPlainText()
                    self.controller.add_keystroke(f'RELEASE_{key}', '', current_content)
                    
        return False
    
    def _handle_input_method_event(self, event):
        """处理输入法事件"""
        if not isinstance(event, QInputMethodEvent):
            return
            
        current_content = self.controller.components['input_section'].input_box.toPlainText()
        
        # 获取输入法事件信息
        preedit_text = event.preeditString()  # 预编辑文本（拼音）
        commit_text = event.commitString()    # 提交文本（上屏文字）
        
        if preedit_text:
            # 有预编辑文本，说明正在输入拼音
            self.composition_text = preedit_text
            self.controller.add_keystroke(f'COMPOSITION_{preedit_text}', preedit_text, current_content)
            
        if commit_text:
            # 有提交文本，说明文字上屏
            self.controller.add_keystroke(f'COMMIT_{commit_text}', commit_text, current_content)
            
            # 检查内容变化
            if current_content != self.last_content:
                self.controller.add_keystroke('IME_CHANGE', '', current_content)
                self.last_content = current_content 