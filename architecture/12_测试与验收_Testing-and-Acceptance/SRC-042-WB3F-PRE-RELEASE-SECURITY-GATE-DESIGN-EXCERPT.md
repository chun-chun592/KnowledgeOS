> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../README.md) for current applicability.

# 历史设计摘录

来源：Architecture-Frozen / 12-Testing-and-Acceptance / historical-source / SRC-042-WB3F-PRE-RELEASE-SECURITY-GATE.md

## 阶段可见性

独立合成 fixture 继承候选 Vault 的角色 ACL。真实 Writer 进程使用写入、DELETE、READ_ATTRIBUTES 与证据用 READ_CONTROL，设置 FILE_SHARE_READ。三个身份以 GENERIC_READ、全共享通过固定路径作原生打开。Writer 通过管道输入同步停在状态边界。数字来自真实 NTFS，不代表完整 Writer 事务已运行。每条记录包含 SID/PID、访问及共享掩码、原始错误、字节数、SHA-256、卷/FILE_ID 和可取得的 Owner/DACL。

| 阶段 | Writer | Agent | Unauthorized | 证据限定 |
|---|---|---|---|---|
| 刚创建，0 字节 | 0，0 字节 | 0，0 字节 | 5 | 持有写入源句柄时实测 |
| 内容写入中 | 0，8 字节 | 0，8 字节 | 5 | 两次写入间同步，实测部分内容 |
| 已刷写，发布前 | 0，17 字节 | 0，17 字节 | 5 | FlushFileBuffers 后暂停，实测完整新内容 |
| 已持久化 PREPARED | 未独立实测 | 源码显示仍为相同句柄和 ACL | 未独立实测 | 实验没有 SQLite 事务，不能判定此业务时点已测 |
| rename 调用期间 | 未实测 | 未实测 | 未实测 | 此次同步只覆盖调用前后，没有证明重叠 |
| rename 成功，源句柄未关闭 | 0，17 字节 | 0，17 字节 | 5 | 新目标 ID 等于原暂存 ID，旧暂存名返回 2 |
| 失败并进入 NEEDS_REVIEW | 未实测 | 保留已记录暂存内容是既有行为，是否可读仍需正式探针 | 未实测 | 不以人工构造状态代替正式失败 |

独立原语可见性判定为 FAIL，部分内容和刷写后的完整新内容都在发布前可读。冻结实现 _windows_fs.py:399–426 从创建暂存对象起启用相同的读取共享，创建时继承目标目录 ACL；434–450 在调用公开 API 之前还要求旧目标和暂存安全描述符一致。实验中旧目标、普通暂存和发布后的对象具有相同 Owner 与 DACL，发布后以原暂存 FILE_ID 出现。已知名称的直接打开不依赖目录可列举性。

## 私有暂存替代与连续性

仅使用新 fixture 验证私有目录。首轮 ACL 设置没有移除 Agent ACE，原始成功打开结果保留为准备失败，不能作为私有设计证据。校正新目录 ACL 并确认 Agent ACE 不再存在后重新试验。发布前旧目标可读 13 字节，私有暂存返回 Win32 5。使用同卷 FileRenameInfoEx 成功替换，暂存 ID 保留，原暂存名返回 2，Agent 打开新目标仍返回 5。显式比较保留了私有描述符。由此排除“仅移动到正式目录就自动获得批准读取权限”的修复。没有实施事后改 ACL，也未证明可在同一原子操作中完成名称及 ACL 切换。

本轮单步发布连续性标记 NOT TESTED：名称切换后的单次读取已实测，但未重跑服务压力。冻结的已测绑定历史为 30 次更新、303,232 次读取、114 次与 rename 包装调用相交，零观测错误。不能将这组结果用于证明暂存保密。推荐维持严格的不提前可读目标，并请 Human 决定是否接受更窄的可见性合同，或等待一种获得独立证据的替代实现。在合同确定且验收前，不合并现有共享修复至生产。无修复补丁交付。 [微软同卷移动权限说明](https://learn.microsoft.com/en-us/troubleshoot/windows-client/windows-security/permissions-on-copying-moving-files) · [微软路径遍历权限说明](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/bypass-traverse-checking)

## P1-2 与管理员审计

P1-2 PARTIAL。已复核冻结的真实管道 Token、运行时 ACL/策略漂移及同卷探测证据。本轮三个真实角色的读取结果补充验证读权限差异。祖先有效权限和持续身份变化、离线恢复的监督证明及真实不支持卷/过滤器仍需独立验收。目标预检和替换没有原子 FILE_ID CAS；本轮不复现竞态或推断未知目标受到原子保护。

管理员恢复审计 PARTIAL。writer_service.py:56–61、105–109 和 secure_ledger.py:733–757 将批准绑定 Vault、事务和动作，但 approval 是非空字符串，无唯一性、有效期或消费记录。已完成事务因状态无法再次 apply；原批准文件本身在仍满足先决条件时可复用，inspect 没有单次消费语义。现有 stdout 事件可收集，不能提供耐久、完整的批准／执行／失败／重试链。后续设计需绑定唯一批准 ID、签发人、到期时间、精确范围和尝试收据，保存中断与失败，避免把重试误认为新授权。整库失败关闭保持，禁止自动清除 NEEDS_REVIEW。
