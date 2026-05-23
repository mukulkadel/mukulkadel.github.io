---
layout: post
title: "TCP vs UDP: When Each Protocol Matters"
date: "2026-05-23 00:00:00 +0530"
slug: tcp-vs-udp-explained
description: "A practical explanation of TCP vs UDP — how each protocol works, their trade-offs, real-world use cases, and when to choose which for your application."
categories: ["wiki"]
tags: ["tcp", "udp", "networking", "protocol", "linux", "sockets", "web", "streaming", "devops", "quic", "network programming"]
---

Every network connection your application makes uses either TCP or UDP under the hood. Most developers default to TCP without thinking about it — and for most use cases, that's correct. But understanding why TCP is reliable and UDP isn't, and what that reliability actually costs, explains a lot of surprising behavior in network applications and informs smarter architectural decisions.

## TCP: Reliability at a Cost

TCP (Transmission Control Protocol) guarantees three things:

1. **Delivery** — every byte sent will be received, or the connection will error
2. **Order** — bytes arrive in the same order they were sent
3. **No duplication** — each byte arrives exactly once

It achieves this through acknowledgments, retransmission, and sequencing. Every segment the sender transmits must be acknowledged by the receiver. If an ACK doesn't arrive within a timeout window, the segment is retransmitted.

### The Three-Way Handshake

Before any data is exchanged, TCP establishes a connection:

```
Client                Server
  |--- SYN ----------->|   "I want to connect, my seq starts at X"
  |<-- SYN-ACK --------|   "OK, my seq starts at Y, acknowledging X+1"
  |--- ACK ----------->|   "Acknowledging Y+1"
  |                    |
  |=== data flows ====>|
```

This handshake adds at least one round trip before data can flow. On a 100ms latency connection, that's 100ms of setup time before your first byte.

### TCP Teardown

Closing a TCP connection is a four-way process (FIN-ACK-FIN-ACK), and sockets linger in `TIME_WAIT` for 2× the maximum segment lifetime (typically 2 minutes) after close. This is why a server with thousands of short-lived connections can exhaust its port space.

### What TCP Costs

- **Latency**: handshake before data, retransmission on loss
- **Head-of-line blocking**: a lost packet blocks all subsequent data until retransmitted
- **Connection state**: both sides must maintain state
- **CPU**: checksum verification, ACK processing, congestion control

## UDP: Fast and Unreliable

UDP (User Datagram Protocol) does almost nothing. It adds source/destination ports and a checksum to your data and sends it. That's it.

- No connection establishment
- No delivery guarantees
- No ordering guarantees
- No duplicate prevention

A UDP packet either arrives or it doesn't, in whatever order the network delivers it, potentially more than once.

### Why Would You Want That?

Because removing guarantees removes overhead. UDP packets have no handshake latency, no retransmission delay, no head-of-line blocking. When speed matters more than completeness — or when your application can handle lost packets better than the OS can — UDP wins.

## Real-World Protocol Choices

### DNS — UDP (with TCP fallback)

DNS uses UDP by default. A DNS query and response are tiny (typically under 512 bytes) and fit in one packet. The client can retransmit the query itself if no response arrives — faster and simpler than TCP setup. Large responses fall back to TCP automatically.

```bash
$ dig example.com
;; Query time: 12 msec
;; SERVER: 8.8.8.8#53(8.8.8.8) (UDP)
```

### HTTP/1.1, HTTP/2 — TCP

HTTP requires reliable delivery. A missing packet in the middle of an HTML response would corrupt the page. TCP's guarantees are worth the overhead here.

### HTTP/3 — QUIC (UDP-based)

HTTP/3 runs over QUIC, which is built on UDP. QUIC re-implements reliability at the application layer, per-stream. A lost packet only blocks its own stream — not all other streams on the connection. This eliminates TCP's head-of-line blocking while keeping the delivery guarantees HTTP needs.

### Video Streaming (Netflix, YouTube) — TCP

Counter-intuitively, most streaming services use TCP. Buffering compensates for retransmission delays, and reliable delivery is better than gaps in the video. The buffer absorbs the jitter.

### Live Video/Audio (Zoom, WebRTC, VoIP) — UDP (RTP)

Real-time audio and video can't buffer. A 200ms audio gap is better played as silence than waited on — the retransmitted packet would arrive too late to be useful. WebRTC uses SRTP over UDP. Zoom uses a custom UDP protocol. VoIP runs RTP over UDP.

### Online Multiplayer Games — UDP

Position updates in a game have no value once they're stale. If a packet containing "player is at position X" is lost, the next packet "player is at position Y" supersedes it. Retransmitting the old position data is pointless and adds latency. Games send position data over UDP and use TCP only for reliable events (game state changes, chat).

### DHCP, SNMP, TFTP — UDP

Protocols that run before a network is fully configured, or on constrained devices, use UDP because it's simpler to implement and requires no connection state.

## Checking Protocol Usage with `ss`

```bash
# Show TCP connections
$ ss -tnp

# Show UDP connections (note: UDP is connectionless, so no ESTABLISHED state)
$ ss -unp

# Show all connections with more detail
$ ss -tunap
Netid  State   Recv-Q Send-Q  Local Address:Port  Peer Address:Port
tcp    ESTAB   0      0       10.0.0.1:443        93.184.216.34:52341
udp    UNCONN  0      0       0.0.0.0:53          0.0.0.0:*        users:(("dnsmasq",pid=812))
```

## Quick Reference

| | TCP | UDP |
|---|---|---|
| Connection | Yes (3-way handshake) | No |
| Reliable delivery | Yes | No |
| Ordered | Yes | No |
| No duplication | Yes | No |
| Speed | Slower (overhead) | Faster |
| Head-of-line blocking | Yes | No |
| Congestion control | Yes | No |
| Typical use | HTTP, SSH, databases, email | DNS, VoIP, gaming, streaming |

## Conclusion

Choose TCP when your application cannot tolerate data loss or corruption: HTTP, database connections, file transfers, SSH. Choose UDP when your application needs low latency and can handle loss better than the OS can via retransmission: live audio/video, online games, DNS. QUIC (HTTP/3) is the interesting middle ground — it builds per-stream reliability on top of UDP, offering TCP's delivery guarantees without TCP's head-of-line blocking. If you're designing a new protocol, consider QUIC rather than building your own reliability layer on raw UDP.
