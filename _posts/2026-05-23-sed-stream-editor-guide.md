---
layout: post
title: "sed — Stream Editor Guide for Text Manipulation"
date: "2026-05-23 00:00:00 +0530"
slug: sed-stream-editor-guide
description: "A practical guide to sed covering substitution, deletion, insertion, address ranges, and in-place editing with real terminal examples."
categories: ["wiki", "unix"]
tags: ["sed", "unix", "linux", "text processing", "command line", "terminal", "stream editor", "regex"]
---

`sed` — the stream editor — is one of the oldest Unix tools still in daily use. It reads input line by line, applies editing commands, and writes the result to stdout. It excels at substitution and transformation tasks where you'd otherwise reach for a full text editor or a throw-away Python script.

## Basic Syntax

```
sed 'command' file
```

Or pipe into it:

```bash
$ echo "Hello World" | sed 's/World/Unix/'
Hello Unix
```

Multiple commands can be chained with `-e` or separated by semicolons:

```bash
$ echo "foo bar baz" | sed -e 's/foo/FOO/' -e 's/bar/BAR/'
FOO BAR baz
```

## Substitution: `s/pattern/replacement/flags`

Substitution is the most-used `sed` command. The basic form replaces the first match on each line:

```bash
$ echo "cat and cat" | sed 's/cat/dog/'
dog and cat
```

Add the `g` flag to replace all occurrences on each line:

```bash
$ echo "cat and cat" | sed 's/cat/dog/g'
dog and dog
```

### Case-insensitive matching

GNU `sed` (Linux) supports `I`:

```bash
$ echo "Cat and CAT" | sed 's/cat/dog/gI'
dog and dog
```

macOS ships with BSD `sed`, which doesn't support `I` — install GNU sed with `brew install gnu-sed` and use it as `gsed`.

### Backreferences

Capture groups with `\(` `\)` and reference them with `\1`, `\2`:

```bash
$ echo "2024-01-15" | sed 's/\([0-9]\{4\}\)-\([0-9]\{2\}\)-\([0-9]\{2\}\)/\3\/\2\/\1/'
15/01/2024
```

With extended regex (`-E` on macOS, `-r` on GNU sed), parentheses don't need escaping:

```bash
$ echo "2024-01-15" | sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\3\/\2\/\1/'
15/01/2024
```

### Using a different delimiter

When your pattern or replacement contains `/`, swap the delimiter for anything else:

```bash
$ echo "/usr/local/bin" | sed 's|/usr/local|/opt|'
/opt/bin
```

## Addresses: Targeting Specific Lines

By default a command runs on every line. Prefix it with an address to restrict it.

**Line number:**

```bash
$ sed '3s/foo/bar/' file.txt
```

Only substitutes on line 3.

**Last line (`$`):**

```bash
$ sed '$d' file.txt
```

Deletes the last line.

**Regex address:**

```bash
$ sed '/^#/d' config.txt
```

Deletes all comment lines (lines starting with `#`).

**Range of lines (`start,end`):**

```bash
$ sed '5,10s/old/new/' file.txt
```

Applies the substitution to lines 5 through 10 only.

**Range with patterns:**

```bash
$ sed '/START/,/END/d' file.txt
```

Deletes everything from the line matching `START` to the line matching `END` (inclusive).

**Every Nth line (`first~step`)** (GNU sed only):

```bash
$ sed -n '1~2p' file.txt
```

Prints every odd-numbered line.

## Deletion: `d`

```bash
$ sed '/^$/d' file.txt
```

Removes blank lines.

```bash
$ sed '1d' file.txt
```

Removes the first line (handy for stripping a CSV header).

## Printing: `p` and `-n`

By default `sed` prints every line. Use `-n` to suppress automatic printing, then `p` to print only what you want:

```bash
$ sed -n '/ERROR/p' app.log
2024-01-15 ERROR connection refused
2024-01-15 ERROR disk full
```

Equivalent to `grep ERROR app.log`, but you can combine it with substitution:

```bash
$ sed -n 's/ERROR/CRITICAL/p' app.log
2024-01-15 CRITICAL connection refused
```

## Inserting and Appending Lines

**Insert a line before a match (`i`):**

```bash
$ sed '/^server {/i # Auto-generated config' nginx.conf
```

**Append a line after a match (`a`):**

```bash
$ sed '/listen 80;/a\    listen [::]:80;' nginx.conf
```

## In-Place Editing with `-i`

`-i` edits the file in place. Always make a backup first with an extension:

```bash
$ sed -i.bak 's/localhost/db.prod.internal/g' config.yaml
```

This writes the original to `config.yaml.bak` and updates `config.yaml`. On macOS (BSD sed), the extension is mandatory. On GNU sed, you can use `-i` without an extension.

To edit with no backup on GNU sed:

```bash
$ sed -i 's/v1/v2/g' api_config.json
```

## Multiline Patterns with `N` and `P`

`N` reads the next line into the pattern space. This lets you match across line boundaries:

```bash
$ printf "foo\nbar\nbaz\n" | sed 'N;s/foo\nbar/replaced/'
replaced
baz
```

## Practical Real-World Examples

**Strip trailing whitespace from every line:**

```bash
$ sed 's/[[:space:]]*$//' file.txt
```

**Comment out lines containing a keyword:**

```bash
$ sed 's/^\(.*debug.*\)$/#\1/' config.py
```

**Extract lines between two markers (exclusive):**

```bash
$ sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p' server.pem
```

**Double-space a file (add a blank line after each):**

```bash
$ sed 'G' file.txt
```

**Number lines (without `nl`):**

```bash
$ sed '=' file.txt | sed 'N;s/\n/\t/'
1	first line
2	second line
```

**Remove HTML tags:**

```bash
$ echo "<p>Hello <b>World</b></p>" | sed 's/<[^>]*>//g'
Hello World
```

**Replace the Nth occurrence on a line** (e.g. the 2nd):

```bash
$ echo "a a a" | sed 's/a/b/2'
a b a
```

## `sed` vs `awk` vs `grep` — Quick Decision Guide

| Task | Reach for |
|---|---|
| Find matching lines | `grep` |
| Substitution / deletion | `sed` |
| Field extraction, arithmetic, reports | `awk` |
| Multi-column transforms | `awk` |

## Conclusion

`sed` is at its best for substitution, deletion, and line-range targeting — especially in pipelines and shell scripts where you need a quick transformation without standing up a full script. The combination of address ranges and the `s` command handles the vast majority of real-world use cases. When your transformations start needing field-awareness or arithmetic, that's the signal to hand off to `awk` or a scripting language.
