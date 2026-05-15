"""
OCR识别模块 - 提供屏幕文本识别功能

本模块基于PaddleOCR实现屏幕文本识别，支持文本定位和点击操作。
"""

from typing import Optional, Tuple, List, Dict, Any
import time
from PIL import Image
import numpy as np

try:
    from paddleocr import PaddleOCR
    PADDLE_OCR_AVAILABLE = True
except ImportError:
    PADDLE_OCR_AVAILABLE = False

from .android import get_screenshot


class OCRManager:
    """
    OCR管理器 - 提供屏幕文本识别和定位功能
    
    特性：
    - 单例模式，避免重复初始化OCR模型
    - 结果缓存，1秒内重复调用返回缓存结果
    """

    _instance = None
    _ocr = None
    _last_ocr_time = 0.0
    _last_ocr_result = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRManager, cls).__new__(cls)
            cls._ocr = None
            cls._last_ocr_time = 0.0
            cls._last_ocr_result = None
        return cls._instance

    def _ensure_initialized(self) -> None:
        """确保OCR引擎已初始化"""
        if not PADDLE_OCR_AVAILABLE:
            raise RuntimeError("PaddleOCR未安装，请安装paddleocr包")
        
        if self._ocr is None:
            # 初始化PaddleOCR，使用中英文模型
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang="ch",
                show_log=False
            )

    def ocr_screen(self) -> str:
        """
        获取屏幕上的所有文字，以文本形式返回
        
        Returns:
            str: 识别到的文本，每行一个条目
            
        Raises:
            RuntimeError: OCR未安装或识别失败
        """
        self._ensure_initialized()

        try:
            screenshot = get_screenshot()
            result = self._ocr.ocr(np.array(screenshot), cls=True)
            
            text_lines = []
            if result and result[0]:
                for line in result[0]:
                    if line[1] and line[1][0]:
                        text_lines.append(line[1][0])
            
            return "\n".join(text_lines)
        except Exception as e:
            raise RuntimeError(f"OCR识别失败: {str(e)}") from e

    def ocr_screen_detailed(self) -> List[Dict[str, Any]]:
        """
        获取屏幕上的所有文字及其位置信息
        
        Returns:
            List[Dict]: 包含文本内容和位置信息的列表
            
        Raises:
            RuntimeError: OCR未安装或识别失败
        """
        self._ensure_initialized()

        try:
            screenshot = get_screenshot()
            result = self._ocr.ocr(np.array(screenshot), cls=True)
            
            detailed_results = []
            if result and result[0]:
                for line in result[0]:
                    if line[1] and line[1][0]:
                        # line[0] 是边界框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                        bbox = line[0]
                        text = line[1][0]
                        confidence = line[1][1]
                        
                        # 计算中心点
                        x_center = (bbox[0][0] + bbox[2][0]) / 2
                        y_center = (bbox[0][1] + bbox[2][1]) / 2
                        
                        detailed_results.append({
                            "text": text,
                            "confidence": confidence,
                            "x": int(x_center),
                            "y": int(y_center),
                            "bbox": [[int(p[0]), int(p[1])] for p in bbox]
                        })
            
            return detailed_results
        except Exception as e:
            raise RuntimeError(f"OCR识别失败: {str(e)}") from e

    def find_text_position(self, target_text: str) -> Optional[Tuple[int, int]]:
        """
        在屏幕上查找指定文本的位置（中心点坐标）
        
        Args:
            target_text: 要查找的目标文本
            
        Returns:
            Optional[Tuple[int, int]]: 文本中心点坐标 (x, y)，未找到返回None
            
        Raises:
            RuntimeError: OCR未安装或识别失败
        """
        self._ensure_initialized()

        try:
            screenshot = get_screenshot()
            result = self._ocr.ocr(np.array(screenshot), cls=True)
            
            if result and result[0]:
                for line in result[0]:
                    if line[1] and line[1][0]:
                        text = line[1][0]
                        if target_text in text or text in target_text:
                            bbox = line[0]
                            x_center = (bbox[0][0] + bbox[2][0]) / 2
                            y_center = (bbox[0][1] + bbox[2][1]) / 2
                            return int(x_center), int(y_center)
            
            return None
        except Exception as e:
            raise RuntimeError(f"查找文本位置失败: {str(e)}") from e

    def click_text(self, target_text: str) -> bool:
        """
        在屏幕上查找并点击指定文本
        
        Args:
            target_text: 要点击的目标文本
            
        Returns:
            bool: 是否成功点击
            
        Raises:
            RuntimeError: OCR未安装或识别失败
        """
        position = self.find_text_position(target_text)
        if position:
            return self.click_position(position[0], position[1])
        return False

    def click_position(self, x: int, y: int) -> bool:
        """
        点击屏幕上指定位置
        
        Args:
            x: 横坐标
            y: 纵坐标
            
        Returns:
            bool: 是否点击成功
            
        Raises:
            RuntimeError: 设备未初始化或点击失败
        """
        from .android import get_device

        try:
            device = get_device()
            device.click(x, y)
            time.sleep(0.5)
            return True
        except Exception as e:
            raise RuntimeError(f"点击位置失败: {str(e)}") from e

    def is_text_on_screen(self, target_text: str) -> bool:
        """
        检查屏幕上是否存在指定文本
        
        Args:
            target_text: 要检查的目标文本
            
        Returns:
            bool: 是否存在
            
        Raises:
            RuntimeError: OCR未安装或识别失败
        """
        return self.find_text_position(target_text) is not None
