"""
设备管理模块 - 提供 Android 设备电源、通知、旋转等管理功能

使用 uiautomator2 直接 API 映射，涵盖 ADB shell 中常见的设备操作。
"""

import time
from typing import Optional

from .android import get_device


def wakeup() -> bool:
    """
    唤醒设备（点亮屏幕）

    Returns:
        bool: 是否执行成功
    """
    try:
        device = get_device()
        device.wakeup()
        time.sleep(0.3)
        return True
    except Exception:
        return False


def sleep() -> bool:
    """
    使设备进入睡眠状态（关闭屏幕）

    Returns:
        bool: 是否执行成功
    """
    try:
        device = get_device()
        device.sleep()
        time.sleep(0.3)
        return True
    except Exception:
        return False


def open_notification() -> bool:
    """
    打开通知面板

    Returns:
        bool: 是否执行成功
    """
    try:
        device = get_device()
        device.open_notification()
        time.sleep(0.5)
        return True
    except Exception:
        return False


def open_quick_settings() -> bool:
    """
    打开快捷设置面板

    Returns:
        bool: 是否执行成功
    """
    try:
        device = get_device()
        device.open_quick_settings()
        time.sleep(0.5)
        return True
    except Exception:
        return False


def set_orientation(orientation: str) -> bool:
    """
    设置屏幕方向

    Args:
        orientation: 方向，支持 "natural" (竖屏), "portrait" (竖屏), "landscape" (横屏),
                     "reverse_portrait", "reverse_landscape"

    Returns:
        bool: 是否执行成功
    """
    try:
        device = get_device()
        valid = {"natural", "portrait", "landscape", "reverse_portrait", "reverse_landscape"}
        if orientation not in valid:
            raise ValueError(f"无效的方向: {orientation}，支持: {', '.join(sorted(valid))}")
        device.set_orientation(orientation)
        time.sleep(0.3)
        return True
    except Exception:
        return False


def freeze_rotation(freeze: bool) -> bool:
    """
    冻结/解冻屏幕旋转

    Args:
        freeze: True 冻结旋转，False 解冻

    Returns:
        bool: 是否执行成功
    """
    try:
        device = get_device()
        device.freeze_rotation(freeze)
        time.sleep(0.3)
        return True
    except Exception:
        return False


def is_screen_on() -> Optional[bool]:
    """
    检查屏幕是否点亮

    Returns:
        Optional[bool]: 点亮返回 True，熄灭返回 False，异常返回 None
    """
    try:
        device = get_device()
        return device.info.get("screenOn", None)
    except Exception:
        return None
