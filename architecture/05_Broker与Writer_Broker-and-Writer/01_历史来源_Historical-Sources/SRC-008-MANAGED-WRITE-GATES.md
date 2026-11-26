> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Managed write gates

The WB3D CLI gate rejects write-capable commands before invoking the handler.
Canonical secure configuration also blocks alternate-config downgrade through the
normal loader. Doctor, Query, Status, Log and lint without a report remain routed
through the local read paths. The planner performs no writes.

Direct Core calls, installer, config creation, authorization helpers, transactions,
index, audit, path-level primitives and adapter entry points require independent
write-gate enforcement or review. Passing the CLI refusal tests does not satisfy
the managed write-gate acceptance item.
