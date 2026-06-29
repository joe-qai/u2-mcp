"""
UI操作模块 - 提供Android UI自动化操作功能

本模块提供点击、输入、滑动等UI交互操作。
"""

import time
from typing import Optional

from .android import get_device


def click_element(
    text: Optional[str] = None,
    description: Optional[str] = None,
    resourceId: Optional[str] = None,
    xpath: Optional[str] = None,
) -> bool:
    """
    点击界面元素
    
    根据提供的定位方式查找并点击界面元素。优先使用text定位，其次是description、resourceId、xpath。
    
    Args:
        text: 通过文本内容定位
        description: 通过描述内容定位
        resourceId: 通过资源ID定位（最可靠）
        xpath: 通过xpath定位
        
    Returns:
        bool: 是否点击成功
        
    Raises:
        RuntimeError: 设备未初始化
        ValueError: 未提供任何定位参数
    """
    if not text and not description and not resourceId and not xpath:
        raise ValueError("必须提供至少一个定位参数: text, description, resourceId 或 xpath")

    device = get_device()

    try:
        if text:
            element = device(text=text)
        elif description:
            element = device(description=description)
        elif resourceId:
            element = device(resourceId=resourceId)
        elif xpath:
            element = device.xpath(xpath)
        else:
            return False

        if element.exists:
            element.click()
            time.sleep(0.5)  # 点击后等待UI响应
            return True
        return False
    except Exception as e:
        raise RuntimeError(f"点击元素失败: {str(e)}") from e


def input_text(text: str, clear: bool = True) -> bool:
    """
    在当前焦点输入框中输入文本
    
    Args:
        text: 要输入的文本
        clear: 是否在输入前清除现有内容
        
    Returns:
        bool: 是否输入成功
        
    Raises:
        RuntimeError: 设备未初始化或输入失败
    """
    try:
        device = get_device()
        if clear:
            device.clear_text()
        device.send_keys(text)
        return True
    except Exception as e:
        raise RuntimeError(f"输入文本失败: {str(e)}") from e


def swipe_screen(direction: str, scale: float = 0.9) -> None:
    """
    滑动屏幕
    
    Args:
        direction: 滑动方向，支持 'up', 'down', 'left', 'right'
        scale: 滑动比例，默认0.9（相对于屏幕尺寸）
        
    Raises:
        RuntimeError: 设备未初始化或滑动失败
        ValueError: 无效的方向参数
    """
    if direction not in ["up", "down", "left", "right"]:
        raise ValueError(f"无效的方向参数: {direction}，支持: up, down, left, right")

    if scale <= 0 or scale > 1:
        raise ValueError(f"scale参数必须在0-1之间，当前值: {scale}")

    device = get_device()
    window_size = device.window_size()
    width, height = window_size[0], window_size[1]

    start_x = width // 2
    start_y = height // 2

    if direction == "up":
        end_x = start_x
        end_y = int(start_y * (1 - scale))
    elif direction == "down":
        end_x = start_x
        end_y = int(height * scale)
    elif direction == "left":
        end_x = int(start_x * (1 - scale))
        end_y = start_y
    elif direction == "right":
        end_x = int(width * scale)
        end_y = start_y

    try:
        device.swipe(start_x, start_y, end_x, end_y)
        time.sleep(0.3)  # 滑动后等待UI响应
    except Exception as e:
        raise RuntimeError(f"滑动屏幕失败: {str(e)}") from e


def wait_and_click_element(
    text: Optional[str] = None, description: Optional[str] = None, timeout: int = 10
) -> bool:
    """
    等待元素出现并点击
    
    Args:
        text: 要等待的文本内容
        description: 要等待的描述内容
        timeout: 超时时间（秒），默认10秒
        
    Returns:
        bool: 是否点击成功
        
    Raises:
        RuntimeError: 设备未初始化
        ValueError: 未提供任何定位参数
    """
    if not text and not description:
        raise ValueError("必须提供text或description参数")

    device = get_device()
    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            if text and device(text=text).exists:
                return click_element(text=text)
            elif description and device(description=description).exists:
                return click_element(description=description)
            time.sleep(0.5)

        return False
    except Exception as e:
        raise RuntimeError(f"等待并点击元素失败: {str(e)}") from e


