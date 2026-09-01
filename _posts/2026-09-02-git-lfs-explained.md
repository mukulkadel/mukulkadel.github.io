---
layout: post
title: "Git LFS Explained: Basics, Use Cases, and Trade-offs"
date: "2026-09-02 00:00:00 +0530"
slug: git-lfs-explained
description: "A practical guide to Git LFS covering how it works, when to use it, the exact commands you need, and the pros and cons of storing large files in Git."
categories: ["Programming", "wiki"]
tags: ["git", "github", "git-lfs", "version control", "large files", "cheatsheet", "tutorial", "binary files"]
---

You've committed a few PSD files, a video, or a trained model checkpoint into a Git repo, and now every clone takes minutes instead of seconds because Git is dragging every historical version of those binaries along with it. Git wasn't built for large binary files — it stores full snapshots and diffs text well, but a 200MB video has no meaningful diff, so every version bloats the repo permanently. Git LFS (Large File Storage) fixes this by replacing large files in your repo with small text pointers, while storing the actual file content on a separate server. This post covers what LFS actually does, when it's worth adopting, the commands you'll use, and the trade-offs that come with it.

## What Git LFS Actually Is

Git LFS is a Git extension that intercepts specific files (matched by pattern, like `*.psd` or `*.mp4`) before they're committed. Instead of storing the file's contents directly in your Git history, it:

1. Uploads the actual file content to a separate LFS storage server (GitHub, GitLab, and Bitbucket all host one alongside your repo).
2. Commits a small **pointer file** — plain text, a few lines — in place of the binary, into your normal Git history.
3. Downloads the real content on demand when you check out a commit, via a `smudge` filter.

```bash
$ cat assets/hero-video.mp4
version https://git-lfs.github.com/spec/v1
oid sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a1
size 214748364
```

That's what's actually stored in Git's history — 130 bytes, regardless of how large the real file is. The clone stays small, and `git log` on that file diffs a text pointer, not a multi-hundred-megabyte binary blob, every single version.

This means:

- Your repo's `.git` history stays lightweight even as binary assets grow and change over time.
- The real file content lives outside normal Git objects, fetched separately by the LFS client.
- Old versions of large files are still fully recoverable — LFS keeps every version on the storage server, it just doesn't bloat the Git object database to do it.

## Common Use Cases

- **Game development.** Textures, audio, 3D models, and level data — binary assets that change often and can be huge, common in Unity and Unreal projects.
- **Design and media assets.** PSD/AI/Sketch files, video, and high-res images checked into a repo alongside a website or app.
- **ML model artifacts.** Trained model weights or checkpoints that need to be versioned alongside the code that produced them.
- **Datasets.** CSV/Parquet/binary data files that a team wants versioned with the same workflow as code, without wrecking clone times.
- **Any repo where a `.gitignore`'d "drop the binary somewhere else" convention keeps breaking.** LFS keeps the asset in the same repo, same PR review flow, same commit history as the code that depends on it.

If your large files rarely change (a one-time logo, a static PDF), plain Git is usually fine — LFS earns its keep when large files change *repeatedly* over the project's life, since that's what causes unbounded repo growth.

## How to Use Git LFS

### Installing and Initializing

```bash
$ brew install git-lfs
$ git lfs install
Updated Git hooks.
Git LFS initialized.
```

`git lfs install` only needs to run once per machine — it sets up the smudge/clean filters in your global Git config.

### Tracking File Patterns

```bash
$ git lfs track "*.psd"
Tracking "*.psd"

$ git lfs track "assets/videos/*.mp4"
Tracking "assets/videos/*.mp4"

$ cat .gitattributes
*.psd filter=lfs diff=lfs merge=lfs -text
assets/videos/*.mp4 filter=lfs diff=lfs merge=lfs -text
```

`git lfs track` writes rules to `.gitattributes`, which must itself be committed — it's what tells collaborators (and GitHub) which files are LFS-managed.

```bash
$ git add .gitattributes
$ git commit -m "Track PSD and video files with Git LFS"
```

### Adding and Committing Large Files

From here it looks like normal Git — `add`, `commit`, `push` behave the same way, the interception happens transparently:

```bash
$ git add assets/hero-video.mp4
$ git commit -m "Add hero video asset"
$ git push origin main
Uploading LFS objects: 100% (1/1), 205 MB | 8.2 MB/s, done.
To github.com:mukulkadel/app.git
   3a9f2e1..7e8b0d4  main -> main
```

### Cloning a Repo That Uses LFS

```bash
$ git clone https://github.com/mukulkadel/app.git
$ cd app
$ git lfs pull
```

If `git lfs install` has already run once on the machine, a plain `git clone` will actually fetch LFS content automatically as part of checkout — `git lfs pull` is mainly needed when you want to (re)fetch content for an existing checkout, or after switching branches.

To clone without downloading LFS content (useful in CI when you only need the code, not the assets):

```bash
$ GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/mukulkadel/app.git
$ cd app
$ git lfs pull --include="assets/hero-video.mp4"
```

