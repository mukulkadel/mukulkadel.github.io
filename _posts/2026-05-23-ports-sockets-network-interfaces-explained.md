---
layout: post
title: "Understanding Ports, Sockets, and Network Interfaces"
date: "2026-05-23 00:00:00 +0530"
slug: ports-sockets-network-interfaces-explained
description: "A clear explanation of how ports, sockets, and network interfaces work together — covering IP binding, common port numbers, and how to inspect network state with ss and lsof."
categories: ["wiki"]
tags: ["ports", "sockets", "networking", "linux", "unix", "tcp", "ip", "devops", "sysadmin", "firewall", "binding", "lsof", "ss"]
---

When your server says "address already in use" or your firewall blocks an unexpected port, the root cause usually traces back to a misunderstanding of ports, sockets, and network interfaces. These three concepts are the foundation of every networked application, and you'll debug problems much faster once the model is clear in your head.

## IP Addresses and Network Interfaces

A network interface is a point of connection between a computer and a network — physical (an Ethernet card) or virtual (a loopback device, a tunnel). Each interface has an IP address.

```bash
$ ip addr show

1: lo: <LOOPBACK,UP,LOWER_UP>
    inet 127.0.0.1/8 scope host lo          # loopback — only accessible locally

2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    inet 10.0.0.5/24 scope global eth0      # private IP (AWS, VPC)
    inet 203.0.113.42/32 scope global eth0  # public IP (if directly assigned)
```

On a cloud instance you typically see:
- `lo` — loopback (`127.0.0.1`) — packets never leave the machine
- `eth0` / `ens3` / `enp0s3` — the main network interface

A server process **binds** to an IP address and port. The combination of IP + port uniquely identifies where it listens.

## Ports: What They Are and Who Assigns Them

A port is a 16-bit number (0–65535) that identifies a specific service or application on a host. The IP address routes packets to the right machine; the port delivers them to the right process.

Port ranges:

| Range | Name | Who uses it |
|---|---|---|
| 0–1023 | Well-known ports | System services (requires root to bind) |
| 1024–49151 | Registered ports | Application-layer services |
| 49152–65535 | Ephemeral ports | Kernel-assigned client ports |

When your browser connects to a server, it uses a random ephemeral port as the source, and connects to port 80 or 443 on the server. The server can distinguish thousands of simultaneous browser connections because each connection has a unique source IP + source port combination.

### Common Port Numbers

| Port | Protocol | Service |
|---|---|---|
| 22 | TCP | SSH |
| 25 | TCP | SMTP |
| 53 | TCP/UDP | DNS |
| 80 | TCP | HTTP |
| 443 | TCP | HTTPS |
| 3306 | TCP | MySQL |
| 5432 | TCP | PostgreSQL |
| 6379 | TCP | Redis |
| 8080 | TCP | HTTP alt (dev servers) |
| 27017 | TCP | MongoDB |

## Sockets: Putting It Together

A socket is the software abstraction that combines an IP address, a port, and a protocol into a communication endpoint. A TCP connection is uniquely identified by a 4-tuple:

```
(source IP, source port, destination IP, destination port)
```

This is why a server can handle thousands of simultaneous connections on port 443 — each connection has a different source IP/port, making each 4-tuple unique.

```
Client 1: (203.0.113.10:52341, 93.184.216.34:443)
Client 2: (203.0.113.10:52342, 93.184.216.34:443)
Client 3: (172.16.5.8:63211,   93.184.216.34:443)
```

All three connections are to the same server port, but they're distinct sockets.

## Binding: Listening on an Address

When you start a web server and it "listens on port 3000," it's creating a socket and calling `bind()` on that port. The bind address controls which network interface the server accepts connections on.

### Binding to `0.0.0.0` vs a Specific IP

```
0.0.0.0:3000    → accepts connections on ALL interfaces
127.0.0.1:3000  → accepts connections ONLY from localhost
10.0.0.5:3000   → accepts connections ONLY on the eth0 interface
```

This is security-relevant: a database or internal service should bind to `127.0.0.1`, not `0.0.0.0`. Binding to `0.0.0.0` exposes the service on every interface, including the public-facing one.

In your application:

```python
# Python — restrict to localhost
server.bind(('127.0.0.1', 3000))

# Python — accept connections on all interfaces
server.bind(('0.0.0.0', 3000))
```

```bash
# Check what a service is bound to
$ ss -tlnp | grep 3000
LISTEN  0  128  127.0.0.1:3000   0.0.0.0:*   users:(("node",pid=12345,fd=21))
```

## Checking What's Listening

```bash
# List all listening TCP sockets with process names
$ ss -tlnp
State    Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
LISTEN   0       128     0.0.0.0:80          0.0.0.0:*          users:(("nginx",pid=1234))
LISTEN   0       128     127.0.0.1:5432      0.0.0.0:*          users:(("postgres",pid=5678))

# Same with lsof
$ lsof -i TCP -s TCP:LISTEN

# Find what's using port 8080
$ ss -tlnp | grep :8080
$ lsof -i :8080

# Show all established connections
$ ss -tnp
```

## "Address Already in Use"

This error means another process is already bound to that port. Track it down:

```bash
$ lsof -i :3000
COMMAND   PID     USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
node    12345   ubuntu  21u  IPv4   98765      0t0  TCP 127.0.0.1:3000 (LISTEN)

# Kill the offending process
$ kill 12345
```

Sometimes the port is held by a socket in `TIME_WAIT` state from a recently closed connection. You can bypass this (during development only) with `SO_REUSEADDR`:

```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 3000))
```

## Basic Firewall with `ufw`

Ports that are open on your process must also be allowed through the firewall:

```bash
# Allow HTTP and HTTPS
$ sudo ufw allow 80/tcp
$ sudo ufw allow 443/tcp

# Allow SSH (before enabling ufw!)
$ sudo ufw allow 22/tcp

$ sudo ufw enable
$ sudo ufw status
Status: active
To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

## Conclusion

IP addresses identify machines, ports identify services on those machines, and sockets are the runtime instances that tie the two together for a specific connection. When you bind to `0.0.0.0`, you expose a service on every interface — bind to `127.0.0.1` for anything that shouldn't be reachable from outside the machine. Use `ss -tlnp` to see exactly what's listening where, and `lsof -i :PORT` to find what owns a specific port when you get "address already in use."
