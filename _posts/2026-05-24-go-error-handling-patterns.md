---
layout: post
title: "Go Error Handling Patterns: The errors Package and Beyond"
date: "2026-05-24 00:00:00 +0530"
slug: go-error-handling-patterns
description: "A practical guide to Go error handling — covering sentinel errors, error wrapping, errors.Is and errors.As, custom error types, and patterns for clean production code."
categories: ["Programming", "wiki"]
tags: ["go", "golang", "error handling", "errors", "sentinel errors", "wrapping", "backend", "tutorial", "best practices"]
---

Error handling is one of the most discussed aspects of Go. The language makes you deal with errors explicitly — every function that can fail returns an error value, and you have to decide what to do with it at each call site. This feels verbose at first, but it makes error paths visible and forces you to think about failure modes up front. The `errors` package and a few established patterns make this manageable without boilerplate.

## The Basics

In Go, errors are values. A function signals failure by returning a non-nil `error`:

```go
package main

import (
    "errors"
    "fmt"
)

func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("cannot divide by zero")
    }
    return a / b, nil
}

func main() {
    result, err := divide(10, 0)
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Println(result)
}
```

```
Error: cannot divide by zero
```

The convention: always check the error immediately after the call. Don't shadow it with another variable later.

## Formatting Errors with `fmt.Errorf`

`fmt.Errorf` creates an error with a formatted message, and with the `%w` verb, it **wraps** another error — preserving the original while adding context:

```go
func readConfig(path string) error {
    data, err := os.ReadFile(path)
    if err != nil {
        return fmt.Errorf("readConfig: %w", err)
    }
    _ = data
    return nil
}
```

The convention for error messages: lowercase, no trailing period, and prefix with the function or package name so the chain reads naturally when unwrapped:

```
readConfig: open /etc/app/config.yaml: no such file or directory
```

## Sentinel Errors

A **sentinel error** is a package-level variable that callers can compare against to check for a specific condition:

```go
package store

import "errors"

var ErrNotFound = errors.New("record not found")
var ErrDuplicate = errors.New("duplicate key")

func (s *Store) Find(id int) (*User, error) {
    user, ok := s.data[id]
    if !ok {
        return nil, ErrNotFound
    }
    return user, nil
}
```

Callers use `errors.Is` to check — not `==` — because `errors.Is` walks the error chain created by wrapping:

```go
user, err := store.Find(42)
if errors.Is(err, store.ErrNotFound) {
    // handle not found specifically
    http.NotFound(w, r)
    return
}
if err != nil {
    // unexpected error
    http.Error(w, "internal error", 500)
    return
}
```

## `errors.Is` and `errors.As`

`errors.Is(err, target)` — checks whether `err` or any error it wraps matches `target`.

`errors.As(err, &target)` — checks whether `err` or any error in its chain can be assigned to `target` (useful for custom error types):

```go
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    fmt.Println("Failed on path:", pathErr.Path)
}
```

Never use `err == ErrNotFound` directly; wrapping breaks equality comparison. Always use `errors.Is`.

## Custom Error Types

When you need to attach structured data to an error, define a type that implements the `error` interface:

```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %q: %s", e.Field, e.Message)
}

func validateAge(age int) error {
    if age < 0 || age > 150 {
        return &ValidationError{Field: "age", Message: "must be between 0 and 150"}
    }
    return nil
}

func main() {
    err := validateAge(-5)
    var ve *ValidationError
    if errors.As(err, &ve) {
        fmt.Printf("Field: %s, Problem: %s\n", ve.Field, ve.Message)
    }
}
```

```
Field: age, Problem: must be between 0 and 150
```

## Wrapping for Context Without Losing the Original

A common pattern in layered code — add context at each layer while keeping the root error inspectable:

```go
func (svc *UserService) GetUser(id int) (*User, error) {
    user, err := svc.db.Find(id)
    if err != nil {
        return nil, fmt.Errorf("GetUser(%d): %w", id, err)
    }
    return user, nil
}

func (h *Handler) HandleGetUser(w http.ResponseWriter, r *http.Request) {
    id, _ := strconv.Atoi(r.PathValue("id"))
    user, err := h.svc.GetUser(id)
    if errors.Is(err, store.ErrNotFound) {
        http.NotFound(w, r)
        return
    }
    if err != nil {
        log.Printf("unexpected error: %v", err)
        http.Error(w, "internal error", 500)
        return
    }
    json.NewEncoder(w).Encode(user)
}
```

The log line will print:
```
unexpected error: GetUser(99): record not found
```

Full chain, readable, with no information lost.

## Panic and Recover

`panic` is for programmer errors — index out of bounds, nil pointer dereference, violated invariants. It's not a substitute for returning an error. Use `recover` only at package boundaries (e.g., in an HTTP handler) to prevent one bad request from crashing the whole server:

```go
func safeHandler(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if rec := recover(); rec != nil {
                log.Printf("panic: %v\n%s", rec, debug.Stack())
                http.Error(w, "internal server error", 500)
            }
        }()
        next(w, r)
    }
}
```

Don't use `panic`/`recover` for normal control flow.

## Joining Multiple Errors

Go 1.20 introduced `errors.Join` to combine multiple errors into one:

```go
func validateUser(u User) error {
    var errs []error
    if u.Name == "" {
        errs = append(errs, errors.New("name is required"))
    }
    if u.Age < 0 {
        errs = append(errs, errors.New("age must be non-negative"))
    }
    return errors.Join(errs...)
}
```

`errors.Join` returns `nil` if all errors are nil, and a joined error otherwise. Each sub-error is inspectable with `errors.Is`/`errors.As`.

## Patterns for Cleaner Error Handling

**Reduce nesting with early returns:**

```go
// Instead of deeply nested if/else
func process(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return fmt.Errorf("process: %w", err)
    }
    defer f.Close()

    data, err := io.ReadAll(f)
    if err != nil {
        return fmt.Errorf("process: read: %w", err)
    }

    return transform(data)
}
```

**Group repeated error-check pattern into a helper:**

```go
type errWriter struct {
    w   io.Writer
    err error
}

func (ew *errWriter) write(data []byte) {
    if ew.err != nil {
        return
    }
    _, ew.err = ew.w.Write(data)
}

// Caller: write multiple times, check error once at the end
ew := &errWriter{w: w}
ew.write(header)
ew.write(body)
ew.write(footer)
if ew.err != nil {
    return ew.err
}
```

## Conclusion

Go's error handling model is intentionally simple: errors are values, you return them, you check them. The `errors` package gives you the tools to make this composable — wrap errors to add context, use `errors.Is` to inspect sentinel conditions, and `errors.As` to extract structured information. The verbosity isn't a bug; it's what makes error paths visible and auditable. Adopt the wrapping convention from the start and your logs will tell you exactly where and why things went wrong.
