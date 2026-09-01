---
layout: post
title: "Wireshark for Developers: Reading and Debugging Network Traffic"
date: "2026-09-02 00:00:00 +0530"
slug: wireshark-for-developers
description: "A practical guide to using Wireshark to debug network issues, covering capture filters, display filters, the TCP handshake, and inspecting TLS and HTTP traffic."
categories: ["wiki", "Tutorials"]
tags: ["wireshark", "networking", "packet capture", "debugging", "tcp", "http", "tls", "pcap", "network analysis", "troubleshooting"]
---

When application logs say "connection refused" or "timeout" and give you nothing else to go on, the actual truth about what happened is sitting on the wire — the literal bytes exchanged between two machines. Wireshark captures and decodes that traffic, turning an opaque network failure into a readable sequence of packets you can actually reason about. This post covers the practical parts: filtering out noise, reading a TCP handshake, and inspecting HTTP and TLS traffic to figure out where a connection actually broke.

## Capture Filters vs Display Filters

Wireshark has two entirely different filtering mechanisms that get confused constantly, and knowing which one to use where matters:

**Capture filters** are applied *before* packets are even recorded — using Berkeley Packet Filter (BPF) syntax, the same syntax `tcpdump` uses. They reduce what gets written to the capture in the first place, which matters for high-traffic interfaces where capturing everything would produce an unmanageably large file.

```bash
$ tshark -i eth0 -f "host 203.0.113.5 and port 443"
```

**Display filters** are applied *after* capture, to a full (or already-filtered) capture, to control what's shown in the UI. They use Wireshark's own, much richer filter syntax, and can be changed and re-applied without recapturing anything.

```
tcp.port == 443 && ip.addr == 203.0.113.5
```

The practical rule: use a broad capture filter to keep the file size reasonable (or none at all for a short debugging session), then use display filters — which you can change repeatedly, for free, without recapturing — to actually narrow down what you're looking at.

## Essential Display Filters

A handful of filters cover the vast majority of real debugging sessions:

```
# Traffic to/from a specific host
ip.addr == 203.0.113.5

# A specific TCP port
tcp.port == 443

# Only HTTP requests (not all TCP traffic on port 80)
http.request

# TCP handshake and teardown packets only
tcp.flags.syn == 1 || tcp.flags.fin == 1

# Retransmissions — a strong signal of packet loss or a struggling connection
tcp.analysis.retransmission

# DNS queries and responses
dns

# Any packet containing a specific string in its payload
frame contains "error"
```

```bash
$ tshark -r capture.pcap -Y "tcp.analysis.retransmission" -T fields -e frame.time -e ip.src -e ip.dst
2026-09-02 10:15:03.421  10.0.1.20   93.184.216.34
2026-09-02 10:15:03.892  10.0.1.20   93.184.216.34
```

`tcp.analysis.retransmission` is worth calling out specifically — Wireshark computes this itself by noticing a TCP segment being sent again with the same sequence number, and it's one of the fastest ways to confirm "this isn't an application bug, the network is actually dropping packets" versus chasing a phantom bug in application code for a problem that's really happening at the transport layer.

## Reading the TCP Three-Way Handshake

Every TCP connection starts with a recognizable pattern, and being able to read it directly from a capture is a foundational skill:

```
No.  Time     Source          Destination     Protocol  Info
1    0.000    10.0.1.20       93.184.216.34   TCP       51200 -> 443 [SYN] Seq=0
2    0.023    93.184.216.34   10.0.1.20       TCP       443 -> 51200 [SYN, ACK] Seq=0 Ack=1
3    0.023    10.0.1.20       93.184.216.34   TCP       51200 -> 443 [ACK] Seq=1 Ack=1
```

`SYN` — the client proposes a connection. `SYN, ACK` — the server acknowledges and proposes its own sequence number back. `ACK` — the client confirms, and the connection is now established. If step 1 appears in a capture but step 2 never arrives, that's a strong, specific signal: either the destination is unreachable, a firewall is silently dropping the packet (not rejecting it, which would send a `RST` back — just dropping it), or the service isn't actually listening on that port at all.

