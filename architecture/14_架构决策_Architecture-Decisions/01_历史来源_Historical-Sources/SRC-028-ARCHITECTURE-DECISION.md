> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# architecture decision

Keep the Standard CLI and core as the reference behavior. Select a backend before invoking the handler. Do not substitute WB3C raw object updates for core business commands. A future service must execute vetted core intents under its own identity and reconcile the ledger and Markdown publication through a defined recovery protocol.
