# 正式系统架构 / Formal Architecture

本目录按 00 至 14 展示当前正式架构。各模块正文以已发布实现和现行 Markdown Native 协作协议为依据，可选严格模式保留独立契约。\
Modules 00 through 14 describe the current formal architecture, based on the released implementation and Markdown Native collaboration rules. Optional Strict mode retains its separate contracts.

## 当前适用性 / Current Applicability

**日常模式**使用现有 Markdown 目录。Human 与 Agent 是逻辑知识主体，Human 自主管理其内容，Agent 在获准范围内读取、引用并维护 Agent Wiki。Human 变更由本人核对完整 Markdown、diff 与基础 SHA-256 后手工应用。\
**Daily mode** uses the existing Markdown tree. Humans and agents are logical knowledge owners. Humans manage their notes, while agents read, cite, and maintain the Agent wiki within approved scopes. Humans review and apply complete Markdown proposals with a diff and base SHA-256.

宿主按任务选用 Skills，然后选择 MCP、CLI 或原生文件工具。真实库的日常写入走获准的原生文件编辑；MCP 和 CLI 对真实库保持只读。Obsidian 是可选编辑器。\
Hosts select Skills by task and use MCP, CLI, or native file tools as appropriate. Daily real-vault writes use approved native file edits, and MCP and CLI access to the real vault stay read-only. Obsidian is an optional editor.

查重后优先更新原页并核对来源和引用。写共享文件前遵循现有租约、哈希和备份规则，写后定点更新索引并追加日志。测试根的同步可重建托管区块，且保留区块之外的内容。\
Check for overlap, prefer the original page, and verify sources and links. Use the existing leases, hashes, and backups before changing shared files, then update the affected index entries and append the log. Test-root sync can rebuild managed blocks while preserving outside content.

原生动作与外部变化分别记录为 `native_local` 和 `observed_filesystem`。两者不会生成严格模式的 SQLite `COMMITTED`。Markdown 是知识正文的唯一权威。\
Native actions and observed external changes use `native_local` and `observed_filesystem` respectively. They do not generate Strict SQLite `COMMITTED` transactions. Markdown remains authoritative for note content.

**可选严格模式**保留独立 Broker／Writer、IPC、账本、私有暂存与恢复约束。历史材料中的 Windows 身份及服务要求适用于原有候选或独立合成测试；其历史验收状态不等于当前生产批准，也不构成日常运行前置条件。Publisher 禁用。\
**Optional Strict mode** retains the separate Broker and Writer, IPC, ledger, private staging, and recovery requirements. Historical Windows identity and service requirements apply to their original candidates or independent synthetic tests. Their recorded acceptance does not authorize production or impose a daily prerequisite. Publisher is disabled.

## 知识目录 / Knowledge Directory

完整的主体及目录设计见[知识架构](07_知识架构_Knowledge-Architecture/00_模块概述_Module-Overview.md)。下列为现有逻辑分区摘要。\
See [Knowledge Architecture](07_知识架构_Knowledge-Architecture/00_模块概述_Module-Overview.md) for the fuller subject and directory design. The following summarizes the established logical areas.

| 相对目录 / Relative directory | 角色 / Purpose |
| --- | --- |
| `00_Human/` | Human 自主知识；Agent 仅访问获准范围。<br>Human-owned knowledge, with scoped Agent reads. |
| `10_Agent/raw/`, `10_Agent/wiki/` | 原始来源和 Agent 知识；Wiki 包含索引和日志。<br>Original sources and Agent knowledge, with an index and log in the wiki. |
| `20_Exchange/`, `30_System/`, `90_Archive/` | 协作、工作规则和归档。<br>Collaboration, operating rules, and archived material. |

## 模块导航 / Module Navigation

