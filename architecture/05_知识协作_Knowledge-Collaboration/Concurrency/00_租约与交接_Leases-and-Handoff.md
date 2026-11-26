# 租约与交接 / Leases and Handoff

真实库协议使用 20_Exchange/agent-to-agent/locks 下的租约；目标相对路径中的斜线和点替换为短横线，文件名以 .lock.md 结束。记录目标、持有人、取得时间、有效期与用途。活动租约存在时等待或停止，不抢占。\
The real-vault protocol stores leases under 20_Exchange/agent-to-agent/locks. Replace slashes and periods in the relative target with hyphens and append .lock.md. Record the target, owner, acquisition time, expiry, and intent. Wait or stop for an active lease.


写入前重读基线并保存备份；完成后校验哈希、更新必要索引行、追加日志，只释放自己的租约。交接记录任务、相关笔记相对路径、证据与待决问题，不保存完整聊天。只在人工确认与现有协议允许时处理陈旧锁。\
Before writing, reread the baseline and save a backup. Verify hashes after editing, update relevant index rows, append the log, and release only your lease. Handoffs record intent, relative note paths, evidence, and open questions. Handle stale leases only when confirmed by a Human and permitted by the vault policy.
