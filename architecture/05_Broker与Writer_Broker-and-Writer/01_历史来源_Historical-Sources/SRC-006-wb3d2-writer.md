> 历史设计证据，原有状态和约束按当时范围解读。当前适用性见[架构入口](../../README.md)。\
> Historical design evidence. Interpret the original status and constraints in their original scope. See the [architecture entry point](../../README.md) for current applicability.

# Experimental Secure New, Update and Recover on Windows

Use a newly installed synthetic Vault for this foreground writer. Install the optional
`writer` extra in the test Python environment. The Vault's canonical
`.knowledgeos/config.toml` must declare `[security]` and `mode = "secure"`.
Create `.knowledgeos/wb3d2-synthetic` with UTF-8 bytes
`KnowledgeOS WB3D2 synthetic vault\n` (LF and no BOM).

Create a separate service JSON file with `synthetic_vault` set to the canonical
local absolute root and `allowed_sids` set to the authorized Windows TokenUser
SID strings. Run `knowledgeos-writer serve --config <service.json>` in the
foreground. The ready event reports the service SID and PID after startup
reconciliation. Transfer those values from the trusted launcher into
`KNOWLEDGEOS_WRITER_SID` and `KNOWLEDGEOS_WRITER_PID` for the CLI. Refresh the
PID pin after a restart. The repository checkout also supports
`python -m knowledgeos.writer_service` with `src` on `PYTHONPATH`.

Use `knowledgeos new concept "Synthetic example" --vault <synthetic-root>
--operation-id example-001` from a client. Retry with the same operation ID and
the same arguments if the service becomes unavailable. Secure Mode accepts
protocol v1 keys of 1–64 ASCII alphanumeric, underscore or hyphen characters
starting with an alphanumeric. It uses the server's configured agent for
frontmatter attribution. The response contains a service-generated transaction
ID. Use New's `sha256` as the initial revision. Subsequent Updates return a
`revision` distinct from the content `sha256`.

```powershell
knowledgeos update 10_Agent/wiki/concepts/synthetic-example.md --expected-revision <revision> --status draft --operation-id example-002 --vault <synthetic-root>
knowledgeos recover --list --vault <synthetic-root>
knowledgeos recover <transaction-id> --dry-run --vault <synthetic-root>
knowledgeos recover <transaction-id> --vault <synthetic-root>
```

Start the writer with `--manual-recovery` to inspect pending receipts before
applying recovery. New writes wait for pending work to be reconciled in that
mode. Ingest, Synthesize, Archive and New/Update dry-run are disabled in Secure
Mode. Recover dry-run is read-only.

Stop the foreground process with Ctrl+C or Ctrl+Break. Startup blocks if
reconciliation encounters conflicting file identity or content. Preserve the
ledger, immutable objects and staging files for review in that case.
