---
layout: post
title: "IP Subnetting and CIDR Notation: A Practical Guide"
date: "2026-09-02 00:00:00 +0530"
slug: ip-subnetting-cidr-notation-guide
description: "A practical guide to IP subnetting and CIDR notation, covering how to calculate subnet ranges, netmasks, and how to size subnets for a VPC or network."
categories: ["wiki"]
tags: ["subnetting", "cidr", "ip addressing", "networking", "ipv4", "netmask", "vpc", "devops", "linux", "sysadmin"]
---

Every time you set up a VPC, configure a firewall rule, or debug why two machines on "the same network" can't actually reach each other, you're working with subnetting whether you think about it explicitly or not. CIDR notation (`10.0.1.0/24`) is the compact way of expressing an IP address range, and once the math behind it clicks, reading and designing network layouts stops being guesswork. This post walks through what the `/24` actually means, how to calculate ranges by hand, and how to size subnets deliberately instead of copy-pasting `/24` everywhere out of habit.

## What an IP Address and a Netmask Actually Are

An IPv4 address is 32 bits, conventionally written as four decimal octets: `192.168.1.10`. A **netmask** (or its CIDR shorthand, the `/n` suffix) splits those 32 bits into two parts: a **network portion** (identifies which subnet an address belongs to) and a **host portion** (identifies a specific machine within that subnet).

```
192.168.1.10/24
      |
      +-- /24 means: the first 24 bits are the network portion,
          the remaining 8 bits identify the host

Binary:  11000000.10101000.00000001.00001010
         |------ network (24 bits) ------|--host (8 bits)--|
         192   . 168   . 1     .          10
```

A `/24` netmask in dotted-decimal form is `255.255.255.0` — each `255` represents 8 bits fully allocated to the network portion, and `0` represents 8 bits available for hosts. The CIDR number and the dotted-decimal netmask are two notations for the exact same information; CIDR is just faster to write and reason about.

## Reading a CIDR Block

Given `10.0.1.0/24`, here's what you can derive immediately, without a calculator:

```
Network address:    10.0.1.0     (all host bits = 0, identifies the subnet itself)
Broadcast address:  10.0.1.255   (all host bits = 1, reserved for subnet-wide broadcast)
Usable host range:  10.0.1.1 - 10.0.1.254
Total addresses:    256  (2^8, since 8 bits are host bits)
Usable addresses:   254  (256 minus network address minus broadcast address)
```

