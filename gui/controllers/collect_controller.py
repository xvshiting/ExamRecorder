import time
import logging
from PyQt5.QtWidgets import QMessageBox, QApplication

from ..models import DataCollectionModel, RecordingModel
from ..views.collect_view import CollectView
from ..controllers.event_handlers.webcam_handler import WebcamEventHandler
from ..controllers.event_handlers.recording_handler import RecordingEventHandler
from ..controllers.event_handlers.input_handler import InputEventHandler
from ..controllers.event_handlers.chinese_input_handler import ChineseInputHandler
from ..services.input.keyboard_listener import KeyboardListenerQt, KeyboardListenerPynputProcess
from ..services.recording.screen_recorder import ScreenRecorder
from ..services.recording.webcam_manager import WebcamManager
from ..services.recording.webcam_recorder import WebcamVideoRecorder
from ..services.recording.webcam_display_recorder import WebcamDisplayRecorder


class CollectController:
    """采集控制器 - 核心协调逻辑"""
    
    def __init__(self, main_window, main_view=None):
        self.main_window = main_window
        
        # 初始化模型
        self.data_model = DataCollectionModel()
        self.recording_model = RecordingModel(self.data_model)
        
        # 初始化视图
        self.main_view = main_view if main_view is not None else CollectView(main_window)
        
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
        self.chinese_input_handler = ChineseInputHandler(self)
    
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
        
        # 视图信号
        self.main_view.start_clicked.connect(self.on_start_clicked)
        self.main_view.next_clicked.connect(self.load_new_question)
        self.main_view.webcam_refresh_clicked.connect(self.webcam_event_handler.refresh_webcams)
        self.main_view.webcam_connect_clicked.connect(self.webcam_event_handler.toggle_webcam_connection)
        self.main_view.webcam_preview_clicked.connect(self.webcam_event_handler.toggle_webcam_preview)
        self.main_view.webcam_snapshot_clicked.connect(self.webcam_event_handler.take_webcam_snapshot)
        self.main_view.webcam_record_clicked.connect(self.webcam_event_handler.toggle_webcam_recording)
        self.main_view.keystroke_mode_changed.connect(self._on_keystroke_mode_changed)
        
        # 安装事件过滤器
        self.main_view.install_input_event_filter(self.input_event_handler)
        self.main_view.install_input_event_filter(self.chinese_input_handler)
    
    def _on_keystroke_mode_changed(self, mode):
        """监听方式切换时，切换监听器"""
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
        
        # 更新视图
        self.main_view.update_question(
            self.data_model.get_question_content(),
            self.data_model.get_question_answer()
        )
        self.main_view.clear_input()
        self.main_view.set_input_readonly(True)
        self.main_view.set_start_button_text('开始')
        self.main_view.set_start_button_enabled(True)
        
        # 重置录制状态
        self._reset_recording_ui()
    
    def _reset_recording_ui(self):
        """重置录制UI状态"""
        self.recording_model.reset_recording_state()
        
        # 恢复webcam预览框正常样式
        self.main_view.set_webcam_recording_style(False)
        self.main_view.set_webcam_record_button_text("开始录制")
        self.main_view.set_webcam_record_button_style("")
        self.main_view.set_webcam_record_button_enabled(True)
        self.main_view.set_recording_status("录制状态: 未录制")
        self.main_view.set_recording_info("录制信息: -")
        
        # 重置输入框样式
        self.main_view.set_input_recording_style(False)
        self.main_view.set_next_button_enabled(True)
    
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
        self.main_view.set_input_readonly(False)
        self.main_view.set_input_focus()
        self.main_view.set_start_button_text('提交')
        self.main_view.set_input_recording_style(True)
        self.main_view.set_next_button_enabled(False)
        
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
        region_qrect = self.main_view.get_input_box_region()
        if not region_qrect:
            logging.error("无法获取输入框录制区域")
            QMessageBox.warning(self.main_window, '警告', '无法获取输入框录制区域，录制可能失败')
            return
        # 转换为dict
        region = {
            'left': region_qrect.left(),
            'top': region_qrect.top(),
            'width': region_qrect.width(),
            'height': region_qrect.height()
        }
        paths = self.data_model.get_recording_paths()
        
        # 创建屏幕录制器
        self.screen_recorder = ScreenRecorder(
            input_box_ref=self.main_view.get_input_widget(),
            output_path=paths['screen_video'],
            region=region
        )
        self.recording_model.set_screen_recorder(self.screen_recorder)
        
        # 开始录制
        self.screen_recorder.start()
        
        # 开始webcam录制
        self._start_webcam_recording()
    
    def _start_webcam_recording(self):
        """开始webcam录制"""
        recording_mode = self.main_view.get_recording_mode()
        
        if recording_mode == "录制预览框区域":
            self._start_webcam_display_recording()
        else:
            self._start_direct_webcam_recording()
    
    def _start_webcam_display_recording(self):
        """开始录制预览框区域"""
        if not self.webcam_manager.is_connected:
            logging.warning("Webcam未连接，跳过webcam录制")
            return
        
        # 获取预览框区域
        webcam_region = self.main_view.get_webcam_display_region()
        if not webcam_region:
            logging.warning("无法获取webcam预览框区域，跳过webcam录制")
            return
        
        # 创建webcam显示录制器
        paths = self.data_model.get_recording_paths()
        self.webcam_display_recorder = WebcamDisplayRecorder(
            webcam_display_ref=self.main_view.get_webcam_display_widget(),
            output_path=paths['webcam_video'],
            region=webcam_region
        )
        self.recording_model.set_webcam_display_recorder(self.webcam_display_recorder)
        
        # 开始录制
        self.webcam_display_recorder.start()
        
        # 更新UI状态
        self._update_recording_ui_state(True, "录制状态: 录制中", "录制信息: 屏幕+预览框")
    
    def _start_direct_webcam_recording(self):
        """开始直接录制摄像头"""
        if not self.webcam_manager.is_connected:
            logging.warning("Webcam未连接，跳过webcam录制")
            return
        
        # 开始录制
        paths = self.data_model.get_recording_paths()
        self.webcam_recorder.start_recording(paths['webcam_video'])
        
        # 更新UI状态
        self._update_recording_ui_state(True, "录制状态: 录制中", "录制信息: 屏幕+摄像头")
    
    def _update_recording_ui_state(self, is_recording, status_text, info_text):
        """更新录制UI状态"""
        self.main_view.set_webcam_recording_style(is_recording)
        self.main_view.set_webcam_record_button_text("停止录制" if is_recording else "开始录制")
        self.main_view.set_webcam_record_button_style(
            "background-color: #FF3B30; color: white;" if is_recording else ""
        )
        self.main_view.set_recording_status(status_text)
        self.main_view.set_recording_info(info_text)
    
    def _submit_collecting(self):
        """提交采集"""
        # 停止键盘监听
        self.current_keyboard_listener.stop_listening()
        
        # 停止录制
        self._stop_recording()
        
        # 保存数据
        user_input = self.main_view.get_input_content()
        webcam_recording_path = self.recording_model.stop_webcam_recording()
        self.data_model.save_data(user_input, webcam_recording_path)
        
        # 显示完成消息
        paths = self.data_model.get_recording_paths()
        self._show_completion_message(paths['screen_video'], paths['webcam_video'])
        
        # 重置采集状态
        self._reset_collecting_state()
    
    def _stop_recording(self):
        """停止录制"""
        self.recording_model.stop_screen_recording()
    
    def _show_completion_message(self, filename, webcam_recording_path):
        """显示完成消息"""
        message = f"采集完成！\n屏幕录制: {filename}"
        if webcam_recording_path:
            message += f"\n摄像头录制: {webcam_recording_path}"
        QMessageBox.information(self.main_window, '完成', message)
    
    def _reset_collecting_state(self):
        """重置采集状态"""
        self.data_model.stop_collecting()
        
        # 更新UI状态
        self.main_view.set_input_readonly(True)
        self.main_view.set_start_button_text('开始')
        self.main_view.set_input_recording_style(False)
        self.main_view.set_next_button_enabled(True)
    
    def add_keystroke(self, key, text, input_content):
        """添加按键记录"""
        self.data_model.add_keystroke(key, text, input_content)
        self.main_view.update_input_content(input_content)
    
    def add_raw_keystroke(self, raw_keystroke):
        """添加原始按键记录"""
        self.data_model.add_raw_keystroke(raw_keystroke) 