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

### 分发与继承 / Distribution and Provenance

产品版本为 0.1.3；Agent Kit 0.1.1 提供原 Core、索引渲染及分段编辑逻辑，许可证及归属保留。\
The product version is 0.1.3. Agent Kit 0.1.1 provides the original Core, index rendering, and section editing logic, with its license and attribution retained.

日常安装使用标准 Python 包，严格模式通过可选 Windows 依赖和既有合成配置启动。\
Daily use uses the standard Python package. Strict mode uses optional Windows dependencies and an existing synthetic configuration.

在设有共享锁目录的测试库中，原生编辑和同步使用既有锁文件命名；未配置共享目录时，仅有本地原生进程协调。\
Native changes and sync use the existing lease filenames in test vaults with a shared lock directory. Without that directory, coordination is limited to local Native processes.

全量同步保留索引托管块外文字；现有真实库继续按其协议逐行更新索引并追加日志。\
Full sync preserves text outside the managed index block. The existing real vault continues to use its own protocol for targeted index edits and log appends.
