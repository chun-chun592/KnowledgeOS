# 部署 / Deployment

[返回正式架构 / Architecture entry point](../README.md)

## 日常安装 / Daily Installation

使用 Python 3.11+，从项目根目录运行 python -m pip install .，再使用 knowledgeos --version 与 knowledgeos --vault <vault-root> doctor。使用现有目录，无需启动 Obsidian、后台服务或管理员工具。\
Use Python 3.11+, run python -m pip install . from the project root, then check knowledgeos --version and knowledgeos --vault <vault-root> doctor. Use the existing tree without starting Obsidian, background services, or administrator tools.

## 宿主配置 / Host Configuration

CLI 和原生文件工具可独立使用。需要 MCP 时用 knowledgeos-mcp --vault <vault-root>，只传明确批准的 Human 范围，不打开真实库直写。配置及 Skill 发现参见[宿主接入](../../adapters/README.md)和[示例](../../config/knowledgeos.example.toml)。\
CLI and native file tools work independently. For MCP, use knowledgeos-mcp --vault <vault-root>, adding only approved Human scopes and leaving real-vault tool writes closed. See [host adapters](../../adapters/README.md) and [sample configuration](../../config/knowledgeos.example.toml).

## 测试根与严格模块 / Test Roots and Strict Module

测试根 Native 写入需要与受保护库分开并保留根保护。严格模式另需可选依赖、既有合成配置、独立身份和受保护 IPC。旧 Windows 部署研究不用于日常安装。\
Native test writes require a separate root and preserve protected-root checks. Strict mode separately requires optional dependencies, existing synthetic configuration, distinct principals, and protected IPC. Historical Windows deployment research does not apply to daily installation.

[目录命名及三语模板对照 / Localized paths and template mapping](../02_知识架构_Knowledge-Architecture/01_三语目录对照_Localized-Paths.md)

v0.1.5 同时同步八个 Skills、三语模板与只读运行包。无需 Obsidian 或后台服务。
