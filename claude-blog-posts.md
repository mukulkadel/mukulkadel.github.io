# Claude Blog Post Generation Plan

## How to use this file

Hand this file to Claude with the following prompt:

> Read `claude-blog-posts.md` and generate the next unchecked blog post. Save it to `_posts/` with the correct filename and front matter, then check off the item in this file. Repeat until I tell you to stop.

- `[ ]` = not started
- `[x]` = written and saved to `_posts/`

Posts are generated one at a time. After each post is written, Claude should:
1. Save the file to `_posts/YYYY-MM-DD-slug.md` using today's date
2. Mark the checkbox `[x]` in this file
3. Report the filename and slug

---

## Generation instructions for Claude

### Front matter template

```yaml
---
layout: post
title: "Human-readable title"
date: "YYYY-MM-DD 00:00:00 +0530"
slug: url-slug-here
description: "120–155 character SEO description. Must be a complete sentence."
categories: ["Cat1", "Cat2"]
tags: ["tag1", "tag2", "tag3"]
---
```

### Writing rules

- Opening paragraph: 2–4 sentences, no heading, sets the "why this matters"
- Use `##` for major sections, `###` for sub-sections, never `#` inside post body
- Tone: conversational and direct — use "we'll", "Let's", "you can" freely
- Every technical post must have at least one fenced code block with a language identifier
- Bash examples must show the `$` prompt and include realistic sample output
- End every post with a `## Conclusion` section (2–5 sentences)
- No inline `<style>` blocks, no Jekyll Rouge highlighter — highlight.js handles it
- Mermaid diagrams use the `mermaid` fence identifier directly, not nested in another block
- Do NOT add comments explaining what the code does — only non-obvious WHY comments

### Category reference

| Category | Use when | Examples from this list |
|---|---|---|
| `wiki` | Conceptual explainers, deep dives, mental models, reference guides | System design, networking internals, psychology posts, "how X works" |
| `Programming` | Language patterns, CLI tools, code architecture, build-things posts | Event sourcing, plugin systems, building from scratch |
| `Tutorials` | Step-by-step how-tos with real commands and expected output | Scripting automation, self-hosted server setup, Ansible playbooks |
| `unix` | Linux/macOS kernel, system tools, process management | systemd, namespaces/cgroups, iptables, launchd |
| `SQL` | Databases, query content, storage engines | WAL, vacuuming, column-oriented DBs, SQLite |

### Tag guidance

Use 5–12 granular, SEO-relevant tags. Err toward more rather than fewer.

---

## Progress tracker

**Total posts**: 149
**Completed**: 26
**Remaining**: 123

---

## Post list

### System Design

- [x] **01** — System Design: Building a Real-Time Chat Application
  - `slug`: system-design-real-time-chat
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["system design", "real-time", "websockets", "backend", "scalability", "chat", "architecture", "pub/sub", "interview"]

- [x] **02** — System Design: How Distributed Locks Work (Redlock, Zookeeper)
  - `slug`: system-design-distributed-locks
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["distributed systems", "distributed locks", "redlock", "zookeeper", "redis", "concurrency", "backend", "architecture"]

- [x] **03** — System Design: Building a File Storage Service Like S3
  - `slug`: system-design-file-storage-service
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["system design", "file storage", "s3", "object storage", "backend", "scalability", "cloud", "architecture", "interview"]

- [x] **04** — Event-Driven Architecture: Patterns and Trade-offs
  - `slug`: event-driven-architecture-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["event-driven", "architecture", "kafka", "events", "microservices", "backend", "async", "pub/sub", "decoupling"]

- [x] **05** — Circuit Breakers, Retries, and Backoff: Resilience Patterns Explained
  - `slug`: circuit-breakers-retries-backoff
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["circuit breaker", "retry", "exponential backoff", "resilience", "distributed systems", "backend", "fault tolerance", "microservices"]

- [x] **06** — System Design: Designing an API Gateway from Scratch
  - `slug`: system-design-api-gateway
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["api gateway", "system design", "routing", "rate limiting", "auth", "backend", "microservices", "nginx", "architecture"]

- [x] **07** — The Saga Pattern: Managing Distributed Transactions Without 2PC
  - `slug`: saga-pattern-distributed-transactions
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["saga pattern", "distributed transactions", "microservices", "eventual consistency", "backend", "architecture", "choreography", "orchestration"]

- [x] **08** — Multi-Tenancy Patterns for SaaS Applications
  - `slug`: multi-tenancy-patterns-saas
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["multi-tenancy", "saas", "database", "architecture", "backend", "isolation", "scalability", "system design", "schema"]

- [x] **09** — System Design: Building a Real-Time Leaderboard with Redis
  - `slug`: system-design-realtime-leaderboard-redis
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["leaderboard", "redis", "sorted sets", "real-time", "system design", "gaming", "backend", "scalability", "zset"]

- [x] **10** — How Distributed Tracing Works (OpenTelemetry, Jaeger)
  - `slug`: distributed-tracing-opentelemetry-jaeger
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["distributed tracing", "opentelemetry", "jaeger", "observability", "microservices", "spans", "backend", "devops", "debugging"]

- [x] **11** — System Design: Building a Search Engine with Inverted Indexes
  - `slug`: system-design-search-engine-inverted-index
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["search engine", "inverted index", "elasticsearch", "full-text search", "system design", "backend", "architecture", "interview"]

- [x] **12** — Zero-Downtime Deployments: Blue-Green, Canary, and Rolling Strategies
  - `slug`: zero-downtime-deployment-strategies
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["zero downtime", "blue-green deployment", "canary release", "rolling deployment", "devops", "kubernetes", "ci/cd", "backend"]

