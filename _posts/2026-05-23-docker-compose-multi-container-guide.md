---
layout: post
title: "Docker Compose — Multi-Container App Setup Guide"
date: "2026-05-23 00:00:00 +0530"
slug: docker-compose-multi-container-guide
description: "Learn how to define, link, and run multi-container applications with Docker Compose using a practical web app and database example."
categories: ["Tutorials", "Programming"]
tags: ["docker", "docker compose", "containers", "devops", "multi-container", "yaml", "networking", "volumes", "tutorial"]
---

Most real applications aren't a single process — they're a web server, a database, a cache, maybe a background worker, all talking to each other. Running each container with long `docker run` commands and manually wiring them together gets painful fast. Docker Compose lets you define the entire stack in one YAML file and bring it up with a single command.

## The `docker-compose.yml` File

Compose describes your application as a set of **services**, each of which maps to a container. Here's a practical example: a FastAPI backend backed by PostgreSQL and Redis.

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:secret@db:5432/appdb
      REDIS_URL: redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - .:/app

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d appdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

Services can reference each other by **service name** as the hostname — `db` and `cache` are resolvable from the `api` container because Compose creates a shared network automatically.

## Starting and Stopping

```bash
# start everything in the background
$ docker compose up -d
[+] Running 3/3
 ✔ Container myapp-db-1     Healthy
 ✔ Container myapp-cache-1  Started
 ✔ Container myapp-api-1    Started

# tail logs from all services
$ docker compose logs -f

# tail just the api service
$ docker compose logs -f api

# stop and remove containers (volumes are preserved)
$ docker compose down

# stop AND remove volumes (wipes the database)
$ docker compose down -v
```

## Rebuilding After Code Changes

When you change your `Dockerfile` or source code, Compose won't automatically pick it up unless you rebuild.

```bash
$ docker compose up -d --build
```

For local development with a bind mount (`- .:/app`), code changes reflect immediately without rebuilding — only dependency changes in your `Dockerfile` need a rebuild.

## Running One-Off Commands

```bash
# open a postgres shell
$ docker compose exec db psql -U user -d appdb

# run database migrations
$ docker compose run --rm api python manage.py migrate

# run tests inside the api container
$ docker compose run --rm api pytest
```

`exec` runs a command in an already-running container. `run` spins up a fresh container for the command and exits when done. `--rm` cleans it up afterwards.

## Scaling a Service

```bash
$ docker compose up -d --scale api=3
```

This starts three instances of the `api` service. You'd typically put a load balancer (Nginx or Traefik) in front of them, but it's a fast way to test horizontal scaling locally.

## Environment Files

Hardcoding secrets in `docker-compose.yml` is fine for local dev, but for shared repos or staging environments, use a `.env` file:

```bash
# .env
POSTGRES_PASSWORD=secret
REDIS_URL=redis://cache:6379
```

Compose reads `.env` automatically. Reference variables with `${VAR_NAME}`:

```yaml
environment:
  DATABASE_URL: postgresql://user:${POSTGRES_PASSWORD}@db:5432/appdb
```

Add `.env` to `.gitignore` and commit a `.env.example` with placeholder values instead.

## Useful Inspection Commands

```bash
# show running containers and their status
$ docker compose ps

# show which host ports are mapped
$ docker compose port api 8000
0.0.0.0:8000

# show resource usage
$ docker compose stats
```

## Conclusion

Docker Compose turns a sprawling set of `docker run` commands into a single, readable file that anyone on the team can spin up identically. The `depends_on` with healthchecks ensures services start in the right order, named volumes keep data safe across restarts, and the built-in network means services find each other by name without any manual configuration. Once you're running containers locally with Compose, moving to production with Kubernetes or a managed container service becomes a much smaller leap.
