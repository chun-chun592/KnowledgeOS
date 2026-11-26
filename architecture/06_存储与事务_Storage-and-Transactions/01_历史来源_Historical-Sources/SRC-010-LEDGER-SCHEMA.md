> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# 单一 SQLite 账本

运行时权威为 .knowledgeos/wb3d2/ledger.sqlite3。沿用 WB3C 的 SQLite 事务、
DELETE rollback journal、FULL synchronous、SHA256 寻址和启动对账模式。
以类型化 schema 代替旧原型 schema，因为原型将投影路径和内容作为请求，
以调用方事务 ID 去重，并以散列匹配代替暂存文件 ID。WB3C 记录没有被导入；
WB3D.2 服务没有打开旧账本。Standard 的历史事务语义独立保持。

transactions 保存服务生成的 transaction_id、authenticated_principal、
idempotency_key、request_fingerprint、operation、request_json、target_relative_path、
expected_revision、parent_directory_identity、previous_file_identity、
new_content_sha256、immutable_object_id、stage_name、stage_identity、
transaction_state、saved_response 和 UTC 时间戳。New 要求前一版本和文件身份为空。
唯一键为 (authenticated_principal, idempotency_key)。目标预留使用不区分 ASCII
大小写的索引，目标 slug 由既有业务规则限制为 ASCII。materialization 按
(transaction_id, kind) 保存派生输出意图及完成水位。

[SQLite 快照和结构 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only) · [快照检查 · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only)
