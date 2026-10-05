#!/usr/bin/env python3
"""Send one English sentence to the configured model.

A skill is optional. The model answers in its own words and may run a
fedesk command or any other installed program. This file never stores an
API key. A key is read from FEDORA_API_KEY only when the HTTP endpoint is
not on localhost.
"""

import json
import os
import shlex
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

MAX_ROUNDS = 6
BIN_DIR = os.path.dirname(os.path.abspath(__file__))
FEDORA = os.path.join(BIN_DIR, "fedesk")
CONFIG_PATH = os.path.expanduser("~/.config/fedora/agent.conf")

SYSTEM = """You are the assistant for this Fedora machine. The user's sentence is the task.
A skill is optional. Do the work even when no fedesk command covers it.

Reply with any of these:
- short explanation lines
- RUN: <one command and its arguments>
- ASK: <one question, only when you cannot proceed>
- DONE when the task is finished

Prefer a fedesk command from the list below when one fits.
Otherwise use the real installed program, such as nmcli, dnf, or kwriteconfig6.
Look up a live name before you change it, in the same reply, as a RUN line.
Never stop after only saying what you will do. A reply that takes an action must contain RUN.
One command per RUN line. No pipes, redirects, command substitution, or --yes.
"Turn the lights off" means Night Light: RUN: fedesk nightlight off.
"""


class Rejected(Exception):
    pass


def die(message, code=1):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def load_env_file():
    """Apply ~/.config/fedora/env when the shell did not source it.

    Values already exported in the environment win.
    """
    path = os.path.expanduser("~/.config/fedora/env")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if not key or key in os.environ:
                continue
            os.environ[key] = value.strip().strip('"').strip("'")


def load_config():
    cfg = {}
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip().lower()
                value = value.strip().strip('"').strip("'")
                if key in {"key", "api_key", "apikey", "token", "secret"}:
                    print(
                        "Ignoring a key in ~/.config/fedora/agent.conf. "
                        "Put it in the FEDORA_API_KEY environment instead.",
                        file=sys.stderr,
                    )
                    continue
                cfg[key] = value
    for key, env in (
        ("provider", "FEDORA_PROVIDER"),
        ("base", "FEDORA_API_BASE"),
        ("model", "FEDORA_MODEL"),
    ):
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    return cfg


def ollama_model():
    try:
        out = subprocess.check_output(["ollama", "list"], text=True, timeout=5, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    lines = [line for line in out.splitlines()[1:] if line.strip()]
    if not lines:
        return None
    return lines[0].split()[0]


def command_list():
    out = subprocess.check_output([FEDORA, "commands"], text=True)
    groups = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] == "fedesk":
            groups.add(parts[1])
    if not groups:
        die("Could not read the fedesk command list.")
    return out.strip(), groups


def local_base(base):
    host = (urllib.parse.urlparse(base).hostname or "").lower()
    return host in {"localhost", "127.0.0.1", "::1"}


def resolve(cfg):
    provider = (cfg.get("provider") or "auto").lower()
    model = cfg.get("model") or ""
    base = cfg.get("base") or ""
    if provider == "auto":
        if base:
            provider = "openai"
        else:
            found = ollama_model()
            if found:
                provider = "ollama"
                model = model or found
            elif shutil_which("grok"):
                provider = "grok"
            elif shutil_which("claude"):
                provider = "claude"
            elif shutil_which("codex"):
                provider = "codex"
            else:
                die(usage_text())
    return provider, base, model


def shutil_which(name):
    from shutil import which
    return which(name)


def usage_text():
    return """Usage:
  fedesk --ask "Turn Night Light off"
  fedesk -a "Turn Night Light off"

The sentence is sent to one model. fedesk does not have a built-in key.
It reads ~/.config/fedora/env itself, then FEDORA_PROVIDER, then
~/.config/fedora/agent.conf. A variable already set in the shell wins.

  grok, claude, codex
      Uses that program's existing login. No API key is read by fedesk.
  ollama
      Local. No API key. Set FEDORA_MODEL to a model from `ollama list`.
  openai
      Any OpenAI-compatible HTTP endpoint.
      FEDORA_API_BASE is the URL ending in /v1.
      FEDORA_MODEL is the model name.
      FEDORA_API_KEY is required only when the host is not localhost.

Examples:
  FEDORA_PROVIDER=ollama FEDORA_MODEL=llama3.1 fedesk --ask "Turn Night Light off"
  FEDORA_PROVIDER=openai FEDORA_API_BASE=https://api.openai.com/v1 \\
    FEDORA_MODEL=gpt-4.1-mini FEDORA_API_KEY=... fedesk -a "Lock the screen"
  FEDORA_PROVIDER=grok fedesk -a "Turn Night Light off"
"""


