from PyQt5.QtWidgets import QApplication
import logging
import cv2
import numpy as np
import mss


class RegionUtils:
    """区域获取工具类"""
    
    @staticmethod
    def get_widget_region(widget):
        """获取指定组件的屏幕区域"""
        try:
            if not widget:
                logging.error("Widget为空，无法获取区域")
                return None
                
            # 获取窗口信息
            window = widget.window()
            if window:
                window_rect = window.geometry()
                logging.debug(f"窗口位置: x={window_rect.x()}, y={window_rect.y()}, width={window_rect.width()}, height={window_rect.height()}")
            
            # 获取控件在窗口中的位置
            widget_rect = widget.rect()
            if widget_rect.isNull() or widget_rect.isEmpty():
                logging.error(f"Widget {widget} 的矩形区域无效: {widget_rect}")
                return None
                
            logging.debug(f"控件在窗口中的位置: x={widget_rect.x()}, y={widget_rect.y()}, width={widget_rect.width()}, height={widget_rect.height()}")
            
            # 获取控件在屏幕中的绝对位置
            top_left = widget.mapToGlobal(widget_rect.topLeft())
            bottom_right = widget.mapToGlobal(widget_rect.bottomRight())
            
            logging.debug(f"控件在屏幕中的位置: 左上角({top_left.x()}, {top_left.y()}), 右下角({bottom_right.x()}, {bottom_right.y()})")
            
            # 获取屏幕信息 - 修复像素比例计算
            screen = QApplication.primaryScreen()
            if screen:
                # 在macOS上，mapToGlobal已经考虑了像素比例，所以不需要再乘以ratio
                # 直接使用逻辑坐标
                left = int(top_left.x())
                top = int(top_left.y())
                right = int(bottom_right.x())
                bottom = int(bottom_right.y())
                width = right - left + 1
                height = bottom - top + 1
                
                logging.debug(f"使用逻辑坐标计算区域: left={left}, top={top}, width={width}, height={height}")
            else:
                logging.error("无法获取主屏幕信息")
                return None
            
            # 验证区域有效性
            if width <= 0 or height <= 0:
                logging.error(f"计算出的区域尺寸无效: width={width}, height={height}")
                return None
                
            if left < 0 or top < 0:
                logging.warning(f"区域位置为负数: left={left}, top={top}")
            
            # 检查区域是否过大（可能是计算错误）
            if width > 10000 or height > 10000:
                logging.error(f"录制区域过大，可能是计算错误: width={width}, height={height}")
                return None
            
            region = {
                'left': left,
                'top': top,
                'width': width,
                'height': height
            }
            
            logging.info(f"成功获取Widget区域: {region}")
            return region
            
        except Exception as e:
            logging.error(f"获取Widget区域时出错: {str(e)}")
            return None
    
    @staticmethod
    def get_input_box_region(input_section_widget):
        """获取输入框的屏幕区域"""
        if not input_section_widget or not hasattr(input_section_widget, 'input_box'):
            logging.error("输入区域组件无效或缺少input_box属性")
            return None
            
        logging.info("开始获取输入框录制区域...")
        region = RegionUtils.get_widget_region(input_section_widget.input_box)
        if region:
            logging.info(f"输入框录制区域: {region}")
        else:
            logging.error("获取输入框录制区域失败")
        return region
    
    @staticmethod
    def get_webcam_display_region(webcam_display_widget):
        """获取webcam预览框的屏幕区域"""
        if not webcam_display_widget or not hasattr(webcam_display_widget, 'webcam_display'):
            logging.error("Webcam显示组件无效或缺少webcam_display属性")
            return None
            
        logging.info("开始获取webcam显示录制区域...")
        region = RegionUtils.get_widget_region(webcam_display_widget.webcam_display)
        if region:
            logging.info(f"Webcam显示录制区域: {region}")
        else:
            logging.error("获取webcam显示录制区域失败")
        return region
    
    @staticmethod
    def debug_widget_hierarchy(widget, level=0):
        """调试Widget层次结构"""
        indent = "  " * level
        if widget:
            widget_name = widget.__class__.__name__
            widget_rect = widget.rect()
            logging.debug(f"{indent}{widget_name}: rect={widget_rect}, visible={widget.isVisible()}")
            
            # 递归显示子控件
            for child in widget.findChildren(widget.__class__):
                if child != widget:
                    RegionUtils.debug_widget_hierarchy(child, level + 1)
    
    @staticmethod
    def visualize_region(region, title="录制区域预览", duration=3):
        """可视化显示录制区域（调试用）"""
        try:
            if not region:
                logging.error("区域为空，无法可视化")
                return
            
            # 截图整个屏幕
            sct = mss.mss()
            monitors = sct.monitors
            monitor = monitors[1] if len(monitors) > 1 else monitors[0]
            
            # 截取包含录制区域的区域
            capture_region = {
                'left': max(0, region['left'] - 50),
                'top': max(0, region['top'] - 50),
                'width': region['width'] + 100,
                'height': region['height'] + 100
            }
            
            # 确保不超出屏幕边界
            capture_region['left'] = min(capture_region['left'], monitor['width'] - capture_region['width'])
            capture_region['top'] = min(capture_region['top'], monitor['height'] - capture_region['height'])
            
            img = np.array(sct.grab(capture_region))
            if img is None or img.size == 0:
                logging.error("截图失败，无法可视化区域")
                return
            
            # 转换颜色空间
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # 在录制区域上画红色边框
            region_x = region['left'] - capture_region['left']
            region_y = region['top'] - capture_region['top']
            
            cv2.rectangle(frame, 
                         (region_x, region_y), 
                         (region_x + region['width'], region_y + region['height']), 
                         (0, 0, 255), 3)
            
            # 添加文字说明
            cv2.putText(frame, f"录制区域: {region['width']}x{region['height']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"位置: ({region['left']}, {region['top']})", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 显示图像
            cv2.imshow(title, frame)
            cv2.waitKey(duration * 1000)
            cv2.destroyAllWindows()
            
            logging.info(f"已显示录制区域预览，区域: {region}")
            
        except Exception as e:
            logging.error(f"可视化录制区域时出错: {str(e)}")
    
    @staticmethod
    def test_region_calculation(widget, widget_name="未知组件"):
        """测试区域计算并可视化"""
        logging.info(f"=== 测试 {widget_name} 区域计算 ===")
        
        # 获取区域
        region = RegionUtils.get_widget_region(widget)
        
        if region:
            logging.info(f"✅ {widget_name} 区域计算成功: {region}")
            
            # 显示区域信息
            info = f"""
{widget_name} 区域信息:
- 左上角: ({region['left']}, {region['top']})
- 宽度: {region['width']} 像素
- 高度: {region['height']} 像素
- 面积: {region['width'] * region['height']} 平方像素
"""
            logging.info(info)
            
            # 可视化区域（可选）
            try:
                RegionUtils.visualize_region(region, f"{widget_name} 录制区域")
            except Exception as e:
                logging.warning(f"可视化区域失败: {e}")
                
            return region
        else:
            logging.error(f"❌ {widget_name} 区域计算失败")
            return None 