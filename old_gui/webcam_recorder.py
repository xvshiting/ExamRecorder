import cv2
import threading
import time
import os
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QImage

class WebcamRecorder(QObject):
    """Webcam录制器，负责录制webcam视频"""
    
    # 信号定义
    recording_started = pyqtSignal(str)  # 录制开始信号
    recording_stopped = pyqtSignal(str)  # 录制停止信号
    recording_error = pyqtSignal(str)  # 录制错误信号
    frame_recorded = pyqtSignal(int)  # 录制帧数信号
    
    def __init__(self, webcam_manager):
        super().__init__()
        self.webcam_manager = webcam_manager
        self.writer = None
        self.is_recording = False
        self.recording_thread = None
        self.output_path = None
        self.frame_count = 0
        self.start_time = None
        self.fps = 30
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
    def start_recording(self, output_path, fps=30, start_time=None):
        """开始录制webcam视频"""
        if self.is_recording:
            self.recording_error.emit("已经在录制中")
            return False
            
        if not self.webcam_manager.cap or not self.webcam_manager.cap.isOpened():
            self.recording_error.emit("摄像头未连接")
            return False
            
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 获取摄像头分辨率
            width = int(self.webcam_manager.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.webcam_manager.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 验证分辨率
            if width <= 0 or height <= 0:
                logging.warning("摄像头分辨率无效，使用默认值")
                width, height = 640, 480
            
            logging.info(f"webcam录制分辨率: {width}x{height}, FPS: {fps}")
            
            # 尝试不同的编码器
            fourcc_options = [
                cv2.VideoWriter_fourcc(*'mp4v'),
                cv2.VideoWriter_fourcc(*'avc1'),
                cv2.VideoWriter_fourcc(*'XVID'),
                cv2.VideoWriter_fourcc(*'H264')
            ]
            
            self.writer = None
            for fourcc in fourcc_options:
                try:
                    self.writer = cv2.VideoWriter(
                        output_path, 
                        fourcc, 
                        fps, 
                        (width, height)
                    )
                    if self.writer.isOpened():
                        logging.info(f"成功创建webcam录制器，使用编码器: {fourcc}")
                        break
                    else:
                        self.writer.release()
                        self.writer = None
                except Exception as e:
                    logging.warning(f"编码器 {fourcc} 失败: {str(e)}")
                    if self.writer:
                        self.writer.release()
                        self.writer = None
            
            if not self.writer or not self.writer.isOpened():
                raise Exception("无法创建视频文件，所有编码器都失败")
                
            self.output_path = output_path
            self.fps = fps
            self.frame_count = 0
            # 使用传入的开始时间，如果没有则使用当前时间
            self.start_time = start_time if start_time is not None else time.time()
            self.is_recording = True
            
            # 启动录制线程
            self.recording_thread = threading.Thread(
                target=self._recording_loop, 
                daemon=True
            )
            self.recording_thread.start()
            
            self.recording_started.emit(f"开始录制到: {output_path}")
            return True
            
        except Exception as e:
            self.recording_error.emit(f"开始录制失败: {str(e)}")
            return False
    
    def stop_recording(self):
        """停止录制webcam视频"""
        if not self.is_recording:
            return False
            
        self.is_recording = False
        
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)
            
        if self.writer:
            self.writer.release()
            self.writer = None
            
        duration = time.time() - self.start_time if self.start_time else 0
        self.recording_stopped.emit(
            f"录制完成: {self.frame_count} 帧, 时长: {duration:.1f}秒"
        )
        
        return True
    
    def _recording_loop(self):
        """录制循环"""
        import cv2
        
        consecutive_failures = 0
        max_consecutive_failures = 10
        
        while self.is_recording:
            if not self.webcam_manager.cap or not self.webcam_manager.cap.isOpened():
                self.recording_error.emit("摄像头连接断开")
                break
                
            try:
                ret, frame = self.webcam_manager.cap.read()
                if ret and self.writer and self.writer.isOpened():
                    # 检查帧是否有效
                    if frame is None or frame.size == 0:
                        consecutive_failures += 1
                        logging.warning(f"webcam读取到无效帧，连续失败次数: {consecutive_failures}")
                        if consecutive_failures >= max_consecutive_failures:
                            self.recording_error.emit("连续读取无效帧次数过多")
                            break
                        time.sleep(0.1)
                        continue
                    
                    consecutive_failures = 0  # 重置失败计数
                    
                    self.writer.write(frame)
                    self.frame_count += 1
                    self.frame_recorded.emit(self.frame_count)
                    
                    # 每100帧记录一次日志
                    if self.frame_count % 100 == 0:
                        logging.debug(f"webcam录制已录制 {self.frame_count} 帧")
                else:
                    consecutive_failures += 1
                    logging.warning(f"读取摄像头帧失败，连续失败次数: {consecutive_failures}")
                    if consecutive_failures >= max_consecutive_failures:
                        self.recording_error.emit("连续读取摄像头帧失败次数过多")
                        break
                    time.sleep(0.1)
                    continue
                    
            except Exception as e:
                consecutive_failures += 1
                logging.error(f"webcam录制过程中出错: {str(e)}, 连续失败次数: {consecutive_failures}")
                if consecutive_failures >= max_consecutive_failures:
                    self.recording_error.emit(f"webcam录制过程中连续出错: {str(e)}")
                    break
                time.sleep(0.1)
                continue
                
            # 使用更精确的帧率控制，与屏幕录制保持一致
            prev = cv2.getTickCount() / cv2.getTickFrequency()
            elapsed = cv2.getTickCount() / cv2.getTickFrequency() - prev
            sleep_time = max(0, 1.0/self.fps - elapsed)
            if sleep_time > 0:
                cv2.waitKey(int(sleep_time * 1000))
            prev = cv2.getTickCount() / cv2.getTickFrequency()
    
    def get_recording_info(self):
        """获取录制信息"""
        if not self.is_recording:
            return None
            
        duration = time.time() - self.start_time if self.start_time else 0
        return {
            'frame_count': self.frame_count,
            'duration': duration,
            'fps': self.fps,
            'output_path': self.output_path
        }
    
    def is_recording_active(self):
        """检查是否正在录制"""
        return self.is_recording


class WebcamVideoRecorder:
    """Webcam视频录制器的高级封装"""
    
    def __init__(self, webcam_manager):
        self.webcam_manager = webcam_manager
        self.recorder = WebcamRecorder(webcam_manager)
        self.recording_path = None
        
    def start_recording(self, filename=None, fps=30, start_time=None):
        """开始录制视频"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"data/webcam_recording_{timestamp}.mp4"
            
        self.recording_path = filename
        return self.recorder.start_recording(filename, fps, start_time)
    
    def stop_recording(self):
        """停止录制视频"""
        return self.recorder.stop_recording()
    
    def get_recording_path(self):
        """获取录制文件路径"""
        return self.recording_path
    
    def is_recording(self):
        """检查是否正在录制"""
        return self.recorder.is_recording_active()
    
    def get_recording_info(self):
        """获取录制信息"""
        return self.recorder.get_recording_info()
    
    # 信号转发
    @property
    def recording_started(self):
        return self.recorder.recording_started
    
    @property
    def recording_stopped(self):
        return self.recorder.recording_stopped
    
    @property
    def recording_error(self):
        return self.recorder.recording_error
    
    @property
    def frame_recorded(self):
        return self.recorder.frame_recorded 