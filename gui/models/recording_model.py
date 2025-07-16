from .data_collection_model import DataCollectionModel
import logging


class RecordingModel:
    """录制管理模型"""
    
    def __init__(self, data_model: DataCollectionModel):
        self.data_model = data_model
        self.screen_recorder = None
        self.webcam_display_recorder = None
        self.webcam_recorder = None
        self.webcam_manager = None
        
    def set_recorders(self, screen_recorder, webcam_recorder, webcam_manager):
        """设置录制器"""
        self.screen_recorder = screen_recorder
        self.webcam_recorder = webcam_recorder
        self.webcam_manager = webcam_manager
    
    def set_screen_recorder(self, screen_recorder):
        """设置屏幕录制器"""
        self.screen_recorder = screen_recorder
    
    def set_webcam_display_recorder(self, webcam_display_recorder):
        """设置webcam显示录制器"""
        self.webcam_display_recorder = webcam_display_recorder
    
    def start_screen_recording(self, input_widget, region):
        """开始屏幕录制"""
        if self.screen_recorder:
            logging.info(f"开始屏幕录制，区域: {region}")
            self.data_model.set_region(region)
            self.screen_recorder.start()
            return True
        else:
            logging.error("屏幕录制器未初始化")
            return False
    
    def stop_screen_recording(self):
        """停止屏幕录制"""
        if self.screen_recorder:
            logging.info("停止屏幕录制")
            self.screen_recorder.stop()
            self.screen_recorder.join()
            
            # 检查录制结果
            if hasattr(self.screen_recorder, 'get_recording_info'):
                info = self.screen_recorder.get_recording_info()
                if info and info.get('error'):
                    logging.error(f"屏幕录制出错: {info.get('error_message')}")
                else:
                    logging.info(f"屏幕录制完成: {info}")
    
    def start_webcam_recording(self, recording_mode, webcam_display_widget, region):
        """开始webcam录制"""
        if not (self.webcam_manager and self.webcam_manager.cap and self.webcam_manager.cap.isOpened()):
            logging.warning("webcam未连接")
            return False, "webcam未连接"
        
        if recording_mode == "录制预览框区域":
            return self._start_webcam_display_recording(webcam_display_widget, region)
        else:
            return self._start_direct_webcam_recording()
    
    def _start_webcam_display_recording(self, webcam_display_widget, region):
        """开始webcam预览框录制"""
        if self.webcam_display_recorder:
            logging.info(f"开始webcam预览框录制，区域: {region}")
            self.webcam_display_recorder.start()
            return True, "录制webcam预览框"
        else:
            logging.error("webcam显示录制器未初始化")
            return False, "webcam显示录制器未初始化"
    
    def _start_direct_webcam_recording(self):
        """开始直接webcam录制"""
        if self.webcam_recorder:
            fps = 30  # 可以从配置获取
            logging.info(f"开始直接webcam录制，FPS: {fps}")
            if self.webcam_recorder.start_recording(fps=fps):
                return True, "直接录制摄像头"
            else:
                logging.error("webcam录制启动失败")
                return False, "webcam录制启动失败"
        else:
            logging.error("webcam录制器未初始化")
            return False, "webcam录制器未初始化"
    
    def stop_webcam_recording(self):
        """停止webcam录制"""
        webcam_recording_path = None
        
        if self.webcam_display_recorder:
            logging.info("停止webcam显示录制")
            self.webcam_display_recorder.stop()
            self.webcam_display_recorder.join()
            webcam_recording_path = self.data_model.webcam_video_path
            
            # 检查录制结果
            if hasattr(self.webcam_display_recorder, 'get_recording_info'):
                info = self.webcam_display_recorder.get_recording_info()
                if info and info.get('error'):
                    logging.error(f"webcam显示录制出错: {info.get('error_message')}")
                else:
                    logging.info(f"webcam显示录制完成: {info}")
            
            # 清理录制器引用
            self.webcam_display_recorder = None
        elif self.webcam_recorder and self.webcam_recorder.is_recording():
            logging.info("停止直接webcam录制")
            self.webcam_recorder.stop_recording()
            webcam_recording_path = self.webcam_recorder.get_recording_path()
        
        return webcam_recording_path
    
    def is_webcam_recording(self):
        """是否正在webcam录制"""
        if self.webcam_display_recorder and self.webcam_display_recorder.is_alive():
            return True
        if self.webcam_recorder and self.webcam_recorder.is_recording():
            return True
        return False
    
    def reset_recording_state(self):
        """重置录制状态"""
        if self.webcam_recorder and self.webcam_recorder.is_recording():
            logging.info("重置webcam录制状态")
            self.webcam_recorder.stop_recording()
        if self.webcam_display_recorder:
            logging.info("重置webcam显示录制状态")
            self.webcam_display_recorder.stop()
            self.webcam_display_recorder.stop()
            self.webcam_display_recorder.join()
            # 清理录制器引用
            self.webcam_display_recorder = None 