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
HANDOFF TEMPLATE → 20_Exchange_协作交流/agent-to-agent_AI之间的交流/YYYY-MM-DD-<from>-to-<to>-<slug>.md
Transient coordination only. Promote durable results to 10_Agent_AI知识库/wiki_整理后的知识/ and close this file.
This file is not validated by the Agent Wiki schema.
-->

# Handoff: {{title}}

- **From:** {{agent_id}}
- **To:** <!-- agent id or "any" -->
- **Date:** {{date}}
- **Task state:** not started / in progress / blocked / ready for review

## Task / 任务

<!-- What the receiving agent must accomplish, in one or two sentences. -->

## State of the work / 工作进度

| Item | Status | Where |
| --- | --- | --- |
|  |  |  |

## Files changed / 改动文件

- `10_Agent_AI知识库/wiki_整理后的知识/...` — what changed

## Decisions already made / 既有决定

- [[]] — do not reopen without new evidence

## Permissions and approvals / 授权范围与租约

- Human-note proposal: <!-- none / proposal path; Human applies it manually -->
- Required locks: <!-- index_知识目录.md / log_知识更新记录.md / none -->

## Do not touch

- `00_Human_个人知识库/**` (any requested changes remain proposals for Human to apply)
- `30_System_知识库管理/**`
- <!-- specific pages -->

## Next steps / 后续步骤

1.
2.
3.

## Open questions / 待解问题

-

## Closing note / 交接结果

When done: append a `log_知识更新记录.md` entry if knowledge changed, set this file `status: done`,
and link the resulting wiki page here.

## 中文填写说明

交接记录放在 `20_Exchange_协作交流/agent-to-agent_AI之间的交流`。记录文件、未决问题和租约。个人知识只提交提案，由本人手工应用。
