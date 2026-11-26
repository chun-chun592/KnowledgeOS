---
name: knowledge-lint
description: Check KnowledgeOS notes for schema, provenance, link, and duplicate-content issues without editing files.
---

# 知识检查 / Knowledge Lint

用 MCP lint_knowledge、CLI inspect 或获准的原生只读检查，核对分类、元数据、来源、歧义、失效链接和重复内容。按需通过任一可用读取工具核实上下文。\
Use MCP lint_knowledge, CLI inspect, or scoped native read-only checks to review classification, metadata, provenance, ambiguity, broken links, and duplicate content. Confirm context with any available read tool.

按类别和相对路径报告发现，区分范围内未解析与已确认失效。此 Skill 只读；按需把获准的 Agent 修复交给 knowledge-update 或 knowledge-maintenance，Human 问题只交付报告或提案。\
Report findings by category and relative path, distinguishing unresolved-in-scope links from confirmed breakage. This Skill is read-only. Hand approved Agent repairs to knowledge-update or knowledge-maintenance as needed, and deliver Human findings as reports or proposals.

从目标库的 AGENTS.md 和现行规范确认目录语言，使用该库实际的相对路径。目录语言不限定笔记正文语言。\
Confirm the layout using the target vault’s AGENTS.md and current rules. Use its actual relative paths. Directory language does not constrain note content.
