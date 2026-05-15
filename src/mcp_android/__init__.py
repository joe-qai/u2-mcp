"""
MCP Android - Android设备自动化模块

提供Android设备控制、UI自动化和OCR识别功能。

主要模块：
- android: 基础设备管理（ADB命令、截图、设备信息）
- ui: UI交互操作（点击、输入、滑动等）
- app: 应用生命周期管理（启动、停止、初始化）
- ocr: 屏幕文本识别（基于PaddleOCR）
"""

from .android import (
    get_device,
    set_device,
    execute_adb_shell_command,
    get_packages,
    get_screenshot,
    get_device_info,
)

from .ui import (
    click_element,
    input_text,
    swipe_screen,
    wait_and_click_element,
    scroll_to_element,
    long_click_element,
)

from .app import (
    init_uiautomator2,
    check_uiautomator2,
    restart_uiautomator2,
    start_app,
    stop_app,
    get_current_app,
    clear_app_data,
    install_apk,
)

from .ocr import OCRManager

__all__ = [
    # android.py
    "get_device",
    "set_device",
    "execute_adb_shell_command",
    "get_packages",
    "get_screenshot",
    "get_device_info",
    
    # ui.py
    "click_element",
    "input_text",
    "swipe_screen",
    "wait_and_click_element",
    "scroll_to_element",
    "long_click_element",
    
    # app.py
    "init_uiautomator2",
    "check_uiautomator2",
    "restart_uiautomator2",
    "start_app",
    "stop_app",
    "get_current_app",
    "clear_app_data",
    "install_apk",
    
    # ocr.py
    "OCRManager",
]