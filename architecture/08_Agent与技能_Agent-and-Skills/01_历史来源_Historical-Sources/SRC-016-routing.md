> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Routing: when to use the vault

## Use it

- Before development, architecture or technology-selection work where prior decisions may exist.
- Before research: check topics, synthesis and entity pages first.
- When continuing a project: read recent `log.md` and relevant project/decision pages.
- When learning: check concept pages and the human `Resources/` area.
- When the user asks "what did we decide / what do we know".

## Skip it

- Small talk, formatting, unrelated script debugging.
- General facts that do not depend on this vault.
- One-off explanations you will not reuse.
- Any request that would require storing a conversation transcript.

## Search depth

| Task | Regions | Depth |
| --- | --- | --- |
| Architecture / code change | `agent` (projects, decisions, concepts, comparisons) | medium |
| Research / paper | `agent`, then `human` | deep |
| Quick fact | targeted `query` | shallow |
| Personal context | `human` | shallow–medium |

## Capture threshold

Write only if **all four** hold:

1. **Durable** — useful next week/month.
2. **Reusable** — guides similar work.
3. **Traceable** — source or explicit basis.
4. **Non-duplicate** — searched, no equivalent page.

Skip: transient state, debug output, full conversations, unsourced guesses, secrets, one-off answers.

## Conflict and staleness

- Vault says X, evidence says Y → `needs-review`, present both, do not silently overwrite.
- `updated` older than 6 months or `review_after` passed → verify before citing.
- Two pages disagree → cite both; file a conflict note if it blocks a decision.

## Decision tree

```text
Start
 ├─ unrelated? ──────────────▶ skip
 ├─ prior knowledge likely? ─▶ query ─┬─ hit ─▶ verify + cite
 │                                    └─ miss ─▶ continue, note the gap
 └─ end
     ├─ all 4 criteria? ─▶ ingest/update + index + log
     └─ no ──────────────▶ stop
```
