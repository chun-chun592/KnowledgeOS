# 存储与事务 / Storage and Transactions

[返回正式架构 / Architecture entry point](../README.md)

## 知识、证据和索引 / Knowledge, Evidence, and Index

Markdown 是正文事实来源。索引按类型分组并展示摘要、状态与统计；真实库定点更新相关行，保留手写内容。日志保存实际操作、目标和哈希变化。\
Markdown is authoritative for content. The index groups notes by type with summaries, status, and counts. Real-vault updates preserve hand-written content and target relevant rows. Logs record the operation, target, and hash changes.

## 原生备份与同步 / Native Backup and Sync

真实库备份与租约按既有协议执行。独立测试根 Native 流程保留按哈希寻址的备份和观察状态；同步重建托管区块，记录 native_local 或 observed_filesystem，不生成严格事务。外部编辑仅在扫描比对时被观察。\
Real-vault backups and leases follow the existing protocol. Native test workflows keep content-addressed backups and observation state. Sync rebuilds managed blocks and records native_local or observed_filesystem without creating Strict transactions. External edits are seen only on a comparison scan.

## 严格账本与恢复 / Strict Ledger and Recovery

严格模式以 SQLite 记录事务和审计，Markdown 仍为正文。通过收据、备份摘要与文件身份对账；确认已投影后补账本，未知证据进入人工检查。\
Strict mode uses SQLite for transactions and audit. Markdown remains authoritative for content. Reconcile receipts, backup digests, and file identity. Complete ledger state for verified projections and send unknown evidence for review.

严格账本以已认证主体与幂等键作为唯一请求关联，并记录请求摘要。投影收据、内容备份和成功审计分开保存；派生文件落后时单独同步，保留已确认提交。\
The Strict ledger uniquely associates the authenticated principal and idempotency key and retains the request digest. Projection receipts, content backups, and successful audit records are separate. Rebuild stale projections independently and retain confirmed commits.

严格投影替换与 SQLite 提交不是同一次操作。直接读取者可能在账本确认之前看到新的完整文件，故严格业务结果应从账本核实。\
Strict projection replacement and SQLite commit are separate operations. Direct readers may see a complete new file before the ledger confirms it, so verify Strict business outcomes against the ledger.

[目录命名及三语模板对照 / Localized paths and template mapping](../02_知识架构_Knowledge-Architecture/01_三语目录对照_Localized-Paths.md)

公共区维护独立索引和日志。公共新增可追加对应索引条目和日志，并维护可重建统计。/ Shared has independent index and log projections.
