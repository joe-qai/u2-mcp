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

本方案实现的 Agent 具备完整的 **思考(Think) → 感知(Perceive) → 决策(Decide) → 执行(Act)** 循环，并配备 **记忆(Memory)** 系统实现上下文保持。

### 1. 完整 ReAct + Memory 架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Agent 核心架构                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         📝 Memory System                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │   │
│  │  │ Session      │  │ Working      │  │ Learned      │               │   │
│  │  │ Memory       │  │ Memory       │  │ Knowledge    │               │   │
│  │  │ (会话记忆)    │  │ (工作记忆)    │  │ (知识库)     │               │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                      │
│                                     ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      🔄 ReAct Loop                                    │   │
│  │                                                                       │   │
│  │   ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐    │   │
│  │   │  THINK  │ ───▶ │ DECIDE  │ ───▶ │   ACT   │ ───▶ │PERCEIVE │    │   │
│  │   │ 推理    │      │ 决策    │      │ 执行    │      │ 感知    │    │   │
│  │   └─────────┘      └─────────┘      └─────────┘      └─────────┘    │   │
│  │        │                                               │            │   │
│  │        │              Loop Back                        │            │   │
│  │        └───────────────────────────────────────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. 各模块详细职责

| 模块 | 职责 | 输入 | 输出 |
|------|------|------|------|
| **Think (推理)** | 分析当前状态，理解任务目标，识别问题 | Memory上下文 + 当前状态 | 推理结果 + 下一步计划 |
| **Decide (决策)** | 根据推理结果，决定行动方案 | 推理结果 | 具体行动指令 |
| **Act (执行)** | 调用MCP工具执行操作 | 行动指令 | 执行结果 |
| **Perceive (感知)** | 感知执行结果，判断是否达成目标 | 执行结果 | 状态更新 + 观察报告 |
| **Memory (记忆)** | 存储会话上下文、工作状态、知识库 | 所有模块读写 | 持久化上下文 |

---

### 3. Memory 记忆系统实现

```python
class MemorySystem:
    """记忆系统 - Agent 的知识管理核心"""

    def __init__(self):
        # 会话记忆：存储当前测试会话的完整上下文
        self.session_memory = {
            'task_id': None,
            'user_request': None,
            'completed_steps': [],      # 已完成的步骤列表
            'failed_attempts': [],     # 失败尝试记录
            'screenshots': [],          # 截图记录
            'ui_dumps': [],            # UI层次结构记录
        }

        # 工作记忆：当前任务的即时状态
        self.working_memory = {
            'current_step': 0,
            'current_page': None,
            'page_source': None,
            'visible_elements': [],     # 当前可见元素
            'last_action': None,
            'last_result': None,
        }

        # 知识库：学习到的经验知识
        self.learned_knowledge = {
            'element_locators': {},      # 元素定位表达式缓存
            'app_structure': {},        # 应用页面结构
            'successful_strategies': [], # 成功的策略模式
            'failure_patterns': [],     # 失败模式记录
        }

    def remember(self, key, value):
        """存入记忆"""
        self.working_memory[key] = value
        logger.debug(f"记住: {key} = {value}")

    def recall(self, key):
        """提取记忆"""
        return self.working_memory.get(key)

    def learn(self, pattern, strategy, success):
        """学习经验"""
        if success:
            self.learned_knowledge['successful_strategies'].append({
                'pattern': pattern,
                'strategy': strategy,
                'timestamp': time.time()
            })
        else:
            self.learned_knowledge['failure_patterns'].append({
                'pattern': pattern,
                'timestamp': time.time()
            })

    def get_context(self):
        """获取完整上下文用于LLM推理"""
        return {
            'session': self.session_memory,
            'working': self.working_memory,
            'knowledge': self.learned_knowledge
        }
```

---

### 4. Think 推理引擎实现

