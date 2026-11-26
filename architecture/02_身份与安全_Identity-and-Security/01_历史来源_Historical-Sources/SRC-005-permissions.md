> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Permissions and write requests

> Enforcement lives in the CLI's policy engine. It is a controlled-write boundary, **not an OS
> sandbox**: a process that writes to the vault without the CLI bypasses all of this. See
> `docs/permissions.md` for the threat model.

## Matrix (summary)

| Path | Human | Agent |
| --- | --- | --- |
| `00_Human/**` | read/write | read-only in the standalone CLI |
| `10_Agent/raw/**` | read/write | create + read; originals immutable |
| `10_Agent/wiki/**` | read/write | read/write |
| `20_Exchange/human-to-agent/**` | read/write | read-only |
| `20_Exchange/agent-to-human/**` | read/write | read/write |
| `20_Exchange/agent-to-agent/**` | read/write | read/write |
| `20_Exchange/write-requests/**` | read/approve | create only; **append-only for agents** — a request file may never be edited by the agent that filed it |
| `20_Exchange/locks/**` | read/write | read/write |
| `30_System/**` | read/write | read-only |
| `90_Archive/**` | read/write | archive-flow create only |
| `.obsidian/`, `.git/`, `.knowledgeos/` | external | denied |

Agents can never delete or move knowledge through the CLI. Archive instead.

## Requesting permission for a human note

```bash
knowledgeos request \
  --target 00_Human/Inbox/idea.md \
  --scope "Append a Related section; do not change existing text" \
  --expires 2026-02-08
```

This writes `20_Exchange/write-requests/YYYY-MM-DD-<agent>-<slug>.md` with `status: pending`.
Send the request to the Human for review. The standalone CLI keeps Human notes read-only.
An integrated host must use an independent authorization provider with exact path, action and
content hashes, expiry and a single-use revocable nonce. Approval inside a chat belongs in the
review record. Leave the historical request untouched.

## Path safety

The CLI rejects:

- `..` components,
- absolute paths outside the vault,
- symlinks/junctions anywhere in the chain,
- protected directories (`.git`, `.obsidian`, `.knowledgeos`, `.trash`),
- case variants that resolve into a protected region.

## Multi-agent coordination

- `index.md` and `log.md` are written under `.knowledgeos/locks/*.lock` by the CLI.
- Manual editors should use a lease in `20_Exchange/agent-to-agent/locks/`:
  path with `/` and `.` replaced by `-`, plus `.lock.md`.
- Re-read shared files before writing; append one log entry; regenerate one index block.
- Stale lock = past `expires` or >15 minutes with no progress. Record the takeover.

## Honest boundary

The matrix is enforced **only** for operations routed through `knowledgeos`. A process with direct
filesystem write access can bypass it. For a hard boundary use a separate OS user/ACL, read-only mount,
container, or an access gateway. See `SECURITY.md` in the repository.

Never state that Markdown or a Skill "prevents" writes at the OS level.

Historical approvals in Markdown are records. Human writes require an independent host provider that authenticates the approver, verifies exact path and content hashes, and consumes a revocable nonce once. The standalone CLI has no such provider.
