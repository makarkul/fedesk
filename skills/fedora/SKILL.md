---
name: fedora
description: >
  Manage this Fedora machine: packages, updates, power, displays, windows,
  themes, shortcuts, screenshots, terminals, night light, lock, and autostart.
  Use for Fedora, Plasma, KDE, GNOME, KWin, dnf, Spectacle, Konsole, tuned,
  firewalld, or SELinux. Read the session, then plasma.md or gnome.md.
  Does not call an LLM API.
---

# Fedora

Manage this Fedora 44 Workstation. One skill covers every desktop. Read the session, then open one topic file.

Do not run `omarchy`. This machine's command is `fedesk`. There is no Hyprland and no `/usr/share/omarchy`.

## Command

`fedesk` is the supported way to change the machine. Discover the live commands instead of guessing flags:

```bash
fedesk
fedesk commands
fedesk <group>
fedesk <group> <action> --help
```

Use `dnf`, `kscreen-doctor`, `kwriteconfig6`, or `gsettings` only when no `fedesk` command covers the change. Shortcuts, panels, autostart, and GNOME keys are in that second group.

`--yes` skips the confirmation on `fedesk theme set` and `fedesk power set`, and passes `-y` to dnf. Do not add `--yes` unless the user already agreed to that exact change.

## Dispatch

```bash
printf '%s %s\n' "$XDG_CURRENT_DESKTOP" "$XDG_SESSION_TYPE"
```

1. `KDE` → read [plasma.md](plasma.md). X11 and Wayland share `kwinrc`. The binary is `kwin_x11` or `kwin_wayland`.
2. `GNOME` → read [gnome.md](gnome.md).
3. Anything else → stop. Do not write KWin or GNOME keys. Name the compositor you found.

The verified session is Plasma 6.7.5 on X11 (`plasmax11`). GNOME is installed and is not the running session. Re-read the variables every time. Do not trust this paragraph over the live session.

## Safety

- Copy a config file to `file.bak.<unix time>` beside itself before editing it.
- Ask before reboot, power off, `dnf remove`, a full `dnf upgrade`, replacing `~/.config/plasma-org.kde.plasma.desktop-appletsrc`, `setenforce`, or a permanent firewall change.
- Use `sudo` in a terminal where a password can be typed. Do not switch to `pkexec` because a command is privileged.
- Do not hand-edit `/usr`. Install and remove software with `dnf` or `flatpak`.
- Do not write secrets, tokens, or API keys into `/home/makarand/fedora` or into a bug report.

`fedora-crash` and `fedora-app` follow these rules when they change the system.

## Packages

```bash
fedesk pkg search <text>
fedesk pkg info <name>
fedesk pkg add <pkg>...
fedesk pkg remove <pkg>...
fedesk pkg flatpak
fedesk update
```

`dnf` is dnf5 and asks before it changes packages. `fedesk update` with no package names upgrades the system. Flatpak names come from `fedesk pkg flatpak search`.

## Power

`power-profiles-daemon` is not installed. `tuned` is.

```bash
fedesk power status
fedesk power list
fedesk power recommend
fedesk power set <profile>
```

`power set` asks before it switches. Battery and lid behavior stay in `~/.config/powermanagementprofilesrc`. Read that file before editing it. There is no `fedesk` command for it.

## SELinux and firewall

```bash
fedesk selinux status
fedesk firewall status
```

The command does not change either one. Do not set SELinux permissive to make a problem go away. A firewall change that should survive reboot uses `firewall-cmd --permanent` and a reload, and needs a yes first.

## Lock and autostart

```bash
fedesk system lock
fedesk system session
```

Autostart entries are `~/.config/autostart/*.desktop`. A user service is `systemctl --user enable --now <unit>`. List what is already running with `systemctl --user --type=service --state=running` before adding another copy. There is no `fedesk` command for autostart.

## English

A person at a terminal can run `fedesk --ask "Turn Night Light off"` or `fedesk -a "..."`. That flag sends the sentence to the provider named by `FEDORA_PROVIDER` or `~/.config/fedora/agent.conf`. You are already the model when this skill is loaded. Do not call `fedesk --ask`. Run the `fedesk` command.

Do not put an API key in this tree. `fedesk --ask` reads `FEDORA_API_KEY` from the environment only for a non-local HTTP provider.

## Out of scope

- Developing Fedora, KDE, or GNOME upstream.
- Hyprland, Waybar, or Omarchy commands.
- A model proxy or a new API account.
