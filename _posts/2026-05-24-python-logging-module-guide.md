---
layout: post
title: "Python logging Module: A Practical Guide for Real Applications"
date: "2026-05-24 00:00:00 +0530"
slug: python-logging-module-guide
description: "A practical guide to Python's logging module — covering log levels, handlers, formatters, structured logging, and patterns for production applications."
categories: ["Programming", "Tutorials"]
tags: ["python", "logging", "observability", "debugging", "tutorial", "handlers", "formatters", "production", "backend"]
---

`print()` statements are fine for a quick debug session, but they don't survive production. You can't filter them by severity, redirect them to a file, rotate them when they get large, or ship them to a log aggregator. Python's built-in `logging` module handles all of this, and once you understand its architecture, configuring it for any scenario takes about ten lines.

## The Basics: Five Log Levels

```python
import logging

logging.debug("Detailed diagnostic info")
logging.info("Normal application events")
logging.warning("Something unexpected, but recoverable")
logging.error("A function failed")
logging.critical("Application cannot continue")
```

Levels in order of severity: `DEBUG < INFO < WARNING < ERROR < CRITICAL`. The root logger defaults to `WARNING`, so `debug` and `info` are silenced unless you configure it otherwise.

## Getting a Named Logger

Don't use the root logger in library or application code. Create a named logger per module:

```python
import logging

logger = logging.getLogger(__name__)

def process(data):
    logger.info("Processing %d records", len(data))
    for record in data:
        logger.debug("Record: %s", record)
```

`__name__` evaluates to the module's dotted path (e.g., `myapp.services.user`). This lets you control log verbosity per module in configuration.

## Basic Configuration

For scripts and small applications, `basicConfig` sets up a handler in one call:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.info("Application starting")
logger.debug("Debug mode active")
```

```
2024-03-15 10:42:01 INFO     __main__: Application starting
2024-03-15 10:42:01 DEBUG    __main__: Debug mode active
```

Call `basicConfig` once, at the entry point of your application. Calling it in library code is an anti-pattern.

## Handlers: Where Logs Go

A logger can have multiple handlers — each sends log records to a different destination:

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

# Console handler — only warnings and above
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

# File handler — everything, rotating at 5MB
file_handler = RotatingFileHandler(
    "app.log", maxBytes=5 * 1024 * 1024, backupCount=3
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")
)

logger.addHandler(console)
logger.addHandler(file_handler)
```

Common built-in handlers:

| Handler | Use |
|---|---|
| `StreamHandler` | stdout / stderr |
| `FileHandler` | plain file |
| `RotatingFileHandler` | rotates by size |
| `TimedRotatingFileHandler` | rotates by time (daily, weekly) |
| `SysLogHandler` | system syslog |
| `SMTPHandler` | email alerts for critical errors |
| `QueueHandler` | async logging (non-blocking) |

## Formatters

A `Formatter` controls what each log line looks like. Key format fields:

```
%(asctime)s     2024-03-15 10:42:01,123
%(levelname)s   DEBUG / INFO / WARNING / ERROR / CRITICAL
%(name)s        logger name (module path)
%(message)s     the log message
%(filename)s    source file
%(lineno)d      line number
%(funcName)s    function name
%(process)d     PID
%(thread)d      thread ID
```

A format string that includes location info — useful during development:

```python
fmt = "%(asctime)s %(levelname)-8s [%(name)s:%(lineno)d] %(message)s"
```

## Structured Logging with `extra` and JSON

For production systems feeding into Elasticsearch, Datadog, or similar, JSON logs are easier to parse than text. Use the `extra` parameter to attach fields:

```python
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "user_id"):
            log["user_id"] = record.user_id
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.getLogger().addHandler(handler)

logger = logging.getLogger("myapp")
logger.info("User logged in", extra={"user_id": 42})
```

```json
{"time": "2024-03-15 10:42:01,123", "level": "INFO", "logger": "myapp", "message": "User logged in", "user_id": 42}
```

For production use, the [`python-json-logger`](https://github.com/madzak/python-json-logger) package is a robust alternative to rolling your own.

## Logging Exceptions

Pass `exc_info=True` or use `logger.exception()` (which implies `ERROR` level and `exc_info=True`):

```python
try:
    result = risky_operation()
except ValueError as e:
    logger.exception("Operation failed for input %s", input_data)
    # Logs the message + full traceback
```

```
2024-03-15 10:42:01 ERROR    myapp: Operation failed for input bad_data
Traceback (most recent call last):
  File "app.py", line 12, in main
    result = risky_operation()
ValueError: invalid literal
```

## Configuring via `logging.config`

For larger applications, keep logging configuration out of code using a dict-config:

```python
import logging.config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 10_000_000,
            "backupCount": 5,
            "formatter": "standard",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
    "loggers": {
        "httpx": {"level": "WARNING"},      # silence verbose third-party loggers
        "sqlalchemy.engine": {"level": "WARNING"},
    },
}

logging.config.dictConfig(LOGGING)
```

## Performance: Lazy Formatting

Logging uses `%`-style formatting deliberately — the message string is only formatted if the log level is active. Don't use f-strings in log calls:

```python
# Bad — string is always formatted, even if DEBUG is silenced
logger.debug(f"Processing {len(data)} records with config {config}")

# Good — formatting only happens if DEBUG is active
logger.debug("Processing %d records with config %s", len(data), config)
```

## Propagation and the Logger Hierarchy

Loggers form a tree rooted at the root logger. By default, a logger propagates records up to its parent. This means configuring the root logger is usually enough — child loggers (like `myapp.db`) inherit handlers automatically.

Set `propagate = False` to stop a logger from passing records up — useful when you want a specific logger to write to its own file without also appearing in the root handler.

```python
db_logger = logging.getLogger("myapp.db")
db_logger.propagate = False
db_logger.addHandler(db_file_handler)
```

## Conclusion

The logging module's architecture — loggers, handlers, formatters — is more powerful than it looks from the outside. The key habits: use `getLogger(__name__)` in every module, call `basicConfig` or `dictConfig` once at startup, always use `%s` lazy formatting rather than f-strings, and prefer JSON output if your logs will be machine-parsed. These four changes alone take you from `print` debugging to production-ready observability.
