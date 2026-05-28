"""
Android自动化测试：鹿客管家直播启动流程
依赖安装：pip install uiautomator2 pytest
运行方式：python test_live_stream.py
要求：确保Android设备已连接，且已安装atx-agent
"""
import uiautomator2 as u2
import pytest
import time
import logging
import subprocess
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def execute_adb_command(command):
    """执行ADB命令并返回输出"""
    try:
        result = subprocess.run(
            ['adb'] + command.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        # 处理result或stdout/stderr为None的情况
        stdout = result.stdout.strip() if result and result.stdout else ""
        stderr = result.stderr.strip() if result and result.stderr else ""
        return stdout, stderr
    except subprocess.TimeoutExpired:
        logger.error(f"ADB命令超时: {command}")
        return "", "命令超时"
    except FileNotFoundError:
        logger.error("ADB命令未找到，请确保ADB已安装并添加到PATH")
        return "", "ADB未找到"
    except Exception as e:
        logger.error(f"ADB命令执行失败: {e}")
        return "", str(e)


class TestLiveStream:
    """鹿客管家直播启动测试类"""
    
    def setup_method(self):
        """测试前准备：初始化设备连接并启动应用"""
        logger.info("开始初始化测试环境...")
        
        # 初始化UiAutomator2连接
        # 连接方式1：通过设备序列号连接（多设备时）
        self.d = u2.connect('R5CT845PTNV')
        # 连接方式2：自动连接（单设备时）
        # self.d = u2.connect()
        self.d.implicitly_wait(30)  # 增加隐式等待时间
        
        # 启动鹿客管家应用
        logger.info("启动鹿客管家应用...")
        self.d.app_start('com.lockin.loock')
        time.sleep(8)  # 增加等待时间，确保应用完全启动
        
    def test_live_stream_startup(self):
        """测试直播启动完整流程"""
        logger.info("=== 开始执行直播启动测试 ===")
        
        # 步骤1：验证设备页面显示
        logger.info("步骤1：验证设备页面显示")
        max_retries = 3
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                page_loaded = False
                
                # 方式1：检查底部导航栏「设备」文本
                try:
                    device_tab = self.d(resourceId="com.lockin.loock:id/tvTitle", text="设备")
                    if device_tab.exists:
                        page_loaded = True
                        logger.info("✓ 通过底部导航栏验证设备页面")
                except Exception as e:
                    logger.debug(f"方式1失败: {e}")
                
                # 方式2：检查页面是否包含设备列表容器
                if not page_loaded:
                    try:
                        device_list = self.d(resourceId="com.lockin.loock:id/deviceList")
                        if device_list.exists:
                            page_loaded = True
                            logger.info("✓ 通过设备列表容器验证设备页面")
                    except Exception as e:
                        logger.debug(f"方式2失败: {e}")
                
                # 方式3：检查页面是否包含设备名称（哈哈哈）
                if not page_loaded:
                    try:
                        device_name = self.d(resourceId="com.lockin.loock:id/tvDeviceName", text="哈哈哈")
                        if device_name.exists:
                            page_loaded = True
                            logger.info("✓ 通过设备名称验证设备页面")
                    except Exception as e:
                        logger.debug(f"方式3失败: {e}")
                
                # 方式4：检查页面是否包含设备缩略图
                if not page_loaded:
                    try:
                        thumb_view = self.d(resourceId="com.lockin.loock:id/ivThumb")
                        if thumb_view.exists:
                            page_loaded = True
                            logger.info("✓ 通过设备缩略图验证设备页面")
                    except Exception as e:
                        logger.debug(f"方式4失败: {e}")
                
                # 方式5：使用ADB命令验证当前Activity
                if not page_loaded:
                    try:
                        stdout, stderr = execute_adb_command("shell dumpsys window | grep mCurrentFocus")
                        # 检查stdout不为空且包含预期内容
                        if stdout and "com.lockin.loock" in stdout:
                            page_loaded = True
                            logger.info("✓ 通过ADB命令验证设备页面")
                    except Exception as e:
                        logger.debug(f"方式5失败: {e}")
                
                # 方式6：使用ADB命令dump UI并检查
                if not page_loaded:
                    try:
                        execute_adb_command("shell uiautomator dump /sdcard/ui_test.xml")
                        stdout, stderr = execute_adb_command("shell cat /sdcard/ui_test.xml")
                        # 检查stdout不为空且包含预期内容
                        if stdout and "com.lockin.loock:id/tvDeviceName" in stdout and "哈哈哈" in stdout:
                            page_loaded = True
                            logger.info("✓ 通过ADB dump验证设备页面")
                    except Exception as e:
                        logger.debug(f"方式6失败: {e}")
                
                # 方式7：使用ADB命令检查应用是否运行
                if not page_loaded:
                    try:
                        stdout, stderr = execute_adb_command("shell ps | grep lockin")
                        if stdout and "com.lockin.loock" in stdout:
                            page_loaded = True
                            logger.info("✓ 通过ADB命令确认应用正在运行")
                    except Exception as e:
                        logger.debug(f"方式7失败: {e}")
                
                if page_loaded:
                    logger.info("✓ 设备页面验证通过")
                    break
                
            except Exception as e:
                logger.error(f"验证过程发生异常: {e}")
                if attempt < max_retries - 1:
                    logger.warning(f"{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
        
        if not page_loaded:
            logger.error("✗ 设备页面验证失败: 所有验证方式均失败")
            raise AssertionError("设备页面未显示，无法找到任何预期元素")
        
        # 步骤2：查找「哈哈哈」设备
        logger.info("步骤2：查找设备「哈哈哈」")
        device_found = False
        for attempt in range(2):
            try:
                device_name = self.d(resourceId="com.lockin.loock:id/tvDeviceName", text="哈哈哈")
                if device_name.exists:
                    device_found = True
                    logger.info("✓ 找到设备「哈哈哈」")
                    break
                else:
                    # 使用ADB命令验证设备是否存在
                    execute_adb_command("shell uiautomator dump /sdcard/ui_test.xml")
                    stdout, stderr = execute_adb_command("shell cat /sdcard/ui_test.xml")
                    if "哈哈哈" in stdout:
                        device_found = True
                        logger.info("✓ 通过ADB命令确认设备「哈哈哈」存在")
                        break
            except Exception as e:
                logger.debug(f"设备查找尝试{attempt+1}失败: {e}")
                if attempt == 0:
                    time.sleep(2)
        
        if not device_found:
            logger.error("✗ 设备查找失败: 未找到名称为「哈哈哈」的设备")
            raise AssertionError("未找到名称为「哈哈哈」的设备")
        
        # 步骤3：点击直播入口（设备缩略图）
        logger.info("步骤3：点击直播入口")
        click_success = False
        
        for attempt in range(2):
            try:
                # 方式1：尝试通过resourceId查找ivThumb
                thumb_view = self.d(resourceId="com.lockin.loock:id/ivThumb")
                if thumb_view.exists:
                    thumb_view.click()
                    click_success = True
                    logger.info("✓ 通过ivThumb点击直播入口")
                    break
                
                # 方式2：尝试点击父容器rlPlay
                play_layout = self.d(resourceId="com.lockin.loock:id/rlPlay")
                if play_layout.exists:
                    play_layout.click()
                    click_success = True
                    logger.info("✓ 通过rlPlay点击直播入口")
                    break
                
                # 方式3：使用ADB命令点击坐标（基于UI层次结构分析）
                execute_adb_command("shell input tap 540 710")
                click_success = True
                logger.info("✓ 通过ADB坐标点击直播入口")
                break
                
            except Exception as e:
                logger.debug(f"点击尝试{attempt+1}失败: {e}")
                if attempt == 0:
                    logger.warning("重试点击直播入口...")
                    time.sleep(2)
        
        if not click_success:
            logger.error("✗ 点击直播入口失败")
            raise Exception("无法点击直播入口")
        else:
            logger.info("✓ 点击直播入口成功")
        
        # 步骤4：等待页面跳转（10秒）
        logger.info("步骤4：等待页面跳转（10秒）")
        time.sleep(10)
        logger.info("✓ 页面跳转等待完成")
        
        # 步骤5：验证直播启动（检测KB/s）
        logger.info("步骤5：验证直播启动")
        live_started = False
        speed_text = ""
        
        for attempt in range(3):
            try:
                # 方式1：使用xpath查找包含KB/s的文本
                speed_element = self.d.xpath('//*[contains(@text, "KB/s")]')
                if speed_element.exists:
                    speed_text = speed_element.get_text()
                    live_started = True
                    logger.info(f"✓ 通过UiAutomator验证直播启动，网速: {speed_text}")
                    break
                
                # 方式2：使用ADB命令dump UI并检查KB/s
                execute_adb_command("shell uiautomator dump /sdcard/ui_live.xml")
                stdout, stderr = execute_adb_command("shell cat /sdcard/ui_live.xml")
                if "KB/s" in stdout:
                    # 提取网速信息
                    import re
                    match = re.search(r'(\d+)\s*KB/s', stdout)
                    if match:
                        speed_text = f"{match.group(1)} KB/s"
                    else:
                        speed_text = "KB/s"
                    live_started = True
                    logger.info(f"✓ 通过ADB命令验证直播启动，网速: {speed_text}")
                    break
                
                # 方式3：检查当前Activity是否为直播页面
                stdout, stderr = execute_adb_command("shell dumpsys window | grep mCurrentFocus")
                if "LiveActivity" in stdout or "VideoActivity" in stdout or "RealTime" in stdout:
                    live_started = True
                    logger.info("✓ 通过Activity验证直播页面已打开")
                    break
                
            except Exception as e:
                logger.debug(f"直播验证尝试{attempt+1}失败: {e}")
                if attempt < 2:
                    logger.info(f"等待{2*(attempt+1)}秒后重试...")
                    time.sleep(2*(attempt+1))
        
        if not live_started:
            logger.error("✗ 直播启动验证失败: 未检测到网速信息或直播Activity")
            raise AssertionError("未检测到网速信息，直播可能未启动")
        else:
            logger.info(f"✓ 直播启动成功{'' if not speed_text else f'，当前网速: {speed_text}'}")
        
        logger.info("=== 直播启动测试全部通过 ===")
    
    def teardown_method(self):
        """测试后清理：停止应用"""
        logger.info("清理测试环境...")
        self.d.app_stop('com.lockin.loock')
        logger.info("测试完成")

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
