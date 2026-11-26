# 知识生命周期 / Knowledge Lifecycle

[返回正式架构 / Architecture entry point](../README.md)

## 日常知识流转 / Daily Knowledge Flow

检索与查重 → 核对来源 → 草稿或变更计划 → 核对主体与权限 → 更新原页或必要时新增 → 重读正文与链接 → 同步受影响的索引和日志。Human 私有与已有公共知识变更先提交可审查提案，获具体批准后按原生协议执行。\
Search and deduplicate → verify sources → draft or plan → check owner and scope → update or create when needed → reread content and links → sync the affected index and log. Human and existing Shared changes require a reviewable proposal and exact approval before native execution.

## Native 状态 / Native States

独立测试根工具重查 SHA-256 后写入，并备份基线。NATIVE_APPLIED 表示写入和同步完成，NATIVE_SYNC_PENDING 表示正文已变而派生文件待核对；应先重读文件再同步。外部编辑的最终状态通过 observed_filesystem 记录。\
Native test tools back up the base and recheck SHA-256 before writing. NATIVE_APPLIED includes sync. NATIVE_SYNC_PENDING indicates content changed while projections need reconciliation; reread before syncing. External final state is recorded as observed_filesystem.

## 严格状态 / Strict States

严格事务以 PREPARED、投影核验、COMMITTED 或 NEEDS_REVIEW 等证据判定。响应丢失先查原幂等键。崩溃恢复仅补核验过的投影；不明确状态不视为成功。\
Strict transactions use evidence such as PREPARED, verified projection, COMMITTED, or NEEDS_REVIEW. Query the original idempotency key after a lost response. Recovery finalizes verified projections only; uncertainty is not success.

PREPARED 包含旧内容、暂存、目标和父目录证据；仅状态为 PREPARED 无法证明替换是否发生。若路径缺失、文件身份不明、摘要相同但身份不同或证据冲突，保留现场供复核，不覆盖或重试。\
PREPARED records old content, staging, target, and parent evidence. The PREPARED state alone cannot prove whether replacement occurred. Preserve missing paths, unknown identities, matching hashes with different identities, or conflicting evidence for review without overwriting or retrying.

[目录命名及三语模板对照 / Localized paths and template mapping](../02_知识架构_Knowledge-Architecture/01_三语目录对照_Localized-Paths.md)

先查重和核对共享许可，再决定新增公共知识。索引追加条目，日志记录事件；已有公共页的反链由检索动态计算。
