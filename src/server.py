"""
UIAutomator2 MCP Server - Android设备自动化服务

提供Android设备控制、UI自动化和OCR识别的MCP工具接口。

启动方式:
    python src/server.py
    或使用 PDM: pdm start

依赖:
    - fastmcp >= 2.0.0
    - uiautomator2 >= 2.16.0
    - pydantic >= 2.0.0
    - paddleocr >= 2.7.0 (可选，用于OCR功能)
"""

import logging
import sys
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/mcp-android.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("mcp-android")

# 初始化FastMCP服务器
mcp = FastMCP("UIAutomator2 MCP Server", version="1.0.0")

# 导入MCP工具模块
from mcp_android import (
    OCRManager,
    check_uiautomator2,
    clear_app_data,
    click_element,
    create_directory,
    delete_file,
    # 设备管理
    download_file,
    drag,
    # 元素发现
    dump_ui_hierarchy,
    execute_adb_shell_command,
    find_clickable_elements,
    find_elements_by_class,
    find_elements_by_resource_id,
    find_elements_by_text,
    freeze_rotation,
    get_all_elements,
    get_app_info,
    get_current_app,
    get_device_info,
    get_display_info,
    get_element_info_at_position,
    get_element_suggestions,
    get_file_info,
    get_packages,
    get_screen_density,
    get_screen_resolution,
    init_uiautomator2,
    input_text,
    install_apk,
    is_screen_on,
    # 文件管理
    list_files,
    list_running_apps,
    long_click_element,
    open_notification,
    open_quick_settings,
    press_key,
    pull_file,
    push_file,
    read_text_file,
    # 录屏功能
    record_screen,
    restart_uiautomator2,
    scroll_to_element,
    search_elements,
    set_clipboard,
    set_orientation,
    sleep,
    start_app,
    stop_app,
    swipe_screen,
    take_screenshot_base64,
    uninstall_app,
    unlock_screen,
    wait_and_click_element,
    wait_for_activity,
    wakeup,
    write_text_file,
)


# Pydantic模型定义
class DeviceStatus(BaseModel):
    """设备状态信息"""
    adb_server: bool = Field(description="ADB服务是否运行")
    device_connected: bool = Field(description="设备是否已连接")
    service_running: bool = Field(description="UIAutomator服务是否运行")
    app_installed: bool = Field(description="UIAutomator应用是否安装")
    device_info: Optional[Dict[str, Any]] = Field(description="设备详细信息")
    error: Optional[str] = Field(description="错误信息")
    serial: Optional[str] = Field(description="设备序列号")
    connected_devices: List[str] = Field(description="已连接设备列表")

class OCRResult(BaseModel):
    """OCR识别结果"""
    text: str = Field(description="识别到的文本")
    confidence: float = Field(description="置信度")
    x: int = Field(description="文本中心点X坐标")
    y: int = Field(description="文本中心点Y坐标")
    bbox: List[List[int]] = Field(description="文本边界框坐标")

class ElementPosition(BaseModel):
    """元素位置信息"""
    x: int = Field(description="X坐标")
    y: int = Field(description="Y坐标")

# 初始化OCR管理器
ocr_manager = OCRManager()

# ==================== 应用管理工具 ====================

@mcp.tool("init_uiautomator2")
def mcp_init_uiautomator2(
    serial: Optional[str] = Field(None, description="设备序列号（多设备时必填）")
) -> str:
    """
    初始化UIAutomator2服务
    
    建立与Android设备的连接，安装必要的UIAutomator服务APK并启动服务。
    
    Args:
        serial: 设备序列号，多设备环境下必填。单设备时可省略，系统会自动选择。
    
    Returns:
        str: 初始化结果状态信息
    """
    try:
        result = init_uiautomator2(serial)
        logger.info(f"UIAutomator2初始化: {result}")
        return result
    except Exception as e:
        error_msg = f"初始化失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("check_uiautomator2")
def mcp_check_uiautomator2() -> DeviceStatus:
    """
    检查UIAutomator2服务状态
    
    检查ADB服务、设备连接、UIAutomator服务运行状态和应用安装情况。
    
    Returns:
        DeviceStatus: 包含设备状态信息的结构化对象
    """
    try:
        status = check_uiautomator2()
        return DeviceStatus(**status)
    except Exception as e:
        logger.error(f"检查设备状态失败: {str(e)}")
        return DeviceStatus(
            adb_server=False,
            device_connected=False,
            service_running=False,
            app_installed=False,
            error=str(e),
            connected_devices=[]
        )

