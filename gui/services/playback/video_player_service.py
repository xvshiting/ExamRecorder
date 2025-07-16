import cv2
import time
import logging
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage

logging.basicConfig(level=logging.DEBUG)


class VideoPlayerService(QThread):
    """视频播放服务"""
    frame_ready = pyqtSignal(QPixmap, int)  # 帧图像, 时间戳(毫秒)
    video_finished = pyqtSignal()
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.cap = None
        self.fps = 0
        self.total_frames = 0
        self.current_frame = 0
        self.is_playing = False
        self.is_paused = False
        self.seek_position = -1
        self.start_time = 0  # 播放开始时间
        self.playback_speed = 1.0  # 新增，默认1.0倍速
        
    def run(self):
        """运行播放线程"""
        if not self.video_path or not self.cap:
            return
            
        # 确保从第一帧开始播放
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.current_frame = 0
        self.start_time = time.time()
        
        while self.is_playing:
            if self.is_paused:
                time.sleep(0.1)
                continue
                
            # 处理跳转
            if self.seek_position >= 0:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_position)
                self.current_frame = self.seek_position
                self.seek_position = -1
                self.start_time = time.time() - (self.current_frame / self.fps)
            
            ret, frame = self.cap.read()
            if not ret:
                self.is_playing = False
                self.video_finished.emit()
                break
                
            # 转换帧格式
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # 计算时间戳
            timestamp_ms = int(self.current_frame / self.fps * 1000)
            
            # 发送帧
            self.frame_ready.emit(pixmap, timestamp_ms)
            self.current_frame += 1
            
            # 控制播放速度 - 每帧之间的延迟
            frame_delay = 1.0 / self.fps
            time.sleep(frame_delay / self.playback_speed)  # 按速度调整
    
    def open_video(self):
        """打开视频"""
        self.cap = cv2.VideoCapture(self.video_path)
        if self.cap.isOpened():
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # 确保从第一帧开始
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.current_frame = 0
            return True
        return False
    
    def play(self):
        """开始播放"""
        self.is_playing = True
        self.is_paused = False
        if not self.isRunning():
            self.start()
    
    def pause(self):
        """暂停播放"""
        self.is_paused = True
    
    def resume(self):
        """恢复播放"""
        self.is_paused = False
        if not self.isRunning():
            self.start()
    
    def stop(self):
        """停止播放"""
        self.is_playing = False
        self.wait()
    
    def seek(self, frame_position):
        """跳转到指定帧"""
        self.seek_position = frame_position
    
    def close(self):
        """关闭视频"""
        self.stop()
        if self.cap:
            self.cap.release()
    
    def get_fps(self):
        """获取帧率"""
        return self.fps
    
    def get_total_frames(self):
        """获取总帧数"""
        return self.total_frames
    
    def get_current_frame(self):
        """获取当前帧"""
        return self.current_frame 

    def set_playback_speed(self, speed):
        """设置播放速度"""
        self.playback_speed = speed 