- [x] **13** — System Design: Designing a Task Queue and Job Scheduler
  - `slug`: system-design-task-queue-job-scheduler
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["task queue", "job scheduler", "celery", "sidekiq", "redis", "backend", "system design", "async", "workers", "architecture"]

- [x] **14** — Write-Ahead Logging: How Databases Recover from Crashes
  - `slug`: write-ahead-logging-database-recovery
  - `categories`: ["wiki", "SQL"]
  - `tags`: ["write-ahead log", "wal", "database", "crash recovery", "postgresql", "durability", "acid", "storage engine", "internals"]

- [x] **15** — CQRS: Command Query Responsibility Segregation Explained
  - `slug`: cqrs-command-query-responsibility-segregation
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["cqrs", "command query", "architecture", "event sourcing", "backend", "read models", "write models", "microservices", "design patterns"]

---

### Networking Deep Dives

- [x] **16** — How BGP Works: The Protocol That Routes the Internet
  - `slug`: how-bgp-works-explained
  - `categories`: ["wiki"]
  - `tags`: ["bgp", "border gateway protocol", "networking", "routing", "internet", "autonomous systems", "isp", "peering", "infrastructure"]

- [x] **17** — IP Subnetting and CIDR Notation: A Practical Guide
  - `slug`: ip-subnetting-cidr-notation-guide
  - `categories`: ["wiki"]
  - `tags`: ["subnetting", "cidr", "ip addressing", "networking", "ipv4", "netmask", "vpc", "devops", "linux", "sysadmin"]

- [x] **18** — How the TLS Handshake Works Step by Step
  - `slug`: tls-handshake-explained-step-by-step
  - `categories`: ["wiki"]
  - `tags`: ["tls", "ssl", "handshake", "https", "encryption", "certificates", "networking", "security", "asymmetric encryption"]

- [x] **19** — iptables and nftables: Packet Filtering on Linux
  - `slug`: iptables-nftables-packet-filtering-linux
  - `categories`: ["wiki", "unix"]
  - `tags`: ["iptables", "nftables", "firewall", "linux", "packet filtering", "networking", "sysadmin", "security", "chains", "rules"]

- [x] **20** — VPNs Explained: How WireGuard Works Under the Hood
  - `slug`: vpn-wireguard-explained
  - `categories`: ["wiki"]
  - `tags`: ["vpn", "wireguard", "networking", "tunneling", "encryption", "privacy", "linux", "security", "peer-to-peer"]

- [ ] **21** — How HTTP Caching Headers Work: Cache-Control, ETag, and Vary
  - `slug`: http-caching-headers-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["http caching", "cache-control", "etag", "vary", "http headers", "web performance", "browser", "cdn", "nginx", "backend"]

- [ ] **22** — How NAT Works: Network Address Translation Explained
  - `slug`: how-nat-works-explained
  - `categories`: ["wiki"]
  - `tags`: ["nat", "network address translation", "networking", "ipv4", "router", "linux", "sysadmin", "masquerade", "port forwarding"]

- [ ] **23** — Wireshark for Developers: Reading and Debugging Network Traffic
  - `slug`: wireshark-for-developers
  - `categories`: ["wiki", "Tutorials"]
  - `tags`: ["wireshark", "networking", "packet capture", "debugging", "tcp", "http", "tls", "pcap", "network analysis", "troubleshooting"]

- [ ] **24** — IPv6 for Developers: What Changes and What You Need to Know
  - `slug`: ipv6-for-developers-explained
  - `categories`: ["wiki"]
  - `tags`: ["ipv6", "networking", "ip addressing", "internet protocol", "dual stack", "linux", "devops", "sysadmin", "transition"]

- [ ] **25** — Understanding Anycast: How CDNs Route Traffic to the Nearest Server
  - `slug`: anycast-routing-how-cdns-work
  - `categories`: ["wiki"]
  - `tags`: ["anycast", "cdn", "routing", "networking", "dns", "cloudflare", "bgp", "latency", "load balancing", "infrastructure"]

---

### Programming Patterns & Internals

- [ ] **26** — Event Sourcing Explained with a Practical Python Example
  - `slug`: event-sourcing-explained-python
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["event sourcing", "events", "python", "backend", "architecture", "audit log", "state", "database", "design patterns"]

- [ ] **27** — State Machines: Making Complex Logic Explicit
  - `slug`: state-machines-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["state machine", "finite state machine", "programming", "design patterns", "python", "backend", "workflow", "logic", "modeling"]

- [ ] **28** — Dependency Injection Without a Framework
  - `slug`: dependency-injection-without-framework
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["dependency injection", "inversion of control", "python", "design patterns", "testing", "decoupling", "backend", "architecture"]

- [ ] **29** — Functional Programming Concepts That Apply to Any Language
  - `slug`: functional-programming-concepts-any-language
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["functional programming", "immutability", "pure functions", "map filter reduce", "python", "javascript", "programming", "design patterns"]

- [ ] **30** — How JavaScript's Event Loop Really Works
  - `slug`: javascript-event-loop-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["javascript", "event loop", "async", "promises", "call stack", "microtasks", "macrotasks", "node", "frontend", "backend"]

- [ ] **31** — Writing Idiomatic Python: Common Patterns and Anti-Patterns
  - `slug`: idiomatic-python-patterns-anti-patterns
  - `categories`: ["Programming", "wiki"]
  - `tags`: ["python", "idiomatic", "best practices", "patterns", "list comprehensions", "generators", "context managers", "pythonic", "code quality"]

