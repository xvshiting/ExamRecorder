#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webcam权限检查脚本
用于检查系统是否允许访问摄像头
"""

import cv2
import sys
import platform

def check_webcam_permission():
    """检查webcam权限"""
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"OpenCV版本: {cv2.__version__}")
    print()
    
    print("正在检查摄像头权限...")
    
    try:
        # 尝试打开默认摄像头
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ 无法打开摄像头")
            print("可能的原因:")
            print("1. 摄像头权限被拒绝")
            print("2. 摄像头被其他程序占用")
            print("3. 摄像头硬件故障")
            
            if platform.system() == "Darwin":  # macOS
                print("\n在macOS上，请检查:")
                print("1. 系统偏好设置 > 安全性与隐私 > 隐私 > 摄像头")
                print("2. 确保Python或终端应用有摄像头访问权限")
                print("3. 重启终端或IDE后重试")
            
            return False
        else:
            print("✅ 摄像头权限正常")
            
            # 尝试读取一帧
            ret, frame = cap.read()
            if ret:
                print("✅ 可以正常读取摄像头画面")
                print(f"画面尺寸: {frame.shape[1]}x{frame.shape[0]}")
            else:
                print("❌ 无法读取摄像头画面")
            
            cap.release()
            return True
            
    except Exception as e:
        print(f"❌ 检查过程中出错: {str(e)}")
        return False

def list_available_cameras():
    """列出可用的摄像头设备"""
    print("\n正在扫描可用摄像头设备...")
    
    available_cameras = []
    for i in range(10):  # 检查前10个设备索引
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    camera_info = {
                        'index': i,
                        'resolution': f"{width}x{height}",
                        'fps': fps
                    }
                    available_cameras.append(camera_info)
                    print(f"✅ 摄像头 {i}: {width}x{height} @ {fps:.1f}fps")
                
                cap.release()
        except Exception as e:
            print(f"❌ 摄像头 {i}: 检查失败 - {str(e)}")
    
    if not available_cameras:
        print("❌ 未发现可用的摄像头设备")
    else:
        print(f"\n总共发现 {len(available_cameras)} 个可用摄像头")
    
    return available_cameras

def main():
    print("=" * 50)
    print("Webcam权限检查工具")
    print("=" * 50)
    
    # 检查权限
    has_permission = check_webcam_permission()
    
    if has_permission:
        # 列出可用设备
        cameras = list_available_cameras()
        
        if cameras:
            print("\n" + "=" * 50)
            print("✅ 摄像头功能正常，可以正常使用webcam功能")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("⚠️  权限正常但未发现可用设备")
            print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ 摄像头权限有问题，请解决后再使用webcam功能")
        print("=" * 50)

if __name__ == "__main__":
    main() 