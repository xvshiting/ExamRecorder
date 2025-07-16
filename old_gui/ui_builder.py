from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox
from .ui_components import (
    QuestionDisplayWidget, InputSectionWidget, ControlButtonsWidget,
    WebcamControlWidget, RecordingControlWidget, WebcamDisplayWidget
)
from .styles import FONT_CONTENT


class MainWindowUIBuilder:
    """主窗口UI构建器"""
    
    def __init__(self):
        self.components = {}
    
    def build_ui(self, main_window):
        """构建主窗口UI"""
        # 创建组件
        self._create_components()
        
        # 构建布局
        main_layout = self._build_main_layout()
        
        # 设置主布局
        main_window.setLayout(main_layout)
        
        # 返回组件引用供主窗口使用
        return self.components
    
    def _create_components(self):
        """创建所有UI组件"""
        self.components['question_display'] = QuestionDisplayWidget()
        self.components['input_section'] = InputSectionWidget()
        self.components['control_buttons'] = ControlButtonsWidget()
        self.components['webcam_control'] = WebcamControlWidget()
        self.components['recording_control'] = RecordingControlWidget()
        self.components['webcam_display'] = WebcamDisplayWidget()
    
    def _build_main_layout(self):
        """构建主布局"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(32, 32, 32, 32)
        
        # 左侧布局
        left_layout = self._build_left_layout()
        main_layout.addLayout(left_layout)
        
        # 右侧布局
        right_layout = self._build_right_layout()
        main_layout.addLayout(right_layout)
        
        return main_layout
    
    def _build_left_layout(self):
        """构建左侧布局"""
        left_layout = QVBoxLayout()
        left_layout.setSpacing(18)
        
        # 添加题目显示
        left_layout.addWidget(self.components['question_display'])
        
        # 添加输入区域
        left_layout.addWidget(self.components['input_section'])
        
        # 添加控制按钮
        left_layout.addWidget(self.components['control_buttons'])
        
        return left_layout
    
    def _build_right_layout(self):
        """构建右侧布局"""
        right_layout = QVBoxLayout()
        right_layout.setSpacing(18)
        
        # 摄像头控制组
        webcam_group = QGroupBox("摄像头控制")
        webcam_group.setFont(FONT_CONTENT)
        webcam_group_layout = QVBoxLayout(webcam_group)
        webcam_group_layout.addWidget(self.components['webcam_control'])
        right_layout.addWidget(webcam_group)
        
        # 录制控制组
        recording_group = QGroupBox("视频录制")
        recording_group.setFont(FONT_CONTENT)
        recording_group_layout = QVBoxLayout(recording_group)
        recording_group_layout.addWidget(self.components['recording_control'])
        right_layout.addWidget(recording_group)
        
        # 摄像头显示
        right_layout.addWidget(self.components['webcam_display'])
        
        return right_layout 