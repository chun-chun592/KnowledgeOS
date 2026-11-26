---
name: knowledge-query
description: Search approved KnowledgeOS scopes, read notes, inspect properties and tags, and trace relationships before synthesis.
---

# 查询知识 / Knowledge Query

先检查获准的导航、标题及别名，以精确词和同义词检索。按需扩大到正文、来源及反向引用。\
Start with authorized indexes, titles, and aliases. Search exact terms and synonyms, then broaden to bodies, sources, and backlinks as needed.

MCP 可用时，可选择 search_knowledge、read_markdown、note_metadata、query_tags、knowledge_links。无 MCP 时，以 CLI query／inspect 或获准的原生搜索和读取完成等效检查；原生工具可直接核对 frontmatter、SHA-256 和链接。\
When MCP is available, choose search_knowledge, read_markdown, note_metadata, query_tags, or knowledge_links as appropriate. Otherwise use CLI query or inspect, or scoped native search and reading. Native tools can check frontmatter, SHA-256, and links directly.

跨主体检索时分别查看获准的 Human 和 Agent 范围；工具支持主体筛选时再使用该参数。标识主体、相对路径、覆盖范围和缺口。空结果仅代表已搜索范围。\
Search authorized Human and Agent scopes separately for cross-subject questions and use a subject parameter where supported. Report subject, relative path, coverage, and gaps. Empty results apply only to the scope searched.
