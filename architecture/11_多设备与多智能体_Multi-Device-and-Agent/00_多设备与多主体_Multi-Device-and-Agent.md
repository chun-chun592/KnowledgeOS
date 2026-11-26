# 多设备 / Multi-Device

[返回正式架构 / Architecture entry point](../README.md)

## 多设备访问 / Multi-Device Access

同一 Markdown 目录可由不同设备或编辑工具访问，知识事实仍是文件正文。项目当前没有内置同步、离线合并或跨设备锁协调能力。\
The same Markdown tree can be opened from different devices and editors. Note content remains authoritative. The project currently provides no built-in sync, offline merge, or distributed locking.

## 外部同步与冲突 / External Sync and Conflicts

若使用外部同步，先由 Human 确认范围和冲突政策，避免并发编辑同一文件。检测到哈希变化或同步冲突时重读并人工核对。观察到的文件变化不会被标成 Writer 事务。\
For external sync, the Human sets scope and conflict policy and avoids concurrent edits of the same file. Re-read and review on hash changes or sync conflicts. Observed changes are not Writer transactions.

## 严格模式范围 / Strict Mode Scope

历史 Writer 同步要求只适用于明确选择的严格投影契约，不约束日常外部 Markdown 同步。\
The historical Writer synchronization requirement only applies to the explicitly selected Strict projection contract.

共享区域已有内容的变更需要批准。新增索引及日志仍使用现有租约。/ Existing Shared edits require approval; lease Shared index and log when adding.
