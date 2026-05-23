---
layout: post
title: "grep, egrep, and ripgrep — Pattern Matching Cheat Sheet"
date: "2026-05-23 00:00:00 +0530"
slug: grep-egrep-ripgrep-cheat-sheet
description: "A complete reference for grep, egrep, and ripgrep covering flags, regex syntax, recursive search, and real-world one-liners for searching code and logs."
categories: ["wiki", "unix"]
tags: ["grep", "ripgrep", "regex", "unix", "linux", "command line", "search", "cheatsheet", "terminal"]
---

`grep` is one of the most-used tools on any Unix system. It searches text for lines matching a pattern — and while the name stands for "Global Regular Expression Print," it's really just a fast line filter. `ripgrep` (`rg`) is a modern replacement that's dramatically faster for searching code, so this cheat sheet covers both.

## Basic Syntax

```bash
$ grep "pattern" file.txt
$ grep "pattern" file1.txt file2.txt
$ command | grep "pattern"
```

## Essential Flags

| Flag | Meaning |
|---|---|
| `-i` | Case-insensitive match |
| `-v` | Invert: print lines that do NOT match |
| `-n` | Show line numbers |
| `-c` | Count matching lines (don't print them) |
| `-l` | Print only filenames that have a match |
| `-L` | Print filenames with NO match |
| `-r` | Recursive: search all files in a directory |
| `-R` | Recursive, following symlinks |
| `-w` | Match whole words only |
| `-x` | Match whole lines only |
| `-A N` | Print N lines after each match |
| `-B N` | Print N lines before each match |
| `-C N` | Print N lines before and after each match |
| `-E` | Extended regex (same as `egrep`) |
| `-P` | Perl-compatible regex (PCRE) — GNU grep only |
| `-F` | Fixed string, no regex (faster for literals) |
| `-o` | Print only the matched part, not the full line |
| `-q` | Quiet: exit 0 if match found, 1 otherwise |
| `--color` | Highlight matches (often default) |

## grep vs egrep vs fgrep

- `grep` — basic regex (BRE): `\(`, `\)`, `\+` need backslashes
- `egrep` / `grep -E` — extended regex (ERE): `(`, `)`, `+`, `|` work without backslashes
- `fgrep` / `grep -F` — no regex, literal string matching; fastest

In practice, always use `grep -E` instead of `egrep` — it's the same behavior, just more explicit.

## Basic Examples

```bash
$ grep "ERROR" app.log
2024-01-15 10:23:11 ERROR Connection refused
2024-01-15 10:25:44 ERROR Timeout after 30s
```

Case-insensitive:

```bash
$ grep -i "error" app.log
```

Count matches:

```bash
$ grep -c "ERROR" app.log
14
```

Show surrounding context (5 lines before and after):

```bash
$ grep -C 5 "segfault" dmesg.log
```

## Recursive Search

```bash
$ grep -rn "TODO" ./src/
./src/api/handler.go:42:  // TODO: add retry logic
./src/db/conn.go:17:      // TODO: use connection pool
```

Restrict to a file type with `--include`:

```bash
$ grep -rn --include="*.py" "import requests" .
./scripts/fetch.py:3:import requests
./api/client.py:1:import requests
```

Exclude a directory:

```bash
$ grep -rn --exclude-dir=".git" --exclude-dir="node_modules" "console.log" .
```

## Extended Regex with `-E`

Match lines containing "foo" or "bar":

```bash
$ grep -E "foo|bar" file.txt
```

One or more digits:

```bash
$ grep -E "[0-9]+" file.txt
```

Match IP addresses:

```bash
$ grep -E "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" access.log
```

Anchors: `^` start of line, `$` end:

```bash
$ grep "^ERROR" app.log        # lines starting with ERROR
$ grep "\.json$" filelist.txt  # lines ending with .json
```

## Whole-Word and Whole-Line Matching

```bash
$ grep -w "log" file.txt     # matches "log" but not "logging" or "catalog"
$ grep -x "exact line" file.txt  # only lines that are exactly "exact line"
```

## Printing Only the Match (`-o`)

Extract just the matching portion from each line:

```bash
$ grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" access.log | sort | uniq -c | sort -rn
     342 192.168.1.1
      87 10.0.0.15
      12 172.16.0.3
```

This extracts IPs, counts occurrences, and sorts by frequency — all without `awk`.

## Using grep in Scripts

`grep -q` exits silently with code 0 (match) or 1 (no match):

```bash
if grep -q "ERROR" app.log; then
  echo "Errors found, alerting oncall"
fi
```

`-l` returns only filenames — useful for batch processing:

```bash
$ grep -rl "deprecated_function" ./src/ | xargs sed -i 's/deprecated_function/new_function/g'
```

## ripgrep (`rg`) — The Faster Alternative

Install:

```bash
$ brew install ripgrep    # macOS
$ sudo apt install ripgrep  # Ubuntu
```

`rg` is 5–10x faster than `grep -r` on codebases because it:

- Uses SIMD for matching
- Skips binary files automatically
- Respects `.gitignore` by default
- Searches in parallel across CPU cores

The interface mirrors `grep` in most ways:

```bash
$ rg "TODO" ./src/
src/api/handler.go:42:  // TODO: add retry logic
src/db/conn.go:17:      // TODO: use connection pool
```

### rg-specific Advantages

**Respects `.gitignore`** — doesn't search `node_modules`, `dist`, or `.git` by default. Override with `--no-ignore`.

**File type filtering** with `-t`:

```bash
$ rg -t py "import os"       # only .py files
$ rg -t js "console.log"     # only .js files
$ rg --type-list             # see all supported types
```

**Fixed string** (faster, no regex):

```bash
$ rg -F "function()" .
```

**Count per file:**

```bash
$ rg -c "ERROR" logs/
logs/app.log:14
logs/worker.log:3
```

**Show only filenames:**

```bash
$ rg -l "TODO" .
```

**Multiline mode:**

```bash
$ rg -U "foo\nbar" .
```

**Replace in output** (doesn't modify files — use with `sed` or `perl` for that):

```bash
$ rg -r "new_name" "old_name" .
```

## Common One-Liners

**Find all files containing a function name:**

```bash
$ grep -rl "handleRequest" ./src/
```

**Count total lines of Python code (excluding blank lines and comments):**

```bash
$ grep -r --include="*.py" -v "^[[:space:]]*#\|^[[:space:]]*$" . | wc -l
```

**Find lines with two or more consecutive spaces:**

```bash
$ grep -P "  +" file.txt
```

**Check if a process is running:**

```bash
$ pgrep -x nginx || grep -q nginx /proc/*/comm 2>/dev/null && echo "running"
```

**Find all TODO and FIXME comments:**

```bash
$ rg "TODO|FIXME|HACK|XXX" --color always | less -R
```

**Search compressed logs:**

```bash
$ zgrep "ERROR" /var/log/nginx/error.log.gz
```

## grep Exit Codes

| Code | Meaning |
|---|---|
| `0` | Match found |
| `1` | No match |
| `2` | Error (bad pattern, missing file) |

These are useful in shell scripts: `grep -q "pattern" file && echo "found"`.

## Conclusion

`grep` with `-E`, `-n`, `-r`, and `-C` covers most daily search needs. For code search, switch to `ripgrep` — it's faster, `.gitignore`-aware, and has better defaults. The fundamentals — anchors, character classes, alternation — transfer directly between the two. Know how to extract just the match with `-o`, how to count with `-c`, and how to use exit codes in scripts, and you'll have `grep` fully in your toolkit.