### Checking What's Tracked

```bash
$ git lfs ls-files
7e8b0d4a1b * assets/hero-video.mp4
3f2a1c9d8e * assets/logo.psd
```

```bash
$ git lfs status
On branch main
Git LFS objects to be pushed to origin/main:

	assets/hero-video.mp4 (LFS: 7e8b0d4)
```

### Migrating Existing Files Into LFS

If binaries were already committed to Git history before you adopted LFS, adding a `.gitattributes` rule going forward won't shrink the existing history. Use the migrate command to rewrite history:

```bash
$ git lfs migrate import --include="*.psd,*.mp4" --everything
migrate: Sorting commits: ..., done
migrate: Rewriting commits: 100% (48/48), done
  main	7e8b0d4a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e
migrate: Updating refs: ..., done
```

This rewrites every historical commit that touched those file patterns, which changes commit SHAs — treat it like any other history rewrite: coordinate with the team, and expect everyone to re-clone or hard-reset their local branches.

## Pros

- **Fast clones regardless of binary history.** New clones only fetch the LFS content actually needed for the checked-out revision, not every historical version.
- **Full version history is preserved.** Unlike `.gitignore`-and-share-elsewhere workarounds, every version of a large file stays recoverable through normal Git commands.
- **Transparent day-to-day workflow.** Once patterns are tracked, `add`/`commit`/`push`/`pull` work exactly like normal Git — no separate tool to learn for daily use.
- **Native GitHub/GitLab/Bitbucket support.** No extra infrastructure to stand up; the hosting platform runs the LFS storage server.
- **Selective fetching.** `git lfs pull --include`/`--exclude` let you skip downloading assets you don't need, which plain Git can't do at all.

## Cons

- **Storage and bandwidth quotas cost money.** GitHub's free tier includes a modest LFS storage and bandwidth allowance; teams with large media libraries hit paid tiers quickly.
- **History rewrites are required to fix past mistakes.** If binaries were committed before LFS was adopted, cleaning up history means `git lfs migrate` and forced re-clones for the whole team — not a casual operation.
- **Extra failure mode: "smudge" errors.** If the LFS server is unreachable, or a contributor doesn't have `git lfs install` set up, files silently check out as pointer text instead of real content — confusing until you recognize the symptom.
- **Not automatically transitive.** If a submodule or a forked/mirrored copy of the repo doesn't have LFS configured, its checkouts get pointer files instead of binaries.
- **CI needs explicit LFS awareness.** Pipelines must fetch LFS objects explicitly (`git lfs pull` or `lfs: true` in CI config); otherwise builds run against tiny pointer text files and fail in non-obvious ways.
- **Deleting LFS objects is not automatic.** Removing a file from the latest commit doesn't remove its historical LFS objects from storage — that requires `git lfs prune` locally and server-side garbage collection, which most hosts run on a delay.

## Gotchas and Non-Obvious Behavior

- **A pointer file committed without LFS installed looks like a real commit — until someone checks it out.** If `.gitattributes` exists but a contributor never ran `git lfs install`, `git add` on a tracked file commits the *raw binary* instead of a pointer, silently defeating the whole setup. Always confirm `git lfs install` ran before the first LFS commit on a new machine.
- **`git lfs prune` deletes local LFS cache, not remote storage.** It's a local disk-space cleanup command; managing remote storage usage is a hosting-platform-side operation (GitHub's LFS storage settings, for example).
- **Diffing LFS files doesn't show content by default.** `git diff` on a tracked binary shows the pointer's OID changing, not a meaningful diff of the asset — `git lfs diff` behaves differently depending on the file type and often can't show a real diff at all for binaries.
- **Forking a repo with LFS content can hit separate quotas.** On GitHub, LFS bandwidth usage is billed to the account whose LFS storage serves the request, so forks of LFS-heavy repos can quietly rack up usage.

## Alternatives Worth Knowing

- **`git-annex`** solves the same core problem with a more flexible, decentralized storage backend (supports many remotes, not just one LFS server), at the cost of a steeper learning curve.
- **Cloud storage + manifest file.** Some teams skip LFS entirely and store large assets in S3/GCS, checking in only a manifest of URLs and hashes — full control over storage cost, but no unified Git history or diffing for the assets.
- **DVC (Data Version Control).** Built specifically for ML datasets and models, layering versioning and pipeline tracking on top of Git, with pluggable remote storage (S3, GCS, Azure) — a better fit than plain LFS if you also need dataset/model pipeline tracking, not just storage.

## Conclusion

Git LFS is the right tool when large binary files need to live in the same repo and review workflow as your code, and those files change often enough that plain Git's full-history storage becomes a real cost — game assets, design files, and versioned model artifacts are the classic cases. The trade-off is real: storage quotas, an extra install step for every contributor, and CI configuration that has to explicitly account for it. If your large files are static and rarely change, plain Git is simpler. If they change repeatedly and need full version history without wrecking clone times, LFS does exactly what it promises.
