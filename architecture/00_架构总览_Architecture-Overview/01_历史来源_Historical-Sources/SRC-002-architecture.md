> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Architecture

CLI command execution selects a local or experimental service backend. Standard
retains its transaction formats. The Windows Writer Service executes Secure New,
Update and Recover over one typed Named Pipe and owns the SQLite ledger and
immutable objects. It records file identity and revision before publishing an
Update. Log and Index are materialized from durable receipts. See the
[transaction model · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only).

KnowledgeOS is a **knowledge system**, not a chat-memory layer. It gives a human and one or more
agents a shared Obsidian vault with explicit ownership, a portable Agent Skill, and a small Python
engine that performs controlled writes.

The design follows Andrej Karpathy's **LLM Wiki** pattern: raw sources, structured wiki pages, a
schema, a derived index, and an append-only log. The human's own notes stay in a PARA/MOC/Zettelkasten
friendly area and are linked from the wiki rather than copied into it.

## Two owners, one graph

```
                 ┌──────────────────────────────┐
                 │        Obsidian vault        │
                 │                              │
  Human ────────▶│  00_Human/**   (human-owned) │◀──── read-only ──── Agent
                 │                              │
  Agent ────────▶│  10_Agent/wiki/** (agent)    │◀──── read/write ─── Human
                 │  10_Agent/raw/**  (immutable)│
                 │                              │
  Both  ────────▶│  20_Exchange/** (hand-off)   │
                 │  30_System/**   (governance) │◀──── read-only ──── Agent
                 │  90_Archive/**  (retired)    │
                 └──────────────────────────────┘
```

| Area | Purpose | Agent rights |
| --- | --- | --- |
| `00_Human/**` | The human's PARA / MOC / Zettelkasten notes | read; write only with an approved, scoped, unexpired request |
| `10_Agent/raw/**` | Immutable copies of sources and their provenance records | create + read; never rewrite originals |
| `10_Agent/wiki/**` | Concepts, entities, topics, comparisons, synthesis, projects, decisions | create, update, index, log |
| `20_Exchange/**` | Human↔Agent and Agent↔Agent hand-off | write to agent folders; create pending write requests; read `human-to-agent` |
| `30_System/**` | Policies, schema, workflows, templates | read-only |
| `90_Archive/**` | Retired knowledge (archive flow only) | create; no update or delete |
| `.obsidian/`, `.git/`, `.knowledgeos/` | Editor, version control, local machinery | denied |

The policy engine is the single source of truth. See [permissions.md · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) for the
decision matrix and the write-request lifecycle.

## Layers

```
Agent client (Codex / Claude Code / Gemini CLI / OpenClaw / Cursor)
        │  reads SKILL.md, then references/*
        ▼
skills/knowledgeos/SKILL.md          one portable router
        │  calls the CLI
        ▼
knowledgeos CLI (src/knowledgeos/cli.py)
        │  policy + path + schema validation
        ▼
Python modules                      atomic write to the Obsidian vault
        │
        ▼
<vault>/                             Markdown files, index, log, backups, locks
```

There is **no MCP server in v0.1** and no duplicated business logic in the Skill. `SKILL.md` explains
when to use the knowledge base and which command to run; the Python modules do the work.

## Modules

| Module | Responsibility |
| --- | --- |
| `config.py` | Vault discovery, TOML loading, stable defaults |
| `paths.py` | Path normalization, `..`/absolute/symlink/junction rejection, atomic writes, backups, file locks |
| `policy.py` | Region/actor/action matrix and scoped write-request parsing |
| `schema.py` | Frontmatter split/parse/render, YAML fallback, JSON-Schema-subset validation |
| `search.py` | Keyword scoring, snippets, wikilink extraction and resolution |
| `index.py` | Managed index block in `10_Agent/wiki/index.md` |
| `log.py` | Append-only operations log with a cooperative lock |
| `ingest.py` | Copy a raw source, create a source record, refuse human-note copies |
| `update.py` | Create a page from a skeleton; update frontmatter, sections or exact text |
| `synthesize.py` | Build a linked synthesis scaffold from two or more pages |
| `lint.py` | Schema, link, orphan, index, log, freshness and request checks |
| `installer.py` | New-vault install and incremental integration without overwriting |
| `diagnostics.py` | Read-only `doctor` and `status` reports |
| `cli.py` | Argument parsing, JSON output, exit codes, dry-run |

