---
layout: post
title: "GitHub Actions CI/CD: Build, Test, and Deploy a Project"
date: "2026-05-23 00:00:00 +0530"
slug: github-actions-cicd-guide
description: "Set up a complete CI/CD pipeline with GitHub Actions that builds, tests, and deploys your app automatically on every push to main."
categories: ["Tutorials", "Programming"]
tags: ["github actions", "ci/cd", "devops", "automation", "yaml", "github", "deployment", "testing", "pipeline"]
render_with_liquid: false
---

Every time you push code and spend the next ten minutes manually running tests and deploying by hand, you're doing work a machine could do for you. GitHub Actions lets you define exactly that automation in YAML files that live in your repository — no external CI service required. This guide walks through building a real pipeline that tests on every pull request and deploys on every merge to `main`.

## How GitHub Actions Works

Actions are triggered by **events** (push, pull_request, schedule, etc.) and run **workflows** — YAML files in `.github/workflows/`. Each workflow has **jobs**, each job runs on a **runner** (a fresh VM), and each job has **steps** that run sequentially.

```
Event → Workflow → Jobs (parallel by default) → Steps (sequential)
```

## A Basic CI Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest --tb=short -q

      - name: Lint
        run: ruff check .
```

Push this file and GitHub immediately starts running the workflow. Every subsequent pull request will show a green or red status check before you can merge.

## Caching Dependencies

By default, every run reinstalls dependencies from scratch. Caching the pip download cache cuts minutes off each run:

```yaml
      - name: Cache pip packages
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
```

The cache key includes a hash of `requirements.txt`, so the cache is invalidated whenever dependencies change.

## Matrix Builds: Test Across Multiple Versions

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install and test
        run: |
          pip install -r requirements.txt
          pytest
```

This runs three parallel jobs — one per Python version — and reports them all in the pull request.

## A Deployment Workflow

Separation of concerns: the CI workflow runs on every PR, the deploy workflow runs only on pushes to `main`. Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Push image
        run: |
          docker tag myapp:${{ github.sha }} myuser/myapp:latest
          docker push myuser/myapp:latest

      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_SSH_KEY }}
          script: |
            docker pull myuser/myapp:latest
            docker compose up -d --no-deps api
```

## Managing Secrets

Never hardcode credentials in workflow files. Store them in **Settings → Secrets and variables → Actions** and reference them as `${{ secrets.SECRET_NAME }}`. Secret values are masked in logs.

For per-environment secrets (staging vs production), use **Environments** (`environment: production` in the job), which lets you require manual approval before a deployment job runs.

## Useful Workflow Patterns

**Run a job only on specific file changes:**

```yaml
on:
  push:
    paths:
      - "src/**"
      - "requirements.txt"
```

**Share data between jobs:**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.tag.outputs.tag }}
    steps:
      - id: tag
        run: echo "tag=${{ github.sha }}" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.image_tag }}"
```

**Conditional steps:**

```yaml
      - name: Notify Slack on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: '{"text":"Deploy failed on ${{ github.ref }}"}'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Conclusion

GitHub Actions gives you a full CI/CD pipeline without leaving your repository. The CI workflow on pull requests catches regressions before they merge, the deployment workflow automates what would otherwise be a manual, error-prone release process, and secrets management keeps credentials out of your codebase. Start with a simple test job and add deployment steps incrementally — a working pipeline you understand beats a sophisticated one that nobody maintains.
