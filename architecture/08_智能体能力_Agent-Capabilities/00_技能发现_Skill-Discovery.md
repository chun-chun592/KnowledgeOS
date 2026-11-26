# Agent 与技能 / Agent and Skills

[返回正式架构 / Architecture entry point](../README.md)

## 发现与组合 / Discovery and Composition

宿主按各自规则加载 SKILL.md，先用描述判断意图，再读取必要流程并组合。Skills 指导流程及检查，MCP、CLI 和原生工具提供实际操作。\
Hosts load SKILL.md through their own discovery rules. Choose by description, then load and combine the relevant instructions. Skills guide process and checks; MCP, CLI, and native tools perform operations.

## 八个入口 / Eight Entries

`knowledgeos` 是可选总路由；`knowledge-query` 找笔记及链接，`knowledge-research` 核对证据并起草，`knowledge-ingest` 处理新来源，`knowledge-synthesis` 综合多源，`knowledge-update` 更新或提案，`knowledge-lint` 只读质检，`knowledge-maintenance` 维护引用、索引、日志及受控恢复。\
`knowledgeos` optionally routes work. `knowledge-query` retrieves notes and links, `knowledge-research` reviews evidence and drafts, `knowledge-ingest` handles new sources, `knowledge-synthesis` combines sources, `knowledge-update` updates or proposes, `knowledge-lint` checks quality, and `knowledge-maintenance` maintains links, indexes, logs, and scoped recovery.

## 接入 / Onboarding

从[仓库 Skills](../../skills)及[宿主接入](../../adapters/README.md)选择所需工作流；权限由 Vault 规则及实际工具能力确定。\
Choose workflows from the [repository Skills](../../skills) and [host adapters](../../adapters/README.md). Vault rules and actual tool capabilities determine the available scope.

[目录命名及三语模板对照 / Localized paths and template mapping](../02_知识架构_Knowledge-Architecture/01_三语目录对照_Localized-Paths.md)
