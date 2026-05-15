"""
Android自动化测试：鹿客管家APP事件页面测试
依赖安装：pip install uiautomator2 pytest
运行方式：python test_lockin_event.py
要求：确保Android设备已连接，且已安装atx-agent
"""
import uiautomator2 as u2
import pytest
import time

class TestLockinEvent:
    def setup_method(self):
        """初始化测试环境"""
        # 初始化UiAutomator2连接
        self.d = u2.connect()
        self.d.implicitly_wait(15)
        self.d.settings['wait_timeout'] = 15
        # 启动鹿客管家应用
        self.d.app_start('com.lockin.loock')
        time.sleep(3)
    
    def test_event_tab_navigation(self):
        """测试事件tab导航和美好时光详情页"""
        # 步骤1：等待应用加载完成
        time.sleep(2)
        
        # 步骤2：点击底部事件tab（使用文本定位）
        event_tab = self.d(text="事件")
        if event_tab.exists:
            event_tab.click()
            print("✓ 点击事件tab成功")
        else:
            # 尝试其他定位方式
            print("尝试通过className定位底部导航栏")
            bottom_nav = self.d(className="android.widget.TabWidget")
            if bottom_nav.exists:
                # 通常事件tab在第二个位置（索引1）
                bottom_nav.child(index=1).click()
                print("✓ 通过TabWidget定位并点击成功")
            else:
                raise Exception("未找到事件tab")
        time.sleep(3)
        
        # 步骤3：点击美好时光
        beautiful_time = self.d(text="美好时光")
        assert beautiful_time.exists, "美好时光入口未找到"
        beautiful_time.click()
        print("✓ 点击美好时光成功")
        time.sleep(3)
        
        # 步骤4：验证进入美好时光详情页
        assert self.d(text="美好时光").exists, "未成功进入美好时光详情页"
        print("✓ 成功进入美好时光详情页")
    
    def teardown_method(self):
        """清理测试环境"""
        # 停止应用
        self.d.app_stop('com.lockin.loock')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])