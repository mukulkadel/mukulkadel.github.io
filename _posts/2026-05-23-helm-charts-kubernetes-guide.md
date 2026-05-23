---
layout: post
title: "Helm Charts — Packaging Kubernetes Applications"
date: "2026-05-23 00:00:00 +0530"
slug: helm-charts-kubernetes-guide
description: "Learn how Helm charts work, how to install community charts, and how to write your own chart to package a Kubernetes application for repeatable deploys."
categories: ["wiki", "Programming"]
tags: ["helm", "kubernetes", "k8s", "charts", "devops", "cloud native", "deployment", "packaging", "yaml"]
---

Once you have more than one Kubernetes application to manage, raw YAML manifests start to show their limits. Every environment needs slightly different values — different image tags, replica counts, resource limits, ingress hostnames — and maintaining separate copies of near-identical files is error-prone. Helm is the package manager for Kubernetes that solves this with **charts**: reusable, parameterized application packages.

## What is a Helm Chart?

A chart is a directory of templates and a values file. Helm renders the templates using the values, then applies the resulting manifests to your cluster. The same chart can deploy to dev, staging, and production with different configurations.

```
mychart/
├── Chart.yaml          # chart metadata (name, version, description)
├── values.yaml         # default configuration values
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    └── ingress.yaml
```

## Installing Helm

```bash
# macOS
$ brew install helm

$ helm version
version.BuildInfo{Version:"v3.15.0", ...}
```

## Using Community Charts

Before writing your own, check the [Artifact Hub](https://artifacthub.io) — there are production-ready charts for PostgreSQL, Redis, Nginx, Prometheus, and hundreds of other tools.

```bash
# add the Bitnami repository
$ helm repo add bitnami https://charts.bitnami.com/bitnami
"bitnami" has been added to your repositories

$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "bitnami" chart repository

# search for a chart
$ helm search repo bitnami/postgresql
NAME                  CHART VERSION   APP VERSION   DESCRIPTION
bitnami/postgresql    15.5.3          16.3.0        PostgreSQL...

# install with custom values
$ helm install my-db bitnami/postgresql \
  --set auth.postgresPassword=secret \
  --set primary.persistence.size=20Gi \
  --namespace databases \
  --create-namespace

# check the release
$ helm list -n databases
NAME    NAMESPACE   REVISION  STATUS    CHART                 APP VERSION
my-db   databases   1         deployed  postgresql-15.5.3     16.3.0
```

## Writing Your Own Chart

```bash
$ helm create myapp
Creating myapp
```

This scaffolds the directory structure. Edit `values.yaml` to define your defaults:

```yaml
replicaCount: 2

image:
  repository: myuser/myapp
  tag: "1.0.0"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
  targetPort: 8000

ingress:
  enabled: false
  host: ""

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

In `templates/deployment.yaml`, reference values with the `{{ .Values.* }}` syntax:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ include "myapp.name" . }}
  template:
    metadata:
      labels:
        app: {{ include "myapp.name" . }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.targetPort }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

## Installing and Upgrading Your Chart

```bash
# install from local directory
$ helm install myapp ./myapp

# override values at install time
$ helm install myapp ./myapp \
  --set image.tag=1.1.0 \
  --set replicaCount=3

# or pass a values file (preferred for many overrides)
$ helm install myapp ./myapp -f production-values.yaml

# upgrade an existing release
$ helm upgrade myapp ./myapp --set image.tag=1.2.0

# upgrade or install if it doesn't exist
$ helm upgrade --install myapp ./myapp -f production-values.yaml
```

## Per-Environment Values Files

Keep a values file per environment and commit them to git:

```
helm/
├── myapp/           # the chart
└── values/
    ├── dev.yaml
    ├── staging.yaml
    └── production.yaml
```

```yaml
# production.yaml
replicaCount: 5

image:
  tag: "1.4.2"

ingress:
  enabled: true
  host: api.mycompany.com

resources:
  requests:
    cpu: 500m
    memory: 512Mi
```

```bash
$ helm upgrade --install myapp ./helm/myapp -f helm/values/production.yaml
```

## Useful Commands

```bash
# render templates without applying (great for debugging)
$ helm template myapp ./myapp -f production.yaml

# list all releases
$ helm list -A

# check release history
$ helm history myapp
REVISION  STATUS     CHART        DESCRIPTION
1         superseded myapp-0.1.0  Install complete
2         deployed   myapp-0.1.0  Upgrade complete

# roll back to a previous revision
$ helm rollback myapp 1

# uninstall a release (removes all Kubernetes objects)
$ helm uninstall myapp
```

## Conclusion

Helm turns a pile of environment-specific YAML files into a single parameterized package. Community charts let you deploy complex software like databases and monitoring stacks in minutes without writing hundreds of lines of manifest. For your own applications, a chart with a well-designed `values.yaml` makes the difference between deploying to a new environment in five minutes versus an afternoon of copy-paste and find-replace. Pair Helm with a GitOps tool like ArgoCD and you get automated, auditable deployments on top of that.
