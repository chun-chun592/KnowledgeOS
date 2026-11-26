# 架构决策登记 / Architecture Decision Register

本文件保留候选 ADR-01 至 ADR-06 的状态和决策边界。\
This document preserves the status and decision boundaries of candidate ADR-01 through ADR-06.

## ADR-01 应用策略与操作系统强制 / Application Policy and OS Enforcement

早期 CLI 设计明确排除操作系统强制执行，后期 Secure Mode 要求 Token、ACL 和服务边界。\
The earlier CLI design explicitly excludes OS enforcement, while later Secure Mode requires Token, ACL, and service boundaries.

保留范围与版本差异，新部署采用的规范契约仍待决定。\
Preserve the scope and version distinctions, with normative contracts for a new deployment still to be decided.

## ADR-02 提交权威与可见投影 / Commit Authority and Visible Projection

早期设计描述 Markdown 文件更新与受管索引，后期设计以 SQLite 的 COMMITTED 为业务权威，直接读取者可能提前看到完整投影。\
The early design describes Markdown file updates and managed indexes, while the later design treats SQLite COMMITTED as business authority and direct readers may observe an early complete projection.

读取类别与发布不变量仍需确认。\
Read classes and publication invariants still require confirmation.

## ADR-03 两步替换与单步替换 / Two-step and Single-step Replacement

保留旧恢复元数据、文件名短暂缺失的证据边界和非原子 FILE_ID CAS 限制。\
Preserve legacy recovery metadata, the evidence limits on missing-name claims, and the non-atomic FILE_ID CAS limitation.

候选功能须经独立证明方可启用。\
Independent proof is required before enabling the candidate.

## ADR-04 控制平面、数据平面与 Publisher / Control Plane, Data Plane, and Publisher

可信控制平面与独立数据根是 PARTIAL 提案，生产权限尚未确定。\
The trusted control plane and separate data root form a PARTIAL proposal, with production permissions still undecided.

最终服务身份、Publisher 权限及绑定仍待决策。\
Final service identities, Publisher authority, and binding still require a decision.

## ADR-05 移动设备与同步 / Mobile Devices and Synchronization

从原始设计来源恢复权威的离线、冲突与同步规范，或取得明确架构决策。\
Recover authoritative offline, conflict, and synchronization specifications from the original design source, or obtain an explicit architecture decision.

同步写入必须经过 Writer。\
Synchronization writes must go through Writer.

## ADR-06 来源溯源 / Source Provenance

历史检查的 Candidate 根目录是没有 Git 元数据的导出。\
The historically inspected Candidate root was an export without Git metadata.

只读核验曾在独立的 WB3F Engineering 基线仓库中确认请求的冻结对象是提交且当时为 HEAD。\
Read-only verification historically confirmed the requested frozen object was a commit and then HEAD in the separate WB3F Engineering baseline repository.

原 ADR 将历史仓库保留和归档恢复核验列为待办；该时间点的判断通过原文及来源清单追溯。\
The original ADR recorded history preservation and archive restoration verification as pending, and that point-in-time judgment remains traceable through the original text and provenance manifest.

[架构来源与索引 / Architecture sources and index](../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md)
