# Reporting a crash

Filing is opt-in. A diagnosis does not become a bug report unless the user asks.

## Who owns it

- Fedora packaging, the kernel build, or a default Workstation component → Red Hat Bugzilla, product Fedora. `abrt-cli report <id>` knows this path.
- Plasma, KWin, or Spectacle, and the same crash happens with upstream KDE → KDE Bugzilla. Say that Fedora's package version may lag upstream.
- GNOME session components, and the crash happened in a GNOME session → GNOME's tracker.
- Any other application → that project's tracker, not Fedora's, unless a Fedora patch is in the stack.

If two of these are plausible, say so and let the user choose. Do not file duplicates.

## Before filing

Search the existing report. `abrt-cli list` shows whether this machine already recorded the same crash. Search Bugzilla for the top resolved function and the package name.

Include:

- Fedora release (`rpm -q fedora-release`) and the package version (`rpm -q <pkg>`)
- The signal, the executable, and the command line
- The backtrace you actually have, marked where symbols are missing
- What changed just before (update, config edit, new monitor)
- Whether SELinux denied anything (`ausearch -m avc -ts recent` when a denial is part of the theory)

Leave out home-directory contents, command arguments that contain secrets, and the core file unless the user explicitly wants it uploaded.

## ABRT

```bash
abrt-cli info <id>
abrt-cli report --help
abrt-cli report <id>
```

`report` can send the core and environment to a remote tracker. Run it only after the user has seen `info` and agreed. Do not pass `--authenticate` unless the report cannot be read without it. Do not remove the problem with `abrt-cli remove` after filing unless the user asks.
