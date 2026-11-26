> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# R1.3.1 重入与状态机审查

**PASS（受控静态范围）。** P1-1 至 P1-4 已修复。五个公开状态操作在执行任何业务、回调或目标 Native 绑定调用前统一调用 _begin_operation。锁内原子检查状态、活动操作和全案隔离门禁，随后登记活动操作；写流程立即进入 IN_PROGRESS。锁只覆盖状态与保全注册，不覆盖回调、证据记录、Native 调用或资源释放。拒绝发生在各入口异常处理之外，因而内层被拒绝的调用不会改写外层状态、调用保全逻辑或释放句柄。若受信回调让拒绝异常传播，外层仍按其自身失败处理。

| 入口 | 原状态 | 活动态 | 正常结果 | 失败结果 |
|---|---|---|---|---|
| open_parent | NEW | IN_PROGRESS | PARENT_READY | NEEDS_REVIEW |
| create_root | PARENT_READY | IN_PROGRESS | ROOT_AWAITING_INSPECTION | NEEDS_REVIEW |
| verify_collision | PARENT_READY | IN_PROGRESS | DONE | NEEDS_REVIEW |
| complete_root | ROOT_AWAITING_INSPECTION | IN_PROGRESS | DONE | NEEDS_REVIEW |
| inspect_preserved | NEEDS_REVIEW | NEEDS_REVIEW，独占活动标记 | NEEDS_REVIEW | NEEDS_REVIEW |

非预期状态、IN_PROGRESS、活跃取证时再次申请和 DONE 均拒绝。verify_collision 的 admission、provenance 和 inspect 都在占用之后执行，两个名称检查及原成功判定未更改。open_parent 在登记输出及打开之前占用。保全取证的 finally 仅结束活动标记；无自动释放路径。全局保全阻止新的执行入口，允许保全会话独占取证；其他实例已经进入的操作不会被该锁取消。Human 执行器应只运行一个受审会话。

公开业务入口未发现其他重入路径。回调直接篡改会话属性、调用私有实现、调用自带系统 API 或保存借用句柄超出此 Python 状态门禁的能力；仍依赖受审回调与专用进程，Windows 边界 NOT PROVEN。
