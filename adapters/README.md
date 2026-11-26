# 宿主接入 / Agent Host Adapters

在有权访问目标知识目录的项目中安装 KnowledgeOS。可只使用 CLI 与原生文件工具，也可按需添加本地 MCP；两者均沿用 Vault 的读取范围及工作协议。+Install KnowledgeOS in a project authorized to access the target knowledge directory. Use the CLI and native file tools, or add local MCP when useful. Both follow the vault's read scopes and working rules.

下例的 `./vault` 是宿主工作目录下的示例路径。换成实际已批准的知识根，机器路径只保存在本地配置。+In these examples, `./vault` is relative to the host's working directory. Use your approved knowledge root and keep machine-specific paths in local configuration.

## CLI 和 Skills / CLI and Skills

```sh
python -m pip install .
knowledgeos --vault ./vault doctor
knowledgeos --vault ./vault query "topic"
```

读取目标 Vault 的 `AGENTS.md`，将所需的 [Skill 目录](../skills) 整体放入宿主的项目发现位置。七个独立 Skills 可按需组合，`knowledgeos` 总入口可选。+Read the target vault's `AGENTS.md` and place the selected [Skill directories](../skills) in the host's project discovery location. Combine the seven task Skills as needed, with an optional `knowledgeos` router.

| 宿主 / Host | 项目 Skills / Project Skills | 可选 MCP / Optional MCP |
| --- | --- | --- |
| Codex | `.agents/skills/<name>/SKILL.md` | `.codex/config.toml` |
| OpenCode | `.opencode/skills/<name>/SKILL.md` | `opencode mcp add` |
| Claude Code | `.claude/skills/<name>/SKILL.md` | `claude mcp add` |

### Codex

在项目 `.codex/config.toml` 添加以下服务。+Add this server to the project `.codex/config.toml`. [MCP guide](https://developers.openai.com/codex/mcp)

```toml
[mcp_servers.knowledgeos]
command = "knowledgeos-mcp"
args = ["--vault", "./vault"]
```

### OpenCode

使用本地 stdio 服务。OpenCode v2 手动配置使用 `mcp.servers`，其他版本应按该版本文档配置。+Use a local stdio server. OpenCode v2 manual configuration uses `mcp.servers`; follow the documentation for other versions. [MCP](https://opencode.ai/docs/mcp-servers/) · [Skills](https://opencode.ai/docs/skills/)

```sh
opencode mcp add knowledgeos -- knowledgeos-mcp --vault ./vault
```

### Claude Code

在目标项目选择所需配置范围并注册 stdio 服务。+Register the stdio server in the target project with the appropriate scope. [MCP](https://code.claude.com/docs/en/mcp) · [Skills](https://code.claude.com/docs/en/skills)

```sh
claude mcp add --transport stdio --scope local knowledgeos -- knowledgeos-mcp --vault ./vault
```

命令不可发现时，在宿主本地配置中使用 Python 安装环境的实际 executable 路径。确有 Human 子目录读取授权时，才显式追加 `--human-read`。真实库的 MCP／CLI 仍只读，获准写入沿用 [原生文件工作流](../architecture/README.md)。+If the command cannot be found, configure the installed executable path locally. Add `--human-read` only for explicitly approved Human subdirectories. Real-vault MCP and CLI access remains read-only, with approved writes following the [native file workflow](../architecture/README.md).