- [ ] **32** — How Git's Object Model Works Internally
  - `slug`: git-object-model-internals
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["git", "internals", "object model", "blobs", "trees", "commits", "refs", "pack files", "plumbing", "version control"]

- [ ] **33** — Understanding Memory Leaks in Long-Running Python Applications
  - `slug`: python-memory-leaks-debugging
  - `categories`: ["Programming", "wiki"]
  - `tags`: ["python", "memory leaks", "debugging", "profiling", "gc", "garbage collection", "backend", "performance", "tracemalloc"]

- [ ] **34** — Profiling and Benchmarking Python Applications
  - `slug`: python-profiling-benchmarking
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["python", "profiling", "benchmarking", "performance", "cProfile", "py-spy", "line_profiler", "optimization", "backend"]

- [ ] **35** — How a Database Engine Works Internally (B-Trees, WAL, MVCC)
  - `slug`: database-engine-internals-btree-wal-mvcc
  - `categories`: ["wiki", "SQL"]
  - `tags`: ["database internals", "b-tree", "wal", "mvcc", "postgresql", "storage engine", "concurrency", "transactions", "sql"]

- [ ] **36** — Building a Plugin System in Python
  - `slug`: building-plugin-system-python
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["python", "plugin system", "extensibility", "architecture", "importlib", "abc", "design patterns", "backend", "tutorial"]

- [ ] **37** — Understanding Copy-on-Write in Linux and Databases
  - `slug`: copy-on-write-linux-databases-explained
  - `categories`: ["wiki"]
  - `tags`: ["copy-on-write", "cow", "linux", "fork", "database", "postgresql", "memory", "kernel", "filesystems", "internals"]

- [ ] **38** — Understanding Linux Process Scheduling
  - `slug`: linux-process-scheduling-explained
  - `categories`: ["wiki", "unix"]
  - `tags`: ["linux", "process scheduling", "cfs", "kernel", "cpu", "nice", "priority", "real-time", "sysadmin", "performance"]

---

### Scripting & Automation

- [ ] **39** — Python Scripts That Save Hours: File and Directory Processing Patterns
  - `slug`: python-file-processing-automation-scripts
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["python", "scripting", "automation", "file processing", "pathlib", "shutil", "glob", "batch processing", "productivity"]

- [ ] **40** — Web Scraping with Python: Requests, BeautifulSoup, and Playwright
  - `slug`: web-scraping-python-requests-beautifulsoup-playwright
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["web scraping", "python", "beautifulsoup", "playwright", "requests", "automation", "html", "data extraction", "tutorial"]

- [ ] **41** — Automating GitHub with the GitHub API and Python
  - `slug`: automating-github-with-api-python
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["github api", "python", "automation", "scripting", "repos", "pull requests", "issues", "devops", "pygithub", "tutorial"]

- [ ] **42** — Parsing and Processing Large CSV and JSON Files in Python
  - `slug`: parsing-large-csv-json-python
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["python", "csv", "json", "data processing", "streaming", "pandas", "ijson", "large files", "scripting", "automation"]

- [ ] **43** — Sending Notifications from Your Scripts (Slack, Email, Telegram)
  - `slug`: sending-notifications-from-scripts
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["python", "notifications", "slack", "email", "telegram", "scripting", "automation", "webhooks", "smtplib", "alerts"]

- [ ] **44** — Automating macOS with Shell Scripts and launchd
  - `slug`: automating-macos-shell-scripts-launchd
  - `categories`: ["Tutorials", "unix"]
  - `tags`: ["macos", "automation", "shell scripts", "launchd", "bash", "zsh", "scheduled tasks", "plist", "productivity", "unix"]

- [ ] **45** — Building a Personal Automation System with Python and Cron
  - `slug`: personal-automation-system-python-cron
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["python", "automation", "cron", "scripting", "productivity", "scheduled tasks", "unix", "linux", "macos", "personal tools"]

- [ ] **46** — Automating Browser Tasks with Playwright: A Practical Guide
  - `slug`: automating-browser-tasks-playwright
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["playwright", "browser automation", "python", "javascript", "scraping", "testing", "automation", "headless browser", "tutorial"]

- [ ] **47** — Building a PDF Report Generator with Python
  - `slug`: python-pdf-report-generator
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["python", "pdf", "reportlab", "weasyprint", "automation", "scripting", "reporting", "tutorial", "productivity"]

- [ ] **48** — Writing a Static Site Generator from Scratch in Python
  - `slug`: build-static-site-generator-python
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["static site generator", "python", "markdown", "jinja2", "html", "build tool", "tutorial", "from scratch", "scripting"]

---

### Building Useful Things

- [ ] **49** — Build a Personal Knowledge Base with Markdown and SQLite
  - `slug`: build-personal-knowledge-base-markdown-sqlite
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["knowledge base", "sqlite", "markdown", "python", "note-taking", "full-text search", "productivity", "personal tools", "tutorial"]

- [ ] **50** — Build a Local File Search Engine with Python and FTS5
  - `slug`: build-local-file-search-engine-python-fts5
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["file search", "sqlite", "fts5", "full-text search", "python", "indexing", "productivity", "personal tools", "tutorial"]

- [ ] **51** — Build a DNS Resolver from Scratch to Understand DNS
  - `slug`: build-dns-resolver-from-scratch
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["dns", "resolver", "python", "from scratch", "networking", "udp", "protocol", "tutorial", "internals", "learning"]

- [ ] **52** — Build a TCP Chat Server in Python
  - `slug`: build-tcp-chat-server-python
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["tcp", "sockets", "python", "chat server", "networking", "asyncio", "tutorial", "from scratch", "concurrency"]

