---
layout: post
title: "tmux — Terminal Multiplexer Setup and Workflow"
date: "2026-05-23 00:00:00 +0530"
slug: tmux-terminal-multiplexer-guide
description: "Learn tmux from scratch: sessions, windows, panes, keybindings, and a practical workflow for remote development and long-running processes."
categories: ["Tutorials", "unix"]
tags: ["tmux", "terminal", "unix", "linux", "macos", "multiplexer", "productivity", "ssh", "workflow"]
---

If you've ever SSHed into a server, started a long-running process, and then lost your connection — you already know why `tmux` exists. It's a terminal multiplexer: it lets you run multiple terminal sessions inside a single connection, detach from them, come back later, and pick up exactly where you left off. Once it's in your workflow, working without it feels broken.

## Installing tmux

On macOS:

```bash
$ brew install tmux
```

On Debian/Ubuntu:

```bash
$ sudo apt-get install tmux
```

Check the version — anything 3.x is solid:

```bash
$ tmux -V
tmux 3.4
```

## Core Concepts

`tmux` has three layers of hierarchy:

- **Session** — a collection of windows. You can detach from a session and it keeps running.
- **Window** — like a tab. One session holds multiple windows.
- **Pane** — a split inside a window. One window holds multiple panes.

The **prefix key** is the gateway to all `tmux` commands. The default is `Ctrl-b`. Every shortcut below assumes you press `Ctrl-b` first, then the listed key.

## Starting and Managing Sessions

Start a new unnamed session:

```bash
$ tmux
```

Start a named session (recommended — easier to reattach later):

```bash
$ tmux new -s work
```

List running sessions:

```bash
$ tmux ls
work: 2 windows (created Sat May 23 10:00:00 2026) [220x50]
```

Detach from the current session (leaves it running in the background):

```
Ctrl-b d
```

Reattach to a named session:

```bash
$ tmux attach -t work
```

Kill a session:

```bash
$ tmux kill-session -t work
```

## Windows (Tabs)

| Shortcut | Action |
|---|---|
| `Ctrl-b c` | Create a new window |
| `Ctrl-b ,` | Rename the current window |
| `Ctrl-b n` | Next window |
| `Ctrl-b p` | Previous window |
| `Ctrl-b 0`–`9` | Switch to window by number |
| `Ctrl-b w` | Interactive window list |
| `Ctrl-b &` | Kill the current window (prompts for confirmation) |

A good naming habit: rename windows to reflect what's running in them (`server`, `logs`, `db`, etc.). The status bar at the bottom shows all windows at a glance.

## Panes (Splits)

| Shortcut | Action |
|---|---|
| `Ctrl-b %` | Split vertically (left/right) |
| `Ctrl-b "` | Split horizontally (top/bottom) |
| `Ctrl-b Arrow` | Move between panes |
| `Ctrl-b z` | Zoom/unzoom the current pane (full-screen toggle) |
| `Ctrl-b x` | Kill the current pane |
| `Ctrl-b q` | Show pane numbers briefly |
| `Ctrl-b {` / `}` | Swap pane position with the previous/next |
| `Ctrl-b Ctrl-Arrow` | Resize pane by one cell |

A typical layout for local development: one pane running your dev server, one for your editor, one for a shell. Zoom in on whichever you need at the moment.

## Copy Mode

`tmux` has a built-in scroll buffer and copy mode. Enter it with:

```
Ctrl-b [
```

Once in copy mode:

- Arrow keys (or vi keys if configured) move the cursor
- `/` searches forward, `?` searches backward
- `Space` starts a selection, `Enter` copies it
- `q` exits copy mode

Paste the copied text with `Ctrl-b ]`.

## Customizing with `~/.tmux.conf`

The default keybindings aren't ideal. A minimal `~/.tmux.conf` that most people settle on:

```bash
# Remap prefix from Ctrl-b to Ctrl-a (screen-style)
unbind C-b
set-option -g prefix C-a
bind-key C-a send-prefix

# Split panes with | and -
bind | split-window -h
bind - split-window -v
unbind '"'
unbind %

# Vim-style pane navigation
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# Reload config in place
bind r source-file ~/.tmux.conf \; display "Config reloaded!"

# Enable mouse support
set -g mouse on

# Increase scrollback buffer
set -g history-limit 10000

# Start window numbering at 1
set -g base-index 1
setw -g pane-base-index 1

# True color support
set-option -g default-terminal "screen-256color"
set-option -sa terminal-overrides ",xterm-256color:RGB"
```

After editing, reload without restarting:

```
Ctrl-b r    (or Ctrl-a r if you remapped the prefix)
```

## Practical Workflows

### Remote dev with persistent sessions

SSH to a server, create a named session, start your work:

```bash
$ ssh user@myserver.com
$ tmux new -s deploy
# run your build, migration, whatever
$ Ctrl-a d   # detach
$ exit       # close SSH
```

Later, SSH back and reattach:

```bash
$ ssh user@myserver.com
$ tmux attach -t deploy
```

The session survived your disconnection — everything is exactly as you left it.

### Multiple services at a glance

```bash
$ tmux new -s dev
# in pane 1: run the API
$ npm run dev

# split and run the database
$ Ctrl-a |
$ docker compose up postgres

# split again for a shell
$ Ctrl-a -
```

Zoom into any pane with `Ctrl-a z` when you need to focus.

### Scripting session layouts

For a reproducible dev environment, start `tmux` with a shell script:

```bash
#!/bin/bash
tmux new-session -d -s dev -n editor
tmux send-keys -t dev:editor 'nvim .' C-m

tmux new-window -t dev -n server
tmux send-keys -t dev:server 'npm run dev' C-m

tmux new-window -t dev -n logs
tmux send-keys -t dev:logs 'tail -f /var/log/app.log' C-m

tmux select-window -t dev:editor
tmux attach-session -t dev
```

Run this script instead of `tmux` and you get a fully configured session in one command.

## tmux Cheat Sheet

| Action | Command |
|---|---|
| New session | `tmux new -s name` |
| Attach session | `tmux attach -t name` |
| List sessions | `tmux ls` |
| Kill session | `tmux kill-session -t name` |
| Detach | `Ctrl-b d` |
| New window | `Ctrl-b c` |
| Rename window | `Ctrl-b ,` |
| Next/prev window | `Ctrl-b n` / `Ctrl-b p` |
| Split vertical | `Ctrl-b %` |
| Split horizontal | `Ctrl-b "` |
| Navigate panes | `Ctrl-b Arrow` |
| Zoom pane | `Ctrl-b z` |
| Copy mode | `Ctrl-b [` |
| Paste | `Ctrl-b ]` |
| Reload config | `Ctrl-b r` (if bound) |

## Conclusion

`tmux` is the difference between a fragile terminal workflow and a resilient one. The key insight is that sessions outlive your SSH connection or terminal window — your work keeps running whether you're there or not. Start by learning sessions and detach/attach, then gradually adopt windows and panes as your workflow grows. The `~/.tmux.conf` customization above covers 90% of what most developers need, and you can always extend it later.
