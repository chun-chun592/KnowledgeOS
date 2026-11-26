# 实际能力矩阵 / Actual Capability Matrix

| 模式 / Mode | 读取 / Reads | 变更 / Changes |
| --- | --- | --- |
| 真实库 MCP / Real-vault MCP | Agent Wiki 与明确授权的 Human 子目录 / Agent wiki and explicitly approved Human scopes | 只生成提案 / Proposals only |
| 真实库 CLI / Real-vault CLI | doctor、query、inspect，以配置作用域为准 / doctor, query, inspect under configured scopes | 可起草，工具直写关闭 / Drafts only |
| 原生文件工具 / Native file tools | 实际授权范围 / Approved scope | Human 自主编辑；Agent 区按库内协议 / Human edits directly; Agent edits follow vault rules |
| 独立 Native 测试根 / Separate test root | 范围内工具读取 / Scoped tool reads | Native CRUD、摄取、综合脚手架、分段追加、归档、恢复和同步 / Native CRUD, intake, synthesis scaffold, section append, soft archive, restore, and sync |
| 可选严格合成模式 / Optional synthetic Strict mode | 本地 Broker 验证 / Local Broker checks | Secure Writer 与 SQLite 提交 / Secure Writer and SQLite commits |

未实现内置跨设备同步、中央 Agent 调度或 Human 自动提交。CLI 与 MCP 在真实库保持原有读写边界。\
Built-in cross-device sync, a central Agent scheduler, and automatic Human commits are unavailable. CLI and MCP preserve the real vault’s existing access boundary.
