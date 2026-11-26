---
title: "{{title}}"
type: handoff
owner: agent
created_by: "{{agent_id}}"
created: "{{date}}"
updated: "{{date}}"
status: draft
sources: []
related: []
tags: [knowledgeos, handoff]
---

<!--
HANDOFF TEMPLATE → 20_Exchange/agent-to-agent/YYYY-MM-DD-<from>-to-<to>-<slug>.md
Transient coordination only. Promote durable results to 10_Agent/wiki/ and close this file.
This file is not validated by the Agent Wiki schema.
-->

# Handoff: {{title}}

- **From:** {{agent_id}}
- **To:** <!-- agent id or "any" -->
- **Date:** {{date}}
- **Task state:** not started / in progress / blocked / ready for review

## Task

<!-- What the receiving agent must accomplish, in one or two sentences. -->

## State of the work

| Item | Status | Where |
| --- | --- | --- |
|  |  |  |

## Files changed

- `10_Agent/wiki/...` — what changed

## Decisions already made

- [[]] — do not reopen without new evidence

## Permissions and approvals

- Human-note proposal: <!-- none / proposal path; Human applies it manually -->
- Required locks: <!-- index.md / log.md / none -->

## Do not touch

- `00_Human/**` (any requested changes remain proposals for Human to apply)
- `30_System/**`
- <!-- specific pages -->

## Next steps

1.
2.
3.

## Open questions

-

## Closing note

When done: append a `log.md` entry if knowledge changed, set this file `status: done`,
and link the resulting wiki page here.
