# Fedora desktop skills

Agent skills and the `fedora` command for this Fedora 44 Workstation. They replace the Omarchy skills for managing the machine. The command is the same idea as `omarchy`: one entry point, groups, and `--help`.

```bash
fedora
fedora commands
fedora theme list
fedora capture screenshot
fedora system lock
fedora --ask "Turn Night Light off"
```

`fedora --ask` (or `fedora -a`) sends the sentence to the model even when no skill covers it. A matching `fedora` command is used when one fits. Otherwise the model answers and may run another installed program. It does not store an API key. The provider is `FEDORA_PROVIDER` or `~/.config/fedora/agent.conf`: `grok`, `claude`, or `codex` use that program's existing login; `ollama` is local and needs no key; `openai` is any OpenAI-compatible URL and needs `FEDORA_API_KEY` only when the host is not localhost. With nothing set, it uses Ollama if a model is installed, otherwise an agent CLI that is already on `PATH`. Run `fedora --ask --help`.

The instructions are plain `SKILL.md` files. They do not call an LLM API and they do not store keys. Claude Code, Codex, Grok, Cursor, and any harness that reads the Agent Skills layout can load the same directories.

| Skill | Use |
| --- | --- |
| `fedora` | Desktop and system changes. Reads the session, then `plasma.md` or `gnome.md`. |
| `fedora-crash` | A crash, from ABRT and `coredumpctl`. |
| `fedora-app` | A launcher entry, or an RPM when you ask for one. |

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/makarkul/fedesk/main/install.sh | sh
```

That clones the repo to `~/.local/share/fedesk` and links `fedora` onto `~/.local/bin`. To install a named version:

```sh
curl -fsSL https://raw.githubusercontent.com/makarkul/fedesk/main/install.sh | sh -s -- v0.1.0
```

From a checkout, `./install.sh` only refreshes the links for that checkout.

## Version

```sh
fedora version
fedora upgrade
fedora upgrade 0.1.0
fedora downgrade 0.1.0
```

`fedora version` prints the fedesk release, then the Fedora and desktop versions. `upgrade` with no version checks out the newest `v*` tag. A version argument checks out that tag, so the same command moves forward or back. `downgrade` requires a version.

Links:

- `~/.claude/skills/` when `claude` is on `PATH`
- `~/.codex/skills/` when `codex` is on `PATH`
- `~/.grok/skills/` when Grok is installed
- `~/.agents/skills/` for other harnesses
- `~/.cursor/skills/` when `~/.cursor` exists

Grok also reads the Claude and Codex skill directories and keeps a single skill when the name is the same.

The source of truth is the checkout `install.sh` printed. Edit those files. Do not edit the symlinks.
