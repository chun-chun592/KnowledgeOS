> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

<!-- 发布处理：仅泛化机器绑定路径和卷标 / Publication edit: machine paths and volume letters generalized -->

# 独占创建与句柄核验合同

**设计候选，NOT TESTED。** 不把存在性查询当作创建前置证明。禁止先按默认权限创建、再收紧 DACL。下面是后续另获 Human 批准时的准入合同，不是本轮运行步骤。

1. 由受监督管理员启动受信创建器，固定本地 NTFS 卷及直接父目录。先对已打开的 数据卷 根句柄验卷标识、FILE_ID、目录属性、重解析标签、Owner 与 DACL。只允许可信配置指定的单个名称；拒绝路径成分、备用数据流、设备名或不一致的路径别名。
2. 在创建请求中提供非空的显式 DACL，并设置 SE_DACL_PROTECTED（SDDL D:P）。使用签核的 Owner SID 和有界 ACE；根 Owner 必须属于 SYSTEM 或受监督管理员等可信主体。创建器预先核对 TokenUser、TokenOwner、有效组及可合法赋给新对象的 Owner。没有合法 Owner 时拒绝创建，不依赖事后提权或改 Owner；禁止给普通 Broker 授予 SeTakeOwnershipPrivilege 或 SeRestorePrivilege 来满足此条件。明确指定并验证预期 Group。不继承 AU/BU 写删能力，能力按子目录职责授予。[创建时安全描述符](https://learn.microsoft.com/en-us/windows/win32/fileio/file-security-and-access-rights) · [受保护 DACL](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/applying-security-descriptors-on-the-device-object) · [Windows 特权](https://learn.microsoft.com/en-us/windows/win32/secauthz/privilege-constants)
3. 首选待审路径为从已验证的父句柄进行相对单段目录创建，由受审启动器使用公开文档描述的 NtCreateFile、RootDirectory、FILE_CREATE、FILE_DIRECTORY_FILE 和适用的 OBJ_DONT_REPARSE。只接受调用成功且最终 I/O 状态为 FILE_CREATED，并使用同次返回的不可继承目录句柄。不得使用打开或创建两用模式。对支持性、文件系统和过滤器行为的本机证据仍缺失，Native API 需单独批准和审查。[NtCreateFile](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntcreatefile) · [OBJECT_ATTRIBUTES](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_object_attributes)
4. CreateDirectoryW 可以在创建时应用描述符，且既有名称会失败；它只返回成功标志，后续按路径打开是另一操作。若只准用 Win32，此方案暂时仍缺从创建到首个可信句柄的完整绑定证据。任何必要条件失败时停止，无自动回退。[CreateDirectoryW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createdirectoryw)
5. 如果遇到名称冲突、重解析、无效 Owner、访问拒绝、不支持或返回状态不明确，保留原始 NTSTATUS、I/O 状态或 Win32 错误，不接管既有目录、不清理陌生对象、不依据再次探测选择覆盖。创建响应丢失时，未知对象隔离审查；重启仅允许从受保护控制面已登记的卷及 FILE_ID 绑定重新核验。
6. 新句柄读回 FileIdInfo 和 FileAttributeTagInfo；GetSecurityInfo 用 READ_CONTROL 读取 Owner、Group 和 DACL，核对保护位、ACE、继承范围和 NONE/NULL DACL 拒绝条件。确认同卷，核对固定名称仍指向同一对象并验证父目录未漂移。拒绝任何重解析点（包括 Junction、符号链接与挂载跳转）。成功持有对象句柄仍需验证 ACL 与命名空间，因此不得仅凭 FILE_ID 放行。创建器句柄不交给 Agent；授予 Binder／Broker 所需的最小引用。[GetSecurityInfo](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo) · [FILE_ID_INFO](https://learn.microsoft.com/en-us/windows/desktop/api/winbase/ns-winbase-file_id_info)

启动前还须验真实 Token 的负向权限，并单独区分访问拒绝、名称冲突、共享冲突和工具错误。先证明配置可用再启用生成数据；后续发布的 FILE_ID 检查仍无原子 CAS。
