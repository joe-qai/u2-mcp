"""
性能分析模块 - 提供Android设备性能监控和分析功能

本模块提供应用性能分析、设备日志收集、电池信息等功能。
"""

from typing import Optional
import time
import tempfile
from .android import get_device


def get_battery_info() -> str:
    """
    获取电池信息
    
    Returns:
        str: 电池详细信息
    """
    device = get_device()
    try:
        output = device.shell("dumpsys battery")
        return output.strip() if output else "无法获取电池信息"
    except Exception as e:
        return f"获取电池信息失败: {str(e)}"


def get_memory_info() -> str:
    """
    获取内存信息
    
    Returns:
        str: 内存使用情况
    """
    device = get_device()
    try:
        output = device.shell("dumpsys meminfo")
        return output.strip() if output else "无法获取内存信息"
    except Exception as e:
        return f"获取内存信息失败: {str(e)}"


def get_cpu_info() -> str:
    """
    获取CPU信息
    
    Returns:
        str: CPU使用情况
    """
    device = get_device()
    try:
        output = device.shell("dumpsys cpuinfo")
        return output.strip() if output else "无法获取CPU信息"
    except Exception as e:
        return f"获取CPU信息失败: {str(e)}"


def analyze_app_performance(package_name: str, duration: int = 10) -> str:
    """
    分析应用性能
    
    Args:
        package_name: 应用包名
        duration: 分析时长（秒），默认10秒
        
    Returns:
        str: 性能分析结果
    """
    device = get_device()
    try:
        # 启动应用
        device.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        time.sleep(2)
        
        performance_data = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # 获取内存使用
            mem_info = device.shell(f"dumpsys meminfo {package_name}")
            
            # 获取CPU使用
            cpu_info = device.shell(f"top -n 1 | grep {package_name}")
            
            # 获取电池消耗
            battery_info = device.shell("dumpsys battery | grep level")
            
            performance_data.append(
                f"时间点: {time.time() - start_time:.2f}秒\n"
                f"CPU: {cpu_info.strip() if cpu_info else '无法获取'}\n"
                f"电池: {battery_info.strip() if battery_info else '无法获取'}\n"
                f"内存摘要: {' '.join(mem_info.split()[:20]) if mem_info else '无法获取'}"
            )
            
            time.sleep(1)
        
        return "性能分析结果:\n\n" + "\n\n".join(performance_data)
    except Exception as e:
        return f"分析应用性能失败: {str(e)}"


def collect_device_logs(duration: int = 10) -> str:
    """
    收集设备日志
    
    Args:
        duration: 收集日志的时长（秒），默认10秒
        
    Returns:
        str: 收集到的日志内容
    """
    device = get_device()
    try:
        # 清除旧日志
        device.shell("logcat -c")
        time.sleep(0.5)
        
        # 收集指定时长的日志
        time.sleep(duration)
        
        # 获取日志
        logs = device.shell("logcat -d -v threadtime")
        
        if len(logs) > 10000:
            logs = "...\n[日志太长，只显示最后部分]\n" + logs[-10000:]
        
        return logs
    except Exception as e:
        return f"收集设备日志失败: {str(e)}"


def get_app_memory_usage(package_name: str) -> str:
    """
    获取应用内存使用情况
    
    Args:
        package_name: 应用包名
        
    Returns:
        str: 内存使用详情
    """
    device = get_device()
    try:
        output = device.shell(f"dumpsys meminfo {package_name}")
        return output.strip() if output else "无法获取应用内存信息"
    except Exception as e:
        return f"获取应用内存使用失败: {str(e)}"


def get_app_cpu_usage(package_name: str) -> str:
    """
    获取应用CPU使用情况
    
    Args:
        package_name: 应用包名
        
    Returns:
        str: CPU使用详情
    """
    device = get_device()
    try:
        output = device.shell(f"top -n 1 | grep {package_name}")
        return output.strip() if output else "应用未运行或无法获取CPU信息"
    except Exception as e:
        return f"获取应用CPU使用失败: {str(e)}"


def get_system_info() -> str:
    """
    获取系统信息汇总
    
    Returns:
        str: 系统信息汇总
    """
    device = get_device()
    try:
        info = []
        
        # 获取系统版本
        android_version = device.shell("getprop ro.build.version.release")
        info.append(f"Android版本: {android_version.strip()}")
        
        # 获取设备型号
        model = device.shell("getprop ro.product.model")
        info.append(f"设备型号: {model.strip()}")
        
        # 获取内存信息
        mem_info = device.shell("cat /proc/meminfo | grep MemTotal")
        if mem_info:
            info.append(f"总内存: {mem_info.split()[1]} KB")
        
        # 获取存储信息
        storage = device.shell("df /data | tail -1")
        if storage:
            parts = storage.split()
            if len(parts) >= 4:
                info.append(f"存储使用: {parts[4] if len(parts) > 4 else '未知'}")
        
        return "\n".join(info)
    except Exception as e:
        return f"获取系统信息失败: {str(e)}"
