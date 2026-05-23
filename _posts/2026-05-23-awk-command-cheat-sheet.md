---
layout: post
title: "awk Command Cheat Sheet with Real Examples"
date: "2026-05-23 00:00:00 +0530"
slug: awk-command-cheat-sheet
description: "A practical awk reference covering field splitting, patterns, built-in variables, and real one-liners for text processing on Linux and macOS."
categories: ["wiki", "unix"]
tags: ["awk", "unix", "command line", "linux", "text processing", "cheatsheet", "terminal", "scripting"]
---

`awk` is one of those Unix tools that looks cryptic at first glance and then becomes indispensable. It reads input line by line, splits each line into fields, and lets you run a tiny program against each one — making it perfect for log parsing, report generation, and quick data transformations without writing a script.

## Basic Structure

Every `awk` program follows the same pattern:

```
awk 'pattern { action }' file
```

- **pattern** — a condition that must be true for the action to run (optional)
- **action** — what to do with the matching line (optional; default is `print`)

If you omit the pattern, the action runs on every line. If you omit the action, `awk` prints the matching lines.

## Fields and the Field Separator

`awk` splits each line on whitespace by default. Fields are numbered `$1`, `$2`, ..., and `$0` is the entire line.

```bash
$ echo "Alice 30 Engineer" | awk '{ print $1, $3 }'
Alice Engineer
```

Change the field separator with `-F`:

```bash
$ echo "root:x:0:0:root:/root:/bin/bash" | awk -F: '{ print $1, $7 }'
root /bin/bash
```

Set a multi-character or regex separator:

```bash
$ echo "key=value=extra" | awk -F'=' '{ print $2 }'
value
```

## Built-in Variables

| Variable | Meaning |
|---|---|
| `$0` | The full current line |
| `$1`, `$2`, ... | Individual fields |
| `NF` | Number of fields on the current line |
| `NR` | Current line (record) number |
| `FS` | Input field separator (default: whitespace) |
| `OFS` | Output field separator (default: space) |
| `RS` | Input record separator (default: newline) |
| `ORS` | Output record separator (default: newline) |
| `FILENAME` | Name of the current input file |

```bash
$ awk '{ print NR, NF, $0 }' /etc/hosts
1 2 127.0.0.1 localhost
2 1 ::1
3 4 255.255.255.255 broadcasthost
```

## Pattern Matching

Match lines containing a regex:

```bash
$ awk '/ERROR/' app.log
2024-01-15 ERROR connection refused on port 5432
2024-01-15 ERROR disk quota exceeded
```

Negate with `!~`:

```bash
$ awk '!/DEBUG/' app.log
```

Match a specific field against a pattern:

```bash
$ awk '$3 ~ /ERROR/' app.log
```

Numeric comparisons work directly:

```bash
$ awk '$5 > 1000' access.log
```

## BEGIN and END Blocks

`BEGIN` runs before any input is read. `END` runs after all input is processed. Both are optional.

```bash
$ awk 'BEGIN { print "=== Report ===" } { print $1 } END { print "=== Done ===" }' names.txt
=== Report ===
Alice
Bob
Carol
=== Done ===
```

A classic use: summing a column.

```bash
$ awk '{ sum += $3 } END { print "Total:", sum }' sales.txt
Total: 48320
```

## Printing and Formatting

`print` separates items with `OFS` (default space). `printf` works just like C:

```bash
$ awk '{ printf "%-20s %5d\n", $1, $2 }' data.txt
Alice                   30
Bob                     25
```

Set `OFS` to change the output delimiter:

```bash
$ echo "Alice 30 Engineer" | awk 'BEGIN { OFS="," } { print $1, $2, $3 }'
Alice,30,Engineer
```

Print the last field regardless of how many there are:

```bash
$ echo "a b c d e" | awk '{ print $NF }'
e
```

Print all but the first field:

```bash
$ echo "timestamp INFO message goes here" | awk '{ $1=""; print $0 }'
 INFO message goes here
```

## Conditionals and Loops

`awk` has full `if/else`, `for`, and `while` support inside action blocks:

```bash
$ awk '{ if ($2 >= 90) print $1, "PASS"; else print $1, "FAIL" }' scores.txt
Alice PASS
Bob FAIL
Carol PASS
```

```bash
$ awk 'BEGIN { for (i=1; i<=5; i++) print i }'
1
2
3
4
5
```

## Arrays

`awk` arrays are associative (like a hash map). You don't declare them — just use them:

```bash
$ awk '{ count[$1]++ } END { for (user in count) print user, count[user] }' access.log
alice 42
bob 17
carol 8
```

Check if a key exists with `in`:

```bash
$ awk '$1 in seen { next } { seen[$1]=1; print }' file.txt
```

This prints only the first occurrence of each value in column 1 — a simple dedup.

## Common One-Liners

**Print lines between two patterns (inclusive):**

```bash
$ awk '/START/,/END/' file.txt
```

**Count lines matching a pattern:**

```bash
$ awk '/ERROR/ { count++ } END { print count }' app.log
14
```

**Remove duplicate lines (preserving order):**

```bash
$ awk '!seen[$0]++' file.txt
```

**Print every other line:**

```bash
$ awk 'NR % 2 == 0' file.txt
```

**Sum the second column of a CSV:**

```bash
$ awk -F, '{ sum += $2 } END { print sum }' data.csv
```

**Convert whitespace-delimited output to CSV:**

```bash
$ ps aux | awk 'NR>1 { print $1","$2","$11 }'
root,1,/sbin/launchd
_windowserver,188,/System/Library/PrivateFrameworks/SkyLight.framework/...
```

**Find lines longer than 80 characters:**

```bash
$ awk 'length($0) > 80' source.c
```

**Print unique values of a field:**

```bash
$ awk -F: '!seen[$1]++ { print $1 }' /etc/passwd
root
nobody
daemon
```

## Multiple Files and FILENAME

When processing multiple files, `FILENAME` tells you which file the current line came from:

```bash
$ awk '{ print FILENAME, NR, $0 }' *.log
access.log 1 GET /index.html 200
error.log 1 PHP Warning: ...
```

Reset a counter per file using `FNR` (file-relative record number) vs `NR` (global):

```bash
$ awk 'FNR==1 { print "--- File:", FILENAME }' *.log
--- File: access.log
--- File: error.log
```

## Conclusion

`awk` covers an enormous range of tasks — anywhere from a quick column extraction to a multi-pass report with totals and grouping. The key mental model is: pattern gates the action, fields are `$1`…`$NF`, and `BEGIN`/`END` handle setup and teardown. Once those three ideas are solid, most `awk` one-liners read naturally. For anything more complex, `sed` handles in-place substitution and `jq` handles JSON — but for structured plaintext, `awk` is still the sharpest tool in the box.
