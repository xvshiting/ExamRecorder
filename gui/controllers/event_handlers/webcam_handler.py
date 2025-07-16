import time
import os
import logging
from PyQt5.QtWidgets import QMessageBox


class WebcamEventHandler:
    """摄像头事件处理器"""
    
    def __init__(self, controller):
        self.controller = controller
    
    def refresh_webcams(self):
        """刷新webcam设备列表"""
        self.controller.main_view.clear_webcam_devices()
        devices = self.controller.webcam_manager.discover_webcams()
        
        if not devices:
            self.controller.main_view.add_webcam_device("未发现设备", None)
        else:
            for device in devices:
                text = f"摄像头 {device['index']} ({device['resolution']})"
                self.controller.main_view.add_webcam_device(text, device['index'])
    
    def toggle_webcam_connection(self):
        """切换webcam连接状态"""
        if self.controller.webcam_manager.cap is None:
            # 连接设备
            current_index = self.controller.main_view.get_selected_webcam_device()
            if current_index is not None:
                if self.controller.webcam_manager.connect_webcam(current_index):
                    self.controller.main_view.set_webcam_connect_button_text("断开")
                    self.controller.main_view.set_webcam_preview_button_enabled(True)
                    self.controller.main_view.set_webcam_snapshot_button_enabled(True)
                    self.controller.main_view.set_webcam_record_button_enabled(True)
                    self.controller.main_view.set_recording_fps_enabled(True)
                    self.controller.main_view.set_recording_mode_enabled(True)
                    
                    # 自动开始预览
                    if self.controller.webcam_manager.start_capture():
                        self.controller.main_view.set_webcam_preview_button_text("停止预览")
        else:
            # 断开连接
            if self.controller.webcam_recorder.is_recording():
                self.controller.webcam_recorder.stop_recording()
            self.controller.webcam_manager.disconnect_webcam()
            self.controller.main_view.set_webcam_connect_button_text("连接")
            self.controller.main_view.set_webcam_preview_button_text("开始预览")
            self.controller.main_view.set_webcam_preview_button_enabled(False)
            self.controller.main_view.set_webcam_snapshot_button_enabled(False)
            self.controller.main_view.set_webcam_record_button_text("开始录制")
            self.controller.main_view.set_webcam_record_button_enabled(False)
            self.controller.main_view.set_recording_fps_enabled(False)
            self.controller.main_view.set_recording_mode_enabled(False)
            self.controller.main_view.set_webcam_display_text("摄像头未连接")
    
    def toggle_webcam_preview(self):
        """切换webcam预览状态"""
        if not self.controller.webcam_manager.is_running:
            if self.controller.webcam_manager.start_capture():
                self.controller.main_view.set_webcam_preview_button_text("停止预览")
        else:
            self.controller.webcam_manager.stop_capture()
            self.controller.main_view.set_webcam_preview_button_text("开始预览")
    
    def take_webcam_snapshot(self):
        """拍摄webcam快照"""
        frame = self.controller.webcam_manager.get_snapshot()
        if frame is not None:
            # 保存图片到data目录
            os.makedirs('data', exist_ok=True)
            timestamp = int(time.time())
            filename = f"data/webcam_snapshot_{timestamp}.jpg"
            import cv2
            cv2.imwrite(filename, frame)
            QMessageBox.information(self.controller.main_window, "拍照成功", f"图片已保存为: {filename}")
        else:
            QMessageBox.warning(self.controller.main_window, "拍照失败", "无法获取图像")
    
    def toggle_webcam_recording(self):
        """切换webcam录制状态"""
        # 如果正在采集数据，不允许手动控制录制
        if self.controller.data_model.is_collecting():
            QMessageBox.information(self.controller.main_window, "提示", "正在采集数据中，请等待完成后再手动控制录制")
            return
            
        # 检查是否正在使用webcam显示录制器
        if self.controller.recording_model.is_webcam_recording():
            QMessageBox.information(self.controller.main_window, "提示", "正在使用webcam预览框录制，请等待完成后再手动控制录制")
            return
            
        if not self.controller.webcam_recorder.is_recording():
            # 开始录制
            fps = self.controller.main_view.get_recording_fps()
            if self.controller.webcam_recorder.start_recording(fps=fps):
                self.controller.main_view.set_webcam_record_button_text("停止录制")
                self.controller.main_view.set_webcam_record_button_style("background-color: #ff4444; color: white;")
        else:
            # 停止录制
            if self.controller.webcam_recorder.stop_recording():
                self.controller.main_view.set_webcam_record_button_text("开始录制")
                self.controller.main_view.set_webcam_record_button_style("") 