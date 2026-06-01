---
layout: post
title: "macOS Keyboard Shortcuts Every Developer Should Know"
date: "2026-06-01 00:00:00 +0530"
slug: macos-keyboard-shortcuts-developers
description: "A practical cheat sheet of macOS keyboard shortcuts that save developers time every day — from Finder and terminal to text editing and window management."
categories: ["wiki"]
tags: ["macos", "keyboard shortcuts", "productivity", "terminal", "developer tools", "cheatsheet", "apple", "workflow"]
---

The mouse is slow. Every time your hand leaves the keyboard to click something, you lose a second or two — and those seconds add up. macOS has a deep set of keyboard shortcuts that most developers use only a fraction of, often because they were never laid out in one place. This cheat sheet focuses on what's actually useful in a development context: text editing, window management, terminal, Finder, and the system shortcuts that replace common mouse clicks.

## System-Wide Shortcuts

These work across virtually every macOS application.

| Shortcut | Action |
|---|---|
| `Cmd+Space` | Spotlight search — launch apps, convert units, do math |
| `Cmd+Tab` | Switch between open apps |
| `Cmd+`` ` | Switch between windows of the current app |
| `Cmd+Q` | Quit the current app |
| `Cmd+W` | Close the current tab or window |
| `Cmd+H` | Hide the current app |
| `Cmd+M` | Minimize the current window |
| `Cmd+,` | Open preferences/settings for the current app |
| `Cmd+Z` | Undo |
| `Cmd+Shift+Z` | Redo |
| `Cmd+C / Cmd+V / Cmd+X` | Copy / Paste / Cut |
| `Cmd+A` | Select all |
| `Cmd+F` | Find |
| `Cmd+S` | Save |
| `Cmd+P` | Print (or in VS Code: quick open) |

## Text Editing

These work in every native text field — Terminal, browser address bar, editor, Slack, email.

| Shortcut | Action |
|---|---|
| `Ctrl+A` | Jump to beginning of line |
| `Ctrl+E` | Jump to end of line |
| `Ctrl+K` | Delete from cursor to end of line |
| `Ctrl+U` | Delete from cursor to beginning of line |
| `Ctrl+W` | Delete the word before the cursor |
| `Ctrl+F / Ctrl+B` | Move forward / backward one character |
| `Option+→ / Option+←` | Jump forward / backward one word |
| `Cmd+→ / Cmd+←` | Jump to end / beginning of line |
| `Cmd+↑ / Cmd+↓` | Jump to top / bottom of document |
| `Shift+Option+→` | Select next word |
| `Shift+Cmd+→` | Select to end of line |
| `Fn+Delete` | Forward delete (delete character to the right) |
| `Option+Delete` | Delete word to the left of cursor |

The `Ctrl+A`, `Ctrl+E`, `Ctrl+K` trio is particularly useful in the terminal — they come from readline and work in bash, zsh, and most REPLs.

## Terminal Shortcuts

These apply to the terminal application itself (iTerm2 or Terminal.app), separate from shell-level shortcuts.

| Shortcut | Action |
|---|---|
| `Cmd+T` | New tab |
| `Cmd+N` | New window |
| `Cmd+D` | Split pane vertically (iTerm2) |
| `Cmd+Shift+D` | Split pane horizontally (iTerm2) |
| `Cmd+Option+Arrow` | Navigate between panes (iTerm2) |
| `Cmd+[1–9]` | Switch to tab by number |
| `Cmd+K` | Clear scrollback buffer |
| `Cmd+F` | Search terminal buffer |
| `Ctrl+C` | Interrupt / kill current process |
| `Ctrl+Z` | Suspend current process (resume with `fg`) |
| `Ctrl+D` | Send EOF / exit current shell |
| `Ctrl+L` | Clear screen (keeps scrollback) |
| `Ctrl+R` | Search command history interactively |
| `!!` | Repeat last command |
| `!$` | Last argument of previous command |

## Finder Shortcuts

| Shortcut | Action |
|---|---|
| `Cmd+Shift+G` | Go to folder (type any path, supports tab completion) |
| `Cmd+Shift+H` | Go to home directory |
| `Cmd+Shift+D` | Go to Desktop |
| `Cmd+Shift+F` | Go to Recents |
| `Cmd+Option+L` | Go to Downloads |
| `Cmd+I` | Get Info on selected file |
| `Cmd+Delete` | Move selected file to Trash |
| `Cmd+Shift+Delete` | Empty Trash |
| `Space` | Quick Look preview (works on images, PDFs, videos) |
| `Cmd+Shift+.` | Show/hide hidden files (dotfiles) |
| `Return` | Rename selected file |

`Cmd+Shift+.` is the one most developers don't know: it toggles visibility of dotfiles like `.zshrc`, `.env`, and `.git` directories right in Finder.

## Screenshot Shortcuts

| Shortcut | Action |
|---|---|
| `Cmd+Shift+3` | Screenshot entire screen (saved to Desktop) |
| `Cmd+Shift+4` | Screenshot selection (drag to select area) |
| `Cmd+Shift+4` then `Space` | Screenshot a specific window |
| `Cmd+Shift+5` | Screenshot toolbar with all options |
| `Cmd+Ctrl+Shift+3` | Screenshot entire screen to clipboard |
| `Cmd+Ctrl+Shift+4` | Screenshot selection to clipboard |

Adding `Ctrl` to any screenshot shortcut copies to clipboard instead of saving to disk — useful when you want to paste directly into Slack or an issue.

## Window Management

macOS's native window management is basic, but these help. Install [Rectangle](https://rectangleapp.com/) (`brew install --cask rectangle`) for tiling shortcuts.

| Shortcut | Action |
|---|---|
| `Cmd+Option+H` | Hide all other apps (focus current) |
| `Ctrl+↑` | Mission Control (all open windows) |
| `Ctrl+↓` | Show all windows of current app |
| `Ctrl+→ / Ctrl+←` | Switch between Spaces (virtual desktops) |
| `Ctrl+1`, `Ctrl+2` ... | Jump to a specific Space |
| `F11` | Show Desktop (hide all windows) |

**Rectangle shortcuts** (after install):

| Shortcut | Action |
|---|---|
| `Ctrl+Option+←` | Left half |
| `Ctrl+Option+→` | Right half |
| `Ctrl+Option+↑` | Top half |
| `Ctrl+Option+↓` | Bottom half |
| `Ctrl+Option+Enter` | Maximize |
| `Ctrl+Option+C` | Center window |
| `Ctrl+Option+U/I/J/K` | Quarter corners |

## Spotlight as a Calculator and Unit Converter

Spotlight (`Cmd+Space`) doubles as a quick calculator and converter — no app needed:

```
143 * 24          → 3432
sqrt(144)         → 12
100 USD in INR    → ₹8,340.00
10 km in miles    → 6.21 miles
500 MB in GB      → 0.49 GB
```

## Conclusion

Most of these shortcuts take a few days of deliberate use to become muscle memory — don't try to learn all of them at once. Start with the text editing row (`Ctrl+A`, `Ctrl+E`, `Ctrl+K`, `Option+Delete`) since they work everywhere, then add the Finder dotfile toggle (`Cmd+Shift+.`) and the clipboard screenshot shortcut (`Cmd+Ctrl+Shift+4`). Those five alone will save noticeable time within a week.
