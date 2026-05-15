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