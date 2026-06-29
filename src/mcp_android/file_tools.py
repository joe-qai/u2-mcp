"""
文件管理模块 - 提供Android设备文件管理功能

本模块提供文件上传、下载、列表、读取等文件管理功能。
"""

import base64
import os
import tempfile

from .android import get_device


def list_files(dir_path: str = "/sdcard") -> str:
    """
    列出指定目录的文件和子目录
    
    Args:
        dir_path: 要列出内容的目录路径，默认为/sdcard
        
    Returns:
        str: 文件列表信息
    """
    device = get_device()
    try:
        output = device.shell(f"ls -la {dir_path}")
        return output.strip() if output else "目录为空或不存在"
    except Exception as e:
        return f"列出文件失败: {str(e)}"


def push_file(local_path: str, device_path: str) -> str:
    """
    将文件推送到设备
    
    Args:
        local_path: 本地文件路径
        device_path: 设备上的目标路径
        
    Returns:
        str: 操作结果信息
    """
    device = get_device()
    try:
        device.push(local_path, device_path)
        return f"成功将文件 {local_path} 推送到设备 {device_path}"
    except Exception as e:
        return f"推送文件失败: {str(e)}"


def pull_file(device_path: str, local_path: str) -> str:
    """
    从设备拉取文件
    
    Args:
        device_path: 设备上的文件路径
        local_path: 本地保存路径
        
    Returns:
        str: 操作结果信息
    """
    device = get_device()
    try:
        device.pull(device_path, local_path)
        return f"成功将设备上的文件 {device_path} 拉取到本地 {local_path}"
    except Exception as e:
        return f"拉取文件失败: {str(e)}"


def read_text_file(device_path: str) -> str:
    """
    读取设备上的文本文件
    
    Args:
        device_path: 设备上的文件路径
        
    Returns:
        str: 文件内容
    """
    device = get_device()
    try:
        output = device.shell(f"cat {device_path}")
        if len(output) > 10000:
            output = output[:10000] + "...\n[文件太长，只显示前面部分]"
        return output
    except Exception as e:
        return f"读取文件失败: {str(e)}"


def download_file(device_path: str) -> str:
    """
    下载设备上的文件并转换为base64
    
    Args:
        device_path: 设备上的文件路径
        
    Returns:
        str: base64编码的文件数据
    """
    device = get_device()
    try:
        _, ext = os.path.splitext(device_path)

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
            temp_path = temp_file.name

        device.pull(device_path, temp_path)

        with open(temp_path, "rb") as file:
            base64_data = base64.b64encode(file.read()).decode("utf-8")

        os.remove(temp_path)

        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".pdf": "application/pdf",
            ".mp4": "video/mp4",
            ".mp3": "audio/mpeg",
            ".txt": "text/plain",
        }
        mime_type = mime_types.get(ext.lower(), "application/octet-stream")

        return f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        return f"下载文件失败: {str(e)}"


def write_text_file(device_path: str, content: str) -> str:
    """
    在设备上创建或覆盖文本文件
    
    Args:
        device_path: 设备上的文件路径
        content: 要写入的文本内容
        
    Returns:
        str: 操作结果信息
    """
    device = get_device()
    try:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        device.push(temp_path, device_path)
        os.remove(temp_path)

        return f"成功在设备上创建文件: {device_path}"
    except Exception as e:
        return f"创建文件失败: {str(e)}"


def delete_file(device_path: str) -> str:
    """
    删除设备上的文件或目录
    
    Args:
        device_path: 设备上的文件或目录路径
        
    Returns:
        str: 操作结果信息
    """
    device = get_device()
    try:
        device.shell(f"rm -rf {device_path}")
        return f"成功删除: {device_path}"
    except Exception as e:
        return f"删除失败: {str(e)}"


def create_directory(dir_path: str) -> str:
    """
    在设备上创建目录
    
    Args:
        dir_path: 要创建的目录路径
        
    Returns:
        str: 操作结果信息
    """
    device = get_device()
    try:
        device.shell(f"mkdir -p {dir_path}")
        return f"成功创建目录: {dir_path}"
    except Exception as e:
        return f"创建目录失败: {str(e)}"


def get_file_info(file_path: str) -> str:
    """
    获取文件详细信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件详细信息
    """
    device = get_device()
    try:
        output = device.shell(f"ls -lh {file_path}")
        return output.strip() if output else "文件不存在"
    except Exception as e:
        return f"获取文件信息失败: {str(e)}"
