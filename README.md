# KnowledgeOS

[简体中文](README.zh-CN.md)

KnowledgeOS helps you and your agents turn existing notes and source material into reusable knowledge. It works with a shared Markdown folder. Open the notes in any editor or file manager. Obsidian is optional and can stay closed.

## What you can do

- Find relevant notes, follow their links, and check for overlap before creating a new page.
- Summarize new sources, combine them with existing knowledge, and update a note while preserving citations and metadata.
- Maintain the Agent index and activity log. Use hashes and backups to check conflicts and recover older content.
- Ask for a Human note change proposal with complete Markdown, a unified diff and the original SHA-256.

Markdown is the source of truth. Human and Agent are logical knowledge owners. Humans edit their own notes directly. Agents read explicitly opened Human scopes and write in approved Agent scopes. Apply Human proposals manually after checking the base hash.

## Start with an existing knowledge folder

1. Install Python 3.11 or newer and run `python -m pip install -r requirements.txt` from this project.
2. Use the existing folder containing `10_Agent/wiki`. Keep the folder structure and read its `AGENTS.md` and linked policies first.
3. Set up one tool path below, then ask the agent a normal question.

MCP starts in read-only mode:

```text
python -B server.py --vault <vault-root>
```

If a Human subdirectory has already been approved, append `--human-read 00_Human/Resources` or the exact approved relative scope. Add no Human read scope by default. On a CLI-only host, pipe the following JSON to `python write_client.py --vault <vault-root> inspect`.

```json
{"tool":"search_knowledge","arguments":{"query":"MCP"}}
```

## Connect an Agent Host

Register a local **stdio** MCP server using the Python interpreter that has the dependencies installed. Pass `-B <project>/server.py --vault <vault-root>` as separate arguments and keep machine-specific values in your local configuration. Use each host's own Skills discovery method to expose the relevant `skills/<name>/SKILL.md` files. Agents can select and combine Skills by task and fall back to CLI or native file tools.

| Host | Where to configure it |
| --- | --- |
| Codex | Add a `[mcp_servers.knowledgeos]` entry with `command` and `args` in the project Codex configuration. [MCP guide](https://developers.openai.com/codex/mcp) |
| OpenCode | Register a local server in the version-appropriate OpenCode project configuration. [MCP guide](https://opencode.ai/docs/mcp-servers/) |
| Claude Code | Register a local stdio server with `claude mcp add`; choose the appropriate scope. [MCP guide](https://code.claude.com/docs/en/mcp) |

Try “Find our existing notes on this topic and show what overlaps,” “Integrate these sources into the existing Agent note and keep citations,” or “Draft a change to this Human note and show me the diff.”

## Daily writes and limits

**Markdown Native is the recommended daily workflow.** The real vault currently uses authorized native file edits in the Agent wiki. Follow the vault's lease, backup, SHA-256, index and log rules. MCP and CLI direct writes to the real vault are unavailable. Native edits and filesystem observations do not produce Strict Writer SQLite commits. These boundaries are application rules.

For a **separate approved test root**, set `KNOWLEDGEOS_PROTECTED_VAULT` to your protected vault path, then use `python markdown_native.py --vault <test-root> sync` or start the MCP server with `--native-write`. Test-root create, update, delete and restore use scoped file rules. External edits are detected by a later sync and can race with other editors.

### Advanced option: Strict mode

Strict mode uses separate Windows principals, Broker, Secure Writer and SQLite. It requires `pywin32`, a trusted synthetic deployment, a protected-root setting and preconfigured identities and ACLs. Configure the server with `--synthetic-write-config` for that environment. Publisher stays disabled. [Architecture](docs/Architecture.md)

## Project and attribution

The project is pending GitHub publication. Bundled Core modules originate from the KnowledgeOS Agent Kit and retain their MIT license. [Upstream license](knowledgeos/LICENSE)
