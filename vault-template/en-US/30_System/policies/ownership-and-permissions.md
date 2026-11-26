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