```python
class ReasoningEngine:
    """推理引擎 - Think 模块"""

    def __init__(self, memory: MemorySystem, llm_client):
        self.memory = memory
        self.llm = llm_client

    def think(self, task_description: str) -> Dict:
        """
        推理阶段：分析当前状态，决定下一步行动

        推理过程：
        1. 理解任务目标
        2. 分析当前页面状态
        3. 检查历史记忆
        4. 制定下一步计划
        """
        context = self.memory.get_context()

        prompt = f"""
你是Android自动化测试Agent。当前任务：{task_description}

当前状态：
- 已完成步骤：{context['session']['completed_steps']}
- 当前步骤：{context['working']['current_step']}
- 当前页面：{context['working']['current_page']}
- 可见元素数：{len(context['working']['visible_elements'])}

历史记忆：
- 成功策略：{context['knowledge']['successful_strategies'][-3:]}
- 失败模式：{context['knowledge']['failure_patterns'][-3:]}

请进行推理分析：
1. 当前页面是否包含目标元素？
2. 如果不包含，可能的原因是什么？（5W1H分析）
3. 历史经验对当前情况有什么启示？
4. 下一步应该采取什么行动？

请输出：
- 分析结果（reasoning）
- 下一步行动（next_action）
- 行动参数（action_params）
"""

        response = self.llm.generate(prompt)

        return {
            'reasoning': response.get('reasoning'),
            'next_action': response.get('next_action'),
            'action_params': response.get('action_params'),
            'confidence': response.get('confidence', 0.8)
        }
```

---

### 5. Decide 决策引擎实现

```python
class DecisionEngine:
    """决策引擎 - Decide 模块"""

    def __init__(self, memory: MemorySystem):
        self.memory = memory
        self.max_retries = 3
        self.max_loops = 5

    def decide(self, reasoning_result: Dict) -> Dict:
        """
        决策阶段：根据推理结果决定行动方案

        决策树：
        ├── 置信度 > 0.8 → 直接执行
        ├── 置信度 0.5-0.8 → 执行 + 准备备选方案
        └── 置信度 < 0.5 → 多策略并行尝试
        """
        confidence = reasoning_result.get('confidence', 0.5)
        next_action = reasoning_result.get('next_action')

        decision = {
            'action': next_action,
            'params': reasoning_result.get('action_params', {}),
            'fallback': None,
            'mode': None
        }

        # 根据置信度决定执行模式
        if confidence > 0.8:
            decision['mode'] = 'direct'  # 直接执行
            decision['fallback'] = self._create_fallback(next_action)

        elif confidence > 0.5:
            decision['mode'] = 'cautious'  # 谨慎执行
            decision['fallback'] = self._create_fallback(next_action)
            decision['backup_strategies'] = self._get_backup_strategies(next_action)

        else:
            decision['mode'] = 'explorative'  # 探索执行
            decision['parallel_strategies'] = self._get_parallel_strategies(next_action)

        # 更新记忆
        self.memory.remember('current_decision', decision)

        return decision

    def _create_fallback(self, action):
        """创建备选方案"""
        fallbacks = {
            'find_element': [
                {'type': 'text', 'value': None},
                {'type': 'textContains', 'value': None},
                {'type': 'xpath', 'value': None},
                {'type': 'ocr', 'value': None},
                {'type': 'coordinates', 'value': None}
            ],
            'click': [
                {'type': 'adb_shell', 'command': 'input tap {x} {y}'},
                {'type': ' swipe', 'direction': 'up'},
            ]
        }
        return fallbacks.get(action, [])

    def _get_backup_strategies(self, action):
        """获取备份策略"""
        return []

    def _get_parallel_strategies(self, action):
        """获取并行探索策略"""
        return []
```

---

### 6. Act 执行引擎实现

