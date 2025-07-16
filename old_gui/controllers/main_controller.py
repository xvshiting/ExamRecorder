import time
import logging
from PyQt5.QtWidgets import QMessageBox, QApplication
from ..models import DataCollectionModel, RecordingModel
from ..ui_builder import MainWindowUIBuilder
from ..event_handlers import WebcamEventHandler, RecordingEventHandler, InputEventHandler
from ..chinese_input_handler import ChineseInputHandler
from ..keyboard_listener import KeyboardListenerQt, KeyboardListenerPynputProcess
from ..region_utils import RegionUtils
from ..screen_recorder import ScreenRecorder
from ..webcam_manager import WebcamManager
from ..webcam_recorder import WebcamVideoRecorder
from ..webcam_display_recorder import WebcamDisplayRecorder


class MainController:
    """主控制器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        
        # 初始化模型
        self.data_model = DataCollectionModel()
        self.recording_model = RecordingModel(self.data_model)
        
        # 初始化UI构建器
        self.ui_builder = MainWindowUIBuilder()
        self.components = self.ui_builder.build_ui(main_window)
        
        # 初始化事件处理器
        self._init_event_handlers()
        
        # 初始化录制器
        self._init_recorders()
        
        # 初始化底层按键监听器
        self.keyboard_listener_qt = KeyboardListenerQt(self)
        self.keyboard_listener_pynput = KeyboardListenerPynputProcess(self)
        self.current_keyboard_listener = self.keyboard_listener_qt
        
        # 连接信号
        self._connect_signals()
        
        # 初始化webcam设备列表
        self.webcam_event_handler.refresh_webcams()
        
        # 加载第一题
        self.load_new_question()
    
    def _init_event_handlers(self):
        """初始化事件处理器"""
        self.webcam_event_handler = WebcamEventHandler(self)
        self.recording_event_handler = RecordingEventHandler(self)
        self.input_event_handler = InputEventHandler(self)
        self.chinese_input_handler = ChineseInputHandler(self)  # 添加中文输入法处理器
    
    def _init_recorders(self):
        """初始化录制器"""
        self.webcam_manager = WebcamManager()
        self.webcam_recorder = WebcamVideoRecorder(self.webcam_manager)
        
        # 设置录制模型
        self.recording_model.set_recorders(
            screen_recorder=None,  # 将在需要时创建
            webcam_recorder=self.webcam_recorder,
            webcam_manager=self.webcam_manager
        )
    
    def _connect_signals(self):
        """连接信号"""
        # Webcam管理器信号
        self.webcam_manager.frame_ready.connect(self.recording_event_handler.on_webcam_frame_ready)
        self.webcam_manager.webcam_connected.connect(self.recording_event_handler.on_webcam_connected)
        self.webcam_manager.webcam_disconnected.connect(self.recording_event_handler.on_webcam_disconnected)
        self.webcam_manager.error_occurred.connect(self.recording_event_handler.on_webcam_error)
        
        # Webcam录制器信号
        self.webcam_recorder.recording_started.connect(self.recording_event_handler.on_webcam_recording_started)
        self.webcam_recorder.recording_stopped.connect(self.recording_event_handler.on_webcam_recording_stopped)
        self.webcam_recorder.recording_error.connect(self.recording_event_handler.on_webcam_recording_error)
        self.webcam_recorder.frame_recorded.connect(self.recording_event_handler.on_webcam_frame_recorded)
        
        # 按钮信号
        self.components['control_buttons'].start_btn.clicked.connect(self.on_start_clicked)
        self.components['control_buttons'].next_btn.clicked.connect(self.load_new_question)
        
        # Webcam控制信号
        self.components['webcam_control'].refresh_webcam_btn.clicked.connect(self.webcam_event_handler.refresh_webcams)
        self.components['webcam_control'].webcam_connect_btn.clicked.connect(self.webcam_event_handler.toggle_webcam_connection)
        self.components['webcam_control'].webcam_preview_btn.clicked.connect(self.webcam_event_handler.toggle_webcam_preview)
        self.components['webcam_control'].webcam_snapshot_btn.clicked.connect(self.webcam_event_handler.take_webcam_snapshot)
        
        # 录制控制信号
        self.components['recording_control'].webcam_record_btn.clicked.connect(self.webcam_event_handler.toggle_webcam_recording)
        
        # 安装事件过滤器
        self.components['input_section'].install_event_filter(self.input_event_handler)
        # 安装中文输入法处理器（优先级更高）
        self.components['input_section'].install_event_filter(self.chinese_input_handler)
        
        # 监听底层按键监听方式切换
        self.components['input_section'].keystroke_mode_combo.currentIndexChanged.connect(self._on_keystroke_mode_changed)
    
    def _on_keystroke_mode_changed(self):
        """监听方式切换时，切换监听器"""
        mode = self.components['input_section'].get_keystroke_mode()
        # 停止当前监听器
        self.current_keyboard_listener.stop_listening()
        # 切换监听器
        if mode == 'pynput全局监听':
            self.current_keyboard_listener = self.keyboard_listener_pynput
        else:
            self.current_keyboard_listener = self.keyboard_listener_qt
        logging.info(f'底层按键监听方式切换为: {mode}')
    
    def load_new_question(self):
        """加载新题目"""
        question = self.data_model.load_new_question()
        if not question:
            QMessageBox.warning(self.main_window, '警告', '题库为空或没有符合条件的题目！')
            return
        
        # 更新UI
        self.components['question_display'].update_question(
            self.data_model.get_question_content(),
            self.data_model.get_question_answer()
        )
        self.components['input_section'].clear_input()
        self.components['input_section'].set_readonly(True)
        self.components['control_buttons'].start_btn.setText('开始')
        self.components['control_buttons'].start_btn.setEnabled(True)
        
        # 重置录制状态
        self._reset_recording_ui()
    
    def _reset_recording_ui(self):
        """重置录制UI状态"""
        self.recording_model.reset_recording_state()
        
        # 恢复webcam预览框正常样式
        self.components['webcam_display'].webcam_display.set_recording_style(False)
        self.components['recording_control'].webcam_record_btn.setText("开始录制")
        self.components['recording_control'].webcam_record_btn.setStyleSheet("")
        self.components['recording_control'].webcam_record_btn.setEnabled(True)
        self.components['recording_control'].recording_status_label.setText("录制状态: 未录制")
        self.components['recording_control'].recording_info_label.setText("录制信息: -")
        
        # 重置输入框样式
        self.components['input_section'].set_recording_style(False)
        self.components['control_buttons'].next_btn.setEnabled(True)
    
    def on_start_clicked(self):
        """开始/提交按钮点击事件"""
        if not self.data_model.is_collecting():
            self._start_collecting()
        else:
            self._submit_collecting()
    
    def _start_collecting(self):
        """开始采集"""
        self.data_model.start_collecting()
        
        # 启动当前选择的底层键盘监听器
        self.current_keyboard_listener.start_listening()
        
        # 更新UI状态
        self.components['input_section'].set_readonly(False)
        self.components['input_section'].set_focus()
        self.components['control_buttons'].start_btn.setText('提交')
        self.components['input_section'].set_recording_style(True)
        self.components['control_buttons'].next_btn.setEnabled(False)
        
        QMessageBox.information(self.main_window, '提示', '采集期间请勿遮挡或移动输入框，否则录制区域可能不准确。')
        
        # 准备录制
        self._prepare_recording()
        
        # 开始录制
        self._start_recording()
    
    def _prepare_recording(self):
        """准备录制"""
        # 等待预览稳定（如果webcam已连接并运行）
        if self.webcam_manager.cap and self.webcam_manager.cap.isOpened() and self.webcam_manager.is_running:
            QApplication.processEvents()
            time.sleep(0.5)
    
    def _start_recording(self):
        """开始录制"""
        # 设置录制开始时间（在实际开始录制时）
        self.data_model.set_recording_start_time()
        
        # 开始屏幕录制
        region = RegionUtils.get_input_box_region(self.components['input_section'])
        if not region:
            logging.error("无法获取输入框录制区域")
            QMessageBox.warning(self.main_window, '警告', '无法获取输入框录制区域，录制可能失败')
            return
            
        paths = self.data_model.get_recording_paths()
        
        logging.info(f"准备开始屏幕录制，区域: {region}")
        
        screen_recorder = ScreenRecorder(
            self.components['input_section'].input_box, 
            paths['screen_video'], 
            region, 
            fps=15, 
            start_time=self.data_model.recording_start_time
        )
        self.recording_model.screen_recorder = screen_recorder
        
        # 开始屏幕录制
        if self.recording_model.start_screen_recording(self.components['input_section'].input_box, region):
            logging.info("屏幕录制已启动")
        else:
            logging.error("屏幕录制启动失败")
            QMessageBox.warning(self.main_window, '警告', '屏幕录制启动失败')
        
        # 等待屏幕录制线程启动
        time.sleep(0.1)
        
        # 开始webcam录制
        self._start_webcam_recording()
    
    def _start_webcam_recording(self):
        """开始webcam录制"""
        if not (self.webcam_manager.cap and self.webcam_manager.cap.isOpened()):
            QMessageBox.information(self.main_window, '提示', 'webcam未连接，仅进行屏幕录制')
            return
        
        recording_mode = self.components['recording_control'].recording_mode_combo.currentText()
        
        if recording_mode == "录制预览框区域":
            self._start_webcam_display_recording()
        else:
            self._start_direct_webcam_recording()
    
    def _start_webcam_display_recording(self):
        """开始webcam预览框录制"""
        self.components['webcam_display'].webcam_display.set_recording_style(True)
        
        webcam_region = RegionUtils.get_webcam_display_region(self.components['webcam_display'])
        if not webcam_region:
            logging.error("无法获取webcam显示录制区域")
            QMessageBox.warning(self.main_window, '警告', '无法获取webcam显示录制区域，webcam录制可能失败')
            return
            
        paths = self.data_model.get_recording_paths()
        
        webcam_display_recorder = WebcamDisplayRecorder(
            self.components['webcam_display'].webcam_display, 
            paths['webcam_video'], 
            webcam_region, 
            fps=15,
            start_time=self.data_model.recording_start_time
        )
        self.recording_model.set_webcam_display_recorder(webcam_display_recorder)
        
        success, message = self.recording_model.start_webcam_recording(
            "录制预览框区域", 
            self.components['webcam_display'], 
            webcam_region
        )
        
        if success:
            self._update_recording_ui_state(True, "自动录制中", message)
        else:
            QMessageBox.warning(self.main_window, '警告', f'{message}，但屏幕录制已开始')
    
    def _start_direct_webcam_recording(self):
        """开始直接webcam录制"""
        fps = self.components['recording_control'].recording_fps_spin.value()
        paths = self.data_model.get_recording_paths()
        
        if self.webcam_recorder.start_recording(paths['webcam_video'], fps=fps, start_time=self.data_model.recording_start_time):
            self._update_recording_ui_state(True, "自动录制中", "直接录制摄像头")
        else:
            QMessageBox.warning(self.main_window, '警告', 'webcam录制启动失败，但屏幕录制已开始')
    
    def _update_recording_ui_state(self, is_recording, status_text, info_text):
        """更新录制UI状态"""
        if is_recording:
            self.components['recording_control'].webcam_record_btn.setText("录制中...")
            self.components['recording_control'].webcam_record_btn.setStyleSheet("background-color: #ff4444; color: white;")
            self.components['recording_control'].webcam_record_btn.setEnabled(False)
        else:
            self.components['recording_control'].webcam_record_btn.setText("开始录制")
            self.components['recording_control'].webcam_record_btn.setStyleSheet("")
            self.components['recording_control'].webcam_record_btn.setEnabled(True)
            
        self.components['recording_control'].recording_status_label.setText(f"录制状态: {status_text}")
        self.components['recording_control'].recording_info_label.setText(f"录制信息: {info_text}")
    
    def _submit_collecting(self):
        """提交采集"""
        user_input = self.components['input_section'].get_input_content()
        if not user_input.strip():
            QMessageBox.information(self.main_window, '提示', '请输入内容后再提交！')
            return
        
        # 停止录制
        self._stop_recording()
        
        # 保存数据
        webcam_recording_path = self.recording_model.stop_webcam_recording()
        filename = self.data_model.save_data(user_input, webcam_recording_path)
        
        # 显示完成信息
        self._show_completion_message(filename, webcam_recording_path)
        
        # 重置状态
        self._reset_collecting_state()
        
        # 重置录制UI状态
        self._reset_recording_ui()
    
    def _stop_recording(self):
        """停止录制"""
        logging.info("停止所有录制")
        self.recording_model.stop_screen_recording()
    
    def _show_completion_message(self, filename, webcam_recording_path):
        """显示完成信息"""
        paths = self.data_model.get_recording_paths()
        completion_message = f'已采集本题数据！\n数据已保存到 {filename}\n屏幕录制已保存到 {paths["screen_video"]}'
        if webcam_recording_path:
            completion_message += f'\nwebcam录制已保存到 {webcam_recording_path}'
        QMessageBox.information(self.main_window, '采集完成', completion_message)
    
    def _reset_collecting_state(self):
        """重置采集状态"""
        self.components['input_section'].set_readonly(True)
        self.components['input_section'].set_recording_style(False)
        self.components['control_buttons'].start_btn.setText('开始')
        self.data_model.stop_collecting()
        
        # 停止当前底层键盘监听器
        self.current_keyboard_listener.stop_listening()
        
        self.components['control_buttons'].next_btn.setEnabled(True)
    
    def add_keystroke(self, key, text, input_content):
        """添加按键记录"""
        # 添加调试日志
        logging.debug(f'MainController.add_keystroke called: key={key}, text="{text}", collecting={self.data_model.is_collecting()}')
        
        self.data_model.add_keystroke(key, text, input_content)
    
    def add_raw_keystroke(self, raw_keystroke):
        """添加原始按键记录"""
        # 添加调试日志
        logging.debug(f'MainController.add_raw_keystroke called: keystroke={raw_keystroke}, collecting={self.data_model.is_collecting()}')
        
        self.data_model.add_raw_keystroke(raw_keystroke) 