---
layout: post
title: "Docker Basics: Containers, Images, and Volumes Explained"
date: "2026-05-23 00:00:00 +0530"
slug: docker-basics-containers-images-volumes
description: "Learn how Docker containers, images, and volumes work with practical examples you can run right now on any Linux or macOS machine."
categories: ["Programming", "Tutorials"]
tags: ["docker", "containers", "devops", "images", "volumes", "dockerfile", "linux", "cloud", "tutorial"]
---

If you've heard "just throw it in a container" more times than you can count, it's time to understand what that actually means. Docker packages your app and all its dependencies into an isolated unit that runs the same way everywhere — on your laptop, a CI server, or production. This post walks through the three building blocks: images, containers, and volumes.

## Images vs Containers

An **image** is a read-only blueprint. A **container** is a running instance of that blueprint. The relationship is the same as a class and an object in code — one image can spawn many containers.

Pull the official Nginx image and you've downloaded a layered filesystem snapshot:

```bash
$ docker pull nginx:alpine
alpine: Pulling from library/nginx
Digest: sha256:2d194184...
Status: Downloaded newer image for nginx:alpine
```

Spin up a container from it:

```bash
$ docker run -d -p 8080:80 --name web nginx:alpine
c3a1f9e7b2d4...

$ docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS                  NAMES
c3a1f9e7b2d4   nginx:alpine   "/docker-entrypoint.…"   5 seconds ago   Up 4 seconds   0.0.0.0:8080->80/tcp   web
```

`-d` runs it in the background. `-p 8080:80` maps host port 8080 to container port 80. Visit `http://localhost:8080` and you'll see Nginx's welcome page.

## Building Your Own Image

A **Dockerfile** is a recipe for your image. Each instruction adds a layer.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

Build it:

```bash
$ docker build -t myapp:latest .
[+] Building 12.3s
 => [1/5] FROM python:3.12-slim
 => [2/5] WORKDIR /app
 => [3/5] COPY requirements.txt .
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt
 => [5/5] COPY . .
 => exporting to image
```

The `COPY requirements.txt` step is deliberately before `COPY . .` — Docker caches each layer. If you change application code but not `requirements.txt`, the pip install layer is reused and rebuilds are fast.

## Essential Container Commands

```bash
# list running containers
$ docker ps

# list all containers including stopped ones
$ docker ps -a

# stream logs
$ docker logs -f web

# open a shell inside a running container
$ docker exec -it web sh

# stop and remove
$ docker stop web && docker rm web

# remove the image
$ docker rmi nginx:alpine
```

## Volumes: Persisting Data

Containers are ephemeral — when you remove one, all data written inside it disappears. **Volumes** solve this by mounting a storage location from the host (or a Docker-managed directory) into the container.

```bash
# named volume — Docker manages the location
$ docker run -d \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  --name db \
  postgres:16

# bind mount — explicit host path
$ docker run -d \
  -v /home/mukul/site:/usr/share/nginx/html:ro \
  -p 8080:80 \
  nginx:alpine
```

Named volumes survive container removal. Bind mounts are great for local development because you edit files on the host and the container picks up changes immediately.

List and inspect volumes:

```bash
$ docker volume ls
DRIVER    VOLUME NAME
local     pgdata

$ docker volume inspect pgdata
[
  {
    "Name": "pgdata",
    "Mountpoint": "/var/lib/docker/volumes/pgdata/_data",
    ...
  }
]
```

## Cleaning Up

Docker accumulates unused images, stopped containers, and dangling volumes quickly.

```bash
# remove all stopped containers, unused networks, dangling images
$ docker system prune
WARNING! This will remove:
  - all stopped containers
  - all networks not used by at least one container
  - all dangling images
  - all dangling build cache

Total reclaimed space: 1.23GB

# nuclear option — also removes unused images
$ docker system prune -a
```

## Conclusion

Images are immutable blueprints, containers are running instances, and volumes are where persistent data lives. With just `docker build`, `docker run`, and a well-written Dockerfile, you can package any application into a portable, reproducible artifact. Once you're comfortable running single containers, the natural next step is coordinating multiple services with Docker Compose.