```python
class ActEngine:
    """执行引擎 - Act 模块"""

    def __init__(self, memory: MemorySystem, mcp_tools: MCPClient):
        self.memory = memory
        self.mcp = mcp_tools
        self.d = mcp_tools.device

    def execute(self, decision: Dict) -> Dict:
        """
        执行阶段：调用MCP工具执行操作

        执行流程：
        1. 解析决策指令
        2. 调用MCP工具
        3. 记录执行日志
        4. 返回执行结果
        """
        action = decision.get('action')
        params = decision.get('params', {})

        logger.info(f"执行阶段 - 操作: {action}, 参数: {params}")

        try:
            if action == 'find_element':
                result = self._find_element(params)

            elif action == 'click_element':
                result = self._click_element(params)

            elif action == 'input_text':
                result = self._input_text(params)

            elif action == 'swipe':
                result = self._swipe(params)

            elif action == 'wait':
                result = self._wait(params)

            elif action == 'dump_ui':
                result = self._dump_ui(params)

            elif action == 'ocr_screen':
                result = self._ocr_screen(params)

            elif action == 'execute_adb':
                result = self._execute_adb(params)

            else:
                result = {'success': False, 'error': f'未知操作: {action}'}

            # 记录执行结果到记忆
            self.memory.remember('last_action', action)
            self.memory.remember('last_result', result)

            return result

        except Exception as e:
            logger.error(f"执行异常: {e}")
            return {'success': False, 'error': str(e)}

    def _find_element(self, params):
        """查找元素"""
        strategies = params.get('strategies', [
            {'type': 'resourceId', 'value': params.get('resourceId')},
            {'type': 'text', 'value': params.get('text')},
            {'type': 'textContains', 'value': params.get('textContains')},
            {'type': 'description', 'value': params.get('description')},
            {'type': 'xpath', 'value': params.get('xpath')},
        ])

        for strategy in strategies:
            try:
                if strategy['type'] == 'resourceId':
                    obj = self.d(resourceId=strategy['value'])
                elif strategy['type'] == 'text':
                    obj = self.d(text=strategy['value'])
                elif strategy['type'] == 'textContains':
                    obj = self.d(textContains=strategy['value'])
                elif strategy['type'] == 'description':
                    obj = self.d(description=strategy['value'])
                elif strategy['type'] == 'xpath':
                    obj = self.d.xpath(strategy['value'])
                else:
                    continue

                if obj.exists:
                    info = obj.info
                    logger.info(f"元素找到: {strategy} -> {info.get('bounds')}")
                    return {
                        'success': True,
                        'strategy': strategy,
                        'bounds': info.get('bounds'),
                        'text': info.get('text'),
                        'enabled': info.get('enabled')
                    }
            except Exception as e:
                logger.debug(f"定位失败 {strategy['type']}: {e}")
                continue

        return {'success': False, 'error': '所有定位方式均失败'}

    def _click_element(self, params):
        """点击元素"""
        element_result = self._find_element(params)
        if element_result.get('success'):
            obj = self._get_element_object(element_result['strategy'])
            obj.click()
            return {'success': True, 'action': 'click', 'element': element_result}
        return {'success': False, 'error': '无法点击元素'}

    def _swipe(self, params):
        """滑动屏幕"""
        direction = params.get('direction', 'up')
        scale = params.get('scale', 0.9)
        self.d.swipe_screen(direction=direction, scale=scale)
        return {'success': True, 'action': 'swipe', 'direction': direction}

    def _wait(self, params):
        """等待"""
        seconds = params.get('seconds', 2)
        time.sleep(seconds)
        return {'success': True, 'action': 'wait', 'duration': seconds}

    def _dump_ui(self, params):
        """获取UI层次结构"""
        xml = self.d.dump_hierarchy()
        self.memory.remember('page_source', xml)
        return {'success': True, 'ui_xml': xml}

    def _ocr_screen(self, params):
        """OCR屏幕识别"""
        text = self.mcp.ocr_screen()
        self.memory.remember('screen_text', text)
        return {'success': True, 'text': text}

    def _execute_adb(self, params):
        """执行ADB命令"""
        command = params.get('command')
        stdout, stderr = self.mcp.execute_adb_command(command)
        return {'success': not stderr, 'stdout': stdout, 'stderr': stderr}
```

---

### 7. Perceive 感知引擎实现

