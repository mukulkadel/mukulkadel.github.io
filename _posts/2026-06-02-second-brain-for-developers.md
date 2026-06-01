---
layout: post
title: "Building a Second Brain as a Developer: Notes, References, and Recall"
date: "2026-06-02 00:00:00 +0530"
slug: second-brain-for-developers
description: "A second brain is a personal system for capturing and recalling the knowledge you need as a developer. Here's a practical approach that doesn't require perfect discipline."
categories: ["wiki"]
tags: ["second brain", "note-taking", "knowledge management", "obsidian", "zettelkasten", "productivity", "developer", "learning", "recall"]
---

Developers accumulate enormous amounts of knowledge — from deep dives into unfamiliar systems, from debugging sessions that took hours, from documentation they've read twice but will forget by next week. Most of this knowledge evaporates. You hit the same problem again six months later, vaguely remember solving it, and spend an hour rediscovering the answer you already found. A "second brain" is a personal knowledge system designed to prevent this: a place where knowledge you encounter gets captured in a form you can actually find and use later. The goal isn't to remember everything — it's to make retrieval fast enough that you don't waste time re-deriving things you've already figured out.

## What Actually Goes in a Second Brain

Not everything is worth capturing. The test: would you want to retrieve this in the future? A few categories that reliably have a high return:

**Solutions to non-obvious problems.** If you spent more than 20 minutes figuring something out, capture it. The specific error message, what you tried, and what actually fixed it. Future-you (or a teammate) will hit the same problem.

**Mental models and conceptual breakthroughs.** The moment something clicks — how PostgreSQL's MVCC works, what the difference between a process and a thread actually is at the OS level — write it down in your own words. Your explanation of your own understanding is more useful to future-you than the article that triggered the understanding.

**Configuration and setup steps.** Anything you had to figure out by trial and error: environment setup, deployment configuration, tricky library integrations. These are almost guaranteed to be needed again.

**Decision records.** Why did you choose library X over Y? Why is the schema structured the way it is? Why does this service have a queue in front of it? These decay fast from working memory but are invaluable when revisiting decisions.

**Useful commands and snippets.** The `jq` command that extracts a nested field from a response, the `psql` flags you always forget, the `git` incantation for a specific workflow.

## The Capture Habit

A second brain is only as useful as the consistency with which you add to it. The failure mode is capturing everything in a burst of enthusiasm and then abandoning it. The solution is making capture as low-friction as possible.

The practical rule: capture immediately, refine later. When you solve a hard problem, take 2 minutes to write a rough note before you close the terminal. Don't worry about organization. A messy note that exists is more valuable than a perfect note you planned to write.

Use whatever captures fastest in the moment:
- A scratch note in Obsidian, Bear, or Notion
- A comment at the top of a file in your dotfiles repo
- A `til/` (Today I Learned) directory in your personal notes git repo

The refining — organizing, linking, improving the explanation — happens in a separate pass, not at capture time.

## A Simple Structure That Works

You don't need a complex Zettelkasten hierarchy. A flat structure with good search covers 80% of use cases:

```
notes/
    til/              # Today I Learned — small, discrete facts
        2026-05-12-postgres-explain-buffers.md
        2026-05-20-git-filter-repo.md
    solutions/        # Solved problems — error + solution
        docker-networking-host-mode-macos.md
        python-ssl-certificate-verify-failed.md
    references/       # Cheat sheets, command collections
        git-commands.md
        jq-patterns.md
        postgres-useful-queries.md
    decisions/        # Architecture and tool decisions
        why-we-use-redis-for-sessions.md
        choosing-between-celery-and-arq.md
```

This structure is searchable by file path and contents. With `ripgrep` or Obsidian's search, you can find any note in under 5 seconds:

```bash
$ rg "certificate verify failed" ~/notes/
notes/solutions/python-ssl-certificate-verify-failed.md
3: ## Problem
4: requests.exceptions.SSLError: HTTPSConnectionPool ... certificate verify failed
```

## Tools

**Obsidian** is the most popular choice for developers. It's Markdown files stored locally (no vendor lock-in), has a powerful search and graph view, and supports bidirectional linking with `[[note-name]]` syntax. The local storage model means your notes are in git if you want them to be.

**A git repo with Markdown files** is the minimal viable system. No app required beyond a text editor. Use `rg` or `grep` to search. The advantage: it's already version-controlled, easily backed up, and renders on GitHub.

**Notion** works well for teams but has more friction for quick personal capture. The block editor is slower than Markdown for technical notes.

The tool matters less than the habit. Pick the one with the least friction in your specific workflow and stick with it.

## The TIL Format

"Today I Learned" is a useful atomic format for small, discrete facts. Each TIL is one thing: a surprising behavior, a useful flag, a non-obvious gotcha. Short, searchable, datestamped.

```markdown
# TIL: git log --follow tracks file renames

## Date
2026-05-12

## The thing
`git log filename.py` stops at the commit where the file was renamed.
`git log --follow filename.py` follows the rename history.

## Why it matters
Without --follow, `git log` on a refactored/renamed file shows only
changes after the rename, missing all the earlier history.

## Command
git log --follow -p path/to/file.py
```

A TIL should take under 3 minutes to write. If it's taking longer, you're over-engineering it.

## The Solutions Format

For debugging sessions and non-obvious fixes, a slightly more structured format pays off:

```markdown
# Docker containers can't reach each other on macOS in host networking mode

## Problem
`--network host` doesn't work on macOS Docker Desktop. Containers can't
bind to host ports or reach the host's localhost.

## Why
`--network host` only works on Linux. On macOS, Docker runs inside a VM,
so "host" means the VM's network, not the Mac's network.

## Solution
Use `host.docker.internal` to reach the Mac's localhost from a container:
    curl http://host.docker.internal:8080

Or use Docker Compose networking and reference services by name.

## Environment
Docker Desktop 4.x, macOS 14
```

The environment line is underrated. Many problems are version-specific. Knowing the context tells you whether a solution from two years ago still applies.

## Linking Notes Together

The real leverage of a second brain comes from linking related notes. When you write a note about PostgreSQL MVCC, link it to your note on vacuuming, which links to your note on table bloat. You're building a personal knowledge graph that reflects how *your* understanding is organized.

In Obsidian, this is `[[postgresql-vacuum]]`. In plain Markdown, it's a relative path link. Either way, following the links surfaces context you'd otherwise have to reconstruct from scratch.

## Reviewing and Maintaining

A second brain you never revisit is a filing cabinet. A few practices that keep it useful:

**Weekly review (5 minutes):** Look at notes from the past week. Refine the rough ones. Delete the ones that turned out to be dead ends.

**Before starting something familiar:** Search your notes before starting a setup you've done before. You probably documented it last time.

**When something takes longer than expected:** After you finally solve it, write the solution down. The frustration is a reliable signal that future-you will hit this again.

You don't need to review everything regularly — just don't let it grow into a write-only archive. The goal is a system you trust enough to actually use.

## Conclusion

A second brain doesn't require discipline or the perfect tool — it requires making capture fast enough that you actually do it. Start with a flat directory of Markdown files, write TILs when you learn something non-obvious, and write solution notes whenever you solve a hard problem. The return compounds over time: each note you retrieve instead of re-deriving is time saved, and the habit of capturing makes you a more deliberate learner. The best system is the simplest one you'll actually maintain.
