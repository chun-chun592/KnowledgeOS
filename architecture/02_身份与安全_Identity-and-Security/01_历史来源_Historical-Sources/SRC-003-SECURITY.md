> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Security policy

Secure Mode production deployment is blocked. New, Update and Recover have
same-SID functional coverage on synthetic Windows Vaults. Independent Windows
SID and NTFS ACL enforcement are NOT TESTED. Launcher pins and canonical
configuration require protection from processes with access to the same SID.
See the [WB3D.3 boundaries · 历史引用 / historical reference](../../16_%E6%9E%B6%E6%9E%84%E6%9D%A5%E6%BA%90_Architecture-Sources.md#local-only).

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |
| < 0.1 | No |

## Threat model

KnowledgeOS is a **controlled-write CLI** for a shared Obsidian vault. It is not a sandbox.

What the tool does protect against:

- Accidental writes to `00_Human/**` by a cooperative agent using the CLI.
- Path traversal (`../`), absolute paths outside the vault, symlink/junction escapes, and
  case-insensitive path variants on Windows.
- Unintended replacement in the controlled write paths. Existing note updates record a verified
  backup and an operation ID. Recoverable transaction coverage applies to the update command.
- Concurrent index/log corruption between cooperating agents: `.knowledgeos/locks/` plus
  read-modify-write with atomic replacement.

What it cannot protect against:

- A process with direct filesystem access that ignores KnowledgeOS.
- A malicious agent that uses shell commands instead of the CLI.
- A human approving a write request that is broader than intended.
- Malicious Markdown content: Obsidian community plugins and embedded HTML can execute actions.
  Only open vaults and plugins you trust.
- Data exfiltration by the model provider or agent runtime.

Real enforcement requires an OS boundary: run the agent as a separate OS user with read-only ACLs on
`00_Human/`, mount the vault read-only, use a container, or place a policy-enforcing gateway in front of
all writes. Those options are documented, not implemented.

## Write-request authorization

The standalone CLI keeps Human notes read-only. Exchange Markdown requests record intent and
historical approvals. The application host must supply an independent `HumanAuthority` to
authorize an embedded update. Its authenticated grant binds executor, normalized path, action,
original SHA256, candidate SHA256, transaction ID, nonce and expiry. The provider must atomically
check revocation and consume the nonce. A production signer and protected approval store are
deployment requirements. This distribution includes the provider interface and synthetic tests.

Store signer credentials and the nonce ledger under an identity inaccessible to the Agent.
A same-account process can still bypass the CLI or alter local journals. Windows directory
identity can also change between path validation and use. Use NTFS ACLs for isolation.

## Reporting a vulnerability

Please **do not** open a public issue. Email the maintainers listed in `pyproject.toml` via the
repository's private security advisory form ("Report a vulnerability" on GitHub). Include:

- KnowledgeOS version and OS,
- a minimal reproduction using a synthetic vault,
- the expected vs. observed permission decision,
- whether a write escaped the intended region.

We aim to acknowledge within 7 days and to ship a fix or documented mitigation within 30 days.

## Hardening checklist for users

- Keep `00_Human/**` under version control (Git) and review diffs before committing.
- Run `knowledgeos doctor` and `knowledgeos lint` regularly.
- Review `20_Exchange/write-requests/` before approving; use short `expires` windows.
- Do not store secrets in notes; the vault is plain text.
- Back up `.obsidian/` separately; KnowledgeOS never edits it.
