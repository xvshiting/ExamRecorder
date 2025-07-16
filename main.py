import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 使用重构后的主窗口
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec_()) 