The general formula: a `/n` prefix leaves `32 - n` bits for hosts, giving `2^(32-n)` total addresses in that block, and typically `2^(32-n) - 2` usable host addresses (subtracting the network and broadcast addresses, which aren't assignable to individual hosts).

```bash
$ ipcalc 10.0.1.0/24
Address:   10.0.1.0
Netmask:   255.255.255.0 = 24
Network:   10.0.1.0/24
HostMin:   10.0.1.1
HostMax:   10.0.1.254
Broadcast: 10.0.1.255
Hosts/Net: 254
```

## The Prefix-to-Host-Count Table

Rather than recomputing `2^(32-n)` every time, it's worth memorizing the shape of this table for the prefixes that come up constantly in practice:

| CIDR | Netmask | Total addresses | Usable hosts |
|---|---|---|---|
| /32 | 255.255.255.255 | 1 | 1 (a single host route) |
| /30 | 255.255.255.252 | 4 | 2 (common for point-to-point links) |
| /29 | 255.255.255.248 | 8 | 6 |
| /28 | 255.255.255.240 | 16 | 14 |
| /27 | 255.255.255.224 | 32 | 30 |
| /26 | 255.255.255.192 | 64 | 62 |
| /25 | 255.255.255.128 | 128 | 126 |
| /24 | 255.255.255.0 | 256 | 254 |
| /23 | 255.255.254.0 | 512 | 510 |
| /16 | 255.255.0.0 | 65,536 | 65,534 |

The pattern: **each step down by 1 in the prefix number doubles the block size.** Going from `/24` to `/23` doesn't add 1 host — it doubles the entire block from 256 to 512 addresses. This is the single most useful mental model for subnetting: think in powers of two, not linear increments.

## Splitting a Block Into Subnets

Say you're handed `10.0.0.0/16` (65,536 addresses) and need to split it into four equally-sized subnets for four different environments (dev, staging, prod, shared services). Each split moves the prefix number up by however many bits are needed to divide the space into that many pieces — splitting into 4 pieces needs 2 extra bits (`2^2 = 4`), so `/16` becomes `/18`:

```
10.0.0.0/16  split into 4x /18 blocks:

10.0.0.0/18    -> 10.0.0.0   - 10.0.63.255   (16,384 addresses) - dev
10.0.64.0/18   -> 10.0.64.0  - 10.0.127.255  (16,384 addresses) - staging
10.0.128.0/18  -> 10.0.128.0 - 10.0.191.255  (16,384 addresses) - prod
10.0.192.0/18  -> 10.0.192.0 - 10.0.255.255  (16,384 addresses) - shared services
```

```bash
$ ipcalc 10.0.64.0/18
Address:   10.0.64.0
Netmask:   255.255.192.0 = 18
Network:   10.0.64.0/18
HostMin:   10.0.64.1
HostMax:   10.0.127.254
Broadcast: 10.0.127.255
Hosts/Net: 16382
```

Each subnet's starting address is a multiple of its block size — `/18` blocks are 16,384 addresses wide, so valid starting points are `.0`, `.64.0`, `.128.0`, `.192.0` in the third octet's relevant bit boundary, never an arbitrary offset. This alignment requirement is why subnetting tools flag "invalid" subnets that look fine at a glance but don't actually start on a block boundary — a `/18` block can't start at `10.0.30.0`, because that's not a multiple of 64 in the relevant octet position.

## Sizing Subnets in Practice (VPC Design)

The practical mistake to avoid: sizing every subnet as `/24` out of habit, regardless of what actually needs to live in it. A `/24` giving 254 usable addresses is enormous for a subnet that will only ever host 3 NAT gateways, and cripplingly small for one expected to autoscale to thousands of container IPs.

A more deliberate approach sizes each subnet to its actual expected population, with headroom for growth but not wild overallocation:

```
VPC: 10.0.0.0/16

10.0.0.0/24    - public subnet (NAT gateways, load balancers)     - 254 addresses
10.0.1.0/24    - management subnet (bastion, admin tooling)       - 254 addresses
10.0.16.0/20   - application subnet (autoscaling compute)       - 4,094 addresses
10.0.32.0/20   - database subnet (RDS instances, replicas)      - 4,094 addresses
```

Note the gap between `10.0.1.0/24` and `10.0.16.0/20` — deliberately leaving unallocated space between subnets is common practice, because it lets a subnet grow (by re-carving from the unused space, or being resized before anything is deployed into the neighboring range) without immediately colliding with the next subnet's address range. Packing subnets edge-to-edge with zero headroom is the kind of decision that looks tidy on day one and becomes a costly re-architecture the first time a subnet needs to grow.

## A Worked Example: "Does This Address Belong to This Subnet?"

A question that comes up constantly when debugging connectivity: given `172.16.5.130`, does it belong to `172.16.5.128/26`?

```
Netmask for /26:  255.255.255.192   (binary: 11000000 in the last octet)

172.16.5.128  -> last octet: 10000000
172.16.5.130  -> last octet: 10000010

AND each address with the netmask's last octet (11000000):
172.16.5.128 & 11000000 = 10000000  (128)
172.16.5.130 & 11000000 = 10000000  (128)

Both resolve to network address 172.16.5.128 -> yes, .130 is inside this /26.
```

The mechanical process is always the same: bitwise-AND the address with the netmask, and compare the result to the subnet's network address. If they match, the address is inside that subnet — this is exactly the check a router performs on every packet to decide whether a destination is on a locally-connected subnet or needs to be forwarded elsewhere.

```bash
$ ipcalc 172.16.5.130/26
Address:   172.16.5.130
Network:   172.16.5.128/26
HostMin:   172.16.5.129
HostMax:   172.16.5.190
Broadcast: 172.16.5.191
```

## Conclusion

CIDR notation compresses "network range" and "how many hosts fit here" into one small suffix, and once the powers-of-two relationship between prefix length and block size clicks, subnetting stops requiring a calculator for anything but the least common cases. The practical skill worth building isn't memorizing every prefix's exact host count — it's sizing subnets deliberately for their actual expected population, leaving growth headroom between allocations instead of packing them edge-to-edge, and being able to quickly answer "does this address belong to this subnet" when debugging why two machines that seem like they should reach each other, can't.
