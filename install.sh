#!/bin/bash
# Link the fedora command onto PATH, and link each skill into the
# installed agent harnesses. Safe to re-run. Refuses to replace a real file.

set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skills="$root/skills"

if [[ ! -d $skills || ! -x $root/bin/fedora ]]; then
  printf 'missing skills or bin/fedora under %s\n' "$root" >&2
  exit 1
fi

link_command() {
  local dest="$HOME/.local/bin/fedora"
  local target="$root/bin/fedora"
  mkdir -p "$HOME/.local/bin"
  if [[ -L $dest ]]; then
    ln -sfn "$target" "$dest"
  elif [[ -e $dest ]]; then
    printf 'skip %s (not a symlink)\n' "$dest" >&2
  else
    ln -s "$target" "$dest"
  fi
}

link_into() {
  local dest_root="$1"
  local skill name dest target
  mkdir -p "$dest_root"
  for skill in "$skills"/*/; do
    [[ -d $skill ]] || continue
    name="${skill%/}"
    name="${name##*/}"
    target="$skills/$name"
    dest="$dest_root/$name"
    if [[ -L $dest ]]; then
      ln -sfn "$target" "$dest"
    elif [[ -e $dest ]]; then
      printf 'skip %s (not a symlink)\n' "$dest" >&2
    else
      ln -s "$target" "$dest"
    fi
  done
}

if command -v claude >/dev/null 2>&1; then
  link_into "$HOME/.claude/skills"
fi

if command -v codex >/dev/null 2>&1; then
  link_into "$HOME/.codex/skills"
fi

if command -v grok >/dev/null 2>&1 || [[ -x "$HOME/.grok/bin/grok" ]]; then
  link_into "$HOME/.grok/skills"
fi

link_into "$HOME/.agents/skills"

if [[ -d "$HOME/.cursor" ]]; then
  link_into "$HOME/.cursor/skills"
fi

link_command
