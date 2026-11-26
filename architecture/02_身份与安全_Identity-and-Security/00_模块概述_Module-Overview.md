# 身份与安全 / Identity and Security

状态为 CANDIDATE / PARTIAL。\
The status is CANDIDATE / PARTIAL.

Human、Agent、Writer 和 Unauthorized 使用不同身份，并核验 SID 和 Token。\
Human, Agent, Writer, and Unauthorized use distinct principals with verified SID and Token.

通过显式 ACL、所有者、继承、父目录删除子项权限及身份检查执行默认拒绝和最小权限。\
Enforce default deny and least privilege with explicit ACL, owner, inheritance, parent delete-child, and identity checks.

已证明的非特权隔离保证不覆盖同 SID 进程和受信任的特权主体。\
The demonstrated nonprivileged isolation guarantee excludes same-SID processes and trusted privileged principals.

静态审查不能证明运行时强制执行。\
Static review cannot establish runtime enforcement.

## 来源 / Sources

[SRC-003](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-003-SECURITY.md) [SRC-004](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-004-permissions.md) [SRC-005](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-005-permissions.md) [SRC-032 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-033 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-034 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-035 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-046 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-047 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-048 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)

[架构来源与索引 / Architecture sources and index](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md)
