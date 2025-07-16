from PyQt5.QtWidgets import QMessageBox


class RecordingEventHandler:
    """录制事件处理器"""
    
    def __init__(self, controller):
        self.controller = controller
    
    def on_webcam_frame_ready(self, image):
        """处理webcam新帧"""
        self.controller.main_view.update_webcam_frame(image)
    
    def on_webcam_connected(self, message):
        """处理webcam连接成功"""
        self.controller.main_view.set_webcam_status(f"摄像头状态: {message}")
    
    def on_webcam_disconnected(self):
        """处理webcam断开连接"""
        self.controller.main_view.set_webcam_status("摄像头状态: 已断开")
    
    def on_webcam_error(self, error_message):
        """处理webcam错误"""
        QMessageBox.warning(self.controller.main_window, "摄像头错误", error_message)
    
    def on_webcam_recording_started(self, message):
        """处理webcam录制开始"""
        self.controller.main_view.set_recording_status("录制状态: 录制中")
        self.controller.main_view.set_recording_info("录制信息: 开始录制...")
    
    def on_webcam_recording_stopped(self, message):
        """处理webcam录制停止"""
        self.controller.main_view.set_recording_status("录制状态: 录制完成")
        self.controller.main_view.set_recording_info(f"录制信息: {message}")
        
        # 只有在非采集状态下才显示录制完成信息
        if not self.controller.data_model.is_collecting():
            recording_path = self.controller.webcam_recorder.get_recording_path()
            if recording_path:
                QMessageBox.information(self.controller.main_window, "录制完成", f"视频已保存到: {recording_path}")
    
    def on_webcam_recording_error(self, error_message):
        """处理webcam录制错误"""
        self.controller.main_view.set_recording_status("录制状态: 录制错误")
        self.controller.main_view.set_recording_info(f"录制信息: {error_message}")
        QMessageBox.warning(self.controller.main_window, "录制错误", error_message)
    
    def on_webcam_frame_recorded(self, frame_count):
        """处理webcam录制帧数更新"""
        info = self.controller.webcam_recorder.get_recording_info()
        if info:
            duration = info['duration']
            self.controller.main_view.set_recording_info(f"录制信息: {frame_count} 帧, {duration:.1f}秒") 