def parse(text):
    runs = []
    asks = []
    done = False
    for raw in text.splitlines():
        line = raw.strip().lstrip("-*").strip()
        if line.startswith("`") and line.endswith("`"):
            line = line[1:-1].strip()
        if not line:
            continue
        head, _, rest = line.partition(":")
        kind = head.strip().upper()
        if kind == "RUN":
            runs.append(rest.strip())
        elif kind == "ASK":
            asks.append(rest.strip())
        elif kind == "DONE":
            done = True
    return runs, asks, done


def command_argv(command, groups):
    if any(char in command for char in ";&|`$<>(){}\\\n"):
        raise Rejected(f"Refusing to run: {command}")
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        raise Rejected(f"Refusing to run: {command} ({exc})") from exc
    if not argv:
        raise Rejected(f"Refusing to run: {command}")
    if argv[0] == "fedesk":
        if "--yes" in argv:
            raise Rejected("Refusing --yes from the model.")
        argv[0] = FEDORA
    return argv


def validate(command, groups):
    try:
        return command_argv(command, groups)
    except Rejected as exc:
        die(str(exc))


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Run one command on this machine and return its output. "
                "Use this for every lookup and every change."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "One command and its arguments. No pipes or redirects.",
                    }
                },
                "required": ["command"],
            },
        },
    }
]


def chat_http(base, model, messages, tools=None):
    if not base or not model:
        die("HTTP providers need FEDORA_API_BASE and FEDORA_MODEL.\n" + usage_text())
    key = os.environ.get("FEDORA_API_KEY", "")
    if not key and not local_base(base):
        die(
            "This endpoint is not local, so it needs FEDORA_API_KEY in the environment. "
            "fedesk does not store the key."
        )
    url = base.rstrip("/") + "/chat/completions"
    payload = {"model": model, "temperature": 0, "messages": messages}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    if key:
        request.add_header("Authorization", "Bearer " + key)
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:500]
        die(f"Model request failed ({exc.code}). {body}")
    except urllib.error.URLError as exc:
        die(f"Model request failed: {exc.reason}")
    try:
        return data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        die("Model response did not contain a message.")


def chat_cli(provider, model, messages):
    system = messages[0]["content"]
    transcript = "\n\n".join(item["content"] for item in messages[1:])
    if provider == "grok":
        command = [
            "grok", "-p", transcript,
            "--system-prompt-override", system,
            "--output-format", "plain",
            "--no-plan", "--no-subagents", "--disable-web-search",
            "--tools", "",
            "--max-turns", "1",
        ]
    elif provider == "claude":
        command = [
            "claude", "-p", transcript,
            "--system-prompt", system,
            "--tools", "",
            "--output-format", "text",
        ]
    elif provider == "codex":
        command = [
            "codex", "exec",
            "--sandbox", "read-only",
            "--skip-git-repo-check",
            "--color", "never",
            system + "\n\n" + transcript,
        ]
    else:
        die(f"Unknown provider: {provider}")
    if model and provider in {"grok", "claude"}:
        command[1:1] = ["--model", model]
    if model and provider == "codex":
        command[2:2] = ["--model", model]
    try:
        completed = subprocess.run(
            command, text=True, capture_output=True, timeout=180, check=False
        )
    except subprocess.TimeoutExpired:
        die(f"{provider} timed out.")
    except OSError as exc:
        die(f"Could not run {provider}: {exc}")
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        die(f"{provider} failed.\n{detail[:800]}")
    return completed.stdout


def complete(provider, base, model, messages):
    if provider in {"grok", "claude", "codex"}:
        return chat_cli(provider, model, messages)
    die(f"Unknown provider: {provider}\n" + usage_text())


def execute_command(command, groups):
    try:
        argv = command_argv(command, groups)
    except Rejected as exc:
        print(str(exc), file=sys.stderr)
        return str(exc)
    print("+ " + command, file=sys.stderr)
    completed = subprocess.run(argv, text=True, capture_output=True, check=False)
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return (
        f"exit {completed.returncode}\n"
        f"{completed.stdout}{completed.stderr}"
    )


