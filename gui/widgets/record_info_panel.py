from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QWidget, QFormLayout
)
from PyQt5.QtCore import Qt


class RecordInfoPanel(QFrame):
    """记录信息面板控件 - 纯UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet("""
            QFrame {
                background: #23272e;
                border-radius: 10px;
                border: 1px solid #444;
                color: #fff;
                padding: 18px 20px;
            }
            QLabel {
                color: #fff;
                font-size: 14px;
            }
            QPushButton {
                background: #23272e;
                color: #fff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background: #007AFF;
                color: #fff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # 顶部：ID + toggle
        top_row = QHBoxLayout()
        self.id_label = QLabel("记录ID: ")
        self.id_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        top_row.addWidget(self.id_label)
        top_row.addStretch()
        self.toggle_btn = QPushButton("详情 ∨")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.clicked.connect(self.toggle_detail)
        top_row.addWidget(self.toggle_btn)
        layout.addLayout(top_row)

        # 详细内容区
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        detail_widget = QWidget()
        detail_layout = QFormLayout(detail_widget)
        detail_layout.setLabelAlignment(Qt.AlignRight)
        detail_layout.setFormAlignment(Qt.AlignTop)
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.input_label = QLabel()
        self.input_label.setWordWrap(True)
        detail_layout.addRow("题目：", self.question_label)
        detail_layout.addRow("用户输入：", self.input_label)
        self.detail_area.setWidget(detail_widget)
        layout.addWidget(self.detail_area)

    def toggle_detail(self):
        """切换详情显示"""
        show = self.toggle_btn.isChecked()
        self.detail_area.setVisible(show)
        self.toggle_btn.setText("收起 ∧" if show else "详情 ∨")

    def set_info(self, record_id, question, user_input):
        """设置记录信息
        Args:
            record_id: 记录ID
            question: 题目内容
            user_input: 用户输入内容
        """
        self.id_label.setText(f"记录ID: {record_id}")
        self.question_label.setText(question)
        self.input_label.setText(user_input) 