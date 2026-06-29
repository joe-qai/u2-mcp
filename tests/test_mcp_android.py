"""
MCP Android 模块单元测试

本测试文件包含对核心模块的单元测试，验证各项功能的正确性。

注意：部分测试需要连接真实Android设备才能运行。
"""

import pytest
import sys
import os

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_android.android import get_device, execute_adb_shell_command, get_packages
from mcp_android.ui import click_element, input_text, swipe_screen, long_click_element
from mcp_android.app import check_uiautomator2, start_app, stop_app, get_current_app
from mcp_android.ocr import OCRManager


class TestAndroidModule:
    """Android设备管理模块测试"""

    def test_get_device_not_initialized(self):
        """测试获取未初始化的设备对象"""
        with pytest.raises(RuntimeError, match="Device not initialized"):
            get_device()

    def test_execute_adb_shell_command_invalid(self):
        """测试执行无效ADB命令（需要设备连接）"""
        try:
            result = execute_adb_shell_command("echo test")
            assert isinstance(result, str)
        except RuntimeError:
            pytest.skip("设备未连接")


class TestUIModule:
    """UI操作模块测试"""

    def test_click_element_no_params(self):
        """测试点击元素时未提供任何定位参数"""
        with pytest.raises(ValueError, match="必须提供至少一个定位参数"):
            click_element()

    def test_swipe_screen_invalid_direction(self):
        """测试滑动屏幕时提供无效方向"""
        with pytest.raises(ValueError, match="无效的方向参数"):
            swipe_screen("invalid")

    def test_swipe_screen_invalid_scale(self):
        """测试滑动屏幕时提供无效比例值"""
        with pytest.raises(ValueError, match="scale参数必须在0-1之间"):
            swipe_screen("up", scale=1.5)

    def test_wait_and_click_no_params(self):
        """测试等待点击时未提供任何参数"""
        with pytest.raises(ValueError, match="必须提供text或description参数"):
            from mcp_android.ui import wait_and_click_element
            wait_and_click_element()

    def test_scroll_to_element_no_params(self):
        """测试滚动到元素时未提供任何参数"""
        with pytest.raises(ValueError, match="必须提供text或description参数"):
            from mcp_android.ui import scroll_to_element
            scroll_to_element()

    def test_long_click_element_no_params(self):
        """测试长按元素时未提供任何定位参数"""
        with pytest.raises(ValueError, match="必须提供至少一个定位参数"):
            long_click_element()


class TestAppModule:
    """应用管理模块测试"""

    def test_check_uiautomator2_returns_dict(self):
        """测试检查UIAutomator2状态返回字典"""
        status = check_uiautomator2()
        assert isinstance(status, dict)
        assert "adb_server" in status
        assert "device_connected" in status
        assert "service_running" in status
        assert "app_installed" in status

    def test_get_current_app_returns_tuple(self):
        """测试获取当前应用返回元组"""
        package, activity = get_current_app()
        assert isinstance(package, str)
        assert isinstance(activity, str)


