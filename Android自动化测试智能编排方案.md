# Android自动化测试智能编排方案

## 方案概述

本方案基于 LLM（大语言模型）+ Prompt（提示词工程）+ Agent（智能体）架构，实现自然语言驱动的Android真机自动化测试。通过调用MCP（Model Context Protocol）工具链，在真机设备上完成实际操作，实时提取元素定位信息，最终自动生成可维护的YAML测试用例和可执行的Python自动化脚本。

---

## 核心架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户自然语言输入                           │
│              "启动鹿客管家App，找到哈哈哈设备，进入直播"           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM 意图理解层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  意图识别   │  │  任务拆解   │  │  参数提取   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ReAct Agent 循环执行层                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐              │   │
│  │  │ Reason  │ →  │  Act    │ →  │ Observe │              │   │
│  │  │ 推理    │    │ 执行    │    │ 观察    │              │   │
│  │  └─────────┘    └─────────┘    └─────────┘              │   │
│  │       ↑                                              │   │
│  │       └──────────────── Loop ────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP 工具服务层                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐  │
│  │ UiAutomator│  │    ADB    │  │   OCR     │  │  设备管理 │  │
│  │   Server  │  │  Commands │  │  Manager  │  │           │  │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Android 真机设备                            │
│              (UIAutomator2 + atx-agent)                        │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      输出产物层                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │   YAML 测试用例     │  │  Python 测试脚本    │              │
│  │  (可维护/可编辑)    │  │  (可直接执行)       │              │
│  └─────────────────────┘  └─────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent 核心能力

### 1. ReAct 循环执行模式

Agent 采用 **ReAct (Reasoning + Acting)** 模式，通过推理-执行-观察的循环来完成任务：

```
┌─────────────────────────────────────────────────────────────────┐
│                     ReAct 执行循环                               │
│                                                                 │
│   ┌─────────┐                                                   │
│   │ THOUGHT │  推理阶段：分析当前状态，决定下一步行动              │
│   └────┬────┘                                                   │
│        ↓                                                         │
│   ┌────┴────┐                                                   │
│   │  ACTION │  执行阶段：调用工具执行操作                        │
│   └────┬────┘                                                   │
│        ↓                                                         │
│   ┌────┴────┐                                                   │
│   │ OBSERVE │  观察阶段：获取执行结果，分析是否达成目标            │
│   └────┬────┘                                                   │
│        │                                                         │
│        ↓                                                         │
│   ┌────┴────┐                                                   │
│   │ LOOP?   │  判断是否继续循环或结束                            │
│   └─────────┘                                                   │
└─────────────────────────────────────────────────────────────────┘
```

#### Prompt 模板（ReAct 推理）

```
你是一个Android自动化测试Agent。当前任务：{task_description}

当前状态：
- 已完成步骤：{completed_steps}
- 当前步骤：{current_step}
- 页面状态：{page_info}

请推理：
1. 当前页面是否包含目标元素？
2. 如果不包含，可能的原因是什么？
3. 下一步应该采取什么行动？

选项：
A. 继续等待元素出现（元素可能正在加载）
B. 尝试其他定位方式（降级策略）
C. 滑动屏幕后再查找（元素可能在屏幕下方）
D. 截图分析当前页面实际内容
E. 中止任务并报告失败

请选择并说明理由。
```

### 2. Loop 循环机制

Agent 支持多层循环来处理不同层级的问题：

#### 2.1 元素查找循环（Element Search Loop）

```
元素查找循环 (max_attempts=5)
│
├── Attempt 1: 使用首选定位方式 (resourceId)
│   ├── 成功 → 返回元素信息
│   └── 失败 → 记录失败原因
│
├── Attempt 2: 降级到备用定位方式 (text)
│   ├── 成功 → 返回元素信息 + 更新定位策略
│   └── 失败 → 记录失败原因
│
├── Attempt 3: 尝试滚动查找 (scroll)
│   ├── 成功 → 返回元素信息
│   └── 失败 → 记录失败原因
│
├── Attempt 4: 使用 OCR 定位
│   ├── 成功 → 返回坐标信息
│   └── 失败 → 记录失败原因
│
├── Attempt 5: 使用坐标点击（兜底方案）
│   ├── 成功 → 返回成功
│   └── 失败 → 报告失败
│
└── 全部失败 → 进入异常处理流程
```

#### 2.2 步骤执行循环（Step Execution Loop）

