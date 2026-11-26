> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Proposed transaction and ledger contract

The service exclusively coordinates writes. A dedicated typed ledger is the
commit authority. Standard transaction records retain their historical meaning.
Legacy operations and WB3C records require an explicit import decision.

| Durable stage | Rule on restart |
|---|---|
| REQUEST_ACCEPTED | Bind principal, idempotency key and digest. Revalidate an unsigned plan. |
| VALIDATED | Record target, parent and previous leaf identity, expected revision and complete edit plan. |
| OBJECT_STORED | Verify immutable object hashes. Unreferenced objects may remain. |
| PREPARED | Persist both hashes and the staged file identity before projection. |
| PROJECTED | Verify that the leaf matches the staged identity and new hash. |
| COMMITTED | Publish the saved response on retry and reconcile derived audit/index. |
| NEEDS_REVIEW | Freeze the affected target and preserve evidence. |

A PREPARED record reconciles a crash after publication by comparing the observed leaf
with the persisted old and staged identities and hashes. A proven old leaf allows
publication to resume. A proven staged leaf allows commit to proceed. Unknown content
or identity enters NEEDS_REVIEW. A retry after COMMITTED reads the saved result.
Projection before PREPARED is prohibited. Repeated recovery uses the same rules.

Audit and Index are derived. A materializer must reconcile by transaction ID, record
a durable watermark and verify controlled output identity before updating. No second
transaction log can mark the version committed. This document defines the proposed
ordering. Persistence, materialization and process-exit proof are pending.