- [ ] **53** — Build a Minimal HTTP Server Without a Framework
  - `slug`: build-minimal-http-server-python
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["http server", "python", "sockets", "from scratch", "networking", "tutorial", "http protocol", "backend", "learning by doing"]

- [ ] **54** — Build a Simple Key-Value Store from Scratch
  - `slug`: build-key-value-store-from-scratch
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["key-value store", "database", "python", "from scratch", "storage", "tutorial", "hash map", "persistence", "learning"]

- [ ] **55** — Build a Personal Finance Dashboard in the Terminal
  - `slug`: build-personal-finance-dashboard-terminal
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["personal finance", "python", "terminal", "cli", "rich", "csv", "visualization", "productivity", "personal tools", "tutorial"]

- [ ] **56** — Build a Command-Line Bookmark Manager
  - `slug`: build-cli-bookmark-manager
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["bookmark manager", "cli", "python", "sqlite", "productivity", "terminal", "personal tools", "tutorial", "fzf"]

- [ ] **57** — Build a File Watcher That Triggers Actions on Change
  - `slug`: build-file-watcher-python
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["file watcher", "watchdog", "python", "automation", "scripting", "inotify", "macos", "linux", "tutorial", "productivity"]

- [ ] **58** — Build a Personal Work Log Generator with Git and Python
  - `slug`: build-personal-work-log-git-python
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["work log", "git", "python", "automation", "changelog", "productivity", "scripting", "personal tools", "tutorial"]

- [ ] **59** — Build a Daily Habit Tracker in the Terminal
  - `slug`: build-cli-habit-tracker
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["habit tracker", "cli", "python", "sqlite", "terminal", "productivity", "personal tools", "rich", "tutorial"]

- [ ] **60** — Build a Background Job Queue from Scratch in Python
  - `slug`: build-job-queue-from-scratch-python
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["job queue", "background jobs", "python", "redis", "from scratch", "tutorial", "workers", "async", "task processing"]

---

### Infrastructure & DevOps

- [ ] **61** — Linux Namespaces and cgroups: How Containers Work Under the Hood
  - `slug`: linux-namespaces-cgroups-how-containers-work
  - `categories`: ["wiki", "unix"]
  - `tags`: ["linux", "namespaces", "cgroups", "containers", "docker", "internals", "kernel", "isolation", "resource limits", "devops"]

- [ ] **62** — Setting Up a Self-Hosted Server: VPS, Nginx, SSL, and systemd
  - `slug`: self-hosted-server-vps-nginx-ssl-systemd
  - `categories`: ["Tutorials", "unix"]
  - `tags`: ["vps", "nginx", "ssl", "systemd", "linux", "self-hosted", "devops", "server setup", "certbot", "tutorial"]

- [ ] **63** — Understanding Linux systemd: Services, Timers, and Targets
  - `slug`: linux-systemd-services-timers-targets
  - `categories`: ["wiki", "unix"]
  - `tags`: ["systemd", "linux", "services", "timers", "units", "sysadmin", "devops", "daemon", "init system", "journald"]

- [ ] **64** — Writing Ansible Playbooks: Configuration Management Without the Pain
  - `slug`: ansible-playbooks-configuration-management
  - `categories`: ["Tutorials", "Programming"]
  - `tags`: ["ansible", "configuration management", "devops", "playbooks", "yaml", "automation", "linux", "idempotent", "tutorial", "infrastructure"]

- [ ] **65** — Observability: The Difference Between Logs, Metrics, and Traces
  - `slug`: observability-logs-metrics-traces-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["observability", "logs", "metrics", "traces", "monitoring", "opentelemetry", "devops", "backend", "sre", "debugging"]

- [ ] **66** — Secrets Management: Vault, SOPS, and AWS Secrets Manager
  - `slug`: secrets-management-vault-sops-aws
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["secrets management", "vault", "sops", "aws secrets manager", "security", "devops", "kubernetes", "environment variables", "encryption"]

- [ ] **67** — Understanding LSM Trees: The Data Structure Behind RocksDB and Cassandra
  - `slug`: lsm-trees-rocksdb-cassandra-explained
  - `categories`: ["wiki"]
  - `tags`: ["lsm tree", "rocksdb", "cassandra", "database internals", "storage engine", "write optimization", "compaction", "memtable", "sstable"]

- [ ] **68** — Column-Oriented Databases: Why Analytics Needs Different Storage
  - `slug`: column-oriented-databases-explained
  - `categories`: ["wiki", "SQL"]
  - `tags`: ["columnar database", "analytics", "olap", "clickhouse", "parquet", "redshift", "storage", "compression", "query performance"]

---

### Security

- [ ] **69** — How Password Hashing Works: bcrypt, Argon2, and scrypt
  - `slug`: password-hashing-bcrypt-argon2-scrypt
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["password hashing", "bcrypt", "argon2", "scrypt", "security", "cryptography", "authentication", "backend", "salting"]

- [ ] **70** — Public Key Infrastructure (PKI) Explained from Scratch
  - `slug`: public-key-infrastructure-pki-explained
  - `categories`: ["wiki"]
  - `tags`: ["pki", "public key infrastructure", "certificates", "ca", "x509", "tls", "encryption", "security", "trust chain"]

- [ ] **71** — How JWT Attacks Work and How to Defend Against Them
  - `slug`: jwt-attacks-and-defenses
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["jwt", "json web tokens", "security", "attacks", "alg none", "key confusion", "authentication", "backend", "owasp"]

- [ ] **72** — Container Security: Common Misconfigurations and Fixes
  - `slug`: container-security-misconfigurations
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["container security", "docker", "kubernetes", "security", "misconfigurations", "devops", "least privilege", "seccomp", "devSecOps"]