```
步骤执行循环 (max_retries=3)
│
├── 步骤执行
│   ├── 成功 → 验证结果 → 进入下一步
│   └── 失败 → 重试当前步骤
│       │
│       ├── Retry 1: 等待 + 重试
│       ├── Retry 2: 刷新页面 + 重试
│       └── Retry 3: 重启服务 + 重试
│
└── 全部重试失败 → 决策点
    │
    ├── 降级执行：跳过当前步骤，尝试后续步骤
    ├── 替代方案：使用ADB命令完成相同功能
    └── 报告失败：记录失败原因，生成问题报告
```

#### 2.3 任务级别循环（Task Level Loop）

```
整个测试任务循环
│
├── 任务启动
├── 循环执行每个测试步骤
│   └── 每个步骤内部包含上述两层循环
│
├── 遇到不可恢复错误
│   ├── 检查是否有替代路径
│   ├── 记录错误上下文
│   └── 决定继续或中止
│
└── 任务完成或中止
    └── 生成测试报告
```

### 3. 元素找不到时的处理策略

当元素定位失败时，Agent 按照以下策略逐步处理：

#### 策略 1：等待重试（Wait & Retry）

```
检测到元素不存在
    │
    ▼
等待 2 秒
    │
    ▼
重新获取页面信息
    │
    ▼
再次尝试定位
    │
    ├── 成功 → 继续执行
    └── 失败 → 进入策略 2
```

#### 策略 2：多维度重新定位（Multi-Dimension Relocation）

```
分析失败原因：
│
├── 原因A: 元素尚未加载
│   └── 行动：等待 + 刷新页面 + 重试
│
├── 原因B: 元素在屏幕外（需要滚动）
│   └── 行动：scroll_to_element 或 swipe
│
├── 原因C: 元素被遮挡
│   └── 行动：关闭弹窗/广告 + 重试
│
├── 原因D: 定位表达式错误
│   └── 行动：重新解析UI结构，更新定位表达式
│
└── 原因E: 页面结构变化
    └── 行动：dump UI，重新分析页面
```

#### 策略 3：降级执行（Degradation Execution）

```
当所有定位方式都失败时：
│
├── 检查是否有兜底坐标
│   └── 有 → 使用坐标点击
│
├── 检查是否可用ADB命令替代
│   └── 可以 → 使用 `adb shell input tap x y`
│
├── 检查是否可跳过当前步骤
│   └── 可以 → 记录跳过原因，继续下一步
│
└── 全部不可行 → 报告失败
```

#### 策略 4：智能分析与学习（Smart Analysis）

```
Agent 具备自我诊断能力：
│
├── 失败模式识别
│   ├── "按钮不存在" → 可能页面未加载完成
│   ├── "坐标超出范围" → 可能屏幕尺寸不匹配
│   └── "服务无响应" → 可能UIAutomator服务异常
│
├── 上下文推理
│   ├── 根据上一步操作推断当前页面状态
│   ├── 根据历史执行记录调整等待时间
│   └── 根据设备状态调整操作策略
│
└── 自适应学习
    ├── 记录成功的定位方式，优先使用
    └── 记录失败的定位方式，减少重试
```

### 4. Prompt 推理示例

#### 场景：查找"哈哈哈"设备失败

```
【Thought】
用户要求找到「哈哈哈」设备，但当前页面未找到该元素。
分析可能原因：
1. 设备列表还未加载完成
2. 「哈哈哈」设备不在当前屏幕可见区域
3. 设备名称与预期不符

【Action】
先尝试滑动屏幕，查看更多设备

【Observe】
滑动后，页面显示了更多设备，但仍无「哈哈哈」

【Thought】
滑动后仍未找到，可能设备名称有误或需要进入子页面。
让我检查页面中是否有包含"哈哈"字样的元素。

【Action】
使用 OCR 扫描当前页面所有文字

【Observe】
发现设备列表中有一个设备名称为"哈哈哈😂"

【Thought】
找到原因了！设备名称包含emoji，需要使用模糊匹配而非精确匹配。

【Action】
使用 textContains="哈哈哈" 定位设备

【Success】
成功定位到设备
```

### 5. 决策点与分支处理