@mcp.tool("restart_uiautomator2")
def mcp_restart_uiautomator2() -> str:
    """
    重启UIAutomator2服务
    
    停止并重新启动UIAutomator服务，用于解决服务异常问题。
    
    Returns:
        str: 重启结果状态信息
    """
    try:
        result = restart_uiautomator2()
        logger.info(f"UIAutomator2重启: {result}")
        return result
    except Exception as e:
        error_msg = f"重启失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("start_app")
def mcp_start_app(
    package_name: str = Field(description="应用包名，如 'com.lockin.loock'"),
    activity: Optional[str] = Field(None, description="启动的Activity名称")
) -> str:
    """
    启动Android应用
    
    Args:
        package_name: 目标应用的包名
        activity: 可选的Activity名称，不指定则启动应用主Activity
    
    Returns:
        str: 启动结果（成功或失败原因）
    """
    try:
        success = start_app(package_name, activity)
        if success:
            message = f"✅ 成功启动应用: {package_name}"
            logger.info(message)
            return message
        else:
            error_msg = f"❌ 启动应用失败: {package_name}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 启动应用异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("stop_app")
def mcp_stop_app(
    package_name: str = Field(description="应用包名，如 'com.lockin.loock'")
) -> str:
    """
    停止Android应用
    
    Args:
        package_name: 目标应用的包名
    
    Returns:
        str: 停止结果（成功或失败原因）
    """
    try:
        success = stop_app(package_name)
        if success:
            message = f"✅ 成功停止应用: {package_name}"
            logger.info(message)
            return message
        else:
            error_msg = f"❌ 停止应用失败: {package_name}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 停止应用异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("get_current_app")
def mcp_get_current_app() -> Dict[str, str]:
    """
    获取当前运行的应用信息
    
    Returns:
        Dict[str, str]: 包含当前应用包名(package)和Activity(activity)的字典
    """
    try:
        package, activity = get_current_app()
        return {"package": package, "activity": activity}
    except Exception as e:
        logger.error(f"获取当前应用失败: {str(e)}")
        return {"package": "", "activity": ""}

@mcp.tool("clear_app_data")
def mcp_clear_app_data(
    package_name: str = Field(description="应用包名")
) -> str:
    """清除应用数据（pm clear）"""
    try:
        success = clear_app_data(package_name)
        if success:
            return f"✅ 已清除 {package_name} 的应用数据"
        else:
            return f"❌ 清除 {package_name} 的应用数据失败"
    except Exception as e:
        error_msg = f"❌ 清除应用数据失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("install_apk")
def mcp_install_apk(
    apk_path: str = Field(description="设备上的APK文件路径")
) -> str:
    """在设备上安装APK文件"""
    try:
        success = install_apk(apk_path)
        if success:
            return f"✅ APK安装成功: {apk_path}"
        else:
            return f"❌ APK安装失败: {apk_path}"
    except Exception as e:
        error_msg = f"❌ 安装APK失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("get_app_info")
def mcp_get_app_info(
    package_name: str = Field(description="应用包名")
) -> Dict[str, Any]:
    """获取应用详细信息（版本名、版本号、大小、label等）"""
    try:
        result = get_app_info(package_name)
        logger.info(f"获取应用 {package_name} 信息成功")
        return result
    except Exception as e:
        logger.error(f"获取应用信息失败: {str(e)}")
        return {"error": str(e)}

@mcp.tool("uninstall_app")
def mcp_uninstall_app(
    package_name: str = Field(description="应用包名")
) -> str:
    """卸载应用"""
    try:
        success = uninstall_app(package_name)
        if success:
            return f"✅ 已卸载应用: {package_name}"
        else:
            return f"❌ 卸载失败: {package_name}"
    except Exception as e:
        error_msg = f"❌ 卸载应用失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("list_running_apps")
def mcp_list_running_apps() -> List[str]:
    """获取正在运行的应用列表"""
    try:
        result = list_running_apps()
        logger.info(f"获取到 {len(result)} 个运行中的应用")
        return result
    except Exception as e:
        logger.error(f"获取运行应用列表失败: {str(e)}")
        return []