- [ ] **73** — Supply Chain Security: Protecting Your Dependencies
  - `slug`: supply-chain-security-dependencies
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["supply chain security", "dependencies", "npm", "pip", "sbom", "sigstore", "software security", "devops", "open source"]

- [ ] **74** — Secrets in Code: Finding and Fixing Leaked Credentials
  - `slug`: finding-fixing-leaked-credentials-code
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["secrets", "credentials", "security", "git", "trufflehog", "gitleaks", "api keys", "devops", "best practices", "prevention"]

---

### Psychology & Mental Models for Engineers

- [ ] **75** — The Psychology of Debugging: Why We Miss Obvious Errors
  - `slug`: psychology-of-debugging
  - `categories`: ["wiki"]
  - `tags`: ["debugging", "psychology", "cognitive bias", "confirmation bias", "mental models", "programming", "problem solving", "engineering mindset"]

- [ ] **76** — Mental Models Every Software Engineer Should Know
  - `slug`: mental-models-software-engineers
  - `categories`: ["wiki"]
  - `tags`: ["mental models", "first principles", "systems thinking", "engineering", "problem solving", "decision making", "productivity", "learning"]

- [ ] **77** — Flow State and Deep Work for Software Engineers
  - `slug`: flow-state-deep-work-software-engineers
  - `categories`: ["wiki"]
  - `tags`: ["flow state", "deep work", "productivity", "focus", "software engineering", "cal newport", "context switching", "concentration"]

- [ ] **78** — Cognitive Biases That Affect Code Reviews (And How to Counter Them)
  - `slug`: cognitive-biases-code-reviews
  - `categories`: ["wiki"]
  - `tags`: ["cognitive bias", "code review", "confirmation bias", "anchoring", "software engineering", "collaboration", "psychology", "team dynamics"]

- [ ] **79** — The Feynman Technique Applied to Learning New Technologies
  - `slug`: feynman-technique-learning-technology
  - `categories`: ["wiki"]
  - `tags`: ["feynman technique", "learning", "technology", "understanding", "mental models", "programming", "self-improvement", "study techniques"]

- [ ] **80** — First Principles Thinking in Software Architecture
  - `slug`: first-principles-thinking-software-architecture
  - `categories`: ["wiki"]
  - `tags`: ["first principles", "software architecture", "system design", "problem solving", "reasoning", "mental models", "engineering", "decision making"]

- [ ] **81** — The Sunk Cost Fallacy in Software Projects
  - `slug`: sunk-cost-fallacy-software-projects
  - `categories`: ["wiki"]
  - `tags`: ["sunk cost fallacy", "software projects", "decision making", "psychology", "refactoring", "rewrites", "technical debt", "engineering management"]

- [ ] **82** — Building Systems Thinking Skills as an Engineer
  - `slug`: systems-thinking-for-engineers
  - `categories`: ["wiki"]
  - `tags`: ["systems thinking", "engineering", "feedback loops", "complexity", "mental models", "problem solving", "architecture", "learning"]

- [ ] **83** — How to Give and Receive Technical Feedback Without Ego
  - `slug`: technical-feedback-without-ego
  - `categories`: ["wiki"]
  - `tags`: ["feedback", "code review", "ego", "collaboration", "team dynamics", "psychology", "software engineering", "communication", "growth mindset"]

- [ ] **84** — Managing Decision Fatigue as a Developer
  - `slug`: managing-decision-fatigue-developers
  - `categories`: ["wiki"]
  - `tags`: ["decision fatigue", "productivity", "developer", "mental health", "defaults", "systems", "automation", "focus", "psychology"]

---

### Go Deep: How Things Work

- [ ] **85** — How SSH Works Internally: The Protocol Deep Dive
  - `slug`: how-ssh-works-internally
  - `categories`: ["wiki"]
  - `tags`: ["ssh", "protocol", "internals", "encryption", "key exchange", "diffie-hellman", "networking", "security", "linux"]

- [ ] **86** — How Modern CPUs Execute Code Out of Order
  - `slug`: how-cpus-execute-out-of-order
  - `categories`: ["wiki"]
  - `tags`: ["cpu", "out-of-order execution", "speculative execution", "pipeline", "branch prediction", "hardware", "performance", "computer architecture"]

- [ ] **87** — How Memory Allocators Work: malloc Under the Hood
  - `slug`: how-memory-allocators-work-malloc
  - `categories`: ["wiki"]
  - `tags`: ["memory allocator", "malloc", "heap", "memory management", "c", "glibc", "jemalloc", "tcmalloc", "internals", "performance"]

- [ ] **88** — How Garbage Collection Works in Python and Go
  - `slug`: garbage-collection-python-go-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["garbage collection", "python", "go", "memory management", "gc", "reference counting", "mark and sweep", "generational gc", "internals"]

- [ ] **89** — How Databases Use Bloom Filters to Speed Up Lookups
  - `slug`: bloom-filters-databases-explained
  - `categories`: ["wiki"]
  - `tags`: ["bloom filter", "probabilistic data structure", "database", "rocksdb", "cassandra", "performance", "false positive", "hashing", "internals"]

- [ ] **90** — How Consistent Hashing Works and Why Distributed Systems Use It
  - `slug`: consistent-hashing-explained
  - `categories`: ["wiki"]
  - `tags`: ["consistent hashing", "distributed systems", "load balancing", "cache", "ring", "virtual nodes", "backend", "scalability", "architecture"]

---

### Data, Storage & Databases

