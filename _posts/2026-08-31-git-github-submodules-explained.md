---
layout: post
title: "Git & GitHub Submodules Explained: Basics, Use Cases, and Trade-offs"
date: "2026-08-31 00:00:00 +0530"
slug: git-github-submodules-explained
description: "A practical guide to Git submodules covering how they work, when to use them, the exact commands you need, and the pros and cons in real projects."
categories: ["Programming", "wiki"]
tags: ["git", "github", "submodules", "version control", "monorepo", "cheatsheet", "tutorial", "collaboration"]
---

You've got a shared library that two or three of your repositories depend on, and copy-pasting it around is starting to hurt — a bug fix in one place doesn't propagate anywhere else. Git submodules solve this by letting you embed one Git repository inside another while keeping their histories completely separate. They're one of the most misunderstood features in Git, mostly because the mental model — "a pointer to a specific commit, not a copy of the code" — isn't obvious from how the commands behave. This post covers what submodules actually are, when they're the right tool, the commands you'll use day to day, and the trade-offs that make people either love or hate them.

## What a Submodule Actually Is

A submodule is a reference in your repository to a specific commit in another repository. When you add a submodule, Git doesn't copy the files into your repo's history — it creates a `.gitmodules` file that records the submodule's URL and path, and it stores a special entry (called a **gitlink**) that points to one exact commit SHA in the other repo.

This means:

- The submodule's code lives in its own independent Git repository, with its own commit history.
- Your parent repo only tracks *which commit* of the submodule it currently points to — not the submodule's file contents directly.
- Updating the submodule's code doesn't happen automatically. You have to explicitly move the pointer forward.

Think of it less like "including a folder" and more like "pinning a dependency version," except the dependency is a full Git repository instead of a package.

```bash
$ cat .gitmodules
[submodule "libs/shared-utils"]
	path = libs/shared-utils
	url = https://github.com/mukulkadel/shared-utils.git
```

## Common Use Cases

- **Shared internal libraries.** A utility library, a design system, or a set of shared configs used across several independent repositories.
- **Vendoring third-party code.** Pulling in an exact version of a dependency's source when you need to patch it locally or the ecosystem has no package manager (common in C/C++ and some Arduino/embedded projects).
- **Separating concerns with different access control.** Keeping a public open-source component and a private application in separate repos with separate permissions, while still composing them into one build.
- **Documentation or theme repos.** Static site generators (Jekyll and Hugo themes, for example) are frequently distributed as submodules so a theme can be updated independently of the site content.
- **Multi-repo monorepo-adjacent setups.** Teams that don't want a full monorepo but still need certain repos to build together often reach for submodules as a middle ground.

If your dependency is versioned and published (an npm package, a Go module, a Python wheel), a real package manager is almost always a better fit than a submodule. Submodules earn their keep when there's no package registry involved, or when you need the *exact source*, not a built artifact.

## How to Use Submodules

### Adding a Submodule

```bash
$ git submodule add https://github.com/mukulkadel/shared-utils.git libs/shared-utils
Cloning into '/Users/mukulkadel/projects/app/libs/shared-utils'...
remote: Enumerating objects: 142, done.
remote: Total 142 (delta 0), reused 0 (delta 0)
Receiving objects: 100% (142/142), 38.21 KiB | 4.25 MiB/s, done.
Resolving deltas: 100% (61/61), done.
```

This clones the submodule into `libs/shared-utils`, writes an entry to `.gitmodules`, and stages both files for commit.

```bash
$ git status
On branch main
Changes to be committed:
	new file:   .gitmodules
	new file:   libs/shared-utils

$ git commit -m "Add shared-utils as a submodule"
```

### Cloning a Repo That Has Submodules

A plain `git clone` leaves submodule directories empty. You need one extra step:

```bash
$ git clone https://github.com/mukulkadel/app.git
$ cd app
$ git submodule update --init --recursive
```

Or clone and pull everything in one shot:

```bash
$ git clone --recurse-submodules https://github.com/mukulkadel/app.git
```

`--recursive` matters if the submodule itself has submodules — without it, only one level gets initialized.

### Updating a Submodule to a Newer Commit

```bash
$ cd libs/shared-utils
$ git fetch
$ git checkout main
$ git pull
$ cd ../..
$ git status
Changes not staged for commit:
	modified:   libs/shared-utils (new commits)

$ git add libs/shared-utils
$ git commit -m "Bump shared-utils to latest main"
```

The parent repo's diff for a submodule bump is just the pointer changing — one line, not the submodule's actual file diff:

