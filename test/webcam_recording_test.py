#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webcam录制测试工具
用于测试webcam视频录制功能
"""

import sys
import cv2
import time
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QComboBox, QLabel, QMessageBox,
                             QGroupBox, QGridLayout, QSpinBox, QProgressBar, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from gui.webcam_manager import WebcamManager, WebcamDisplay
from gui.webcam_recorder import WebcamVideoRecorder

class WebcamRecordingTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Webcam录制测试工具')
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建webcam管理器
        self.webcam_manager = WebcamManager()
        self.webcam_manager.frame_ready.connect(self.on_frame_ready)
        self.webcam_manager.webcam_connected.connect(self.on_webcam_connected)
        self.webcam_manager.webcam_disconnected.connect(self.on_webcam_disconnected)
        self.webcam_manager.error_occurred.connect(self.on_error_occurred)
        
        # 创建录制器
        self.webcam_recorder = WebcamVideoRecorder(self.webcam_manager)
        self.webcam_recorder.recording_started.connect(self.on_recording_started)
        self.webcam_recorder.recording_stopped.connect(self.on_recording_stopped)
        self.webcam_recorder.recording_error.connect(self.on_recording_error)
        self.webcam_recorder.frame_recorded.connect(self.on_frame_recorded)
        
        # 录制信息
        self.recording_start_time = None
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_time)
        
        self.init_ui()
        self.refresh_devices()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # 设备控制组
        device_group = QGroupBox("设备控制")
        device_layout = QGridLayout(device_group)
        
        # 设备选择
        device_layout.addWidget(QLabel("选择设备:"), 0, 0)
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(200)
        device_layout.addWidget(self.device_combo, 0, 1)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新设备")
        self.refresh_btn.clicked.connect(self.refresh_devices)
        device_layout.addWidget(self.refresh_btn, 0, 2)
        
        # 连接/断开按钮
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.toggle_connection)
        device_layout.addWidget(self.connect_btn, 0, 3)
        
        # 开始/停止预览按钮
        self.preview_btn = QPushButton("开始预览")
        self.preview_btn.clicked.connect(self.toggle_preview)
        self.preview_btn.setEnabled(False)
        device_layout.addWidget(self.preview_btn, 1, 0, 1, 2)
        
        main_layout.addWidget(device_group)
        
        # 录制控制组
        recording_group = QGroupBox("录制控制")
        recording_layout = QGridLayout(recording_group)
        
        # 录制帧率设置
        recording_layout.addWidget(QLabel("录制帧率:"), 0, 0)
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(30)
        self.fps_spin.setEnabled(False)
        recording_layout.addWidget(self.fps_spin, 0, 1)
        
        # 录制按钮
        self.record_btn = QPushButton("开始录制")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.record_btn.setEnabled(False)
        recording_layout.addWidget(self.record_btn, 0, 2, 1, 2)
        
        # 录制状态
        recording_layout.addWidget(QLabel("录制状态:"), 1, 0)
        self.recording_status_label = QLabel("未录制")
        recording_layout.addWidget(self.recording_status_label, 1, 1)
        
        # 录制时间
        recording_layout.addWidget(QLabel("录制时间:"), 1, 2)
        self.recording_time_label = QLabel("00:00")
        recording_layout.addWidget(self.recording_time_label, 1, 3)
        
        # 录制进度条
        self.recording_progress = QProgressBar()
        self.recording_progress.setVisible(False)
        recording_layout.addWidget(self.recording_progress, 2, 0, 1, 4)
        
        main_layout.addWidget(recording_group)
        
        # 视频显示区域
        video_group = QGroupBox("视频预览")
        video_layout = QVBoxLayout(video_group)
        
        self.webcam_display = WebcamDisplay()
        video_layout.addWidget(self.webcam_display)
        
        main_layout.addWidget(video_group)
        
        # 录制信息显示
        info_group = QGroupBox("录制信息")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(100)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        main_layout.addWidget(info_group)
        
    def refresh_devices(self):
        """刷新可用设备列表"""
        self.device_combo.clear()
        devices = self.webcam_manager.discover_webcams()
        
        if not devices:
            self.device_combo.addItem("未发现可用设备")
            QMessageBox.information(self, "设备发现", "未发现可用的摄像头设备")
        else:
            for device in devices:
                text = f"摄像头 {device['index']} - {device['resolution']} ({device['fps']:.1f}fps)"
                self.device_combo.addItem(text, device['index'])
            
            QMessageBox.information(self, "设备发现", f"发现 {len(devices)} 个可用设备")
    
    def toggle_connection(self):
        """切换连接状态"""
        if self.webcam_manager.cap is None:
            # 连接设备
            current_index = self.device_combo.currentData()
            if current_index is not None:
                if self.webcam_manager.connect_webcam(current_index):
                    self.connect_btn.setText("断开")
                    self.preview_btn.setEnabled(True)
                    self.record_btn.setEnabled(True)
                    self.fps_spin.setEnabled(True)
        else:
            # 断开连接
            if self.webcam_recorder.is_recording():
                self.webcam_recorder.stop_recording()
            self.webcam_manager.disconnect_webcam()
            self.connect_btn.setText("连接")
            self.preview_btn.setText("开始预览")
            self.preview_btn.setEnabled(False)
            self.record_btn.setText("开始录制")
            self.record_btn.setEnabled(False)
            self.fps_spin.setEnabled(False)
            self.webcam_display.setText("摄像头未连接")
    
    def toggle_preview(self):
        """切换预览状态"""
        if not self.webcam_manager.is_running:
            if self.webcam_manager.start_capture():
                self.preview_btn.setText("停止预览")
        else:
            self.webcam_manager.stop_capture()
            self.preview_btn.setText("开始预览")
    
    def toggle_recording(self):
        """切换录制状态"""
        if not self.webcam_recorder.is_recording():
            # 开始录制
            fps = self.fps_spin.value()
            if self.webcam_recorder.start_recording(fps=fps):
                self.record_btn.setText("停止录制")
                self.record_btn.setStyleSheet("background-color: #ff4444; color: white;")
                self.recording_start_time = time.time()
                self.recording_timer.start(1000)  # 每秒更新一次
                self.recording_progress.setVisible(True)
        else:
            # 停止录制
            if self.webcam_recorder.stop_recording():
                self.record_btn.setText("开始录制")
                self.record_btn.setStyleSheet("")
                self.recording_timer.stop()
                self.recording_progress.setVisible(False)
    
    def update_recording_time(self):
        """更新录制时间显示"""
        if self.recording_start_time:
            elapsed = time.time() - self.recording_start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.recording_time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def on_frame_ready(self, image):
        """处理新的视频帧"""
        self.webcam_display.update_frame(image)
    
    def on_webcam_connected(self, message):
        """处理webcam连接成功"""
        self.add_info(f"✅ {message}")
    
    def on_webcam_disconnected(self):
        """处理webcam断开连接"""
        self.add_info("❌ 摄像头已断开连接")
    
    def on_error_occurred(self, error_message):
        """处理错误"""
        self.add_info(f"❌ 错误: {error_message}")
        QMessageBox.warning(self, "错误", error_message)
    
    def on_recording_started(self, message):
        """处理录制开始"""
        self.add_info(f"🎬 {message}")
        self.recording_status_label.setText("录制中")
        self.recording_status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def on_recording_stopped(self, message):
        """处理录制停止"""
        self.add_info(f"✅ {message}")
        self.recording_status_label.setText("录制完成")
        self.recording_status_label.setStyleSheet("color: green; font-weight: bold;")
        
        # 显示录制文件路径
        recording_path = self.webcam_recorder.get_recording_path()
        if recording_path:
            self.add_info(f"📁 视频文件: {recording_path}")
            QMessageBox.information(self, "录制完成", f"视频已保存到: {recording_path}")
    
    def on_recording_error(self, error_message):
        """处理录制错误"""
        self.add_info(f"❌ 录制错误: {error_message}")
        self.recording_status_label.setText("录制错误")
        self.recording_status_label.setStyleSheet("color: orange; font-weight: bold;")
        QMessageBox.warning(self, "录制错误", error_message)
    
    def on_frame_recorded(self, frame_count):
        """处理录制帧数更新"""
        info = self.webcam_recorder.get_recording_info()
        if info:
            duration = info['duration']
            fps = info['fps']
            self.add_info(f"📹 录制进度: {frame_count} 帧, {duration:.1f}秒, {fps}fps")
    
    def add_info(self, message):
        """添加信息到日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.info_text.append(f"[{timestamp}] {message}")
        # 自动滚动到底部
        self.info_text.verticalScrollBar().setValue(
            self.info_text.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.webcam_recorder.is_recording():
            self.webcam_recorder.stop_recording()
        if self.webcam_manager.cap is not None:
            self.webcam_manager.disconnect_webcam()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = WebcamRecordingTestWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 