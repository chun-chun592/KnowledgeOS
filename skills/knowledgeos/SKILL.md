---
name: knowledgeos
description: Route a KnowledgeOS task across retrieval, source intake, synthesis, updates, lint, or maintenance when the user's request spans multiple workflows.
---

# 知识工作路由 / Knowledge Workflow Routing

先读目标 Vault 的 AGENTS.md，检查宿主可用的 Skills、MCP 和 CLI。\
Read the target vault's AGENTS.md and inspect the host's available Skills, MCP, and CLI.

已批准的原生文件读取可用于无 MCP 的宿主。分别选择真实库原生编辑、独立 Native 测试工具和可选严格模式流程。\
Approved native reading works in hosts without MCP. Choose the relevant workflow for real-vault native edits, independent Native test tools, or optional Strict mode.

按需组合 knowledge-query、knowledge-ingest、knowledge-research、knowledge-synthesis、knowledge-update、knowledge-lint 和 knowledge-maintenance。\
Combine knowledge-query, knowledge-ingest, knowledge-research, knowledge-synthesis, knowledge-update, knowledge-lint, and knowledge-maintenance as needed.

先检索及查重，核对来源后优先更新现有笔记；真实库用已批准的原生编辑流程，Human 变更交付提案。\
Search and check for overlap first, then prefer an existing note after reviewing sources. Use the vault's approved native edit workflow and deliver proposals for Human changes.

先从 AGENTS.md 与实际目录识别知识主体和模式，再按任务按需组合 Skills。已知任务可以直接选择相应 Skill。\
Identify the knowledge owners and mode from AGENTS.md and the actual tree, then combine Skills as needed. A known task can use its relevant Skill directly.

从目标库的 AGENTS.md 和现行规范确认目录语言，使用该库实际的相对路径。目录语言不限定笔记正文语言。\
Confirm the layout using the target vault’s AGENTS.md and current rules. Use its actual relative paths. Directory language does not constrain note content.