```
                        ┌─────────────────────┐
                        │     决策节点        │
                        │  Decision Point     │
                        └──────────┬──────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
    ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
    │   继续执行   │        │    降级     │        │   报告失败  │
    │  Continue   │        │ Degradation │        │   Abort     │
    └─────────────┘        └─────────────┘        └─────────────┘
           │                       │                       │
           ▼                       ▼                       ▼
    执行下一步骤           使用备选方案              记录错误信息
    - 使用备用元素          - ADB命令               - 保存截图
    - 增加等待时间          - 坐标点击               - 生成报告
    - 滑动屏幕             - 跳过步骤               - 通知用户
```

### 6. 最大重试与超时机制

| 层级 | 最大次数 | 超时时间 | 说明 |
|------|----------|----------|------|
| 元素定位 | 5次 | 30秒 | 尝试5种不同定位方式 |
| 步骤执行 | 3次 | 60秒 | 每步最多重试3次 |
| 服务重启 | 2次 | 30秒 | 最多重启服务2次 |
| 整任务执行 | 1次 | 300秒 | 整个测试任务超时5分钟 |

---

## 组件职责

### 1. LLM 意图理解层

| 组件 | 职责 | 输入示例 |
|------|------|----------|
| 意图识别 | 判断用户操作类型 | "启动App"、"点击元素"、"验证页面" |
| 任务拆解 | 将复杂任务分解为原子步骤 | 直播启动 → 启动App → 验证页面 → 查找设备 → 点击入口 → 验证直播 |
| 参数提取 | 提取应用包名、元素定位符、等待时间等 | com.lockin.loock、哈哈哈、10秒 |

### 2. ReAct Agent 执行编排层

| 功能 | 说明 |
|------|------|
| 推理引擎 | 分析当前状态，决定下一步行动（Reason） |
| 执行引擎 | 调用MCP工具执行操作（Act） |
| 观察引擎 | 获取执行结果，分析是否达成目标（Observe） |
| 循环控制 | 管理Loop循环，判断是否继续或结束 |
| 决策控制 | 决定是否降级、跳过或报告失败 |
| 异常处理 | 服务异常恢复、元素找不到处理 |

### 3. MCP 工具服务层

#### 3.1 UiAutomator2 Server
提供UI自动化核心能力：
- `click_element` - 点击界面元素
- `input_text` - 输入文本
- `swipe_screen` - 滑动屏幕
- `wait_and_click` - 等待元素出现并点击
- `scroll_to_element` - 滚动到指定元素

#### 3.2 ADB Commands
提供设备底层控制能力：
- `execute_adb_command` - 执行任意ADB shell命令
- `start_app` / `stop_app` - 应用启停
- `get_current_app` - 获取当前应用信息
- `list_packages` - 列出已安装应用

#### 3.3 OCR Manager
提供屏幕文字识别能力：
- `ocr_screen` - 识别屏幕所有文字
- `find_text_position` - 查找文字位置
- `click_text` - 点击指定文字

#### 3.4 设备管理
提供设备状态监控：
- `get_device_info` - 获取设备信息
- `get_battery_info` - 获取电池信息
- `get_network_info` - 获取网络信息

---

## 元素定位策略

为保证测试用例的稳定性和可维护性，采用多层级定位策略：

### 定位优先级（从高到低）

| 优先级 | 定位方式 | 示例 | 适用场景 |
|--------|----------|------|----------|
| 1 | resourceId | `com.example.app:id/username` | 唯一ID标识的元素 |
| 2 | text | `text="登录"` | 文本固定的按钮/标签 |
| 3 | textContains | `textContains="KB/s"` | 文本包含特定字符串的元素 |
| 4 | description | `description="返回"` | 无障碍描述元素 |
| 5 | xpath | `//android.widget.Button[@text='确定']` | 结构稳定的元素 |
| 6 | 坐标 | `click(540, 710)` | 布局不确定的动态元素 |

### 定位降级策略

```
优先使用resourceId定位
    │
    ├─ 失败 → 尝试text定位
    │         │
    │         ├─ 失败 → 尝试textContains定位
    │         │         │
    │         │         ├─ 失败 → 尝试description定位
    │         │         │         │
    │         │         │         └─ 失败 → 尝试xpath定位
    │         │         │                   │
    │         │         │                   └─ 失败 → 使用坐标点击
    │         │         │
    │         │         └─ 成功 → 记录定位方式
    │         │
    │         └─ 成功 → 记录定位方式
    │
    └─ 成功 → 记录定位方式
```

---

## 异常处理机制

### 服务异常恢复

