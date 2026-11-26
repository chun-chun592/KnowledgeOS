## KnowledgeOS v0.1.5 权限

Human 和 Agent 是两个知识主体。Human 私有、Agent 私有及公共知识是三个知识区域。公共知识仅供库内协作，外部发布需另行授权。

| Agent 操作 | Human 私有 | Agent 私有 | 公共知识 |
| --- | --- | --- | --- |
| 搜索、读取、引用 | 明确开放范围 | 自主 | 自主 |
| 新增 | 具体批准 | 自主 | 自主创建原先不存在的路径 |
| 修改、删除、移动、改名、归档、恢复 | 具体批准 | 自主 | 具体批准 |

Agent 自主维护所获准的私有知识。保留 Raw 原件及后续版本的追溯关系，普通知识优先使用可恢复归档或软删除。移动须满足来源与目标权限，归档保留原归属。作者登记用于署名，操作权限依据获准的知识区域。

公共新增只可补入新条目的索引、日志、该新页中的链接和可重建统计。保留已有笔记、索引条目及日志历史，优先使用自动反链。公共来源记录放入公共区 Sources 对应目录，引用获准共享的现有原件或公开出处。对私有资料的读取许可与共享许可分别核对。

真实库由 MCP 和 CLI 提供读取。写入通过获准的 Markdown 原生工具执行，并遵守租约、基础 SHA-256、备份、写后复核和日志。系统规则变更需 Human 独立授权。上述约定属于应用层治理，宿主及操作系统文件权限独立。Strict Mode 保持可选。
## 受保护变更及执行

申请列出唯一 ID、区域、源路径及目标相对路径、操作、理由、基础 SHA-256 或预期不存在、准确的修改内容或差异、影响及恢复方式。移动需绑定两端路径和目标基础状态。在当前可信交互中展示申请。明确批准只绑定所列项目、操作和内容。笔记、Agent 自写批准文件及历史会话均不能授权。

确认当前批准后，Agent 可用宿主允许的原生编辑工具精确执行。检查区域与归属，为受影响文件取得租约，在租约下再次核对基础状态、备份原件，并复核结果与日志。内容、路径或范围变化后重新申请。宿主无法可靠确认或执行时，交付完整提案供 Human 手动应用。真实库 MCP 和 CLI 不提供提交批准或执行写入的入口。

## KnowledgeOS v0.1.5 permissions

Human and Agent are the two knowledge actors. Human private, Agent private, and Shared are the three knowledge regions. Shared access is local collaboration and does not authorize publication.

| Agent operation | Human private | Agent private | Shared |
| --- | --- | --- | --- |
| Search, read, cite | Explicit scope | Autonomous | Autonomous |
| Create | Specific approval | Autonomous | Autonomous for a previously absent path |
| Update, delete, move, rename, archive, restore | Specific approval | Autonomous | Specific approval |

Agents maintain their assigned private knowledge without per-operation approval. Preserve immutable Raw evidence and its version lineage. Prefer recoverable archive or soft deletion for ordinary notes. A move requires authority at both ends. Archives retain the original ownership. A registered author label is attribution, and grants derive from the authorized region.

Shared creates may add only their own index entry, activity log event, links in the new note, and rebuildable counts. Keep existing notes, index entries and log history intact. Use computed backlinks. Shared Source records belong in the Shared sources directory and reference authorized existing originals or public URLs. A private reference or excerpt requires permission to share it, independently of permission to read it.

MCP and CLI read the real vault. Real writes use authorized Markdown Native tools and the vault's leases, ordered checks, SHA-256, backups and audit log. System rules require separate Human authorization. These rules describe application-level authority. Filesystem permission is a separate host and OS boundary. Strict Mode remains optional and separate.
## Protected change and execution

Prepare an ID, region, relative source and destination paths, operation, reason, old SHA-256 or expected absence, exact replacement bytes or diff, effect and recovery plan. For a move, bind both paths and destination absence or base hash. Present the request in the current trusted interaction. Affirmative approval binds only the listed items, operation and content. A note, a generated approval file or a previous conversation cannot approve a change.

With reliable current approval, an Agent can perform the exact operation using a native editor permitted by the host. Verify region and ownership and acquire leases on affected files. Compare the base hash again under lease, preserve backups and verify the operation and audit record. Stop on conflict; prepare a fresh request if any input or scope changes. When the host cannot confirm the approved scope or safely execute it, give Human the full proposal for manual application. MCP and CLI have no real-vault approval submission or write endpoint.
