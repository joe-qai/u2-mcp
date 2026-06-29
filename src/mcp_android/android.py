"""
Android设备管理模块 - 提供基础的Android设备操作功能

本模块提供ADB命令执行、包管理、屏幕截图等核心功能。
"""

import io
from typing import Any, Dict, Optional

import uiautomator2 as u2
from PIL import Image

# 全局设备对象
_device: Optional[u2.Device] = None


def set_device(device: u2.Device) -> None:
    """
    设置全局设备对象
    
    Args:
        device: UIAutomator2设备对象
    """
    global _device
    _device = device


def get_device() -> u2.Device:
    """
    获取当前设备对象，如果未初始化则抛出异常
    
    Returns:
        u2.Device: UIAutomator2设备对象
        
    Raises:
        RuntimeError: 设备未初始化时抛出
    """
    global _device
    if _device is None:
        raise RuntimeError(
            "Device not initialized. Please call init_uiautomator2() first."
        )
    return _device


def execute_adb_shell_command(command: str) -> str:
    """
    执行ADB shell命令
    
    Args:
        command (str): 要执行的ADB shell命令
        
    Returns:
        str: 命令执行输出
        
    Raises:
        RuntimeError: 设备未初始化或命令执行失败
    """
    device = get_device()
    try:
        result = device.shell(command)
        if hasattr(result, "output"):
            return str(result.output).strip()
        return str(result).strip()
    except Exception as e:
        raise RuntimeError(f"ADB命令执行失败: {str(e)}") from e


def get_packages() -> str:
    """
    获取所有已安装应用包列表
    
    使用 uiautomator2 的 app_list() API。
    
    Returns:
        str: 已安装包列表，每行一个包名
        
    Raises:
        RuntimeError: 设备未初始化或获取失败
    """
    device = get_device()
    try:
        packages = device.app_list()
        return "\n".join(sorted(packages))
    except Exception as e:
        raise RuntimeError(f"获取包列表失败: {str(e)}") from e


def get_screenshot() -> Image.Image:
    """
    获取屏幕截图
    
    Returns:
        Image.Image: PIL图像对象
        
    Raises:
        RuntimeError: 设备未初始化或截图失败
        TypeError: 截图数据类型异常
    """
    device = get_device()
    try:
        screenshot_data = device.screenshot()
        if isinstance(screenshot_data, Image.Image):
            return screenshot_data
        elif isinstance(screenshot_data, bytes):
            return Image.open(io.BytesIO(screenshot_data))
        else:
            raise TypeError(f"Unexpected screenshot data type: {type(screenshot_data)}")
    except TypeError as e:
        raise e
    except Exception as e:
        raise RuntimeError(f"获取截图失败: {str(e)}") from e


def get_device_info() -> Dict[str, Any]:
    """
    获取设备详细信息
    
    Returns:
        Dict[str, Any]: 设备信息字典
        
    Raises:
        RuntimeError: 设备未初始化或获取失败
    """
    device = get_device()
    try:
        return {
            "serial": device.serial,
            "info": device.info,
            "window_size": device.window_size(),
            "display_info": device.display_info
        }
    except Exception as e:
        raise RuntimeError(f"获取设备信息失败: {str(e)}") from e
