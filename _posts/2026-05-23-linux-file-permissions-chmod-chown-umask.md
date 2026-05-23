---
layout: post
title: "Linux File Permissions Explained: chmod, chown, umask"
date: "2026-05-23 00:00:00 +0530"
slug: linux-file-permissions-chmod-chown-umask
description: "A clear explanation of Linux file permissions, the chmod octal and symbolic modes, chown for ownership changes, and how umask controls new file defaults."
categories: ["wiki", "unix"]
tags: ["linux", "chmod", "chown", "umask", "permissions", "unix", "security", "terminal", "sysadmin"]
---

File permissions in Linux confuse most people exactly once — after that they're completely mechanical. The confusion usually comes from the octal notation. Once you see how the numbers map to read/write/execute for three groups of users, it clicks and stays clicked.

## Reading Permissions

List files with full permission info using `ls -l`:

```bash
$ ls -l
-rw-r--r-- 1 mukul staff  1234 May 23 10:00 config.yaml
drwxr-xr-x 3 mukul staff   96 May 23 09:00 src/
-rwxr-xr-x 1 mukul staff  8192 May 23 10:01 server
```

The first column is the permission string: 10 characters.

```
- rw- r-- r--
│ │   │   └── Other (everyone else): read only
│ │   └────── Group: read only
│ └────────── Owner: read + write
└──────────── Type: - (file), d (directory), l (symlink)
```

Each of the three permission groups (owner, group, other) has three bits: **r** (read), **w** (write), **x** (execute).

For directories, the bits mean slightly different things:
- **r** — can list the directory contents (`ls`)
- **w** — can create, rename, or delete files inside
- **x** — can enter the directory (`cd`) and access files within

## chmod — Changing Permissions

### Octal Mode

Each permission bit has a value: r=4, w=2, x=1. Add them up for each group:

| Octal | Binary | rwx |
|---|---|---|
| 7 | 111 | rwx |
| 6 | 110 | rw- |
| 5 | 101 | r-x |
| 4 | 100 | r-- |
| 0 | 000 | --- |

So `chmod 755` means:
- Owner: 7 = rwx
- Group: 5 = r-x
- Other: 5 = r-x

Common permission patterns:

| Mode | Meaning | Typical use |
|---|---|---|
| `644` | Owner rw, group+other r | Config files, HTML |
| `755` | Owner rwx, group+other rx | Directories, executables |
| `600` | Owner rw only | Private keys, secrets |
| `700` | Owner rwx only | Private directories |
| `777` | Everyone rwx | Avoid in production |

```bash
$ chmod 644 config.yaml
$ chmod 755 deploy.sh
$ chmod 600 ~/.ssh/id_ed25519
```

Apply recursively to a directory:

```bash
$ chmod -R 755 /var/www/html/
```

### Symbolic Mode

Symbolic mode is more readable for incremental changes — you don't need to remember the full permission state.

Syntax: `[ugoa][+-=][rwx]`

- `u` — owner (user), `g` — group, `o` — other, `a` — all
- `+` — add, `-` — remove, `=` — set exactly

```bash
$ chmod +x script.sh         # add execute for all
$ chmod u+x script.sh        # add execute for owner only
$ chmod go-w file.txt        # remove write from group and other
$ chmod u=rw,go=r file.txt   # set explicitly: owner rw, others r
$ chmod a-x file.txt         # remove execute from everyone
```

Make a script executable without touching other permissions:

```bash
$ chmod +x deploy.sh
```

This is equivalent to `chmod a+x` — it adds execute for all three groups. Use `u+x` if you only want the owner to execute it.

## Special Bits: setuid, setgid, sticky

These are less commonly set manually, but you'll encounter them.

### setuid (`s` on owner execute bit)

When set on an executable, the process runs with the file owner's privileges, not the caller's:

```bash
$ ls -l /usr/bin/passwd
-rwsr-xr-x 1 root root 59976 Mar 22 2024 /usr/bin/passwd
```