def scroll_to_element(
    text: Optional[str] = None, description: Optional[str] = None
) -> bool:
    """
    滚动到指定元素
    
    Args:
        text: 要查找的文本
        description: 要查找的描述
        
    Returns:
        bool: 是否找到并滚动到元素
        
    Raises:
        RuntimeError: 设备未初始化或滚动失败
        ValueError: 未提供任何定位参数
    """
    if not text and not description:
        raise ValueError("必须提供text或description参数")

    device = get_device()

    try:
        if text:
            return device(scrollable=True).scroll.to(text=text)
        elif description:
            return device(scrollable=True).scroll.to(description=description)
        return False
    except Exception as e:
        raise RuntimeError(f"滚动到元素失败: {str(e)}") from e


def long_click_element(
    text: Optional[str] = None,
    description: Optional[str] = None,
    resourceId: Optional[str] = None,
    duration: float = 1.0,
) -> bool:
    """
    长按界面元素
    
    Args:
        text: 通过文本内容定位
        description: 通过描述内容定位
        resourceId: 通过资源ID定位
        duration: 长按时长（秒），默认1秒
        
    Returns:
        bool: 是否长按成功
        
    Raises:
        RuntimeError: 设备未初始化或长按失败
        ValueError: 未提供任何定位参数
    """
    if not text and not description and not resourceId:
        raise ValueError("必须提供至少一个定位参数: text, description 或 resourceId")

    device = get_device()

    try:
        if text:
            element = device(text=text)
        elif description:
            element = device(description=description)
        elif resourceId:
            element = device(resourceId=resourceId)
        else:
            return False

        if element.exists:
            element.long_click(duration=duration)
            time.sleep(0.5)
            return True
        return False
    except Exception as e:
        raise RuntimeError(f"长按元素失败: {str(e)}") from e


def press_key(key_name: str) -> bool:
    """
    模拟系统按键
    
    支持的按键: home, back, left, right, up, down, center, menu, search, enter,
    delete(del), recent(recent apps), volume_up, volume_down, volume_mute, camera, power
    
    Args:
        key_name: 按键名称
        
    Returns:
        bool: 是否成功
    """
    try:
        device = get_device()
        device.press(key_name)
        time.sleep(0.3)
        return True
    except Exception:
        return False


def unlock_screen() -> bool:
    """
    解锁屏幕
    
    Returns:
        bool: 是否解锁成功
    """
    try:
        device = get_device()
        device.unlock()
        time.sleep(0.5)
        return True
    except Exception:
        return False


def drag(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration: float = 0.5,
) -> bool:
    """
    拖拽（长按并移动到目标位置）

    Args:
        start_x: 起始 X 坐标
        start_y: 起始 Y 坐标
        end_x: 结束 X 坐标
        end_y: 结束 Y 坐标
        duration: 拖拽持续时间（秒），默认 0.5 秒

    Returns:
        bool: 是否执行成功
    """
    try:
        device = get_device()
        device.drag(start_x, start_y, end_x, end_y, duration=duration)
        time.sleep(0.3)
        return True
    except Exception:
        return False


def set_clipboard(text: str, label: Optional[str] = None) -> bool:
    """
    设置剪贴板内容
    
    Args:
        text: 剪贴板文本
        label: 可选的标签
        
    Returns:
        bool: 是否设置成功
    """
    try:
        device = get_device()
        sess = device.session()
        try:
            if label:
                sess.set_clipboard(text, label)
            else:
                sess.set_clipboard(text)
            return True
        finally:
            sess.close()
    except Exception:
        return False
