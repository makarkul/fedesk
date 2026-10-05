---
name: fedora-app
description: >
  Add a desktop application on Fedora as a user-local launcher entry, and
  build an RPM only when asked. Use for a new app, a .desktop file, an
  icon in the application menu, or rpmbuild. Follow the language the user
  asked for.
---

# A desktop app on Fedora

Safety rules for `sudo`, `dnf`, and secrets are in the `fedesk` skill. Do not copy Omarchy's Qt layout, `~/Work/<name>` rule, or PKGBUILD.

## Settle the app

Ask what the one job is if the user did not say. Pick a short lowercase name. That name is the binary, the `.desktop` file, and the icon.

Use the language and toolkit the user asked for. Do not switch the project to C++ and Qt because this is a KDE session.

Put the project where the user said. If they did not say, use a new directory under their home and tell them the path.

## Launcher entry

Install for this user first. Do not copy files into `/usr`.

```
~/.local/share/applications/<name>.desktop
~/.local/share/icons/hicolor/256x256/apps/<name>.png
```

The desktop file needs `Type=Application`, `Name`, `Exec` with a full path or a binary already on `PATH`, and `Icon=<name>`. After writing it:

```bash
update-desktop-database ~/.local/share/applications
```

Log out is not required. If the menu does not show it, check `desktop-file-validate` when that command exists, then re-read the file.

## RPM

Build a package only when the user asks for an RPM or for a system-wide install.

`rpmbuild` is installed. Read `rpmbuild --help` and the Fedora packaging guidelines you are following for the language. A spec file installs into the RPM build root, not into `/usr` by hand. `rpm -qpl` on the built RPM is the check that the payload is what you think it is.

Ask before `sudo dnf install` of the local RPM. Removing it later is `sudo dnf remove <name>`.
