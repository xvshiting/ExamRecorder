import time
import json as pyjson
import os
import logging
from textlib import TextLib


class DataCollectionModel:
    """数据采集模型"""
    
    def __init__(self, textlib_path='textlib/questions.json'):
        self.textlib = TextLib(textlib_path)
        self.current_question = None
        self.keystroke_records = []  # 原有的input_tool_keystrokes
        self.raw_keystroke_records = []  # 新增的底层keystrokes
        self.collecting = False
        self.recording_start_time = None
        
        # 录制相关
        self.video_path = None
        self.webcam_video_path = None
        self.region = None
    
    def load_new_question(self):
        """加载新题目"""
        self._reset_state()
        
        question = self.textlib.get_random_question()
        if not question:
            return None
            
        self.current_question = question
        return question
    
    def _reset_state(self):
        """重置状态"""
        self.keystroke_records = []
        self.raw_keystroke_records = []
        self.collecting = False
        self.video_path = None
        self.webcam_video_path = None
        self.recording_start_time = None
        self.region = None
    
    def start_collecting(self):
        """开始采集"""
        self.collecting = True
        self.keystroke_records = []
        self.raw_keystroke_records = []
        # 录制开始时间将在实际开始录制时设置
        # self.recording_start_time = time.time()
        
        # 准备录制文件路径
        os.makedirs('data', exist_ok=True)
        timestamp = int(time.time())
        self.video_path = f"data/sample_{timestamp}.mp4"
        self.webcam_video_path = f"data/webcam_{timestamp}.mp4"
    
    def set_recording_start_time(self):
        """设置录制开始时间（在实际开始录制时调用）"""
        self.recording_start_time = time.time()
        logging.debug(f'Recording start time set to: {self.recording_start_time}')
    
    def stop_collecting(self):
        """停止采集"""
        self.collecting = False
    
    def add_keystroke(self, key, text, input_content):
        """添加按键记录（保留用于兼容性）"""
        if self.collecting:
            current_time = time.time()
            absolute_timestamp = current_time
            
            if self.recording_start_time is not None:
                relative_timestamp = current_time - self.recording_start_time
            else:
                relative_timestamp = current_time
            
            keystroke_record = {
                'key': key,
                'text': text,
                'timestamp': relative_timestamp,  # 相对时间（用于回放）
                'absolute_timestamp': absolute_timestamp,  # 绝对时间（用于调试）
                'input_content': input_content
            }
            
            self.keystroke_records.append(keystroke_record)
            logging.debug(f'Keystroke added: {keystroke_record}')
            logging.debug(f'Total keystrokes: {len(self.keystroke_records)}')
        else:
            logging.warning(f'Keystroke ignored: collecting={self.collecting}, key={key}, text="{text}"')
    
    def add_raw_keystroke(self, raw_keystroke):
        """添加原始按键记录（底层keystrokes）"""
        if self.collecting:
            self.raw_keystroke_records.append(raw_keystroke)
            logging.debug(f'Raw keystroke added: {raw_keystroke}')
            logging.debug(f'Total raw keystrokes: {len(self.raw_keystroke_records)}')
        else:
            logging.warning(f'Raw keystroke ignored: collecting={self.collecting}, keystroke={raw_keystroke}')
    
    def save_data(self, user_input, webcam_recording_path=None):
        """保存数据"""
        data = {
            'question': self.current_question,
            'user_input': user_input,
            'keystrokes': self.keystroke_records,  # 原有的input_tool_keystrokes
            'raw_keystrokes': self.raw_keystroke_records,  # 新增的底层keystrokes
            'recording_start_time': self.recording_start_time,  # 保存录制开始时间
            'timestamp': time.time(),  # 保存数据保存时间
            'screen_video_path': self.video_path,
            'webcam_video_path': webcam_recording_path
        }
        filename = self.video_path.replace('.mp4', '.json')
        with open(filename, 'w', encoding='utf-8') as f:
            pyjson.dump(data, f, ensure_ascii=False, indent=2)
        return filename
    
    def get_question_content(self):
        """获取题目内容"""
        return self.current_question.get('content', '') if self.current_question else ''
    
    def get_question_answer(self):
        """获取题目答案"""
        return self.current_question.get('answer', None) if self.current_question else None
    
    def is_collecting(self):
        """是否正在采集"""
        return self.collecting
    
    def get_recording_paths(self):
        """获取录制路径"""
        return {
            'screen_video': self.video_path,
            'webcam_video': self.webcam_video_path
        }
    
    def set_region(self, region):
        """设置录制区域"""
        self.region = region
    
    def get_region(self):
        """获取录制区域"""
        return self.region 