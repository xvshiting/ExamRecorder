import threading
import mss
import cv2
import numpy as np
import time
import os
import logging
from PyQt5.QtWidgets import QApplication

class ScreenRecorder(threading.Thread):
    """屏幕录制服务"""
    
    def __init__(self, input_box_ref, output_path, region, fps=15, start_time=None):
        super().__init__()
        self.input_box_ref = input_box_ref  # PyQt控件引用
        self.output_path = output_path
        self.region = region  # 只在开始时获取一次
        self.fps = fps
        self.start_time = start_time  # 录制开始时间
        self.running = threading.Event()
        self.running.set()
        self.writer = None
        self.sct = mss.mss()
        self.frame_count = 0
        self.error_occurred = False
        self.error_message = ""

    def run(self):
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            # 验证区域参数
            if not self._validate_region():
                self.error_occurred = True
                self.error_message = f"无效的录制区域: {self.region}"
                logging.error(self.error_message)
                return
            
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
                        self.output_path, fourcc, self.fps,
                        (self.region['width'], self.region['height'])
                    )
                    if self.writer.isOpened():
                        logging.info(f"成功创建视频写入器，使用编码器: {fourcc}")
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
                self.error_occurred = True
                self.error_message = "无法创建视频写入器，所有编码器都失败"
                logging.error(self.error_message)
                return
            
            # 使用传入的开始时间，如果没有则使用当前时间
            if self.start_time is None:
                self.start_time = time.time()
            
            logging.info(f"开始屏幕录制: 区域={self.region}, FPS={self.fps}, 输出={self.output_path}")
            
            prev = time.time()
            consecutive_failures = 0
            max_consecutive_failures = 10
            
            while self.running.is_set():
                try:
                    # 截图
                    img = np.array(self.sct.grab(self.region))
                    
                    # 检查图像是否有效
                    if img is None or img.size == 0:
                        consecutive_failures += 1
                        logging.warning(f"截图失败，连续失败次数: {consecutive_failures}")
                        if consecutive_failures >= max_consecutive_failures:
                            self.error_occurred = True
                            self.error_message = f"连续截图失败次数过多: {consecutive_failures}"
                            logging.error(self.error_message)
                            break
                        time.sleep(0.1)
                        continue
                    
                    consecutive_failures = 0  # 重置失败计数
                    
                    # 转换颜色空间
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    
                    # 检查帧尺寸并调整到目标尺寸
                    if frame.shape[1] != self.region['width'] or frame.shape[0] != self.region['height']:
                        logging.debug(f"调整帧尺寸: 从 {frame.shape[1]}x{frame.shape[0]} 到 {self.region['width']}x{self.region['height']}")
                        frame = cv2.resize(frame, (self.region['width'], self.region['height']))
                    
                    # 写入帧
                    if self.writer and self.writer.isOpened():
                        self.writer.write(frame)
                        self.frame_count += 1
                        
                        # 每100帧记录一次日志
                        if self.frame_count % 100 == 0:
                            logging.debug(f"已录制 {self.frame_count} 帧")
                    else:
                        self.error_occurred = True
                        self.error_message = "视频写入器已关闭"
                        logging.error(self.error_message)
                        break
                    
                    # 帧率控制
                    current_time = time.time()
                    elapsed = current_time - prev
                    sleep_time = max(0, 1.0/self.fps - elapsed)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    prev = time.time()
                    
                except Exception as e:
                    consecutive_failures += 1
                    logging.error(f"录制过程中出错: {str(e)}, 连续失败次数: {consecutive_failures}")
                    if consecutive_failures >= max_consecutive_failures:
                        self.error_occurred = True
                        self.error_message = f"录制过程中连续出错: {str(e)}"
                        break
                    time.sleep(0.1)
            
            # 清理资源
            if self.writer:
                self.writer.release()
            self.sct.close()
            
            duration = time.time() - self.start_time
            logging.info(f"屏幕录制完成: {self.frame_count} 帧, 时长: {duration:.1f}秒")
            
        except Exception as e:
            self.error_occurred = True
            self.error_message = f"录制初始化失败: {str(e)}"
            logging.error(self.error_message)

    def _validate_region(self):
        """验证录制区域参数"""
        if not self.region:
            logging.error("录制区域为空")
            return False
        
        required_keys = ['left', 'top', 'width', 'height']
        for key in required_keys:
            if key not in self.region:
                logging.error(f"录制区域缺少必要参数: {key}")
                return False
        
        # 检查尺寸是否合理
        if self.region['width'] <= 0 or self.region['height'] <= 0:
            logging.error(f"录制区域尺寸无效: width={self.region['width']}, height={self.region['height']}")
            return False
        
        # 检查位置是否合理（不能为负数）
        if self.region['left'] < 0 or self.region['top'] < 0:
            logging.warning(f"录制区域位置为负数: left={self.region['left']}, top={self.region['top']}")
        
        # 检查区域是否过大（可能是计算错误）
        if self.region['width'] > 10000 or self.region['height'] > 10000:
            logging.error(f"录制区域过大，可能是计算错误: {self.region}")
            return False
        
        logging.info(f"录制区域验证通过: {self.region}")
        return True

    def stop(self):
        """停止录制"""
        self.running.clear()
        logging.info("正在停止屏幕录制...")
    
    def get_recording_info(self):
        """获取录制信息"""
        if self.error_occurred:
            return {
                'error': True,
                'error_message': self.error_message,
                'frame_count': self.frame_count
            }
        
        duration = time.time() - self.start_time if self.start_time else 0
        return {
            'error': False,
            'frame_count': self.frame_count,
            'duration': duration,
            'fps': self.fps,
            'output_path': self.output_path
        } 