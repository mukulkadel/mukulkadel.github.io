---
layout: post
title: "ssh — Complete Guide: Keys, Config, Tunnels, and Agent Forwarding"
date: "2026-05-23 00:00:00 +0530"
slug: ssh-complete-guide
description: "A thorough SSH reference covering key generation, ssh-agent, the client config file, port forwarding, jump hosts, and agent forwarding with real examples."
categories: ["wiki", "Programming", "unix"]
tags: ["ssh", "unix", "linux", "security", "keys", "tunneling", "devops", "networking", "remote access"]
---

SSH is the backbone of remote development and server administration, but most developers only ever use `ssh user@host` and call it a day. The full toolkit — key management, the client config, port forwarding, and jump hosts — can turn a clunky multi-step workflow into a single command. This guide covers all of it.

## Key Generation

Prefer `ed25519` for new keys — it's faster and more secure than the legacy `rsa` default:

```bash
$ ssh-keygen -t ed25519 -C "your_email@example.com"
Generating public/private ed25519 key pair.
Enter file in which to save the key (/Users/mukul/.ssh/id_ed25519):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /Users/mukul/.ssh/id_ed25519
Your public key has been saved in /Users/mukul/.ssh/id_ed25519.pub
```

The `-C` comment is just a label — it ends up in the `.pub` file and helps you identify the key later.

If you need RSA for compatibility with older systems, use at least 4096 bits:

```bash
$ ssh-keygen -t rsa -b 4096 -C "legacy-server"
```

### Copying Your Public Key to a Server

```bash
$ ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server.example.com
```

This appends your public key to `~/.ssh/authorized_keys` on the remote host. Equivalent manual step:

```bash
$ cat ~/.ssh/id_ed25519.pub | ssh user@server.example.com "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

## ssh-agent: Managing Keys in Memory

`ssh-agent` holds decrypted private keys in memory so you don't type your passphrase on every connection.

Start the agent and add your key:

```bash
$ eval "$(ssh-agent -s)"
Agent pid 12345

$ ssh-add ~/.ssh/id_ed25519
Enter passphrase for /Users/mukul/.ssh/id_ed25519:
Identity added: /Users/mukul/.ssh/id_ed25519 (your_email@example.com)
```

List currently loaded keys:

```bash
$ ssh-add -l
256 SHA256:abc123... your_email@example.com (ED25519)
```

On macOS, add this to `~/.ssh/config` to have the agent auto-start and remember keys across reboots:

```
Host *
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
```

## The SSH Client Config: `~/.ssh/config`

The config file is where SSH becomes genuinely powerful. Instead of typing long flags, you define named hosts:

```
Host myserver
  HostName 192.168.1.100
  User deploy
  Port 2222
  IdentityFile ~/.ssh/id_ed25519

Host bastion
  HostName bastion.prod.example.com
  User ec2-user
  IdentityFile ~/.ssh/prod_key
```

With this config, `ssh myserver` is equivalent to:

```bash
$ ssh -i ~/.ssh/id_ed25519 -p 2222 deploy@192.168.1.100
```

### Useful Config Options

| Option | What it does |
|---|---|
| `HostName` | The actual hostname or IP |
| `User` | Default username |
| `Port` | Non-standard port |
| `IdentityFile` | Which private key to use |
| `ForwardAgent` | Enable agent forwarding |
| `ServerAliveInterval` | Send keepalive packets every N seconds |
| `ServerAliveCountMax` | Disconnect after N missed keepalives |
| `StrictHostKeyChecking no` | Skip host key verification (use sparingly) |
| `ProxyJump` | Route through a jump host |

A `Host *` block at the bottom sets defaults for all connections:

```
Host *
  ServerAliveInterval 60
  ServerAliveCountMax 3
  AddKeysToAgent yes
```

## Port Forwarding (Tunneling)

SSH tunnels let you securely forward traffic between local and remote ports. There are three types.

### Local Forwarding (`-L`)

Forward a local port to a remote destination. Classic use: accessing a database that's only accessible from within a private network.

```bash
$ ssh -L 5432:db.internal:5432 user@bastion.example.com
```

Now `localhost:5432` on your machine connects to `db.internal:5432` via the bastion. Your Postgres client points to `localhost` and never touches the internet directly.

General form: `-L local_port:destination_host:destination_port`

### Remote Forwarding (`-R`)

Forward a port on the *remote* server back to your local machine. Useful for exposing a local dev server through a public-facing host:

```bash
$ ssh -R 8080:localhost:3000 user@publicserver.com
```

Now `publicserver.com:8080` routes to port 3000 on your laptop.

### Dynamic Forwarding / SOCKS Proxy (`-D`)

Turns the SSH connection into a SOCKS5 proxy. Any application that supports SOCKS can route all traffic through it:

```bash
$ ssh -D 1080 user@jumpserver.com
```

Then configure your browser to use `localhost:1080` as a SOCKS5 proxy.

### Keeping Tunnels Open

Add `-N` (don't execute a command) and `-f` (go to background):

```bash
$ ssh -N -f -L 5432:db.internal:5432 user@bastion.example.com
```

## Jump Hosts (Bastion Servers)

Accessing a server that's not directly reachable from the internet via a bastion:

```bash
$ ssh -J user@bastion.example.com user@private-host.internal
```

In `~/.ssh/config`, this is cleaner:

```
Host private-host
  HostName private-host.internal
  User user
  ProxyJump bastion

Host bastion
  HostName bastion.example.com
  User ec2-user
  IdentityFile ~/.ssh/prod_key
```

Now `ssh private-host` transparently hops through the bastion.

For nested jumps (bastion → intermediate → target):

```
ProxyJump bastion,intermediate
```

## Agent Forwarding

When you SSH to a bastion and then need to SSH onward to another host, agent forwarding lets the second host use the keys stored in your local `ssh-agent` — without ever copying your private key onto the bastion.

Enable per-connection:

```bash
$ ssh -A user@bastion.example.com
```

Or in config:

```
Host bastion
  ForwardAgent yes
```

**Important:** only enable `ForwardAgent` on hosts you fully trust. A compromised server with your agent forwarded can authenticate as you to any other host your agent has access to.

## Hardening the Server Side

These go in `/etc/ssh/sshd_config` on the server:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
MaxAuthTries 3
AllowUsers deploy ec2-user
```

After changing `sshd_config`, reload without dropping existing connections:

```bash
$ sudo systemctl reload sshd
```

## Useful One-Liners

**Copy a file from remote to local:**

```bash
$ scp user@server:/var/log/app.log ./app.log
```

**Copy a directory recursively:**

```bash
$ scp -r user@server:/opt/backups/ ./backups/
```

**Run a single command on a remote host without a shell:**

```bash
$ ssh user@server "df -h && free -m"
```

**Escape a hung session:** If the connection freezes, type `Enter ~ .` (tilde then dot) to kill it.

**Check what's authorized on a remote server:**

```bash
$ ssh user@server "cat ~/.ssh/authorized_keys"
```

## Conclusion

Most SSH friction comes from typing the same options repeatedly and managing keys manually. A well-structured `~/.ssh/config` eliminates that — you name your hosts, set their keys and ports once, and never think about it again. Tunnels and jump hosts extend that to networks that would otherwise require a VPN or a cumbersome multi-hop dance. Spend an hour setting this up and you'll save it back within a week.