The `s` in place of `x` for the owner is the setuid bit. This is why a normal user can change their password — the `passwd` binary temporarily runs as root.

Set with `chmod u+s file` or `chmod 4755 file`.

### setgid (`s` on group execute bit)

On a directory, new files inherit the directory's group rather than the creator's primary group — useful for shared project directories:

```bash
$ mkdir /srv/shared
$ chmod g+s /srv/shared
$ ls -ld /srv/shared
drwxr-sr-x 2 root devteam 4096 May 23 10:00 /srv/shared
```

Set with `chmod g+s dir` or `chmod 2755 dir`.

### sticky bit (`t` on other execute bit)

On a directory, only the file owner (or root) can delete files, even if others have write permission. Used on `/tmp`:

```bash
$ ls -ld /tmp
drwxrwxrwt 18 root root 4096 May 23 10:00 /tmp
```

The `t` at the end is the sticky bit. Set with `chmod +t dir` or `chmod 1777 dir`.

## chown — Changing Ownership

```bash
$ chown user file.txt              # change owner only
$ chown user:group file.txt        # change owner and group
$ chown :group file.txt            # change group only
$ chown -R user:group /var/www/    # recursive
```

Examples:

```bash
$ sudo chown www-data:www-data /var/www/html/
$ sudo chown -R deploy:deploy /opt/myapp/
```

You need root (or `sudo`) to change a file's owner to someone else. You can change a file's group to any group you belong to without sudo.

## chgrp — Changing Group

`chgrp` is a shortcut for when you only want to change the group:

```bash
$ chgrp developers project/
$ chgrp -R devteam /srv/shared/
```

Equivalent to `chown :developers project/`.

## umask — Default Permissions for New Files

`umask` controls the permissions applied to newly created files and directories. It's a mask — bits set in `umask` are *removed* from the default:

- Default file permissions: `666` (rw-rw-rw-)
- Default directory permissions: `777` (rwxrwxrwx)
- With `umask 022`: files get `644`, directories get `755`

View the current umask:

```bash
$ umask
0022

$ umask -S
u=rwx,g=rx,o=rx
```

The `0022` umask subtracts write from group and other:

```
666 (default file)
- 022 (umask)
= 644 (resulting permission)
```

```
777 (default directory)
- 022 (umask)
= 755
```

A more restrictive umask like `0077` gives new files `600` and directories `700` — nothing visible to group or other:

```bash
$ umask 0077
$ touch secret.txt
$ ls -l secret.txt
-rw------- 1 mukul staff 0 May 23 10:05 secret.txt
```

Set `umask` in `~/.bashrc` or `~/.zshrc` to persist it:

```bash
umask 022   # standard, files are 644
```

## Real-World Examples

**Fix permissions on a web root after a botched deploy:**

```bash
$ sudo find /var/www/html -type f -exec chmod 644 {} \;
$ sudo find /var/www/html -type d -exec chmod 755 {} \;
$ sudo chown -R www-data:www-data /var/www/html/
```

**Secure an SSH private key:**

```bash
$ chmod 600 ~/.ssh/id_ed25519
$ chmod 700 ~/.ssh/
```

**Make a script executable and move it to PATH:**

```bash
$ chmod +x myscript.sh
$ sudo mv myscript.sh /usr/local/bin/myscript
```

**Set up a shared directory where any team member can delete only their own files:**

```bash
$ mkdir /srv/uploads
$ chmod 1777 /srv/uploads    # 1 = sticky bit
```

## Conclusion

File permissions in Linux are three sets of read/write/execute bits for owner, group, and everyone else. `chmod` in octal is the fastest way to set them precisely — internalize `644` (files), `755` (directories and executables), and `600` (secrets). `chown` sets who owns the file, and `umask` determines what permissions new files inherit. These three tools cover virtually every permission management task you'll run into on a Linux system.
