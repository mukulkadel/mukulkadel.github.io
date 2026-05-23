---
layout: post
title: Getting started with Go (Mac)
date: "2024-06-14 00:00:00 +0530"
slug: set-up-go-golang-mac-hello-world-program
description: "Learn how to set up Go (Golang) on a Mac and run a basic \"Hello, world!\" program. This step-by-step guide includes prerequisites, installation commands, and a simple program example."
categories: ["Programming", "Software Development", "Tutorials"]
tags: ["Go environment variables", "Go language tutorial", "Go programming basics", "Go setup", "Golang installation", "Hello World program", "Homebrew Go installation", "Install Go on Mac", "Mac programming", "Simple Go program"]
---

Welcome to my blog! In this post, I’ll guide you on how to set up Go (Golang) on a Mac and run a basic “Hello, world!” program.

Go is an open-source, statically typed, compiled language. It’s very clean and efficient, and its concurrency mechanisms make it easy to get the most out of multicore systems.

## Prerequisites

- A basic code editor.
- A code terminal.
- [Homebrew](https://brew.sh/)

## How to install

- Open terminal.
- Run the following command:

```bash
brew install go
```

This command will install the latest version of Go.

If you want to install a specific version, use the command below:

```go
brew install go@1.22.4
```

- Run the command below to test the installation:

```bash
go version
# output: go version go1.xx.x darwin/arm64
```

- Now, set up environment variables by running the commands below:

```bash
export PATH="$PATH:$HOME/go/bin"
echo "export PATH=\"$PATH:$HOME/go/bin\"" >> ~/.zprofile
```

Your Go setup is complete. Let’s now explore how to run it!

## A Simple Program: Hello, World!

- Make a new directory `demo` & open a new file `main.go` in it.

```bash
mkdir demo
cd demo
nano main.go # You can also use an IDE.
```

- In the file, paste the code below and run `go run main.go` in the terminal:

```go
package main

import "fmt"

func main() {
	fmt.Println("Hello, World!")
}

```

You should see the following output in the terminal:

```go
Hello, World!
```

Congratulations on your first Go program!
