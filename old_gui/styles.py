from PyQt5.QtGui import QFont

STYLE_SHEET = '''
QWidget {
    background-color: #181C24;
    color: #E6EAF3;
}
QLabel {
    color: #7EC8E3;
}
QPushButton {
    background-color: #232A34;
    color: #7EC8E3;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 15px;
}
QPushButton:hover {
    background-color: #2D3748;
    color: #AEE6FB;
}
QTextEdit {
    background-color: #232A34;
    color: #E6EAF3;
    border-radius: 8px;
    font-size: 16px;
    padding: 8px;
}
QFrame#Line {
    background: #2D3748;
    max-height: 2px;
    min-height: 2px;
}
'''

FONT_TITLE = QFont('Arial', 18, QFont.Bold)
FONT_CONTENT = QFont('Arial', 14)
FONT_INPUT = QFont('Arial', 16)