"""
录屏功能模块 - 提供Android设备屏幕录制功能

本模块提供屏幕录制、截图等功能。
"""

import base64
import io
import os
import tempfile
import time

from .android import get_device


def record_screen(duration: int = 10) -> str:
    """
    录制设备屏幕视频

    注：uiautomator2 没有原生录屏 API，仍然使用 screenrecord shell 命令。
    
    Args:
        duration: 录制时长（秒），默认10秒，最大180秒
        
    Returns:
        str: base64编码的视频数据
    """
    device = get_device()
    try:
        if duration > 180:
            duration = 180
        if duration < 1:
            duration = 1

        device.shell(f"screenrecord --time-limit {duration} /sdcard/screen_recording.mp4")
        time.sleep(duration + 1)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_path = temp_file.name

        device.pull("/sdcard/screen_recording.mp4", temp_path)
        device.shell("rm /sdcard/screen_recording.mp4")

        with open(temp_path, "rb") as file:
            base64_data = base64.b64encode(file.read()).decode("utf-8")

        os.remove(temp_path)
        return f"data:video/mp4;base64,{base64_data}"
    except Exception as e:
        return f"录制屏幕视频失败: {str(e)}"


def take_screenshot_base64() -> str:
    """
    截取屏幕并返回base64编码的图片
    
    使用 uiautomator2 的 screenshot() API 直接获取 PIL Image，转为 base64。
    
    Returns:
        str: base64编码的截图数据
    """
    device = get_device()
    try:
        img = device.screenshot()
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{base64_data}"
    except Exception as e:
        return f"截图失败: {str(e)}"


def get_screen_resolution() -> str:
    """
    获取屏幕分辨率
    
    使用 uiautomator2 的 window_size() API。
    
    Returns:
        str: 屏幕分辨率信息
    """
    device = get_device()
    try:
        width, height = device.window_size()
        return f"屏幕分辨率: {width}x{height}"
    except Exception as e:
        return f"获取屏幕分辨率失败: {str(e)}"


def get_screen_density() -> str:
    """
    获取屏幕密度
    
    优先使用 uiautomator2 的 display_info API，回退到 wm density shell 命令。
    
    Returns:
        str: 屏幕密度信息
    """
    device = get_device()
    try:
        display_info = device.display_info
        density = getattr(display_info, "densityDpi", None)
        if density:
            return f"屏幕密度: {density} dpi"
    except Exception:
        pass

    try:
        output = device.shell("wm density")
        return f"屏幕密度: {output.strip()}"
    except Exception as e:
        return f"获取屏幕密度失败: {str(e)}"


def get_display_info() -> str:
    """
    获取显示信息汇总
    
    使用 uiautomator2 的 window_size() 和 display_info API。
    
    Returns:
        str: 显示信息汇总
    """
    device = get_device()
    try:
        info = []

        width, height = device.window_size()
        info.append(f"分辨率: {width}x{height}")

        display_info = device.display_info
        density = getattr(display_info, "densityDpi", None)
        if density:
            info.append(f"密度: {density} dpi")
        rotation = getattr(display_info, "rotation", None)
        if rotation is not None:
            info.append(f"方向: {rotation}")

        return "\n".join(info)
    except Exception as e:
        return f"获取显示信息失败: {str(e)}"
