# 数据平面 / Data Plane

状态为 CANDIDATE / PARTIAL。\
The status is CANDIDATE / PARTIAL.

业务账本、Broker 审计、私有暂存与封存、受限提前读取投影各自独立。\
Keep the business ledger, Broker audit, private staging and seal, and limited early read projection separate.

Broker 私有权限不会下放给 Writer 或 Agent。\
Broker private rights do not transfer to Writer or Agent.

保留失败时关闭的激活行为，以及父目录稳定性、继承、重解析点与链接规则。\
Retain fail-closed activation and rules for stable parents, inheritance, reparse points, and links.

## 来源 / Sources

[SRC-037](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-037-SECURE-CREATION-CONTRACT.md) [SRC-038 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)

[架构来源与索引 / Architecture sources and index](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md)
