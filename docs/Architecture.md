# 架构与维护 / Architecture and Maintenance

Markdown 记录正文，固定 Human 与 Agent 区域分别承载各自知识。\
Markdown holds note contents, and the fixed Human and Agent regions hold their respective knowledge.

宿主根据任务选择 Skills 和工具，MCP 提供范围受控的检索与提案，CLI 复用相同读取规则。\
The host selects Skills and tools by intent, MCP provides scoped search and proposals, and the CLI reuses the same read rules.

Agent 搜索并核验来源后更新现有知识，保留出处、链接和必要的历史。\
The Agent searches and verifies sources, then updates existing knowledge while preserving provenance, links, and relevant history.

原生模式用内容哈希和备份支持冲突检查与恢复，外部编辑通过同步重新发现。\
Native mode uses content hashes and backups for conflict checking and recovery, and sync discovers external edits.

索引和日志是可重建的派生文件，原生写入和文件观察使用不同的事件来源。\
Index and log files are rebuildable projections, and native actions and filesystem observations use distinct event origins.

严格模式由 Broker 验证 Windows 调用方，再由独立 Secure Writer 提交；SQLite 记录事务，Markdown 保持正文权威。\
In Strict mode the Broker verifies the Windows caller and an independent Secure Writer commits the projection. SQLite records transactions, and Markdown remains authoritative for note content.

现有合成严格模式要求已验证的根、独立主体、受保护暂存及失败关闭，Publisher 保持禁用。\
The existing synthetic Strict mode requires a verified root, distinct principals, protected staging, and fail-closed behavior. Publisher remains disabled.

Human 自动写入保持关闭，Agent 交付完整改动提案供 Human 手动应用。\
Automatic Human writes stay disabled, and the Agent prepares complete proposals for manual application.

本公开候选只包含脱敏的架构概要；历史 ADR 的机器绑定、运行证据及原始来源留在本地。\
This public candidate contains the sanitized architecture summary. Machine bindings, operational evidence, and original historical sources remain local.

[ADR-04 secure projection addendum](ADR04-Secure-Projection.md)
