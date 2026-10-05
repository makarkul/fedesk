#!/bin/sh
# Install fedesk from a checkout, or from a piped download.
# Safe to re-run. Refuses to replace a real file with a symlink.

set -eu

repo_url=https://github.com/makarkul/fedesk.git
dest="${FEDESK_HOME:-$HOME/.local/share/fedesk}"

is_checkout() {
  [ -n "${1:-}" ] && [ -x "$1/bin/fedesk" ] && [ -d "$1/skills" ]
}

root=""
if [ -f "$0" ]; then
  root=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
  if ! is_checkout "$root"; then
    root=""
  fi
fi

if [ -z "$root" ]; then
  command -v git >/dev/null 2>&1 || {
    printf 'git is required\n' >&2
    exit 1
  }
  if [ ! -d "$dest/.git" ]; then
    git clone "$repo_url" "$dest"
  else
    git -C "$dest" fetch --tags origin
  fi
  root=$dest
  ref="${1:-${FEDESK_REF:-}}"
  if [ -n "$ref" ]; then
    git -C "$root" checkout "$ref"
  fi
fi

link_one() {
  dest_path=$1
  target=$2
  mkdir -p "$(dirname "$dest_path")"
  if [ -L "$dest_path" ]; then
    ln -sfn "$target" "$dest_path"
  elif [ -e "$dest_path" ]; then
    printf 'skip %s (not a symlink)\n' "$dest_path" >&2
  else
    ln -s "$target" "$dest_path"
  fi
}

link_into() {
  dest_root=$1
  skill=""
  name=""
  mkdir -p "$dest_root"
  for skill in "$root/skills"/*; do
    [ -d "$skill" ] || continue
    name=$(basename "$skill")
    link_one "$dest_root/$name" "$skill"
  done
}

if command -v claude >/dev/null 2>&1; then
  link_into "$HOME/.claude/skills"
fi

if command -v codex >/dev/null 2>&1; then
  link_into "$HOME/.codex/skills"
fi

if command -v grok >/dev/null 2>&1 || [ -x "$HOME/.grok/bin/grok" ]; then
  link_into "$HOME/.grok/skills"
fi

link_into "$HOME/.agents/skills"

if [ -d "$HOME/.cursor" ]; then
  link_into "$HOME/.cursor/skills"
fi

link_one "$HOME/.local/bin/fedesk" "$root/bin/fedesk"
old="$HOME/.local/bin/fedora"
if [ -L "$old" ]; then
  current=$(readlink "$old")
  case "$current" in
    */bin/fedora|*/bin/fedesk) rm -f "$old" ;;
  esac
fi
printf 'installed %s\n' "$root"
