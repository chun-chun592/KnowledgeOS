> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# KnowledgeOS WB3F 技术设计

**状态：只读设计草案，等待 Human 审阅。** WB3E 冻结为 365 PASS、2 BLOCKED，整体验收 PARTIAL。WB3F 正式开发与 Secure Mode 生产安全均为 BLOCKED。

## 1. 现有实现与设计决策

WB3D.4 的 Secure Update 在 secure_ledger.py 中校验当前账本头、预期版本、目标文件身份和摘要。它先落盘不可变对象，在目标同目录创建并刷写暂存文件，再把暂存名和身份写入 PREPARED。_windows_fs.py 的 guarded_replace 将验证过的旧句柄重命名至唯一备份名，再以禁止覆盖的方式将暂存文件发布到原名。两次重命名之间目标名缺失。第二步遇到已经存在的目标会拒绝覆盖。现有恢复能检查备份、暂存及最终投影。

WB3D.4.1 验证了在受测本机 NTFS 上，一次 POSIX 句柄重命名可以用暂存对象替换目标名。WB3E 后续跨 SID 独立实验观察到 100 次发布、50,000 次读取，其中 1,178 次与发布重叠，未出现缺名、共享冲突、部分正文或未知摘要。该证据仅对应独立实验及受测环境。已有旧对象句柄与发布后新打开的同名句柄可以看到不同的完整版本。WB3D.4.1 的公开 API 绝对路径变体成功，公开相对变体没有建立所需的句柄锚定。Native 相对变体是单独的研究分支。

**建议**仅为通过准入的本机 NTFS Secure Update 引入单步投影策略。沿用 Named Pipe 身份验证、Writer 单写者保护、账本版本检查、对象存储和暂存管理。Secure New 继续使用禁止覆盖的发布。Standard、Log 和 Index 的发布路径保持原样。若目标目录的锚定或有效写权限证明不足，候选禁止选用单步策略。

最小改动范围为 _windows_fs.py 的专用受管投影入口、secure_ledger.py 内 Update 的策略分派和恢复检查、账本兼容迁移及配套测试。公共 CLI 和管道协议保持现有形态。发布策略由受信任部署配置决定，不接受 Agent 参数或可写环境变量作为授权来源。设计先验证公开 API 路径；若公开方式无法满足目录稳定性要求，提交独立设计审查后才评估 Native 接口，禁止运行时自动切换。

## 2. API 合同、兼容性与失败处理

- 公共入口使用 SetFileInformationByHandle，信息类别为 FileRenameInfoEx，Windows SDK 结构为 FILE_RENAME_INFO。只使用 REPLACE_IF_EXISTS 和 POSIX_SEMANTICS。暂存句柄具备 DELETE 权限，暂存和目标在同一 NTFS 卷和同一受管目录。采用正确的 ABI 对齐和 UTF-16 字节长度。避免依赖当前目录，不接受 ADS、设备路径或未审核的别名。公共类别和 Native 信息类别分别绑定，不能交换数值。 [Microsoft API](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle) · [信息类别](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ne-minwinbase-file_info_by_handle_class) · [FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info)
- 首版支持范围限定为通过独立验收的 Windows 构建、架构、实际 NTFS 卷及 Writer Token。启动时在同卷受控临时对象上探测所选 API 和打开行为，测试进程身份与实际 Writer 一致，验证失败即关闭该能力。SDK 结构可编译或系统导出函数存在仅说明接口可加载。SMB、ReFS、FAT、其他架构和未验收的文件系统过滤器组合保持禁用。微软 Native 和协议文档各有适用范围，权限和标志行为需在本机目标配置实测。 [Microsoft Native 结构与标志](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/ns-ntifs-_file_rename_information) · [Microsoft 文件系统协议](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/4217551b-d2c0-42cb-9dc1-69a716cf6d0c)
- 沿用受控的父目录句柄链和规范路径检查，审查父目录以及祖先的删除、替换、ACL 和所有权权限。公开绝对路径方案只在可证明路径稳定的部署中启用。验证目标与暂存的卷标识、FILE_ID、规范路径、单链接约束、SHA-256 和安全描述符。暂存对象已继承正确 ACL 后才允许发布，发布后再次验证投影 ACL 和所有者。撤销兼容性探测能力或目录权限变化时暂停新 Update。
- 删除共享语义必须纳入兼容性测试。拒绝共享删除的句柄、过滤器和属性限制可能阻止操作。禁止扩大 Writer 特权、忽略只读属性、削弱 DACL，禁止通过先删目标再重命名绕过失败。对无副作用且已证实的短时共享冲突，在期限内重新获取现场证据后可限次重试。权限拒绝或不支持单独报告；任何结果不明确先执行只读对账。保留原始 Win32 错误、阶段、事务 ID 和是否曾调用 API。禁止将 Win32 5 一概按暂时失败处理。
- 单次替换的命名空间结果、进程退出恢复和断电持久性分别验收。暂存内容刷写和现有 SQLite synchronous=FULL 保留，不能据此推断跨文件事务或断电下目录元数据的写入顺序。 [Microsoft SetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle)