```
检测到 UiAutomator 服务异常 (NullPointerException)
           │
           ▼
┌──────────────────────────────┐
│     重试机制 (最多3次)        │
│  ┌────────────────────────┐  │
│  │ 1. 等待2秒             │  │
│  │ 2. 停止并重启服务      │  │
│  │ 3. 重新连接设备        │  │
│  │ 4. 重试当前操作        │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
           │
           ▼
      重试成功 → 继续执行
           │
           ▼
      重试失败 → 降级到ADB命令
```

### 验证码处理

| 场景 | 处理策略 |
|------|----------|
| 图形验证码 | 调用OCR识别验证码内容，自动填写 |
| 短信验证码 | 监听短信接收，自动提取验证码 |
| 滑块验证 | 计算滑块距离，模拟滑动轨迹 |

---

## YAML 测试用例格式

```yaml
name: 鹿客管家直播启动测试
description: 测试从设备列表进入直播的完整流程
package_name: com.lockin.loock
version: 1.0
author: AutoTest

steps:
  - action: 启动应用
    element: "com.lockin.loock"
    activity: ".MainActivity"
    wait_time: 8
    description: 启动鹿客管家App，等待应用完全启动
    expected: 应用成功启动，显示设备列表页面

  - action: 验证设备页面
    element: "com.lockin.loock:id/tvTitle"
    text: "设备"
    verify_methods:
      - type: resourceId
        value: "com.lockin.loock:id/tvTitle"
        text: "设备"
      - type: resourceId
        value: "com.lockin.loock:id/deviceList"
      - type: resourceId
        value: "com.lockin.loock:id/tvDeviceName"
        text: "哈哈哈"
      - type: resourceId
        value: "com.lockin.loock:id/ivThumb"
    retry:
      max_attempts: 5
      wait_between: 2
      degradation: adb
    description: 多重验证策略，任一方式通过即可
    expected: 设备页面成功加载

  - action: 查找设备
    element: "com.lockin.loock:id/tvDeviceName"
    text: "哈哈哈"
    fuzzy_match: true
    description: 在设备列表中找到「哈哈哈」设备
    expected: 设备名称匹配

  - action: 点击直播入口
    element: "com.lockin.loock:id/ivThumb"
    click_methods:
      - type: resourceId
        value: "com.lockin.loock:id/ivThumb"
      - type: resourceId
        value: "com.lockin.loock:id/rlPlay"
      - type: adb
        command: "input tap 540 710"
    fallback:
      - type: swipe
        direction: up
        duration: 500
      - type: wait
        seconds: 3
    description: 点击设备缩略图进入直播页面
    expected: 跳转到实时视频页面

  - action: 等待页面跳转
    value: 10
    unit: seconds
    description: 等待直播页面加载完成
    expected: 页面成功跳转

  - action: 验证直播启动
    element: "textContains=KB/s"
    verify_methods:
      - type: xpath
        value: '//*[contains(@text, "KB/s")]'
      - type: textContains
        value: "KB/s"
      - type: adb_dump
        pattern: "KB/s"
      - type: activity
        names:
          - "LiveActivity"
          - "VideoActivity"
          - "RealTimeActivity"
    timeout: 30
    description: 检测网速信息或直播Activity，确认直播已启动
    expected: 显示网速信息或进入直播Activity
```

---

## Python 测试脚本格式

