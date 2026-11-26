# Agent Host adapters

- Codex uses the project's MCP server configuration and its supported Skills directory.
- OpenCode registers a local stdio MCP server in its project configuration.
- Claude Code can register a local stdio server with its MCP command.

Use the installed Python environment and the command knowledgeos-mcp with the arguments --vault and the local vault root. Add --human-read separately for each approved scope. The actual vault path stays in local configuration. Expose skills from the project's skills directory through the host's documented discovery mechanism. The optional umbrella Skill routes among the independent Skills.
