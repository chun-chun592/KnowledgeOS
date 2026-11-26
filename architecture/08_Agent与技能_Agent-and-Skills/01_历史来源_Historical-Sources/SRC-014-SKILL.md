> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

---
name: knowledgeos
description: "Use when a task involves searching, reading, citing, ingesting, updating, synthesizing or linting an Obsidian human+agent knowledge base. Also use proactively before architecture, research, technology comparison or project-continuation tasks when prior knowledge may exist. Human notes (00_Human) are read-only in the standalone CLI. Do not use for small talk, unrelated tasks, or as session memory; never store chat history."
license: MIT
compatibility: "Requires Python 3.10+ and the `knowledgeos` CLI (or skills/knowledgeos/scripts/knowledgeos.py). Works with any agent that can run shell commands. Obsidian is the human interface."
metadata:
  version: "0.1.1"
  homepage: "https://github.com/knowledgeos/KnowledgeOS-Agent-Kit"
  vault_env: "KNOWLEDGEOS_VAULT"
---

# KnowledgeOS Skill

Use `knowledgeos doctor` to inspect the configured mode and writer availability.
Secure New, Update and Recover use the configured Writer Service. Specify the
latest committed revision with `update --expected-revision`. If a write result
is unknown, retry with identical arguments and the same operation ID. Use
`recover <transaction-id> --dry-run` to inspect service evidence and report
NEEDS_REVIEW to the human.
If Secure Mode refuses a command, report the blocker and stop that workflow.
Do not change the mode, substitute a config, invoke core modules directly, or
edit managed files outside the CLI. Recovery and write requests use the CLI;
if blocked, report the operation ID to the human when available.

A thin router over a local knowledge base. The Python CLI does the file work; this Skill decides
**whether** to use the vault, **which** workflow applies, and **how** to report the result.

## Core rules (read every time)

1. **Search before writing.** Query titles, aliases and tags first; merge instead of duplicating.
2. **Human notes are read-only.** `00_Human/**` may be read, searched and cited. Writing requires an
   independently authorized host workflow. The standalone CLI keeps Human notes read-only.
3. **Agent Wiki is writable.** `10_Agent/wiki/**` is the shared agent area. `10_Agent/raw/**` accepts new
   sources; originals are immutable. `30_System/**` is read-only.
4. **No memory.** Never store conversation transcripts, user preferences, persona files or session state.
   The vault holds knowledge notes, not agent memory.
5. **Sources and labels.** Facts need `sources`; label inferences and opinions. Do not mark `verified`
   without evidence.
6. **Never claim enforcement you do not have.** The CLI checks paths and policy. It is not an OS sandbox.

## Does this task need the vault?

| Task | Action |
| --- | --- |
| Development, architecture, technology choice | Search `projects`, `decisions`, `concepts`, `comparisons` first |
| Research, paper reading, investigation | Search `topics`, `synthesis`, `entities`, then ingest if durable |
| Learning a new subject | Search `concepts` and human `Resources/` |
| Continuing earlier work | Read recent log entries and relevant project/decision pages |
| Simple unrelated question | Do not use the vault |
| Chat, formatting, script debugging | Do not use the vault |

Capture at the end **only** if the result is durable, reusable, traceable and non-duplicate.
Read `references/routing.md` for the full threshold.

## Command surface

```bash
knowledgeos doctor                       # health check (read-only)
knowledgeos status                       # counts, index state, pending requests
knowledgeos query "terms"                # keyword search, cites paths
knowledgeos new concept "Title"          # create a wiki skeleton (type: concept/entity/...)
knowledgeos ingest ./file.pdf --kind papers
knowledgeos update PATH --set k=v --append-section H --content "..."
knowledgeos synthesize --title "..." --from A.md B.md
knowledgeos index                        # regenerate managed index block
knowledgeos lint [--strict] [--json]     # structural checks
knowledgeos request --target PATH --scope "..."
knowledgeos log --limit 5                # recent audit entries
knowledgeos recover --list               # list interrupted transactions (read-only)
knowledgeos recover <operation-id> --dry-run   # show the recovery plan (read-only)
knowledgeos recover <operation-id>       # finish one interrupted transaction
```

