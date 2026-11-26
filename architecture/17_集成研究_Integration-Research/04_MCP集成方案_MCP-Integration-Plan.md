> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../README.md) for current applicability.

# MCP集成方案 / MCP Integration Plan

先评审只读 MCP 适配层，其身份、授权及持久状态继承现有边界，MCP 不承担 SQLite 提交权威。\
Review a read-only MCP adapter first. It inherits existing identity, authorization, and durable-state boundaries, and does not become the SQLite commit authority.

## 注册、输入与资源 / Registration, Inputs, and Resources

将查询、读取、反链和审计建议注册为独立只读能力，资源 URI 使用逻辑标识并经受控解析。\
Register query, read, backlink, and audit suggestions as distinct read-only capabilities, with resource URIs using logical identifiers and controlled resolution.

在注册 schema 中声明类型、范围、必需字段和有界输出，校验将同时覆盖枚举、调用和资源模板。\
Specify types, ranges, required fields, and bounded output in registration schemas, and validate tool enumeration, calls, and resource templates.

列举结果按当前主体过滤，执行时再次授权；readOnlyHint 和 idempotentHint 只表达提示。\
Filter enumeration by the current principal and authorize again on execution. readOnlyHint and idempotentHint are advisory.

[MCP 工具规范 / MCP Tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) · [MCP 资源规范 / MCP Resources specification](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) · [server.py](https://github.com/basicmachines-co/basic-memory/blob/8d002c93fd5d68fbb9690c6de9b90792040dce1c/src/basic_memory/mcp/server.py#L259-L268) · [notes.py](https://github.com/basicmachines-co/basic-memory/blob/8d002c93fd5d68fbb9690c6de9b90792040dce1c/src/basic_memory/mcp/resources/notes.py#L122-L145) · [test_note_resources.py](https://github.com/basicmachines-co/basic-memory/blob/8d002c93fd5d68fbb9690c6de9b90792040dce1c/tests/mcp/test_note_resources.py#L30-L107) · [config.ts](https://github.com/inkeep/open-knowledge/blob/cfee15dc8e7aaae0fb8579bbd3e73b91b41a8de1/packages/server/src/mcp/tools/config.ts#L56-L65) · [json-schema-dialect.ts](https://github.com/inkeep/open-knowledge/blob/cfee15dc8e7aaae0fb8579bbd3e73b91b41a8de1/packages/server/src/mcp/json-schema-dialect.ts#L57-L97) · [config.test.ts](https://github.com/inkeep/open-knowledge/blob/cfee15dc8e7aaae0fb8579bbd3e73b91b41a8de1/packages/server/src/mcp/tools/config.test.ts#L123-L145)

## 受控写入、幂等与错误 / Controlled Writes, Idempotency, and Errors

未来写入能力需单独批准，并经 Broker 与 Writer 路径授权；工具不得接受任意本机路径或直接修改数据库。\
Future write capabilities require separate approval and authorization through the Broker and Writer path. Tools must reject arbitrary host paths and direct database mutations.

将外部请求映射到现有版本、主体、操作、目标、修订及幂等约束，并以现有契约确定重复或冲突行为。\
Map external requests to existing version, principal, operation, target, revision, and idempotency constraints. Existing contracts decide duplicate and conflict behavior.

保留协议传输错误、已知业务拒绝和结果未知的区别；收到未知结果后先读取持久事务状态再决定下一步。\
Keep transport failures, known business rejections, and unknown results distinct. After an unknown result, consult durable transaction state before choosing the next action.

验收先覆盖非特权主体、未知 URI、有界返回、跨区拒绝、连接丢失和重复请求，并保留原 IPC 帧限制。\
Acceptance first covers nonprivileged principals, unknown URIs, bounded results, cross-area denial, lost connections, and duplicate requests while preserving the IPC frame limit.

[身份与安全 / Identity and Security](../02_%E8%BA%AB%E4%BB%BD%E4%B8%8E%E5%AE%89%E5%85%A8_Identity-and-Security/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [Broker 与 Writer / Broker and Writer](../05_Broker%E4%B8%8EWriter_Broker-and-Writer/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [API 与契约 / API and Contracts](../10_API%E4%B8%8E%E5%A5%91%E7%BA%A6_API-and-Contracts/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [状态机 / State Machines](../11_%E7%8A%B6%E6%80%81%E6%9C%BA_State-Machines/00_%E6%A8%A1%E5%9D%97%E6%A6%82%E8%BF%B0_Module-Overview.md) · [edit.py](https://github.com/basicmachines-co/basic-memory/blob/8d002c93fd5d68fbb9690c6de9b90792040dce1c/src/basic_memory/mcp/tools/edit.py#L38-L85) · [server.py](https://github.com/Labhund/lacuna-wiki/blob/b7aadcb29dae0e66725dcf40ee005c6152aae36d/src/lacuna_wiki/mcp/server.py#L18-L150)

## 版本约束 / Version Constraints

引用的 MCP 规范版本仅是本研究的参考，支持版本、传输方式、凭据配置和资源订阅应在独立验收中确认。\
The cited MCP revision is the research reference. Confirm supported revisions, transport, credential configuration, and resource subscriptions in separate acceptance.
