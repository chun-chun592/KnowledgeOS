> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Permissions and security

Standard rules are application-level constraints. The experimental Secure Writer
Service reads the Windows client token, checks its allowlist and validates its
own vault-relative Agent Wiki destination before writing. Recover is scoped to
the transaction's original principal. Cross-SID isolation and NTFS ACL
enforcement await independent testing. Production deployment is blocked.

KnowledgeOS separates **ownership** (who may change what) from **enforcement** (what actually stops a
write). The ownership rules are implemented once, in the policy engine
(`src/knowledgeos/policy.py` + `src/knowledgeos/paths.py`), and every mutating CLI command consults
them before touching the filesystem.

The vault-side policy text that ships with every install is
`30_System/policies/permissions.md` in [`vault-template/` · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only); this document is the
implementation-level reference. See also [SECURITY.md · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) for reporting vulnerabilities.

> **One-sentence summary:** the CLI is a *controlled-write boundary*, not an operating-system
> sandbox. Everything below describes what the CLI enforces for processes that use it — and the
> honest list of what it cannot enforce.

## 1. Enforcement layers

| Layer | What it does | Can it be bypassed? |
| --- | --- | --- |
| `SKILL.md` / `AGENTS.md` instructions | Tell the model when and how to use the vault | Yes — instructions are advisory only |
| Policy engine (`policy.evaluate` / `assert_allowed`) | Deny writes outside the ownership matrix; validate write requests | Only by not using the CLI (see §7) |
| Path hardening (`Vault.resolve`) | Reject traversal, escapes, symlinks/junctions, protected dirs | Only by not using the CLI |
| OS filesystem permissions | Would stop any process | **Not provided** by KnowledgeOS v0.1 |

There is no daemon, no filesystem filter driver, no container. If you need OS-level guarantees,
§7 lists the options users typically add on top.

## 2. Ownership matrix

Regions are derived from the first path component (`config.paths.*`, default names below). The
matrix is the single source of truth in `policy.evaluate`; this table mirrors `region_matrix()`.

| Path | Human | Agent | Notes |
| --- | --- | --- | --- |
| `00_Human/**` | read / write | **read-only** in standalone CLI | The core rule of the system |
| `10_Agent/raw/**` | read / write | create + read | Originals are immutable; `update` is denied |
| `10_Agent/wiki/**` | read / write | read / write | The agent's own area; every write is logged |
| `20_Exchange/agent-to-human/**` | read / write | read / write | Reports, lint output, questions |
| `20_Exchange/agent-to-agent/**` | read / write | read / write | Multi-agent hand-off |
| `20_Exchange/human-to-agent/**` | read / write | **read-only** | Tasks and answers flow one way |
| `20_Exchange/write-requests/**` | read / approve | **create only** | Agents cannot edit requests (§4) |
| `20_Exchange/locks/**` | read / write | read / write | Machinery |
| `20_Exchange/` root and other subfolders | read / write | read-only | e.g. the README |
| `30_System/**` and `AGENTS.md` | read / write | **read-only** | Human-governed policies, schema, workflows |
| `90_Archive/**` | read / write | **create only** (archive flow) | Archived content is immutable |
| `.git/`, `.obsidian/`, `.knowledgeos/`, `.trash/` | managed externally | **denied** | Refused for every actor, every action |
| Any other path (unknown region) | read / write | read-only | Unrecognised top-level folders are not agent-writable |

Additional rules that apply to **every** actor:

- `delete` and `move` are denied by the CLI for humans and agents alike. Knowledge is retired with
  `status: archived` (+ `superseded_by`), never removed. Use Git or Obsidian for real deletions.
- Paths inside protected directories are refused **before** the policy matrix is consulted, so no
  approval can authorise a write into `.git/`, `.obsidian/`, `.knowledgeos/` or `.trash/`.
- Case variants do not create new regions: on Windows the containment comparison is case-insensitive,
  and directory names are matched casefolded, so `00_human/secret.md` is still a human note.

## 3. Action semantics

| Action | Meaning | Who may do it |
| --- | --- | --- |
| `read` | Open, search, quote, link | Everyone, everywhere (except protected dirs) |
| `create` | New file at a path that does not exist | Per matrix above |
| `update` | Replace content or frontmatter of an existing file | Per matrix above |
| `archive` | Create a record under `90_Archive/` | Both actors; nothing may be edited afterwards |
| `delete` | Remove a file | **Nobody via the CLI** |
| `move` | Change a path | **Nobody via the CLI** |

Whether an operation is `create` or `update` is derived from the filesystem at execution time, so a
write to an existing path cannot be smuggled through as a "create".

## 4. Write requests — the only path into `00_Human/`

