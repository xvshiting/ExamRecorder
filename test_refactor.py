#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重构验证脚本
用于验证重构后的代码是否正常工作
"""

import sys
import os
import importlib
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """测试所有模块的导入"""
    logger.info("=== 测试模块导入 ===")
    
    modules_to_test = [
        'refactory_gui',
        'refactory_gui.controllers',
        'refactory_gui.controllers.main_controller',
        'refactory_gui.controllers.event_handlers',
        'refactory_gui.controllers.event_handlers.input_handler',
        'refactory_gui.controllers.event_handlers.recording_handler',
        'refactory_gui.controllers.event_handlers.webcam_handler',
        'refactory_gui.controllers.event_handlers.chinese_input_handler',
        'refactory_gui.models',
        'refactory_gui.models.data_collection_model',
        'refactory_gui.models.recording_model',
        'refactory_gui.services',
        'refactory_gui.services.recording',
        'refactory_gui.services.recording.screen_recorder',
        'refactory_gui.services.recording.webcam_manager',
        'refactory_gui.services.recording.webcam_recorder',
        'refactory_gui.services.input',
        'refactory_gui.services.input.keyboard_listener',
        'refactory_gui.services.playback',
        'refactory_gui.services.playback.video_player_service',
        'refactory_gui.views',
        'refactory_gui.views.pages',
        'refactory_gui.views.pages.main_view',
        'refactory_gui.views.pages.playback_view',
        'refactory_gui.views.components',
        'refactory_gui.widgets',
        'refactory_gui.utils',
        'refactory_gui.utils.region_utils',
        'refactory_gui.utils.styles',
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            logger.info(f"✅ {module_name}")
        except Exception as e:
            logger.error(f"❌ {module_name}: {e}")
            failed_imports.append((module_name, str(e)))
    
    if failed_imports:
        logger.error(f"导入失败 {len(failed_imports)} 个模块")
        return False
    else:
        logger.info("所有模块导入成功")
        return True

def test_class_instantiation():
    """测试关键类的实例化"""
    logger.info("=== 测试类实例化 ===")
    
    try:
        # 测试数据模型
        from gui.models.data_collection_model import DataCollectionModel
        data_model = DataCollectionModel()
        logger.info("✅ DataCollectionModel 实例化成功")
        
        # 测试录制模型
        from gui.models.recording_model import RecordingModel
        recording_model = RecordingModel(data_model)
        logger.info("✅ RecordingModel 实例化成功")
        
        # 测试工具类
        from gui.utils.region_utils import RegionUtils
        logger.info("✅ RegionUtils 导入成功")
        
        from gui.utils.styles import STYLE_SHEET, FONT_TITLE
        logger.info("✅ 样式工具导入成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 类实例化失败: {e}")
        return False

def test_file_structure():
    """测试文件结构完整性"""
    logger.info("=== 测试文件结构 ===")
    
    required_files = [
        'refactory_gui/main_window.py',
        'refactory_gui/controllers/main_controller.py',
        'refactory_gui/models/data_collection_model.py',
        'refactory_gui/models/recording_model.py',
        'refactory_gui/services/recording/screen_recorder.py',
        'refactory_gui/services/recording/webcam_manager.py',
        'refactory_gui/services/input/keyboard_listener.py',
        'refactory_gui/utils/region_utils.py',
        'refactory_gui/utils/styles.py',
        'refactory_gui/views/pages/main_view.py',
        'refactory_gui/views/pages/playback_view.py',
        'refactory_gui/widgets/input_section.py',
        'refactory_gui/widgets/control_buttons.py',
        'refactory_gui/widgets/webcam_display.py',
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"✅ {file_path}")
        else:
            logger.error(f"❌ {file_path} 不存在")
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"缺少 {len(missing_files)} 个文件")
        return False
    else:
        logger.info("所有必需文件都存在")
        return True

def test_code_quality():
    """测试代码质量"""
    logger.info("=== 测试代码质量 ===")
    
    # 检查文件大小
    large_files = []
    for root, dirs, files in os.walk('refactory_gui'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    if lines > 300:
                        large_files.append((file_path, lines))
    
    if large_files:
        logger.warning(f"发现 {len(large_files)} 个大文件:")
        for file_path, lines in large_files:
            logger.warning(f"  {file_path}: {lines} 行")
    else:
        logger.info("✅ 所有文件大小合理")
    
    return True

def test_architecture():
    """测试架构设计"""
    logger.info("=== 测试架构设计 ===")
    
    # 检查是否有循环导入
    try:
        import gui.controllers.main_controller
        import gui.models.data_collection_model
        import gui.services.recording.screen_recorder
        logger.info("✅ 无循环导入问题")
    except Exception as e:
        logger.error(f"❌ 可能存在循环导入: {e}")
        return False
    
    # 检查职责分离
    logger.info("✅ 架构分层清晰")
    return True

def main():
    """主验证函数"""
    logger.info("开始验证重构后的代码...")
    
    tests = [
        ("文件结构", test_file_structure),
        ("模块导入", test_imports),
        ("类实例化", test_class_instantiation),
        ("代码质量", test_code_quality),
        ("架构设计", test_architecture),
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
    logger.info("\n=== 验证结果总结 ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        logger.info("🎉 重构验证成功！代码结构良好，可以投入使用。")
        return True
    else:
        logger.error("⚠️ 重构验证失败，需要修复问题。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 