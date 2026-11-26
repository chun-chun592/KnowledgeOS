# 主体协作与提案 / Ownership and Proposals

Human 掌管 Human 区。Agent 可在获准范围读取并引用 Human 内容，维护共享 Agent Wiki，保留创建者及来源。Human 可利用 Agent 知识及引用追溯证据。\
Humans own Human content. Agents can read and cite approved Human scopes and maintain the shared Agent wiki, retaining authorship and provenance. Humans can use Agent knowledge and trace its evidence.

Human 笔记变更只提交目标、理由、原始 SHA-256、完整 Markdown 与 diff。Human 核对基线后用任意编辑器应用；哈希不匹配则重新生成提案。\
For a Human change, deliver the target, rationale, base SHA-256, full Markdown, and diff. Humans apply it in any editor after checking the baseline. If the hash differs, regenerate the proposal.

共享编辑使用租约和备份，保存前核对哈希，冲突时重新读取、比较并人工决定。索引定点更新，日志追加。详细过程见[并发与交接](Concurrency/00_租约与交接_Leases-and-Handoff.md)。\
Shared edits require a lease and backup. Recheck the hash before saving, and reread and review conflicts. Update index entries in place and append to the log. See [leases and handoff](Concurrency/00_租约与交接_Leases-and-Handoff.md).

[租约、冲突与交接 / Leases, Conflicts, and Handoff](Concurrency/00_租约与交接_Leases-and-Handoff.md)

[目录命名及三语模板对照 / Localized paths and template mapping](../02_知识架构_Knowledge-Architecture/01_三语目录对照_Localized-Paths.md)
