# 知识架构 / Knowledge Architecture

[返回正式架构 / Architecture entry point](../README.md)

## 目录契约 / Directory Contract

`00_Human/` 保存 Human 内容，`10_Agent/raw/` 保留原始来源，`10_Agent/wiki/` 保存知识笔记、index.md 与 log.md。`20_Exchange/` 协作，`30_System/` 记录治理，`90_Archive/` 保存归档。保留现有目录和历史命名。\
`00_Human/` is Human content, `10_Agent/raw/` keeps originals, and `10_Agent/wiki/` holds notes, index.md, and log.md. `20_Exchange/` supports collaboration, `30_System/` holds governance, and `90_Archive/` retains archival material. Preserve existing layout and names.

## Schema 与证据 / Schema and Evidence

知识页保留 title、type、owner、created_by、created、updated、status、sources、related 与 tags。索引把 concept、entity、topic、comparison、synthesis、project、decision 和 source 分组。未经核验的推断与确定的来源陈述分开。\
Notes retain title, type, owner, created_by, created, updated, status, sources, related, and tags. The index groups concept, entity, topic, comparison, synthesis, project, decision, and source pages. Separate unverified inference from supported statements.

状态包括 draft、verified、needs-review、outdated 与 archived。编辑保留原创建者和来源；归档以状态变更保留原路径。CLI 测试根摄取按内容哈希保存原始资料，并建立指向原件的来源页。\
Statuses include draft, verified, needs-review, outdated, and archived. Edits retain original authorship and provenance. Soft archive changes status while preserving the path. CLI test-root intake stores originals by content hash and creates a linked source page.

## 检索与引用 / Retrieval and References

先搜索同义词和相邻主题，再读来源、综合并更新原页。MCP 解析相对 Markdown 链接和 WikiLink，反链依据当前读取范围计算；范围外不可见不等于链接目标不存在。\
Search synonyms and related topics, then read evidence, synthesize, and update existing notes. MCP resolves relative Markdown links and wikilinks, with backlinks calculated in the visible scope. An out-of-scope target may still exist.