## Write path

Every mutating command follows the same order:

1. **Resolve the vault** from `--vault`, `KNOWLEDGEOS_VAULT`, cwd discovery, or the config file.
2. **Normalize the target path.** Reject `..`, absolute escapes, symlink/junction components, protected
   directories and shortcut files.
3. **Ask the policy engine.** Agent writes outside `10_Agent/wiki`, `10_Agent/raw` and approved exchange
   folders are refused unless a matching write request exists.
4. **Validate the result.** Agent pages must satisfy the frontmatter schema; generated content is
   parsed and checked before it is written.
5. **Write atomically.** Content goes to a temporary file in the same directory, is flushed and
   `os.replace`d. Existing files are backed up to `.knowledgeos/backups/<stamp>/` first.
6. **Append the log** under a lock. The log records the action, files, reason, impact and authorization.
7. **Rebuild the index** when a wiki page changed. Only the managed block is replaced.

A failure before step 5 leaves the vault untouched. A crash during step 5 leaves either the old file
or the new file, never a partial write.

## Index and log

`10_Agent/wiki/index.md` contains a managed region:

```markdown
<!-- knowledgeos:index:start -->
...generated tables...
<!-- knowledgeos:index:end -->
```

Everything outside the markers is preserved. `knowledgeos index --check` is read-only and exits `1`
when the block is stale.

`10_Agent/wiki/log.md` is append-only. One entry looks like:

```markdown
## 2026-11-18 14:05 · researcher

- action: `update`
- files: `10_Agent/wiki/concepts/retrieval-augmented-generation.md`
- reason: Added a source-backed boundary section
- impact: Fields: updated, sources
- authorization: —
```

The log is an audit trail for knowledge operations, not a transcript. Chat, scratchpads and failed
attempts are not recorded.

## Search model

v0.1 uses transparent keyword scoring over frontmatter and body text:

- exact/prefix title matches, aliases and tags score highest;
- headings and body occurrences add smaller amounts;
- `verified` pages get a small boost; `archived` pages are demoted;
- CJK text works through casefolded substring matching;
- results include the matched signals and a snippet.

There are no embeddings, no vector database and no network calls. A semantic search layer can be added
later without changing the write path.

## Concurrency

Cooperative agents share the vault through `FileLock`, which uses `O_CREAT|O_EXCL` lock files in
`.knowledgeos/locks/`. Locks have a timeout and a stale-after policy. `log.append` and `index.rebuild`
take the relevant lock; `atomic_append` re-reads the file inside the lock before writing.

This prevents cooperating KnowledgeOS processes from interleaving writes. It cannot stop a process
that ignores the lock. See the honest boundary in [permissions.md · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only).

## Compatibility

- Python 3.10+.
- Standard library only; PyYAML is optional. A restricted YAML parser handles flat frontmatter when
  PyYAML is absent. On Python 3.10, `tomli` is required to read TOML.
- Windows, macOS and Linux. Path checks handle Windows junctions and case-insensitive comparisons.
- Unquoted ISO dates in Obsidian frontmatter are normalized to strings, so existing notes validate.
- `.obsidian/` is never read or written by the engine.

## Deliberate non-goals

- AI memory, session persistence, persona files, automatic chat capture.
- An MCP server (the CLI is the stable interface; modules are reusable if one is added).
- OS-level enforcement. The CLI is a controlled-write boundary, not a sandbox.
- Automatic semantic tagging, graph analytics, or an embedding pipeline.