```
No.  Time     Source          Destination     Protocol  Info
1    0.000    10.0.1.20       93.184.216.34   TCP       51200 -> 443 [SYN] Seq=0
2    3.000    10.0.1.20       93.184.216.34   TCP       51200 -> 443 [SYN] Seq=0  (retransmission)
3    9.000    10.0.1.20       93.184.216.34   TCP       51200 -> 443 [SYN] Seq=0  (retransmission)
```

This pattern — a `SYN` sent repeatedly with growing gaps between retries, and never a response — is the exact fingerprint of a connection that's timing out at the network level, as distinct from a connection that connects fine but then hangs waiting on an application-layer response. Distinguishing these two failure modes from application logs alone is often impossible; from a packet capture, it's immediate.

## Following a TCP Stream

Rather than reading individual packets, Wireshark can reassemble an entire TCP conversation into its logical order — right-click any packet in a connection and choose "Follow > TCP Stream":

```
GET /api/orders/42 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...

HTTP/1.1 500 Internal Server Error
Content-Type: application/json
Content-Length: 87

{"error": "database connection timeout", "request_id": "req_9f8e7d"}
```

This reconstructed view is usually more useful than the packet-by-packet view for debugging application-layer issues — it's essentially what `curl -v` would have shown you, but reconstructed after the fact from a capture, which matters when you're debugging a failure you can't easily reproduce on demand (a customer-reported issue, an intermittent problem) rather than one you're actively triggering yourself.

## Inspecting TLS: What You Can and Can't See

By default, a capture of TLS traffic shows you the handshake in full detail (ClientHello, ServerHello, certificate exchange — all unencrypted, since the handshake itself has to be) but the actual application data is encrypted and unreadable, as it should be.

```
No.  Protocol  Info
1    TLSv1.3   Client Hello
2    TLSv1.3   Server Hello, Certificate, Certificate Verify, Finished
3    TLSv1.3   Finished
4    TLSv1.3   Application Data  (encrypted, not human-readable)
```

For debugging purposes — never for intercepting someone else's traffic without consent — you can decrypt your own TLS traffic by pointing Wireshark at a **TLS key log file**, which most browsers and some HTTP clients will write to if the `SSLKEYLOGFILE` environment variable is set:

```bash
$ export SSLKEYLOGFILE=~/tls-keys.log
$ google-chrome  # or curl, or any client respecting this env var
```

```
Edit > Preferences > Protocols > TLS > (Pre)-Master-Secret log filename: ~/tls-keys.log
```

With the key log loaded, Wireshark can decrypt the session for display purposes, letting you inspect the actual HTTP request/response inside a TLS-encrypted capture — genuinely useful for debugging your own application's HTTPS traffic, and only possible because you legitimately have access to the session keys involved, not because TLS itself has been broken.

## A Practical Debugging Sequence

A reasonable general approach when facing an unexplained network issue:

1. **Capture with a broad filter** on the relevant host/port, reproduce the issue, stop the capture.
2. **Check for a completed TCP handshake.** No `SYN,ACK` at all points at connectivity/firewall/routing; a handshake that completes but then nothing else happens points higher up the stack.
3. **Check for retransmissions** (`tcp.analysis.retransmission`) — present retransmissions point at packet loss or an overloaded link, not an application bug.
4. **Follow the stream** for the actual request/response content, if unencrypted or decryptable via a key log.
5. **Check timing between packets** — a large gap between a request being sent and a response arriving points at slow server-side processing, not a network problem at all, which redirects the investigation toward application code and away from the network layer entirely.

## Conclusion

Wireshark's real value for a developer isn't packet-level networking arcana — it's that it turns "the connection failed" from a vague symptom into a specific, visible fact: did the handshake even complete, was there retransmission, did a response come back at the transport layer but the application returned an error. Capture filters keep captures manageable, display filters let you narrow down after the fact for free, and following a TCP stream reconstructs the actual conversation into something as readable as `curl -v` output — the difference being you can capture it once and inspect it as many ways as you need, including after the fact, for an issue you can't easily reproduce on demand.
