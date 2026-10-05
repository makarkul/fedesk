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

`install.sh` links `fedora` to `~/.local/bin/fedora` and links each skill into the harness directories for tools that are installed here. Re-running it updates the links. It does not copy the files. `~/.local/bin` is already on `PATH`.

```bash
./install.sh
```

Links:

- `~/.claude/skills/` when `claude` is on `PATH`
- `~/.codex/skills/` when `codex` is on `PATH`
- `~/.grok/skills/` when Grok is installed
- `~/.agents/skills/` for other harnesses
- `~/.cursor/skills/` when `~/.cursor` exists

Grok also reads the Claude and Codex skill directories and keeps a single skill when the name is the same.

The source of truth is `/home/makarand/fedora/skills`. Edit those files. Do not edit the symlinks.