@mcp.tool("wait_for_activity")
def mcp_wait_for_activity(
    activity: str = Field(description="Activity名称"),
    timeout: float = Field(10.0, description="超时时间（秒），默认10秒")
) -> bool:
    """等待指定Activity出现"""
    try:
        result = wait_for_activity(activity, timeout)
        if result:
            logger.info(f"Activity '{activity}' 已出现")
        else:
            logger.warning(f"等待 Activity '{activity}' 超时")
        return result
    except Exception as e:
        logger.error(f"等待Activity失败: {str(e)}")
        return False

# ==================== UI交互工具 ====================

@mcp.tool("click_element")
def mcp_click_element(
    text: Optional[str] = Field(None, description="元素显示文本，如 '登录'"),
    description: Optional[str] = Field(None, description="元素描述文本"),
    resourceId: Optional[str] = Field(None, description="元素资源ID，如 'com.example.app:id/login_btn'"),
    xpath: Optional[str] = Field(None, description="元素XPath路径")
) -> str:
    """
    点击界面元素
    
    根据提供的定位方式查找并点击界面元素。优先使用text定位，其次是description、resourceId、xpath。
    
    Args:
        text: 通过元素显示文本定位
        description: 通过元素描述文本定位
        resourceId: 通过元素资源ID定位（最可靠）
        xpath: 通过XPath路径定位
    
    Returns:
        str: 点击结果（成功或失败原因）
    """
    try:
        if not text and not description and not resourceId and not xpath:
            return "❌ 错误：必须提供至少一个定位参数"

        success = click_element(text, description, resourceId, xpath)
        if success:
            message = "✅ 点击元素成功"
            logger.info(f"点击元素成功 - text={text}, resourceId={resourceId}")
            return message
        else:
            error_msg = f"❌ 未找到元素 - text={text}, description={description}, resourceId={resourceId}, xpath={xpath}"
            logger.warning(error_msg)
            return error_msg
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return f"❌ 参数错误: {str(e)}"
    except Exception as e:
        error_msg = f"❌ 点击元素失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("long_click_element")
def mcp_long_click_element(
    text: Optional[str] = Field(None, description="元素显示文本"),
    description: Optional[str] = Field(None, description="元素描述文本"),
    resourceId: Optional[str] = Field(None, description="元素资源ID"),
    duration: float = Field(1.0, description="长按时长（秒），默认1秒")
) -> str:
    """
    长按界面元素
    
    Args:
        text: 通过元素显示文本定位
        description: 通过元素描述文本定位
        resourceId: 通过元素资源ID定位
        duration: 长按时长，默认1秒
    
    Returns:
        str: 长按结果（成功或失败原因）
    """
    try:
        success = long_click_element(text, description, resourceId, duration)
        if success:
            message = "✅ 长按元素成功"
            logger.info(message)
            return message
        else:
            error_msg = f"❌ 未找到元素 - text={text}, resourceId={resourceId}"
            logger.warning(error_msg)
            return error_msg
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return f"❌ 参数错误: {str(e)}"
    except Exception as e:
        error_msg = f"❌ 长按元素失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("input_text")
def mcp_input_text(
    text: str = Field(description="要输入的文本内容"),
    clear: bool = Field(True, description="输入前是否清除现有内容，默认为True")
) -> str:
    """
    在当前焦点输入框中输入文本
    
    Args:
        text: 要输入的文本内容
        clear: 是否在输入前清除输入框中的现有内容
    
    Returns:
        str: 输入结果（成功或失败原因）
    """
    try:
        success = input_text(text, clear)
        if success:
            message = f"✅ 输入文本成功: {text}"
            logger.info(message)
            return message
        else:
            error_msg = "❌ 输入文本失败"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 输入文本失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("swipe_screen")
def mcp_swipe_screen(
    direction: str = Field(description="滑动方向，支持 'up', 'down', 'left', 'right'"),
    scale: float = Field(0.9, description="滑动比例（0-1），默认0.9")
) -> str:
    """
    滑动屏幕
    
    Args:
        direction: 滑动方向（up/down/left/right）
        scale: 滑动距离占屏幕尺寸的比例，范围0-1
    
    Returns:
        str: 滑动结果（成功或失败原因）
    """
    try:
        swipe_screen(direction, scale)
        message = f"✅ 成功向 {direction} 滑动屏幕"
        logger.info(message)
        return message
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return f"❌ 参数错误: {str(e)}"
    except Exception as e:
        error_msg = f"❌ 滑动屏幕失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("wait_and_click")
