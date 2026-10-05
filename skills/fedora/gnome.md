# GNOME

Use this only when `XDG_CURRENT_DESKTOP` contains `GNOME`. Safety rules are in [SKILL.md](SKILL.md).

Do not edit `kwinrc`, `kglobalshortcutsrc`, or `plasma-org.kde.plasma.desktop-appletsrc` in a GNOME session. Those files belong to Plasma.

This machine has GNOME sessions installed and was last verified while Plasma was the running session. Re-check the session variables. If they are not GNOME, go back to [SKILL.md](SKILL.md).

## Settings

Write keys with `gsettings` only. Read the schema and the current value first.

```bash
gsettings list-schemas
gsettings list-keys <schema>
gsettings get <schema> <key>
gsettings describe <schema> <key>
gsettings set <schema> <key> <value>
```

Schemas present here include `org.gnome.desktop.interface`, `org.gnome.desktop.background`, `org.gnome.desktop.screensaver`, `org.gnome.desktop.wm.keybindings`, and `org.gnome.desktop.wm.preferences`. List keys again before setting one. A range or enum from `describe` overrides a guessed value.

`gsettings set` applies to the user session. Do not edit dconf binary files by hand.

## Terminal

Ptyxis is the GNOME terminal installed on this machine (`/usr/bin/ptyxis`). Konsole and Alacritty are also installed. Change the terminal the user named. If they did not name one, change Ptyxis while this session is GNOME.

Ptyxis profiles appear under `~/.config/ptyxis` after one is saved. Read that directory before creating a second profile.

## Theme and capture

`gnome-screenshot` and `grim` are not installed. Find a capture tool with `command -v` before taking a shot. Spectacle is a Plasma app and may run, but do not assume its KWin path.

Do not invent a theme command. Look for an installed setter (`command -v`) and read its `--help`. Interface font and color-scheme keys, when they exist, are on `org.gnome.desktop.interface`. Read them with `gsettings get` before `gsettings set`.
