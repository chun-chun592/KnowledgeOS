> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

<!-- 发布处理：仅泛化机器绑定路径和卷标 / Publication edit: machine paths and volume letters generalized -->

# 控制面与数据面决策

**唯一判定 PARTIAL。** 候选是 受保护控制目录 控制面配合 数据卷 上尚未创建的独立直属数据根。仅批准架构审阅，保留启动和发布门禁。

| 边界 | 设计授权 |
|---|---|
| 控制卷 控制面 | 仅放 Broker 二进制、可信配置和启动身份绑定；受监督管理员／SYSTEM 维护，服务只读必要文件。绑定 数据卷 卷、根 FILE_ID、预期 Owner／DACL 及策略版本。控制卷 的保护证据不能用于批准 数据卷 数据面 |
| 数据卷 实验根 | 受监督创建，根与信任子目录保护 DACL。普通主体不能获得容器的删除子项权或改安全；按句柄核验所有目录稳定性 |
| 私有暂存与封存 | 仅 Broker 得到批准的合成文件写、刷盘、核验和封存权。Agent 与普通 Writer 无直接私有文件能力 |
| 合成投影 | 位于与暂存同一 数据卷 卷，普通 Writer、Agent 无直接写删及替换权限。Publisher 权限未评估，发布保持禁用 |
| 业务账本与审计 | Writer 只拥有独立业务账本所需权；Broker 只拥有自身审计所需权。各目录的父级权限不得扩散到其他职责。需要向 Agent 开放读时沿用有限提前可见性合同 |

改变权限或启用前必须由 Human 批准实际创建方式、Owner 和 SID 权限配置，并获得 Windows／NTFS 的同次创建证据、首个新目录句柄和跨 Token 有效权限证据。名称被占、权限漂移、卷或身份不匹配即停。缺少证据时不启用，不放宽合同。

WB3E PARTIAL，365 PASS、2 BLOCKED。WB3F 原正式开发准入未通过，受控工程候选 NOT READY，76061ab 冻结，Secure Mode 生产安全 BLOCKED。
