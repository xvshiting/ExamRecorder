import time
import json as pyjson
import os
import logging
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtGui import QKeyEvent


class WebcamEventHandler:
    """摄像头事件处理器"""
    
    def __init__(self, controller):
        self.controller = controller
    
    def refresh_webcams(self):
        """刷新webcam设备列表"""
        self.controller.components['webcam_control'].webcam_combo.clear()
        devices = self.controller.webcam_manager.discover_webcams()
        
        if not devices:
            self.controller.components['webcam_control'].webcam_combo.addItem("未发现设备")
        else:
            for device in devices:
                text = f"摄像头 {device['index']} ({device['resolution']})"
                self.controller.components['webcam_control'].webcam_combo.addItem(text, device['index'])
    
    def toggle_webcam_connection(self):
        """切换webcam连接状态"""
        if self.controller.webcam_manager.cap is None:
            # 连接设备
            current_index = self.controller.components['webcam_control'].webcam_combo.currentData()
            if current_index is not None:
                if self.controller.webcam_manager.connect_webcam(current_index):
                    self.controller.components['webcam_control'].webcam_connect_btn.setText("断开")
                    self.controller.components['webcam_control'].webcam_preview_btn.setEnabled(True)
                    self.controller.components['webcam_control'].webcam_snapshot_btn.setEnabled(True)
                    self.controller.components['recording_control'].webcam_record_btn.setEnabled(True)
                    self.controller.components['recording_control'].recording_fps_spin.setEnabled(True)
                    self.controller.components['recording_control'].recording_mode_combo.setEnabled(True)
                    
                    # 自动开始预览
                    if self.controller.webcam_manager.start_capture():
                        self.controller.components['webcam_control'].webcam_preview_btn.setText("停止预览")
        else:
            # 断开连接
            if self.controller.webcam_recorder.is_recording():
                self.controller.webcam_recorder.stop_recording()
            self.controller.webcam_manager.disconnect_webcam()
            self.controller.components['webcam_control'].webcam_connect_btn.setText("连接")
            self.controller.components['webcam_control'].webcam_preview_btn.setText("开始预览")
            self.controller.components['webcam_control'].webcam_preview_btn.setEnabled(False)
            self.controller.components['webcam_control'].webcam_snapshot_btn.setEnabled(False)
            self.controller.components['recording_control'].webcam_record_btn.setText("开始录制")
            self.controller.components['recording_control'].webcam_record_btn.setEnabled(False)
            self.controller.components['recording_control'].recording_fps_spin.setEnabled(False)
            self.controller.components['recording_control'].recording_mode_combo.setEnabled(False)
            self.controller.components['webcam_display'].webcam_display.setText("摄像头未连接")
    
    def toggle_webcam_preview(self):
        """切换webcam预览状态"""
        if not self.controller.webcam_manager.is_running:
            if self.controller.webcam_manager.start_capture():
                self.controller.components['webcam_control'].webcam_preview_btn.setText("停止预览")
        else:
            self.controller.webcam_manager.stop_capture()
            self.controller.components['webcam_control'].webcam_preview_btn.setText("开始预览")
    
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
            fps = self.controller.components['recording_control'].recording_fps_spin.value()
            if self.controller.webcam_recorder.start_recording(fps=fps):
                self.controller.components['recording_control'].webcam_record_btn.setText("停止录制")
                self.controller.components['recording_control'].webcam_record_btn.setStyleSheet("background-color: #ff4444; color: white;")
        else:
            # 停止录制
            if self.controller.webcam_recorder.stop_recording():
                self.controller.components['recording_control'].webcam_record_btn.setText("开始录制")
                self.controller.components['recording_control'].webcam_record_btn.setStyleSheet("")


class RecordingEventHandler:
    """录制事件处理器"""
    
    def __init__(self, controller):
        self.controller = controller
    
    def on_webcam_frame_ready(self, image):
        """处理webcam新帧"""
        self.controller.components['webcam_display'].webcam_display.update_frame(image)
    
    def on_webcam_connected(self, message):
        """处理webcam连接成功"""
        self.controller.components['webcam_display'].webcam_status_label.setText(f"摄像头状态: {message}")
    
    def on_webcam_disconnected(self):
        """处理webcam断开连接"""
        self.controller.components['webcam_display'].webcam_status_label.setText("摄像头状态: 已断开")
    
    def on_webcam_error(self, error_message):
        """处理webcam错误"""
        QMessageBox.warning(self.controller.main_window, "摄像头错误", error_message)
    
    def on_webcam_recording_started(self, message):
        """处理webcam录制开始"""
        self.controller.components['recording_control'].recording_status_label.setText("录制状态: 录制中")
        self.controller.components['recording_control'].recording_info_label.setText("录制信息: 开始录制...")
    
    def on_webcam_recording_stopped(self, message):
        """处理webcam录制停止"""
        self.controller.components['recording_control'].recording_status_label.setText("录制状态: 录制完成")
        self.controller.components['recording_control'].recording_info_label.setText(f"录制信息: {message}")
        
        # 只有在非采集状态下才显示录制完成信息
        if not self.controller.data_model.is_collecting():
            recording_path = self.controller.webcam_recorder.get_recording_path()
            if recording_path:
                QMessageBox.information(self.controller.main_window, "录制完成", f"视频已保存到: {recording_path}")
    
    def on_webcam_recording_error(self, error_message):
        """处理webcam录制错误"""
        self.controller.components['recording_control'].recording_status_label.setText("录制状态: 录制错误")
        self.controller.components['recording_control'].recording_info_label.setText(f"录制信息: {error_message}")
        QMessageBox.warning(self.controller.main_window, "录制错误", error_message)
    
    def on_webcam_frame_recorded(self, frame_count):
        """处理webcam录制帧数更新"""
        info = self.controller.webcam_recorder.get_recording_info()
        if info:
            duration = info['duration']
            self.controller.components['recording_control'].recording_info_label.setText(f"录制信息: {frame_count} 帧, {duration:.1f}秒")


class InputEventHandler(QObject):
    """输入事件处理器"""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.last_content = ""  # 记录上次的内容，用于检测变化
    
    def eventFilter(self, obj, event):
        if obj == self.controller.components['input_section'].input_box and self.controller.data_model.is_collecting():
            if event.type() == QEvent.KeyPress:
                # 记录物理按键
                key = event.key()
                text = event.text()
                current_content = self.controller.components['input_section'].input_box.toPlainText()
                
                # 记录按键信息
                self.controller.add_keystroke(key, text, current_content)
                
            elif event.type() == QEvent.InputMethod:
                # 记录中文输入法事件
                current_content = self.controller.components['input_section'].input_box.toPlainText()
                
                # 如果内容有变化，记录输入法上屏
                if current_content != self.last_content:
                    self.controller.add_keystroke('IME', '', current_content)
                    self.last_content = current_content
                    
            elif event.type() == QEvent.KeyRelease:
                # 记录按键释放（可选，用于更精确的按键记录）
                key = event.key()
                if key not in [16777216, 16777217, 16777218]:  # 排除一些特殊键
                    current_content = self.controller.components['input_section'].input_box.toPlainText()
                    self.controller.add_keystroke(f'RELEASE_{key}', '', current_content)
                    
        return False 