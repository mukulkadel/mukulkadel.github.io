---
layout: post
title: "Code Review Best Practices: What to Look For and What to Skip"
date: "2026-06-02 00:00:00 +0530"
slug: code-review-best-practices
description: "Effective code reviews catch real problems without slowing teams down. Here's what to focus on, what to automate away, and how to give feedback that actually lands."
categories: ["wiki", "Programming"]
tags: ["code review", "best practices", "collaboration", "software engineering", "feedback", "pull requests", "quality", "team", "checklist"]
---

Code review is one of the highest-leverage activities on a software team — and also one of the most commonly done badly. Reviews that take days, comments that devolve into style debates, feedback that feels personal rather than technical, PRs that land without meaningful scrutiny — all of these are symptoms of a review process without a clear mental model. This post covers what to actually look for in a review, how to structure your feedback, and — just as importantly — what to automate away so reviewers can focus on things that actually require human judgment.

## Automate Everything That Doesn't Require Judgment

Before a human reviewer sees a PR, automated checks should have already caught:

- **Formatting** — Prettier, Black, gofmt, rustfmt. There should be zero formatting comments in a code review in 2026.
- **Linting** — ESLint, Ruff, staticcheck, clippy. Style guide violations, unused variables, obvious bugs.
- **Type errors** — mypy, tsc, pyright. Type mismatches don't need human attention.
- **Test coverage** — CI fails if coverage drops below the threshold.
- **Secret scanning** — gitleaks or similar catches committed credentials.

If your team is spending review time on comments like "missing blank line" or "prefer double quotes", that's a misconfigured CI pipeline, not a code review problem. Get a linter and a pre-commit hook in place first. This frees reviewers to focus on things only humans can assess.

## What to Actually Look For

### Correctness

This is the highest priority. Does the code do what it claims to do? Not "does it look right" — actually trace through the logic.

- Does it handle the edge cases? Empty input, null/nil, zero, very large values, concurrent access?
- Does it handle errors — not just the happy path?
- Are there off-by-one errors in loops, slice operations, pagination?
- Do any assumptions the code makes fail in production conditions?

```python
# Looks fine at first glance
def get_user_page(users, page, per_page=20):
    start = page * per_page
    return users[start:start + per_page]

# Problem: page=0 returns first page, but what does page=-1 return?
# users[-20:0] returns an empty list, not an error — silently wrong behavior
```

This is the category where reviewers add the most value. A linter can't tell you that your pagination silently returns empty results for negative page numbers.

### Security

Security issues are often invisible to the person who wrote the code because they're thinking about the happy path.

Things to watch for:
- **Injection vectors** — user input reaching a SQL query, shell command, or template without sanitization
- **Authentication checks** — is this endpoint actually guarded? Is the permission check happening on the right object?
- **Sensitive data in logs** — passwords, tokens, PII being printed or logged
- **Insecure defaults** — `verify=False` on HTTPS calls, world-readable file permissions
- **Mass assignment** — accepting arbitrary fields from user input and persisting them

```python
# Dangerous: user input passed directly to shell
subprocess.run(f"convert {filename} output.png", shell=True)

# Safer: pass as a list, no shell interpolation
subprocess.run(["convert", filename, "output.png"])
```

### Maintainability

Will someone (including the author, in six months) be able to understand and change this code?

- Is the logic too deeply nested to follow?
- Are functions doing too many things — can you summarize what a function does in one sentence?
- Is the naming clear? Does `process_data` tell you anything? Does `normalize_and_deduplicate_users` tell you a lot?
- Are there magic numbers or magic strings that should be named constants?
- Is there dead code, commented-out code, or `TODO`s with no issue reference?

### Test Quality

Checking that tests exist isn't enough. Check that they're testing the right things.

- Do the tests actually verify the behavior, or just call the function and assert it doesn't crash?
- Are the edge cases tested — not just the happy path?
- Are the tests fragile? Tests that are tightly coupled to implementation details break whenever you refactor, even when nothing is wrong.
- Is there a test for the bug this PR is fixing? (A regression test ensures it doesn't come back.)

### The Design Question

Zoom out from individual lines and ask: does this change fit naturally into the existing codebase, or does it create new inconsistency? If you're seeing a new pattern that duplicates something that already exists, that's worth flagging. Similarly, if a function is growing to 200 lines, it's worth asking whether it should be split, even if each individual line is correct.

## What to Skip (or Deprioritize)

**Stylistic preferences** where no objective argument exists. If your linter allows both and the code is consistent, "I prefer X" is not a code review comment. It's a distraction.

**Speculative future-proofing.** "What if we need to support multiple databases later?" is not a reason to add an abstraction layer that isn't needed now. Review what's in the PR, not what might be needed someday.

**Small inefficiencies in non-critical paths.** Micro-optimizations in code that runs once at startup or handles ten requests per day are noise. Reserve performance feedback for hot paths with evidence.

**Things the author clearly already knows.** If you see a `TODO` comment that says "clean this up in a follow-up PR", you don't need to flag it as a review comment. They know.

## How to Write Review Feedback

The way feedback is worded matters as much as the content.

**Ask questions instead of making declarations when you're uncertain.** "Did you consider what happens when X is null?" lands differently than "This will break when X is null." The first acknowledges you might be missing context; the second assumes you're right and can feel dismissive.

**Distinguish blocking from non-blocking comments.** Not everything you write should block a merge. Use prefixes like `nit:` for minor style notes, `suggestion:` for optional improvements, and `blocking:` for things that must be addressed. This prevents reviewers from accidentally treating a comment about variable naming with the same weight as a security issue.

```
blocking: This call to subprocess.run with shell=True is an injection 
          risk if filename comes from user input.

nit: `process_data` → `normalize_phone_numbers` would make the intent clearer.

suggestion: We could use a dataclass here instead of a dict to get type 
            checking, but a dict works fine if you prefer.
```

**Explain the why.** "Use a parameterized query here" is less useful than "Use a parameterized query here — this is currently vulnerable to SQL injection because the user ID is interpolated directly into the query string." The explanation helps the author learn, not just fix.

**Approve when it's good enough, not only when it's perfect.** A PR doesn't need to be the best possible version of that code — it needs to be correct, not harmful to the codebase, and better than what was there before. Holding a PR for hypothetical improvements that may never matter creates the kind of review culture where developers dread opening PRs.

## The Author's Responsibilities

Code review isn't only the reviewer's job. The author can make a review faster and more effective:

- Write a clear PR description. What does this change? Why? What are the non-obvious parts?
- Keep PRs small. A 2000-line PR takes hours to review. A 200-line PR takes 15 minutes.
- Self-review before requesting review — read your own diff and leave comments on the non-obvious parts.
- Respond to every comment, even if just "done" or "won't fix, because X."

## Conclusion

Effective code review is about finding real problems — correctness bugs, security issues, maintainability concerns — not policing style or accumulating comment counts. Automate what can be automated, focus human attention on what requires judgment, write feedback that teaches rather than criticizes, and keep PRs small enough to review thoroughly. A team that does this well ships faster than one that doesn't, not slower.