def mcp_wait_and_click(
    text: Optional[str] = Field(None, description="等待的文本内容"),
    description: Optional[str] = Field(None, description="等待的描述内容"),
    timeout: int = Field(10, description="超时时间（秒），默认10秒")
) -> str:
    """
    等待元素出现并点击
    
    在指定时间内等待目标元素出现，出现后立即点击。
    
    Args:
        text: 要等待的元素文本
        description: 要等待的元素描述
        timeout: 最大等待时间，默认10秒
    
    Returns:
        str: 操作结果（成功或超时/失败原因）
    """
    try:
        if not text and not description:
            return "❌ 错误：必须提供text或description参数"

        success = wait_and_click_element(text, description, timeout)
        if success:
            message = f"✅ 等待并点击成功 - text={text}, description={description}"
            logger.info(message)
            return message
        else:
            error_msg = f"❌ 超时未找到元素 - text={text}, description={description}, timeout={timeout}s"
            logger.warning(error_msg)
            return error_msg
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return f"❌ 参数错误: {str(e)}"
    except Exception as e:
        error_msg = f"❌ 等待并点击失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("scroll_to_element")
def mcp_scroll_to_element(
    text: Optional[str] = Field(None, description="要查找的文本"),
    description: Optional[str] = Field(None, description="要查找的描述")
) -> str:
    """
    滚动到指定元素
    
    在可滚动区域内滚动直到找到目标元素。
    
    Args:
        text: 目标元素的文本
        description: 目标元素的描述
    
    Returns:
        str: 滚动结果（成功或失败原因）
    """
    try:
        if not text and not description:
            return "❌ 错误：必须提供text或description参数"

        success = scroll_to_element(text, description)
        if success:
            message = f"✅ 滚动到元素成功 - text={text}, description={description}"
            logger.info(message)
            return message
        else:
            error_msg = f"❌ 滚动未找到元素 - text={text}, description={description}"
            logger.warning(error_msg)
            return error_msg
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return f"❌ 参数错误: {str(e)}"
    except Exception as e:
        error_msg = f"❌ 滚动失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("press_key")
def mcp_press_key(
    key_name: str = Field(description="按键名称: home, back, left, right, up, down, center, menu, search, enter, delete, recent, volume_up, volume_down, volume_mute, camera, power")
) -> str:
    """模拟系统按键"""
    try:
        success = press_key(key_name)
        if success:
            message = f"✅ 按下按键: {key_name}"
            logger.info(message)
            return message
        else:
            error_msg = f"❌ 按键失败: {key_name}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 按键异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("unlock_screen")
def mcp_unlock_screen() -> str:
    """解锁屏幕"""
    try:
        success = unlock_screen()
        if success:
            message = "✅ 屏幕已解锁"
            logger.info(message)
            return message
        else:
            error_msg = "❌ 解锁屏幕失败"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 解锁异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("set_clipboard")
def mcp_set_clipboard(
    text: str = Field(description="要设置的剪贴板文本"),
    label: Optional[str] = Field(None, description="可选的剪贴板标签")
) -> str:
    """设置设备剪贴板内容"""
    try:
        success = set_clipboard(text, label)
        if success:
            message = "✅ 剪贴板已设置"
            logger.info(message)
            return message
        else:
            error_msg = "❌ 设置剪贴板失败"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 设置剪贴板异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("drag")
def mcp_drag(
    start_x: int = Field(description="起始 X 坐标"),
    start_y: int = Field(description="起始 Y 坐标"),
    end_x: int = Field(description="结束 X 坐标"),
    end_y: int = Field(description="结束 Y 坐标"),
    duration: float = Field(0.5, description="拖拽持续时间（秒），默认0.5秒")
) -> str:
    """拖拽（长按并移动到目标位置）"""
    try:
        success = drag(start_x, start_y, end_x, end_y, duration)
        if success:
            message = f"✅ 拖拽成功: ({start_x},{start_y}) -> ({end_x},{end_y})"
            logger.info(message)
            return message
        else:
            error_msg = "❌ 拖拽失败"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 拖拽异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 设备管理工具 ====================

@mcp.tool("wakeup")
def mcp_wakeup() -> str:
    """唤醒设备（点亮屏幕）"""
    try:
        success = wakeup()
        if success:
            message = "✅ 设备已唤醒"
            logger.info(message)
            return message
        else:
            error_msg = "❌ 唤醒设备失败"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 唤醒设备异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("sleep")
