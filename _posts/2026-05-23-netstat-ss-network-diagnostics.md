---
layout: post
title: "netstat and ss — Diagnosing Network Connections on Linux"
date: "2026-05-23 00:00:00 +0530"
slug: netstat-ss-network-diagnostics
description: "Learn how to use netstat and ss to inspect open ports, active connections, socket state, and listening services on Linux with practical examples."
categories: ["wiki", "unix"]
tags: ["netstat", "ss", "networking", "linux", "unix", "diagnostics", "ports", "tcp", "devops"]
---

When something isn't listening on the port you expect, or a service won't start because "address already in use," `netstat` and `ss` are the first tools to reach for. They show you what sockets are open, which processes own them, and the state of every connection on the machine. `ss` is the modern replacement for `netstat` — faster and more detailed — but `netstat` is still installed on most systems, so it's worth knowing both.

## Installing the Tools

On modern Debian/Ubuntu systems, `netstat` has been removed from the default install:

```bash
$ sudo apt install net-tools   # provides netstat
$ sudo apt install iproute2    # provides ss (usually pre-installed)
```

On macOS, `netstat` is available by default. `ss` is a Linux-only tool.

## netstat Basics

`netstat` with no arguments shows all active connections and Unix domain sockets — usually more noise than you want. These are the flags you'll actually use:

| Flag | Meaning |
|---|---|
| `-t` | TCP sockets |
| `-u` | UDP sockets |
| `-l` | Listening sockets only |
| `-a` | All sockets (listening + connected) |
| `-n` | Numeric output (don't resolve hostnames or port names) |
| `-p` | Show the PID/process name owning the socket |
| `-r` | Show the routing table |
| `-s` | Summary statistics per protocol |

### Most common command: what's listening

```bash
$ sudo netstat -tlnp
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      1234/sshd
tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      5678/postgres
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      9012/nginx
tcp6       0      0 :::443                  :::*                    LISTEN      9012/nginx
```

Breaking down the flags: `-t` (TCP), `-l` (listening), `-n` (numeric), `-p` (process).

Check UDP as well:

```bash
$ sudo netstat -ulnp
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
udp        0      0 0.0.0.0:53              0.0.0.0:*                           1111/systemd-resolve
```

### Show all active TCP connections

```bash
$ netstat -tn
Active Internet connections (w/o servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State
tcp        0      0 192.168.1.10:56234      93.184.216.34:443       ESTABLISHED
tcp        0      0 192.168.1.10:54321      140.82.113.4:443        ESTABLISHED
```

### Find what's using a specific port

```bash
$ sudo netstat -tlnp | grep :8080
tcp        0      0 0.0.0.0:8080            0.0.0.0:*               LISTEN      3456/node
```

### Routing table

```bash
$ netstat -rn
Kernel IP routing table
Destination     Gateway         Genmask         Flags   MSS Window  irtt Iface
0.0.0.0         192.168.1.1     0.0.0.0         UG        0 0          0 eth0
192.168.1.0     0.0.0.0         255.255.255.0   U         0 0          0 eth0
```

### Protocol statistics

```bash
$ netstat -s | head -20
Ip:
    123456 total packets received
    0 forwarded
    0 incoming packets discarded
Tcp:
    5678 active connection openings
    1234 passive connection openings
    12 failed connection attempts
```

## ss — The Modern Replacement

`ss` queries socket information directly from the kernel and is significantly faster than `netstat` on busy systems. The flag interface is similar but not identical.

| Flag | Meaning |
|---|---|
| `-t` | TCP |
| `-u` | UDP |
| `-l` | Listening |
| `-a` | All |
| `-n` | Numeric |
| `-p` | Process info |
| `-s` | Summary |
| `-e` | Extended socket info |
| `-o` | Timer information |
| `-r` | Try to resolve hostnames |

### What's listening (the ss equivalent of netstat -tlnp)

```bash
$ sudo ss -tlnp
State   Recv-Q  Send-Q   Local Address:Port    Peer Address:Port  Process
LISTEN  0       128            0.0.0.0:22           0.0.0.0:*     users:(("sshd",pid=1234,fd=3))
LISTEN  0       5            127.0.0.1:5432         0.0.0.0:*     users:(("postgres",pid=5678,fd=5))
LISTEN  0       511            0.0.0.0:80           0.0.0.0:*     users:(("nginx",pid=9012,fd=6))
```

### Filter by state

`ss` supports rich state filtering:

```bash
$ ss -tn state established
Recv-Q  Send-Q  Local Address:Port   Peer Address:Port
0       0       192.168.1.10:56234   93.184.216.34:443
```

Available states: `established`, `syn-sent`, `syn-recv`, `fin-wait-1`, `fin-wait-2`, `time-wait`, `closed`, `close-wait`, `last-ack`, `listening`, `closing`.

Filter for TIME_WAIT sockets (a common sign of connection churn):

```bash
$ ss -tn state time-wait | wc -l
247
```

### Filter by address or port

```bash
$ ss -tnp 'dport = :443'    # connections to port 443
$ ss -tnp 'sport = :8080'   # connections from local port 8080
$ ss -tnp 'dst 10.0.0.1'    # connections to a specific IP
```

### Show socket memory usage

```bash
$ ss -tm
```

### Summary

```bash
$ ss -s
Total: 245
TCP:   18 (estab 5, closed 1, orphaned 0, timewait 1)

Transport Total     IP        IPv6
RAW       0         0         0
UDP       6         4         2
TCP       17        9         8
```

## Practical Diagnostic Scenarios

### "Port already in use" on startup

```bash
$ sudo ss -tlnp | grep :3000
LISTEN  0  511  0.0.0.0:3000  0.0.0.0:*  users:(("node",pid=7890,fd=22))

$ kill 7890
```

### Check if a remote port is reachable

`netstat` and `ss` only show local sockets. For remote connectivity, use:

```bash
$ nc -zv db.internal 5432
Connection to db.internal (10.0.0.5) 5432 port [tcp/postgresql] succeeded!
```

Or with timeout:

```bash
$ timeout 3 bash -c 'cat < /dev/null > /dev/tcp/db.internal/5432' && echo "open" || echo "closed"
open
```

### Monitor connections to a service in real time

```bash
$ watch -n 1 'ss -tn state established | grep :443 | wc -l'
```

### Find the process behind an established connection

```bash
$ sudo ss -tnp state established
Recv-Q  Send-Q  Local Address:Port   Peer Address:Port  Process
0       0       10.0.0.5:41234       34.107.221.82:443  users:(("curl",pid=12345,fd=5))
```

## netstat vs ss — Quick Comparison

| | `netstat` | `ss` |
|---|---|---|
| Speed | Slower (reads `/proc`) | Faster (kernel netlink) |
| Available | Linux, macOS, BSD | Linux only |
| State filtering | Limited | Rich |
| Default install | No (removed from many distros) | Yes |
| Flags | `-tlnp` style | Same, plus filter expressions |

On Linux, prefer `ss`. On macOS, `netstat` is your only option (or install `lsof`).

## Conclusion

The two commands worth memorizing are `sudo ss -tlnp` (listening TCP sockets with process info) and `sudo ss -tn state established` (active connections). Everything else is layered on top. When a port isn't responding as expected, these tools give you the ground truth in seconds — what's bound, what's connected, and which process owns it.
