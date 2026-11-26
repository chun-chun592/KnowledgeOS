# 原始设计与取舍 / Origins and Decisions

原始架构 SRC-002 与 SRC-012 明确采用 LLM Wiki 的 Raw、Wiki、Schema、Index 与 Log，并把 Human 笔记留在自己的组织体系中。SRC-011 和 SRC-014–021补充 Schema 与路由工作流。\
Original designs SRC-002 and SRC-012 explicitly adopt LLM Wiki’s Raw, Wiki, Schema, Index, and Log while keeping Human notes in their own organization system. SRC-011 and SRC-014–021 add schema and routing workflows.


| 参考 / Reference | 实际关系 / Observed relationship |
| --- | --- |
| [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | 直接设计来源：保留原件并持续编译可引用的知识，索引及日志保留导航和演进。KnowledgeOS 自主增加双主体和提案边界。<br>Direct design source for immutable originals, compiled knowledge, navigation, and evolution. KnowledgeOS adds its dual ownership and proposal boundary. |
| [Kepano / Bottom-up](https://stephango.com/vault) | 对照参考：个人笔记及链接可先形成，再按使用演进。原始资料未证实移植其模板、插件或字段。<br>Comparison for notes and links evolving bottom-up. The original evidence does not establish adoption of his templates, plugins, or fields. |
| [PARA](https://fortelabs.com/blog/para/)、[Zettelkasten](https://zettelkasten.de/introduction/)、MOC | 早期设计注明兼容。Projects、Areas、Resources、Archive 对应 PARA 式职责；Literature、Permanent-Notes 与概念链接支持 Zettelkasten 式使用；MOCs 是人工导航。命名、ID 体系和专用应用由 Human 自选。<br>Explicitly compatible in the early design. Projects, Areas, Resources, and Archive correspond to PARA-style roles. Literature, permanent notes, and concept links support Zettelkasten-style use. MOCs are curated maps. Naming, ID schemes, and apps remain user choices. |
| [Ar9av / Obsidian Wiki](https://github.com/Ar9av/obsidian-wiki) | Agent Kit README 已列为来源，未证实直接集成；Obsidian Mind 名称未在已核对的来源中唯一定位，因此不作采用判断。<br>Agent Kit credits this reference without establishing direct integration. “Obsidian Mind” could not be uniquely matched in the reviewed source record, so no adoption is claimed. |

## 已研究的实现 / Studied Implementations

| 项目 / Project | 对照与取舍 / Comparison and decision |
| --- | --- |
| [Basic Memory](https://github.com/basicmachines-co/basic-memory/tree/8d002c93fd5d68fbb9690c6de9b90792040dce1c) | 参考 Markdown、检索及关系的分层；未接入其数据库、watcher 或写入能力。<br>Reference for Markdown, search, and relations. No integration of its database, watcher, or writes. |
| [Superpowers](https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7) · [Agent Skills](https://agentskills.io/specification) | 参考发现、组合和渐进式披露，保持独立任务 Skills；未复制强制流程或调度器。<br>Reference for discovery, composition, and progressive disclosure. Task Skills stay independent, without adopting a mandatory workflow or scheduler. |
| [Claude Obsidian](https://github.com/AgriciDaniel/claude-obsidian/tree/2e545563172f97f02ecaaaab376ceea1246a0583) | 对照摄取、出处、质量和事务；未引入 hooks、事务引擎或宿主绑定。<br>Comparison for intake, provenance, quality, and transactions. Its hooks, engine, and host binding are not integrated. |
| [Obsidian 官方 Skills](https://github.com/obsidianmd/obsidian-skills/tree/b110b2f8e9eb1f287892f937050dfd40af862cbb) | 对照 properties、链接和附件；不依赖 Obsidian CLI、Headless 或插件。<br>Comparison for properties, links, and attachments. The project does not depend on Obsidian CLI, Headless, or plugins. |
| [Open Knowledge](https://github.com/inkeep/open-knowledge/tree/cfee15dc8e7aaae0fb8579bbd3e73b91b41a8de1) | 对照 MCP 工具、反向索引、审计与 Skill 安装；不引入其桌面端或服务平台。<br>Reference for MCP, backlinks, audit, and Skill installation. Its desktop app and service platform are not used. |
| [Lacuna Wiki](https://github.com/Labhund/lacuna-wiki/tree/b7aadcb29dae0e66725dcf40ee005c6152aae36d) | 对照资料研究、主张与关联；不引入 daemon、同步或独立索引。<br>Comparison for research, claims, and relationships. Its daemon, sync, and separate index are not used. |

第三方链接用于溯源，未复制其代码或私人示例。实际继承的 Agent Kit Core 0.1.1 保留 [MIT 许可证](../../LICENSE)。正式架构历史可在 Git 基线 d859290 及本地原始资料追溯。\
Third-party links record provenance. Their code and private examples are not copied. The inherited Agent Kit Core 0.1.1 retains its [MIT license](../../LICENSE). Earlier architecture evidence remains traceable in Git baseline d859290 and the local originals.
