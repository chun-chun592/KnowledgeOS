> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# 类型化 Windows Named Pipe

协议 v1 每次连接处理一个请求及一个响应。帧为 4 字节无符号大端长度，
随后是 1–262144 字节 UTF-8 JSON。精确读取允许头部和正文分片。
解码拒绝重复字段、未知字段、错误版本、无效 JSON 和超长帧。
响应验证协议版本及请求 ID。畸形帧没有可绑定的请求 ID，响应使用 null。
客户端读取合法响应后发送单字节 ACK，使服务关闭连接时管道不会丢弃响应。

管道为本地 byte mode，拒绝远程客户端。连接繁忙有截止时间，读写使用
overlapped I/O 和同线程 CancelIo。真实管道验收包括分片和恰好 262144 字节、
无效 JSON、重复和未知字段、错误版本、超长帧、断开、超时及响应关联。

[pytest · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) · [原始管道数据 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)
