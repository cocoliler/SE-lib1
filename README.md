# Code Review Agent

一个面向 Python 项目的代码审查 Agent。它通过 LLM 进行代码理解与审查，同时结合本地工具完成文件读取和 Python AST 静态分析，输出结构化的代码质量问题、潜在 Bug、风险等级和改进建议。

## 1. 项目简介

本项目对应「代码审查 Agent」方向。

目标是实现一个简单但完整的 Agent：

```text
用户输入
   ↓
Agent 判断任务
   ↓
工具调用：读取代码 / AST 分析
   ↓
LLM 推理与代码审查
   ↓
结构化结果
   ↓
用户输出
```

核心能力：

- 分析 Python 代码质量
- 发现潜在 Bug
- 分析异常处理、复杂度、可维护性等问题
- 给出可操作的改进建议
- 支持单文件和项目目录审查
- 支持上下文记忆
- 支持工具调用
- 支持 LLM 请求重试
- 支持命令行交互

## 2. 技术栈

- Python 3.10+
- OpenAI-compatible Python SDK
- Python `ast` 标准库
- argparse / pathlib / dataclasses / logging
- 不依赖大型 Agent 框架，直接实现 Agent Loop，便于展示 Agent 原理

## 3. 项目结构

```text
code_review_agent/
├── app.py                  # CLI 入口
├── agent/
│   ├── __init__.py
│   ├── agent.py            # Agent 主循环
│   ├── llm.py              # LLM 调用与重试
│   ├── memory.py           # 上下文记忆
│   ├── prompts.py           # Prompt 模板
│   └── schemas.py           # 数据结构
├── tools/
│   ├── __init__.py
│   ├── file_tool.py         # 文件读取工具
│   └── ast_tool.py          # Python AST 静态分析工具
├── examples/
│   └── bad_example.py       # 用于演示审查效果
├── tests/
│   └── test_ast_tool.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Design.md
└── README.md
```

## 4. 安装

建议 Python 3.10+。

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 5. 配置 LLM

复制环境变量模板：

```bash
cp .env.example .env
```

然后设置：

```text
LLM_API_KEY=你的API_KEY
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=你的模型名称
```

项目采用 OpenAI-compatible API，因此也可以将 `LLM_BASE_URL` 修改为课程允许使用的其他兼容服务。

## 6. 使用方法

### 审查单个 Python 文件

```bash
python app.py review examples/bad_example.py
```

### 审查目录

```bash
python app.py review examples
```

默认只读取 `.py` 文件，并限制单文件大小，避免一次性把超大文件送入模型。

### 交互模式

```bash
python app.py chat
```

示例：

```text
You: 请重点检查 examples/bad_example.py 的异常处理和潜在 Bug
Agent: ...
You: 还有哪些可维护性问题？
Agent: ...
```

### 查看 AST 静态分析

不调用 LLM，也可以直接运行：

```bash
python app.py ast examples/bad_example.py
```

### 查看帮助

```bash
python app.py --help
```

## 7. Agent 循环

项目核心 Agent Loop 为：

```text
输入任务
  ↓
读取代码
  ↓
调用 AST 工具
  ↓
构造 Prompt
  ↓
LLM 推理
  ↓
检查输出
  ↓
保存上下文
  ↓
输出结果
```

其中：

- `file_tool.py`：负责安全读取代码文件
- `ast_tool.py`：负责 Python 语法树分析
- `llm.py`：负责 LLM 调用和指数退避重试
- `memory.py`：保存当前会话中的代码审查上下文
- `agent.py`：负责协调上述组件

## 8. 审查输出

模型被要求尽量按照以下结构输出：

```text
## 总结

## 发现的问题

### [高] 问题标题
- 文件/位置：
- 问题：
- 原因：
- 建议：

## 正确之处

## 修改优先级
```

注意：LLM 的判断属于辅助性分析，不能替代实际测试、编译器、静态分析器或人工 Code Review。

## 9. 测试

运行：

```bash
python -m unittest discover -s tests -v
```

测试不依赖 LLM API，主要验证 AST 工具。

## 10. 设计亮点

### 10.1 Agent，而不是简单 Chat

普通聊天程序：

```text
用户 → LLM → 输出
```

本项目：

```text
用户
 ↓
Agent
 ├── 文件读取 Tool
 ├── AST 分析 Tool
 ├── LLM
 └── Memory
 ↓
审查结果
```

Agent 会先获取代码和静态分析信息，再把这些信息交给 LLM。

### 10.2 工具增强

单纯让 LLM“猜”代码问题容易产生幻觉。

因此项目增加：

1. 文件读取工具
2. Python AST 分析工具

AST 工具可以提供函数数量、类数量、导入数量、过长函数、过长文件、裸 `except`、可疑 `eval/exec` 等客观信息。

### 10.3 错误处理

LLM 调用失败时进行有限次数重试，并使用指数退避：

```text
第 1 次失败 → 等待
第 2 次失败 → 等待更久
第 3 次失败 → 返回明确错误
```

不会无限重试。

## 11. 演示建议

1. 运行 `python app.py ast examples/bad_example.py`
2. 展示 AST 工具发现的客观问题
3. 运行 `python app.py review examples/bad_example.py`
4. 展示 LLM 对问题的进一步解释
5. 再进入 `python app.py chat`
6. 追问“请重点解释异常处理问题”
7. 展示上下文记忆效果


