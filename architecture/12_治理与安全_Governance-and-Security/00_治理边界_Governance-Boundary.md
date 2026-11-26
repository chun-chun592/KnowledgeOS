# 身份与安全 / Identity and Security

[返回正式架构 / Architecture entry point](../README.md)

## 主体和范围 / Principals and Scope

Human 与 Agent 是逻辑知识主体。Human 可用任意 Markdown 工具直接编辑。Agent 仅在获准范围内读写；默认查询 Agent Wiki 及公共区，Human 读取范围须明确配置。\
Human and Agent are logical knowledge owners. Humans can edit directly with any Markdown tool. Agents operate only within approved scopes. The Agent wiki and Shared are default read scopes. Human scopes require explicit configuration.

## 提案与治理 / Proposals and Governance

Human 修改交付目标、理由、完整 Markdown、diff 和基础 SHA-256。获得当前具体批准并复核基线后，Agent 可依宿主能力原生执行。Skills、哈希和协作租约属于应用层治理，同一账户的文件工具仍受其实际文件权限约束。\
Human changes are delivered with the target, rationale, complete Markdown, diff, and base SHA-256. After exact current approval and a fresh baseline check, Agents can apply them using permitted native tools. Skills, hashes, and leases are application-level governance. File tools retain the permissions of their actual account.

## 严格模式例外 / Strict Mode Boundary

独立 Windows 身份、Token 验证、管道 ACL 和拒绝门禁属于可选合成严格模式。Human 自动写入保持关闭，Publisher 禁用。\
Separate Windows principals, token checks, pipe ACLs, and deny gates belong to optional synthetic Strict mode. Automatic Human writes remain closed and Publisher is disabled.

具体批准来自当前可信交互，绑定目标、操作及基础哈希。获准原生编辑与真实库 MCP／CLI 只读可同时成立。/ Current trusted interaction binds exact approval; real-vault MCP and CLI stay read-only.
