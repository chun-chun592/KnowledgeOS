# 数据平面 / Data Plane

[返回正式架构 / Architecture entry point](../README.md)

## 正文与派生数据 / Content and Projections

Agent Wiki 的 Markdown 保存正文。读取会验证范围、路径和文件访问条件，链接与索引反映当前已读范围；日志、备份和测试根缓存是辅助数据。\
Agent wiki Markdown holds note content. Reads check scope, paths, and file access conditions. Links and indexes reflect the visible scope. Logs, backups, and test-root caches are auxiliary.

## 写入边界 / Write Boundary

真实库按库内协议原生编辑，先保留基础哈希与备份，再更新目标和派生记录。独立测试根的 Native 工具仅对合格 Agent Markdown 执行替换、备份与同步，拒绝受保护根和标记的严格测试根。\
Real-vault edits follow local protocol: capture a base hash and backup, then update the note and its derived records. Native tools replace, back up, and sync eligible Agent Markdown in a separate test root. They reject protected roots and marked Strict roots.

## 严格投影 / Strict Projection

严格模式要求绑定根和父目录、验证文件身份、拒绝链接、私有暂存、提交前后核对及失败关闭。严格账本只在验证投影后确认 COMMITTED。\
Strict mode requires root and parent binding, file identity checks, link rejection, private staging, pre- and post-write verification, and fail-closed behavior. Its ledger marks COMMITTED only after verifying the projection.
