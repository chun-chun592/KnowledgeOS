# 架构决策登记 / Architecture Decision Register

[返回正式架构 / Architecture entry point](../README.md)

## ADR-01 主体与权限 / Principals and Permissions

日常 Human 与 Agent 是逻辑主体。应用层治理约束工作流程；独立 Windows 身份仅适用于选用的严格模式。\
Daily Human and Agent are logical principals. Application governance guides the workflow. Separate Windows identities apply only to optional Strict mode.

## ADR-02 内容与事务 / Content and Transactions

Markdown 为正文事实来源。Native 记录本地与观察事件，严格 SQLite COMMITTED 仅表示经验证的业务投影提交。\
Markdown is authoritative for content. Native records local and observed events. Strict SQLite COMMITTED denotes a verified business projection commit.

## ADR-03 替换与恢复 / Replacement and Recovery

保留哈希、备份与现有恢复证据。文件身份核验与替换无法构成原子比较交换；冲突或不确定时停止并对账。\
Preserve hashes, backups, and existing recovery evidence. File identity verification and replacement do not form atomic compare-and-swap. Stop and reconcile on conflict or uncertainty.

## ADR-04 可选严格投影 / Optional Strict Projection

独立的合成控制面、数据面、IPC 和角色范围继续受[严格投影补充](02_ADR04补充安全投影_ADR04-Secure-Projection-Addendum.md)约束。原生产服务绑定仍未批准，Publisher 禁用。\
The separate synthetic control plane, data plane, IPC, and roles remain limited by the [Strict projection addendum](02_ADR04补充安全投影_ADR04-Secure-Projection-Addendum.md). Production service binding remains unapproved and Publisher is disabled.

## ADR-05 同步范围 / Sync Scope

暂无内置多设备同步；旧 Writer 要求由严格模式范围解释。外部 Markdown 同步继续使用冲突检测和人工核对。\
There is no built-in multi-device sync. The older Writer requirement is limited to Strict mode. External Markdown synchronization continues to use conflict checks and review.

## ADR-06 来源与版本 / Provenance and Versions

历史候选和证据可经本地正式原件或 Git 历史追溯。发布版保留 Agent Kit 0.1.1 的来源与 MIT 声明，未把历史测试状态升级为当前验收。\
Historical candidates and evidence remain traceable in local originals or Git history. The release retains Agent Kit 0.1.1 attribution and MIT terms without promoting historical tests to current acceptance.

## v0.1.5 决策

保留 Markdown Native、双主体及原分类，增加第三个公共知识区。公共新增自主，已有公共知识与 Human 私有变更按具体批准执行。真实库 MCP／CLI 保持只读。此公共区域模型是 KnowledgeOS 自身设计。
