> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../README.md) for current applicability.

# Skills集成方案 / Skills Integration Plan

本方案供评审，现有 Skills 工作流、角色和 Writer 权限仍以封存架构为准。\
This plan is for review. Existing Skills workflows, roles, and Writer permissions remain governed by the frozen architecture.

## 发现与动态加载 / Discovery and Dynamic Loading

仅从经批准的技能目录或宿主注册表读取 name、description 与版本信息，按需加载主体和声明的参考资料。\
Read name, description, and version metadata from approved skill catalogs or host registries, then load the body and declared references on demand.

使用固定来源、版本和哈希识别技能，拒绝重名且无法确认优先级的定义、越界引用和未经批准的脚本。\
Identify a skill by its pinned source, version, and hash. Reject definitions with unresolved naming precedence, out-of-scope references, and unapproved scripts.

[Agent Skills 规范 / Agent Skills specification](https://agentskills.io/specification) · [session-start](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/hooks/session-start#L22-L87) · [marketplace.json](https://github.com/obsidianmd/obsidian-skills/blob/b110b2f8e9eb1f287892f937050dfd40af862cbb/.claude-plugin/marketplace.json) · [skill-install.ts](https://github.com/inkeep/open-knowledge/blob/cfee15dc8e7aaae0fb8579bbd3e73b91b41a8de1/packages/server/src/skill-install.ts#L60-L100)

## 路由、选择与组合 / Routing, Selection, and Composition

将请求映射到既有 ingest、query、update、synthesis 或 lint，并记录选用理由、输入来源、要求的权限和输出边界。\
Map requests to existing ingest, query, update, synthesis, or lint operations and record the selection reason, input provenance, required permissions, and output boundaries.

组合采用读取来源、生成候选、检查格式与引用、按既定授权提交的顺序。\
Compose workflows in the order of reading sources, preparing a candidate, checking format and citations, and submitting under existing authorization.

将独立复核用于发现缺失来源或未授权变更，任何写请求仍通过现有受控 Writer。\
Use independent review to spot missing sources or unauthorized changes. Route every write request through the existing controlled Writer.

[Agent 与技能 / Agent and Skills](../08_Agent%E4%B8%8E%E6%8A%80%E8%83%BD_Agent-and-Skills/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [Broker 与 Writer / Broker and Writer](../05_Broker%E4%B8%8EWriter_Broker-and-Writer/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [SKILL.md](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development/SKILL.md) · [test-subagent-driven-development.sh](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/tests/claude-code/test-subagent-driven-development.sh) · [SKILL.md](https://github.com/AgriciDaniel/claude-obsidian/blob/2e545563172f97f02ecaaaab376ceea1246a0583/skills/wiki-ingest/SKILL.md) · [lint_engine.py](https://github.com/AgriciDaniel/claude-obsidian/blob/2e545563172f97f02ecaaaab376ceea1246a0583/claude_obsidian/lint_engine.py)

## Hooks、错误、重试与验收 / Hooks, Errors, Retries, and Acceptance

启动钩子可提供受控技能目录，文件事件仅生成候选或触发派生索引刷新。\
A startup hook may expose a controlled skill catalog. File events only produce candidates or trigger derived-index refreshes.

仅读错误在批准的瞬态分类内可限次重试，授权拒绝与契约冲突转人工，提交结果未知时先对账。\
Retry read-only failures within approved transient classifications and bounds. Send authorization denies and contract conflicts to a human, and reconcile before retrying an unknown commit outcome.

验收样例覆盖路由歧义、技能未注册、组合中断、重复事件、权限拒绝以及恢复后不会重复发布。\
Acceptance cases cover ambiguous routing, unregistered skills, interrupted composition, duplicate events, permission denial, and recovery without duplicate publication.

[状态机 / State Machines](../11_%E7%8A%B6%E6%80%81%E6%9C%BA_State-Machines/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [hook_adapter.py](https://github.com/AgriciDaniel/claude-obsidian/blob/2e545563172f97f02ecaaaab376ceea1246a0583/claude_obsidian/hook_adapter.py) · [SKILL.md](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging/SKILL.md) · [test_watch_coordinator.py](https://github.com/basicmachines-co/basic-memory/blob/8d002c93fd5d68fbb9690c6de9b90792040dce1c/tests/index/test_watch_coordinator.py)