```python
class PerceptionEngine:
    """感知引擎 - Perceive 模块"""

    def __init__(self, memory: MemorySystem):
        self.memory = memory

    def perceive(self, act_result: Dict) -> Dict:
        """
        感知阶段：观察执行结果，判断是否达成目标

        感知内容：
        1. 操作是否成功
        2. 页面状态是否变化
        3. 是否出现异常
        4. 是否达成目标
        """
        success = act_result.get('success', False)
        action = self.memory.recall('last_action')
        expected = self._get_expected_outcome(action)

        perception = {
            'success': success,
            'action': action,
            'expected': expected,
            'actual': act_result,
            'goal_achieved': False,
            'anomalies': [],
            'observations': []
        }

        if success:
            # 分析操作结果是否符合预期
            if action == 'find_element':
                perception['goal_achieved'] = act_result.get('success', False)
                perception['observations'].append(f"元素{'找到' if act_result.get('success') else '未找到'}")

            elif action == 'click_element':
                # 点击后通常页面会跳转，检查页面变化
                page_changed = self._check_page_change()
                perception['goal_achieved'] = page_changed
                perception['observations'].append(f"页面{'已跳转' if page_changed else '未变化'}")

            elif action == 'swipe':
                perception['observations'].append("滑动操作执行")
                perception['goal_achieved'] = True

        else:
            # 分析失败原因
            error = act_result.get('error', '未知错误')
            perception['anomalies'].append(error)

            # 根据错误类型判断是否可恢复
            if '超时' in error or '等待' in error:
                perception['recoverable'] = True
            elif '未找到' in error:
                perception['recoverable'] = True
            else:
                perception['recoverable'] = False

        # 更新工作记忆
        self.memory.remember('last_perception', perception)

        return perception

    def _get_expected_outcome(self, action):
        """获取预期结果"""
        expectations = {
            'find_element': '元素存在于当前页面',
            'click_element': '元素被点击，页面发生变化',
            'input_text': '文本被输入到元素中',
            'swipe': '屏幕发生滑动',
            'wait': '等待完成',
            'dump_ui': '获取到UI层次结构',
            'ocr_screen': '识别到屏幕文字'
        }
        return expectations.get(action, '操作完成')

    def _check_page_change(self):
        """检查页面是否变化"""
        old_page = self.memory.recall('current_page')
        # 实际实现中会获取新页面进行比较
        new_page = None
        return old_page != new_page
```

---

### 8. 完整 ReAct Loop 整合

