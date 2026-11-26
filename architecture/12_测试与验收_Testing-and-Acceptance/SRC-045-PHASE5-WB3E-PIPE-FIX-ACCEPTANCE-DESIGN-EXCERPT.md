> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../README.md) for current applicability.

# 历史设计摘录

来源：Architecture-Frozen / 12-Testing-and-Acceptance / historical-source / SRC-045-PHASE5-WB3E-PIPE-FIX-ACCEPTANCE.md

## 根因和最小修复

原始实际 DACL 为显式且受保护的两条允许 ACE。Writer 所有者为 0x1f01ff，配置中的 Agent SID 为 0x120103。CreateFile 同样请求 0x120103，仍返回 Win32 5。仅将 Agent ACE 改为 0x120183 后，以原请求掩码即可打开并通过服务身份验证。该 A/B 对照将本机失败定位到 Agent ACE 缺少 FILE_READ_ATTRIBUTES（0x80）。中间对照曾同时调整两处掩码，最终补丁仅修改 ACE。

最终客户端掩码仍为 0x120103，含 FILE_READ_DATA、FILE_WRITE_DATA、FILE_WRITE_EA、READ_CONTROL 和 SYNCHRONIZE。ACE 额外含 FILE_READ_ATTRIBUTES。未加入 GENERIC_WRITE、FILE_CREATE_PIPE_INSTANCE、FILE_WRITE_ATTRIBUTES 或通用用户组授权。原 Writer 权限及 SQOS 保持。没有为此另加恢复 ACE。CreateFile flags 仍为 0x40110000（OVERLAPPED、SQOS_PRESENT、IDENTIFICATION），共享模式 0，OPEN_EXISTING。服务端 CreateNamedPipe open mode 为 0x40080003（双向、OVERLAPPED、FIRST_PIPE_INSTANCE），pipe mode 为 0x8（拒绝远程），实例数 1，输入输出缓冲区各 65536。FIRST_PIPE_INSTANCE 成功，未观察到抢先存在的实例。实际管道名、所有者、DACL SDDL、ACE、SID、PID 及 Win32 返回信息见私有日志。
