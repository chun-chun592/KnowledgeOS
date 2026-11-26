# 存储与事务 / Storage and Transactions

状态为 CANDIDATE / PARTIAL。\
The status is CANDIDATE / PARTIAL.

Markdown 承载知识，SQLite 在后期设计中是业务提交权威，不可变对象以内容寻址，日志与索引可派生并修复。\
Markdown carries knowledge, SQLite is the business commit authority in the later design, immutable objects are content-addressed, and logs and indexes are derived and repairable.

保留同卷原子替换、锁、幂等性、明确的结果未知状态、崩溃恢复和完整性检查。\
Preserve same-volume atomic replacement, locks, idempotency, explicit unknown outcomes, crash recovery, and integrity checks.

文件身份检查与重命名是不同步骤，候选设计不提供原子 FILE_ID CAS。\
File identity checks and rename are separate steps, and the candidate provides no atomic FILE_ID CAS.

## 来源 / Sources

[SRC-009](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-009-TRANSACTION-LEDGER-CONTRACT.md) [SRC-010](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-010-LEDGER-SCHEMA.md) [SRC-039](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-039-WB3F-TECHNICAL-DESIGN.md) [SRC-052 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-053 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-054 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)

[架构来源与索引 / Architecture sources and index](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md)
