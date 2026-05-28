"""
网络工具模块 - 提供Android设备网络管理功能

本模块提供WiFi、移动数据、飞行模式等网络管理功能。
"""

from typing import Optional
from .android import get_device


def toggle_wifi(enable: bool) -> str:
    """
    打开或关闭WiFi
    
    Args:
        enable: True开启，False关闭
        
    Returns:
        str: 操作结果信息
    """
    device = get_device()
    try:
        state = "enable" if enable else "disable"
        device.shell(f"svc wifi {state}")
        return f"WiFi已{'开启' if enable else '关闭'}"
    except Exception as e:
        return f"操作WiFi失败: {str(e)}"


def toggle_mobile_data(enable: bool) -> str:
    """
    打开或关闭移动数据
    
    Args:
        enable: True开启，False关闭
        
    Returns:
        str: 操作结果信息
    """
    device = get_device()
    try:
        state = "enable" if enable else "disable"
        device.shell(f"svc data {state}")
        return f"移动数据已{'开启' if enable else '关闭'}"
    except Exception as e:
        return f"操作移动数据失败: {str(e)}"


def toggle_airplane_mode(enable: bool) -> str:
    """
    打开或关闭飞行模式
    
    Args:
        enable: True开启，False关闭
        
    Returns:
        str: 操作结果信息
    """
    device = get_device()
    try:
        mode = 1 if enable else 0
        device.shell(f"settings put global airplane_mode_on {mode}")
        device.shell("am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true")
        return f"飞行模式已{'开启' if enable else '关闭'}"
    except Exception as e:
        return f"操作飞行模式失败: {str(e)}"


def get_wifi_info() -> str:
    """
    获取WiFi连接信息
    
    Returns:
        str: WiFi连接状态信息
    """
    device = get_device()
    try:
        output = device.shell("dumpsys wifi | grep 'mNetworkInfo\\|SSID'")
        return output.strip() if output else "未获取到WiFi信息"
    except Exception as e:
        return f"获取WiFi信息失败: {str(e)}"


def get_ip_address() -> str:
    """
    获取设备IP地址
    
    Returns:
        str: IP地址信息
    """
    device = get_device()
    try:
        output = device.shell("ip addr show wlan0 | grep 'inet '")
        if output:
            ip = output.split()[1].split('/')[0]
            return f"WiFi IP地址: {ip}"
        return "未获取到IP地址"
    except Exception as e:
        return f"获取IP地址失败: {str(e)}"


def ping(host: str, count: int = 4) -> str:
    """
    Ping网络主机
    
    Args:
        host: 目标主机地址
        count: ping次数，默认4次
        
    Returns:
        str: ping结果
    """
    device = get_device()
    try:
        output = device.shell(f"ping -c {count} {host}")
        return output.strip() if output else "ping无响应"
    except Exception as e:
        return f"Ping失败: {str(e)}"


def get_network_info() -> str:
    """
    获取网络详细信息
    
    Returns:
        str: 网络信息汇总
    """
    device = get_device()
    try:
        info = []
        
        # 获取WiFi状态
        wifi_state = device.shell("settings get global wifi_on")
        info.append(f"WiFi状态: {'开启' if wifi_state.strip() == '1' else '关闭'}")
        
        # 获取移动数据状态
        data_state = device.shell("settings get global mobile_data")
        info.append(f"移动数据: {'开启' if data_state.strip() == '1' else '关闭'}")
        
        # 获取飞行模式状态
        airplane_state = device.shell("settings get global airplane_mode_on")
        info.append(f"飞行模式: {'开启' if airplane_state.strip() == '1' else '关闭'}")
        
        # 获取IP地址
        ip_output = device.shell("ip addr show wlan0 | grep 'inet '")
        if ip_output:
            ip = ip_output.split()[1].split('/')[0]
            info.append(f"WiFi IP: {ip}")
        
        return "\n".join(info)
    except Exception as e:
        return f"获取网络信息失败: {str(e)}"