```python
class ReActAgent:
    """
    完整的 ReAct Agent 实现

    包含：Think(推理) + Decide(决策) + Act(执行) + Perceive(感知) + Memory(记忆)
    """

    def __init__(self, mcp_client: MCPClient, llm_client=None):
        self.memory = MemorySystem()
        self.reasoner = ReasoningEngine(self.memory, llm_client)
        self.decider = DecisionEngine(self.memory)
        self.actor = ActEngine(self.memory, mcp_client)
        self.perceiver = PerceptionEngine(self.memory)

        self.max_loops = 10
        self.max_step_retries = 3

    def run(self, task: str) -> Dict:
        """
        执行完整 ReAct 循环

        流程：
        1. Think: 分析任务和当前状态
        2. Decide: 制定行动决策
        3. Act: 执行操作
        4. Perceive: 观察结果
        5. Loop: 判断是否继续
        """
        logger.info(f"=== 开始执行任务: {task} ===")

        self.memory.session_memory['user_request'] = task
        self.memory.session_memory['task_id'] = generate_task_id()

        for loop in range(self.max_loops):
            logger.info(f"--- Loop {loop + 1}/{self.max_loops} ---")

            # Step 1: Think - 推理
            reasoning = self.reasoner.think(task)
            logger.info(f"推理结果: {reasoning.get('reasoning')}")

            # 记录推理结果
            self.memory.session_memory['current_reasoning'] = reasoning

            # Step 2: Decide - 决策
            decision = self.decider.decide(reasoning)
            logger.info(f"决策方案: {decision.get('action')} (mode: {decision.get('mode')})")

            # Step 3: Act - 执行
            act_result = self.actor.execute(decision)
            logger.info(f"执行结果: {act_result}")

            # Step 4: Perceive - 感知
            perception = self.perceiver.perceive(act_result)
            logger.info(f"感知结果: goal_achieved={perception.get('goal_achieved')}")

            # 判断是否达成目标
            if perception.get('goal_achieved'):
                logger.info("=== 目标达成！===")
                self._record_success()
                return {'success': True, 'loops': loop + 1, 'perception': perception}

            # 判断是否可恢复
            if not perception.get('recoverable', True):
                logger.warning("遇到不可恢复错误")
                self._handle_irrecoverable_error(perception)
                return {'success': False, 'error': perception.get('anomalies')}

            # 更新循环计数
            self._update_loop_state(loop, reasoning, decision, act_result, perception)

        # 达到最大循环次数
        logger.error("达到最大循环次数，任务失败")
        return {'success': False, 'error': 'max_loops_exceeded'}

    def _record_success(self):
        """记录成功经验到记忆"""
        self.memory.learn(
            pattern=self.memory.recall('current_page'),
            strategy=self.memory.recall('last_action'),
            success=True
        )

    def _handle_irrecoverable_error(self, perception):
        """处理不可恢复错误"""
        self.memory.session_memory['failed_attempts'].append({
            'perception': perception,
            'timestamp': time.time()
        })

    def _update_loop_state(self, loop, reasoning, decision, act_result, perception):
        """更新循环状态"""
        self.memory.remember('current_loop', loop)
        self.memory.remember('current_reasoning', reasoning)
        self.memory.remember('current_decision', decision)
        self.memory.remember('current_act_result', act_result)
        self.memory.remember('current_perception', perception)

    def get_test_case_yaml(self) -> str:
        """从记忆生成YAML测试用例"""
        steps = []
        for step in self.memory.session_memory['completed_steps']:
            steps.append({
                'action': step['action'],
                'element': step.get('element'),
                'expected': step.get('expected'),
                'verify_methods': step.get('verify_methods', [])
            })

        return yaml.dump({
            'name': self.memory.session_memory.get('task_id'),
            'description': self.memory.session_memory.get('user_request'),
            'steps': steps
        }, allow_unicode=True)

    def get_test_script(self) -> str:
        """从记忆生成Python测试脚本"""
        # 根据记忆中的执行过程生成可执行脚本
        script_template = '''
import uiautomator2 as u2
import pytest
import time

class TestGenerated:
    def setup_method(self):
        self.d = u2.connect()
        self.d.implicitly_wait(30)

    # TODO: 根据执行历史生成完整测试代码
'''

        return script_template
```

---

### 9. 执行流程示例

以"启动鹿客管家App，找到哈哈哈设备，进入直播"为例，完整执行流程如下：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        完整执行流程示例                                       │
└─────────────────────────────────────────────────────────────────────────────┘

用户输入: "启动鹿客管家App，找到哈哈哈设备，进入直播"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loop 1: Think → Decide → Act → Perceive
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【Think 推理】
输入: 任务描述 + 当前状态(无)
分析: 
  - 这是一个多步骤任务，需要拆解
  - 第一步：启动应用
  - 第二步：等待页面加载
  - 第三步：查找设备
  - 第四步：点击进入
  - 第五步：验证直播启动
输出: next_action="start_app", params={package: "com.lockin.loock"}

【Decide 决策】
输入: 推理结果
决策:
  - 置信度高(0.95)，直接执行
  - 模式: direct
  - 备选方案: 重启UIAutomator服务
输出: action="start_app", mode="direct", fallback=["restart_service"]

【Act 执行】
调用MCP工具: mcp.start_app(package_name="com.lockin.loock")
结果: {'success': True, 'activity': '.MainActivity'}

【Perceive 感知】
观察执行结果:
  - 操作成功 ✓
  - 应用已启动 ✓
  - 应进入设备列表页面
