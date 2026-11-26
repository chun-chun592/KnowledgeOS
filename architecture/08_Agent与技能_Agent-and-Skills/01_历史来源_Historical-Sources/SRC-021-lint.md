> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Lint

Reports structural defects; never deletes or rewrites knowledge.

```bash
knowledgeos lint                 # human + agent (default)
knowledgeos lint --json
knowledgeos lint --strict        # exit 1 on errors
knowledgeos lint --region all
knowledgeos lint --report        # 20_Exchange/agent-to-human/lint-*.md
```

## Checks

| Code | Meaning | Level |
| --- | --- | --- |
| `frontmatter.*` | missing/invalid YAML, enum, date | error |
| `schema.invalid` | JSON Schema violation | error |
| `type.location` | type/directory mismatch | error |
| `owner.wiki` | `owner: agent` missing in wiki | error |
| `status.unsourced` | `verified` with no sources | error |
| `link.broken` | unresolved wikilink | error |
| `source.missing` | source target absent | error |
| `request.no_approver` | approved without `approved_by` | error |
| `link.orphan` | no inbound and no outbound | warning |
| `index.missing_entry` | page absent from index | warning |
| `index.stale` | managed block out of date | warning |
| `duplicate.title` / `duplicate.alias` | collisions | warning |
| `freshness.overdue` | `review_after` passed | warning |
| `log.untracked` | recent update absent from log | warning |
| `request.expired` | approved request past expiry | warning |
| `filename.style` | non-kebab-case | warning |

Lint checks links in human notes but never schema-validates or edits them.

## Triage

1. Errors: schema, owner, broken links/sources.
2. Warnings: orphans, index gaps, duplicates, overdue review.
3. Info: no inbound link.

Do not chase zero warnings. Structural health is not knowledge quality.

## Fix

```bash
knowledgeos index
knowledgeos update PATH --set review_after=2026-06-01
knowledgeos update PATH --append-section "Related" --content "- [[...]]"
knowledgeos update PATH --replace "[[old]]" --with "[[new]]"
knowledgeos update PATH --set status=archived --set 'superseded_by="[[canonical]]"'
```

- One class of problem per pass; re-run lint.
- Log `lint-fix` with a reason.
- Never edit human notes to silence a warning.
- Never delete an orphan; link or archive it.

## Limits

Lint cannot judge truth, detect subtle paraphrase duplication, resolve real contradictions, read PDFs, or
check external URLs. A human or agent must still read the knowledge.
