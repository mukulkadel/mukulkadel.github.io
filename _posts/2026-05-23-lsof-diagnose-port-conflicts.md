---
layout: post
title: "lsof — List Open Files and Diagnose Port Conflicts"
date: "2026-05-23 00:00:00 +0530"
slug: lsof-diagnose-port-conflicts
description: "Learn how to use lsof to list open files, find which process owns a port, and debug file handle leaks on Linux and macOS."
categories: ["wiki", "unix"]
tags: ["lsof", "unix", "linux", "ports", "networking", "debugging", "processes", "command line", "sysadmin"]
---

On Unix, everything is a file — sockets, pipes, device nodes, and actual files on disk. `lsof` (list open files) gives you a live view of every file descriptor held open by every process on your system. It's the first tool to reach for when a port is already in use, a file won't delete because something holds it open, or you want to know exactly what a process is doing.

## Basic usage

```bash
$ lsof
COMMAND     PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
systemd       1   root  cwd    DIR    8,1     4096    2 /
sshd       1234   root    4u  IPv4  12345      0t0  TCP *:22 (LISTEN)
nginx      5678   root    6u  IPv4  23456      0t0  TCP *:80 (LISTEN)
python3    9012  mukul    3u  IPv4  34567      0t0  TCP 127.0.0.1:5000 (LISTEN)
...
```

The output is verbose — typically thousands of lines. You'll almost always pair `lsof` with a filter.

## Finding what's using a port

This is the most common reason to reach for `lsof`:

```bash
$ lsof -i :8080
COMMAND   PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
node     4321  mukul   23u  IPv4  56789      0t0  TCP *:http-alt (LISTEN)
```

`-i` filters by network file. `:8080` matches any process listening on port 8080. Now you have the PID and can kill it:

```bash
$ kill 4321
# or forcefully:
$ kill -9 4321
```

### Filter by protocol or address

```bash
$ lsof -i tcp            # all TCP connections
$ lsof -i udp:53         # DNS (UDP port 53)
$ lsof -i @192.168.1.10  # connections to a specific host
$ lsof -i tcp:3000-3100  # port range
```

## Listing open files for a specific process

```bash
$ lsof -p 1234
```

Or by process name:

```bash
$ lsof -c nginx
```

`-c` matches processes whose name starts with the string. Combine with `-r` to watch in real time:

```bash
$ lsof -c nginx -r 2   # refresh every 2 seconds
```

## Finding which process has a file open

Useful when you can't delete a file because something still holds it:

```bash
$ lsof /var/log/app.log
COMMAND  PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
myapp   8888  mukul    1w   REG    8,1   204800  123 /var/log/app.log
```

Same trick for a whole directory:

```bash
$ lsof +D /var/log/
```

`+D` recurses into subdirectories. It can be slow on large trees.

## Listing all network connections

```bash
$ lsof -i
COMMAND     PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
sshd       1234   root    3u  IPv4  11111      0t0  TCP *:22 (LISTEN)
postgres   2345 postgres   5u  IPv4  22222      0t0  TCP 127.0.0.1:5432 (LISTEN)
chrome    56789  mukul   45u  IPv4  33333      0t0  TCP 192.168.1.5:51234->142.250.1.1:443 (ESTABLISHED)
```

To show only established connections (no listeners):

```bash
$ lsof -i -s TCP:ESTABLISHED
```

To show only listeners:

```bash
$ lsof -i -s TCP:LISTEN
```

## Listing deleted files still held open

A common gotcha: a log file is deleted, but disk space isn't freed because a process still has it open. `lsof` shows these as `(deleted)`:

```bash
$ lsof | grep deleted
nginx   4567  root    2w   REG    8,1   1073741824  999 /var/log/nginx/error.log (deleted)
```

You can recover the content from `/proc/<pid>/fd/<fd>` or just restart the process to release the handle and reclaim the space.

## Useful flags cheat sheet

| Flag | Meaning |
|---|---|
| `-i :PORT` | Files on network port |
| `-p PID` | Files for a specific PID |
| `-c NAME` | Files for processes matching name |
| `-u USER` | Files opened by a user |
| `+D DIR` | All open files under a directory |
| `-t` | Output PIDs only (pipe-friendly) |
| `-n` | Skip hostname resolution (faster) |
| `-P` | Skip port-name resolution (shows numbers) |
| `-r N` | Repeat every N seconds |

### `-n` and `-P` speed things up significantly

DNS and port-name lookups make `lsof` sluggish. Add both flags when you don't need human-readable names:

```bash
$ lsof -nP -i :5432
COMMAND     PID     USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
postgres   2345 postgres    5u  IPv4  22222      0t0  TCP 127.0.0.1:5432 (LISTEN)
```

## Pipe-friendly output with `-t`

`-t` outputs only the PID, making it easy to feed into `kill`:

```bash
# Kill everything on port 3000
$ kill $(lsof -t -i :3000)
```

## macOS quirks

On macOS, `lsof` is preinstalled and works the same way. One difference: macOS uses `launchd` for many system sockets, so some entries will show `launchd` or `com.apple.*` names. Also, some system sockets may require `sudo` to show up:

```bash
$ sudo lsof -i :443
```

## Conclusion

`lsof` is the definitive answer to "what has this port/file open?" Once you know the core flags — `-i` for network, `-p` for PID, `-c` for process name, `-t` for pipe-friendly output — you can diagnose port conflicts, track down file handle leaks, and understand exactly what a running process is touching. Adding `-nP` as a habit keeps it fast. It's one of those tools you install once and never uninstall.