```python
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
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ReActAgent:
    """ReAct 模式的 Agent 实现"""

    def __init__(self, device):
        self.d = device
        self.max_loop = 5
        self.max_retries = 3

    def think(self, state):
        """Reason: 分析当前状态，决定下一步行动"""
        logger.info(f"推理阶段 - 当前状态: {state}")
        return state

    def act(self, action):
        """Act: 执行操作"""
        action_type = action.get('type')
        logger.info(f"执行阶段 - 操作类型: {action_type}")

        if action_type == 'find_element':
            return self._find_element_with_retry(action)
        elif action_type == 'click':
            return self._click_with_retry(action)
        elif action_type == 'wait':
            time.sleep(action.get('seconds', 2))
            return True
        elif action_type == 'scroll':
            direction = action.get('direction', 'up')
            self.d.swipe_screen(direction)
            return True

    def observe(self, result):
        """Observe: 观察结果"""
        logger.info(f"观察阶段 - 结果: {result}")
        return result.get('success', False)

    def run_loop(self, task):
        """执行 ReAct 循环"""
        state = {'task': task, 'step': 0, 'attempts': 0}

        for loop in range(self.max_loop):
            state = self.think(state)
            if state.get('done'):
                break

            action = state.get('next_action')
            result = self.act(action)

            if not self.observe(result):
                state['attempts'] += 1
                if state['attempts'] >= self.max_retries:
                    state = self.handle_failure(state)

        return state

    def _find_element_with_retry(self, element_info):
        """带重试的元素查找"""
        strategies = [
            {'type': 'resourceId', 'value': element_info.get('resourceId')},
            {'type': 'text', 'value': element_info.get('text')},
            {'type': 'textContains', 'value': element_info.get('textContains')},
            {'type': 'xpath', 'value': element_info.get('xpath')},
        ]

        for strategy in strategies:
            try:
                obj = self.d(**{strategy['type']: strategy['value']})
                if obj.exists:
                    return {'success': True, 'strategy': strategy}
            except Exception as e:
                logger.debug(f"策略 {strategy['type']} 失败: {e}")
                continue

        return {'success': False}

    def _click_with_retry(self, element_info):
        """带重试的元素点击"""
        for attempt in range(self.max_retries):
            result = self._find_element_with_retry(element_info)
            if result.get('success'):
                obj = self.d(**{result['strategy']['type']: result['strategy']['value']})
                obj.click()
                return {'success': True}

            logger.warning(f"点击尝试 {attempt + 1} 失败，等待后重试...")
            time.sleep(2)

        return {'success': False}

    def handle_failure(self, state):
        """处理失败情况 - 决策点"""
        logger.error("所有重试均失败，进入决策处理")

        # 策略1: 降级使用ADB命令
        if state.get('fallback_adb'):
            logger.info("尝试使用ADB命令作为降级方案")
            # 执行ADB降级逻辑

        # 策略2: 跳过当前步骤
        if state.get('can_skip'):
            logger.info("跳过当前步骤，继续执行后续步骤")
            state['step'] += 1
            state['attempts'] = 0
            return state

        # 策略3: 报告失败
        state['done'] = True
        state['error'] = "无法完成当前步骤"
        return state


def execute_adb_command(command):
    """执行ADB命令并返回输出"""
    try:
        result = subprocess.run(
            ['adb'] + command.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        stdout = result.stdout.strip() if result and result.stdout else ""
        stderr = result.stderr.strip() if result and result.stderr else ""
        return stdout, stderr
    except subprocess.TimeoutExpired:
        return "", "命令超时"
    except FileNotFoundError:
        return "", "ADB未找到"
    except Exception as e:
        return "", str(e)


def restart_uiautomator_service():
    """重启UIAutomator服务"""
    logger.info("尝试重启UIAutomator服务...")
    execute_adb_command("shell am force-stop com.github.uiautomator")
    execute_adb_command("shell pm clear com.github.uiautomator")
    time.sleep(2)
    execute_adb_command("shell am start -n com.github.uiautomator/.MainActivity")
    time.sleep(3)
    logger.info("UIAutomator服务重启完成")


class TestLiveStream:
    """鹿客管家直播启动测试类"""

    def setup_method(self):
        """测试前准备：初始化设备连接并启动应用"""
        logger.info("开始初始化测试环境...")
        self.d = u2.connect()
        self.d.implicitly_wait(30)

        logger.info("启动鹿客管家应用...")
        self.d.app_start('com.lockin.loock', '.MainActivity')
        time.sleep(8)

    def test_live_stream_startup(self):
        """测试直播启动完整流程"""
        logger.info("=== 开始执行直播启动测试 ===")

        agent = ReActAgent(self.d)

        task = {
            'steps': [
                {'action': 'verify_page', 'expected': '设备页面'},
                {'action': 'find_device', 'name': '哈哈哈'},
                {'action': 'click_live', 'element': 'ivThumb'},
                {'action': 'wait', 'seconds': 10},
                {'action': 'verify_live', 'indicator': 'KB/s'},
            ]
        }

        result = agent.run_loop(task)

        if result.get('error'):
            pytest.fail(result['error'])

        logger.info("=== 直播启动测试全部通过 ===")

    def teardown_method(self):
        """测试后清理"""
        logger.info("清理测试环境...")
        self.d.app_stop('com.lockin.loock')
        logger.info("测试完成")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 工作流程

### 完整执行流程

```
1. 接收自然语言需求
   │
   ├─ "启动鹿客管家App，找到哈哈哈设备，点击进入直播，等待10秒，验证直播启动"
   │
   ▼
