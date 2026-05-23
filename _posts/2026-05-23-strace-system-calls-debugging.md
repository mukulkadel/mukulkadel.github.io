---
layout: post
title: "strace — Tracing System Calls for Debugging"
date: "2026-05-23 00:00:00 +0530"
slug: strace-system-calls-debugging
description: "A practical guide to strace for tracing system calls on Linux, with real examples for debugging crashes, slow programs, and permission errors."
categories: ["wiki", "unix"]
tags: ["strace", "linux", "debugging", "system calls", "unix", "performance", "sysadmin", "processes"]
---

When a program misbehaves and logs tell you nothing, `strace` is the next step. It intercepts every system call a process makes — file opens, network reads, memory maps, signal deliveries — and prints them to your terminal in real time. You don't need source code, debug symbols, or a recompile. You just attach to the process and watch.

## What is a system call?

User-space programs can't directly touch hardware or kernel data structures. They ask the kernel to do it via **system calls** — `open()`, `read()`, `write()`, `connect()`, `mmap()`, and so on. `strace` sits between the program and the kernel and logs every one of these calls along with its arguments and return value.

## Basic usage

```bash
$ strace ls /tmp
execve("/usr/bin/ls", ["ls", "/tmp"], 0x... /* 23 vars */) = 0
brk(NULL)                               = 0x55a3c1000000
...
openat(AT_FDCWD, "/tmp", O_RDONLY|O_DIRECTORY|O_CLOEXEC) = 3
getdents64(3, /* 12 entries */, 32768)  = 352
write(1, "file1.txt  file2.log\n", 21)  = 21
close(3)                                = 0
exit_group(0)                           = ?
```

Each line shows: `syscall_name(args) = return_value`. A return value of `-1` means the call failed, and `strace` appends the errno and a short description:

```
openat(AT_FDCWD, "/etc/shadow", O_RDONLY) = -1 EACCES (Permission denied)
```

## Tracing an already-running process

Attach to a running process with `-p`:

```bash
$ sudo strace -p 1234
strace: Process 1234 attached
read(5, "", 4096)                       = 0
epoll_wait(4, [], 1, 999)               = 0
...
```

Use `Ctrl-C` to detach without killing the process.

## Filtering by syscall

The raw output is noisy. `-e trace=` filters to specific syscalls or groups:

```bash
# Only file-related calls
$ strace -e trace=file ls /tmp

# Only network calls
$ strace -e trace=network curl https://example.com

# Only read and write
$ strace -e trace=read,write cat /etc/hostname
```

Built-in groups: `file`, `network`, `memory`, `process`, `signal`, `ipc`, `desc` (file descriptors).

## Saving output to a file

`strace` writes to stderr by default. Use `-o` to redirect to a file:

```bash
$ strace -o /tmp/trace.txt myapp
```

Then grep through it:

```bash
$ grep "ENOENT" /tmp/trace.txt
openat(AT_FDCWD, "/etc/myapp/config.toml", O_RDONLY) = -1 ENOENT (No such file or directory)
```

This is often how you discover an app is silently looking for a config file in the wrong path.

## Timing syscalls

`-T` prints the time spent in each call (in seconds):

```bash
$ strace -T -e trace=read,write myapp
read(3, "...", 4096)  = 4096 <0.000023>
write(1, "...", 512)  = 512  <0.000011>
read(3, "...", 4096)  = 0    <2.134567>   # blocked for 2 seconds!
```

A single slow `read()` stands out immediately. This is far faster than profiling when the bottleneck is I/O or a blocking network call.

`-c` gives an aggregate summary instead:

```bash
$ strace -c myapp
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 87.42    0.234512          58      4032           read
  7.13    0.019123          19      1008           write
  3.21    0.008612         215        40         1 openat
...
```

## Tracing child processes

By default, `strace` only follows the initial process. Use `-f` to follow `fork()` and `clone()` calls into child processes:

```bash
$ strace -f -o /tmp/full.txt myapp
```

The output includes the PID of each process:

```
[pid 5678] openat(AT_FDCWD, "config.json", O_RDONLY) = 3
[pid 5679] read(0, "", 4096)           = 0
```

## Real debugging scenarios

### Why is my app not finding a config file?

```bash
$ strace -e trace=openat ./myapp 2>&1 | grep -i config
openat(AT_FDCWD, "/etc/myapp/config.yml", O_RDONLY) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/home/mukul/.config/myapp/config.yml", O_RDONLY) = 3
```

The app tried `/etc/myapp/config.yml` first, failed, then found one at home. Now you know exactly which paths it checks — no source code needed.

### Why is a process hanging?

```bash
$ sudo strace -p 9999 -e trace=read,write,select,epoll_wait
epoll_wait(7, [], 1, 30000)             = 0   # waiting on epoll with 30s timeout
epoll_wait(7, [], 1, 30000)             = 0
epoll_wait(7, [], 1, 30000)             = 0
```

It's blocked in `epoll_wait` — waiting for I/O that never comes. The file descriptor involved (7 here) is the next thing to investigate with `lsof -p 9999`.

### Why does this fail with permission denied?

```bash
$ strace -e trace=file ./deploy.sh 2>&1 | grep "EACCES\|EPERM"
openat(AT_FDCWD, "/var/run/myapp.pid", O_WRONLY|O_CREAT|O_TRUNC, 0666) = -1 EACCES (Permission denied)
```

Exactly the file, exactly the operation. No guessing.

## Useful flags at a glance

| Flag | Effect |
|---|---|
| `-p PID` | Attach to a running process |
| `-f` | Follow child processes (fork/clone) |
| `-e trace=X` | Filter to syscall group or list |
| `-o FILE` | Write output to file |
| `-T` | Show time spent in each call |
| `-c` | Print aggregate summary on exit |
| `-s N` | Show up to N bytes of string args (default 32) |
| `-v` | Verbose: don't abbreviate structures |

`-s 256` is often worth setting — the default truncates strings at 32 bytes, which hides long paths and payloads.

## `strace` is Linux-only

`strace` uses Linux's `ptrace` interface and doesn't exist on macOS. The macOS equivalent is `dtruss` (built on DTrace) or `ktrace`/`kdebug`. On macOS with SIP enabled, `dtruss` requires disabling SIP or running as root in a VM, which makes it much less convenient. If you're debugging on macOS, `lldb` and `Instruments` are usually more practical.

## Conclusion

`strace` turns black-box debugging into a transparent one. When a process crashes with no useful log, silently ignores a config file, or hangs with no explanation, attaching `strace` gives you a complete record of every kernel interaction. Start with `-e trace=file` or `-e trace=network` to cut the noise, add `-T` to spot slow calls, and use `-o` to capture traces for offline analysis. It's a tool that repeatedly pays for the five minutes it takes to learn.
