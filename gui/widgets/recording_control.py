from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox, QPushButton, QSpinBox
from ..utils.styles import FONT_CONTENT


class RecordingControlWidget(QWidget):
    """录制控制控件 - 纯UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QGridLayout()
        
        # 录制模式选择
        layout.addWidget(QLabel("录制模式:"), 0, 0)
        self.recording_mode_combo = QComboBox()
        self.recording_mode_combo.addItem("直接录制摄像头")
        self.recording_mode_combo.addItem("录制预览框区域")
        self.recording_mode_combo.setCurrentText("录制预览框区域")
        self.recording_mode_combo.setEnabled(False)
        layout.addWidget(self.recording_mode_combo, 0, 1)
        
        # 录制帧率设置
        layout.addWidget(QLabel("录制帧率:"), 1, 0)
        self.recording_fps_spin = QSpinBox()
        self.recording_fps_spin.setRange(1, 60)
        self.recording_fps_spin.setValue(30)
        self.recording_fps_spin.setEnabled(False)
        layout.addWidget(self.recording_fps_spin, 1, 1)
        
        # 开始/停止录制按钮
        self.webcam_record_btn = QPushButton("开始录制")
        self.webcam_record_btn.setFont(FONT_CONTENT)
        self.webcam_record_btn.setEnabled(False)
        layout.addWidget(self.webcam_record_btn, 0, 2, 2, 2)
        
        # 录制状态显示
        self.recording_status_label = QLabel("录制状态: 未录制")
        self.recording_status_label.setFont(FONT_CONTENT)
        layout.addWidget(self.recording_status_label, 2, 0, 1, 2)
        
        # 录制信息显示
        self.recording_info_label = QLabel("录制信息: -")
        self.recording_info_label.setFont(FONT_CONTENT)
        layout.addWidget(self.recording_info_label, 2, 2, 1, 2)
        
        self.setLayout(layout) 

    def _reset_collecting_state(self):
        """重置采集状态"""
        self.data_model.stop_collecting()
        # 更新UI状态
        self.main_view.set_input_readonly(True)
        self.main_view.set_start_button_text('开始')
        self.main_view.set_input_recording_style(False)
        self.main_view.set_next_button_enabled(True)
        # 再次强制刷新录制UI
        self._reset_recording_ui()