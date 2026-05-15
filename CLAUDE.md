# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UIAutomator2 MCP Server — a FastMCP-based server that exposes Android device automation capabilities (via uiautomator2) as MCP tools for AI assistants like Claude. Supports ADB commands, UI interactions, app management, and OCR-based text recognition (PaddleOCR).

## Commands

### Install dependencies
```bash
pip install -e .
```

### Install with dev dependencies (lint + test)
```bash
pip install -e ".[dev]"
```
Or with PDM:
```bash
pdm install
```

### Run the MCP server
```bash
python src/server.py
# or via PDM:
pdm start
```

### Run tests
```bash
pytest
```
Tests are integration tests that require a connected Android device with ADB. They cannot run in isolation without hardware.

### Lint and format
```bash
ruff check src/ tests/
black src/ tests/
```

## Architecture

**Entry point:** `src/server.py` — creates a `FastMCP` instance, initializes the device connection on startup, and registers all MCP tool functions as decorated endpoints.

**Core package:** `src/mcp_android/` contains four modules:

- **`android.py`** — Device connection singleton (`_device` global). All other modules call `get_device()` to access the u2.Device object. Provides ADB shell execution, package listing, and screenshot capture.
- **`ui.py`** — UI automation operations (click, input, swipe, wait-and-click, scroll-to). Element locators: text, description, resourceId, xpath.
- **`app.py`** — App lifecycle management (init/start/stop/get current app). `init_uiautomator2()` handles ADB checks, device connection, APK installation, and service startup. Also provides `check_uiautomator2()` status diagnostics and `restart_uiautomator2()`.
- **`ocr.py`** — `OCRManager` singleton using PaddleOCR for screen text recognition. Caches OCR results with a 1-second timeout. Provides `ocr_screen()`, `find_text_position()`, `click_text()`, and `click_position()`.

**Pattern:** All modules depend on `android.py`'s global device object. The device is initialized at server startup in `server.py` and shared across all operations. If the device is not initialized, `get_device()` raises `RuntimeError`.

## Key Configuration

- **Python:** ≥3.10
- **Line length:** 100 (both black and ruff)
- **Ruff rules:** E, F, I, N, W, B
- **Build system:** PDM backend (`pdm-backend`)
- **Logging:** Writes to `/tmp/mcp-android.log` and stderr

## MCP Integration

The server is designed to be consumed by Claude Desktop or Cursor via their `mcp.json` config. Tools are registered with `@mcp.tool()` decorators. OCR tools (ocr_screen, find_text_position, click_text, click_position) are registered directly from the `OCRManager` instance rather than from the package's `__init__.py` exports.