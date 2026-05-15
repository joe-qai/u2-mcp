# UIAutomator2 MCP Server

基于 FastMCP 框架实现的 UIAutomator2 MCP 服务器，提供 Android 设备自动化控制与 OCR 文本识别能力。

## 功能特性

- **设备管理** — ADB 命令执行、应用包列表、屏幕截图
- **UI 自动化** — 元素点击、文本输入、屏幕滑动、等待点击、页面滚动
- **应用管理** — 应用启动/停止、当前应用信息、UIAutomator2 服务管理
- **OCR 识别** — 屏幕文字识别（PaddleOCR）、文本定位与点击

## 环境要求

- Python 3.10+（推荐 3.11，PaddlePaddle 兼容性最佳）
- ADB 工具（已加入系统 PATH）
- Android 设备或模拟器（已通过 ADB 连接）

## 安装与配置

### 方式一：本地 Python 环境

适合已有全局 Python 环境、不希望使用虚拟环境的场景。

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/uiautomator2-mcp.git
cd uiautomator2-mcp

# 2. 安装依赖
pip install -e .
```

Agent 配置（`mcp.json`）：

```json
{
  "mcpServers": {
    "android": {
      "command": "python",
      "args": ["src/server.py"]
    }
  }
}
```

> **注意**：此方式依赖全局 Python 环境，需确保 `PYTHONPATH` 包含项目根目录。如遇模块导入问题，可在配置中添加 `env`：

```json
{
  "mcpServers": {
    "android": {
      "command": "python",
      "args": ["src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/uiautomator2-mcp"
      }
    }
  }
}
```

### 方式二：uv 虚拟环境

适合希望项目依赖隔离、使用 uv 管理环境的场景。

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/uiautomator2-mcp.git
cd uiautomator2-mcp

# 2. 用 uv 创建虚拟环境并安装依赖
uv venv --python 3.11
uv pip install -e .
```

Agent 配置（`mcp.json`）：

```json
{
  "mcpServers": {
    "android": {
      "command": ".venv/Scripts/python.exe",
      "args": ["src/server.py"]
    }
  }
}
```

Linux/macOS 下 venv Python 路径为 `.venv/bin/python`：

```json
{
  "mcpServers": {
    "android": {
      "command": ".venv/bin/python",
      "args": ["src/server.py"]
    }
  }
}
```

### 方式三：uv --directory 自动管理（推荐）

最简配置，uv 自动在指定目录下创建并管理虚拟环境，无需手动安装。

```json
{
  "mcpServers": {
    "android": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/uiautomator2-mcp",
        "run",
        "src/server.py"
      ]
    }
  }
}
```

> 将 `/path/to/uiautomator2-mcp` 替换为项目的实际绝对路径。

## MCP 配置文件位置

| 客户端              | 配置文件路径                      |
| ---------------- | --------------------------- |
| Claude Desktop   | `~/.claude/mcp.json`        |
| Cursor (macOS)   | `~/.cursor/mcp.json`        |
| Cursor (Windows) | `%APPDATA%\Cursor\mcp.json` |

## 可用工具

| 工具名                    | 说明                                              |
| ---------------------- | ----------------------------------------------- |
| `ADB_shell`            | 执行 ADB shell 命令                                 |
| `get_packages`         | 获取已安装应用包列表                                      |
| `get_screenshot`       | 获取屏幕截图                                          |
| `click_element`        | 点击界面元素（支持 text/description/resourceId/xpath 定位） |
| `input_text`           | 输入文本                                            |
| `swipe_screen`         | 滑动屏幕（up/down/left/right）                        |
| `wait_and_click`       | 等待元素出现并点击                                       |
| `scroll_to_element`    | 滚动到指定元素                                         |
| `start_app`            | 启动应用                                            |
| `stop_app`             | 停止应用                                            |
| `get_current_app`      | 获取当前运行的应用信息                                     |
| `UIAutomator2`         | 初始化 UIAutomator2 服务                             |
| `check_uiautomator2`   | 检查 UIAutomator2 服务状态                            |
| `restart_uiautomator2` | 重启 UIAutomator2 服务                              |
| `OCR`                  | 屏幕 OCR 文字识别                                     |
| `find_text`            | 查找文本位置坐标                                        |
| `click_text`           | 点击指定文本                                          |
| `click_position`       | 点击指定坐标                                          |

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试（需连接 Android 设备）
pytest

# 代码格式化
black src/ tests/

# 代码检查
ruff check src/ tests/
```

## 许可证

MIT License