An agent may modify a human note only when an approved request file covers the exact target path.
Requests live in `20_Exchange/write-requests/` and are normally created by:

```bash
knowledgeos request --target "00_Human/Inbox/idea.md" \
  --scope "Append a 'Related' section linking to the RAG concept; no other changes."
```

### Lifecycle

```
pending ──human edits frontmatter──▶ approved ──CLI write (logged)──▶ done
   │                                    │
   └── human sets rejected              └── expires date passes → invalid
```

- The agent creates the file (`status: pending`) and then **stops and waits**.
- Only a human, editing the file in Obsidian or a text editor, sets `status: approved` and fills
  `approved_by`. The CLI has no "act as human" mode by design.
- Agents may **create** request files but may never **update** them: `policy.evaluate` denies agent
  `update` in `20_Exchange/write-requests/`, so an agent cannot approve its own request, widen its
  targets, or flip the status to `done`. Request files are append-only from the agent's side.

### Required fields (enforced by `parse_write_request`)

| Field | Rule |
| --- | --- |
| `type: write-request` | Required; anything else is rejected |
| `status: approved` | Only `approved` authorises. `pending` / `rejected` / `done` / `expired` are recognised but never authorise |
| `approved_by` | Non-empty, not `pending` / `tbd` / `todo`; a human identity such as `human:alice` |
| `approved_for` | The requesting agent id, a glob pattern over agent ids, or `*`. The running agent id must match |
| `scope` | Non-empty prose describing exactly what will change. Human-reviewed, not machine-checked |
| `targets` | At least one entry; machine-checked against the normalized target path (§4.1) |
| `expires` | `YYYY-MM-DD`, today or later. Missing or invalid = no authorisation |

### Example

```yaml
---
title: "Triage three Inbox notes"
type: write-request
owner: human
created_by: opencode
created: 2026-02-01
updated: 2026-02-01
status: approved            # set by the human
id: WR-20260201-inbox-triage
requested_by: opencode
approved_by: "human:alice"  # set by the human
approved_for: opencode
approved_at: 2026-02-02
expires: 2026-02-08
targets:
  - "00_Human/Inbox/idea.md"
  - "00_Human/Inbox/reading-list.md"
scope: "Append a 'Related' section with wiki links; do not modify existing text."
---
```

The write is then executed with the request attached, which records the authorisation in `log.md`:

```bash
knowledgeos update 00_Human/Inbox/idea.md \
  --append-section "Related" --content "- [[10_Agent/wiki/concepts/retrieval-augmented-generation]]" \
  --reason "Approved WR-20260201-inbox-triage" \
  --request 20_Exchange/write-requests/2026-02-01-opencode-inbox-triage.md
```

`--request PATH` must point inside `20_Exchange/write-requests/`; a request file stored anywhere else
is refused.

### Target matching

`targets` entries support four shapes (compared casefolded, backslashes normalised):

| Pattern | Matches |
| --- | --- |
| `00_Human/Inbox/idea.md` | Exactly that file |
| `00_Human/Inbox/*.md` | Glob (`fnmatch`) on the whole relative path |
| `00_Human/Inbox/` | Every path under that folder (trailing slash) |
| `00_Human/Inbox/**` | Same as a directory prefix, made explicit |
| `00_Human/Inbox/idea` | Bare stems are completed with `.md` |

`scope` is deliberately descriptive: it is what a human reviewer reads. `targets` is what the code
checks. A write outside `targets` is denied even if the prose would have allowed it; widening either
one after approval is a policy violation and should be handled by filing a new request.

## 5. Path hardening

Before any read or write, `Vault.resolve` performs, in order:

1. Reject empty paths and any path containing a `..` component (before expansion, so `..%2f`-style
   tricks and `foo\..\bar` both fail).
2. Expand `~` and environment variables, then make the path absolute relative to the vault root.
3. Lexical normalisation and a containment check: the result must stay inside the vault root.
4. Reject symlinks, junctions and reparse points at **every existing component** of the chain —
   including links that point *back inside* the vault.
5. Resolve the real path and re-check containment (catches case tricks and remaining redirections).
6. Refuse paths whose first component is a protected directory (`.git`, `.obsidian`, `.knowledgeos`,
   `.trash`; matched casefolded).
7. Refuse writing `.lnk` / `.url` shortcut files.
8. Classify the region and consult the policy matrix (and any `--request`) before the write.

Writes themselves are atomic: content goes to a temporary file in the same directory, is flushed and
`fsync`ed, then `os.replace`d. A failure before the replace leaves the old file untouched; there is
no moment when a partially written note exists.

## 6. What every write records

