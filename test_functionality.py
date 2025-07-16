#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能测试脚本
测试重构后的核心功能是否正常工作
"""

import sys
import os
import logging
import tempfile
import shutil
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_data_model():
    """测试数据模型功能"""
    logger.info("=== 测试数据模型 ===")
    
    try:
        from refactory_gui.models.data_collection_model import DataCollectionModel
        
        # 创建临时题库文件
        temp_dir = tempfile.mkdtemp()
        questions_file = os.path.join(temp_dir, 'test_questions.json')
        
        with open(questions_file, 'w', encoding='utf-8') as f:
            f.write('''[
                {
                    "content": "测试题目1",
                    "answer": "测试答案1"
                },
                {
                    "content": "测试题目2", 
                    "answer": "测试答案2"
                }
            ]''')
        
        # 测试数据模型
        data_model = DataCollectionModel(questions_file)
        
        # 测试加载题目
        question = data_model.load_new_question()
        assert question is not None, "加载题目失败"
        assert data_model.get_question_content() == "测试题目1", "题目内容不匹配"
        
        # 测试采集状态
        assert not data_model.is_collecting(), "初始状态应该是未采集"
        
        # 测试开始采集
        data_model.start_collecting()
        assert data_model.is_collecting(), "开始采集后应该是采集状态"
        
        # 测试添加按键记录
        data_model.add_keystroke(65, 'A', 'A')
        data_model.add_keystroke(66, 'B', 'AB')
        assert len(data_model.keystroke_records) == 2, "按键记录数量不匹配"
        
        # 测试停止采集
        data_model.stop_collecting()
        assert not data_model.is_collecting(), "停止采集后应该是未采集状态"
        
        # 清理
        shutil.rmtree(temp_dir)
        
        logger.info("✅ 数据模型功能测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据模型功能测试失败: {e}")
        return False

def test_recording_model():
    """测试录制模型功能"""
    logger.info("=== 测试录制模型 ===")
    
    try:
        from refactory_gui.models.data_collection_model import DataCollectionModel
        from refactory_gui.models.recording_model import RecordingModel
        
        data_model = DataCollectionModel()
        recording_model = RecordingModel(data_model)
        
        # 测试设置录制器
        recording_model.set_recorders(None, None, None)
        assert recording_model.screen_recorder is None
        assert recording_model.webcam_recorder is None
        assert recording_model.webcam_manager is None
        
        # 测试设置屏幕录制器
        recording_model.set_screen_recorder("test_screen_recorder")
        assert recording_model.screen_recorder == "test_screen_recorder"
        
        # 测试设置webcam显示录制器
        recording_model.set_webcam_display_recorder("test_webcam_display_recorder")
        assert recording_model.webcam_display_recorder == "test_webcam_display_recorder"
        
        logger.info("✅ 录制模型功能测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 录制模型功能测试失败: {e}")
        return False

def test_region_utils():
    """测试区域工具功能"""
    logger.info("=== 测试区域工具 ===")
    
    try:
        from refactory_gui.services.recording.screen_recorder import ScreenRecorder
        
        # 测试区域验证（使用ScreenRecorder中的方法）
        valid_region = {
            'left': 100,
            'top': 100,
            'width': 640,
            'height': 480
        }
        
        invalid_region = {
            'left': 100,
            'top': 100
            # 缺少width和height
        }
        
        # 创建临时录制器来测试区域验证
        class MockInputBox:
            pass
        
        recorder = ScreenRecorder(
            input_box_ref=MockInputBox(),
            output_path="/tmp/test.mp4",
            region=valid_region
        )
        
        # 测试有效区域
        assert recorder._validate_region(), "有效区域应该通过验证"
        
        # 测试无效区域
        recorder.region = invalid_region
        assert not recorder._validate_region(), "无效区域应该不通过验证"
        
        # 测试空区域
        recorder.region = None
        assert not recorder._validate_region(), "空区域应该不通过验证"
        
        logger.info("✅ 区域工具功能测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 区域工具功能测试失败: {e}")
        return False

def test_styles():
    """测试样式功能"""
    logger.info("=== 测试样式功能 ===")
    
    try:
        from refactory_gui.utils.styles import STYLE_SHEET, FONT_TITLE, FONT_CONTENT, FONT_INPUT
        
        # 测试样式表不为空
        assert STYLE_SHEET is not None, "样式表不能为空"
        assert len(STYLE_SHEET) > 0, "样式表长度应该大于0"
        
        # 测试字体不为空
        assert FONT_TITLE is not None, "标题字体不能为空"
        assert FONT_CONTENT is not None, "内容字体不能为空"
        assert FONT_INPUT is not None, "输入字体不能为空"
        
        # 测试样式表包含关键样式
        assert 'QWidget' in STYLE_SHEET, "样式表应该包含QWidget样式"
        assert 'QPushButton' in STYLE_SHEET, "样式表应该包含QPushButton样式"
        assert 'QTextEdit' in STYLE_SHEET, "样式表应该包含QTextEdit样式"
        
        logger.info("✅ 样式功能测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 样式功能测试失败: {e}")
        return False

def test_keyboard_listener():
    """测试键盘监听器功能"""
    logger.info("=== 测试键盘监听器功能 ===")
    
    try:
        from refactory_gui.services.input.keyboard_listener import KeyboardListenerQt
        
        # 创建一个模拟控制器
        class MockController:
            def __init__(self):
                self.data_model = MockDataModel()
                self.components = {'input_section': MockInputSection()}
            
            def add_raw_keystroke(self, keystroke):
                pass
        
        class MockDataModel:
            def is_collecting(self):
                return True
            recording_start_time = None
        
        class MockInputSection:
            def __init__(self):
                self.input_box = MockInputBox()
        
        class MockInputBox:
            def toPlainText(self):
                return "test"
        
        # 测试键盘监听器创建
        controller = MockController()
        listener = KeyboardListenerQt(controller)
        
        # 测试初始状态
        assert not listener.is_listening, "初始状态应该是未监听"
        assert len(listener.raw_keystrokes) == 0, "初始按键记录应该为空"
        
        # 测试开始监听（跳过QApplication相关测试）
        listener.start_listening()
        assert listener.is_listening, "开始监听后应该是监听状态"
        
        # 测试停止监听
        listener.stop_listening()
        assert not listener.is_listening, "停止监听后应该是未监听状态"
        
        logger.info("✅ 键盘监听器功能测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 键盘监听器功能测试失败: {e}")
        return False

def test_webcam_manager():
    """测试webcam管理器功能"""
    logger.info("=== 测试webcam管理器功能 ===")
    
    try:
        from refactory_gui.services.recording.webcam_manager import WebcamManager
        
        # 创建webcam管理器
        webcam_manager = WebcamManager()
        
        # 测试初始状态
        assert webcam_manager.cap is None, "初始状态cap应该为None"
        assert not webcam_manager.is_running, "初始状态应该不是运行状态"
        assert webcam_manager.current_device is None, "初始状态current_device应该为None"
        
        # 测试发现webcam（可能没有设备，但不会报错）
        devices = webcam_manager.discover_webcams()
        assert isinstance(devices, list), "设备列表应该是list类型"
        
        # 测试连接状态检查
        assert not webcam_manager.is_connected, "未连接时is_connected应该为False"
        
        logger.info("✅ webcam管理器功能测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ webcam管理器功能测试失败: {e}")
        return False

def test_screen_recorder():
    """测试屏幕录制器功能"""
    logger.info("=== 测试屏幕录制器功能 ===")
    
    try:
        from refactory_gui.services.recording.screen_recorder import ScreenRecorder
        
        # 创建模拟输入框引用
        class MockInputBox:
            pass
        
        # 测试录制器创建
        input_box_ref = MockInputBox()
        output_path = "/tmp/test_recording.mp4"
        region = {
            'left': 100,
            'top': 100,
            'width': 640,
            'height': 480
        }
        
        recorder = ScreenRecorder(
            input_box_ref=input_box_ref,
            output_path=output_path,
            region=region
        )
        
        # 测试初始状态
        assert recorder.input_box_ref == input_box_ref, "输入框引用不匹配"
        assert recorder.output_path == output_path, "输出路径不匹配"
        assert recorder.region == region, "录制区域不匹配"
        assert recorder.running.is_set(), "初始状态应该是运行状态"
        assert recorder.frame_count == 0, "初始帧数应该为0"
        assert not recorder.error_occurred, "初始状态应该没有错误"
        
        # 测试区域验证
        assert recorder._validate_region(), "有效区域应该通过验证"
        
        # 测试停止录制
        recorder.stop()
        assert not recorder.running.is_set(), "停止后running应该为False"
        
        logger.info("✅ 屏幕录制器功能测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 屏幕录制器功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始功能测试...")
    
    tests = [
        ("数据模型", test_data_model),
        ("录制模型", test_recording_model),
        ("区域工具", test_region_utils),
        ("样式功能", test_styles),
        ("键盘监听器", test_keyboard_listener),
        ("webcam管理器", test_webcam_manager),
        ("屏幕录制器", test_screen_recorder),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 {test_name} 时出错: {e}")
            results.append((test_name, False))
    
    # 输出总结
    logger.info("\n=== 功能测试结果总结 ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        logger.info("🎉 功能测试成功！核心功能正常工作。")
        return True
    else:
        logger.error("⚠️ 功能测试失败，需要修复问题。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 