- [ ] **91** — Time-Series Databases Explained: InfluxDB and TimescaleDB
  - `slug`: time-series-databases-influxdb-timescaledb
  - `categories`: ["wiki", "SQL"]
  - `tags`: ["time-series", "influxdb", "timescaledb", "database", "metrics", "monitoring", "iot", "analytics", "postgresql", "backend"]

- [ ] **92** — When to Use a Graph Database (and How They Work)
  - `slug`: graph-databases-when-and-how
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["graph database", "neo4j", "relationships", "nosql", "backend", "social network", "recommendation", "query", "cypher"]

- [ ] **93** — SQLite: The Most Deployed Database in the World
  - `slug`: sqlite-the-most-deployed-database
  - `categories`: ["wiki", "SQL"]
  - `tags`: ["sqlite", "database", "embedded database", "sql", "lightweight", "mobile", "local-first", "backend", "file-based", "python"]

- [ ] **94** — Understanding Database Vacuuming and Table Bloat in PostgreSQL
  - `slug`: postgresql-vacuum-table-bloat-explained
  - `categories`: ["wiki", "SQL"]
  - `tags`: ["postgresql", "vacuum", "autovacuum", "table bloat", "mvcc", "dead tuples", "database maintenance", "performance", "sql"]

---

### Career, Craft & Productivity

- [x] **95** — How to Read Technical Documentation Effectively
  - `slug`: how-to-read-technical-documentation
  - `categories`: ["wiki"]
  - `tags`: ["technical documentation", "reading", "learning", "productivity", "engineering", "self-improvement", "reference docs", "tutorials"]

- [x] **96** — The Art of the Technical Deep Dive: How to Understand Any System
  - `slug`: how-to-do-a-technical-deep-dive
  - `categories`: ["wiki"]
  - `tags`: ["technical deep dive", "learning", "systems", "engineering", "curiosity", "reading code", "understanding", "methodology", "research"]

- [x] **97** — Code Review Best Practices: What to Look For and What to Skip
  - `slug`: code-review-best-practices
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["code review", "best practices", "collaboration", "software engineering", "feedback", "pull requests", "quality", "team", "checklist"]

- [x] **98** — Technical Debt: When to Pay It Down and When to Ignore It
  - `slug`: technical-debt-when-to-pay-down
  - `categories`: ["wiki"]
  - `tags`: ["technical debt", "software engineering", "refactoring", "architecture", "trade-offs", "engineering management", "code quality", "maintenance"]

- [x] **99** — Writing Technical Blog Posts That Actually Help People
  - `slug`: writing-technical-blog-posts-that-help
  - `categories`: ["wiki"]
  - `tags`: ["technical writing", "blogging", "communication", "software engineering", "documentation", "teaching", "knowledge sharing", "tutorials"]

- [x] **100** — Building a Second Brain as a Developer: Notes, References, and Recall
  - `slug`: second-brain-for-developers
  - `categories`: ["wiki"]
  - `tags`: ["second brain", "note-taking", "knowledge management", "obsidian", "zettelkasten", "productivity", "developer", "learning", "recall"]

---

### Algorithms & Data Structures

- [ ] **101** — Sliding Window Technique Explained: Fixed and Variable Size Patterns
  - `slug`: sliding-window-technique-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["sliding window", "algorithms", "data structures", "arrays", "patterns", "programming", "interview prep", "problem solving"]

- [ ] **102** — Two Pointers Technique: Patterns and When to Use Them
  - `slug`: two-pointers-technique-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["two pointers", "algorithms", "arrays", "data structures", "programming", "patterns", "problem solving", "sorted arrays"]

- [ ] **103** — Dynamic Programming Patterns Explained: From 1D to Knapsack
  - `slug`: dynamic-programming-patterns-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["dynamic programming", "algorithms", "knapsack", "memoization", "tabulation", "programming", "problem solving", "interview prep"]

- [ ] **104** — Union-Find (Disjoint Set) Explained with Practical Use Cases
  - `slug`: union-find-disjoint-set-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["union-find", "disjoint set", "algorithms", "data structures", "path compression", "graphs", "programming", "problem solving"]

- [ ] **105** — Binary Search on the Answer: A Pattern Beyond Sorted Arrays
  - `slug`: binary-search-on-the-answer-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["binary search", "algorithms", "problem solving", "programming", "search space", "optimization", "interview prep"]

- [ ] **106** — Topological Sort Explained: Kahn's Algorithm and DFS
  - `slug`: topological-sort-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["topological sort", "graphs", "algorithms", "kahn's algorithm", "dfs", "dag", "programming", "problem solving"]

---

### Java Concurrency & Spring Boot

- [ ] **107** — Java Concurrency Explained: Threads, Locks, and the Java Memory Model
  - `slug`: java-concurrency-threads-locks-memory-model
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["java", "concurrency", "threads", "java memory model", "synchronized", "locks", "backend", "multithreading"]

- [ ] **108** — volatile vs synchronized in Java: What Each One Actually Guarantees
  - `slug`: volatile-vs-synchronized-java-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["java", "volatile", "synchronized", "concurrency", "visibility", "atomicity", "java memory model", "multithreading"]

- [ ] **109** — Java's ThreadPoolExecutor Explained: Pools, Queues, and Rejection Policies
  - `slug`: java-threadpoolexecutor-explained
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["java", "threadpoolexecutor", "thread pools", "concurrency", "executors", "backend", "queues", "rejection policy"]

- [ ] **110** — CompletableFuture Explained: Composing Async Code in Java
  - `slug`: java-completablefuture-explained
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["java", "completablefuture", "async", "concurrency", "backend", "futures", "non-blocking", "composition"]