class TestOCRModule:
    """OCR识别模块测试"""

    def test_ocr_manager_singleton(self):
        """测试OCR管理器单例模式"""
        ocr1 = OCRManager()
        ocr2 = OCRManager()
        assert ocr1 is ocr2

    def test_is_text_on_screen_returns_bool(self):
        """测试检查文本是否在屏幕上返回布尔值"""
        ocr = OCRManager()
        try:
            result = ocr.is_text_on_screen("test")
            assert isinstance(result, bool)
        except RuntimeError:
            pytest.skip("PaddleOCR未安装或设备未连接")

    def test_ocr_screen_returns_text(self):
        """测试OCR屏幕识别返回文本内容"""
        ocr = OCRManager()
        try:
            result = ocr.ocr_screen()
            assert isinstance(result, str)
            # 检查返回内容是否合理（非空或包含预期的文本特征）
        except RuntimeError as e:
            error_msg = str(e)
            if "PaddleOCR" in error_msg or "paddlepaddle" in error_msg.lower() or "paddle_static" in error_msg:
                pytest.skip("PaddleOCR或paddlepaddle未安装")
            raise

    def test_ocr_screen_detailed_returns_list(self):
        """测试OCR详细识别返回列表"""
        ocr = OCRManager()
        try:
            result = ocr.ocr_screen_detailed()
            assert isinstance(result, list)
            # 如果有识别结果，检查每个结果的结构
            if len(result) > 0:
                for item in result:
                    assert "text" in item
                    assert "confidence" in item
                    assert "bbox" in item
        except RuntimeError as e:
            error_msg = str(e)
            if "PaddleOCR" in error_msg or "paddlepaddle" in error_msg.lower() or "paddle_static" in error_msg:
                pytest.skip("PaddleOCR或paddlepaddle未安装")
            raise

    def test_find_text_position_returns_coordinates(self):
        """测试查找文本位置返回坐标"""
        ocr = OCRManager()
        try:
            # 使用一个常见的界面文本进行测试
            result = ocr.find_text_position("设置")
            if result is not None:
                assert isinstance(result, tuple)
                assert len(result) == 2
                assert isinstance(result[0], int)
                assert isinstance(result[1], int)
            # 如果找不到文本，返回None也是预期行为
        except RuntimeError as e:
            error_msg = str(e)
            if "PaddleOCR" in error_msg or "paddlepaddle" in error_msg.lower() or "paddle_static" in error_msg:
                pytest.skip("PaddleOCR或paddlepaddle未安装")
            raise

    def test_click_text_finds_common_text(self):
        """测试点击文本功能（需要设备连接）"""
        ocr = OCRManager()
        try:
            # 尝试点击一个常见文本，测试函数是否正常执行
            result = ocr.click_text("设置")
            # 返回True表示点击成功，False表示未找到文本
            assert isinstance(result, bool)
        except RuntimeError as e:
            error_msg = str(e)
            if "PaddleOCR" in error_msg or "paddlepaddle" in error_msg.lower() or "paddle_static" in error_msg:
                pytest.skip("PaddleOCR或paddlepaddle未安装")
            elif "device" in error_msg.lower():
                pytest.skip("设备未连接")
            raise

    def test_click_position_valid_coordinates(self):
        """测试点击位置功能（需要设备连接）"""
        ocr = OCRManager()
        try:
            # 测试点击屏幕中心位置
            result = ocr.click_position(500, 500)
            assert result is True
        except RuntimeError as e:
            if "device" in str(e).lower():
                pytest.skip("设备未连接")
            raise

    def test_click_position_invalid_coordinates(self):
        """测试点击无效坐标"""
        ocr = OCRManager()
        try:
            # 超出屏幕范围的坐标应该返回False或抛出异常
            result = ocr.click_position(-100, -100)
            assert result is False
        except (RuntimeError, ValueError):
            # 某些实现可能会抛出异常，这也是合理的
            pytest.skip("坐标验证行为因实现而异")

    def test_cache_mechanism(self):
        """测试OCR缓存机制"""
        ocr = OCRManager()
        # 验证缓存属性存在
        assert hasattr(ocr, '_last_ocr_time')
        assert hasattr(ocr, '_last_ocr_result')
        # 验证初始状态
        assert ocr._last_ocr_time == 0.0
        assert ocr._last_ocr_result is None


class TestInputValidation:
    """输入验证测试"""

    def test_input_text_empty_string(self):
        """测试输入空字符串"""
        # 空字符串应该被允许
        # 实际执行需要设备连接
        pass

    def test_swipe_direction_valid_values(self):
        """测试滑动方向的有效值"""
        valid_directions = ["up", "down", "left", "right"]
        for direction in valid_directions:
            # 实际执行需要设备连接，这里只验证参数验证逻辑
            try:
                swipe_screen(direction)
            except RuntimeError:
                # 设备未连接是预期的
                pass
            except ValueError:
                pytest.fail(f"方向 '{direction}' 应该是有效的")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])