---
layout: post
title: "SSH Key Management Best Practices"
date: "2026-05-26 00:00:00 +0530"
slug: ssh-key-management-best-practices
description: "A practical guide to SSH key management — generating strong keys, using ssh-agent, organizing multiple keys, rotating credentials, and securing GitHub access."
categories: ["wiki", "unix"]
tags: ["ssh", "keys", "security", "ed25519", "rsa", "github", "devops", "linux", "macos", "best practices"]
---

SSH keys are the foundation of secure access for most developers — servers, GitHub, deployment pipelines, CI systems. But generating a key and pasting it somewhere is only half the story. Poor key hygiene — sharing keys, reusing them across contexts, never rotating them, leaving them without passphrases — turns a strong security mechanism into a liability.

## Key Types: Ed25519 vs RSA

For new keys, always use **Ed25519**. It's based on modern elliptic-curve cryptography, produces smaller keys, and is faster than RSA while being equally or more secure at comparable key lengths.

```bash
# Generate an Ed25519 key — the modern default
$ ssh-keygen -t ed25519 -C "your@email.com"
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/user/.ssh/id_ed25519):
Enter passphrase (empty for no passphrase): ****
Enter same passphrase again: ****
Your identification has been saved in /home/user/.ssh/id_ed25519
Your public key has been saved in /home/user/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:AbCdEf1234567890AbCdEf1234567890AbCdEf12345 your@email.com
```

If you must use RSA for legacy systems that don't support Ed25519, use at least 4096 bits:

```bash
$ ssh-keygen -t rsa -b 4096 -C "your@email.com"
```

**Always set a passphrase.** A passphrase encrypts your private key on disk — if someone steals your laptop or the key file, they still can't use it without the passphrase. Use `ssh-agent` so you only type it once per session.

## Organizing Multiple Keys

Most developers eventually accumulate keys for different contexts: personal GitHub, work GitHub, multiple servers, deployment accounts. Keep them organized:

```
~/.ssh/
├── config                    # Connection routing rules
├── id_ed25519                # Default personal key
├── id_ed25519.pub
├── work_github               # Work GitHub key
├── work_github.pub
├── prod_server               # Production server key
├── prod_server.pub
└── known_hosts
```

The `~/.ssh/config` file maps hosts to keys so you never need to specify `-i`:

```
# Personal GitHub
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

# Work GitHub account
Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/work_github
    IdentitiesOnly yes

# Production server
Host prod
    HostName 203.0.113.10
    User deploy
    IdentityFile ~/.ssh/prod_server
    Port 2222
    IdentitiesOnly yes
```

`IdentitiesOnly yes` prevents SSH from trying all loaded keys — it only offers the specified one. This matters when you have many keys loaded in the agent.

With this config, cloning a work repo is just:

```bash
$ git clone git@github-work:your-org/repo.git
```

## SSH Agent: One Passphrase Per Session

`ssh-agent` holds decrypted private keys in memory so you don't retype your passphrase on every connection.

```bash
# Start the agent (usually automatic on macOS/modern Linux)
$ eval "$(ssh-agent -s)"
Agent pid 12345

# Add your key — enter passphrase once
$ ssh-add ~/.ssh/id_ed25519
Enter passphrase for /home/user/.ssh/id_ed25519: ****
Identity added: /home/user/.ssh/id_ed25519 (your@email.com)

# List loaded keys
$ ssh-add -l
256 SHA256:AbCdEf... your@email.com (ED25519)

# Remove all keys from agent (on shared/untrusted machines)
$ ssh-add -D
```

On macOS, add keys to the Keychain so they persist across reboots:

```bash
$ ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

And in `~/.ssh/config`:

```
Host *
    AddKeysToAgent yes
    UseKeychain yes        # macOS only
```

## Installing Public Keys on Servers

The public key (`.pub`) is what you share. The private key never leaves your machine.

```bash
# Install your public key on a remote server
$ ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server.example.com

# Or manually
$ cat ~/.ssh/id_ed25519.pub | ssh user@server "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# Verify permissions — SSH is strict about these
$ ssh user@server "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

Check the server's `authorized_keys` format — each line is one public key:

```bash
$ ssh user@server "cat ~/.ssh/authorized_keys"
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... personal laptop
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... work laptop
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... CI/CD system
```

Labeling keys with their origin (`-C "personal laptop"`) makes auditing much easier.

## GitHub SSH Setup

```bash
# Add your public key to GitHub
$ cat ~/.ssh/id_ed25519.pub
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... your@email.com

# Copy that output, then go to:
# GitHub → Settings → SSH and GPG keys → New SSH key

# Test the connection
$ ssh -T git@github.com
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

For multiple GitHub accounts (personal + work), use the `Host` alias from your config:

```bash
# Personal
$ git clone git@github.com:personal-user/repo.git

# Work (uses the github-work alias pointing to work_github key)
$ git clone git@github-work:work-org/repo.git
```

## Key Rotation

Keys should be rotated periodically — especially for service accounts and CI/CD systems.

```bash
# Generate a new key
$ ssh-keygen -t ed25519 -C "deploy-key-$(date +%Y-%m)" -f ~/.ssh/new_deploy_key

# Add the new public key to the server's authorized_keys
$ ssh-copy-id -i ~/.ssh/new_deploy_key.pub deploy@prod.example.com

# Verify the new key works BEFORE removing the old one
$ ssh -i ~/.ssh/new_deploy_key deploy@prod.example.com "echo 'new key works'"
new key works

# Remove the old key from authorized_keys
$ ssh deploy@prod.example.com "sed -i '/old-key-fingerprint/d' ~/.ssh/authorized_keys"

# Remove the old key locally
$ rm ~/.ssh/old_deploy_key ~/.ssh/old_deploy_key.pub
```

Always verify the new key works before revoking the old one.

## Hardening the SSH Server

On servers you control, tighten the SSH daemon config (`/etc/ssh/sshd_config`):

```bash
# Disable password authentication entirely — keys only
PasswordAuthentication no
ChallengeResponseAuthentication no

# Disable root login
PermitRootLogin no

# Only allow specific users
AllowUsers deploy alice bob

# Use a non-standard port (reduces automated scanning noise, not real security)
Port 2222

# Disable unused auth methods
PubkeyAuthentication yes
KerberosAuthentication no
GSSAPIAuthentication no
```

```bash
# Reload after changes
$ sudo systemctl reload sshd

# Test config before reloading (catches syntax errors)
$ sudo sshd -t
```

## Key Principles

- **One key per machine, not per service.** Each device you use should have its own key. If a device is lost, revoke that device's key — not all your access.
- **Different keys for different trust levels.** Personal GitHub, work GitHub, and production servers should each have their own key.
- **Never share private keys.** If a teammate needs access to a server, they generate their own key and you add their public key.
- **Store backups securely.** Back up private keys to an encrypted password manager (1Password, Bitwarden) or encrypted external storage — not plain cloud drives.

## Conclusion

Good SSH key management is straightforward once you have a system: Ed25519 keys with passphrases, `ssh-agent` for convenience, `~/.ssh/config` to organize multiple keys, and a rotation plan for service accounts. The most common mistake is sharing private keys or using a single personal key for everything — one key per device and one key per context makes revocation clean and limits blast radius if a key is ever compromised.
