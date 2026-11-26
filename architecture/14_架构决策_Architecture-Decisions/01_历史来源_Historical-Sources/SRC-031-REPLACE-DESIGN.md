> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Windows Update / Replace 设计评审

**BLOCKED。** 未找到同时能拒绝未知同名对象、又维持对外单步旧→新发布语义的受支持方案。考虑有父目录写权限但不遵循 KnowledgeOS 锁的同机进程；协作锁不是 OS 访问控制。

## 当前调用链（源码核查）

`cli._cmd_update` → `update_note`（锁、旧对象快照、intent）→ `update._resume_update`（状态、备份、暂存收据）→ `Vault.write_text` → `_windows_fs.publish_internal`（父目录绑定、暂存刷新、旧 ID 和 SHA256 校验）→ `_snapshot_handle` 释放保护句柄 → `_rename` 按名称覆盖 → `windows_update_state` 验证暂存 ID、SHA256 → Wiki Index → Log → done。Recover 汇入同一条 `_resume_update`。验证新对象不能追证被替换对象的身份。

## A：单步替换 — BLOCKED

- [CreateFileW](https://learn.microsoft.com/windows/win32/api/fileapi/nf-fileapi-createfilew) 按名打开对象，匹配共享模式；`DELETE` 是访问权，`FILE_SHARE_DELETE` 是共享标志，不是名称预留。
- [ReplaceFileW](https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-replacefilew) 与 [MoveFileExW](https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-movefileexw) 按目标名操作，不接收预期目标句柄或 ID；长路径前缀不提供绑定。
- `SetFileInformationByHandle` 和 `NtSetInformationFile` 的重命名操作绑定源句柄；[FILE_RENAME_INFORMATION / Ex](https://learn.microsoft.com/windows-hardware/drivers/ddi/ntifs/ns-ntifs-_file_rename_information) 可通过 `RootDirectory` 绑定目标目录，仍由名称解析目标叶。`REPLACE_IF_EXISTS` 不比较 ID；POSIX 标志允许替换仍有打开句柄的对象，旧句柄继续引用旧对象，并不指定必须替换哪个旧对象。普通覆盖的共享限制见隔离测试；本轮未独立实测 Ex/POSIX。
- [FILE_DISPOSITION_INFO](https://learn.microsoft.com/windows/win32/api/winbase/ns-winbase-file_disposition_info) 能对已打开且具 DELETE 权限的对象设置删除，不能同时发布另一个对象。上述接口没有预期目标 ID 条件字段。

## B：双阶段无覆盖改名 — BLOCKED

隔离测试按旧对象句柄无覆盖停放原件，再无覆盖发布新对象，核对停放对象和最终对象的 ID，并明确断言两次改名之间原名不存在。可拒绝已占用原名，但不能阻止其他进程在此时占用原名；无覆盖回滚也只能在原名空闲时成功。独立读者能观察到缺名，不等价于单步替换。

若将来允许缺名，候选协议（未实现）先持久记录 PREPARED（卷、父目录、旧对象、暂存 ID 和哈希），在 OLD_TARGET_PINNED 验证句柄；每次改名完成后验证并记录 OLD_TARGET_RENAMED、NEW_TARGET_PUBLISHED、VERIFIED，再幂等完成 LOGGED、INDEXED、COMPLETED。Recover 应按实际对象身份推断改名已发生但收据未写的情形；未知占用、错件、丢失或状态不明一律 NEEDS_REVIEW，保留证据。状态机不能消除缺名，也不能证明二次中断安全。

## C：强制写入隔离 — REVIEWED

若能强制只有受信代理修改目标命名空间，可重新论证隔离边界内的串行校验与覆盖。现有协作锁不具备此前提，本轮不改 ACL、不建设代理。[TxF](https://learn.microsoft.com/windows/win32/fileio/deprecation-of-txf) 未验证，Microsoft 建议采用替代方案，不选为生产依赖。