| 模块 / Module | 正文 / Document |
| --- | --- |
| 00 架构总览 / Architecture Overview | [模块概述 / Overview](00_架构总览_Architecture-Overview/00_模块概述_Module-Overview.md) |
| 01 系统架构 / System Architecture | [模块概述 / Overview](01_系统架构_System-Architecture/00_模块概述_Module-Overview.md) |
| 02 身份与安全 / Identity and Security | [模块概述 / Overview](02_身份与安全_Identity-and-Security/00_模块概述_Module-Overview.md) |
| 03 控制平面 / Control Plane | [模块概述 / Overview](03_控制平面_Control-Plane/00_模块概述_Module-Overview.md) |
| 04 数据平面 / Data Plane | [模块概述 / Overview](04_数据平面_Data-Plane/00_模块概述_Module-Overview.md) |
| 05 Broker 与 Writer / Broker and Writer | [模块概述 / Overview](05_Broker与Writer_Broker-and-Writer/00_模块概述_Module-Overview.md) |
| 06 存储与事务 / Storage and Transactions | [模块概述 / Overview](06_存储与事务_Storage-and-Transactions/00_模块概述_Module-Overview.md) |
| 07 知识架构 / Knowledge Architecture | [模块概述 / Overview](07_知识架构_Knowledge-Architecture/00_模块概述_Module-Overview.md) |
| 08 Agent 与技能 / Agent and Skills | [模块概述 / Overview](08_Agent与技能_Agent-and-Skills/00_模块概述_Module-Overview.md) |
| 09 多设备 / Multi-Device | [模块概述 / Overview](09_多设备_Multi-Device/00_模块概述_Module-Overview.md) |
| 10 API 与契约 / API and Contracts | [模块概述 / Overview](10_API与契约_API-and-Contracts/00_模块概述_Module-Overview.md) |
| 11 状态机 / State Machines | [模块概述 / Overview](11_状态机_State-Machines/00_模块概述_Module-Overview.md) |
| 12 测试与验收 / Testing and Acceptance | [模块概述 / Overview](12_测试与验收_Testing-and-Acceptance/00_模块概述_Module-Overview.md) |
| 13 部署 / Deployment | [模块概述 / Overview](13_部署_Deployment/00_模块概述_Module-Overview.md) |
| 14 架构决策 / Architecture Decisions | [ADR-01 至 ADR-06](14_架构决策_Architecture-Decisions/00_架构决策登记_Architecture-Decision-Register.md) · [ADR-04 补充 / Addendum](14_架构决策_Architecture-Decisions/02_ADR04补充安全投影_ADR04-Secure-Projection-Addendum.md) |

## 安装、分发与来源 / Setup, Distribution, and Attribution

项目按标准 Python 包安装，严格模式使用可选 Windows 依赖。入口见[项目 README](../README.md)、[宿主适配](../adapters/README.md)、[配置示例](../config/knowledgeos.example.toml)和[日常示例](../examples/README.md)。\
The project installs as a standard Python package, with optional Windows dependencies for Strict mode. See the [project README](../README.md), [host adapters](../adapters/README.md), [configuration sample](../config/knowledgeos.example.toml), and [everyday examples](../examples/README.md).

产品版本与 Core 来源版本分开维护。Agent Kit 0.1.1 提供继承的 Core、索引渲染和分段编辑代码；沿用既有 MIT 声明。\
The product version is tracked separately from the Core source version. Agent Kit 0.1.1 provides the inherited Core, index rendering, and section editing code under its retained MIT notice. [LICENSE](../LICENSE)

知识结构与工作流承接 SRC-011、012、014–021；可选严格投影承接 SRC-006–010、028–031、036–037、039–040 中仍适用的契约。原文、设计摘录、候选集成方案及逐文件来源清单可在此前的架构发布提交中追溯，本地原件保留。\
The knowledge schema and workflows draw from SRC-011, 012, and 014–021. Optional Strict projection retains the applicable contracts from SRC-006–010, 028–031, 036–037, and 039–040. The prior architecture publication commit retains the source text, design excerpts, candidate integration plans, and file-level provenance. Local originals remain in place.

本次仅整理文档。历史候选状态不变，未产生新的测试验收结论。\
This is a documentation update. Historical candidate statuses remain in their original scope, and no new runtime acceptance results are claimed.