def run_http(sentence, base, model, groups):
    system = (
        "You are on the user's Fedora machine and you have the run_command tool. "
        "Call it for every lookup and every change. Do not tell the user to run a command. "
        "Do not stop after saying what you will do. "
        "Prefer a fedesk command when one fits. Otherwise use the installed program, such as nmcli. "
        "One command per call. No pipes, redirects, command substitution, or --yes.\n\n"
        "Commands:\n" + command_list()[0]
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": sentence},
    ]
    nudged = False
    for _ in range(MAX_ROUNDS):
        message = chat_http(base, model, messages, TOOLS)
        calls = message.get("tool_calls") or []
        content = message.get("content") or ""
        if content.strip():
            print(content.strip())
        assistant = {"role": "assistant", "content": content or None}
        if calls:
            assistant["tool_calls"] = calls
        messages.append(assistant)
        if not calls:
            if nudged:
                return 0
            nudged = True
            messages.append({
                "role": "user",
                "content": "Call run_command now. Do not describe the command.",
            })
            continue
        for call in calls:
            function = call.get("function") or {}
            name = function.get("name")
            raw_args = function.get("arguments") or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                result = "rejected: arguments were not valid JSON"
            else:
                if name != "run_command":
                    result = f"rejected: unknown tool {name}"
                else:
                    result = execute_command(str(args.get("command") or ""), groups)
            messages.append({
                "role": "tool",
                "tool_call_id": call.get("id"),
                "content": result,
            })
    die("Stopped after too many model steps.")


def run_sentence(sentence, provider, base, model, groups):
    system = SYSTEM + "\nCommands:\n" + command_list()[0]
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": sentence},
    ]
    for _ in range(MAX_ROUNDS):
        text = complete(provider, base, model, messages)
        runs, asks, done = parse(text)
        spoken = [
            raw for raw in text.splitlines()
            if raw.strip()
            and not raw.strip().startswith("RUN:")
            and not raw.strip().startswith("ASK:")
            and raw.strip() != "DONE"
            and not raw.strip().startswith("DONE:")
        ]
        if spoken:
            print("\n".join(spoken))
        if asks and not runs:
            print("\n".join(asks))
            return 0
        messages.append({"role": "assistant", "content": text})
        if not runs:
            if done:
                return 0
            messages.append({
                "role": "user",
                "content": (
                    "No command ran. If the task is finished, reply DONE. "
                    "If you need the user, reply ASK. "
                    "Otherwise reply with the RUN line for the next command now."
                ),
            })
            continue
        results = []
        for command in runs:
            argv = validate(command, groups)
            print("+ " + command, file=sys.stderr)
            completed = subprocess.run(argv, text=True, capture_output=True, check=False)
            sys.stdout.write(completed.stdout)
            sys.stderr.write(completed.stderr)
            results.append(
                f"$ {command}\nexit {completed.returncode}\n"
                f"{completed.stdout}{completed.stderr}"
            )
        if done:
            return 0
        messages.append({"role": "user", "content": "Output:\n" + "\n".join(results)})
    die("Stopped after too many model steps.")


def self_test():
    groups = {"nightlight", "theme", "pkg", "version"}
    argv = validate("fedesk nightlight off", groups)
    assert argv[1:] == ["nightlight", "off"]
    assert argv[0] == FEDORA
    other = validate("nmcli connection show", groups)
    assert other == ["nmcli", "connection", "show"]
    for bad in (
        "fedesk nightlight off; rm -rf /",
        "fedesk theme set x --yes",
        "nmcli -f NAME connection show | cat",
    ):
        try:
            validate(bad, groups)
        except SystemExit:
            continue
        raise SystemExit(f"accepted bad command: {bad}")
    runs, asks, done = parse("RUN: fedesk nightlight off\nDONE\n")
    assert runs == ["fedesk nightlight off"] and done and not asks
    runs, asks, done = parse("I'll look it up.\nRun: nmcli connection show\n")
    assert runs == ["nmcli connection show"] and not done
    runs, asks, done = parse("ASK: Which display?\n")
    assert asks == ["Which display?"] and not runs
    print("ok")


def main(argv):
    if os.environ.get("FEDORA_ASK_SELFTEST") == "1":
        self_test()
        return 0
    if not argv or argv[0] in {"--help", "-h"}:
        print(usage_text(), end="")
        return 0 if argv else 2
    sentence = " ".join(argv).strip()
    if not sentence:
        print(usage_text(), end="")
        return 2
    load_env_file()
    cfg = load_config()
    provider, base, model = resolve(cfg)
    if provider == "ollama" and not model:
        model = ollama_model()
        if not model:
            die("Ollama has no model. Run `ollama pull <name>` and set FEDORA_MODEL.")
    if provider == "openai" and not (base and model):
        die("Set FEDORA_API_BASE and FEDORA_MODEL.\n" + usage_text())
    _, groups = command_list()
    note = {
        "grok": "existing grok login, no API key",
        "claude": "existing claude login, no API key",
        "codex": "existing codex login, no API key",
        "ollama": "local Ollama, no API key",
        "openai": "OpenAI-compatible endpoint",
    }[provider]
    print(f"provider: {provider} ({note})", file=sys.stderr)
    if provider in {"openai", "ollama"}:
        if provider == "ollama" and not base:
            base = "http://127.0.0.1:11434/v1"
        return run_http(sentence, base, model, groups)
    return run_sentence(sentence, provider, base, model, groups)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
