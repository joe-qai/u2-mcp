"""
元素发现模块 - 提供主动发现和分析页面元素的功能

本模块提供多种方式来主动发现页面上的UI元素，包括：
- 获取完整UI层次结构
- 根据条件筛选元素
- 获取元素详细信息
- 自动发现可交互元素
"""

from typing import Any, Dict, List, Optional

from .android import get_device


def dump_ui_hierarchy() -> str:
    """
    获取当前页面的完整UI层次结构
    
    Returns:
        str: UI层次结构XML内容
    """
    device = get_device()
    try:
        # 使用UiAutomator dump获取UI层次
        result = device.shell("uiautomator2 dump /sdcard/ui_hierarchy.xml")

        # 读取dump文件内容
        output = device.shell("cat /sdcard/ui_hierarchy.xml")

        # 清理临时文件
        device.shell("rm /sdcard/ui_hierarchy.xml")

        return output.strip() if output else "无法获取UI层次结构"
    except Exception as e:
        return f"获取UI层次结构失败: {str(e)}"


def get_all_elements() -> List[Dict[str, Any]]:
    """
    获取当前页面的所有元素信息（简化版）
    
    Returns:
        List[Dict]: 元素信息列表，包含text、resourceId、className、bounds等
    """
    device = get_device()
    try:
        # 获取UI层次结构
        result = device.shell("uiautomator dump /sdcard/ui_hierarchy.xml")
        ui_xml = device.shell("cat /sdcard/ui_hierarchy.xml")
        device.shell("rm /sdcard/ui_hierarchy.xml")

        # 解析XML提取元素信息
        elements = []

        # 简单的XML解析（提取关键属性）
        import re

        # 匹配节点
        node_pattern = r'<node[^>]+/>|<node[^>]+>'
        nodes = re.findall(node_pattern, ui_xml)

        for node in nodes:
            element_info = {}

            # 提取text属性
            text_match = re.search(r'text="([^"]*)"', node)
            if text_match:
                text = text_match.group(1)
                if text:
                    element_info["text"] = text

            # 提取resource-id属性
            resource_id_match = re.search(r'resource-id="([^"]*)"', node)
            if resource_id_match:
                resource_id = resource_id_match.group(1)
                if resource_id:
                    element_info["resourceId"] = resource_id

            # 提取class属性
            class_match = re.search(r'class="([^"]*)"', node)
            if class_match:
                element_info["className"] = class_match.group(1)

            # 提取description属性
            desc_match = re.search(r'description="([^"]*)"', node)
            if desc_match:
                desc = desc_match.group(1)
                if desc:
                    element_info["description"] = desc

            # 提取bounds属性
            bounds_match = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
            if bounds_match:
                element_info["bounds"] = {
                    "left": int(bounds_match.group(1)),
                    "top": int(bounds_match.group(2)),
                    "right": int(bounds_match.group(3)),
                    "bottom": int(bounds_match.group(4))
                }
                # 计算中心点
                element_info["centerX"] = (int(bounds_match.group(1)) + int(bounds_match.group(3))) // 2
                element_info["centerY"] = (int(bounds_match.group(2)) + int(bounds_match.group(4))) // 2

            # 提取clickable属性
            clickable_match = re.search(r'clickable="([^"]*)"', node)
            if clickable_match:
                element_info["clickable"] = clickable_match.group(1) == "true"

            # 只保留有实际内容的元素
            if element_info:
                elements.append(element_info)

        return elements
    except Exception as e:
        return [{"error": f"获取元素列表失败: {str(e)}"}]


def find_elements_by_text(text: str, contains: bool = True) -> List[Dict[str, Any]]:
    """
    根据文本内容查找元素
    
    Args:
        text: 要查找的文本内容
        contains: 是否包含匹配（True为包含，False为精确匹配）
        
    Returns:
        List[Dict]: 匹配的元素列表
    """
    all_elements = get_all_elements()

    if "error" in all_elements:
        return all_elements

    matched = []
    for element in all_elements:
        element_text = element.get("text", "")
        if element_text:
            if contains and text in element_text:
                matched.append(element)
            elif not contains and text == element_text:
                matched.append(element)

    return matched