Every write runs as a crash-recoverable transaction: an intent with per-file
SHA256 is recorded before anything is written, so a hard crash leaves a state
that `knowledgeos recover --list` can find and `recover <id>` can finish.
Retrying the same command (same arguments, or the same `--operation-id`)
resumes the interrupted transaction instead of failing with "already exists".
Ingest deduplicates by content (SHA256): identical bytes are stored once and
later sources reuse the existing raw original with their own provenance page.
Use `--json` when you need to parse results. Use `--dry-run` before any non-trivial write.

The CLI is normally installed (`pip install -e .`). If it is not on `PATH`, run:

```bash
python skills/knowledgeos/scripts/knowledgeos.py <command>
```

Vault resolution: `--vault PATH` → `KNOWLEDGEOS_VAULT` → `.knowledgeos/config.toml` in cwd or a parent.
Do not hard-code absolute paths in notes or commits.

## Workflow routes

Load only the reference you need:

| Situation | Read |
| --- | --- |
| First time in this repo / unclear architecture | `references/architecture.md` |
| Any write, or a permission question | `references/permissions.md` |
| Deciding whether to use the vault | `references/routing.md` |
| Adding a source or a new page | `references/ingest.md` |
| Answering from existing notes | `references/query.md` |
| Correcting / merging / archiving | `references/update.md` |
| Combining pages into a conclusion | `references/synthesize.md` |
| Checking quality or preparing a report | `references/lint.md` |
| Frontmatter fields, types and statuses | `references/schema.md` |
| End-to-end walkthroughs of the six workflows | `references/workflows.md` |

## Query protocol

1. Run `knowledgeos query "<terms>"` (add `--type`, `--tag`, `--status`, `--region`).
2. Read the best 1–3 pages, not the whole vault.
3. Check `status`, `updated` and at least one `sources` entry.
4. Cite vault-relative paths in the answer.
5. If nothing is found, say so; do not fabricate that the vault contains it.

## Write protocol

1. Confirm the region (`agent_wiki` = free, `human` = approval only, `system` = read-only).
2. For human notes: `knowledgeos request --target <exact> --scope "<specific>"`, then stop and wait.
3. Search for duplicates.
4. Use `new` / `ingest` / `synthesize` rather than hand-creating frontmatter.
5. Fill sources and label claims; keep `status: draft` until verified.
6. `knowledgeos index`, then `knowledgeos lint`.
7. Report what changed, where, and what remains uncertain.

## Multi-agent behaviour

- Use one stable agent id in `--agent` / `KNOWLEDGEOS_AGENT`, `created_by`, and log entries.
- `created_by` is permanent; add contributions under `## Contribution log`.
- Shared index/log writes use CLI locks. If you edit manually, follow `references/permissions.md`.
- Disagreement: keep both claims, mark `needs-review`, file a note in `20_Exchange/agent-to-human/`.
- Preserve the source and preview Agent archival copies with archive PATH --reason REASON --dry-run.

## Output discipline

- Cite pages as `10_Agent/wiki/...` (never absolute local paths).
- Distinguish what the vault says from what you infer.
- State when a page is stale, disputed or unsourced.
- If a tool call fails, report the error and the attempted command; do not pretend it succeeded.
- Do not claim a write happened unless the command returned success.

## Anti-patterns

- Creating a page for every query.
- Treating `draft` as truth.
- Copying a human note into the wiki instead of linking it.
- Editing `30_System/**` to make a write "allowed".
- Using the vault as a memory store or transcript archive.
- Approving your own write request (only a human can approve).
- Editing a write request after filing it: requests are append-only for agents. Only the human
  sets `status`, `approved_by`, `approved_at` or `expires`.
