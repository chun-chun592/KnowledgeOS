> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Ingest

Turn a source into citable knowledge without altering the original.

## Steps

```bash
# 1. Add the source (copies the file; never moves it)
knowledgeos ingest ./papers/rag.pdf --kind papers \
  --title "RAG (Lewis et al., 2020)" --summary "One-paragraph source-faithful summary."

# URL: records provenance without downloading
knowledgeos ingest https://example.com/article --kind websites --title "Article title"

# 2. Check for duplicates
knowledgeos query "retrieval augmented generation" --region agent

# 3. Create knowledge pages only for durable units
knowledgeos new concept "Retrieval-Augmented Generation" --tags rag,retrieval \
  --source "[[10_Agent/raw/papers/rag.pdf]]"

# 4. Refresh index and check quality
knowledgeos index
knowledgeos lint
```

## Source placement

| Source | Where |
| --- | --- |
| Local document | copy to `10_Agent/raw/documents/` |
| Paper | copy to `10_Agent/raw/papers/` |
| Web page | record in `10_Agent/raw/websites/` (URL only in v0.1) |
| Human note/clipping | keep in `00_Human/`, link to it; never copy |

## Page selection

| Content | Type |
| --- | --- |
| Idea / mechanism | `concept` |
| Named actor/product/model | `entity` |
| Domain overview | `topic` |
| Choice between options | `comparison` |
| Cross-page conclusion | `synthesis` |
| Source itself | `source` (automatic) |

## Rules

- One page, one idea. Do not paste full documents.
- Search titles, aliases and tags before creating.
- Facts get source anchors (page/section); inferences state their basis; opinions are labelled.
- Default `status: draft`; `verified` only with sources.
- Link new pages from at least one existing page.
- Human material is cited, not copied or edited.
- Log and index updates are automatic with the CLI; verify them if you wrote manually.

## Output checklist

- [ ] Original opens from the source page
- [ ] Provenance filled (author, date, reliability)
- [ ] No duplicate page
- [ ] Facts sourced; labels present
- [ ] Linked from a topic/related page
- [ ] `knowledgeos lint` shows no new errors
