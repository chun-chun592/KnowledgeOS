> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# WB3B.3 — 最终安全架构决策

**唯一首选 A+B+C：独立身份的单写入服务、NTFS 排他写权限、版本账本与 Markdown 投影。P0-1、完整 W2/W9、生产验收和上线仍 BLOCKED。** 这是设计决策，不是实现声明。

**[源码]** 0.1.1 `update.py:390` 的正常与恢复路径共用提交：旧对象证据、备份、暂存收据 → `paths.py:264` → `_windows_fs.py:370`。同一父目录句柄内打开旧叶并校验 ID/SHA256，`_snapshot_handle` 关闭旧句柄后，第 440 行按叶名覆盖。发布后观察到新文件 ID 和数据不能证明之前覆盖了哪一个旧对象。双改名会产生缺名，不满足固定 Markdown 名称的旧→新发布。

**[历史实验，不是本轮实测]** WB3A.5→WB3B→WB3B.1→WB3B.2；最近三组各 275 项。历史双改名观察到缺名；未接生产。本轮只读源码及官方资料，无新运行实验。详见 [WB3B.2 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) 和[原设计 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)。

**[推断]** A 不阻止绕行，B 排除不受信的命名空间写者，C 提供不可变旧版本和可恢复投影。A+B 可消除限定边界内的竞争前提，C 不创造原子文件 CAS，但为恢复消除对单一旧对象的依赖。受管根、父、旧叶及元数据只能由串行服务修改，旧对象重验后执行单步发布；超时、未知对象或越界即停止。Human 直写区不提供服务条件覆盖，以受管草稿和人工合并替代。

**[待验证]** Windows 11 本地 NTFS + Python 可作为实现目标；需要 SCM 服务和受保护的 Win32 绑定环境，不需驱动或独立数据库服务器。Obsidian 的普通 Markdown 模型相容，但实际权限、保存、刷新和插件未测试。MVP 只开放受管区 New/Update/Recover，其他写入口关闭；生产版须收口所有写入口，不允许退回本地写。若不能接受独立 Human/Agent 令牌及受管区只读，维持 BLOCKED。

- [威胁模型 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) · [三路线与四组合 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)
- [API 研究 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) · [官方来源 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)
- [七阶段迁移 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) · [成本 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) · [风险与独立验收 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)

仅交付研究文档，不访问真实 Vault、不变更生产源码、测试、服务、账户、ACL、注册表或全局接入。停止于 WB3B.3，等待 Human 审阅。