判断: 目标部分达成，继续下一步

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loop 2: Think → Decide → Act → Perceive
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【Think 推理】
输入: 任务 + 记忆(应用已启动)
分析:
  - 应用已启动，需要验证设备页面
  - 验证方式：检查"设备"文本或底部导航栏
  - 可能需要等待页面加载
输出: next_action="verify_page", params={expected_text: "设备"}

【Decide 决策】
输入: 推理结果
决策:
  - 需要多种验证方式并行检查
  - 模式: cautious
  - 验证方法: resourceId(text="设备") + 底部导航栏 + ADB dumpsys
输出: action="verify_page", mode="cautious", strategies=[...]

【Act 执行】
调用MCP工具: mcp.dump_ui() + mcp.ocr_screen()
获取页面结构，分析是否包含设备列表元素

【Perceive 感知】
观察结果:
  - 页面包含 com.lockin.loock:id/tvTitle (text="设备") ✓
  - 页面包含设备列表容器 ✓
  - 页面可见元素数量: 23
判断: 设备页面验证成功 ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loop 3-5: 查找设备 "哈哈哈" 
（包含多次 Think/Act/Perceive 循环处理元素定位失败）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【Think 推理】
输入: 任务 + 当前页面信息
分析:
  - 需要在设备列表中找到"哈哈哈"设备
  - 当前页面有多个设备，如何定位？
  - 尝试使用 resourceId + textContains
输出: next_action="find_element", params={resourceId: "tvDeviceName", textContains: "哈哈哈"}

【Act 执行】
调用MCP工具: mcp.find_element(resourceId="tvDeviceName", textContains="哈哈哈")
结果: {'success': False, 'error': '元素未找到'}

【Perceive 感知】
观察结果:
  - 元素定位失败
  - 可能原因: 设备名称包含emoji("哈哈哈😂")而非纯文本
  - 需要使用模糊匹配
判断: 需要降级策略

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loop 4: 降级策略执行
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【Think 推理】
输入: 之前的失败信息
分析:
  - 精确匹配失败，需要模糊匹配
  - 尝试 textContains="哈哈哈"
输出: next_action="find_element", params={textContains: "哈哈哈"}

【Act 执行】
调用MCP工具: mcp.find_element(textContains="哈哈哈")
结果: {'success': True, 'bounds': {x: 100, y: 350, x2: 500, y2: 420}}

【Perceive 感知】
观察结果:
  - 成功找到包含"哈哈哈"的元素
  - 元素位于设备列表中
判断: 设备查找成功 ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loop 5-6: 点击设备进入直播
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【Act 执行】
调用MCP工具: mcp.click_element(resourceId="ivThumb")
点击设备缩略图

【等待页面跳转】
调用MCP工具: mcp.wait(seconds=10)

【验证直播启动】
调用MCP工具: mcp.find_element(textContains="KB/s")
结果: {'success': True}

【最终判断】
观察结果:
  - 网速信息 "KB/s" 出现在页面 ✓
  - 直播启动成功 ✓
目标达成！任务完成！

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
生成测试产物
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【YAML测试用例】
自动生成可维护的YAML测试用例文件

【Python测试脚本】
自动生成可直接执行的Python自动化脚本

【测试报告】
记录完整执行过程和结果
```

---

### 10. 与之前调试流程的关系

本方案中的 ReAct Agent 实现与之前实际调试鹿客管家直播启动流程完全一致：

| 调试过程中的操作 | Agent模块 | 说明 |
|-----------------|----------|------|
| 分析设备页面未显示原因 | Think | 推理分析可能原因 |
| 决定增加等待时间+多方式验证 | Decide | 决策采用谨慎模式 |
| 调用 start_app + dump_ui | Act | 执行MCP工具操作 |
| 检查是否出现"设备"文本 | Perceive | 感知验证页面状态 |
| 记录定位策略和失败原因 | Memory | 记忆学习经验 |

**关键差异**：
- 之前是手动编写代码调用工具
- 现在是将调用过程封装为自主决策的Agent
- Agent根据每次执行结果自主决定下一步行动

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
