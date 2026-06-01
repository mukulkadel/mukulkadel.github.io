---
layout: post
title: "iTerm2 + Zsh + Oh My Zsh: The Ultimate macOS Terminal Setup"
date: "2026-06-01 00:00:00 +0530"
slug: iterm2-zsh-oh-my-zsh-setup
description: "Set up a fast, beautiful, and productive terminal on macOS with iTerm2, Zsh, Oh My Zsh, and the plugins that actually save time. Step-by-step from scratch."
categories: ["Tutorials", "unix"]
tags: ["iterm2", "zsh", "oh my zsh", "macos", "terminal", "productivity", "shell", "plugins", "themes", "developer tools"]
---

macOS's default Terminal app is functional but bare — no split panes, no tab completion beyond the basics, no visual distinction between a command that succeeded and one that failed. The iTerm2 + Zsh + Oh My Zsh stack is the standard setup most macOS developers land on for good reason: it's fast, highly configurable, and a collection of plugins eliminate entire categories of friction. Here's how to set it up from scratch and which configuration choices actually matter.

## Step 1: Install iTerm2

```bash
$ brew install --cask iterm2
```

Open iTerm2 from `/Applications/iTerm2.app`. You can replace Terminal in your Dock.

### Key iTerm2 settings to configure first

**Appearance → Theme → Minimal** — removes the title bar clutter.

**Keys → Hotkey → Show/Hide with a system-wide hotkey** — set `Cmd+`` ` to toggle iTerm2 from anywhere. This is the single highest-ROI setting.

**Profiles → Default → Colors** — import a color scheme. Popular options:
- [Catppuccin](https://github.com/catppuccin/iterm) — soft pastels, easy on the eyes
- [Gruvbox](https://github.com/morhetz/gruvbox) — warm, earthy tones
- [Dracula](https://draculatheme.com/iterm) — dark purple, high contrast

Import via Profiles → Colors → Color Presets → Import.

**Profiles → Default → Text → Font** — set to JetBrains Mono (install via `brew install --cask font-jetbrains-mono`). Enable ligatures.

## Step 2: Zsh

Zsh has been the default shell on macOS since Catalina (10.15), so it's already installed. Confirm:

```bash
$ echo $SHELL
/bin/zsh

$ zsh --version
zsh 5.9 (x86_64-apple-darwin24.0)
```

If you're on an older system still using bash, switch:

```bash
$ chsh -s /bin/zsh
```

## Step 3: Install Oh My Zsh

Oh My Zsh is a framework that manages Zsh configuration, plugins, and themes. It installs into `~/.oh-my-zsh` and writes a starter `~/.zshrc`.

```bash
$ sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

```
  __                                     __
 / /  ___  ___  ___ ___  __ _  __ __   / /  ____
/ /__/ _ \/ _ \/ -_) _ \/  ' \/ // /  /_/  /_ /
/____/\___/_//_/\__/_//_/_/_/_/\_, /  (_)  /__/
                               /___/

...Oh My Zsh is now installed!
```

Restart your shell or run `source ~/.zshrc`.

## Step 4: Install Powerlevel10k (Theme)

Powerlevel10k is the most popular Zsh theme. It's fast (renders synchronously, no shell lag), shows git status, exit codes, execution time, and is fully configurable via a visual wizard.

```bash
$ brew install powerlevel10k
$ echo "source $(brew --prefix)/share/powerlevel10k/powerlevel10k.zsh-theme" >> ~/.zshrc
$ source ~/.zshrc
```

The configuration wizard launches automatically on first run. It asks about your font, prompt style, and which segments to show. Run `p10k configure` any time to restart it.

## Step 5: Essential Plugins

Oh My Zsh ships with plugins for most tools, but two critical ones need separate installation.

### zsh-autosuggestions

Shows a grey autocomplete based on your command history as you type. Press `→` to accept.

```bash
$ git clone https://github.com/zsh-users/zsh-autosuggestions \
    ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

### zsh-syntax-highlighting

Colors your commands as you type — green for valid commands, red for unrecognized ones. Catches typos before you hit enter.

```bash
$ git clone https://github.com/zsh-users/zsh-syntax-highlighting \
    ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

Now enable all your plugins in `~/.zshrc`:

```bash
plugins=(
  git
  docker
  docker-compose
  node
  npm
  python
  pip
  brew
  macos
  kubectl
  zsh-autosuggestions
  zsh-syntax-highlighting
)
```

`source ~/.zshrc` to reload.

## Step 6: fzf — Fuzzy History Search

`fzf` transforms `Ctrl+R` (history search) from a linear scroll into a fuzzy-matched interactive list. It also powers fuzzy file search and directory jumping.

```bash
$ brew install fzf
$ $(brew --prefix)/opt/fzf/install
```

Answer yes to all prompts. Now `Ctrl+R` opens an interactive history picker you can filter by typing.

## Step 7: Useful Aliases and Functions

Add these to `~/.zshrc`:

```bash
# Navigation
alias ..="cd .."
alias ...="cd ../.."
alias ll="ls -lAh"

# Git shortcuts (supplement Oh My Zsh's git plugin)
alias gs="git status"
alias gl="git log --oneline --graph --decorate -20"
alias gp="git push"

# Docker
alias dps="docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

# Safety nets
alias rm="rm -i"
alias cp="cp -i"
alias mv="mv -i"

# Show which process is using a port
port() { lsof -i ":$1" | grep LISTEN }

# Create and enter a directory in one command
mkcd() { mkdir -p "$1" && cd "$1" }
```

## Step 8: `.zshrc` Structure

A clean `~/.zshrc` after all this:

```bash
# Powerlevel10k instant prompt (must be near the top)
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"

plugins=(
  git docker node brew zsh-autosuggestions zsh-syntax-highlighting
)

source $ZSH/oh-my-zsh.sh

# Homebrew
eval "$(/opt/homebrew/bin/brew shellenv)"

# fzf
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# Aliases
alias ll="ls -lAh"
alias gs="git status"

# Powerlevel10k config
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
```

## iTerm2 Features Worth Knowing

**Split panes** — `Cmd+D` (vertical) and `Cmd+Shift+D` (horizontal). Navigate with `Cmd+Option+Arrow`.

**Search** — `Cmd+F` opens a search bar across the terminal buffer, including scrollback.

**Shell integration** — install via iTerm2 → Install Shell Integration. Enables jump-to-previous command mark, command timing, and the ability to right-click and open a file from its path in the terminal.

**Profiles** — create separate profiles for different projects (different colors, starting directories, environment variables). Switch with `Cmd+O`.

## Conclusion

iTerm2 + Powerlevel10k + zsh-autosuggestions + zsh-syntax-highlighting is the setup most experienced macOS developers converge on, and for good reason — each piece has a clear, discrete benefit. The hotkey toggle alone (`Cmd+`` `) is worth the setup time. Get the basics running, commit your `~/.zshrc` to a dotfiles repo, and then add plugins gradually as you notice friction points rather than installing everything at once.
