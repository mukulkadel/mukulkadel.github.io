---
layout: post
title: "Go Goroutines and Channels: Concurrency Made Simple"
date: "2026-05-24 00:00:00 +0530"
slug: go-goroutines-channels-concurrency
description: "Learn how Go goroutines and channels work together to make concurrent programming practical, safe, and surprisingly readable."
categories: ["Programming", "wiki"]
tags: ["go", "golang", "goroutines", "channels", "concurrency", "parallelism", "tutorial", "backend", "waitgroup"]
---

Concurrency is one of Go's defining features — not bolted on as an afterthought, but baked into the language from day one. With goroutines that cost a few kilobytes of stack space and channels that let you pass data between them safely, Go makes concurrent code feel almost as straightforward as sequential code. Let's dig into how it all fits together.

## What is a Goroutine?

A goroutine is a lightweight thread managed by the Go runtime — not an OS thread. You can spawn thousands of them without breaking a sweat. Starting one is as simple as putting `go` before a function call.

```go
package main

import (
    "fmt"
    "time"
)

func greet(name string) {
    fmt.Printf("Hello, %s!\n", name)
}

func main() {
    go greet("Alice")
    go greet("Bob")
    time.Sleep(100 * time.Millisecond)
    fmt.Println("done")
}
```

```
Hello, Bob!
Hello, Alice!
done
```

The order is non-deterministic — that's the nature of concurrent execution. The `time.Sleep` is a crude way to wait; we'll fix that with proper synchronization shortly.

## Channels: Communicating Between Goroutines

Channels are typed conduits for passing values between goroutines. The Go philosophy is: *don't communicate by sharing memory; share memory by communicating*.

```go
ch := make(chan int)      // unbuffered
bch := make(chan int, 10) // buffered, capacity 10
```

Send with `<-` and receive with `<-`:

```go
ch <- 42     // send
val := <-ch  // receive
```

A minimal producer–consumer example:

```go
package main

import "fmt"

func produce(ch chan<- int) {
    for i := 0; i < 5; i++ {
        ch <- i
    }
    close(ch)
}

func main() {
    ch := make(chan int)
    go produce(ch)

    for v := range ch {
        fmt.Println(v)
    }
}
```

```
0
1
2
3
4
```

`range` on a channel reads until the channel is closed. Always close channels from the sender side — receiving from a closed channel returns the zero value immediately.

## Buffered vs Unbuffered Channels

**Unbuffered** channels block the sender until a receiver is ready and vice versa. They enforce synchronization at every message.

**Buffered** channels allow the sender to put up to `N` items in without blocking, useful when producer and consumer run at different speeds.

```go
ch := make(chan string, 3)
ch <- "a"
ch <- "b"
ch <- "c"
// ch <- "d" would block here — buffer is full

fmt.Println(<-ch) // a
fmt.Println(<-ch) // b
```

## Synchronizing with `sync.WaitGroup`

`time.Sleep` is never a real solution. Use `sync.WaitGroup` to wait for a known number of goroutines to finish:

```go
package main

import (
    "fmt"
    "sync"
)

func worker(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    fmt.Printf("worker %d starting\n", id)
    // ... do work ...
    fmt.Printf("worker %d done\n", id)
}

func main() {
    var wg sync.WaitGroup

    for i := 1; i <= 5; i++ {
        wg.Add(1)
        go worker(i, &wg)
    }

    wg.Wait()
    fmt.Println("all workers done")
}
```

```
worker 3 starting
worker 1 starting
worker 5 starting
worker 2 starting
worker 4 starting
worker 4 done
worker 1 done
worker 5 done
worker 3 done
worker 2 done
all workers done
```

The `defer wg.Done()` pattern ensures `Done` is called even if the worker panics.

## The `select` Statement

`select` lets a goroutine wait on multiple channel operations, choosing whichever is ready first — like a `switch` for channels.

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    ch1 := make(chan string)
    ch2 := make(chan string)

    go func() {
        time.Sleep(50 * time.Millisecond)
        ch1 <- "from ch1"
    }()
    go func() {
        time.Sleep(30 * time.Millisecond)
        ch2 <- "from ch2"
    }()

    select {
    case msg := <-ch1:
        fmt.Println(msg)
    case msg := <-ch2:
        fmt.Println(msg)
    }
}
```

```
from ch2
```

Add a `default` case to make it non-blocking.

## Fan-Out and Fan-In

A common pattern: distribute work across multiple goroutines (fan-out), then collect results into a single channel (fan-in).

```go
package main

import (
    "fmt"
    "sync"
)

func square(in <-chan int, out chan<- int, wg *sync.WaitGroup) {
    defer wg.Done()
    for v := range in {
        out <- v * v
    }
}

func main() {
    jobs := make(chan int, 10)
    results := make(chan int, 10)
    var wg sync.WaitGroup

    for w := 0; w < 3; w++ {
        wg.Add(1)
        go square(jobs, results, &wg)
    }

    for i := 1; i <= 9; i++ {
        jobs <- i
    }
    close(jobs)

    go func() {
        wg.Wait()
        close(results)
    }()

    for r := range results {
        fmt.Println(r)
    }
}
```

```
1
4
9
16
25
36
49
64
81
```

The goroutine that calls `wg.Wait()` and then closes `results` is a standard idiom: it ensures we only close the output channel after all workers have finished.

## Avoiding Race Conditions

The Go race detector is invaluable during development:

```bash
$ go run -race main.go
```

If two goroutines access the same variable without synchronization, the race detector will catch it. Use channels to pass ownership, or `sync.Mutex` when shared state is unavoidable:

```go
var mu sync.Mutex
var counter int

go func() {
    mu.Lock()
    counter++
    mu.Unlock()
}()
```

## Common Gotchas

**Goroutine leak** — a goroutine blocked on a channel receive with no sender will live forever. Always ensure goroutines have a way to exit, typically via a `done` channel or `context.Context`.

**Closing a channel twice** panics. Assign closing responsibility to exactly one goroutine.

**Sending on a closed channel** panics. Design your pipeline so senders always know when to stop.

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

select {
case result := <-ch:
    fmt.Println(result)
case <-ctx.Done():
    fmt.Println("timed out")
}
```

Using `context.Context` for cancellation and timeouts is the idiomatic Go way to prevent goroutine leaks in production code.

## Conclusion

Go's concurrency model — goroutines for lightweight execution and channels for safe communication — makes it genuinely easy to write concurrent programs that are also readable. The key mental shift is treating data transfer through channels as the primary coordination mechanism rather than shared locks. Start with `sync.WaitGroup` for structured parallelism, reach for `select` when you need to multiplex channels, and always run your code with `-race` during development to catch data races early.
