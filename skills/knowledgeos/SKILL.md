---
name: knowledgeos
description: Route a KnowledgeOS task across retrieval, source intake, synthesis, updates, lint, or maintenance when the user's request spans multiple workflows.
---

# 知识工作路由 / Knowledge Workflow Routing

先读目标 Vault 的 AGENTS.md，检查宿主可用的 Skills、MCP 和 CLI。\
Read the target vault's AGENTS.md and inspect the host's available Skills, MCP, and CLI.

按需组合 knowledge-query、knowledge-ingest、knowledge-research、knowledge-synthesis、knowledge-update、knowledge-lint 和 knowledge-maintenance。\
Combine knowledge-query, knowledge-ingest, knowledge-research, knowledge-synthesis, knowledge-update, knowledge-lint, and knowledge-maintenance as needed.

先检索及查重，核对来源后优先更新现有笔记；真实库用已批准的原生编辑流程，Human 变更交付提案。\
Search and check for overlap first, then prefer an existing note after reviewing sources. Use the vault's approved native edit workflow and deliver proposals for Human changes.