### 2.1 Win32 绑定和错误记录

| 合同项 | 实施要求 |
|---|---|
| API 和标志 | 调用 SetFileInformationByHandle，信息类别为 FileRenameInfoEx。使用 FILE_RENAME_INFO 的 Flags 成员，将 FILE_RENAME_FLAG_REPLACE_IF_EXISTS (0x00000001) 与 FILE_RENAME_FLAG_POSIX_SEMANTICS (0x00000002) 组合。两者均属重命名结构，不能用创建句柄的标志替代。 |
| ABI 和长度 | 以目标 Windows SDK 头文件与进程位宽核对本机对齐、字段偏移、HANDLE 宽度和最小结构尺寸。缓冲区清零，在 FileName 偏移填入 UTF-16LE 名称，预留终止 WCHAR。FileNameLength 是名称字节数，排除终止符，dwBufferSize 是实际缓冲区大小。验证长路径及代理对。 |
| RootDirectory | 首版公开绝对路径候选使用规范绝对路径，RootDirectory 为 NULL，不依赖当前目录。相对方案必须绑定已验证的父目录句柄，并独立实证所选接口确实按该句柄解析。WB3D.4.1 公开相对变体尚未达到这个标准。 |
| 权限 | 暂存源句柄必须以 DELETE 权限打开。Writer 对父目录须有遍历、创建文件项（FILE_ADD_FILE）及替换所需有效权限。替换涉及目标 DELETE 或可适用的父目录 FILE_DELETE_CHILD，同时受实际 ACL、拒绝 ACE、令牌和卷行为约束。 |
| 共享和过滤器 | 分别验证 FILE_SHARE_READ、FILE_SHARE_WRITE、FILE_SHARE_DELETE，记录旧目标已打开、无删除共享及过滤器介入时的行为。仅在通过实测的配置中承诺旧句柄继续访问旧对象，新的路径打开访问新对象。 |
| 返回与错误 | BOOL 非零记录成功返回并复核投影。BOOL 为零立即在同一线程读取 GetLastError，早于其他 API、清理和日志。原样保存数值、事务 ID、阶段、构建与卷，再进行应用层映射。失败码本身不证明无副作用。 |

