"""
MCP Android - Android设备自动化模块

提供Android设备控制、UI自动化和OCR识别功能。

主要模块：
- android: 基础设备管理（ADB命令、截图、设备信息）
- ui: UI交互操作（点击、输入、滑动等）
- app: 应用生命周期管理（启动、停止、初始化）
- ocr: 屏幕文本识别（基于PaddleOCR）
- file_tools: 文件管理（上传、下载、列表、读取）
- screen_tools: 录屏功能（屏幕录制、截图）
- element_finder: 元素发现（查找元素、UI层次结构）
"""

from .android import (
    execute_adb_shell_command,
    get_device,
    get_device_info,
    get_packages,
    get_screenshot,
    set_device,
)
from .app import (
    check_uiautomator2,
    clear_app_data,
    get_current_app,
    init_uiautomator2,
    install_apk,
    restart_uiautomator2,
    start_app,
    stop_app,
)
from .element_finder import (
    dump_ui_hierarchy,
    find_clickable_elements,
    find_elements_by_class,
    find_elements_by_resource_id,
    find_elements_by_text,
    get_all_elements,
    get_element_info_at_position,
    get_element_suggestions,
    search_elements,
)
from .file_tools import (
    create_directory,
    delete_file,
    download_file,
    get_file_info,
    list_files,
    pull_file,
    push_file,
    read_text_file,
    write_text_file,
)
from .ocr import OCRManager
from .screen_tools import (
    get_display_info,
    get_screen_density,
    get_screen_resolution,
    record_screen,
    take_screenshot_base64,
)
from .ui import (
    click_element,
    input_text,
    long_click_element,
    scroll_to_element,
    swipe_screen,
    wait_and_click_element,
)

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

    # file_tools.py
    "list_files",
    "push_file",
    "pull_file",
    "read_text_file",
    "download_file",
    "write_text_file",
    "delete_file",
    "create_directory",
    "get_file_info",

    # screen_tools.py
    "record_screen",
    "take_screenshot_base64",
    "get_screen_resolution",
    "get_screen_density",
    "get_display_info",

    # element_finder.py
    "dump_ui_hierarchy",
    "get_all_elements",
    "find_elements_by_text",
    "find_elements_by_resource_id",
    "find_clickable_elements",
    "find_elements_by_class",
    "get_element_info_at_position",
    "get_element_suggestions",
    "search_elements",
]
