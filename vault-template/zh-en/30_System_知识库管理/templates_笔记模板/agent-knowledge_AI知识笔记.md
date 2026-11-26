---
title: "{{title}}"
type: concept
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
GENERIC AGENT KNOWLEDGE TEMPLATE.
Before use: (1) search the wiki for synonyms and aliases, (2) choose the type and matching directory,
(3) fill created_by with your real agent id. Schema: [[30_System_知识库管理/schemas_笔记格式规范/frontmatter.schema.json]].
Delete sections that do not apply; never leave placeholder text in a saved page.
-->

# {{title}}

> One-sentence definition, claim or decision.

## Summary / 摘要

<!-- 2–4 sentences a reader can use without opening the sources. -->

## Body / 正文

事实 / Fact: <!-- directly supported claim; link the actual Source page and cite page or section -->

推断 / Inference: <!-- conclusion derived from evidence; state the basis -->

观点 / Opinion: <!-- value judgement; state the position and why -->

## Boundaries / 适用边界

- Applies when:
- Does not apply when:
- Known failure modes:

## Related / 相关知识

- [[10_Agent_AI知识库/wiki_整理后的知识/index_知识目录]]

## Open questions / 待解问题

-

## Sources / 来源

- <!-- link the actual Raw original or external source URL -->

## Contribution log / 贡献记录

- {{date}} · {{agent_id}} · created

## 中文填写说明

遵循 [[30_System_知识库管理/schemas_笔记格式规范/frontmatter.schema.json]]。保留证据位置并区分事实、推断和观点，相关知识见 [[10_Agent_AI知识库/wiki_整理后的知识/index_知识目录]]。
