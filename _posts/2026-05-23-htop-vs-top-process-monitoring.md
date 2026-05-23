---
layout: post
title: "htop vs top — Monitoring Processes in the Terminal"
date: "2026-05-23 00:00:00 +0530"
slug: htop-vs-top-process-monitoring
description: "A practical comparison of htop and top for monitoring Linux processes, CPU, and memory — with interactive shortcuts and real-world usage tips."
categories: ["wiki", "unix"]
tags: ["htop", "top", "linux", "unix", "processes", "monitoring", "terminal", "performance", "sysadmin"]
---

When a server slows to a crawl or a process starts eating memory, `top` is usually the first thing you open. It's been on every Unix system since the 1980s. `htop` is the modern replacement — same idea, better interface, more features. Knowing both means you can work effectively whether you're on a barebones VM or your own machine.

## `top` — the universal baseline

`top` is available on every Linux and macOS system without installation. Launch it:

```bash
$ top
```

The header shows a system summary, followed by a process list sorted by CPU usage:

```
top - 14:32:05 up 3 days,  2:14,  2 users,  load average: 0.42, 0.38, 0.35
Tasks: 182 total,   1 running, 181 sleeping,   0 stopped,   0 zombie
%Cpu(s):  3.2 us,  0.8 sy,  0.0 ni, 95.8 id,  0.0 wa,  0.0 hi,  0.2 si
MiB Mem :  15823.8 total,   4201.2 free,   8930.4 used,   2692.2 buff/cache
MiB Swap:   2048.0 total,   1798.4 free,    249.6 used.   6312.4 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 4321 mukul     20   0 1234560 234512  45678 S  12.3   1.5   3:21.45 node
 5678 mukul     20   0  456789  89012  12345 S   3.1   0.5   0:45.23 python3
    1 root      20   0  168144  12084   8448 S   0.0   0.1   0:03.12 systemd
```

### Key columns

| Column | Meaning |
|---|---|
| `PID` | Process ID |
| `USER` | Owner |
| `PR` / `NI` | Priority / nice value |
| `VIRT` | Total virtual memory allocated |
| `RES` | Resident memory (physically in RAM) |
| `SHR` | Shared memory |
| `S` | State: `R` running, `S` sleeping, `Z` zombie, `D` uninterruptible sleep |
| `%CPU` | CPU usage since last refresh |
| `%MEM` | Percentage of physical RAM |
| `TIME+` | Total CPU time used |

### Interactive shortcuts in `top`

| Key | Action |
|---|---|
| `k` | Kill a process (prompts for PID) |
| `r` | Renice a process |
| `M` | Sort by memory usage |
| `P` | Sort by CPU (default) |
| `T` | Sort by time |
| `u` | Filter by user |
| `f` | Field management — add/remove columns |
| `1` | Toggle per-CPU breakdown |
| `q` | Quit |

## `htop` — the better default

`htop` is not installed by default on all systems, but it's one command away:

```bash
# Debian/Ubuntu
$ sudo apt install htop

# macOS
$ brew install htop

# RHEL/CentOS
$ sudo yum install htop
```

Launch it:

```bash
$ htop
```

The display is similar to `top` but with color, horizontal scrolling, and a mouse-clickable interface:

```
  CPU[|||||||||||||||||||||||||||||||||||||||||||||45.3%]
  Mem[|||||||||||||||||||||||||||||||||||9.02G/15.5G]
  Swp[|32.6M/2.00G]

  PID USER       PRI  NI  VIRT   RES   SHR S CPU% MEM%   TIME+  Command
 4321 mukul       20   0 1.18G  229M 44.6M S 12.3  1.5  3:21.45 node
 5678 mukul       20   0  446M 86.9M 12.1M S  3.1  0.5  0:45.23 python3
    1 root        20   0  164M 11.8M  8.2M S  0.0  0.1  0:03.12 /sbin/init
```

### What `htop` adds over `top`

- **Per-core CPU meters** — each core gets its own bar so you can see uneven load at a glance
- **Mouse support** — click column headers to sort, click a process to select it
- **Tree view** — press `F5` to see the process hierarchy (parent → child relationships)
- **Easier process management** — select a process with arrow keys, press `F9` to send a signal, `F7`/`F8` to adjust nice value
- **Search** — press `F3` or `/` to filter by process name
- **No truncation** — command lines aren't cut off; scroll right to see the full command

### htop keyboard shortcuts

| Key | Action |
|---|---|
| `F1` | Help |
| `F2` | Setup (customize columns, colors) |
| `F3` / `/` | Search |
| `F4` | Filter |
| `F5` | Tree view toggle |
| `F6` | Sort by column |
| `F9` | Kill (choose signal) |
| `F10` / `q` | Quit |
| `Space` | Tag a process |
| `u` | Filter by user |
| `H` | Toggle user threads |
| `K` | Toggle kernel threads |

## Reading the load average

Both tools show load average in the header:

```
load average: 0.42, 0.38, 0.35
```

These three numbers are the 1-minute, 5-minute, and 15-minute averages. A load average equal to the number of CPU cores means the system is fully utilized. Higher than that means processes are waiting. On a 4-core machine, a load of 4.0 is 100% — a load of 8.0 means the queue is backed up.

## Memory: `RES` is what matters

`VIRT` (virtual memory) is almost always misleadingly large — it includes memory-mapped files, shared libraries, and allocated-but-not-used memory. `RES` (resident set size) is the actual physical RAM the process is using. Focus on `RES` when diagnosing memory pressure.

## Zombie processes

A `Z` in the state column means a zombie — the process has exited but its parent hasn't called `wait()` to collect the exit status. Zombies consume no CPU or memory (just a PID slot), but a large number of them indicates a bug in the parent process. You can't kill a zombie directly; restarting the parent is the fix.

## `btop` — the third option

If you want an even more visual interface, `btop` (also available via Homebrew or `apt`) takes the idea further with animated graphs, network and disk I/O panels, and a more polished layout. It's worth a look if you spend a lot of time monitoring servers.

## Quick reference: `top` vs `htop`

| Feature | `top` | `htop` |
|---|---|---|
| Pre-installed | Always | Usually not |
| Color UI | No | Yes |
| Mouse support | Limited | Full |
| Tree view | No | Yes (`F5`) |
| Per-core meters | Toggle (`1`) | Always visible |
| Search/filter | `u` (user only) | `F3`, `F4` |
| Kill signal choice | No | Yes |

## Conclusion

Use `top` when you're on a system where you can't install anything — it's always there. Switch to `htop` as your daily driver once it's available; the tree view, per-core meters, and search alone make it worth it. Either way, the fundamentals are the same: watch `RES` for memory, watch `%CPU` for CPU, look at load average relative to your core count, and filter aggressively so you're not staring at 200 sleeping processes to find the one that's causing problems.
