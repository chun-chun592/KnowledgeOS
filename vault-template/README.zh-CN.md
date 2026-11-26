# 选择知识库模板

将 [中文版](zh-CN/使用说明.md)、[英文版](en-US/README.md) 或 [中英双语版](zh-en/README_使用说明.md) 中任一完整模板复制到空目录，根目录保留 AGENTS.md。现有英文库继续使用原路径；引用旧模板根的脚本改用 vault-template/en-US。已有知识库无需覆盖或迁移。Human 读取授权必须使用对应版本的实际相对路径，笔记正文可使用任意语言。

CLI 根据标准区域目录识别布局。用 `knowledgeos --vault <路径> doctor` 检查；开发骨架可用 `knowledgeos --vault <空目录> init --locale zh-CN`。完整文档请复制对应模板。MCP 和 CLI 写入仍只用于获准的独立测试根。可选严格模式沿用 en-US 合成环境契约。
