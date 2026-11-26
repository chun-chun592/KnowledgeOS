> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../README.md) for current applicability.

# ADR-04 补充：受控投影 / ADR-04 Addendum for Controlled Projection

R5 已批准在独立合成环境中由获准的 Secure Writer 执行普通 Markdown 提交，Publisher 继续禁用。\
R5 approves ordinary Markdown commits by an authorized Secure Writer in an isolated synthetic environment. Publisher remains disabled.

本决定仅对 R5 合成部署替代 SRC-036 第 10 行的执行主体限制，以及第 11 行对该专用 Writer 仅有账本权限的限制。\
For R5 synthetic deployment only, this decision supersedes the executor restriction in SRC-036 line 10 and the ledger-only restriction in line 11 for this dedicated Writer.

普通 Writer、Agent 和 Broker 仍不能直接修改正式投影；SRC-036 的根绑定、私有暂存、权限证据及失败关闭要求继续适用。\
Ordinary Writer, Agent, and Broker remain barred from directly modifying final projections. SRC-036 requirements for root binding, private staging, permission evidence, and fail-closed behavior continue to apply.

生产身份、真实 Vault 和 Publisher 的既有门禁继续有效。\
Existing gates remain in effect for production identities, the real Vault, and Publisher.

## 执行职责与接口 / Execution Roles and Interface

| 主体 / Principal | 合成环境权限 / Synthetic authority |
| --- | --- |
| Agent | 使用经验证的独立 SID 请求 Agent 区的新建或更新；无目标、暂存及账本直接写权限。<br>Requests creates or updates in Agent scope under a verified distinct SID, with no direct target, staging, or ledger write access. |
| Broker | 从本地连接的真实 Windows Token 验证主体、操作、授权和目标；可拒绝请求及记录审计，不执行正式投影。<br>Verifies principal, operation, grant, and target from a real Windows token on a local connection. May deny and audit requests and has no final projection authority. |
| Secure Writer | 使用与 Broker、Agent 和 Human 不同的已验证 SID；只在独立合成根中预先绑定的 Markdown 目录和事务对象上获得必要权限。<br>Uses a verified SID distinct from Broker, Agent, and Human, with necessary permissions limited to prebound Markdown directories and transaction objects in the isolated synthetic root. |
| Human / Publisher | Human 单独批准 Human 目标和操作，授权绑定 Agent、相对目标、期限、撤销状态及前置版本；Publisher 禁用。<br>Human separately approves Human targets and operations, with grants bound to the Agent, relative target, expiry, revocation status, and prior revision. Publisher is disabled. |

Broker 到 Writer 使用仅允许 Broker SID 接入的独立本地管道；Writer 验证 Broker Token、目标绑定和交接内容，Agent 提供的 SID 不能作为凭证。\
Broker-to-Writer handoff uses a separate local pipe that admits only the Broker SID. Writer verifies the Broker token, target binding, and handoff data. An Agent-supplied SID cannot serve as a credential.

交接须包含已认证主体、操作、幂等键、目标相对路径、预期版本与摘要、请求摘要、授权引用及策略版本；它是内部接口，既有外部 v1 帧和验证约束继续适用。\
Handoff must include the authenticated principal, operation, idempotency key, relative target, expected revision and digest, request digest, grant reference, and policy version. This is an internal interface and existing external v1 frame and validation constraints still apply.

实际测试 SID、单一合成根、有效 ACL 和审计配置须在部署前记录并绑定；本轮未部署这套交接或分配这些身份。\
Actual test SIDs, the single synthetic root, effective ACLs, and audit configuration must be recorded and bound before deployment. This round did not deploy that handoff or assign those identities.

## 提交和恢复 / Commit and Recovery

只允许新建、更新及同类链接维护，提交前重查有效授权、根与父目录身份、目标身份、单链接、重解析点和 SHA-256 前置条件。\
Only create, update, and equivalent link maintenance are allowed. Recheck effective grants, root and parent identity, target identity, single-link and reparse constraints, and SHA-256 preconditions before execution.

沿用 REQUEST_ACCEPTED、VALIDATED、OBJECT_STORED、PREPARED、PROJECTED、COMMITTED；仅核验新投影后才能标记 PROJECTED，业务完成以 SQLite COMMITTED 为准。\
Keep REQUEST_ACCEPTED, VALIDATED, OBJECT_STORED, PREPARED, PROJECTED, and COMMITTED. Mark PROJECTED only after verifying the new projection, and use SQLite COMMITTED for business completion.

撤销或漂移停止新动作；恢复先只读对账，已验证投影补账本，未知投影进入 NEEDS_REVIEW，不重放写入。\
Revocation or drift stops new actions. Recovery starts with read-only reconciliation, completes ledger records for verified projections, and puts unknown projections in NEEDS_REVIEW without replaying writes.

Windows 的 FILE_ID 核验和替换并非原子比较交换；存在等效直写身份且未完成验证时，执行保持关闭。\
Windows FILE_ID verification and replacement do not form atomic compare-and-swap. Execution stays disabled where an equivalent direct writer exists and validation is incomplete.


原文后续 H2 身份迁移试验保留在本地；本节只保留合成严格模式条款。\
The subsequent H2 identity experiment remains local. This copy retains the synthetic Strict mode terms.
