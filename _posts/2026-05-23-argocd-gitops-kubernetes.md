---
layout: post
title: "Understanding ArgoCD: GitOps for Kubernetes"
date: "2026-05-23 00:00:00 +0530"
slug: argocd-gitops-kubernetes
description: "Learn how ArgoCD implements GitOps by syncing Kubernetes clusters to a Git repository, with a full setup walkthrough and real-world deployment patterns."
categories: ["wiki", "Programming"]
tags: ["argocd", "gitops", "kubernetes", "k8s", "devops", "continuous delivery", "cloud native", "deployment"]
---

With Kubernetes, you can apply manifests manually with `kubectl apply` or trigger deployments from a CI pipeline. Both approaches work — until someone applies a hotfix directly to the cluster and now production no longer matches what's in git. ArgoCD solves this by making git the single source of truth: the cluster continuously reconciles itself to match whatever is in the repository.

## What is GitOps?

**GitOps** is an operational model where:

1. The desired state of your system lives in git
2. An agent continuously compares desired state to actual state
3. Any drift is automatically corrected (or flagged)

With ArgoCD, you push a change to git and the cluster catches up — you never `kubectl apply` to production directly.

## Installing ArgoCD

```bash
$ kubectl create namespace argocd

$ kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# wait for pods to be ready
$ kubectl wait --for=condition=available deployment \
  -l app.kubernetes.io/name=argocd-server \
  -n argocd --timeout=120s

# port-forward the UI
$ kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Get the initial admin password:

```bash
$ kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath='{.data.password}' | base64 -d
r8Kf9pXqZmN2wQ4T
```

Visit `https://localhost:8080`, log in as `admin`, and you're in.

Install the CLI:

```bash
$ brew install argocd

$ argocd login localhost:8080 \
  --username admin \
  --password r8Kf9pXqZmN2wQ4T \
  --insecure
```

## Creating Your First Application

An ArgoCD **Application** links a git repository path to a cluster namespace. Here's the YAML approach:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/myorg/k8s-manifests
    targetRevision: main
    path: apps/myapp

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true       # delete resources removed from git
      selfHeal: true    # revert manual changes to the cluster
    syncOptions:
      - CreateNamespace=true
```

```bash
$ kubectl apply -f myapp-argocd.yaml
application.argoproj.io/myapp created

$ argocd app get myapp
Name:               myapp
Project:            default
Server:             https://kubernetes.default.svc
Namespace:          production
URL:                https://localhost:8080/applications/myapp
Repo:               https://github.com/myorg/k8s-manifests
Target:             main
Path:               apps/myapp
Sync Policy:        Automated (Prune, Self Heal)
Sync Status:        Synced to main (a3f2c9d)
Health Status:      Healthy
```

## Sync Policies

ArgoCD can sync manually or automatically.

**Manual sync** — ArgoCD shows drift but waits for you to approve:

```bash
$ argocd app sync myapp
```

**Automated sync** — ArgoCD applies changes within seconds of a git push. Use `prune: true` to also delete resources that were removed from git, and `selfHeal: true` to revert any manual `kubectl` edits.

For production, many teams prefer **automated sync with manual promotion**: automated in staging, manual approval gate for production. You can set up ArgoCD sync windows to restrict when automated syncs are allowed.

## Repository Structure Patterns

ArgoCD works with raw manifests, Helm charts, or Kustomize. A common layout for multiple apps and environments:

```
k8s-manifests/
├── apps/
│   ├── myapp/
│   │   ├── base/          # shared manifests
│   │   └── overlays/
│   │       ├── staging/   # kustomize patches for staging
│   │       └── production/
│   └── api-gateway/
└── argocd/
    └── applications/      # ArgoCD Application YAMLs
```

Kustomize source:

```yaml
source:
  repoURL: https://github.com/myorg/k8s-manifests
  path: apps/myapp/overlays/production
  targetRevision: main
```

Helm chart source:

```yaml
source:
  repoURL: https://github.com/myorg/k8s-manifests
  path: helm/myapp
  targetRevision: main
  helm:
    valueFiles:
      - values/production.yaml
```

## App of Apps Pattern

Managing dozens of ArgoCD Application resources manually doesn't scale. The **App of Apps** pattern uses one root Application to manage all others:

```yaml
# root-app.yaml
spec:
  source:
    path: argocd/applications   # directory of Application YAMLs
```

Push a new Application YAML to `argocd/applications/` and ArgoCD picks it up automatically — no manual `kubectl apply` needed.

## Checking Sync Status

```bash
# list all apps
$ argocd app list
NAME    CLUSTER        NAMESPACE   PROJECT  STATUS  HEALTH   SYNCPOLICY
myapp   in-cluster     production  default  Synced  Healthy  Auto-Prune

# see what's out of sync (before syncing)
$ argocd app diff myapp

# force a sync
$ argocd app sync myapp --prune

# roll back to a previous git commit
$ argocd app rollback myapp <revision-id>
```

## Conclusion

ArgoCD enforces a discipline that's hard to achieve with pipelines alone: every change to the cluster goes through git, drift is visible and correctable, and the history of every deployment is a git commit. The combination of automated sync, self-healing, and pull-request-based change management gives you Kubernetes deployments that are auditable, reproducible, and recoverable. Pair it with Helm or Kustomize for per-environment configuration and you have a complete GitOps workflow.
