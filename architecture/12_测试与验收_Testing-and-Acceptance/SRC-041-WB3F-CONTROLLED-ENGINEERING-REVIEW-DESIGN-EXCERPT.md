> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../README.md) for current applicability.

# 历史设计摘录

来源：Architecture-Frozen / 12-Testing-and-Acceptance / historical-source / SRC-041-WB3F-CONTROLLED-ENGINEERING-REVIEW.md

## 混合策略与管理员恢复

真正在同一 v3 账本测试。显式 legacy 模式在 PUBLISHING 中断，保留旧策略 PREPARED；已授权离线管理员通过真实 Writer 进程读取可信审批，先只读检查，随后 apply 原事务，完成正式 Log／Index。原请求经真实客户端重放得到原事务 ID。随后新策略单步在 PREPARED 中断；从同一库启动的旧兼容服务在写入前拒绝接管，账本 SHA-256 未变；默认的单步必选服务按新记录恢复并重放原事务。两种未决策略按顺序在同一账本验收，整库串行门禁没有人为关闭以制造并存未决状态。

独立 LegacyVault 中实际 v2 未决事务阻断迁移，获授权的旧策略 Recover 后才能迁移。DDL 事务内退出 75 后仍为 v2；有效检查点经 SQLite Backup API 恢复到另一个离线文件并与崩溃后的账本逻辑一致，未改写现有 Markdown。旧 reader 对复制 v3 拒绝启动，未复审的检查点不能自动复用。

默认采用整库失败关闭，优先保障恢复顺序，代价是同一库的所有写入和默认监听器可用性。R02_API_PENDING 后重启发现不确定状态，目标不变；第二次重启在任何自动恢复前检测到已持久 NEEDS_REVIEW。手动诊断只能列出，拒绝业务请求和 Recover apply。管理员入口只读 inspect 已验证数据库字节不变；apply 只能对满足既有证据的最早挂起事务执行。待审查状态不能清除或覆盖，Agent 身份不能使用管理员入口，多次 apply 已结事务被拒绝。审批文件限定 Vault、事务和动作，服务记录批准标识、检查、开始及结果，由受控调用方保存并哈希。正式审批的防重放、到期时间、耐久审计及按路径隔离均待审查。当前未提供任何审查豁免。