- [ ] **111** — How Java's ConcurrentHashMap Works Internally
  - `slug`: java-concurrenthashmap-internals
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["java", "concurrenthashmap", "concurrency", "internals", "cas", "bin locking", "data structures", "backend"]

- [ ] **112** — Spring Boot Bean Lifecycle Explained
  - `slug`: spring-boot-bean-lifecycle-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["spring boot", "java", "bean lifecycle", "dependency injection", "backend", "spring framework", "beanpostprocessor"]

- [ ] **113** — The N+1 Query Problem in ORMs and How to Fix It
  - `slug`: n-plus-one-query-problem-orms
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["n+1 query", "orm", "database", "performance", "backend", "hibernate", "sql", "eager loading", "lazy loading"]

- [ ] **114** — Implementing Resilience Patterns in Spring Boot with Resilience4j
  - `slug`: resilience4j-spring-boot-guide
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["resilience4j", "spring boot", "circuit breaker", "retry", "rate limiter", "bulkhead", "java", "fault tolerance", "backend"]

---

### Go Internals

- [ ] **115** — How the Go Scheduler Works: The GMP Model Explained
  - `slug`: go-scheduler-gmp-model-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["go", "golang", "scheduler", "gmp model", "goroutines", "concurrency", "runtime", "internals"]

