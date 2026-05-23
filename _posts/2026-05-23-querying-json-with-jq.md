---
layout: post
title: "jq — Querying JSON from the Terminal: A Practical Guide"
date: "2026-05-23 00:00:00 +0530"
slug: querying-json-with-jq
description: "Learn how to use jq to filter, transform, and reshape JSON data directly in the terminal with practical examples and real command output."
categories: ["Programming", "unix", "Tutorials"]
tags: ["jq", "json", "unix", "command line", "terminal", "linux", "macos", "tutorial", "data processing"]
---

If you've ever piped `curl` output to `python -m json.tool` just to make it readable, you're already halfway to wanting `jq`. It's a lightweight, blazing-fast command-line tool for parsing and transforming JSON — and once it clicks, you'll reach for it constantly when working with APIs, log files, and config output.

## Installing jq

On macOS with Homebrew:

```bash
$ brew install jq
```

On Debian/Ubuntu:

```bash
$ sudo apt-get install jq
```

Verify it's working:

```bash
$ jq --version
jq-1.7.1
```

## Your First Filter

`jq` reads JSON from stdin and applies a filter. The identity filter `.` just pretty-prints the input:

```bash
$ echo '{"name":"Alice","age":30}' | jq '.'
{
  "name": "Alice",
  "age": 30
}
```

To pull out a single field, use `.fieldname`:

```bash
$ echo '{"name":"Alice","age":30}' | jq '.name'
"Alice"
```

To strip the surrounding quotes from a string, use the `-r` (raw output) flag:

```bash
$ echo '{"name":"Alice","age":30}' | jq -r '.name'
Alice
```

## Working with Arrays

Given a JSON array, `.[]` iterates over every element:

```bash
$ echo '[1,2,3]' | jq '.[]'
1
2
3
```

To access a specific index, use `.[0]`, `.[1]`, etc.:

```bash
$ echo '["a","b","c"]' | jq '.[1]'
"b"
```

Array slicing works just like Python:

```bash
$ echo '[0,1,2,3,4]' | jq '.[2:4]'
[
  2,
  3
]
```

## Querying Nested Objects

Let's use a more realistic payload — a GitHub API response for a user:

```bash
$ curl -s https://api.github.com/users/torvalds | jq '.'
```

Drill into nested fields with chained `.`:

```bash
$ curl -s https://api.github.com/users/torvalds | jq '.name, .public_repos, .location'
"Linus Torvalds"
256
"Portland, OR"
```

## Mapping Over Arrays with `map`

`map(f)` applies a filter to every element of an array and returns a new array. This is the most useful pattern in `jq`.

```bash
$ echo '[{"name":"Alice","score":90},{"name":"Bob","score":75}]' | jq 'map(.name)'
[
  "Alice",
  "Bob"
]
```

Combine with arithmetic:

```bash
$ echo '[{"name":"Alice","score":90},{"name":"Bob","score":75}]' | jq 'map({name: .name, grade: (if .score >= 80 then "A" else "B" end)})'
[
  {
    "name": "Alice",
    "grade": "A"
  },
  {
    "name": "Bob",
    "grade": "B"
  }
]
```

## Filtering with `select`

`select(condition)` keeps only elements where the condition is true:

```bash
$ echo '[{"name":"Alice","active":true},{"name":"Bob","active":false}]' | jq '.[] | select(.active == true) | .name'
"Alice"
```

The `|` in `jq` is a pipe — it feeds the output of one filter into the next, just like shell pipes.

Filter by numeric comparison:

```bash
$ echo '[{"port":80},{"port":443},{"port":8080}]' | jq '[.[] | select(.port > 100)]'
[
  {
    "port": 443
  },
  {
    "port": 8080
  }
]
```

## Building New Objects and Arrays

You can construct a new JSON object from scratch inside a filter using `{}`:

```bash
$ curl -s https://api.github.com/users/torvalds | jq '{login: .login, repos: .public_repos}'
{
  "login": "torvalds",
  "repos": 256
}
```

Wrap in `[]` to collect streamed output back into an array:

```bash
$ echo '[{"id":1,"val":10},{"id":2,"val":20}]' | jq '[.[] | {id: .id, doubled: (.val * 2)}]'
[
  {
    "id": 1,
    "doubled": 20
  },
  {
    "id": 2,
    "doubled": 40
  }
]
```

## Useful Built-in Functions

### `keys` and `values`

```bash
$ echo '{"a":1,"b":2,"c":3}' | jq 'keys'
[
  "a",
  "b",
  "c"
]
```

### `length`

Works on arrays, objects, and strings:

```bash
$ echo '[1,2,3,4,5]' | jq 'length'
5

$ echo '"hello"' | jq 'length'
5
```

### `has`

Checks if a key exists:

```bash
$ echo '{"name":"Alice"}' | jq 'has("age")'
false
```

### `to_entries` and `from_entries`

Converts an object to an array of `{key, value}` pairs and back — useful for iterating over object fields:

```bash
$ echo '{"x":1,"y":2}' | jq 'to_entries'
[
  {
    "key": "x",
    "value": 1
  },
  {
    "key": "y",
    "value": 2
  }
]
```

### `group_by` and `unique_by`

```bash
$ echo '[{"type":"A"},{"type":"B"},{"type":"A"}]' | jq 'group_by(.type) | map({type: .[0].type, count: length})'
[
  {
    "type": "A",
    "count": 2
  },
  {
    "type": "B",
    "count": 1
  }
]
```

## Reading from a File

Pass a file directly instead of using stdin:

```bash
$ jq '.users | map(.email)' data.json
```

Use `-c` (compact) to output one JSON object per line — handy for log processing:

```bash
$ jq -c '.[] | select(.level == "error")' app.log.json
{"level":"error","message":"connection refused","ts":1716428800}
{"level":"error","message":"timeout after 30s","ts":1716428900}
```

## Practical One-Liners

**Get all running Docker container names:**

```bash
$ docker inspect $(docker ps -q) | jq -r '.[].Name' | sed 's|/||'
my-api
postgres
redis
```

**Extract AWS instance IDs from `describe-instances`:**

```bash
$ aws ec2 describe-instances | jq -r '.Reservations[].Instances[].InstanceId'
i-0abcdef1234567890
i-0fedcba9876543210
```

**Pretty-print and filter a large log file:**

```bash
$ cat events.json | jq 'select(.severity == "CRITICAL") | {time: .timestamp, msg: .message}'
```

## Conclusion

`jq` rewards a small upfront investment with enormous payoff — once you know `.`, `map`, `select`, and `|`, you can handle the vast majority of real-world JSON wrangling without leaving the terminal. The built-in functions like `group_by`, `to_entries`, and `has` fill in the gaps for more complex transformations. Keep the [jq manual](https://jqlang.github.io/jq/manual/) bookmarked; it's dense but well-organized and covers everything from string interpolation to recursive descent.
