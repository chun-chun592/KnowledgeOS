> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Synthesize

Combine sourced pages into a conclusion no single page states.

`knowledgeos synthesize` builds the scaffold; you write the analysis. It never invents conclusions.

```bash
knowledgeos synthesize \
  --title "RAG versus long-context prompting" \
  --question "When should a system retrieve instead of stuffing the context window?" \
  --from 10_Agent/wiki/concepts/rag.md 10_Agent/wiki/comparisons/long-context.md \
  --tags rag,context
```

## Preconditions

- At least two inputs, read fully.
- Inputs have sources (or accept lower confidence).
- The question fits in one sentence.

## Method

1. **State the question.**
2. **Build a claim table**: claim | input | evidence type | confidence.
3. **Find agreements** (independent support strengthens).
4. **Find conflicts** (state both and the conditions; do not average).
5. **Find gaps** (keep visible).
6. **Write the argument**, leading with the answer and its conditions.
7. **Label** `事实 / Fact`, `推断 / Inference`, `观点 / Opinion`.
8. **Set status/confidence**:

| Evidence | Status | Confidence |
| --- | --- | --- |
| Draft inputs, untested argument | `draft` | low |
| Sourced inputs, coherent, no independent check | `draft` / `needs-review` | medium |
| Independent sources, conflicts addressed | `verified` | high |

## Quality bar

Good: answers a new question, makes the inference explicit, preserves disagreement, cites everything,
states limits.

Bad: summary of summaries, quote stacking, false certainty, new unsourced "facts", duplicate comparison.

## Afterwards

```bash
knowledgeos index
knowledgeos lint
```

Link the synthesis from each input's `## Related`, and log contributions to inputs.
