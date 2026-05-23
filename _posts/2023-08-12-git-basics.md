---
layout: post
title: Git Basics
date: "2023-08-12 00:00:00 +0530"
slug: git-basics
description: Git is a tool that helps people work on projects together. It’s like a super organized way to keep track of changes in projects, whether they’re small or really big. It’s not…
categories: ["Programming", "Tutorials", "git"]
tags: ["cheatsheet", "git", "tutorial", "version control", "git commands", "branching", "merging", "github", "command line"]
---

Git is a tool that helps people work on projects together. It’s like a super organized way to keep track of changes in projects, whether they’re small or really big.

It’s not hard to learn how to use Git, and it works really fast. It’s better than other tools like Subversion, CVS, Perforce, and ClearCase because it lets you do things like make new versions easily, prepare changes step by step, and use different methods to work on things together.

Here’s a list of a few commands which would be useful in your day-to-day life.

## Commands

- `git init` – Creates an empty git repository or reinitializes an existing one.

To initialize a new git repository in an existing directory, run `git init`

```bash
$ git init
Initialized empty Git repository in <directory-path>/.git/
```

- `git status` – Show the working tree status.

In simple terms, it shows the files which have been changed since the last commit and indicate whether our local repository is matching the remote repository or not.

```bash
$ ls
Readme.md

$ git status
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	Readme.md

nothing added to commit but untracked files present (use "git add" to track)
```

In my git repository, I have only one file which isn’t committed yet.

- `git add` – Add file contents to the index.

It prepares the file for commit and we can specify multiple files at once.

```bash
$ git add Readme.md
$ git status
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   Readme.md

# If you want to specify multiple files.
$ git add file1 file2 file3

# To stage whole directory at once.
$ git add .
```

- `git commit` – Record changes to the repository.

It commits all the files which have been added in the previous command execution.

`-m` : *Required*. To specify a meaningful message.

```bash
$ git commit -m "My first commit."
[main (root-commit) c43f339] My first commit.
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 Readme.md
```

- `git log` – Show commit logs.

List all the commits which are present in current branch.

```bash
$ git log
commit c43f339124385ffc6f0ac33fb60fe9706c7fa036 (HEAD -> main)
Author: Mukul Kadel <my-email@gmail.com>
Date:   Mon Aug 14 02:53:44 2023 +0530

    My first commit.
```
