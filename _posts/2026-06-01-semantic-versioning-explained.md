---
layout: post
title: "Semantic Versioning Explained: major.minor.patch and When to Bump"
date: "2026-06-01 00:00:00 +0530"
slug: semantic-versioning-explained
description: "Semantic versioning gives version numbers meaning. Learn what major, minor, and patch represent, when to bump each, and how semver works with npm, pip, and git tags."
categories: ["wiki", "Programming"]
tags: ["semantic versioning", "semver", "versioning", "releases", "npm", "git", "changelog", "api", "best practices"]
---

Version numbers should communicate something to the people reading them. `2.4.1` should tell you more than "this is newer than 2.4.0." Semantic Versioning (SemVer) is the widely adopted convention that gives version numbers a precise meaning: each component of `MAJOR.MINOR.PATCH` signals a specific kind of change to consumers of your software. It's the standard used by npm, pip, Cargo, Go modules, and most modern package ecosystems.

## The Format

```
MAJOR.MINOR.PATCH
  │     │     └─ Backwards-compatible bug fixes
  │     └─────── Backwards-compatible new features
  └─────────────  Breaking changes
```

A version of `0.0.0` means "just started." A version of `2.4.1` means: second major version (one breaking change milestone), fourth minor release (four feature additions since 2.0.0), first patch (one bug fix since 2.4.0).

## When to Bump Each Component

### PATCH — `2.4.0` → `2.4.1`

Bump patch when you fix a bug without changing the API or adding features. Existing code that works with `2.4.0` should work identically with `2.4.1`.

Examples:
- Fix a nil pointer dereference
- Correct an off-by-one error
- Fix a typo in an error message
- Handle an edge case that was crashing

### MINOR — `2.4.1` → `2.5.0`

Bump minor when you add functionality in a backwards-compatible way. Code written for `2.4.x` must continue to work with `2.5.0` — you only added things, you didn't remove or change anything existing.

Examples:
- Add a new API endpoint
- Add a new optional parameter to an existing function
- Add a new configuration option with a sensible default
- Deprecate something (but not remove it yet)

When you bump MINOR, reset PATCH to 0: `2.4.9` → `2.5.0`.

### MAJOR — `2.5.0` → `3.0.0`

Bump major when you make changes that break backwards compatibility. If users of `2.x` need to change their code to work with `3.0`, it's a major bump.

Examples:
- Remove a function, endpoint, or field
- Change the return type of a function
- Rename a required parameter
- Change authentication mechanism
- Drop support for a runtime version (e.g., Node 16 → require Node 20)

When you bump MAJOR, reset both MINOR and PATCH to 0: `2.5.3` → `3.0.0`.

## Pre-Release and Build Metadata

SemVer supports extensions for pre-release versions and build metadata:

```
1.0.0-alpha
1.0.0-alpha.1
1.0.0-beta.2
1.0.0-rc.1
1.0.0                 ← stable release
1.0.0+build.20260601  ← build metadata (ignored in comparisons)
```

Pre-release versions (`-alpha`, `-rc.1`) have lower precedence than the release version: `1.0.0-rc.1 < 1.0.0`.

In npm:

```bash
$ npm version prerelease --preid=beta
# 1.0.0 → 1.0.1-beta.0

$ npm version prerelease
# 1.0.1-beta.0 → 1.0.1-beta.1

$ npm version patch
# 1.0.1-beta.1 → 1.0.1
```

## Version 0.x — Initial Development

SemVer treats `0.x.y` as a special case: the public API is considered unstable and anything can change in a minor version bump. `0.4.0` to `0.5.0` is allowed to be breaking.

Use `0.x` while the API is in flux. Ship `1.0.0` when you're ready to commit to backwards compatibility. This is a signal to users that the API has stabilized.

## Version Ranges in Package Managers

Understanding how package managers interpret SemVer version ranges prevents surprise upgrades.

### npm / package.json

```json
{
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "~4.17.21",
    "uuid": "9.0.0"
  }
}
```

| Range | Meaning | Allows |
|---|---|---|
| `^4.18.0` | Compatible with 4.18.0 | `>=4.18.0 <5.0.0` (minor and patch) |
| `~4.17.21` | Approximately equivalent | `>=4.17.21 <4.18.0` (patch only) |
| `9.0.0` | Exact version | Only `9.0.0` |
| `>=4.0.0` | Greater than or equal | Any version ≥4.0.0 |
| `4.x` | Wildcard | `>=4.0.0 <5.0.0` |

The `^` (caret) is the default when you `npm install` something. It allows minor and patch upgrades but not major — it trusts that minor bumps are backwards-compatible.

### pip / requirements.txt

```
requests>=2.28.0,<3.0.0   # compatible release range
flask~=3.0.0              # ~= means >=3.0.0, ==3.* (same as caret)
django==4.2.13            # exact pin
```

### Go modules

Go uses import paths with major versions embedded for v2+:

```go
import "github.com/some/library/v2"
```

This is a Go-specific convention to allow different major versions to coexist in the same binary.

## Tagging Releases in Git

The conventional way to mark a release in git:

```bash
$ git tag -a v2.5.0 -m "Release 2.5.0"
$ git push origin v2.5.0
```

```bash
$ git tag --list
v2.3.0
v2.4.0
v2.4.1
v2.5.0
```

The `v` prefix is a convention (not part of SemVer itself) that most ecosystems follow. GitHub's release UI and most CI tools recognize `v*` tags as release tags.

To automate tagging based on Conventional Commits:

```bash
$ npm install -g standard-version
$ standard-version   # bumps version, updates CHANGELOG.md, creates git tag
```

```
✔ bumping version in package.json from 2.4.1 to 2.5.0
✔ outputting changes to CHANGELOG.md
✔ committing package.json and CHANGELOG.md
✔ tagging release v2.5.0
```

## Common Mistakes

**Bumping patch when a minor is warranted** — if you added a new function that didn't exist before, it's a minor bump even if it feels small. Users might be running `~1.2.0` (patch-only range) and won't get the new function.

**Treating `0.x` as stable** — don't ship a library at `0.1.0` and tell users to depend on it in production without warning them that the API can change in any `0.x` release.

**Bumping major too aggressively** — internal refactors that don't touch the public API are not breaking changes. Only surface area that your users interact with counts.

**Not zeroing out lower components** — `2.4.9` → `2.5.9` is wrong. Minor bumps reset patch: `2.4.9` → `2.5.0`.

## Conclusion

SemVer gives version numbers a contract: PATCH means safe to upgrade, MINOR means new things available but nothing broken, MAJOR means review the changelog before upgrading. Following this contract consistently lets package managers automate safe upgrades and signals trust to your users. Pair it with Conventional Commits for automated version bumping, and you get a release process where the version number is derived from the code changes themselves rather than decided arbitrarily.
