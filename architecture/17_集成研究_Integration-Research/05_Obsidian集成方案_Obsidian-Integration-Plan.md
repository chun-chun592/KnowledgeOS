> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../README.md) for current applicability.

# Obsidian集成方案 / Obsidian Integration Plan

保留真实 Vault、当前目录契约和 Markdown 内容语义，采用离线测试夹具验证格式兼容。\
Preserve the real Vault, existing directory contract, and Markdown content semantics, using offline fixtures to check compatibility.

## Properties、链接与附件 / Properties, Links, and Attachments

夹具覆盖 YAML Properties 的类型和未知字段保留，以及 wikilink 别名、标题、区块、反链和相对附件嵌入。\
Fixtures cover YAML Property types, retention of unknown fields, and wikilink aliases, headings, blocks, backlinks, and relative attachment embeds.

在重名、大小写差异、Unicode 和附件缺失时记录歧义，保持既有解析与 Writer 权限边界。\
Report ambiguity for duplicate names, casing differences, Unicode, and missing attachments while preserving existing resolution and Writer permission boundaries.

[知识架构 / Knowledge Architecture](../07_%E7%9F%A5%E8%AF%86%E6%9E%B6%E6%9E%84_Knowledge-Architecture/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [SKILL.md](https://github.com/obsidianmd/obsidian-skills/blob/b110b2f8e9eb1f287892f937050dfd40af862cbb/plugins/obsidian/skills/obsidian-markdown/SKILL.md) · [PROPERTIES.md](https://github.com/obsidianmd/obsidian-skills/blob/b110b2f8e9eb1f287892f937050dfd40af862cbb/plugins/obsidian/skills/obsidian-markdown/references/PROPERTIES.md) · [EMBEDS.md](https://github.com/obsidianmd/obsidian-skills/blob/b110b2f8e9eb1f287892f937050dfd40af862cbb/plugins/obsidian/skills/obsidian-markdown/references/EMBEDS.md) · [backlink-index.ts](https://github.com/inkeep/open-knowledge/blob/cfee15dc8e7aaae0fb8579bbd3e73b91b41a8de1/packages/server/src/backlink-index.ts)

## CLI、Headless 与后台索引 / CLI, Headless, and Background Indexing

只读 CLI 可作兼容性对照；会写入笔记或设置的 CLI 命令及 Headless 同步不进入本方案的初期试验。\
Read-only CLI commands may serve as compatibility references. CLI commands that change notes or settings and Headless Sync are outside this initial trial.

派生索引重建从获准的快照读取，按现有提交和修订边界发布，并保留重建测试证据。\
A derived-index rebuild reads an authorized snapshot, publishes within existing commit and revision boundaries, and retains rebuild test evidence.

任何未来同步启用须明确离线编辑、重放、冲突归属和关闭机制，经 ADR 评审后仍使用受控 Writer。\
Future synchronization activation requires explicit offline-edit, replay, conflict-ownership, and shutdown semantics. It still uses the controlled Writer after ADR review.

[多设备 / Multi-Device](../09_%E5%A4%9A%E8%AE%BE%E5%A4%87_Multi-Device/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [存储与事务 / Storage and Transactions](../06_%E5%AD%98%E5%82%A8%E4%B8%8E%E4%BA%8B%E5%8A%A1_Storage-and-Transactions/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [数据平面 / Data Plane](../04_%E6%95%B0%E6%8D%AE%E5%B9%B3%E9%9D%A2_Data-Plane/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [SKILL.md](https://github.com/obsidianmd/obsidian-skills/blob/b110b2f8e9eb1f287892f937050dfd40af862cbb/plugins/obsidian/skills/obsidian-cli/SKILL.md) · [SKILL.md](https://github.com/obsidianmd/obsidian-skills/blob/b110b2f8e9eb1f287892f937050dfd40af862cbb/plugins/obsidian/skills/obsidian-headless/SKILL.md) · [test_search_refresh_atomicity.py](https://github.com/basicmachines-co/basic-memory/blob/8d002c93fd5d68fbb9690c6de9b90792040dce1c/tests/services/test_search_refresh_atomicity.py#L60-L166) · [sync.py](https://github.com/Labhund/lacuna-wiki/blob/b7aadcb29dae0e66725dcf40ee005c6152aae36d/src/lacuna_wiki/daemon/sync.py#L44-L206) · [Obsidian CLI](https://obsidian.md/help/cli) · [Obsidian Headless](https://obsidian.md/help/headless)
