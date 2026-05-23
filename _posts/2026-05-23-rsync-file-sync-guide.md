---
layout: post
title: "rsync — Syncing Files Like a Pro"
date: "2026-05-23 00:00:00 +0530"
slug: rsync-file-sync-guide
description: "A practical rsync guide covering flags, incremental transfers, remote syncing over SSH, excludes, dry runs, and real backup workflows."
categories: ["Tutorials", "unix"]
tags: ["rsync", "unix", "linux", "file sync", "backup", "command line", "scp", "terminal", "devops"]
---

`rsync` is the right tool any time you need to copy files efficiently — locally or over a network. Unlike `cp` or `scp`, it only transfers the parts of files that changed, compresses data in transit, and can resume interrupted transfers. Once you understand a handful of flags, it replaces a surprising number of ad-hoc backup scripts.

## Basic Syntax

```
rsync [options] source destination
```

A simple local copy (mirrors `cp -r`):

```bash
$ rsync -a ~/projects/myapp/ /backup/myapp/
```

The trailing slash on the source is significant:

- `source/` — copy the *contents* of `source` into the destination
- `source` (no slash) — copy the `source` directory itself into the destination

```bash
$ rsync -a ~/photos/ /backup/photos/
# Result: /backup/photos/img001.jpg, /backup/photos/img002.jpg ...

$ rsync -a ~/photos /backup/
# Result: /backup/photos/img001.jpg, /backup/photos/img002.jpg ...
```

Both produce the same final structure here, but the distinction matters when the destination already has other files in it.

## Essential Flags

| Flag | Meaning |
|---|---|
| `-a` | Archive mode: preserves permissions, timestamps, symlinks, owner, group. Equivalent to `-rlptgoD`. |
| `-v` | Verbose: show which files are being transferred |
| `-z` | Compress data during transfer (useful over slow networks) |
| `-P` | Combines `--progress` and `--partial` — shows progress and resumes partial transfers |
| `-n` or `--dry-run` | Simulate without making changes |
| `--delete` | Delete files in the destination that no longer exist in the source |
| `--exclude` | Skip files matching a pattern |
| `--include` | Include files matching a pattern (overrides excludes) |
| `-h` | Human-readable output sizes |
| `--checksum` | Compare by checksum instead of timestamp+size (slower but more accurate) |

The most common combination for a reliable sync:

```bash
$ rsync -avz --progress source/ destination/
```

## Remote Transfers Over SSH

Add a remote host with the same colon syntax as `scp`:

**Local → Remote:**

```bash
$ rsync -avz -P ~/myapp/ user@server.example.com:/var/www/myapp/
sending incremental file list
index.html
assets/css/main.css

sent 45,231 bytes  received 86 bytes  18,126.80 bytes/sec
total size is 1,234,567  speedup is 27.27
```

**Remote → Local:**

```bash
$ rsync -avz user@server.example.com:/var/log/nginx/ ~/logs/nginx/
```

To use a non-standard SSH port or a specific key:

```bash
$ rsync -avz -e "ssh -p 2222 -i ~/.ssh/prod_key" ~/app/ user@server:/opt/app/
```

## Always Dry-Run First

Before any destructive sync (especially with `--delete`), do a dry run:

```bash
$ rsync -avz --delete --dry-run ~/photos/ /backup/photos/
deleting 2023/old-vacation.jpg
./
2024/trip001.jpg

(dry run) sent 1,234 bytes  received 56 bytes
```

The output shows exactly what *would* happen — nothing is actually changed.

## Excluding Files and Directories

```bash
$ rsync -avz --exclude='*.log' --exclude='.git/' ~/project/ /backup/project/
```

For a long exclude list, put patterns in a file:

```bash
$ cat .rsync-exclude
.git/
node_modules/
__pycache__/
*.pyc
.DS_Store
*.log
dist/

$ rsync -avz --exclude-from='.rsync-exclude' ~/project/ /backup/project/
```

Includes and excludes are evaluated in order — the first match wins. To sync only `.py` files from a directory:

```bash
$ rsync -avz --include='*.py' --exclude='*' src/ backup/
```

## Mirroring with `--delete`

`--delete` makes the destination an exact mirror of the source by removing files that were deleted from the source:

```bash
$ rsync -avz --delete ~/docs/ /backup/docs/
deleting old-report.pdf
sending incremental file list
new-report.pdf

sent 234,567 bytes  received 1,234 bytes
```

Use this carefully — combined with `--dry-run`, it's safe; without it, files vanish from the destination permanently.

## Incremental Backups with `--link-dest`

`--link-dest` creates a new backup directory but hard-links files that haven't changed from the previous backup. This gives you full snapshot history with minimal disk space:

```bash
$ DATE=$(date +%Y-%m-%d)
$ rsync -avz --link-dest=/backup/latest ~/data/ /backup/$DATE/
$ ln -sfn /backup/$DATE /backup/latest
```

Each dated directory looks like a full copy, but unchanged files are just hard links — no extra space consumed. This is the core of many professional backup strategies.

## Bandwidth Limiting

On a shared connection, cap the transfer rate to avoid saturating the network:

```bash
$ rsync -avz --bwlimit=5000 ~/data/ user@server:/backup/
```

The limit is in KB/s — `5000` means 5 MB/s.

## Common Real-World Patterns

**Deploy a website to a server:**

```bash
$ rsync -avz --delete \
  --exclude='.git/' \
  --exclude='node_modules/' \
  _site/ user@server:/var/www/mysite/
```

**Backup home directory to an external drive:**

```bash
$ rsync -avz --delete \
  --exclude-from="$HOME/.rsync-exclude" \
  $HOME/ /Volumes/Backup/home/
```

**Mirror an S3 bucket locally** (via AWS CLI, not `rsync`, but worth knowing the alternative exists):

```bash
$ aws s3 sync s3://my-bucket ./local-copy/
```

**Transfer large files with resume support:**

```bash
$ rsync -avz -P largefile.iso user@server:/downloads/
```

If the connection drops, run the same command again — `rsync` picks up where it left off.

## rsync vs scp

| | `rsync` | `scp` |
|---|---|---|
| Incremental transfer | Yes | No |
| Resume on failure | Yes (`-P`) | No |
| Compression | Yes (`-z`) | Yes (`-C`) |
| Exclude patterns | Yes | No |
| Mirror with delete | Yes | No |
| Simpler syntax | No | Yes |

Use `scp` when you need to copy a single file quickly. Use `rsync` for everything else.

## Conclusion

The three flags to internalize are `-avz` (archive, verbose, compress), `--delete` (mirror the source), and `--dry-run` (preview before acting). Everything else — excludes, `--link-dest`, bandwidth limiting — is layered on top of those fundamentals. Once you're comfortable with `rsync`, it becomes the default tool for any "move or sync files" task, whether it's a one-off deployment or a nightly backup cron job.
