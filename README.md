# Cache Simulator A · Lab 4

Cache 基本性能分析模拟器。前后端分离：后端 Python + FastAPI，前端 React + TypeScript + Vite。

## 功能特性

- N 路组相联 Cache 模拟（1 / 2 / 4 / 8 路）
- LRU 替换策略 + 写分配写回策略
- 支持 Cache 大小 8 / 16 / 32 / 64 KB
- 支持块大小 16 / 32 / 64 / 128 B
- 参数扫描：自动对比不同 Cache 大小、相联度、块大小的缺失率
- 纯 CSS 分组柱状图可视化（无外部图表库）
- 支持粘贴 trace 文本或上传 `.din` 文件

## Trace 文件格式

每行格式：`access_type address data`

- `0`：load data
- `1`：store data
- `2`：fetch instruction（自动跳过）

示例（SPEC 基准程序 trace）：

```
2 400190 8fa40000
0 7ffebc64 0
1 100039b8 0
```

## 目录结构

```
sim_a/        核心模拟逻辑（Python）
server/       FastAPI 服务
frontend/     React + TypeScript + Vite 前端
cache_sim.py  CLI 命令行工具（独立可用）
cache_gui.py  tkinter 图形界面（独立可用）
```

## 环境要求

- Python 3.13+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv)
- npm

## 初始化

```bash
# Python 虚拟环境
uv sync

# 前端依赖
cd frontend && npm install
```

## 启动项目

```bash
# 后端（在项目根目录）
uv run uvicorn server.app:app --host 127.0.0.1 --port 8767 --reload

# 前端（另开终端）
cd frontend && npm run dev
```

浏览器访问 http://localhost:5173

## CLI 使用

```bash
# 单次运行
uv run python cache_sim.py trace.din -s 16384 -a 2 -b 32

# 批量扫描所有参数组合
uv run python cache_sim.py trace.din --batch

# 图形界面
uv run python cache_gui.py
```

## 测试

```bash
# 后端
uv run python -m pytest

# 前端类型检查
cd frontend && npm run build
```
