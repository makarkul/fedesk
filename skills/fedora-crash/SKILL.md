---
name: fedora-crash
description: >
  Diagnose why a program crashed on this Fedora machine, from ABRT and from
  a systemd core dump when core_pattern says so. Use for a segfault, abort,
  core dump, abrt, coredumpctl, or "why did X crash". Covers reporting a
  confirmed bug. See reporting.md.
---

# Diagnosing a crash

Work from evidence. Safety rules for any system change are in the `fedesk` skill. Diagnosis reads. It does not tune, update, or reconfigure unless the user asks.

## Where the core went

Read the handler before choosing a tool.

```bash
cat /proc/sys/kernel/core_pattern
```

On this machine the pattern pipes to `systemd-coredump`, and `coredumpctl` is installed (from the `systemd-udev` package, not a package named `systemd-coredump`). ABRT is also installed (`abrt-cli`, `abrt-addon-ccpp`) and keeps its own problem list. Use both. If `core_pattern` no longer names `systemd-coredump`, say so and follow the handler that is actually configured.

```bash
fedesk crash status
fedesk crash list
fedesk crash info <id>
fedesk crash cores
coredumpctl info <pid>
```

`fedesk crash` is the list and the summary. `coredumpctl info` is still the command-line and signal detail for one dump.

`abrt-cli list` can be long. Match the program and the time. Do not report the whole backlog.

From `coredumpctl info`, record the command line, signal, timestamp, and executable. The command line is often the whole story.

## Rule out the boring causes

Check memory and the journal before blaming the program.

```bash
free -h
journalctl --since "30 min ago" -p warning --no-pager
```

A process the OOM killer stopped is not a bug in that process. A crash that starts immediately after a `dnf` update points at that update. `dnf history` shows it.

## Read more than the first frame

`abrt-cli bt <id>` and `coredumpctl info` show the crashing thread. Other threads show work that was in flight. Note plugins and out-of-tree drivers in the mapping. Do not blame them without a frame or a log line that implicates them.

## Symbolize when you can

Fedora's debuginfod URL is already configured in `/etc/debuginfod/elfutils.urls`. Use the environment the system set. Do not point gdb at `debuginfod.archlinux.org`.

A core is a copy of process memory. It can hold passwords and private files. Write it to a fresh temp path and delete it.

```bash
core=$(mktemp -t crash-XXXXXX.core)
trap 'rm -f "$core"' EXIT
coredumpctl dump <pid> --output="$core"
gdb -q <executable> "$core" -batch -ex 'set debuginfod enabled on' -ex 'bt'
```

When frames stay unresolved, say so. Do not invent function names. The library each frame belongs to is still evidence.

`abrt-cli gdb <id>` and `abrt-cli retrace <id>` are the ABRT paths. Read `abrt-cli <command> --help` before adding flags. Retrace may upload a core. Do not run it unless the user agrees to send the dump.

## Report

1. What crashed, and the command line it was started with.
2. The likely mechanism. Separate what the evidence proves from what you infer.
3. Whether user data was lost, and where a copy might still be.
4. Whether it is likely to happen again, and what would avoid it.

If the cause is ambiguous, say so.

Leave the system as you found it. Delete the core you extracted. Do not mute ABRT or notification popups unless the user asks, and then say how to turn them back on.

## If it is a distribution bug

Most crashes belong to the upstream application. When the cause is in Fedora packaging, KDE, GNOME, or the kernel as shipped here, read [reporting.md](reporting.md) before offering to file anything.
