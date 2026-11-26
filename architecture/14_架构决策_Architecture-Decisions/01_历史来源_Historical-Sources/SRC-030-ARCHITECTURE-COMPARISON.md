> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# 路线比较 [设计推断]

| 维度 | A 单写者（无独立 ACL） | B ACL（无统一协议） | C 版本发布（无隔离） | A+B+C |
|---|---|---|---|---|
| 同用户非协作 | BLOCKED | CONDITIONAL 独立写令牌 | BLOCKED | CONDITIONAL 直写隔离；IPC 按令牌 |
| 不同用户 | BLOCKED 单靠 IPC 不封直写 | CONDITIONAL 最小 ACL | BLOCKED | CONDITIONAL 最小 ACL |
| 文件身份 | CONDITIONAL 协作者内 | CONDITIONAL 绑定并验证 | CONDITIONAL 哈希仅识别字节 | CONDITIONAL ID+哈希+epoch |
| TOCTOU | BLOCKED 对非协作者 | CONDITIONAL 唯一可信写者且串行 | BLOCKED 固定投影名称 | CONDITIONAL 封闭写域 |
| 多 Agent | CONDITIONAL 队列 | BLOCKED 无协调 | CONDITIONAL 原子账本提交 | NOT TESTED |
| 崩溃恢复 | CONDITIONAL 需日志 | BLOCKED 无恢复协议 | CONDITIONAL 可重放 | NOT TESTED |
| 数据完整性 | CONDITIONAL 仅协议内 | CONDITIONAL 防越权修改 | CONDITIONAL 旧版本与校验 | NOT TESTED |
| Obsidian | CONDITIONAL 保留 Markdown | NOT TESTED 保存与插件 | BLOCKED 仅 manifest；投影则 CONDITIONAL | NOT TESTED |
| 部署难度 | CONDITIONAL 服务安装 | CONDITIONAL ACL 迁移 | CONDITIONAL 数据引导 | NOT TESTED 全链部署 |
| 维护成本 | CONDITIONAL 服务维护 | CONDITIONAL ACL 漂移检查 | CONDITIONAL 账本与 GC | NOT TESTED |
| 迁移成本 | CONDITIONAL CLI 改道 | CONDITIONAL 权限转换 | CONDITIONAL 导入旧记录 | NOT TESTED |
| 长期可维护 | CONDITIONAL 无直写承诺 | CONDITIONAL 身份治理 | CONDITIONAL 账本协议稳定 | CONDITIONAL 单运行时、无内核组件 |

PASS 仅用于已实现且有相应证据的能力；无目标架构 PASS。CONDITIONAL 表示可行条件，不等同实测；NOT TESTED 不暗示条件已满足。

## A：入口、授权和可用性

OpenCode/Claude Code 保留 Skill → Python CLI 调用，CLI 发版本化本地 Named Pipe 请求；每 Vault 一个有界写队列，可并行接收但不能并行发布。同 token 的服务不能建立直写边界。管道显式 DACL、拒绝远端、限流/体积/超时；读取消息后以系统令牌核验 SID 与角色，失败拒绝，恢复服务令牌后才执行经授权动作。绝不将客户端上送路径、PID、自报 ID 或配置视作授权。服务端注册 Vault ID、白名单动作、相对路径与基础版本；输入文件通过字节提交，不让服务替客户端读取任意本地路径。只读与写入角色可分端点；客户端还须验证端点属于可信服务，首次创建标志不单独证明服务身份。请求按 Vault+主体+请求 ID 唯一，绑定规范化入参摘要；重试返回同结果，不同摘要冲突，响应丢失查结果。`ncalrpc` 是备选，不同时维护两套 IPC。

SCM 重启、启动恢复、离线只读、备份恢复降低停机；不是消除单点。升级暂停接单、排空或持久化、关闭旧写者并确认退出，验证 schema/epoch 后恢复。严禁双主动和本地写兜底。Windows 虚拟服务账户作为首选候选（无交互凭据），需验证实际令牌和服务 DACL。

## B：可执行的权限设计

受保护祖先到受管叶完整核验：目录的添加及删除子项能力、对象删除/写数据/写安全描述符、所有者与宽泛继承组都需检查。受管根不能由日常用户改名、移动或替换；暂存与目标统一模板，不能指望移动时重新继承。审核已存在对象、显式 ACE、别名/链接、挂载和同卷边界；保持句柄绑定与拒绝异常对象（不因 ACL 通过而略过）。迁移前保存 DACL、所有者和必要 SACL、快照及验收基线，撤销旧写权限前先停止旧程序并确认句柄关闭。备份运行身份最小权限；还原仅离线可信维护，复验 ACL 后接客。

Human 照常编辑 Human 子树并写 `.obsidian` 是设计目标；顶层重命名、跨区拖动、受管 Markdown 保存、同步插件覆盖不是原样兼容。插件继承 Obsidian 权限，限定可信插件/隔离测试。需要清晰的只读区提示与人工合并路径，不承诺使用习惯零变化。

## C：版本账本与普通 Markdown

用服务私有 SQLite 单库事务存当前逻辑版本、不可变内容（初期 BLOB）、请求、投影状态和审计待办。新版本唯一键与父版本比较在同一 DB 事务完成，不覆盖旧版本；重复内容可去重但必须核验字节。MVP 先明确持久 PREPARED 及版本对象 → 对受管 Markdown 做单次投影 → 核验对象和内容 → 同库更新可见版本、结果和审计待办；成功响应只在验证和终态提交后。读 API 以已提交账本为准，Obsidian 可能先看到新投影，不能承诺两个视图同一瞬间改变。不能把 DB 与文件系统当作一个事务。

启动阻止新写：旧投影匹配经验证的基线则继续；新投影匹配已登记的阶段对象和哈希则补记；缺失、异常或证据不足则 NEEDS_REVIEW，不按相同字节猜身份。衍生 Index/Log 通过版本水位和去重待办重建，不标作多文件原子。回滚创建新恢复版本；GC 仅清理无可达版本、无挂起意图或备份保留要求的数据。SHA256 内容寻址不保护路径或 ACL。外部更改受管投影视为完整性事件；Human 独立区只读导入快照或人工合并，不自动反写。单文件固定名称继续供 Obsidian 链接与索引；批准的直接编辑不能边直写边享有排他边界。

## 组合取舍

| 组合 | 安全与恢复 | 实现/成本与性能 | 部署与维护/兼容 |
|---|---|---|---|
| A+B | 封闭写域；现有收据仍需增强 | 中；串行 + IPC；可作骨架 | 身份和 ACL 部署；普通 Markdown 保留；恢复风险留存 |
| A+C | 对协作者有可恢复性，不能信任未隔离投影/账本 | 中；DB 与投影双写成本 | 无有效直写边界；漂移需人工处理 |
| B+C | 受管存储可保护，但直接授予多个业务程序服务级权能破坏统一授权 | 中高；另需调度/恢复宿主 | ACL 和 schema 都要运维；若加统一代理即接近首选 |
| A+B+C | OS 排他 + 请求授权 + 可重放版本 | 最高；限制队列与版本保留，基准验证 I/O 和延迟 | 服务升级、ACL 漂移检查和 DB 迁移；固定 Markdown 路径，明确只读区 |
