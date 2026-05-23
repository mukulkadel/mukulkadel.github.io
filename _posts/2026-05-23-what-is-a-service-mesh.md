---
layout: post
title: "What is a Service Mesh? (Beyond Istio)"
date: "2026-05-23 00:00:00 +0530"
slug: what-is-a-service-mesh
description: "Understand what a service mesh does, when you actually need one, and how Istio, Linkerd, and Cilium differ in their approach to managing microservice traffic."
categories: ["wiki"]
tags: ["service mesh", "istio", "linkerd", "microservices", "kubernetes", "devops", "networking", "envoy", "cloud native"]
---

Once you have dozens of microservices talking to each other on Kubernetes, a familiar set of problems emerges: How do you encrypt traffic between services? How do you retry failed requests without writing retry logic in every service? How do you trace a request as it fans out across ten services? You could solve each of these in application code, or you could handle all of them at the network layer with a service mesh.

## What a Service Mesh Actually Does

A service mesh intercepts all network traffic between services by injecting a **sidecar proxy** into each Pod. The proxy handles:

- **mTLS** — mutual TLS between every pair of services, encrypting traffic and verifying identity without code changes
- **Retries and timeouts** — automatic retry on transient failures, configurable per-route
- **Load balancing** — advanced algorithms (least request, consistent hash) beyond what Kubernetes Services offer
- **Circuit breaking** — stop sending traffic to a failing service to prevent cascade failures
- **Traffic splitting** — send 10% of traffic to a new version for canary deployments
- **Distributed tracing** — inject trace headers and report spans to Jaeger or Zipkin
- **Observability** — automatic golden signal metrics (requests, errors, latency) for every service pair

The key insight: your application code doesn't change. The proxy handles all of this transparently.

## The Sidecar Architecture

```
Pod A                          Pod B
┌────────────────────┐         ┌────────────────────┐
│  app container     │         │  app container     │
│  (port 8080)       │         │  (port 8080)       │
│        ↓           │         │        ↑           │
│  sidecar proxy     │─ mTLS ──│  sidecar proxy     │
│  (Envoy/linkerd2)  │         │  (Envoy/linkerd2)  │
└────────────────────┘         └────────────────────┘
         ↕                              ↕
    Control Plane (issues certs, pushes routing config, collects telemetry)
```

The control plane distributes certificates, pushes routing rules to every proxy, and aggregates metrics — all without touching your application.

## Istio

Istio is the most feature-rich service mesh, built on the **Envoy** proxy. It's the choice when you need granular traffic control.

Install with Helm:

```bash
$ helm repo add istio https://istio-release.storage.googleapis.com/charts
$ helm install istio-base istio/base -n istio-system --create-namespace
$ helm install istiod istio/istiod -n istio-system
```

Enable sidecar injection for a namespace:

```bash
$ kubectl label namespace production istio-injection=enabled
```

Every new Pod in `production` now gets an Envoy sidecar injected automatically.

**Traffic splitting for a canary deploy:**

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
    - myapp
  http:
    - route:
        - destination:
            host: myapp
            subset: v1
          weight: 90
        - destination:
            host: myapp
            subset: v2
          weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  subsets:
    - name: v1
      labels:
        version: "1.4.2"
    - name: v2
      labels:
        version: "1.5.0"
```

Istio's power comes with real complexity — the CRD count alone is over 40.

## Linkerd

Linkerd takes the opposite philosophy: minimal surface area, production-safe defaults, zero configuration for 80% of use cases. It uses its own ultra-lightweight **Rust proxy** (linkerd2-proxy) instead of Envoy, which means significantly lower CPU and memory overhead.

```bash
$ brew install linkerd
$ linkerd install --crds | kubectl apply -f -
$ linkerd install | kubectl apply -f -
$ linkerd check

# inject into a namespace
$ kubectl annotate namespace production \
  linkerd.io/inject=enabled
```

Linkerd gives you mTLS, retries, timeouts, and golden-signal metrics with almost no configuration. If you don't need Istio's advanced traffic management, Linkerd's operational simplicity is a strong argument.

## Cilium (eBPF-based)

Cilium takes a fundamentally different approach: instead of sidecars, it uses **eBPF** — a Linux kernel technology — to intercept and control traffic directly in the kernel. No sidecar, no proxy overhead, no extra container per Pod.

This makes Cilium extremely performant and the right choice if you're already using it as your CNI (cluster network interface). Cilium Mesh handles L7 policy, mTLS via SPIFFE, and observability through Hubble.

## Do You Actually Need a Service Mesh?

A service mesh adds operational overhead — more components to upgrade, more things to debug when networking breaks. Before adopting one, check whether you actually need what it provides:

| Problem | Simpler alternative |
|---|---|
| Encryption between services | Istio mTLS | Network policies + cert-manager |
| Retries | Service mesh | Client library (tenacity, go-retry) |
| Canary deployments | Istio VirtualService | Argo Rollouts, Flagger |
| Distributed tracing | Any mesh | OpenTelemetry SDK in your app |
| Circuit breaking | Any mesh | Resilience4j, go-resiliency |

The honest answer: if you have fewer than ~10 services and a small team, a service mesh is probably more complexity than it's worth. If you have 50+ services, heterogeneous languages, and a security requirement for zero-trust networking, it earns its keep.

## Conclusion

A service mesh moves cross-cutting concerns — encryption, observability, reliability — out of application code and into the network layer. Istio gives you maximum control at the cost of significant operational complexity. Linkerd offers a production-ready experience with a much gentler learning curve. Cilium sidesteps the sidecar model entirely with eBPF for environments where performance overhead is non-negotiable. Whichever you choose — or don't choose — understanding what a service mesh does helps you make that decision deliberately rather than by cargo-culting what larger organizations run.