def find_elements_by_resource_id(resource_id: str) -> List[Dict[str, Any]]:
    """
    根据资源ID查找元素
    
    Args:
        resource_id: 资源ID（可以是完整ID或部分匹配）
        
    Returns:
        List[Dict]: 匹配的元素列表
    """
    all_elements = get_all_elements()

    if "error" in all_elements:
        return all_elements

    matched = []
    for element in all_elements:
        rid = element.get("resourceId", "")
        if rid and resource_id in rid:
            matched.append(element)

    return matched


def find_clickable_elements() -> List[Dict[str, Any]]:
    """
    查找所有可点击的元素
    
    Returns:
        List[Dict]: 可点击元素列表
    """
    all_elements = get_all_elements()

    if "error" in all_elements:
        return all_elements

    return [elem for elem in all_elements if elem.get("clickable", False)]


def find_elements_by_class(class_name: str) -> List[Dict[str, Any]]:
    """
    根据类名查找元素
    
    Args:
        class_name: 类名（可以是完整类名或部分匹配）
        
    Returns:
        List[Dict]: 匹配的元素列表
    """
    all_elements = get_all_elements()

    if "error" in all_elements:
        return all_elements

    matched = []
    for element in all_elements:
        cls = element.get("className", "")
        if cls and class_name in cls:
            matched.append(element)

    return matched


def get_element_info_at_position(x: int, y: int) -> Optional[Dict[str, Any]]:
    """
    获取指定坐标位置的元素信息
    
    Args:
        x: X坐标
        y: Y坐标
        
    Returns:
        Optional[Dict]: 元素信息，未找到返回None
    """
    all_elements = get_all_elements()

    if "error" in all_elements:
        return None

    for element in all_elements:
        bounds = element.get("bounds")
        if bounds:
            left = bounds["left"]
            top = bounds["top"]
            right = bounds["right"]
            bottom = bounds["bottom"]

            if left <= x <= right and top <= y <= bottom:
                return element

    return None


def get_element_suggestions() -> Dict[str, List[Dict[str, Any]]]:
    """
    获取页面元素建议，分类整理可操作的元素
    
    Returns:
        Dict: 分类的元素建议
    """
    all_elements = get_all_elements()

    if "error" in all_elements:
        return {"error": all_elements["error"]}

    suggestions = {
        "clickable_elements": [],
        "text_inputs": [],
        "buttons": [],
        "text_elements": [],
        "images": []
    }

    for element in all_elements:
        class_name = element.get("className", "")

        # 可点击元素
        if element.get("clickable", False):
            suggestions["clickable_elements"].append(element)

        # 文本输入框
        if "EditText" in class_name:
            suggestions["text_inputs"].append(element)

        # 按钮
        if "Button" in class_name or ("text" in element and element.get("clickable")):
            suggestions["buttons"].append(element)

        # 文本元素
        if "text" in element and element.get("text"):
            suggestions["text_elements"].append(element)

        # 图片元素
        if "ImageView" in class_name:
            suggestions["images"].append(element)

    return suggestions


def search_elements(keyword: str) -> List[Dict[str, Any]]:
    """
    搜索包含关键字的元素（在text、resourceId、description中搜索）
    
    Args:
        keyword: 搜索关键字
        
    Returns:
        List[Dict]: 匹配的元素列表
    """
    all_elements = get_all_elements()

    if "error" in all_elements:
        return all_elements

    keyword_lower = keyword.lower()
    matched = []

    for element in all_elements:
        text = element.get("text", "").lower()
        resource_id = element.get("resourceId", "").lower()
        description = element.get("description", "").lower()

        if keyword_lower in text or keyword_lower in resource_id or keyword_lower in description:
            matched.append(element)

    return matched
