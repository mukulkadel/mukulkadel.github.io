---
layout: post
title: "Writing Effective Commit Messages: Conventional Commits Guide"
date: "2026-06-01 00:00:00 +0530"
slug: writing-effective-commit-messages
description: "Good commit messages make git history readable and automate changelogs. The Conventional Commits spec gives you a simple format to follow consistently across a team."
categories: ["wiki", "Programming"]
tags: ["git", "commit messages", "conventional commits", "semantic commits", "version control", "collaboration", "changelog", "best practices"]
---

`git log` on most projects reads like a disaster: "fix", "WIP", "changes", "more changes", "asdfgh". These messages are useless for understanding why a change was made, debugging a regression, or generating a changelog. Writing good commit messages is a low-effort habit that pays compound interest — six months later, when you're tracking down why a behavior changed, a clear commit history is the fastest path to the answer. The Conventional Commits specification makes this consistent and machine-readable too.

## The Anatomy of a Good Commit Message

The classic rule from Tim Pope's git guidelines: a commit message has a subject line, an optional body, and an optional footer, separated by blank lines.

```
<type>(<scope>): <short summary>

<body: explain WHY, not WHAT>

<footer: breaking changes, issue refs>
```

The subject line should:
- Be 50 characters or fewer
- Use the imperative mood ("add", "fix", "remove" — not "added", "fixing", "removed")
- Not end with a period
- Describe *what* the commit does, not how

The body should explain *why* the change was made. The diff already shows what changed; the message should add context the diff can't.

## The Conventional Commits Specification

[Conventional Commits](https://www.conventionalcommits.org/) is a lightweight convention on top of commit messages. It defines a structured format that tooling can parse to automate changelogs and version bumps.

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to use |
|---|---|
| `feat` | A new feature visible to users |
| `fix` | A bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code restructuring without behavior change |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `build` | Build system, dependency updates |
| `ci` | CI configuration changes |
| `chore` | Everything else (scripts, tooling) |

### Scopes

The scope is optional and specifies what part of the codebase the change touches. Use whatever makes sense for your project:

```
feat(auth): add OAuth2 login flow
fix(api): handle null user in session middleware
docs(readme): update local setup instructions
perf(db): add index on users.email column
```

### Real examples

```
feat(payments): add Stripe webhook handler for subscription events

Previously we only handled one-time payment webhooks. This adds
support for subscription.created, subscription.updated, and
subscription.deleted events, updating the user's plan status in
the database accordingly.

Closes #847
```

```
fix(auth): prevent session fixation on login

Regenerate the session ID after successful authentication to prevent
session fixation attacks. The old session data is copied to the new
session before the ID is rotated.

CVE-2024-xxxx
```

```
refactor(cache): replace custom LRU with redis-lru package

The custom implementation had an off-by-one bug in the eviction
logic (see issue #291) and lacked proper TTL support. redis-lru
is well-tested and covers both needs.

BREAKING CHANGE: Cache.get() now returns a Promise instead of
a value. All callers updated in this commit.
```

## Breaking Changes

A breaking change is signaled two ways:

1. Add a `!` after the type/scope: `feat(api)!: remove deprecated v1 endpoints`
2. Add a `BREAKING CHANGE:` footer with a description

Both can be used together. Tooling (like semantic-release) uses this to bump the major version automatically.

```
feat(api)!: remove GET /api/v1/users endpoint

The v1 endpoint was deprecated in 2.0.0 and has been removed.
Clients should migrate to GET /api/v2/users which returns
paginated results and includes the `role` field.

BREAKING CHANGE: GET /api/v1/users no longer exists. Returns 410 Gone.
```

## Automating Changelogs

The payoff for following Conventional Commits is automation. Tools parse your git history and generate a changelog without you writing one manually.

### Using `conventional-changelog`

```bash
$ npm install -g conventional-changelog-cli
$ conventional-changelog -p conventionalcommits -i CHANGELOG.md -s
```

```markdown
# Changelog

## [3.2.0] - 2026-06-01

### Features
- **payments:** add Stripe webhook handler for subscription events (#847)
- **auth:** support passkey authentication

### Bug Fixes
- **auth:** prevent session fixation on login
- **api:** handle null user in session middleware

### Performance Improvements
- **db:** add index on users.email column
```

### Using `semantic-release`

`semantic-release` goes further — it reads your commit history and automatically determines the next version number (patch/minor/major), creates a GitHub release, publishes to npm, and generates the changelog. All you do is write proper commit messages.

```bash
$ npm install --save-dev semantic-release
```

In CI:

```yaml
- name: Release
  run: npx semantic-release
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

A `feat:` commit triggers a minor version bump. A `fix:` triggers a patch. A `BREAKING CHANGE:` triggers a major bump. The version is derived entirely from commit messages.

## Enforcing the Convention with Commitlint

`commitlint` checks commit messages at commit time via a git hook. Add it to your project:

```bash
$ npm install --save-dev @commitlint/cli @commitlint/config-conventional husky
$ echo "module.exports = { extends: ['@commitlint/config-conventional'] };" > commitlint.config.js
$ npx husky install
$ npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```

Now any commit that doesn't follow the convention is rejected immediately:

```bash
$ git commit -m "stuff"
⧗   input: stuff
✖   subject may not be empty [subject-empty]
✖   type may not be empty [type-empty]

✖   found 2 problems, 0 warnings
```

```bash
$ git commit -m "fix(auth): prevent session fixation on login"
[main 3a9f2e1] fix(auth): prevent session fixation on login
```

## Quick Reference

```
feat: new feature
fix: bug fix
docs: documentation
style: formatting only
refactor: restructure without behavior change
perf: performance improvement
test: tests only
build: build/dependency changes
ci: CI config
chore: everything else

feat(scope): description        scoped change
feat!: description              breaking change
feat(scope)!: description       scoped breaking change

BREAKING CHANGE: description    breaking change footer
Closes #123                     issue reference footer
```

## Conclusion

Good commit messages are a gift to your future self and your teammates. The Conventional Commits format adds just enough structure to make messages consistent, machine-readable, and useful for automated tooling — without requiring much more effort than writing a freeform message. Set up commitlint so the convention is enforced automatically, and you get changelog generation and semantic versioning for free as a byproduct.
