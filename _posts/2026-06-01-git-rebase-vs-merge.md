---
layout: post
title: "Git Rebase vs Merge: When to Use Which"
date: "2026-06-01 00:00:00 +0530"
slug: git-rebase-vs-merge
description: "Rebase and merge both integrate changes but produce different histories. Here's a clear explanation of how each works, when to use which, and what to avoid."
categories: ["wiki", "Programming"]
tags: ["git", "rebase", "merge", "version control", "branching", "history", "tutorial", "collaboration", "comparison"]
---

Rebase and merge are both ways to integrate changes from one branch into another, but they produce very different histories and carry different risks. Most developers use `git merge` by default without fully understanding what rebase does — and then hit confusing conflicts or rewrites of shared history that break their teammates' branches. Here's a clear breakdown of how each command works, when each is appropriate, and which patterns to avoid.

## How Merge Works

`git merge` takes two branch tips and creates a new **merge commit** that ties them together. The history retains both lines of development exactly as they happened.

```bash
$ git checkout main
$ git merge feature/auth
```

```
Before:
  main:    A - B - C
                    \
  feature:           D - E

After:
  main:    A - B - C - M   ← merge commit
                    \ /
  feature:           D - E
```

The merge commit `M` has two parents: `C` (the tip of main) and `E` (the tip of feature). The entire history of both branches is preserved.

```bash
$ git log --oneline --graph
*   3f2a1b4 Merge branch 'feature/auth'
|\
| * 9c8d6e2 Add token refresh logic
| * 4a1b3c5 Implement JWT validation
* | 2f9e8d1 Fix typo in README
* | 1c4b7a3 Update dependencies
|/
* 8a2c9f1 Initial commit
```

## How Rebase Works

`git rebase` replays your commits on top of another branch. Instead of creating a merge commit, it rewrites your commits so they appear as if they were made after the latest commit on the target branch.

```bash
$ git checkout feature/auth
$ git rebase main
```

```
Before:
  main:    A - B - C
                    \
  feature:           D - E

After:
  main:    A - B - C
                    \
  feature:           D' - E'   ← new commits (same changes, new hashes)
```

`D'` and `E'` have the same code changes as `D` and `E`, but they're new commits with new SHA hashes because their parent commit changed. The result looks like the feature was developed linearly after `C`.

```bash
$ git log --oneline --graph
* 7e3f1c2 Add token refresh logic
* 2d8b4a9 Implement JWT validation
* 2f9e8d1 Fix typo in README
* 1c4b7a3 Update dependencies
* 8a2c9f1 Initial commit
```

Clean, linear history — no merge commits.

## The Golden Rule of Rebase

**Never rebase commits that have been pushed to a shared branch.**

When you rebase, you rewrite commits (new SHAs). If someone else has based their work on the original commits, their branch now diverges from yours in a confusing way. They'll see their commits and your rebased commits as separate when they try to merge, resulting in duplicate commits and a history that's hard to untangle.

Safe to rebase:
- Your local feature branch before pushing
- Your feature branch after pushing, if you're the only one working on it and you force-push

Never rebase:
- `main`, `develop`, or any branch other people are actively working on
- A branch someone else has checked out

## Interactive Rebase: Cleaning Up Commits

`git rebase -i` (interactive) is one of the most powerful history-editing tools in git. It lets you squash, reorder, edit, and drop commits before merging.

```bash
$ git rebase -i HEAD~4   # edit the last 4 commits
```

This opens an editor listing the last 4 commits:

```
pick 9a1b2c3 WIP: add login form
pick 4d5e6f7 fix typo
pick 7g8h9i0 fix another typo
pick 1j2k3l4 Add JWT validation
```

Change `pick` to the action you want:

```
pick 9a1b2c3 WIP: add login form
squash 4d5e6f7 fix typo
squash 7g8h9i0 fix another typo
pick 1j2k3l4 Add JWT validation
```

Save and close. Git squashes the three "fix typo" commits into the first, prompting you to write a new combined commit message. You end up with two clean commits instead of four messy ones.

| Command | What it does |
|---|---|
| `pick` | Keep the commit as-is |
| `squash` / `s` | Merge into previous commit, combine messages |
| `fixup` / `f` | Merge into previous commit, discard this message |
| `reword` / `r` | Keep the commit, edit the message |
| `edit` / `e` | Pause to amend the commit |
| `drop` / `d` | Delete the commit entirely |

## Resolving Rebase Conflicts

Rebase replays commits one at a time, so you may hit conflicts at each step. The workflow:

```bash
$ git rebase main

Auto-merging api/auth.go
CONFLICT (content): Merge conflict in api/auth.go
error: could not apply 9c8d6e2... Implement JWT validation
hint: Resolve all conflicts manually, mark them as resolved with
hint: "git add/rm <conflicted_files>", then run "git rebase --continue".

$ # Fix conflicts in api/auth.go
$ git add api/auth.go
$ git rebase --continue

# If you want to abort and return to the original state:
$ git rebase --abort
```

With merge, you resolve conflicts once in the merge commit. With rebase, you may need to resolve conflicts for each commit being replayed, which can be more work for long-lived branches with many commits.

## When to Use Each

**Use merge when:**
- Integrating a completed feature branch into `main` or `develop` (the merge commit documents when the feature landed)
- Working with shared branches that others depend on
- You want to preserve the exact history of when things happened
- You're following Git Flow

**Use rebase when:**
- Updating your local feature branch with the latest changes from `main` before opening a PR — it avoids an unnecessary merge commit in the branch history
- Cleaning up messy commit history with `git rebase -i` before a PR review
- You want a linear history in your main branch

A common workflow that combines both:

```bash
# Update your feature branch with latest main (rebase)
$ git fetch origin
$ git rebase origin/main

# When merging the PR, use merge (preserves the fact it was a separate branch)
$ git checkout main
$ git merge --no-ff feature/auth
```

## `git pull --rebase`

By default, `git pull` creates a merge commit when your local branch diverges from the remote. This pollutes history with "Merge branch 'main' of github.com/..." commits that add no information.

```bash
$ git config --global pull.rebase true
```

With this set, `git pull` replays your local commits on top of the fetched commits instead of merging. For personal branches, this keeps the history clean without extra effort.

## Conclusion

Merge preserves history faithfully; rebase rewrites it to be linear. Use rebase to clean up your local work before sharing it, and use merge to integrate completed work into shared branches. The cardinal rule — never rebase shared history — prevents the confusing situations that give rebase a bad reputation. Once you understand the distinction, using both tools in the right contexts gives you the benefits of each: clean linear history where it helps readability, and honest merge commits where the integration point matters.
