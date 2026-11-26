# 知识工作流 / Knowledge Workflow

## 检索、摄取与编译 / Query, Intake, and Compilation

先查导航、标题、别名及来源，在[主体规则](../policies/ownership-and-permissions.md)允许的范围内定位相关页面。临时研究直接返回；值得复用的成果按现有授权保存。\
Start with indexes, titles, aliases, and sources within the [ownership rules](../policies/ownership-and-permissions.md). Return temporary findings directly and save reusable work within existing authorization.

按来源标识和 SHA-256 查重，将获准的原件保留在 `10_Agent/raw/`，用 [Source 模板](../templates/source.md) 在 Wiki 记录出处、摘要、证据和原件链接。按内容决定引用、补充、更新或新建；保留冲突证据及其适用范围。\
Check source identifiers and SHA-256 for duplicates. Keep approved originals under `10_Agent/raw/` and use the [Source template](../templates/source.md) to record provenance, summary, evidence, and the original-file link in the wiki. Cite, extend, update, or create as the material warrants. Preserve conflicting evidence and its scope.

## Agent 原生编辑 / Agent Native Editing

1. 依照 [Schema](../schemas/frontmatter.schema.json) 选择类型。新建前确认目标不存在，更新时保留有效来源及原作者。\
   Choose the type using the [schema](../schemas/frontmatter.schema.json). For new notes, confirm the target is absent. For updates, preserve valid sources and original authorship.
2. 每个待改文件分别取得租约，索引和日志也适用。将目标相对路径中的斜线和点替换为短横线并追加 `.lock.md`，在[租约目录](../../20_Exchange/agent-to-agent/locks/)检查同名文件。无锁时写入 `lock: true`、`path`、`owner`、`acquired`、`expires`、`intent`，重读确认持有人和有效期。遇到活动租约时等待或交接；陈旧锁按现行规则及 Human 确认处理。该约定存在竞争窗口。\
   Lease each affected file, including the index and log. Replace slashes and dots in its relative path with hyphens and append `.lock.md`, then check the [lease directory](../../20_Exchange/agent-to-agent/locks/) for that name. If clear, record `lock: true`, `path`, `owner`, `acquired`, `expires`, and `intent`, then reread to confirm ownership and expiry. Wait or hand off an active lease. Handle stale leases under local rules with Human confirmation. This cooperative convention has a race window.
3. 保存旧文件的原始字节与 SHA-256。新模板库如未另设备份位置，可在 `.knowledgeos/backups/` 以唯一操作标识建子目录，按目标相对路径保存并记录备份路径和哈希。写前再次核对租约及基线，新文件再次检查不存在。冲突时停止、重读和比较，从新的基线重做。恢复时核对备份哈希，把恢复作为获准的原生更新，先保存并核对当前版本。\
   Retain exact prior bytes and their SHA-256. A new template vault without a configured backup location can use a unique operation directory under `.knowledgeos/backups/`, keeping the target relative path and recording the backup path and digest. Before saving, recheck the lease and baseline, or confirm absence for a new file. On conflict, stop, reread, and compare before retrying from a fresh baseline. For recovery, verify the backup digest and treat restoration as an approved native update, first preserving and checking the current version.
4. 重读结果并核对哈希与引用。定点更新[索引](../../10_Agent/wiki/index.md)，保留其他条目、分组和顺序；[日志](../../10_Agent/wiki/log.md)只追加已核实的操作、路径、哈希与结果。同步中断时先核对实际状态，再补遗漏的记录。完成后只释放自己持有的租约。\
   Reread the result and verify its digest and links. Update affected [index](../../10_Agent/wiki/index.md) entries in place, preserving other entries, groups, and order. Append only verified actions, paths, digests, and outcomes to the [log](../../10_Agent/wiki/log.md). After interrupted synchronization, reconcile actual state before filling in missing records. Release only your own leases when finished.

## Human 提案与交接 / Human Proposals and Handoffs

Human 修改交付[提案](../templates/human-change-proposal.md)，附基础哈希、完整 Markdown 与 diff，由 Human 手工应用。用[交接模板](../templates/handoff.md)记录任务、相对路径、证据、未决问题和租约。接手者先读日志，再核对授权、基线和租约。\
Deliver Human changes as [proposals](../templates/human-change-proposal.md) with the base digest, full Markdown, and diff for manual application. Use the [handoff template](../templates/handoff.md) to record the task, relative paths, evidence, open issues, and leases. The recipient reads the log and rechecks authorization, baselines, and leases.
