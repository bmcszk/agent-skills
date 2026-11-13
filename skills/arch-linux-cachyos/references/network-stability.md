# Network stability triage

Read when a link flakes: drops, stalls, or slow-throughput windows
that ping sometimes survives. The goal is a verdict about WHERE the
loss lives, not a faster retry.

## The probe ladder

1. Split the path: ping the gateway, then a WAN anchor (a stable
   public IP). Gateway loss is LAN; anchor loss past a clean gateway
   is upstream or WAN-side.
2. Probe with a FRESH lookup, not a name already cached:
   `dig <name> @<resolver>` next to the ping. Ping-by-name proves
   nothing through the resolver cache; a stale cached answer hides
   a DNS failure behind a working ping.
3. Read the NAT-session-hang signature: TCP fails while ICMP passes,
   across multiple destinations. Per-destination TCP loss with clean
   ICMP points at the NAT/table layer, not the link.
4. Check the daily clustering signature: loss clustering at the same
   wall-clock time daily indicates a scheduled reboot or a cron
   restart of a daemon, not random RF noise.

## Kernel-journal arbitration

`journalctl -k` arbitrates competing hypotheses: NIC resets,
link-flap messages, and firmware errors are timestamped evidence of
which layer failed first, before any user-space claim.

## Offloads as reversible discriminators

Toggle NIC offloads (`ethtool -K <dev> gro off`, `gso off`, `tso
off`) one at a time as discriminators. They are runtime-only, so a
reboot restores them: the experiment is reversible by design and
never ships as a permanent fix until a cause is proven.

## Overnight capture

Capture overnight via a systemd user unit writing bounded CSV or
logs (rotate or cap the file): an unbounded capture fills the disk
by morning, and a bounded one survives to span the outage window.

## Analysis discipline

- Analyze at the right granularity: per-minute aggregates hide
  2-second hangs; per-packet or per-second series find them.
- Cluster gaps, not averages: three 100% loss windows and a clean
  rest is a different fault than 5% everywhere.
- Client-side counters (socket errors, retransmits) are effect, not
  cause: they tell you the failure reached the app, not where it
  started.
- Close with a controlled saturation test: load the link deliberately
  and watch whether the signature reproduces, separating congestion
  behavior from idle-time loss.

## Verdict discipline

The capture must span an outage window: evidence from clean periods
certifies nothing about the fault. Never certify upstream before
inspecting the local router's own config and logs - the local box
can be the cause, and an upstream claim without that inspection is
a guess.