- [ ] **116** — Go Generics Explained: When Type Parameters Help (and When They Don't)
  - `slug`: go-generics-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["go", "golang", "generics", "type parameters", "constraints", "programming", "go 1.18", "readability"]

---

### Protocols & Messaging

- [ ] **117** — Protocol Buffers Explained: Binary Encoding and Schema Evolution
  - `slug`: protocol-buffers-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["protobuf", "protocol buffers", "grpc", "binary encoding", "serialization", "schema evolution", "backend", "api"]

- [ ] **118** — Kafka Producer Acks and Delivery Guarantees Explained
  - `slug`: kafka-producer-acks-delivery-guarantees
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["kafka", "producer", "acks", "delivery guarantees", "idempotent producer", "messaging", "backend", "distributed systems"]

- [ ] **119** — Kafka Consumer Groups and Partition Rebalancing Explained
  - `slug`: kafka-consumer-groups-rebalancing-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["kafka", "consumer groups", "rebalancing", "partitions", "offsets", "messaging", "backend", "distributed systems"]

- [ ] **120** — Server-Sent Events (SSE) Explained: The Simpler Alternative to WebSockets
  - `slug`: server-sent-events-sse-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["server-sent events", "sse", "websockets", "real-time", "eventsource", "http", "streaming", "backend", "frontend"]

---

### Distributed Systems Theory

- [ ] **121** — The Outbox Pattern: Reliable Event Publishing with Databases
  - `slug`: outbox-pattern-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["outbox pattern", "distributed transactions", "kafka", "event-driven", "microservices", "backend", "reliability", "database"]

- [ ] **122** — Two-Phase Commit Explained (and Why It Doesn't Scale)
  - `slug`: two-phase-commit-explained
  - `categories`: ["wiki"]
  - `tags`: ["two-phase commit", "2pc", "distributed transactions", "distributed systems", "consensus", "coordinator", "backend", "architecture"]

- [ ] **123** — Raft Consensus Algorithm Explained
  - `slug`: raft-consensus-algorithm-explained
  - `categories`: ["wiki"]
  - `tags`: ["raft", "consensus", "distributed systems", "leader election", "log replication", "etcd", "consul", "quorum", "architecture"]

- [ ] **124** — PACELC Theorem: Extending CAP with Latency Trade-offs
  - `slug`: pacelc-theorem-explained
  - `categories`: ["wiki"]
  - `tags`: ["pacelc", "cap theorem", "distributed systems", "consistency", "latency", "trade-offs", "architecture", "system design"]

- [ ] **125** — Distributed Unique ID Generation: The Snowflake Algorithm Explained
  - `slug`: snowflake-id-generation-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["snowflake id", "distributed id", "unique id generation", "distributed systems", "backend", "system design", "clock skew"]

---

### Databases

- [ ] **126** — Cassandra Data Modeling: Partition Keys and Clustering Keys Explained
  - `slug`: cassandra-data-modeling-explained
  - `categories`: ["wiki", "SQL"]
  - `tags`: ["cassandra", "data modeling", "partition key", "clustering key", "nosql", "wide-column", "database", "query-first design"]

- [ ] **127** — How Cassandra's Read and Write Paths Work
  - `slug`: cassandra-read-write-paths-explained
  - `categories`: ["wiki", "SQL"]
  - `tags`: ["cassandra", "read path", "write path", "commit log", "memtable", "sstable", "compaction", "database internals"]

- [ ] **128** — SQL vs NoSQL: A Practical Decision Framework
  - `slug`: sql-vs-nosql-decision-framework
  - `categories`: ["wiki", "SQL"]
  - `tags`: ["sql", "nosql", "database selection", "acid", "consistency", "scalability", "architecture", "backend", "system design"]

- [ ] **129** — Wide-Column Databases Explained: Cassandra vs Bigtable vs HBase
  - `slug`: wide-column-databases-explained
  - `categories`: ["wiki", "SQL"]
  - `tags`: ["wide-column database", "cassandra", "bigtable", "hbase", "nosql", "database", "distributed database", "time-series"]

- [ ] **130** — Elasticsearch Explained: Inverted Indexes, Analyzers, and Queries
  - `slug`: elasticsearch-explained
  - `categories`: ["wiki"]
  - `tags`: ["elasticsearch", "inverted index", "full-text search", "analyzers", "opensearch", "search", "backend", "aggregations"]

- [ ] **131** — Distributed Locks with Redis: SETNX, Redlock, and the Controversy Around It
  - `slug`: redis-distributed-locks-redlock-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["redis", "distributed locks", "redlock", "setnx", "concurrency", "distributed systems", "backend", "consistency"]

- [ ] **132** — Redis Cluster vs Sentinel: High Availability Explained
  - `slug`: redis-cluster-vs-sentinel-explained
  - `categories`: ["wiki"]
  - `tags`: ["redis", "redis cluster", "redis sentinel", "high availability", "failover", "sharding", "backend", "database"]

---

### Design & Architecture

- [ ] **133** — SOLID Principles Explained with Real Code Examples
  - `slug`: solid-principles-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["solid principles", "object-oriented design", "software design", "clean code", "srp", "dependency inversion", "programming", "architecture"]

- [ ] **134** — Common Design Patterns Every Developer Should Know
  - `slug`: common-design-patterns-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["design patterns", "singleton", "factory", "strategy pattern", "observer pattern", "decorator pattern", "software design", "programming"]

- [ ] **135** — How to Implement an LRU Cache from Scratch
  - `slug`: implement-lru-cache-from-scratch
  - `categories`: ["Programming", "Tutorials"]
  - `tags`: ["lru cache", "data structures", "caching", "hashmap", "linked list", "from scratch", "tutorial", "interview prep"]

- [ ] **136** — The N+1 Problem in GraphQL and How DataLoader Solves It
  - `slug`: graphql-n-plus-one-dataloader-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["graphql", "dataloader", "n+1 problem", "batching", "resolvers", "backend", "performance", "api"]

---

### Kubernetes, Networking & Security

- [ ] **137** — Kubernetes Autoscaling Explained: HPA, VPA, and Cluster Autoscaler
  - `slug`: kubernetes-autoscaling-hpa-vpa-explained
  - `categories`: ["wiki", "Tutorials"]
  - `tags`: ["kubernetes", "autoscaling", "hpa", "vpa", "cluster autoscaler", "devops", "scalability", "k8s"]

- [ ] **138** — Kubernetes Networking Explained: Services, Ingress, and Network Policies
  - `slug`: kubernetes-networking-services-ingress-explained
  - `categories`: ["wiki"]
  - `tags`: ["kubernetes", "networking", "services", "ingress", "network policy", "cni", "k8s", "devops"]

- [ ] **139** — Kubernetes RBAC Explained: Roles, Bindings, and Least Privilege
  - `slug`: kubernetes-rbac-explained
  - `categories`: ["wiki", "Tutorials"]
  - `tags`: ["kubernetes", "rbac", "roles", "role bindings", "security", "least privilege", "k8s", "devops"]

- [ ] **140** — Service Discovery Patterns: Client-Side vs Server-Side
  - `slug`: service-discovery-patterns-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["service discovery", "microservices", "client-side discovery", "server-side discovery", "consul", "eureka", "backend", "architecture"]

- [ ] **141** — mTLS Explained: Mutual TLS for Service-to-Service Authentication
  - `slug`: mtls-mutual-tls-explained
  - `categories`: ["wiki"]
  - `tags`: ["mtls", "mutual tls", "tls", "zero trust", "security", "service-to-service", "certificates", "encryption"]

- [ ] **142** — SPIFFE and SPIRE Explained: Workload Identity for Zero-Trust Systems
  - `slug`: spiffe-spire-workload-identity-explained
  - `categories`: ["wiki"]
  - `tags`: ["spiffe", "spire", "workload identity", "zero trust", "security", "certificates", "svid", "microservices"]

- [ ] **143** — Docker Multi-Stage Builds: Smaller, Faster, Safer Images
  - `slug`: docker-multi-stage-builds-explained
  - `categories`: ["Tutorials", "Programming"]
  - `tags`: ["docker", "multi-stage builds", "dockerfile", "container images", "devops", "optimization", "best practices"]

- [ ] **144** — VPC Design Fundamentals: Public and Private Subnets Explained
  - `slug`: vpc-design-fundamentals-explained
  - `categories`: ["wiki"]
  - `tags`: ["vpc", "subnets", "cloud networking", "aws", "gcp", "nat gateway", "security groups", "infrastructure"]

---

### Observability & AI Systems

- [ ] **145** — SLIs, SLOs, and Error Budgets Explained
  - `slug`: sli-slo-error-budgets-explained
  - `categories`: ["wiki"]
  - `tags`: ["sli", "slo", "sla", "error budget", "sre", "observability", "reliability", "monitoring"]

- [ ] **146** — LLM Inference Optimization: KV Cache, Quantization, and Speculative Decoding Explained
  - `slug`: llm-inference-optimization-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["llm inference", "kv cache", "quantization", "speculative decoding", "vllm", "ai", "machine learning", "performance"]

- [ ] **147** — Feature Stores Explained: Solving the Training-Serving Skew Problem
  - `slug`: feature-stores-training-serving-skew-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["feature store", "machine learning", "training-serving skew", "mlops", "ml pipelines", "backend", "data engineering"]

---

### Modern Java

- [ ] **148** — Java Records and Sealed Classes: Modern Java in Practice
  - `slug`: java-records-sealed-classes-explained
  - `categories`: ["Programming", "wiki"]
  - `tags`: ["java", "records", "sealed classes", "pattern matching", "modern java", "java 21", "programming", "backend"]

- [ ] **149** — Virtual Threads in Java 21: Project Loom Explained
  - `slug`: java-virtual-threads-project-loom-explained
  - `categories`: ["wiki", "Programming"]
  - `tags`: ["java", "virtual threads", "project loom", "concurrency", "structured concurrency", "java 21", "backend", "performance"]