```bash
$ git diff --cached
diff --git a/libs/shared-utils b/libs/shared-utils
index 3f2a1c9..7e8b0d4 160000
--- a/libs/shared-utils
+++ b/libs/shared-utils
@@ -1 +1 @@
-Subproject commit 3f2a1c9d8e2a1b7c6f4d9e0a1b2c3d4e5f6a7b8c
+Subproject commit 7e8b0d4a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e
```

To bump every submodule in the repo to the latest commit on their tracked branch at once:

```bash
$ git submodule update --remote --merge
```

### Pulling Changes When Others Have Bumped Submodules

If a teammate updated a submodule pointer and you pull their commit, your working copy of the submodule is still on the old commit until you sync it:

```bash
$ git pull
$ git submodule update --init --recursive
```

Forgetting this second command is the single most common submodule mistake — the pointer changed in `git log`, but your local files didn't move.

### Removing a Submodule

Removing one isn't a single command — it's three deliberate steps:

```bash
$ git submodule deinit -f libs/shared-utils
$ git rm -f libs/shared-utils
$ rm -rf .git/modules/libs/shared-utils
$ git commit -m "Remove shared-utils submodule"
```

## Pros

- **True separation of history.** Each repo's commit log stays clean and scoped to its own concern — no noise from an embedded dependency's commits.
- **Exact, reproducible pinning.** Every clone at a given commit gets the exact same submodule version, which is stronger reproducibility than a loosely-pinned package range.
- **Independent access control and lifecycle.** The submodule can have its own contributors, CI, issue tracker, and release cadence.
- **No build-artifact indirection.** You get the actual source, useful when you need to debug into or patch the dependency directly.
- **Works with any Git host.** No package registry, private npm/PyPI setup, or extra infrastructure required — it's plain Git.

## Cons

- **Easy to forget to update.** `git pull` on the parent repo does not update submodule contents. New contributors routinely end up building against stale or empty submodule directories.
- **Detached HEAD by default.** After `submodule update`, the submodule sits at a specific commit with no branch checked out. Committing inside it without first checking out a branch creates orphaned commits that are easy to lose.
- **Extra commands for common workflows.** Cloning, pulling, and switching branches all need submodule-aware variants (`--recurse-submodules`, `submodule update --init`). Scripts, CI configs, and onboarding docs all have to account for this.
- **Confusing diffs and merge conflicts.** A merge conflict on a submodule pointer shows two commit SHAs, not a readable code diff — you have to go into the submodule to understand what actually changed.
- **CI complexity.** Pipelines need explicit permissions to clone the submodule repo (a second set of credentials or deploy keys if it's private) and an explicit `--recurse-submodules` step, which is a common source of "works locally, fails in CI."
- **No partial checkout.** You get the whole submodule repo, even if you only need a handful of files from it.

## Gotchas and Non-Obvious Behavior

- **`git status` shows submodules as "modified" even without code changes.** If the submodule's checked-out commit differs from the pointer in the parent's index — often just because someone ran `git submodule update --remote` locally without committing — it'll show as dirty. Run `git diff` inside the submodule to see if it's a real change or just an unstaged pointer bump.
- **Branch tracking isn't automatic.** By default a submodule points at a commit, not a branch. Add `branch = main` under the entry in `.gitmodules` and use `git submodule update --remote` if you want it to follow a branch's tip.
- **`.gitignore` inside a submodule doesn't affect the parent repo**, and vice versa — they're fully independent Git repositories with independent ignore rules.
- **Deleting a submodule's folder isn't the same as removing the submodule.** `rm -rf libs/shared-utils` alone leaves stale entries in `.gitmodules`, `.git/config`, and `.git/modules`, causing confusing errors on the next `submodule update`. Always use `git submodule deinit` first.

## Alternatives Worth Knowing

- **`git subtree`** merges the dependency's files directly into your repo's history, no separate clone step, no detached HEAD — at the cost of a messier combined history and harder-to-isolate updates.
- **Package managers** (npm, pip, Go modules, Cargo) are the right call whenever the dependency is versioned and published; they handle transitive dependencies and semantic versioning, which submodules don't.
- **Monorepos** (with tools like Nx, Turborepo, or Bazel) avoid the cross-repo problem entirely by putting everything in one repository, trading repo-level isolation for build tooling complexity.

## Conclusion

Submodules are the right tool when you need an exact, independently-versioned Git repository embedded in another, and there's no package registry to lean on instead — shared internal libraries, vendored source, and theme repos are the classic cases. Their cost is real: they demand extra commands for cloning, pulling, and CI, and they punish teams that don't build the habit of running `git submodule update --init --recursive` after every pull. If your dependency is publishable, use a package manager. If you need genuine repo separation with exact pinning and you're willing to enforce the extra discipline, submodules do exactly what they promise.
