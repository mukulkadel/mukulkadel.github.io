---
layout: post
title: "`find` — Advanced File Search with Real Examples"
date: "2026-05-23 00:00:00 +0530"
slug: find-command-advanced-guide
description: "Master the Unix find command with real examples covering name, size, time, permissions, and exec — the most powerful file search tool in your terminal."
categories: ["wiki", "unix"]
tags: ["find", "unix", "linux", "command line", "file search", "terminal", "cheatsheet", "sysadmin", "xargs"]
---

The `find` command is one of the most powerful tools in the Unix toolkit — and one of the most underused. Most developers reach for it when they want to locate a file by name, but `find` can filter by size, age, permissions, and file type, and it can pipe results directly into other commands. Once you get comfortable with it, you'll find yourself replacing a lot of ad-hoc scripting with a single well-crafted `find` invocation.

## Basic Syntax

```bash
find [path] [expression]
```

The path is where to start searching (recursively). The expression is a combination of tests and actions.

```bash
$ find . -name "*.log"
./app/logs/access.log
./app/logs/error.log
```

Start with `.` to search the current directory tree, or give an absolute path like `/var/log`.

## Searching by Name

`-name` is case-sensitive. Use `-iname` for a case-insensitive match.

```bash
$ find /etc -name "nginx.conf"
/etc/nginx/nginx.conf

$ find . -iname "readme*"
./README.md
./docs/readme.txt
```

Use shell wildcards (`*`, `?`) inside quotes to prevent the shell from expanding them before `find` sees them.

## Searching by Type

`-type` filters results by file type:

| Flag | Matches |
|---|---|
| `-type f` | Regular files |
| `-type d` | Directories |
| `-type l` | Symbolic links |
| `-type s` | Sockets |

```bash
$ find . -type d -name "__pycache__"
./src/__pycache__
./tests/__pycache__
```

## Searching by Size

`-size` accepts a number with a unit suffix:

| Suffix | Unit |
|---|---|
| `c` | Bytes |
| `k` | Kilobytes |
| `M` | Megabytes |
| `G` | Gigabytes |

Prefix with `+` for "greater than" or `-` for "less than":

```bash
$ find /var/log -type f -size +100M
/var/log/syslog.1

$ find . -type f -size -1k
./config/.gitkeep
./config/empty.conf
```

## Searching by Modification Time

`-mtime` filters by last modification time in days. `-mmin` works the same way in minutes.

```bash
# Files modified in the last 24 hours
$ find . -type f -mtime -1

# Files not touched in over 30 days
$ find /tmp -type f -mtime +30

# Files modified in the last 60 minutes
$ find . -type f -mmin -60
```

There are three time flags:

- `-mtime` — last modification time (content changed)
- `-atime` — last access time (file was read)
- `-ctime` — last status change time (permissions or ownership changed)

## Searching by Permissions

`-perm` matches files by their permission bits:

```bash
# Files with exactly 644 permissions
$ find . -type f -perm 644

# Files that are world-writable (dangerous to have in web roots)
$ find /var/www -type f -perm -o+w
```

The `-` prefix means "at least these bits are set." Without it, `find` requires an exact match.

## Combining Tests with AND, OR, NOT

By default, multiple tests are ANDed together. Use `-o` for OR and `!` for NOT:

```bash
# .log OR .tmp files
$ find . \( -name "*.log" -o -name "*.tmp" \) -type f

# Everything that is NOT a directory
$ find . ! -type d
```

## Executing Commands with `-exec`

This is where `find` gets genuinely powerful. `-exec` runs a command for each matched file. Use `{}` as the placeholder for the filename and terminate the command with `\;`:

```bash
# Delete all .pyc files
$ find . -name "*.pyc" -exec rm {} \;

# Change ownership on all files in a web directory
$ find /var/www -type f -exec chown www-data:www-data {} \;

# Print the size of each matching file
$ find . -name "*.log" -exec du -sh {} \;
4.0K    ./app/logs/access.log
128M    ./app/logs/error.log
```

Replace `\;` with `+` to batch arguments into a single command invocation (faster for large result sets):

```bash
$ find . -name "*.pyc" -exec rm {} +
```

## Using `xargs` for Better Performance

`xargs` is often more flexible than `-exec ... +`. Pipe `find` output into it:

```bash
$ find . -name "*.log" -print0 | xargs -0 grep "ERROR"
```

`-print0` and `-0` use the null byte as a delimiter, which handles filenames with spaces correctly.

## Excluding Directories with `-prune`

`-prune` tells `find` to skip a directory entirely:

```bash
# Search everything except node_modules
$ find . -name "node_modules" -prune -o -name "*.js" -print

# Exclude multiple directories
$ find . \( -name ".git" -o -name "vendor" -o -name "node_modules" \) -prune -o -type f -print
```

The `-o -print` at the end is necessary — without it, `-prune` would suppress output for the non-pruned results.

## Practical One-Liners

```bash
# Find and delete all empty directories
$ find . -type d -empty -delete

# Find duplicate filenames (same name, different location)
$ find . -type f -printf "%f\n" | sort | uniq -d

# List the 10 largest files under /var
$ find /var -type f -printf "%s %p\n" | sort -rn | head -10

# Find files owned by a specific user
$ find /home -user alice -type f

# Find SUID binaries (common security audit)
$ find / -perm -4000 -type f 2>/dev/null
```

## Conclusion

`find` rewards learning its flags properly. The combination of type filtering, time-based searches, permission checks, and `-exec` makes it a complete filesystem query language. The key patterns to internalize are: use `-print0 | xargs -0` for safe pipelining, use `-prune` to skip large directories, and always quote your wildcard patterns. Most tasks that feel like they need a shell loop can be handled more cleanly with a single `find` command.
