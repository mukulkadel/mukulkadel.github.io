---
layout: post
title: "Writing Better Bash Scripts: Tips, Traps, and Patterns"
date: "2026-05-24 00:00:00 +0530"
slug: writing-better-bash-scripts
description: "A practical guide to writing robust, readable Bash scripts — covering safe mode flags, quoting rules, error handling, argument parsing, and common traps to avoid."
categories: ["Programming", "Tutorials", "unix"]
tags: ["bash", "shell scripting", "unix", "linux", "automation", "scripting", "command line", "error handling", "tutorial"]
---

Most Bash scripts start as a handful of commands pasted from a terminal session. They work fine — until they don't, and debugging the failure is harder than writing the script was. A few habits picked up early make Bash scripts significantly more reliable without making them harder to read. Let's go through the patterns that matter most.

## Start with a Safe Mode Header

Every non-trivial script should start with these options:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- `set -e` — exit immediately if any command exits with a non-zero status
- `set -u` — treat unset variables as errors (prevents `rm -rf $UNDEFINED/`)
- `set -o pipefail` — a pipeline fails if any command in it fails, not just the last one

Without `set -e`, a failed `git clone` won't stop your deploy script — it'll blunder onward into broken state.

## Quote Everything

Unquoted variables in Bash split on whitespace and expand globs. This causes subtle bugs:

```bash
# Bad
path=/home/user/my folder
ls $path         # runs: ls /home/user/my folder -> ls two args

# Good
ls "$path"       # runs: ls "/home/user/my folder"
```

The safe rule: **always double-quote variable expansions**, unless you explicitly want word splitting.

```bash
#!/usr/bin/env bash
set -euo pipefail

file="$1"
echo "Processing: $file"
wc -l "$file"
```

## Check If a Variable Is Set

With `set -u`, accessing an unset variable is a fatal error. To provide a default safely:

```bash
name="${NAME:-anonymous}"    # use "anonymous" if NAME is unset or empty
port="${PORT:-8080}"
output="${1:-/tmp/output}"   # default for positional argument
```

Use `${VAR:?message}` to fail with a meaningful error when a required variable is missing:

```bash
DB_HOST="${DB_HOST:?DB_HOST must be set}"
```

## Argument Parsing

For scripts with more than one or two arguments, use `getopts`:

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $0 [-v] [-o output] input"
    exit 1
}

verbose=false
output=""

while getopts "vo:" opt; do
    case "$opt" in
        v) verbose=true ;;
        o) output="$OPTARG" ;;
        *) usage ;;
    esac
done

shift $((OPTIND - 1))
input="${1:-}"

if [[ -z "$input" ]]; then
    echo "Error: input file required" >&2
    usage
fi
```

```bash
$ ./myscript.sh -v -o result.txt data.csv
```

## Error Handling and Cleanup

Use a `trap` to clean up temporary files or undo state when the script exits — even on error:

```bash
#!/usr/bin/env bash
set -euo pipefail

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

# Work in tmpdir — it will be cleaned up automatically
cp important.txt "$tmpdir/"
process "$tmpdir/important.txt"
```

`trap '...' EXIT` fires when the script exits for any reason, including `set -e` failures or `Ctrl+C`.

## Printing Errors to stderr

Error messages should go to `stderr`, not `stdout`, so they don't pollute command substitution:

```bash
die() {
    echo "Error: $*" >&2
    exit 1
}

[[ -f "$config" ]] || die "Config file not found: $config"
```

## Conditional Checks with `[[ ]]`

Prefer `[[ ]]` over `[ ]` — it's a Bash builtin that handles edge cases more safely:

```bash
# String checks
[[ -z "$var" ]]        # true if empty
[[ -n "$var" ]]        # true if non-empty
[[ "$a" == "$b" ]]     # string equality (no quotes needed inside [[ ]])
[[ "$str" == *.log ]]  # glob matching

# File checks
[[ -f "$path" ]]       # exists and is a regular file
[[ -d "$dir" ]]        # exists and is a directory
[[ -x "$bin" ]]        # exists and is executable

# Numeric comparison
[[ "$count" -gt 10 ]]
```

## Looping Over Files Safely

Never parse `ls`. Use globs or `find`:

```bash
# Good: glob expansion
for f in /var/log/*.log; do
    [[ -f "$f" ]] || continue   # skip if glob matched nothing
    echo "Processing $f"
done

# Good: find with null delimiter
find . -name "*.csv" -print0 | while IFS= read -r -d '' file; do
    echo "Found: $file"
done
```

The `IFS= read -r -d ''` pattern handles filenames with spaces, newlines, and other special characters.

## Functions

Bash functions let you avoid repeating code and make logic testable:

```bash
#!/usr/bin/env bash
set -euo pipefail

log() {
    local level="$1"; shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" >&2
}

backup_db() {
    local db="$1"
    local dest="$2"
    log INFO "Backing up $db to $dest"
    pg_dump "$db" > "$dest"
    log INFO "Backup complete"
}

backup_db myapp "/backups/myapp-$(date +%F).sql"
```

Use `local` for variables inside functions to avoid polluting the global scope.

## Checking for Required Commands

```bash
require() {
    command -v "$1" &>/dev/null || {
        echo "Error: '$1' is required but not installed" >&2
        exit 1
    }
}

require jq
require curl
require aws
```

## Debugging

Run a script with tracing enabled to print each command before executing it:

```bash
$ bash -x myscript.sh
```

Or enable it for a section of the script:

```bash
set -x    # start tracing
heavy_operation
set +x    # stop tracing
```

## Conclusion

Most Bash script problems trace back to three root causes: unquoted variables, no error handling, and assuming every command succeeds. The `set -euo pipefail` header, disciplined quoting, and `trap` for cleanup address all three. Pick these habits up from the start and you'll spend far less time debugging scripts that "worked in my terminal" but fail in production.
