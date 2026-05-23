---
layout: post
title: "Regular Expressions Cheat Sheet with Real-World Examples"
date: "2026-05-24 00:00:00 +0530"
slug: regular-expressions-cheat-sheet
description: "A comprehensive regular expressions cheat sheet with real-world examples in Python, JavaScript, grep, and sed — covering anchors, groups, lookaheads, and common patterns."
categories: ["wiki", "Programming"]
tags: ["regex", "regular expressions", "cheatsheet", "pattern matching", "python", "javascript", "grep", "sed", "tutorial"]
---

Regular expressions are one of those tools that feel cryptic until they suddenly click — and then you start seeing patterns everywhere. They show up in every language and half the Unix tools you use daily. This cheat sheet covers the syntax you'll reach for most often, with examples grounded in real tasks rather than contrived strings.

## The Building Blocks

### Literals and the Dot

```
hello          matches the exact string "hello"
hel.o          matches "hello", "helxo", "hel1o" — dot matches any character except newline
hel\.o         matches "hel.o" literally — backslash escapes the dot
```

### Anchors

```
^hello         matches "hello" at the start of a line
world$         matches "world" at the end of a line
^hello world$  matches the entire line "hello world"
\bword\b       matches "word" as a whole word (word boundary)
```

### Character Classes

```
[aeiou]        any single vowel
[^aeiou]       any character that is NOT a vowel
[a-z]          any lowercase letter
[A-Za-z0-9]   any alphanumeric character
[a-z_][a-z0-9_]* valid Python/JS identifier start
```

### Shorthand Classes

```
\d    digit: [0-9]
\D    non-digit: [^0-9]
\w    word character: [A-Za-z0-9_]
\W    non-word character
\s    whitespace: space, tab, newline
\S    non-whitespace
```

### Quantifiers

```
a?      zero or one "a" (optional)
a*      zero or more "a"
a+      one or more "a"
a{3}    exactly 3 "a"s
a{2,5}  between 2 and 5 "a"s
a{3,}   3 or more "a"s
```

By default, quantifiers are **greedy** — they match as much as possible. Add `?` to make them lazy:

```
<.+>    greedy: matches entire "<b>bold</b> and <i>italic</i>"
<.+?>   lazy:   matches "<b>", then "</b>", etc.
```

### Groups and Alternation

```
(cat|dog)        matches "cat" or "dog"
(gr(a|e)y)       matches "gray" or "grey"
(?:non-capturing) groups without capturing
```

## Python: `re` Module

```python
import re

text = "Order #12345 placed on 2024-03-15"

# Search anywhere in the string
m = re.search(r"\d{4}-\d{2}-\d{2}", text)
if m:
    print(m.group())  # 2024-03-15

# Find all matches
ids = re.findall(r"#(\d+)", text)
print(ids)  # ['12345']

# Substitute
result = re.sub(r"\d{4}-\d{2}-\d{2}", "[REDACTED]", text)
print(result)  # Order #12345 placed on [REDACTED]

# Compile for repeated use
pattern = re.compile(r"^\d{3}-\d{2}-\d{4}$")
print(bool(pattern.match("123-45-6789")))  # True
```

**Named groups** make captures readable:

```python
m = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", text)
if m:
    print(m.group("year"))   # 2024
    print(m.group("month"))  # 03
```

## JavaScript

```javascript
const text = "Contact us at support@example.com or sales@company.org"

// Test if a pattern matches
const emailPattern = /\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b/gi
console.log(emailPattern.test(text))  // true

// Find all matches
const emails = text.match(emailPattern)
console.log(emails)  // ['support@example.com', 'sales@company.org']

// Replace
const redacted = text.replace(emailPattern, "[EMAIL]")
console.log(redacted)  // Contact us at [EMAIL] or [EMAIL]

// Named groups (ES2018+)
const dateRe = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/
const m = "2024-03-15".match(dateRe)
console.log(m.groups.year)  // 2024
```

## grep

```bash
# Basic pattern
$ grep "error" /var/log/app.log

# Extended regex (-E) — enables +, ?, |, ()
$ grep -E "error|warn" /var/log/app.log

# Case-insensitive
$ grep -i "error" /var/log/app.log

# Show line numbers
$ grep -n "timeout" /var/log/app.log

# Invert match (lines that don't match)
$ grep -v "DEBUG" /var/log/app.log

# Count matches
$ grep -c "error" /var/log/app.log

# Show only the matching part
$ grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" access.log

# Match whole words
$ grep -w "fail" /var/log/app.log
```

## sed

```bash
# Substitute first match per line
$ sed 's/foo/bar/' file.txt

# Substitute all matches (global flag)
$ sed 's/foo/bar/g' file.txt

# Edit in place
$ sed -i 's/localhost/db.internal/g' config.yml

# Delete lines matching a pattern
$ sed '/^#/d' config.conf       # remove comment lines
$ sed '/^$/d' file.txt          # remove blank lines

# Print lines matching a pattern
$ sed -n '/ERROR/p' app.log

# Extract a capture group (GNU sed)
$ echo "Date: 2024-03-15" | sed -E 's/Date: ([0-9-]+)/\1/'
# 2024-03-15
```

## Lookaheads and Lookbehinds

Lookarounds match a position without consuming characters — they assert what's around the match but don't include it in the result.

```
price(?=\s*USD)    matches "price" only when followed by optional space then "USD"
price(?!\s*EUR)    matches "price" NOT followed by "EUR"
(?<=\$)\d+         matches digits preceded by "$" — but "$" not in result
(?<!\d)\d{4}       matches 4-digit number not preceded by another digit
```

Python example:

```python
import re

prices = "Total: $150 USD, Tax: €20 EUR"

# Extract only USD amounts
usd = re.findall(r"\$(\d+)(?=\s*USD)", prices)
print(usd)  # ['150']
```

## Common Patterns

```python
# Email (simplified)
r"[\w.+-]+@[\w-]+\.[a-z]{2,}"

# IPv4 address
r"\b(?:\d{1,3}\.){3}\d{1,3}\b"

# URL
r"https?://[^\s/$.?#].[^\s]*"

# Date YYYY-MM-DD
r"\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])"

# Indian phone number
r"(?:\+91[-\s]?)?[6-9]\d{9}"

# Hex color
r"#(?:[0-9a-fA-F]{3}){1,2}\b"

# Semantic version
r"\d+\.\d+\.\d+(?:-[\w.]+)?"

# Lines with only whitespace
r"^\s*$"
```

## Flags Reference

| Flag | Python | JS | Effect |
|---|---|---|---|
| Case-insensitive | `re.I` | `i` | `[a-z]` matches uppercase too |
| Multiline | `re.M` | `m` | `^`/`$` match line start/end |
| Dot-all | `re.S` | `s` | `.` matches newline |
| Verbose | `re.X` | — | Allows whitespace and comments in pattern |
| Global | — | `g` | Find all matches (not just first) |

## Conclusion

The biggest payoff from learning regex is recognizing when to stop: regex is excellent for validating and extracting patterns in single-line text, but it's the wrong tool for parsing HTML, JSON, or nested structures. For those, use a proper parser. Within its domain — log analysis, input validation, search-and-replace, text extraction — regex remains one of the most expressive tools in a developer's kit. Keep this cheat sheet nearby, and you'll find you reach for it more than you expect.
