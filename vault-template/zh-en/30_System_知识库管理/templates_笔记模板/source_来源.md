---
title: "{{title}}"
type: source
owner: agent
created_by: "{{agent_id}}"
created: "{{date}}"
updated: "{{date}}"
status: draft
sources: []
related: []
tags: []
aliases: []
confidence: medium
review_after: ""
---

<!--
SOURCE TEMPLATE → an existing permitted Markdown location in 10_Agent_AI知识库/wiki_整理后的知识
Keep the original under 10_Agent_AI知识库/raw_原始资料/ and link it from this page. Record provenance,
summary, and evidence here. No dedicated sources directory is required.
In an authorized test root, knowledgeos ingest --apply stores the original under
10_Agent_AI知识库/raw_原始资料/documents_文档/ and writes the Source page to the allowed wiki path you supply.
-->

# {{title}}

> What this source is and why it is in the vault.

## Provenance / 出处

| Field | Value |
| --- | --- |
| Author / publisher |  |
| Published |  |
| Retrieved | {{date}} |
| Original location |  |
| Local file | [[]] |
| Version / edition |  |
| Licence / access |  |

## Summary / 摘要

<!-- 5–10 sentences, source-faithful. No full-text paste. -->

## Key points / 要点

1.
2.
3.

## Extracted claims / 提取的主张

| Claim | Anchor (page/section/time) | Type | Used in |
| --- | --- | --- | --- |
|  |  | fact / inference | [[]] |

## Quotes worth preserving / 原文引述

> "…" — p. …

## Reliability / 可靠性

- Peer reviewed?
- Independent replication?
- Conflicts of interest?
- Known corrections?

## Links / 相关链接

- Concept pages: [[]]
- Topic page: [[]]
- Index: [[10_Agent_AI知识库/wiki_整理后的知识/index_知识目录]]

## Open questions / 待解问题

-

## 中文填写说明

在 Wiki 允许的位置记录来源，原件保存在 `10_Agent_AI知识库/raw_原始资料`。获准的测试根运行 knowledgeos ingest --apply 时，原件写入 `10_Agent_AI知识库/raw_原始资料/documents_文档`，Source 页使用调用者指定的 Wiki 路径。摘要注明证据位置、版本及访问限制。可从 [[10_Agent_AI知识库/wiki_整理后的知识/index_知识目录]] 查相关知识。
