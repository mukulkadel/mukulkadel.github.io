---
layout: post
title: "Kubernetes Pods, Deployments, and Services Explained"
date: "2026-05-23 00:00:00 +0530"
slug: kubernetes-pods-deployments-services
description: "Understand the three core Kubernetes building blocks — Pods, Deployments, and Services — with real YAML manifests and kubectl commands."
categories: ["wiki", "Programming"]
tags: ["kubernetes", "k8s", "pods", "deployments", "services", "cloud native", "devops", "containers", "orchestration"]
---

Kubernetes manages containers at scale — it decides where they run, restarts them when they crash, and distributes traffic across replicas. But Kubernetes introduces a lot of abstractions all at once, which makes it hard to know where to start. In practice, almost everything you deploy touches three objects: **Pods**, **Deployments**, and **Services**. Understanding these three gets you 80% of the way there.

## Pods: The Smallest Deployable Unit

A **Pod** is a wrapper around one or more containers that share the same network namespace and storage. Containers in the same Pod can talk to each other on `localhost` and share mounted volumes.

You rarely create Pods directly — they're almost always managed by a Deployment. But it's useful to see the raw spec:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-pod
  labels:
    app: api
spec:
  containers:
    - name: api
      image: myapp:latest
      ports:
        - containerPort: 8000
      env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

Apply it:

```bash
$ kubectl apply -f pod.yaml
pod/api-pod created

$ kubectl get pods
NAME      READY   STATUS    RESTARTS   AGE
api-pod   1/1     Running   0          12s

$ kubectl describe pod api-pod
$ kubectl logs api-pod
$ kubectl exec -it api-pod -- sh
```

The problem with a bare Pod: if it crashes or the node it's on goes down, it's gone. Kubernetes won't reschedule it. That's Deployment's job.

## Deployments: Managing Replica Sets

A **Deployment** declares your desired state — "I want 3 replicas of this container" — and Kubernetes continuously works to make reality match it. If a Pod dies, a new one is created. If you push a new image, it rolls out gradually without downtime.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: myapp:1.4.2
          ports:
            - containerPort: 8000
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```

```bash
$ kubectl apply -f deployment.yaml
deployment.apps/api-deployment created

$ kubectl get deployments
NAME             READY   UP-TO-DATE   AVAILABLE   AGE
api-deployment   3/3     3            3           30s

$ kubectl get pods
NAME                              READY   STATUS    RESTARTS   AGE
api-deployment-7d8f9c6b4-2kxmn   1/1     Running   0          30s
api-deployment-7d8f9c6b4-9pqr8   1/1     Running   0          30s
api-deployment-7d8f9c6b4-vbzt1   1/1     Running   0          30s
```

Rolling out a new image:

```bash
$ kubectl set image deployment/api-deployment api=myapp:1.4.3
deployment.apps/api-deployment image updated

$ kubectl rollout status deployment/api-deployment
Waiting for deployment "api-deployment" rollout to finish: 1 out of 3 new replicas have been updated...
deployment "api-deployment" successfully rolled out

# something went wrong? roll back
$ kubectl rollout undo deployment/api-deployment
```

The `readinessProbe` is important — Kubernetes won't send traffic to a Pod until the probe passes, and it won't kill old Pods until new ones are ready. This is what makes zero-downtime deploys work.

## Services: Stable Network Endpoints

Pods are ephemeral. Their IP addresses change every time they're rescheduled. A **Service** provides a stable virtual IP and DNS name that routes to matching Pods via label selectors.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

```bash
$ kubectl apply -f service.yaml
service/api-service created

$ kubectl get services
NAME          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
api-service   ClusterIP   10.96.45.231   <none>        80/TCP    10s
```

Other Pods in the cluster can now reach your app at `http://api-service` (or `http://api-service.default.svc.cluster.local` with the full DNS name). The Service load-balances across all three replicas automatically.

### Service Types

| Type | What it does |
|---|---|
| `ClusterIP` | Internal only — default, no external access |
| `NodePort` | Exposes the service on each node's IP at a static port (30000–32767) |
| `LoadBalancer` | Provisions a cloud load balancer (AWS ELB, GCP LB, etc.) |
| `ExternalName` | Maps a service name to an external DNS name |

For production apps, you'd typically use `ClusterIP` with an **Ingress** controller (like Nginx Ingress or Traefik) to manage external HTTP routing — rather than exposing a `LoadBalancer` per service.

## Putting It Together

The typical flow for any app in Kubernetes:

```
Deployment → manages → ReplicaSet → manages → Pods
                                                 ↑
Service → selects Pods by label and routes traffic
```

```bash
# apply everything at once
$ kubectl apply -f deployment.yaml -f service.yaml

# check the full picture
$ kubectl get all -l app=api
NAME                                  READY   STATUS    RESTARTS   AGE
pod/api-deployment-7d8f9c6b4-2kxmn   1/1     Running   0          5m
pod/api-deployment-7d8f9c6b4-9pqr8   1/1     Running   0          5m
pod/api-deployment-7d8f9c6b4-vbzt1   1/1     Running   0          5m

NAME                             READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/api-deployment   3/3     3            3           5m

NAME                  TYPE        CLUSTER-IP     PORT(S)   AGE
service/api-service   ClusterIP   10.96.45.231   80/TCP    5m
```

## Conclusion

Pods are where your containers actually run, but you almost never manage them directly. Deployments give you self-healing and rolling updates by maintaining a desired replica count. Services give your Pods a stable address so the rest of the cluster can find them regardless of which nodes the Pods happen to land on. These three primitives are the foundation of everything else in Kubernetes — ConfigMaps, Ingresses, StatefulSets, and Jobs all build on top of them.
