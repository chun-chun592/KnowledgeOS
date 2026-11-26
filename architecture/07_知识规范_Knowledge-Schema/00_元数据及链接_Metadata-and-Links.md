# 元数据及链接 / Metadata and Links

Agent 知识使用 YAML 字段 title、type、owner、created_by、created、updated、status、sources、related、tags；保留原创建者及来源。时间字段使用 ISO 日期，证据不足时不能标 verified。查看[模板 Schema](../../vault-template/30_System/schemas/frontmatter.schema.json)。\
Agent notes use YAML fields title, type, owner, created_by, created, updated, status, sources, related, and tags. Retain original authorship and sources. Use ISO dates and reserve verified for supported claims. See the [template schema](../../vault-template/30_System/schemas/frontmatter.schema.json).

来源可以是原件、稳定 URL 或库内路径。引用优先采用可解析的相对 Markdown 链接或 WikiLink，歧义时用更完整路径。作用域外目标不可见不代表其不存在。\
Sources can be originals, stable URLs, or vault-relative paths. Prefer resolvable relative Markdown links or wikilinks. Use fuller paths to resolve ambiguity. An unseen out-of-scope target may still exist.

模板提供页面骨架，验证还须核对来源真实性、事实与推断区分、内容重复、失效关联与状态是否过期。Human 笔记可使用不同字段。\
Templates provide structure. Validation also checks provenance, separates facts from inference, and reviews duplication, broken links, and stale status. Human notes may use different fields.
