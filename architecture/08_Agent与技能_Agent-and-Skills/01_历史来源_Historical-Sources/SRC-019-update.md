> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Update

Amend knowledge without erasing history.

## Operations

```bash
# Frontmatter
knowledgeos update PATH --set confidence=high --set status=draft --reason "..."

# Append a section
knowledgeos update PATH --append-section "Open questions" --content "- ..."

# Replace unique body text
knowledgeos update PATH --replace "old" --with "new" --reason "..."

# Retry or finish the same Agent update
knowledgeos update PATH --operation-id ID --append-section HEADING --content TEXT
knowledgeos recover ID
```

The CLI backs up existing files, re-validates Agent notes, sets `updated`, appends the log and rebuilds
the index. It refuses invalid results. On Windows, recovery verifies the recorded parent and
file identities. If recovery reports NEEDS_REVIEW, leave the note and transaction files in place
for reconciliation.

## Choose the smallest change

| Goal | Operation |
| --- | --- |
| Fix a fact | Edit claim + source; add "was / now / why" |
| Add evidence | Extend section + sources |
| Unresolved conflict | Both claims + `needs-review` |
| Duplicate | Merge, `supersedes`, archive the weaker page |
| Retire | `status: archived` + `superseded_by` |
| Metadata | `--set` |

## Preserve superseded reasoning

```markdown
> **Change 2026-02-01:** previously "X"; now "Y". Reason: newer benchmark. Previous source kept below.
```

Never silently replace a conclusion; future readers need the change history.

## Merge

1. Keep the page with better title/links/sources.
2. Move unique claims and sources; preserve attribution.
3. `supersedes: ["[[old]]"]` on the survivor.
4. Old page: `status: archived`, `superseded_by`.
5. Update inbound links; lint.
6. Log a `merge`.

## Forbidden

- Delete pages or sources.
- Edit `created_by`.
- Rewrite the log.
- Edit `30_System/**`.
- Batch-rewrite human notes.
- Use update to create a new human file (use a request + create flow).
