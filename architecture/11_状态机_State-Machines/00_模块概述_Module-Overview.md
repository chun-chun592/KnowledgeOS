# 状态机 / State Machines

状态为 CANDIDATE / PARTIAL。\
The status is CANDIDATE / PARTIAL.

保留 REQUEST_ACCEPTED → VALIDATED → OBJECT_STORED → PREPARED → PROJECTED → COMMITTED，以及 NEEDS_REVIEW、REJECTED 和 NOOP 结果。\
Preserve REQUEST_ACCEPTED → VALIDATED → OBJECT_STORED → PREPARED → PROJECTED → COMMITTED and the NEEDS_REVIEW, REJECTED, and NOOP outcomes.

依据持久证据恢复，在重试前对账，保留未知结果，并禁止盲目覆盖或回滚。\
Recover from durable evidence, reconcile before retrying, retain unknown outcomes, and prohibit blind overwrite or rollback.

## 来源 / Sources

[SRC-022 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-023 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-039](../06_%E5%AD%98%E5%82%A8%E4%B8%8E%E4%BA%8B%E5%8A%A1_Storage-and-Transactions/01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-039-WB3F-TECHNICAL-DESIGN.md) [SRC-040](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-040-REENTRANCY-STATE-REVIEW.md) [SRC-053 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-052 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)

[架构来源与索引 / Architecture sources and index](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md)
