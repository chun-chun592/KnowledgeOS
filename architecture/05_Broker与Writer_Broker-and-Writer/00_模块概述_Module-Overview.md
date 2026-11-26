# Broker 与 Writer / Broker and Writer

[返回正式架构 / Architecture entry point](../README.md)

## 可选职责 / Optional Roles

Broker 验证本地命名管道对端、授权操作和目标，受保护的 Writer 管道只允许 Broker；Writer 依据绑定的请求及证据修改合成 Agent 投影。\
The Broker authenticates the local named-pipe peer, operation, and target. Only the Broker is admitted to the protected Writer pipe. The Writer changes synthetic Agent projections using bound requests and evidence.

## 提交契约 / Commit Contract

请求和幂等键绑定已验证主体、操作、相对路径、文件身份和内容摘要；重复键用于查询或复用同一决定，摘要不符为冲突。未知结果先查询或核验，不换键盲重试。\
Requests and idempotency keys bind the verified principal, operation, relative path, file identity, and content digest. Replay queries or reuses the same decision, and differing digests conflict. Check unknown outcomes without retrying under a new key.

合成严格传输采用本地消息模式管道，拒绝远程连接，使用有界 JSON 消息并拒绝重复键。客户端核验端点身份；认证或绑定失败时停止，无本地直写回退。\
Synthetic Strict transport uses local message-mode pipes, rejects remote connections, bounds JSON messages, and rejects duplicate keys. Clients verify endpoint identity. Authentication or binding failure stops the request without falling back to local writes.

## 日常边界 / Daily Boundary

Markdown Native 日常工作无需 Broker 或 Writer。独立测试根的 Native 变更走本地作用域与哈希规则；合成 Strict 前置条件及恢复边界见 [ADR-04 补充](../14_架构决策_Architecture-Decisions/02_ADR04补充安全投影_ADR04-Secure-Projection-Addendum.md)。\
Daily Markdown Native use requires neither Broker nor Writer. Native test changes use local scope and hash rules. See the [ADR-04 addendum](../14_架构决策_Architecture-Decisions/02_ADR04补充安全投影_ADR04-Secure-Projection-Addendum.md) for synthetic Strict prerequisites and recovery boundaries.
