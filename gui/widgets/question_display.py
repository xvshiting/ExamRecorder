from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
from ..utils.styles import FONT_TITLE, FONT_CONTENT


class QuestionDisplayWidget(QWidget):
    """题目显示控件 - 纯UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setSpacing(18)
        
        self.question_label = QLabel('题目：')
        self.question_label.setFont(FONT_TITLE)
        self.question_label.setWordWrap(True)
        self.question_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.question_label)
        
        self.answer_label = QLabel('参考答案：')
        self.answer_label.setFont(FONT_CONTENT)
        self.answer_label.setWordWrap(True)
        self.answer_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.answer_label)
        
        line = QFrame()
        line.setObjectName('Line')
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)
        
        self.setLayout(layout)
    
    def update_question(self, question_content, answer_content):
        """更新题目和答案显示
        Args:
            question_content: 题目内容
            answer_content: 答案内容
        """
        self.question_label.setText(f"题目：{question_content}")
        if answer_content:
            self.answer_label.setText(f"参考答案：{answer_content}")
        else:
            self.answer_label.setText("参考答案：无") 