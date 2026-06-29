"""
录屏功能模块 - 提供Android设备屏幕录制功能

本模块提供屏幕录制、截图等功能。
"""

import base64
import os
import tempfile
import time

from .android import get_device


def record_screen(duration: int = 10) -> str:
    """
    录制设备屏幕视频
    
    Args:
        duration: 录制时长（秒），默认10秒，最大180秒
        
    Returns:
        str: base64编码的视频数据
    """
    device = get_device()
    try:
        # 限制录制时长
        if duration > 180:
            duration = 180
        if duration < 1:
            duration = 1

        # 在设备上启动录制
        device.shell(f"screenrecord --time-limit {duration} /sdcard/screen_recording.mp4")

        # 等待录制完成（额外多等待一秒以确保录制完成）
        time.sleep(duration + 1)

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_path = temp_file.name

        # 从设备拉取视频文件
        device.pull("/sdcard/screen_recording.mp4", temp_path)
        device.shell("rm /sdcard/screen_recording.mp4")

        # 转换为base64
        with open(temp_path, "rb") as file:
            base64_data = base64.b64encode(file.read()).decode("utf-8")

        # 删除临时文件
        os.remove(temp_path)

        return f"data:video/mp4;base64,{base64_data}"
    except Exception as e:
        return f"录制屏幕视频失败: {str(e)}"


def take_screenshot_base64() -> str:
    """
    截取屏幕并返回base64编码的图片
    
    Returns:
        str: base64编码的截图数据
    """
    device = get_device()
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_path = temp_file.name

        # 在设备上截图
        device.shell("screencap -p /sdcard/screenshot.png")
        device.pull("/sdcard/screenshot.png", temp_path)
        device.shell("rm /sdcard/screenshot.png")

        # 转换为base64
        with open(temp_path, "rb") as img_file:
            base64_data = base64.b64encode(img_file.read()).decode("utf-8")

        # 删除临时文件
        os.remove(temp_path)

        return f"data:image/png;base64,{base64_data}"
    except Exception as e:
        return f"截图失败: {str(e)}"


def get_screen_resolution() -> str:
    """
    获取屏幕分辨率
    
    Returns:
        str: 屏幕分辨率信息
    """
    device = get_device()
    try:
        output = device.shell("wm size")
        return f"屏幕分辨率: {output.strip()}"
    except Exception as e:
        return f"获取屏幕分辨率失败: {str(e)}"


def get_screen_density() -> str:
    """
    获取屏幕密度
    
    Returns:
        str: 屏幕密度信息
    """
    device = get_device()
    try:
        output = device.shell("wm density")
        return f"屏幕密度: {output.strip()}"
    except Exception as e:
        return f"获取屏幕密度失败: {str(e)}"


def get_display_info() -> str:
    """
    获取显示信息汇总
    
    Returns:
        str: 显示信息汇总
    """
    device = get_device()
    try:
        info = []

        # 获取分辨率
        size = device.shell("wm size")
        info.append(f"分辨率: {size.strip()}")

        # 获取密度
        density = device.shell("wm density")
        info.append(f"密度: {density.strip()}")

        # 获取显示旋转
        rotation = device.shell("dumpsys display | grep 'mCurrentOrientation'")
        if rotation:
            info.append(f"方向: {rotation.strip()}")

        return "\n".join(info)
    except Exception as e:
        return f"获取显示信息失败: {str(e)}"