def mcp_device_sleep() -> str:
    """使设备进入睡眠状态（关闭屏幕）"""
    try:
        success = sleep()
        if success:
            message = "✅ 设备已进入睡眠"
            logger.info(message)
            return message
        else:
            error_msg = "❌ 设备睡眠失败"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 设备睡眠异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("open_notification")
def mcp_open_notification() -> str:
    """打开通知面板"""
    try:
        success = open_notification()
        if success:
            message = "✅ 通知面板已打开"
            logger.info(message)
            return message
        else:
            error_msg = "❌ 打开通知面板失败"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 打开通知面板异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("open_quick_settings")
def mcp_open_quick_settings() -> str:
    """打开快捷设置面板"""
    try:
        success = open_quick_settings()
        if success:
            message = "✅ 快捷设置面板已打开"
            logger.info(message)
            return message
        else:
            error_msg = "❌ 打开快捷设置面板失败"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 打开快捷设置面板异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("set_orientation")
def mcp_set_orientation(
    orientation: str = Field(
        description="方向: natural, portrait, landscape, reverse_portrait, reverse_landscape"
    )
) -> str:
    """设置屏幕方向"""
    try:
        success = set_orientation(orientation)
        if success:
            message = f"✅ 屏幕方向已设置为: {orientation}"
            logger.info(message)
            return message
        else:
            error_msg = f"❌ 设置屏幕方向失败: {orientation}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 设置屏幕方向异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("freeze_rotation")
def mcp_freeze_rotation(
    freeze: bool = Field(description="True 冻结旋转，False 解冻")
) -> str:
    """冻结/解冻屏幕旋转"""
    try:
        success = freeze_rotation(freeze)
        if success:
            action = "冻结" if freeze else "解冻"
            message = f"✅ 已{action}屏幕旋转"
            logger.info(message)
            return message
        else:
            error_msg = "❌ 设置屏幕旋转失败"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"❌ 设置屏幕旋转异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("is_screen_on")
def mcp_is_screen_on() -> str:
    """检查屏幕是否点亮"""
    try:
        result = is_screen_on()
        if result is None:
            return "❌ 无法获取屏幕状态"
        return "✅ 屏幕已点亮" if result else "❌ 屏幕已熄灭"
    except Exception as e:
        error_msg = f"❌ 检查屏幕状态异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== ADB工具 ====================

@mcp.tool("execute_adb_command")
def mcp_execute_adb_command(
    command: str = Field(description="要执行的ADB shell命令，如 'ls /sdcard'")
) -> str:
    """
    执行ADB shell命令
    
    Args:
        command: ADB shell命令内容
    
    Returns:
        str: 命令执行输出结果
    """
    try:
        result = execute_adb_shell_command(command)
        logger.info(f"ADB命令执行成功: {command}")
        return result
    except RuntimeError as e:
        error_msg = f"❌ ADB命令执行失败: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ ADB命令执行异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("list_packages")
def mcp_list_packages() -> str:
    """
    获取设备上已安装的所有应用包名列表
    
    Returns:
        str: 包名列表，每行一个包名
    """
    try:
        result = get_packages()
        logger.info("获取包列表成功")
        return result
    except Exception as e:
        error_msg = f"❌ 获取包列表失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("get_device_info")
def mcp_get_device_info() -> Dict[str, Any]:
    """
    获取设备详细信息
    
    Returns:
        Dict[str, Any]: 包含设备序列号、屏幕尺寸、系统版本等信息的字典
    """
    try:
        info = get_device_info()
        logger.info("获取设备信息成功")
        return info
    except Exception as e:
        logger.error(f"获取设备信息失败: {str(e)}")
        return {"error": str(e)}

# ==================== OCR工具 ====================

@mcp.tool("ocr_screen")
def mcp_ocr_screen() -> str:
    """
    获取屏幕上的所有文字
    
    使用PaddleOCR进行屏幕文本识别，返回识别到的所有文本内容。
    
    Returns:
        str: 识别到的文本，每行一个条目
    """
    try:
        result = ocr_manager.ocr_screen()
        logger.info(f"OCR识别成功，识别到 {len(result.splitlines())} 行文本")
        return result if result else "未识别到文本"
    except RuntimeError as e:
        logger.error(f"OCR识别失败: {str(e)}")
        return f"❌ OCR识别失败: {str(e)}"
    except Exception as e:
        error_msg = f"❌ OCR识别异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("find_text_position")