| Record | Location | Behaviour |
| --- | --- | --- |
| Backup | `.knowledgeos/backups/<stamp>/<relative-path>/` | Written before an existing file is replaced; the 25 most recent runs are retained |
| Log entry | `10_Agent/wiki/log.md` | Append-only; records action, files, reason, impact, authorization (request id/path) |
| Index | `10_Agent/wiki/index.md` | Managed block regenerated after wiki writes; human content outside the block is preserved |
| Lock | `.knowledgeos/locks/<name>.lock` | `O_CREAT\|O_EXCL` cooperative lock with a timeout and stale-after policy, so cooperating agents cannot interleave index/log writes |

The log is an audit trail of knowledge operations — it is not a chat transcript, and failed attempts
are not recorded. Inspect it with `knowledgeos log --limit 20` or `--json`.

## 7. The honest boundary

**Prevented (for processes that use the CLI):** accidental human-note edits, traversal and symlink
escapes, silent overwrites, self-approved write requests, interleaved index/log corruption,
untraceable changes.

**Not prevented:**

- Any process with normal filesystem access that ignores KnowledgeOS — including an agent that runs
  `Set-Content` / `echo >` / `sed -i` instead of the CLI.
- A malicious Obsidian plugin or embedded HTML/JS in a note.
- A human approving a request broader than intended; `targets` is only as strong as the review.
- The model provider or agent runtime exfiltrating note content at read time.
- Library users who import `knowledgeos` modules directly: `update`, `ingest`, `synthesize` and the
  lint report writer call `policy.assert_allowed` internally, but low-level helpers such as
  `Vault.write_text`, `index.rebuild` and `log.append` do **not** — they assume the caller already
  checked. The CLI is the enforced surface.

**Stronger boundaries users can add on top** (documented, not implemented):

| Option | Strength | Cost |
| --- | --- | --- |
| Git review before commit (`git diff 00_Human/`) | medium | human attention |
| Pre-commit hook rejecting `00_Human/` changes | medium–high | can block legitimate human edits |
| Separate OS user + read-only ACL on `00_Human/` (NTFS ACLs / POSIX mode bits) | high | ops complexity |
| Read-only mount or container for the agent | high | setup effort |
| Vault copy for the agent; the human merges | high | slower collaboration |
| Hash snapshot before/after agent runs | detection only | cheap |

`knowledgeos doctor` reports the boundary explicitly on every run.

## 8. Configuration knobs that affect policy

- `[agent] id` — the identity used for `created_by`, log entries and `approved_for` matching.
  Override per run with `--agent` or `KNOWLEDGEOS_AGENT`. See [configuration.md · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only).
- `[agent] require_write_request` — **advisory in v0.1.** The engine always requires an approved
  request for human-note writes; `doctor` prints a warning if a vault sets it to `false`, so the
  safe default cannot be silently weakened by config.
- `[locks] timeout_seconds`, `stale_after_seconds` — concurrency behaviour only; they do not affect
  authorisation.

## 9. Auditing and incident response

Routine review:

```bash
knowledgeos log --limit 20              # what changed, by whom, under which authorization
knowledgeos status                      # pending/approved request counts, index state
knowledgeos lint                        # flags approved-but-expired requests and missing approvers
git diff -- 00_Human/                   # if the vault is version-controlled
```

If an unauthorised write is suspected:

1. Stop the agent; make no further writes.
2. Compare `git status` / `git diff` (or your hash baseline) for `00_Human/`.
3. Restore from Git or `.knowledgeos/backups/<stamp>/`.
4. Write an incident note in `20_Exchange/agent-to-human/`: time, files, cause, recovery.
5. Revoke or narrow the approval: set `status: rejected` or shorten `expires` — remember the agent
   cannot edit request files, so only you can.
6. If the cause was a tool bug, add a regression test and see [SECURITY.md · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only).

## 10. Where this is tested

| Test file | Covers |
| --- | --- |
| `tests/test_policy.py` | Matrix decisions per region/actor/action, request parsing, expiry, `approved_for` matching, agent append-only rule on requests |
| `tests/test_paths.py` | Traversal rejection, symlink/junction refusal, protected directories and case variants, atomic writes, backups, locks |
| `tests/test_installer.py` | Create-only installer, never-overwrite, template escaping |
| `tests/test_privacy.py` | No real-vault data or private configuration in the repository |
| `tests/test_cli.py` | End-to-end CLI behaviour including `--request` flows |

All tests run against synthetic vaults in temporary directories; no real vault is ever touched. Run
them with `python -m pytest`. Known-untested areas are listed in [development.md · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only).

## Human authorization in v0.1.1

The preceding Markdown fields describe historical request records. The standalone CLI keeps Human notes read-only. An embedded host must supply an independent HumanAuthority that authenticates the principal and atomically consumes a revocable nonce bound to the exact write. See SECURITY.md for deployment requirements.
