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
from typing import Optional, Any, Dict, List
from fastmcp import FastMCP, ToolInfo
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
    init_uiautomator2,
    check_uiautomator2,
    restart_uiautomator2,
    start_app,
    stop_app,
    get_current_app,
    click_element,
    input_text,
    swipe_screen,
    wait_and_click_element,
    scroll_to_element,
    long_click_element,
    execute_adb_shell_command,
    get_packages,
    get_device_info,
    OCRManager,
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
    
    # 启动MCP服务器
    mcp.run(host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
