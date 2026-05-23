---
layout: post
title: "cron and crontab — Scheduling Jobs on Linux and macOS"
date: "2026-05-23 00:00:00 +0530"
slug: cron-crontab-scheduling-guide
description: "A practical guide to cron and crontab for scheduling recurring tasks on Linux and macOS, with syntax breakdowns and real-world examples."
categories: ["Tutorials", "unix"]
tags: ["cron", "crontab", "scheduling", "unix", "linux", "macos", "automation", "sysadmin", "terminal"]
---

`cron` is the backbone of task automation on Unix systems. Whether you're rotating logs at midnight, sending a daily report, or polling an API every five minutes, cron is almost certainly the right tool for the job — and it's been reliable enough to ship on every major Linux and macOS system for decades.

## How cron works

`crond` is a daemon that runs in the background and wakes up every minute to check if any scheduled job is due. Jobs are defined in a **crontab** (cron table) — a plain text file with one job per line. Each line specifies a schedule and a command.

```bash
$ crontab -l
# no crontab for mukul
```

To edit your crontab:

```bash
$ crontab -e
```

This opens the file in `$EDITOR` (usually `vi` or `nano`). Changes take effect immediately after saving.

## Crontab syntax

Every cron entry follows this structure:

```
* * * * * /path/to/command
│ │ │ │ │
│ │ │ │ └─ Day of week  (0–7, 0 and 7 are Sunday)
│ │ │ └─── Month        (1–12)
│ │ └───── Day of month (1–31)
│ └─────── Hour         (0–23)
└───────── Minute       (0–59)
```

A `*` means "every valid value". Here are some examples:

| Schedule | Expression |
|---|---|
| Every minute | `* * * * *` |
| Every day at midnight | `0 0 * * *` |
| Every Monday at 9 AM | `0 9 * * 1` |
| Every 5 minutes | `*/5 * * * *` |
| First day of every month | `0 0 1 * *` |
| Every weekday at 6:30 PM | `30 18 * * 1-5` |

### Step values

`*/n` means "every n units". `*/15` in the minute field means every 15 minutes.

### Range and list

- A range: `1-5` (Monday through Friday)
- A list: `1,3,5` (Monday, Wednesday, Friday)
- Combined: `0 9 * * 1,3,5` — 9 AM on Mon, Wed, Fri

## Practical examples

### Run a backup script nightly at 2 AM

```
0 2 * * * /home/mukul/scripts/backup.sh >> /var/log/backup.log 2>&1
```

The `>> ... 2>&1` redirects both stdout and stderr to a log file. Without redirection, cron mails the output to the system user — which often disappears silently.

### Clear a temp directory every Sunday at 3 AM

```
0 3 * * 0 rm -rf /tmp/myapp/cache/*
```

### Restart a service if it crashes (crude watchdog)

```
*/5 * * * * pgrep myapp || systemctl restart myapp
```

### Pull latest code and restart an app every hour

```
0 * * * * cd /srv/myapp && git pull && systemctl restart myapp
```

## Environment in cron

Cron jobs run with a minimal environment — no `~/.bashrc`, no `PATH` beyond `/usr/bin:/bin`. This is the most common source of "it works manually but not in cron" bugs.

Fix it by setting `PATH` at the top of your crontab:

```
PATH=/usr/local/bin:/usr/bin:/bin:/home/mukul/.local/bin

0 2 * * * backup.sh
```

Or use absolute paths everywhere inside the script.

## System-wide cron directories

On Linux, you don't always need `crontab -e`. Drop a script into one of these directories and cron will run it automatically:

```bash
/etc/cron.hourly/
/etc/cron.daily/
/etc/cron.weekly/
/etc/cron.monthly/
```

Files in these directories must be executable and must not have an extension (no `.sh`).

```bash
$ sudo cp myscript /etc/cron.daily/myscript
$ sudo chmod +x /etc/cron.daily/myscript
```

## macOS specifics

macOS ships with `cron` but Apple recommends `launchd` for new automations. That said, `crontab` still works fine on macOS for most use cases. One gotcha: full disk access permissions can block cron from accessing certain directories under modern macOS security restrictions. If a cron job silently fails, check System Settings → Privacy & Security → Full Disk Access and add `cron` or your terminal emulator.

You can also use `launchd` plists in `~/Library/LaunchAgents/` for finer-grained scheduling (e.g., run at login, retry on failure), but for simple recurring jobs `crontab` is less boilerplate.

## Debugging cron jobs

**Check the system mail:**
```bash
$ mail
# or
$ cat /var/spool/mail/$USER
```

**Check syslog for cron activity:**
```bash
$ grep CRON /var/log/syslog | tail -20
May 23 02:00:01 hostname CRON[12345]: (mukul) CMD (/home/mukul/scripts/backup.sh)
```

**Test the command manually with a clean environment:**
```bash
$ env -i HOME=$HOME PATH=/usr/bin:/bin bash -c 'your_command_here'
```

This strips most environment variables and closely mimics what cron sees.

## Common mistakes

- **Forgetting `2>&1`** — error output silently disappears
- **Relative paths** — use absolute paths or set `PATH` in the crontab
- **No newline at end of file** — some cron implementations ignore the last line without a trailing newline
- **Editing `/etc/crontab` directly instead of `crontab -e`** — system crontab has an extra user field; mixing formats causes parse errors

## Conclusion

`cron` is one of those tools you can learn in 20 minutes and rely on for years. The syntax is compact but expressive enough for nearly every scheduling pattern you'll encounter. Once you get the hang of redirecting output, setting `PATH`, and testing jobs in a clean environment, you'll stop wrestling with silent failures and start trusting your scheduled jobs to just run.
