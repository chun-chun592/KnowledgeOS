# KnowledgeOS

[简体中文](README.zh-CN.md)

KnowledgeOS helps you and your agents turn existing notes and source material into reusable knowledge. It works with a shared Markdown folder. Open the notes in any editor or file manager. Obsidian is optional and can stay closed.

## Architecture

The [formal architecture](architecture/README.md) documents the existing Markdown layout, Human and Agent roles, Skills and tool selection, knowledge workflows, and the separate Strict mode contracts.

## What you can do

- Find relevant notes, follow their links, and check for overlap before creating a new page.
- Summarize new sources, combine them with existing knowledge, and update a note while preserving citations and metadata.
- Maintain the Agent index and activity log. Use hashes and backups to check conflicts and recover older content.
- Ask for a Human note change proposal with complete Markdown, a unified diff and the original SHA-256.

Markdown is the source of truth. Human and Agent are logical knowledge owners. Humans edit their own notes directly. Agents read explicitly opened Human scopes and write in approved Agent scopes. Apply Human proposals manually after checking the base hash.

## Start with an existing knowledge folder

1. Install Python 3.11 or newer and run `python -m pip install .` from this project. Run `knowledgeos --version` to confirm the installation.
2. Use the existing folder containing `10_Agent/wiki`. Keep the folder structure and read its `AGENTS.md` and linked policies first.
3. Set up one tool path below, then ask the agent a normal question.

MCP starts in read-only mode:

```text
knowledgeos-mcp --vault <vault-root>
```

If a Human subdirectory has already been approved, append `--human-read 00_Human/Resources` or the exact approved relative scope. Add no Human read scope by default. On a CLI-only host, pipe the following JSON to `python write_client.py --vault <vault-root> inspect`.

```json
{"tool":"search_knowledge","arguments":{"query":"MCP"}}
```

## Connect an Agent Host

Register `knowledgeos-mcp` from the installed environment as a local **stdio** MCP server, with `--vault` and the root as separate arguments. Keep machine-specific values in local configuration. Use the host's Skills discovery mechanism to expose `skills/<name>/SKILL.md`. Seven task Skills and an optional umbrella Skill are available. [Host adapters](adapters/README.md)

| Host | Where to configure it |
| --- | --- |
| Codex | Add a `[mcp_servers.knowledgeos]` entry with `command` and `args` in the project Codex configuration. [MCP guide](https://developers.openai.com/codex/mcp) |
| OpenCode | Register a local server in the version-appropriate OpenCode project configuration. [MCP guide](https://opencode.ai/docs/mcp-servers/) |
| Claude Code | Register a local stdio server with `claude mcp add`; choose the appropriate scope. [MCP guide](https://code.claude.com/docs/en/mcp) |

Try “Find our existing notes on this topic and show what overlaps,” “Integrate these sources into the existing Agent note and keep citations,” or “Draft a change to this Human note and show me the diff.”

## Daily writes and limits

**Markdown Native is the recommended daily workflow.** The real vault currently uses authorized native file edits in the Agent wiki. Follow the vault's lease, backup, SHA-256, index and log rules. MCP and CLI direct writes to the real vault are unavailable. Native edits and filesystem observations do not produce Strict Writer SQLite commits. These boundaries are application rules.

For a **separate approved test root**, set `KNOWLEDGEOS_PROTECTED_VAULT` to your protected vault path, then use `python markdown_native.py --vault <test-root> sync` or start the MCP server with `--native-write`. Test-root create, update, delete and restore use scoped file rules. External edits are detected by a later sync and can race with other editors.

### Installed CLI

`knowledgeos --vault <vault-root> doctor` reports readable scopes. Use `query` for search and `inspect` for structured reads and Human proposals. The [configuration example](config/knowledgeos.example.toml) can be copied to a private location and supplied with `--config`.

`ingest` drafts a source page, and `synthesize` drafts a scaffold from at least two notes. They require `--apply` for writes to an approved test root. Intake preserves an original by digest and records provenance. The original can remain if creating the source page later fails. `append-section` and `archive` check the base SHA-256. Archive sets the note status while keeping its path, and `restore` uses a backup hash. Start with the [examples](examples/README.md) or [English, Simplified Chinese, and bilingual vault templates](vault-template/README.md).

### Advanced option: Strict mode

Strict mode uses separate Windows principals, Broker, Secure Writer and SQLite. It requires `pywin32`, a trusted synthetic deployment, a protected-root setting and preconfigured identities and ACLs. Configure the server with `--synthetic-write-config` for that environment. Publisher stays disabled. [Formal architecture](architecture/README.md)

## Project and attribution

KnowledgeOS 0.1.3 integrates Core source from Agent Kit 0.1.1. The upstream MIT notice is retained. [License](LICENSE) · [Changes](CHANGELOG.md)
