# 控制平面 / Control Plane

[返回正式架构 / Architecture entry point](../README.md)

## 日常控制 / Daily Control

任务路由由宿主及 Skills 完成；实际控制入口是库根 AGENTS.md、批准范围及本机 CLI／MCP 配置。MCP 是可选工具接口，宿主也可直接读文件或走现有 CLI。\
The host and Skills route tasks. The vault's AGENTS.md, approved scopes, and local CLI or MCP configuration define the operating boundary. MCP is optional; hosts may also read files or use the existing CLI.

## 动作选择 / Action Selection

先区分读取、Agent 草稿或实际修改、Human 提案，再按权限与工具可用性执行。真实库直接编辑遵循协作协议；工具缺失或验收失败时保留草稿并报告。\
Distinguish reads, proposed or actual Agent changes, and Human proposals before choosing an available authorized tool. Real-vault edits follow the collaboration protocol. Keep drafts and report unavailable tools or failed verification.

## 可选控制面 / Optional Strict Control Plane

严格模式的可信配置固定根、角色、管道和许可；Broker 认证请求并通过独立受保护管道交给 Writer。普通 Agent 无权把请求声明当成服务身份。\
Trusted Strict configuration binds the root, roles, pipes, and permissions. The Broker authenticates requests and hands them to the Writer over a separate protected pipe. Agent-supplied identity claims carry no service authority.

自主维护 Agent 私有知识和新增公共知识。受保护变更遵循具体批准。/ Maintain Agent private and add Shared knowledge autonomously. Protected changes require exact approval.