2. LLM 解析需求
   │
   ├─ 意图：执行多步骤自动化测试
   ├─ 应用：com.lockin.loock
   ├─ 步骤：
   │   1. 启动应用
   │   2. 验证设备页面
   │   3. 查找设备「哈哈哈」
   │   4. 点击直播入口
   │   5. 等待页面跳转
   │   6. 验证直播启动
   └─ 验证条件：textContains="KB/s"
   │
   ▼
3. ReAct Agent 循环执行
   │
   ├─ Loop 1: 验证设备页面
   │   ├─ Think: 分析页面结构
   │   ├─ Act: 尝试多种定位方式
   │   ├─ Observe: 检查是否成功
   │   └─ Loop: 最多5次重试
   │
   ├─ Loop 2: 查找设备「哈哈哈」
   │   ├─ Think: 设备名称可能包含emoji
   │   ├─ Act: 使用模糊匹配
   │   ├─ Observe: 确认设备存在
   │   └─ Loop: 精确→模糊→滚动→OCR
   │
   ├─ Loop 3: 点击直播入口
   │   ├─ Think: 点击设备缩略图
   │   ├─ Act: resourceId定位 + 点击
   │   ├─ Observe: 检查点击效果
   │   └─ Loop: 失败则降级到ADB
   │
   └─ Loop 4: 验证直播启动
       ├─ Think: 检查KB/s网速显示
       ├─ Act: 多种验证方式
       ├─ Observe: 确认直播成功
       └─ Loop: 超时则报告失败
   │
   ▼
4. 生成测试产物
   │
   ├─ YAML 测试用例 (test_live_stream.yaml)
   │   └─ 包含完整步骤、定位策略、重试配置
   │
   └─ Python 测试脚本 (test_live_stream.py)
       └─ 包含ReAct Agent实现
   │
   ▼
5. 输出 HTML 测试报告
   │
   └─ test_report.html
       └─ 包含测试步骤、循环次数、问题分析
```

---

## 质量保障措施

### 测试稳定性

| 措施 | 说明 |
|------|------|
| ReAct循环 | 每个步骤支持最多5次推理-执行-观察循环 |
| 等待时间 | 应用启动等待8秒，页面跳转等待10秒 |
| 隐式等待 | 全局设置30秒隐式等待时间 |
| 服务自愈 | 失败时自动重启UIAutomator服务 |

### 元素定位可靠性

| 策略 | 说明 |
|------|------|
| 多重验证 | 单元素多方式定位，任一成功即可 |
| 降级策略 | UiAutomator失败时降级到ADB命令 |
| 模糊匹配 | 支持textContains模糊定位 |
| OCR兜底 | 无法定位时使用OCR识别文字位置 |

### 问题可追溯性

| 机制 | 说明 |
|------|------|
| 详细日志 | 每步操作都有详细日志记录，包含推理过程 |
| UI结构打印 | 失败时打印当前页面UI结构 |
| 循环记录 | 记录每个Loop的尝试次数和失败原因 |
| 截图保存 | 可配置保存失败时的屏幕截图 |

---

## 适用场景

| 场景 | 说明 |
|------|------|
| 功能测试 | 验证App核心功能的正确性 |
| 回归测试 | 每次发布前执行完整测试套件 |
| UI验收测试 | 验证UI交互是否符合预期 |
| 冒烟测试 | 快速验证App基本功能可用性 |

---

## 依赖要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | ≥3.10 | 测试脚本运行环境 |
| uiautomator2 | 最新版本 | Android UI自动化框架 |
| pytest | 最新版本 | 测试框架 |
| ADB | 最新版本 | Android调试桥 |
| atx-agent | 最新版本 | Android设备端服务 |

---

## 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install uiautomator2 pytest

# 安装atx-agent到设备
python -m uiautomator2 install-atx

# 启动MCP服务器
python src/server.py
```

### 2. 执行测试

```bash
# 直接运行Python脚本
python tests/test_live_stream.py

# 或使用pytest运行
pytest tests/test_live_stream.py -v
```

### 3. 查看报告

打开生成的 `test_report.html` 文件查看测试结果。

---

## 未来优化方向

| 方向 | 说明 |
|------|------|
| 智能等待 | 根据元素状态动态调整等待时间 |
| 视觉识别 | 结合图像识别处理复杂UI场景 |
| 并行执行 | 支持多设备同时执行测试 |
| CI/CD集成 | 无缝集成到Jenkins/GitHub Actions |