探测失败、权限漂移、调用失败及结果不确定均禁止自动切换至旧两阶段发布。 [Win32 API](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle) · [FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info) · [重命名标志语义](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/ns-ntifs-_file_rename_information) · [有效访问权限](https://learn.microsoft.com/en-us/windows/win32/fileio/file-access-rights-constants)

## 3. FILE_ID CAS 边界

文件身份检查和单次替换是两个独立操作。FileRenameInfoEx 没有“仅当当前目标的 FILE_ID 等于预期值才替换”的条件参数。固定父目录范围可减小路径解析歧义，旧对象句柄也可用于核对曾经打开的文件；两者均不能把目标身份条件附加到替换上。事后看到暂存 ID 只能识别最终投影，无法证明调用前没有出现其他目标。

因此单步策略要求 Writer 是受管目录唯一的非特权直接写入身份，并通过独立验收核对文件、目录、DELETE_CHILD、ACL、所有权、别名、重解析点和共享目录。Writer 同 SID 的其他进程、等效写入主体、管理员、SYSTEM 和内核级主体超出隔离保证。任何需要在存在等效直写者时保证「未知文件绝不被覆盖」的部署，都不得启用该策略。两阶段缺名窗口与单步缺少原子 CAS 是不同风险，不能用前者消失解释后者解决。

### 3.1 启用前强制安全不变量

- 以真实 Token 证明 Writer 有必要的最小受管写权限，且是唯一获准直接写入的非特权身份。Agent 和 Unauthorized 无法直接写入、删除或替换目标，也无法通过父目录、ACL 修改或所有权取得这些能力。
- 验证所有受管目录、目标、暂存及其祖先的有效 ACL、Owner、继承和父目录 FILE_DELETE_CHILD。检查重解析点、链接、别名及父目录身份。验证配置须与实际进程令牌和操作结果一致。
- 同 Writer SID 的其他进程、等效直接写入主体和高权限进程均超出已证明的隔离范围。发布前 FILE_ID 检查和替换分别执行，无法提供原子 CAS。
- 无法证明当前配置符合限定威胁模型时，单步策略保持禁用。运行中发现漂移即暂停新单步 Update，未决事务只读对账或进入 NEEDS_REVIEW。

## 4. 持久状态机与恢复

沿用 REQUEST_ACCEPTED → VALIDATED → OBJECT_STORED → PREPARED → PROJECTED → COMMITTED。NEEDS_REVIEW、REJECTED、NOOP 沿用既有含义。内存中的 API 调用开始、返回和客户端响应事件用于诊断；恢复只依赖持久证据。

1. REQUEST_ACCEPTED 记录真实主体、操作键和规范请求指纹。VALIDATED 固定预期账本头、父目录身份、旧投影身份和摘要，以及新内容摘要。
2. OBJECT_STORED 验证新对象和旧提交的不可变对象可读、摘要正确。旧版本的保留引用必须在替换之前可靠可用。单步分支不创建使原名缺失的重命名备份。逻辑恢复使用已验证旧对象；若业务要求保留原文件身份或额外 NTFS 元数据，须先明确该需求及存储方式，首版不隐含提供。
3. PREPARED 以 SQLite 原子提交记录策略版本、旧版本引用、父目录和目标旧身份、暂存身份与摘要。暂存与旧内容引用应留到恢复可判定时。建议将策略字段与现有 schema 迁移绑定，旧记录显式按原策略处理。PREPARED 成功持久化之后才允许调用替换。
4. 调用返回后重开规范目标，核对父目录、卷、暂存 ID、摘要与 ACL。仅全部一致时进入 PROJECTED。以账本原子事务提交 COMMITTED 和可重放的成功结果。派生输出的待修复状态单独保存或从提交和水位推导。

| 恢复时可验证事实 | 处理 |
|---|---|
| PREPARED，旧身份与摘要仍在，暂存身份与摘要完整，账本头和授权仍有效 | 依 4.1 核对调用证据。只有能确认未发布时才按同一策略继续，每次调用前重核权限与环境。 |
| PREPARED 或 PROJECTED，目标为记录的暂存 ID 且摘要和 ACL 一致，父目录及版本链一致 | 不再重命名，补齐 PROJECTED 和唯一 COMMITTED 记录。 |
| 单步 Update 目标缺失、未知身份、相同摘要但不同 ID、父目录改变、证据冲突或无法读取 | NEEDS_REVIEW，保全现场，禁止重建目标、自动覆盖或盲目回滚。 |
| PREPARED 的旧两阶段记录，存在缺名或备份 | 按旧策略检查原备份和暂存，禁止当作单步记录恢复。 |
| COMMITTED，投影和对象正常，Log 或 Index 落后 | 保留业务已提交事实，重放派生操作。 |
| COMMITTED，当前账本头的投影或对象无法核实 | 记录独立完整性告警，隔离受影响路径，交由审查。不得抹除已提交事实。 |

恢复以不可变对象、账本版本链和文件身份共同决策。对历史提交按对象与版本链核查；活跃投影与当前账本头核对。配置停用后，禁止旧二进制接管含新策略未决记录的账本。启动遇到不能识别的状态或策略版本应失败关闭。

### 4.1 不确定结果决策表

调用证据和投影证据独立记录。进程内的返回值可能随崩溃丢失；只有 PREPARED 时不能推断 API 是否调用或生效。客户端异常同样不能证明替换未发生。任何不确定结果先只读对账，禁止盲目重试、清理或降级。

| 证据 | 恢复动作 |
|---|---|
| 明确尚未调用 API | 重新核验旧身份、摘要、暂存、父目录、权限和版本头，全部一致才继续。 |
| API 成功返回 | 只读复核目标。仅目标为已记录的新对象且所有验证成立才推进 PROJECTED／COMMITTED。 |
| API 明确失败且已证明无副作用 | 记录 Win32 错误。旧对象、暂存与环境经核验后，暂时性错误可限次重试；永久错误停止调用。 |
| API 失败但副作用不明，或进程退出而结果不明 | 先只读检查目标、暂存、父目录、对象和账本。证据矛盾或不足转 NEEDS_REVIEW。 |
| 目标为已记录的新对象 | 卷／FILE_ID、摘要、ACL、Owner、父目录及版本链匹配时补齐 PROJECTED／COMMITTED，禁止重复替换。 |
| 目标仍为已记录的旧对象 | 旧 ID 和摘要一致仍需验证原暂存和授权，且有充分未发布证据才可继续。已记录成功但目标回到旧对象，或历史歧义时转 NEEDS_REVIEW。 |
| 目标为未知 FILE_ID 或缺失 | 单步 Update 转 NEEDS_REVIEW，保全现场。相同摘要不能替代身份。旧两阶段事务按其持久策略判定。 |
| 父目录身份或有效权限变化 | 暂停单步并转 NEEDS_REVIEW。无法安全绑定目录时，仅保全账本和已经可信取得的记录。 |

### 4.2 元数据兼容矩阵

新投影来自暂存对象。以下为拟议的受管元数据合同，需实测验收。

| 元数据 | 发布要求与复核 |
|---|---|
| DACL、Owner、继承 | 暂存必须先满足受管 DACL、批准的 Owner、保护位与继承策略，保持必要的显式权限例外。不能在最小权限内满足则拒绝发布。发布后重开验证安全描述符，并按真实 Token 验收有效权限。 |
| 只读属性 | 首版拒绝只读目标与不符合策略的暂存。不得清除旧对象只读位或使用忽略只读标志。成功后复验新投影的受管属性。 |
| NTFS ADS | 首版仅支持默认数据流，发现命名流或无法枚举即审查。发布后复核无命名流；未来支持须先建立流级保留和校验合同。 |
| 硬链接 | 旧目标与暂存须为单链接；发现额外链接即审查。发布后再验证新投影链接数。 |
| 文件时间戳 | 允许按暂存对象和文件系统语义变化，无需保留旧文件时间戳。账本保留逻辑版本与审计时间。时间戳仅作诊断。 |
| 已打开旧句柄 | 在批准的共享及过滤器组合中，旧句柄仍引用旧对象。独立验收对比旧句柄和新路径的完整内容。 |
| 新投影 FILE_ID | 允许旧 ID 变化，要求新目标的卷和 FILE_ID 与记录的暂存对象一致，重开验证身份、摘要和权限。 |

## 5. 一致性与传输边界

- **SQLite**是唯一业务提交权威。保留 (authenticated_principal, idempotency_key) 唯一约束、规范请求指纹和版本约束。同键不同请求返回冲突。一次投影替换与一次 SQLite 提交仍存在中间状态，其他直读 Markdown 的进程可能在 COMMITTED 前看见新的完整内容。要求业务一致快照的读者采用账本版本及对应对象。
- **不可变对象**按内容摘要寻址。同内容去重不意味着文件身份相同。对象的验证和引用先于投影；回收必须尊重事务、历史版本及审查保留引用，首版不扩展回收。
- **Markdown**是可验证投影。成功响应只在已验证投影且 COMMITTED 后生成。**Log / Index** 是可重建的派生输出，以事务 ID、水位和已验证投影幂等物化。复用既有物化及待修复路径，不在本轮改变协议。若业务已提交而物化失败，保留成功账本记录并保留诊断与待修复标记；客户端若未收到确认，使用原键查询或重试。不得将物化异常映射成业务回滚。
- **提交前取消**：现阶段没有业务取消协议。客户端关闭连接、取消等待或超时，都可能发生在请求已经抵达之后。服务仍按持久状态推进或恢复。客户端只在确知请求未发送时可报告未提交；其余情况结果未知，使用同键重试。若未来引入业务取消，需另设经认证的持久化取消决策，只能在发布副作用开始前生效。
- **提交后取消或响应截断**：事务继续有效。只有完整、有界、关联 ID 正确且经验证的响应才可确认成功。重连重新验证 Writer 管道所有者、PID 与 SID。同键同请求重放原结果及事务 ID，无重复对象或业务提交；失败时无本地写入回退。提交前、API 调用前后、COMMITTED 前后与物化中断均应单独验收。

### 5.1 持久性与故障模型

| 情形 | 保证边界及验收 |
|---|---|
| 正常发布 | 在通过验收的环境中一次替换，验证投影后提交 SQLite。命名空间连续性和业务提交分别判定。 |
| Writer 进程异常退出 | Windows 与存储继续运行。分别测试 API 调用前后、状态持久化和物化中断，以账本和文件身份恢复。 |
| 服务重启 | 重取排他保护并复验环境，在开放受影响路径前核对未决事务。测试正常停服和异常重启，重放保持唯一提交。 |
| Windows 系统崩溃 | NTFS 与 SQLite 各自恢复，重启后需核验双方实际状态。单独测试系统崩溃，不能以进程退出结果推定。 |
| 意外断电 | 单独建立硬件、控制器、写缓存和断电保护模型。需在合成环境取得中断与重启证据；在此之前不承诺断电持久性或跨文件写回顺序。 |

FlushFileBuffers 作用于相应文件缓冲写回，SQLite synchronous=FULL 用于 SQLite 自身协议。两者不构成 SQLite 和 NTFS 的跨系统原子事务。系统崩溃或断电后的歧义必须只读对账或转 NEEDS_REVIEW。 [Microsoft FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers)

## 6. 实施门禁、步骤与回滚

### 6.1 三级准入门禁

| 门禁 | 当前状态及条件 |
|---|---|
| 一级：设计准备 | 允许只读审查和批准范围内的独立原型研究。 |
| 二级：正式 WB3F 集成 | BLOCKED。下列两项 WB3E 用例仍是硬门禁，需独立证据和签署，并由 Human 确认开发准入。门禁调整必须获得 Human 明确批准，禁止自动放宽。 |
| 三级：Secure Mode 生产部署 | BLOCKED。正式集成后须完成真实跨 SID、恢复、完整回归、读取连续性和独立安全验收，并由 Human 单独批准部署。 |

**正式开发前硬门禁。** 下列原始用例均须在独立授权 Windows／NTFS 合成环境取得真实执行证据并由独立 QA 签署。本设计不修改既有 BLOCKED 记录。

| 用例 | 必需证据 |
|---|---|
| tests/test_wb3d3_integration.py::test_publication_gap_preserves_external_file | 真实缺名及恢复时序，外部目标保留，PREPARED／NEEDS_REVIEW 判定，事务无错误 Log。 |
| tests/test_wb3d4_preservation.py::test_live_publication_preserves_independently_created_destination | 真实发布时序，拒绝覆盖，外部目标、备份和暂存保留。原语级用例的业务账本记 N/A。 |

两项独立验收及受影响回归通过、无新增阻断问题后，再由 Human 决定是否批准正式 WB3F。通过门禁后拟按以下顺序：

1. 固定支持矩阵及威胁模型，验证实际 ACL 和目录稳定性，确认公开 API 接口及每卷探测。冻结候选源、测试 ID 和基线证据。
2. 增加默认关闭的 Secure Update 单步策略及状态版本，保留既有管道、Secure New、Standard 和派生输出行为。先验证旧账本和混合历史，再验证新投影。
3. 在独立合成 Vault 注入崩溃及传输故障，完成完整历史回归与三种 Standard 路径长度回归，交独立 QA 签署。通过后单独决策是否试点，生产安全仍需独立审批。

**回滚**：停收新单步 Update，保留当前二进制用于核对并按已记录策略收敛未决事务；歧义转人工审查。离线归档账本及其 SQLite 附属文件、对象、投影、暂存和审计记录。仅在账本版本可读且未决状态已核验时切回经批准的旧模式。禁止在一次操作失败后自动退回两阶段。若必须降级二进制且 schema 不兼容，只能从已验证的一致检查点恢复，经授权处理检查点之后的提交，禁止用旧 Markdown 覆盖较新的已提交或未知对象。

## 7. 独立验收矩阵

| 维度 | 通过标准 |
|---|---|
| 支持与隔离 | 记录 Windows 构建、NTFS、架构、真实 Writer/Agent/Unauthorized Token、路径稳定性与 ACL。探测失败或权限漂移时失败关闭。已测非特权主体的拒绝不能外推到等效写入者。 |
| 替换与读取 | 在支持矩阵中至少 100 次合法发布、50,000 次读取，记录真正重叠的次数、FILE_ID 与已知摘要。正常删除共享条件下无缺名、部分或未知内容。单列不共享删除、过滤器、长路径与大小写表现和原始错误。 |
| 崩溃恢复 | 覆盖 PREPARED 前后、替换调用前后、PROJECTED、COMMITTED 以及 Log／Index 物化中断。未知或矛盾证据进入 NEEDS_REVIEW。进程退出与断电持久性分立判定。 |
| 事务和传输 | 并发 Update 版本冲突、同键同请求、同键异请求、提交前后取消等待、截断头体和关联错误、服务离线及重连鉴权。断言无额外提交或本地回退。 |
| 数据一致性 | SQLite 完整性与外键检查、对象摘要、当前投影身份与摘要、Log／Index 水位及重复恢复，核验历史旧策略恢复兼容。 |
| 回滚和回归 | 停用能力、未决事务、版本不兼容与一致备份恢复均有独立记录。执行 367 项历史用例及 Standard 65／101／106 UTF-16 路径回归，核对新增专项、原始错误和残留进程。 |
| 生产边界 | Obsidian GUI 文件监视、过滤器组合和断电语义单列。未验收配置及等效直写者的竞态风险保持显式限制。 |

本设计依据当前候选的 _windows_fs.py 和 secure_ledger.py、WB3D.4.1 的 publish_probe.py、发布决策与恢复报告，以及 WB3E 的冻结证据。未修改候选、历史验收或生产状态。
