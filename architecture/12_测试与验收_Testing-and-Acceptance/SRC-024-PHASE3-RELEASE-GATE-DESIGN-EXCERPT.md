> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../README.md) for current applicability.

# 历史设计摘录

来源：Architecture-Frozen / 12-Testing-and-Acceptance / historical-source / SRC-024-PHASE3-RELEASE-GATE.md

## 4. 限定模式（当前即可放行的使用方式）

在 P0 修复前，以下部署方式的风险可控，**不构成发布行为**，属使用建议：

1. 单 Agent、Agent 区域读写、Human 区域只读（盲测与探针均验证此默认路径）；
2. CLI 为唯一写入入口（宿主集成不得绕过 CLI 直调库层写函数）；
3. 崩溃后的人工预案：等 300s 或回拨孤儿锁后 `recover`/重试；每日跑 `index --check` + `lint`；
4. 不开启 Human 写入（`human_authority` 保持无 Provider）；
5. 高价值数据依赖外部备份（.git/Obsidian 同步），不依赖 `.knowledgeos/backups` 单一防线。