def mcp_find_text_position(
    text: str = Field(description="要查找的目标文本")
) -> Optional[ElementPosition]:
    """
    在屏幕上查找指定文本的位置
    
    使用OCR识别屏幕文本并定位目标文本的中心坐标。
    
    Args:
        text: 要查找的目标文本
    
    Returns:
        ElementPosition: 文本中心点坐标（未找到返回null）
    """
    try:
        position = ocr_manager.find_text_position(text)
        if position:
            logger.info(f"找到文本 '{text}' 位置: {position}")
            return ElementPosition(x=position[0], y=position[1])
        else:
            logger.warning(f"未找到文本: {text}")
            return None
    except RuntimeError as e:
        logger.error(f"查找文本位置失败: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"查找文本位置异常: {str(e)}")
        return None

@mcp.tool("click_text")
def mcp_click_text(
    text: str = Field(description="要点击的目标文本")
) -> str:
    """
    在屏幕上查找并点击指定文本
    
    使用OCR识别屏幕文本，找到目标文本后点击其中心位置。
    
    Args:
        text: 要点击的目标文本
    
    Returns:
        str: 操作结果（成功或失败原因）
    """
    try:
        success = ocr_manager.click_text(text)
        if success:
            message = f"✅ 成功点击文本: {text}"
            logger.info(message)
            return message
        else:
            error_msg = f"❌ 未找到文本: {text}"
            logger.warning(error_msg)
            return error_msg
    except RuntimeError as e:
        logger.error(f"点击文本失败: {str(e)}")
        return f"❌ 点击文本失败: {str(e)}"
    except Exception as e:
        error_msg = f"❌ 点击文本异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("click_position")
def mcp_click_position(
    x: int = Field(description="横坐标"),
    y: int = Field(description="纵坐标")
) -> str:
    """
    点击屏幕上指定位置
    
    Args:
        x: X坐标
        y: Y坐标
    
    Returns:
        str: 操作结果（成功或失败原因）
    """
    try:
        success = ocr_manager.click_position(x, y)
        if success:
            message = f"✅ 成功点击位置: ({x}, {y})"
            logger.info(message)
            return message
        else:
            error_msg = f"❌ 点击位置失败: ({x}, {y})"
            logger.error(error_msg)
            return error_msg
    except RuntimeError as e:
        logger.error(f"点击位置失败: {str(e)}")
        return f"❌ 点击位置失败: {str(e)}"
    except Exception as e:
        error_msg = f"❌ 点击位置异常: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("ocr_screen_detailed")
def mcp_ocr_screen_detailed() -> List[OCRResult]:
    """
    获取屏幕上的所有文字及其详细位置信息
    
    Returns:
        List[OCRResult]: 包含识别文本、置信度和位置信息的列表
    """
    try:
        results = ocr_manager.ocr_screen_detailed()
        logger.info(f"OCR详细识别成功，共识别到 {len(results)} 个文本块")
        return [OCRResult(**result) for result in results]
    except RuntimeError as e:
        logger.error(f"OCR详细识别失败: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"OCR详细识别异常: {str(e)}")
        return []

# ==================== 文件管理工具 ====================

@mcp.tool("list_files")
def mcp_list_files(
    dir_path: str = Field("/sdcard", description="要列出内容的目录路径，默认为/sdcard")
) -> str:
    """列出指定目录的文件和子目录"""
    try:
        result = list_files(dir_path)
        logger.info(f"列出目录 {dir_path} 成功")
        return result
    except Exception as e:
        error_msg = f"❌ 列出文件失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("push_file")
def mcp_push_file(
    local_path: str = Field(description="本地文件路径"),
    device_path: str = Field(description="设备上的目标路径")
) -> str:
    """将文件推送到设备"""
    try:
        result = push_file(local_path, device_path)
        logger.info(f"推送文件 {local_path} 到 {device_path} 成功")
        return result
    except Exception as e:
        error_msg = f"❌ 推送文件失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("pull_file")
def mcp_pull_file(
    device_path: str = Field(description="设备上的文件路径"),
    local_path: str = Field(description="本地保存路径")
) -> str:
    """从设备拉取文件"""
    try:
        result = pull_file(device_path, local_path)
        logger.info(f"拉取文件 {device_path} 到 {local_path} 成功")
        return result
    except Exception as e:
        error_msg = f"❌ 拉取文件失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("read_text_file")
def mcp_read_text_file(
    device_path: str = Field(description="设备上的文件路径")
) -> str:
    """读取设备上的文本文件"""
    try:
        result = read_text_file(device_path)
        logger.info(f"读取文件 {device_path} 成功")
        return result
    except Exception as e:
        error_msg = f"❌ 读取文件失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("download_file")
def mcp_download_file(
    device_path: str = Field(description="设备上的文件路径")
) -> str:
    """下载设备上的文件并转换为base64"""
    try:
        result = download_file(device_path)
        logger.info(f"下载文件 {device_path} 成功")
        return result
    except Exception as e:
        error_msg = f"❌ 下载文件失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("write_text_file")
def mcp_write_text_file(
    device_path: str = Field(description="设备上的文件路径"),
    content: str = Field(description="要写入的文本内容")
) -> str:
    """在设备上创建或覆盖文本文件"""
    try:
        result = write_text_file(device_path, content)
        logger.info(f"写入文件 {device_path} 成功")
        return result
    except Exception as e:
        error_msg = f"❌ 写入文件失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("delete_file")
def mcp_delete_file(
    device_path: str = Field(description="设备上的文件或目录路径")
) -> str:
    """删除设备上的文件或目录"""
    try:
        result = delete_file(device_path)
        logger.info(f"删除 {device_path} 成功")
        return result
    except Exception as e:
        error_msg = f"❌ 删除失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("create_directory")
def mcp_create_directory(
    dir_path: str = Field(description="要创建的目录路径")
) -> str:
    """在设备上创建目录"""
    try:
        result = create_directory(dir_path)
        logger.info(f"创建目录 {dir_path} 成功")
        return result
    except Exception as e:
        error_msg = f"❌ 创建目录失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("get_file_info")
def mcp_get_file_info(
    file_path: str = Field(description="文件路径")
) -> str:
    """获取文件详细信息"""
    try:
        result = get_file_info(file_path)
        logger.info(f"获取文件 {file_path} 信息成功")
        return result
    except Exception as e:
        error_msg = f"❌ 获取文件信息失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 录屏功能工具 ====================

@mcp.tool("record_screen")
def mcp_record_screen(
    duration: int = Field(10, description="录制时长（秒），默认10秒，最大180秒")
) -> str:
    """录制设备屏幕视频"""
    try:
        result = record_screen(duration)
        logger.info(f"录制屏幕 {duration} 秒完成")
        return result
    except Exception as e:
        error_msg = f"❌ 录制屏幕失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("take_screenshot_base64")
def mcp_take_screenshot_base64() -> str:
    """截取屏幕并返回base64编码的图片"""
    try:
        result = take_screenshot_base64()
        logger.info("截图成功")
        return result
    except Exception as e:
        error_msg = f"❌ 截图失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("get_screen_resolution")
def mcp_get_screen_resolution() -> str:
    """获取屏幕分辨率"""
    try:
        result = get_screen_resolution()
        logger.info("获取屏幕分辨率成功")
        return result
    except Exception as e:
        error_msg = f"❌ 获取屏幕分辨率失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("get_screen_density")
def mcp_get_screen_density() -> str:
    """获取屏幕密度"""
    try:
        result = get_screen_density()
        logger.info("获取屏幕密度成功")
        return result
    except Exception as e:
        error_msg = f"❌ 获取屏幕密度失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("get_display_info")
def mcp_get_display_info() -> str:
    """获取显示信息汇总"""
    try:
        result = get_display_info()
        logger.info("获取显示信息成功")
        return result
    except Exception as e:
        error_msg = f"❌ 获取显示信息失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# ==================== 元素发现工具 ====================

@mcp.tool("dump_ui_hierarchy")
def mcp_dump_ui_hierarchy() -> str:
    """获取当前页面的完整UI层次结构（XML格式）"""
    try:
        result = dump_ui_hierarchy()
        logger.info("获取UI层次结构成功")
        return result
    except Exception as e:
        error_msg = f"❌ 获取UI层次结构失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("get_all_elements")
def mcp_get_all_elements() -> List[Dict[str, Any]]:
    """获取当前页面的所有元素信息"""
    try:
        result = get_all_elements()
        logger.info(f"获取到 {len(result)} 个元素")
        return result
    except Exception as e:
        error_msg = f"❌ 获取元素列表失败: {str(e)}"
        logger.error(error_msg)
        return [{"error": error_msg}]

@mcp.tool("find_elements_by_text")
def mcp_find_elements_by_text(
    text: str = Field(description="要查找的文本内容"),
    contains: bool = Field(True, description="是否包含匹配，默认True")
) -> List[Dict[str, Any]]:
    """根据文本内容查找元素"""
    try:
        result = find_elements_by_text(text, contains)
        logger.info(f"根据文本 '{text}' 找到 {len(result)} 个元素")
        return result
    except Exception as e:
        error_msg = f"❌ 查找元素失败: {str(e)}"
        logger.error(error_msg)
        return [{"error": error_msg}]

@mcp.tool("find_elements_by_resource_id")
def mcp_find_elements_by_resource_id(
    resource_id: str = Field(description="资源ID")
) -> List[Dict[str, Any]]:
    """根据资源ID查找元素"""
    try:
        result = find_elements_by_resource_id(resource_id)
        logger.info(f"根据资源ID '{resource_id}' 找到 {len(result)} 个元素")
        return result
    except Exception as e:
        error_msg = f"❌ 查找元素失败: {str(e)}"
        logger.error(error_msg)
        return [{"error": error_msg}]

@mcp.tool("find_clickable_elements")
def mcp_find_clickable_elements() -> List[Dict[str, Any]]:
    """查找所有可点击的元素"""
    try:
        result = find_clickable_elements()
        logger.info(f"找到 {len(result)} 个可点击元素")
        return result
    except Exception as e:
        error_msg = f"❌ 查找可点击元素失败: {str(e)}"
        logger.error(error_msg)
        return [{"error": error_msg}]

@mcp.tool("find_elements_by_class")
def mcp_find_elements_by_class(
    class_name: str = Field(description="类名")
) -> List[Dict[str, Any]]:
    """根据类名查找元素"""
    try:
        result = find_elements_by_class(class_name)
        logger.info(f"根据类名 '{class_name}' 找到 {len(result)} 个元素")
        return result
    except Exception as e:
        error_msg = f"❌ 查找元素失败: {str(e)}"
        logger.error(error_msg)
        return [{"error": error_msg}]

@mcp.tool("get_element_info_at_position")
def mcp_get_element_info_at_position(
    x: int = Field(description="X坐标"),
    y: int = Field(description="Y坐标")
) -> Optional[Dict[str, Any]]:
    """获取指定坐标位置的元素信息"""
    try:
        result = get_element_info_at_position(x, y)
        if result:
            logger.info(f"获取位置 ({x}, {y}) 的元素信息成功")
        else:
            logger.info(f"位置 ({x}, {y}) 未找到元素")
        return result
    except Exception as e:
        error_msg = f"❌ 获取元素信息失败: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool("get_element_suggestions")
def mcp_get_element_suggestions() -> Dict[str, List[Dict[str, Any]]]:
    """获取页面元素建议，分类整理可操作的元素"""
    try:
        result = get_element_suggestions()
        logger.info("获取元素建议成功")
        return result
    except Exception as e:
        error_msg = f"❌ 获取元素建议失败: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool("search_elements")
def mcp_search_elements(
    keyword: str = Field(description="搜索关键字")
) -> List[Dict[str, Any]]:
    """搜索包含关键字的元素（在text、resourceId、description中搜索）"""
    try:
        result = search_elements(keyword)
        logger.info(f"搜索关键字 '{keyword}' 找到 {len(result)} 个元素")
        return result
    except Exception as e:
        error_msg = f"❌ 搜索元素失败: {str(e)}"
        logger.error(error_msg)
        return [{"error": error_msg}]

# ==================== 服务器启动 ====================

def main():
    """启动MCP服务器"""
    logger.info("正在启动UIAutomator2 MCP Server...")

    try:
        # 尝试初始化设备连接
        init_result = init_uiautomator2()
        logger.info(f"设备初始化结果: {init_result}")
    except Exception as e:
        logger.warning(f"启动时设备初始化失败（可能需要手动初始化）: {str(e)}")

    # 启动MCP服务器（stdio模式，不需要host和port参数）
    mcp.run()

if __name__ == "__main__":
    main()
