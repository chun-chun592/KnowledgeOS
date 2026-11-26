# Choose a KnowledgeOS vault template

Copy the contents of one complete template into an empty directory. Keep AGENTS.md at the root.

- [English](en-US/README.md)
- [中文](zh-CN/使用说明.md)
- [Bilingual / 中英双语](zh-en/README_使用说明.md)
- [中文使用说明](README.zh-CN.md)

Existing English vaults keep their current paths. For scripts referencing the former template root, use vault-template/en-US. Do not overlay or rename an existing vault. Set each Human read grant to the actual localized relative directory. The layout does not constrain the language of notes.

The CLI detects the standard layout using region names. Use `knowledgeos --vault <path> doctor` to check it. For a development scaffold, `knowledgeos --vault <empty-path> init --locale zh-CN` selects the layout. Copy a full template for the complete files. MCP and CLI writes remain limited to approved separate test roots. Optional Strict mode keeps its en-US synthetic contract.
