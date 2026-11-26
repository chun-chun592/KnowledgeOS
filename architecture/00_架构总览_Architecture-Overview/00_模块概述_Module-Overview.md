# 架构总览 / Architecture Overview

[返回正式架构 / Architecture entry point](../README.md)

## 目标与事实来源 / Scope and Source of Truth

正文保存在现有 Markdown 目录中。Human 和 Agent 按逻辑所有权协作；索引、日志和辅助状态可从正文或可核验证据派生。\
Note content lives in the existing Markdown tree. Humans and agents collaborate under logical ownership. Indexes, logs, and auxiliary state derive from content or verifiable evidence.

## 两种运行方式 / Operating Modes

日常 Markdown Native 使用任意编辑器、宿主 Skills、只读 MCP／CLI 和获准的原生编辑。独立测试根可使用 Native 写工具；严格模式另有 Broker、Writer 和 SQLite。\
Daily Markdown Native uses any editor, host Skills, read-only MCP or CLI, and approved native edits. A separate test root can use Native write tools. Strict mode has its own Broker, Writer, and SQLite ledger.

## 继续阅读 / Continue Reading

[系统架构](01_组件与数据流_Components-and-Data-Flow.md)说明组件和数据流，[知识架构](../02_知识架构_Knowledge-Architecture/00_知识目录_Knowledge-Layout.md)说明目录及字段。\
See [system architecture](01_组件与数据流_Components-and-Data-Flow.md) for components and data flow, and [knowledge architecture](../02_知识架构_Knowledge-Architecture/00_知识目录_Knowledge-Layout.md) for directories and fields.
