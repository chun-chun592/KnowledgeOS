> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Query

Read-only retrieval with verification and citations.

## Search

```bash
knowledgeos query "retrieval augmented generation"
knowledgeos query "rag" --type comparison --status verified
knowledgeos query "vector index" --region agent --limit 10
knowledgeos query "project alpha" --region human
knowledgeos query "topic" --region all --json
```

Scoring: title > alias > tag > heading > body; `verified` gets a small boost, `archived` a penalty.
No embeddings, no network.

If the first search misses:

1. try an alias or acronym,
2. open the relevant `topic` page,
3. widen `--region`,
4. fall back to Obsidian search.

## Verify

For each candidate:

- `status`: `draft` = hypothesis, `verified` = sourced, `needs-review` = conflict, `outdated` = stale.
- `updated`: compare with the domain's rate of change.
- `sources`: open at least one; a list is not proof.
- labels: do not present `推断 / Inference` as `事实 / Fact`.
- `confidence`: a hint, not a substitute for checking.

## Cite

Use vault-relative paths:

```text
10_Agent/wiki/decisions/local-storage.md
(see also 10_Agent/raw/documents/sqlite-bench.md, table 3)
```

Never expose absolute local paths in public output.

## Gaps

| Situation | Response |
| --- | --- |
| Nothing found | Say so; answer from general knowledge if appropriate |
| Stale page | Answer with a staleness warning |
| Disagreement | Present both positions; mark `needs-review` |
| Unreachable source | Say the claim is unverified |

## Do not

- Create a note just because you searched.
- Fix pages mid-query; separate retrieval from mutation.
- Treat the index or a draft as truth.
- Invent a citation or claim the vault said something it did not.
