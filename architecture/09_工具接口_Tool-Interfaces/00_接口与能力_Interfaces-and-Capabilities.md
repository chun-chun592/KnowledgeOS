# API 与契约 / API and Contracts

[返回正式架构 / Architecture entry point](../README.md)

## 现行只读接口 / Current Read Interfaces

本地 stdio MCP 提供 search_knowledge、read_markdown、note_metadata、query_tags、knowledge_links、lint_knowledge 及 propose_human_update。按权限返回范围限定结果，读取可用基础哈希校验分页。\
Local stdio MCP provides search_knowledge, read_markdown, note_metadata, query_tags, knowledge_links, lint_knowledge, and propose_human_update. Results are scoped, and paged reads can be pinned to a base hash.

## CLI 与模式发现 / CLI and Capability Discovery

`knowledgeos` 提供 doctor、query、inspect 及知识工作流命令。write_capability 区分 READ_ONLY、独立测试根 Native 写入及 Strict Writer；能力探测不会授予目录权限。真正的 Vault 不配置工具直写。\
`knowledgeos` provides doctor, query, inspect, and workflow commands. write_capability distinguishes READ_ONLY, Native test-root writes, and Strict Writer status. Discovery does not grant directory access. Real vaults are not configured for tool writes.

## 模式专用写入 / Mode-Specific Writes

测试根 Native MCP 使用 native_note_change 和 sync_native_wiki，CLI 以独立测试根执行写入与同步。严格合成入口另有提交、事务状态、恢复与审计，使用 Broker 专用身份验证、幂等键和边界。\
Native test MCP uses native_note_change and sync_native_wiki. The CLI writes and syncs only in an independent test root. Strict synthetic interfaces separately handle submission, transaction status, recovery, and audit with Broker-specific identity, keys, and bounds.

[实际能力矩阵 / Actual Capability Matrix](Modes/00_实际能力矩阵_Capability-Matrix.md)

[目录命名及三语模板对照 / Localized paths and template mapping](../02_知识架构_Knowledge-Architecture/01_三语目录对照_Localized-Paths.md)

MCP 和 CLI 支持 Shared 读取、检索、链接、lint 和提案。真实库写入通过获准的原生文件工具。独立测试根支持 Shared 新建、同名拒绝和追加索引日志。
