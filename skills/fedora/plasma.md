# Plasma

Use this only when `XDG_CURRENT_DESKTOP` is `KDE`. Safety rules are in [SKILL.md](SKILL.md).

Plasma on this machine is 6.7.5. There is no `qdbus6`. Read live properties with `busctl`. KWin picks up `kwinrc` after:

```bash
dbus-send --session --dest=org.kde.KWin --type=method_call /KWin org.kde.KWin.reconfigure
```

`fedesk nightlight` and `fedesk theme` already do this. Do not use `busctl call` for `reconfigure`; that method does not send a reply.

Restarting `plasmashell` or the session needs a yes. It drops the current desktop arrangement.

## Windows and desktops

`~/.config/kwinrc` holds virtual desktops (`[Desktops]`), Night Light (`[NightColor]`), tiling (`[Tiling]`), and Xwayland scale (`[Xwayland]`). Read the file before changing a group. Do not rewrite the whole file to change one key.

```bash
kreadconfig6 --file kwinrc --group Desktops --key Number
kwriteconfig6 --file kwinrc --group Desktops --key Number 4
```

The running binary follows the session: `kwin_x11` on X11, `kwin_wayland` on Wayland. Fractional scale from `kscreen-doctor` works on Wayland only. On X11, scale is the integer `[Xwayland] Scale` key.

## Shortcuts

Global shortcuts live in `~/.config/kglobalshortcutsrc`. A value is `current,default,label`. Change `current` and leave `default` and `label` in place. Search the file for the action before adding a second binding.

`kglobalaccel` is on the session bus as `org.kde.kglobalaccel`. After an edit, do not log the user out unless they ask. Tell them the binding applies when that component reloads.

## Displays

```bash
fedesk display list
fedesk display set output.HDMI-2.position.1920,0 output.eDP-1.position.0,0
```

`display set` forwards every argument to one `kscreen-doctor` invocation, so the layout changes atomically. Read `kscreen-doctor --help` for mode, rotation, HDR, and scale. Use an output name from `fedesk display list`, not a guessed `HDMI-1`.

## Panels and widgets

The panel layout is `~/.config/plasma-org.kde.plasma.desktop-appletsrc`. It is easy to break. Prefer System Settings, or add a widget through the panel editor.

Editing that file requires a backup and a yes. Do not replace the file with a stock layout. `plasma-apply-lookandfeel --resetLayout` resets the whole desktop arrangement and also needs a yes.

## Night Light

```bash
fedesk nightlight status
fedesk nightlight on
fedesk nightlight off
```

Do not assume it is on. `status` reads `kwinrc` and the live KWin property. Schedule and temperature stay in the `[NightColor]` group. Read those keys before writing them. `on` and `off` only change `Active`.

## Theme, wallpaper, and fonts

List, then apply. The argument is a name from the list, not a theme you remember from another distro.

```bash
fedesk theme list
fedesk theme set <package>
fedesk theme colors [scheme]
fedesk theme desktop [theme]
fedesk theme wallpaper <file>
fedesk theme accent <name-or-hex>
fedesk font show
fedesk font set <font-string>
```

`fedesk theme set` asks before it applies a global theme, because that can change panels and widgets. Do not pass `--yes` unless the user already agreed. A partial name is accepted only when it matches one theme.

`font set` writes the raw Plasma font string. Read `fedesk font show` first and keep the same comma-separated shape.

Extra Plasma packages (themes, plasmoids) install with `kpackagetool6`. Read `--help` for the package type flag. There is no `fedesk` command for that.

## Terminals

Find the binary. Do not configure Kitty, Ghostty, or Foot unless `command -v` shows they were installed later.

| Terminal | Config |
| --- | --- |
| Konsole | `~/.config/konsolerc` and profiles in `~/.local/share/konsole/*.profile` |
| Alacritty | `~/.alacritty.toml` on this machine. Also check `~/.config/alacritty/alacritty.toml` if the user creates it |
| Ptyxis | GNOME terminal. Config path is under `~/.config/ptyxis` when a profile exists. See [gnome.md](gnome.md) |

A new Konsole window reads the profile. An existing window keeps the old colors until it is reopened.

## Screenshots and recording

```bash
fedesk capture screenshot
fedesk capture screenshot monitor
fedesk capture screenshot window
fedesk capture screenshot region -o ~/Pictures/shot.png
fedesk capture record screen
```

The default screenshot is the whole desktop, saved under Pictures. `region` and `record` are interactive. `grim` is not installed. KSnip is for editing a shot after it exists, not for taking the first one. Read `fedesk capture screenshot --help` before reaching for `spectacle` flags such as delay or pointer.
