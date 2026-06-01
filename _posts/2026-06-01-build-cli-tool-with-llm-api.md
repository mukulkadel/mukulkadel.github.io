---
layout: post
title: "Building a CLI Tool That Uses an LLM API"
date: "2026-06-01 00:00:00 +0530"
slug: build-cli-tool-with-llm-api
description: "Build a real command-line tool backed by an LLM API using Python and Click. We'll cover streaming output, multi-turn conversations, and piping from stdin."
categories: ["Programming", "Tutorials"]
tags: ["llm", "cli", "python", "api", "claude", "openai", "tutorial", "command line", "automation", "ai"]
---

LLM APIs unlock a new category of command-line tools — ones that understand natural language, can explain code, transform text, or answer questions about piped-in content. Building one is simpler than it sounds: you need an HTTP client, an API key, and about 50 lines of Python. We'll build a `ask` CLI that handles streaming output, multi-turn conversations, and reading from stdin, so you can pipe it into any Unix workflow.

## Project Setup

```bash
$ mkdir ask-cli && cd ask-cli
$ python -m venv .venv && source .venv/bin/activate
$ pip install click anthropic rich
```

We'll use the Anthropic SDK for Claude, `click` for the CLI interface, and `rich` for pretty terminal output.

## A Minimal Version First

Before adding features, let's get a working call to the API:

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is a closure in Python?"}],
)
print(response.content[0].text)
```

```
A closure is a function that remembers the variables from its enclosing scope
even after that scope has finished executing...
```

Now let's turn this into an actual CLI.

## Building the CLI with Click

```python
import sys
import click
import anthropic
from rich.console import Console
from rich.markdown import Markdown

client = anthropic.Anthropic()
console = Console()

@click.command()
@click.argument("prompt", nargs=-1)
@click.option("--model", "-m", default="claude-sonnet-4-6", help="Model to use")
@click.option("--max-tokens", default=2048)
@click.option("--system", "-s", default="You are a helpful assistant.", help="System prompt")
def ask(prompt, model, max_tokens, system):
    """Ask an LLM a question. Reads from stdin if no prompt given."""

    if prompt:
        user_message = " ".join(prompt)
    elif not sys.stdin.isatty():
        stdin_content = sys.stdin.read().strip()
        user_message = stdin_content
    else:
        click.echo("Usage: ask [PROMPT] or pipe content via stdin", err=True)
        raise SystemExit(1)

    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        full_response = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text
        print()

if __name__ == "__main__":
    ask()
```

The `nargs=-1` on `ARGUMENT` means click collects all positional arguments as a tuple, so you don't need to quote multi-word prompts.

## Using It

```bash
$ python ask.py What is the difference between a process and a thread?
A process is an independent program instance with its own memory space.
A thread is a lighter unit of execution that shares memory with other threads
in the same process. Threads are faster to create and communicate through
shared memory, but require careful synchronization to avoid race conditions...

$ cat error.log | python ask.py Summarize the errors in this log file
There are 3 distinct error types in this log:
1. ConnectionRefused (47 occurrences) — database appears unreachable between 14:22 and 14:45
2. TimeoutError (12 occurrences) — external API calls timing out, mostly to payments service
3. NullPointerException (3 occurrences) — in UserController.java line 142
```

The pipe case is especially powerful — you can feed it code, log files, JSON, or any text and ask a question about it.

## Adding Multi-Turn Conversation

For interactive sessions where you want to ask follow-up questions, we need to maintain conversation history:

```python
@click.command()
@click.option("--model", "-m", default="claude-sonnet-4-6")
@click.option("--system", "-s", default="You are a helpful assistant.")
def chat(model, system):
    """Start an interactive multi-turn conversation."""
    messages = []
    console.print("[bold green]Chat started. Type 'exit' or press Ctrl+C to quit.[/bold green]")

    while True:
        try:
            user_input = click.prompt("\nYou", prompt_suffix="> ")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower() in ("exit", "quit", "bye"):
            break

        messages.append({"role": "user", "content": user_input})

        console.print("\n[bold blue]Assistant[/bold blue]> ", end="")
        full_response = ""

        with client.messages.stream(
            model=model,
            max_tokens=2048,
            system=system,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_response += text
            print()

        messages.append({"role": "assistant", "content": full_response})
```

Each turn appends both the user message and the assistant's reply to `messages`. The next API call includes the full history, which is how the model maintains context across turns.

## Piping to Other Commands

Because the output is plain text by default, you can pipe it into standard Unix tools:

```bash
$ python ask.py "List 10 common HTTP status codes" | grep "^[0-9]"
200 OK
201 Created
301 Moved Permanently
400 Bad Request
...

$ git diff HEAD~1 | python ask.py "Write a commit message for this diff"
fix: handle null user in session middleware

Adds an early return in the session middleware when the user object is null,
preventing a NullPointerException when unauthenticated requests reach routes
that call session.getUser().
```

## Making It a Proper CLI Tool

To install it system-wide as a real command:

```
# pyproject.toml
[project]
name = "ask-cli"
version = "0.1.0"
dependencies = ["click", "anthropic", "rich"]

[project.scripts]
ask = "ask_cli.main:ask"
chat = "ask_cli.main:chat"
```

```bash
$ pip install -e .
$ ask What is idempotency in REST APIs?
```

## Conclusion

A working LLM-backed CLI is about 80 lines of Python — the SDK, a Click command, and streaming output. The real leverage comes from composing it with Unix tools: pipe in code, logs, or documents, and pipe the output into `grep`, `jq`, or other commands. Once you have the basic pattern down, you can extend it with tool use (letting the model run shell commands), persistent conversation history via a JSON file, or specialized system prompts for different tasks like code review or log analysis.
