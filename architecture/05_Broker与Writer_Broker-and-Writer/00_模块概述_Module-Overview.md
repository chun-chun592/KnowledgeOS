# Broker与Writer / Broker and Writer

状态为 CANDIDATE / PARTIAL。\
The status is CANDIDATE / PARTIAL.

保留经认证的命名管道端点、有界版本化帧、关联响应、限定身份验证和受控 Writer 操作。\
Preserve authenticated named-pipe endpoints, bounded versioned frames, correlated replies, qualified identity verification, and controlled Writer operations.

安全连接失败时禁止回退到本地写入。\
A failed secure connection cannot fall back to local writes.

Broker、Writer 和 Publisher 的角色决策彼此独立，Publisher 的生产激活仍待决定。\
Broker, Writer, and Publisher role decisions remain distinct, and production Publisher activation is unresolved.

## 来源 / Sources

[SRC-006](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-006-wb3d2-writer.md) [SRC-007](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-007-PIPE-TRANSPORT.md) [SRC-008](01_%E5%8E%86%E5%8F%B2%E6%9D%A5%E6%BA%90_Historical-Sources/SRC-008-MANAGED-WRITE-GATES.md) [SRC-049 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-050 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) [SRC-051 · 历史引用 / historical reference](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)

[架构来源与索引 / Architecture sources and index](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md)
