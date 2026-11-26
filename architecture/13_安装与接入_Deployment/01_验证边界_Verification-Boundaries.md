# 测试与验收 / Testing and Acceptance

[返回正式架构 / Architecture entry point](../README.md)

## 日常验证 / Daily Verification

验证实际安装版本、CLI 读取入口、MCP 工具列表及只读范围。知识工作应检查基线哈希、共享租约、来源和链接，以及索引与日志的对应记录。\
Verify the installed version, CLI reading, MCP tool registration, and read-only scopes. Knowledge work checks the base hash, shared leases, citations and links, and matching index and log entries.

## 模式隔离与证据 / Mode and Evidence Separation

写入、冲突、恢复和同步验证在独立测试根进行。已有验证适用于相应版本和环境；不承诺任意宿主、外部同步或真实库工具写入已验收。\
Validate writes, conflicts, recovery, and sync in a separate test root. Existing checks apply to their tested versions and environments. They do not establish acceptance for every host, external sync, or real-vault tool writes.

## 严格验收 / Strict Acceptance

Token、ACL、IPC、响应丢失和崩溃恢复是严格模式独立验收项目。历史实验数据保留在本地和 Git 历史。\
Token, ACL, IPC, lost response, and crash recovery checks belong to separate Strict-mode acceptance. Historical experimental results remain in local records and Git history.
