---
layout: post
title: "VS Code Setup for Backend Developers: Extensions and Settings"
date: "2026-06-01 00:00:00 +0530"
slug: vscode-setup-backend-developers
description: "A practical VS Code setup for backend developers: the extensions that actually help, settings worth changing, and keybindings for common workflows."
categories: ["wiki", "Programming"]
tags: ["vscode", "visual studio code", "extensions", "backend", "productivity", "editor", "settings", "developer tools", "cheatsheet"]
---

VS Code's default configuration is a reasonable starting point but leaves most of its value on the table. The right extensions automate repetitive tasks, and a few settings changes eliminate daily friction that you'd otherwise accept as normal. This guide is opinionated and focused — it covers what's genuinely useful for backend development, not every extension that exists.

## Installation

```bash
$ brew install --cask visual-studio-code
```

Add the `code` CLI command from the command palette (`Cmd+Shift+P`): type "Shell Command: Install 'code' command in PATH".

```bash
$ code .           # open current directory
$ code file.py     # open a specific file
$ code --diff a.py b.py  # diff two files
```

## Essential Extensions

Install via the command line using `code --install-extension`:

```bash
# Language support
$ code --install-extension ms-python.python
$ code --install-extension ms-python.vscode-pylance
$ code --install-extension golang.go
$ code --install-extension rust-lang.rust-analyzer
$ code --install-extension ms-vscode.vscode-typescript-next

# Database
$ code --install-extension cweijan.vscode-database-client2

# Git
$ code --install-extension eamodio.gitlens
$ code --install-extension mhutchie.git-graph

# API testing
$ code --install-extension humao.rest-client

# Docker/K8s
$ code --install-extension ms-azuretools.vscode-docker
$ code --install-extension ms-kubernetes-tools.vscode-kubernetes-tools

# Formatting and linting
$ code --install-extension esbenp.prettier-vscode
$ code --install-extension ms-python.black-formatter
$ code --install-extension charliermarsh.ruff

# Utilities
$ code --install-extension usernamehw.errorlens
$ code --install-extension streetsidesoftware.code-spell-checker
$ code --install-extension christian-kohler.path-intellisense
$ code --install-extension mikestead.dotenv
```

### What each one does

**GitLens** — enriches the built-in git integration. The killer feature is inline blame that shows who changed a line and when, right in the editor margin. Hover to see the full commit message.

**REST Client** — lets you write `.http` files and send requests directly from VS Code. Much faster than switching to Postman for quick tests:

```http
### Get user
GET https://api.example.com/users/42
Authorization: Bearer {{token}}
Content-Type: application/json

### Create post
POST https://api.example.com/posts
Content-Type: application/json

{
  "title": "Hello World",
  "body": "My first post"
}
```

Press `Send Request` above each block. Responses appear in a split pane. You can reference variables from a `.env` file.

**ErrorLens** — moves error and warning messages inline, next to the offending code. No more hunting through the Problems panel.

**Database Client** — connect to PostgreSQL, MySQL, Redis, MongoDB, or SQLite directly in VS Code. Run queries, browse tables, and see results without leaving the editor.

## Settings Worth Changing

Open `settings.json` with `Cmd+Shift+P` → "Open User Settings (JSON)":

```json
{
  "editor.fontFamily": "JetBrains Mono, Menlo, monospace",
  "editor.fontSize": 14,
  "editor.lineHeight": 1.6,
  "editor.fontLigatures": true,

  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },

  "editor.tabSize": 4,
  "editor.insertSpaces": true,

  "editor.minimap.enabled": false,
  "editor.renderLineHighlight": "line",
  "editor.cursorBlinking": "smooth",
  "editor.smoothScrolling": true,

  "editor.suggestSelection": "first",
  "editor.acceptSuggestionOnCommitCharacter": false,

  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,

  "terminal.integrated.fontFamily": "JetBrains Mono",
  "terminal.integrated.fontSize": 13,

  "workbench.colorTheme": "GitHub Dark Default",
  "workbench.iconTheme": "material-icon-theme",
  "workbench.startupEditor": "none",

  "explorer.confirmDelete": false,
  "explorer.confirmDragAndDrop": false,

  "git.autofetch": true,
  "git.confirmSync": false,
  "gitlens.currentLine.enabled": true
}
```

A few of these deserve explanation:

- `acceptSuggestionOnCommitCharacter: false` — stops VS Code from auto-accepting a suggestion when you type `.` or `(`, which is jarring.
- `trimTrailingWhitespace` and `insertFinalNewline` — keeps diffs clean.
- `autofetch: true` — keeps the git status accurate without manual fetching.

## Keyboard Shortcuts Worth Memorizing

| Shortcut | Action |
|---|---|
| `Cmd+P` | Quick file open (fuzzy search by name) |
| `Cmd+Shift+P` | Command palette |
| `Cmd+T` | Go to symbol in workspace |
| `Cmd+Shift+F` | Search across all files |
| `Cmd+B` | Toggle sidebar |
| `Cmd+`` ` | Toggle integrated terminal |
| `Cmd+D` | Add next matching selection |
| `Cmd+Shift+L` | Select all occurrences of current selection |
| `F12` | Go to definition |
| `Alt+F12` | Peek definition (inline, without navigating) |
| `Shift+F12` | Find all references |
| `F2` | Rename symbol across all files |
| `Ctrl+G` | Go to line number |
| `Cmd+Shift+K` | Delete current line |
| `Alt+↑/↓` | Move line up/down |
| `Cmd+/` | Toggle line comment |

## Workspace Settings and `.vscode/`

Per-project settings live in `.vscode/settings.json`. Commit these to the repo so the whole team shares the same editor configuration:

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "editor.tabSize": 2,
  "[python]": {
    "editor.tabSize": 4
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/*.pyc": true
  }
}
```

Also useful: `.vscode/extensions.json` to recommend extensions to anyone who opens the project:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "humao.rest-client"
  ]
}
```

VS Code will prompt new contributors to install these when they open the workspace.

## Multi-root Workspaces

When working across multiple related repos (e.g., a backend API and a shared library), create a workspace file:

```json
// myproject.code-workspace
{
  "folders": [
    { "path": "./api", "name": "API" },
    { "path": "./shared-lib", "name": "Shared Library" },
    { "path": "./infra", "name": "Infrastructure" }
  ]
}
```

Open with `code myproject.code-workspace`. You get a single VS Code window with search, git, and the terminal spanning all repos.

## Conclusion

VS Code's value comes from configuration, not from using it out of the box. Format on save, inline errors with ErrorLens, inline blame with GitLens, and quick API testing with REST Client eliminate enough daily friction to be worth the setup time. Commit `.vscode/settings.json` and `.vscode/extensions.json` to every project — it's the cheapest way to enforce consistency across a team without a heavy tooling mandate.
