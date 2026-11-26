# Knowledge Workflow

## Query, Intake, and Compilation

Start with indexes, titles, aliases, and sources within the [ownership rules](../policies/ownership-and-permissions.md). Return temporary findings directly and save reusable work within existing authorization.

Check source identifiers and SHA-256 for duplicates. Keep approved originals under `10_Agent/raw` and use the [Source template](../templates/source.md) to record provenance, summary, evidence, and the original-file link in the wiki. Cite, extend, update, or create as the material warrants. Preserve conflicting evidence and its scope.

## Agent Native Editing

Choose the type using the [schema](../schemas/frontmatter.schema.json). For new notes, confirm the target is absent. For updates, preserve valid sources and original authorship.
Lease each affected file, including the index and log. Replace slashes and dots in its relative path with hyphens and append `.lock.md`, then check the [lease directory](../../20_Exchange/agent-to-agent/locks/) for that name. If clear, record `lock: true`, `path`, `owner`, `acquired`, `expires`, and `intent`, then reread to confirm ownership and expiry. Wait or hand off an active lease. Handle stale leases under local rules with Human confirmation. This cooperative convention has a race window.
Retain exact prior bytes and their SHA-256. A new template vault without a configured backup location can use a unique operation directory under `.knowledgeos/backups/`, keeping the target relative path and recording the backup path and digest. Before saving, recheck the lease and baseline, or confirm absence for a new file. On conflict, stop, reread, and compare before retrying from a fresh baseline. For recovery, verify the backup digest and treat restoration as an approved native update, first preserving and checking the current version.
Reread the result and verify its digest and links. Update affected [index](../../10_Agent/wiki/index.md) entries in place, preserving other entries, groups, and order. Append only verified actions, paths, digests, and outcomes to the [log](../../10_Agent/wiki/log.md). After interrupted synchronization, reconcile actual state before filling in missing records. Release only your own leases when finished.

## Human Proposals and Handoffs

Deliver Human changes as [proposals](../templates/human-change-proposal.md) with the base digest, full Markdown, and diff for manual application. Use the [handoff template](../templates/handoff.md) to record the task, relative paths, evidence, open issues, and leases. The recipient reads the log and rechecks authorization, baselines, and leases.
