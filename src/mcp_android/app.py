"""
应用管理模块 - 提供Android应用管理功能

本模块提供应用启动、停止、设备初始化等功能。
"""

import uiautomator2 as u2
from typing import Tuple, Optional, Dict, Any
import time
import subprocess
import os
from .android import set_device, get_device


def init_uiautomator2(serial: Optional[str] = None) -> str:
    """
    初始化 uiautomator2，包括安装和启动服务
    
    Args:
        serial: 设备序列号，多设备时必填。为空时使用环境变量 ANDROID_SERIAL 或自动选择
        
    Returns:
        str: 初始化结果信息
    """
    try:
        # 检查ADB服务是否运行
        try:
            subprocess.run(["adb", "devices"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            return "❌ ADB服务未运行，请启动ADB服务"
        except FileNotFoundError:
            return "❌ 未找到ADB命令，请确保Android SDK已正确配置"

        # 获取设备列表
        adb_output = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True
        ).stdout
        
        # 解析已连接设备列表
        connected_devices = []
        for line in adb_output.strip().split("\n")[1:]:
            if line.strip() and "\tdevice" in line:
                connected_devices.append(line.split("\t")[0].strip())

        if not connected_devices:
            return "❌ 未检测到已连接的设备，请确保设备已通过USB或WiFi连接"

        # 确定目标设备序列号：参数 > 环境变量 > 单设备自动选择
        device_serial = serial or os.environ.get("ANDROID_SERIAL")
        if not device_serial:
            if len(connected_devices) > 1:
                return (
                    f"❌ 检测到多个设备: {', '.join(connected_devices)}\n"
                    "请通过参数指定serial或设置ANDROID_SERIAL环境变量"
                )
            device_serial = connected_devices[0]

        # 初始化设备连接
        device = u2.connect(device_serial)

        # 确保设备已连接
        if not device:
            return "❌ 无法建立设备连接"

        # 设置全局设备对象
        set_device(device)

        # 安装必要的APK（静默安装，忽略已安装错误）
        try:
            device.app_install(
                "https://github.com/openatx/android-uiautomator-server/releases/download/2.3.1/app-uiautomator.apk"
            )
            device.app_install(
                "https://github.com/openatx/android-uiautomator-server/releases/download/2.3.1/app-uiautomator-test.apk"
            )
        except Exception:
            pass  # 如果已经安装则忽略错误

        # 启动UIAutomator服务
        device.app_start("com.github.uiautomator")
        device.app_start("com.github.uiautomator.test")
        time.sleep(2)

        # 检查服务是否正常运行
        try:
            device.info
            return f"✅ UIAutomator2初始化successfully\n设备序列号: {device_serial}"
        except Exception:
            return "❌ UIAutomator服务启动失败，请检查设备状态"

    except Exception as e:
        return f"❌ UIAutomator2初始化失败: {str(e)}"


def check_uiautomator2() -> Dict[str, Any]:
    """
    检查 uiautomator2 是否正确安装和运行
    
    Returns:
        dict: 包含检查结果的字典
    """
    status: Dict[str, Any] = {
        "adb_server": False,
        "device_connected": False,
        "service_running": False,
        "app_installed": False,
        "device_info": None,
        "error": None,
        "serial": None,
        "connected_devices": []
    }

    try:
        # 检查ADB服务
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            if result.returncode == 0:
                status["adb_server"] = True
                # 解析设备列表
                for line in result.stdout.strip().split("\n")[1:]:
                    if line.strip() and "\tdevice" in line:
                        status["connected_devices"].append(line.split("\t")[0].strip())
        except FileNotFoundError:
            status["error"] = "ADB命令未找到，请配置Android SDK环境变量"
            return status

        # 通过 get_device() 检查设备连接
        try:
            device = get_device()
            status["device_connected"] = True
            status["serial"] = device.serial
        except RuntimeError as e:
            status["error"] = str(e)
            return status

        # 检查服务状态
        try:
            device.info
            status["service_running"] = True
        except Exception as e:
            status["service_running"] = False
            status["error"] = f"UIAutomator服务未运行: {str(e)}"

        # 检查应用是否安装
        try:
            packages = device.shell(["pm", "list", "packages"]).output
            status["app_installed"] = "com.github.uiautomator" in packages
        except Exception as e:
            status["app_installed"] = False
            status["error"] = f"无法获取包列表: {str(e)}"

        # 获取设备信息
        try:
            status["device_info"] = {
                "serial": device.serial,
                "model": device.info.get("model", "unknown"),
                "android_version": device.info.get("androidVersion", "unknown"),
                "screen_size": device.window_size()
            }
        except Exception as e:
            status["device_info"] = {"error": str(e)}

        return status
    except Exception as e:
        status["error"] = str(e)
        return status


def restart_uiautomator2() -> str:
    """
    重启 uiautomator2 服务
    
    Returns:
        str: 重启结果信息
    """
    try:
        device = get_device()

        # 停止现有服务
        try:
            device.app_stop("com.github.uiautomator")
            device.app_stop("com.github.uiautomator.test")
            time.sleep(1)

            # 强制停止
            device.shell("am force-stop com.github.uiautomator")
            device.shell("am force-stop com.github.uiautomator.test")
            time.sleep(1)
        except Exception as e:
            pass  # 忽略停止失败

        # 重新启动服务
        device.app_start("com.github.uiautomator")
        device.app_start("com.github.uiautomator.test")
        time.sleep(2)

        # 验证服务是否正常运行
        try:
            device.info
            return "✅ UIAutomator2服务重启成功"
        except Exception as e:
            return f"❌ 服务重启后未正常运行: {str(e)}"

    except RuntimeError as e:
        return f"❌ {str(e)}"
    except Exception as e:
        return f"❌ UIAutomator2服务重启失败: {str(e)}"


def start_app(package_name: str, activity: Optional[str] = None) -> bool:
    """
    启动应用
    
    Args:
        package_name: 应用包名
        activity: 可选的Activity名称
        
    Returns:
        bool: 是否启动成功
    """
    try:
        device = get_device()

        # 先停止应用，确保重新启动
        try:
            device.app_stop(package_name)
            time.sleep(0.5)
        except Exception:
            pass

        # 启动应用
        if activity:
            device.app_start(package_name, activity, wait=True)
        else:
            device.app_start(package_name, wait=True)
        
        time.sleep(1)  # 等待应用启动
        return True
    except Exception as e:
        return False


def stop_app(package_name: str) -> bool:
    """
    停止应用
    
    Args:
        package_name: 应用包名
        
    Returns:
        bool: 是否停止成功
    """
    try:
        device = get_device()
        device.app_stop(package_name)
        return True
    except Exception:
        return False


def get_current_app() -> Tuple[str, str]:
    """
    获取当前运行的应用包名和活动名
    
    Returns:
        Tuple[str, str]: (package_name, activity_name)
    """
    try:
        device = get_device()
        current = device.app_current()
        return current.get("package", ""), current.get("activity", "")
    except Exception:
        return "", ""


def clear_app_data(package_name: str) -> bool:
    """
    清除应用数据
    
    Args:
        package_name: 应用包名
        
    Returns:
        bool: 是否清除成功
    """
    try:
        device = get_device()
        device.shell(f"pm clear {package_name}")
        return True
    except Exception:
        return False


def install_apk(apk_path: str) -> bool:
    """
    安装APK文件
    
    Args:
        apk_path: APK文件路径（设备上的路径）
        
    Returns:
        bool: 是否安装成功
    """
    try:
        device = get_device()
        device.app_install(apk_path)
        return True
    except Exception:
        return False