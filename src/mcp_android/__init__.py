"""
MCP Android - Android设备自动化模块

提供Android设备控制、UI自动化和OCR识别功能。

主要模块：
- android: 基础设备管理（ADB命令、截图、设备信息）
- ui: UI交互操作（点击、输入、滑动等）
- app: 应用生命周期管理（启动、停止、初始化）
- ocr: 屏幕文本识别（基于PaddleOCR）
- network_tools: 网络工具（WiFi、移动数据、飞行模式）
- file_tools: 文件管理（上传、下载、列表、读取）
- performance_tools: 性能分析（电池、内存、CPU、日志）
- screen_tools: 录屏功能（屏幕录制、截图）
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

from .network_tools import (
    toggle_wifi,
    toggle_mobile_data,
    toggle_airplane_mode,
    get_wifi_info,
    get_ip_address,
    ping,
    get_network_info,
)

from .file_tools import (
    list_files,
    push_file,
    pull_file,
    read_text_file,
    download_file,
    write_text_file,
    delete_file,
    create_directory,
    get_file_info,
)

from .performance_tools import (
    get_battery_info,
    get_memory_info,
    get_cpu_info,
    analyze_app_performance,
    collect_device_logs,
    get_app_memory_usage,
    get_app_cpu_usage,
    get_system_info,
)

from .screen_tools import (
    record_screen,
    take_screenshot_base64,
    get_screen_resolution,
    get_screen_density,
    get_display_info,
)

from .element_finder import (
    dump_ui_hierarchy,
    get_all_elements,
    find_elements_by_text,
    find_elements_by_resource_id,
    find_clickable_elements,
    find_elements_by_class,
    get_element_info_at_position,
    get_element_suggestions,
    search_elements,
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
    
    # network_tools.py
    "toggle_wifi",
    "toggle_mobile_data",
    "toggle_airplane_mode",
    "get_wifi_info",
    "get_ip_address",
    "ping",
    "get_network_info",
    
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
    
    # performance_tools.py
    "get_battery_info",
    "get_memory_info",
    "get_cpu_info",
    "analyze_app_performance",
    "collect_device_logs",
    "get_app_memory_usage",
    "get_app_cpu_usage",
    "get_system_info",
    
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