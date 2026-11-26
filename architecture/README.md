# KnowledgeOS 正式架构 / Formal Architecture

KnowledgeOS 将 Human 自主笔记和 Agent 知识编译置于同一 Markdown 文件系统。正文是唯一知识事实来源，索引、日志及备份辅助检索、维护和追溯。\
KnowledgeOS brings Human-authored notes and Agent knowledge compilation into one Markdown tree. Note text is authoritative. Indexes, logs, and backups support retrieval, maintenance, and provenance.

默认工作方式为 Markdown Native。Obsidian 可选，宿主按任务选择 Skills、MCP、CLI 或原生文件工具。真实库 MCP／CLI 只读，获准 Agent 修改按库内原生编辑协议执行。\
Markdown Native is the daily workflow. Obsidian is optional. Hosts choose Skills, MCP, CLI, or native tools. Real-vault MCP and CLI stay read-only, with approved Agent writes following the vault’s native editing rules.

[总体架构图 / System diagram](00_架构总览_Architecture-Overview/01_组件与数据流_Components-and-Data-Flow.md) · [完整知识目录 / Knowledge tree](02_知识架构_Knowledge-Architecture/00_知识目录_Knowledge-Layout.md) · [可复用模板 / Reusable template](../vault-template/README.md)

| 编号 / No. | 正式模块 / Module |
| --- | --- |
| 00 | [架构总览 / Overview](00_架构总览_Architecture-Overview/00_模块概述_Module-Overview.md) |
| 01 | [设计来源 / Design References](01_设计来源_Design-References/00_原始设计与取舍_Origins-and-Decisions.md) |
| 02 | [知识架构 / Knowledge Architecture](02_知识架构_Knowledge-Architecture/00_知识目录_Knowledge-Layout.md) |
| 03 | [人类知识 / Human Knowledge](03_人类知识_Human-Knowledge/00_目录与知识地图_Directories-and-Maps.md) |
| 04 | [智能体知识 / Agent Knowledge](04_智能体知识_Agent-Knowledge/00_原始资料与知识编译_Raw-and-Knowledge-Compilation.md) |
| 05 | [知识协作 / Knowledge Collaboration](05_知识协作_Knowledge-Collaboration/00_主体协作与提案_Ownership-and-Proposals.md) |
| 06 | [知识工作流 / Knowledge Workflows](06_知识工作流_Knowledge-Workflows/00_知识生命周期_Knowledge-Lifecycle.md) |
| 07 | [知识规范 / Knowledge Schema](07_知识规范_Knowledge-Schema/00_元数据及链接_Metadata-and-Links.md) |
| 08 | [智能体能力 / Agent Capabilities](08_智能体能力_Agent-Capabilities/00_技能发现_Skill-Discovery.md) |
| 09 | [工具接口 / Tool Interfaces](09_工具接口_Tool-Interfaces/00_接口与能力_Interfaces-and-Capabilities.md) |
| 10 | [存储与维护 / Storage and Maintenance](10_存储与维护_Storage-and-Maintenance/00_存储与派生数据_Storage-and-Projections.md) |
| 11 | [多设备与多智能体 / Multi-Device and Agent](11_多设备与多智能体_Multi-Device-and-Agent/00_多设备与多主体_Multi-Device-and-Agent.md) |
| 12 | [治理与安全 / Governance and Security](12_治理与安全_Governance-and-Security/00_治理边界_Governance-Boundary.md) |
| 13 | [安装与接入 / Deployment](13_安装与接入_Deployment/00_安装与宿主_Setup-and-Hosts.md) |
| 14 | [架构决策 / Architecture Decisions](14_架构决策_Architecture-Decisions/00_架构决策登记_Architecture-Decision-Register.md) |

严格模式是单独配置的合成能力，不是日常依赖。Human 自动写入和 Publisher 保持关闭。\
Strict mode is a separately configured synthetic capability and is optional for daily use. Automatic Human writes and Publisher remain disabled.
