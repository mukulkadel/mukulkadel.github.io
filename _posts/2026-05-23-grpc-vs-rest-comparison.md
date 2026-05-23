---
layout: post
title: "gRPC vs REST: Which One Should You Use?"
date: "2026-05-23 00:00:00 +0530"
slug: grpc-vs-rest-comparison
description: "A practical comparison of gRPC and REST APIs covering performance, tooling, streaming, and when each protocol is the right choice for your backend."
categories: ["wiki", "Programming"]
tags: ["grpc", "rest", "api", "protobuf", "networking", "microservices", "backend", "performance", "http2"]
---

REST has been the default API style for over a decade, and for good reason — it's simple, human-readable, and works everywhere. But REST has real limitations when you're building internal microservices, need bidirectional streaming, or care deeply about payload size and latency. gRPC addresses those limitations with a strongly-typed, binary protocol built on HTTP/2. Knowing which to reach for saves you from both over-engineering and painting yourself into a corner.

## What is gRPC?

gRPC is a remote procedure call framework from Google. Instead of defining routes and JSON schemas, you define a **service contract** in a `.proto` file using Protocol Buffers, and the framework generates client and server code in your language of choice.

```protobuf
syntax = "proto3";

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User);
  rpc CreateUser (CreateUserRequest) returns (User);
}

message GetUserRequest {
  string user_id = 1;
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}
```

Run `protoc` on this file and you get generated stubs in Python, Go, Java, TypeScript, or any other supported language. The client calls `stub.GetUser(request)` like a normal function call.

## Side-by-Side Comparison

| | REST | gRPC |
|---|---|---|
| **Protocol** | HTTP/1.1 or HTTP/2 | HTTP/2 only |
| **Data format** | JSON (text) | Protocol Buffers (binary) |
| **Schema** | Optional (OpenAPI) | Required (`.proto`) |
| **Code generation** | Optional | Built-in |
| **Browser support** | Native | Requires grpc-web proxy |
| **Streaming** | SSE / WebSockets (bolted on) | First-class (4 modes) |
| **Payload size** | Larger | 3–10× smaller |
| **Latency** | Higher | Lower |
| **Human readability** | Easy to inspect with curl | Binary (need grpcurl) |
| **Ecosystem** | Massive | Growing |

## Performance

gRPC's performance advantage comes from two sources:

1. **Binary encoding** — Protocol Buffers are more compact than JSON. A `User` object with 5 fields might be 200 bytes as JSON and 40 bytes as protobuf.
2. **HTTP/2 multiplexing** — multiple requests share one TCP connection, eliminating the head-of-line blocking and connection overhead of HTTP/1.1.

For high-frequency internal service calls — tens of thousands per second — this compounds into measurable throughput gains and latency reductions.

## The Four Streaming Modes

This is gRPC's biggest differentiator over REST:

```protobuf
service StreamingService {
  // classic request/response
  rpc UnaryCall (Request) returns (Response);

  // server sends a stream of responses
  rpc ServerStreaming (Request) returns (stream Response);

  // client sends a stream of requests
  rpc ClientStreaming (stream Request) returns (Response);

  // both sides stream simultaneously
  rpc BidirectionalStreaming (stream Request) returns (stream Response);
}
```

Bidirectional streaming enables real-time communication patterns that would require WebSockets over REST — chat, live data feeds, collaborative editing.

## A Minimal gRPC Server in Python

```python
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserServicer(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        # fetch from database
        return user_pb2.User(
            id=request.user_id,
            name="Mukul Kadel",
            email="mukul@example.com",
        )

    def ListUsers(self, request, context):
        users = fetch_users(limit=request.limit)
        for user in users:
            yield user_pb2.User(id=user.id, name=user.name, email=user.email)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()
```

The client:

```python
channel = grpc.insecure_channel("localhost:50051")
stub = user_pb2_grpc.UserServiceStub(channel)

user = stub.GetUser(user_pb2.GetUserRequest(user_id="abc123"))
print(user.name)  # Mukul Kadel

for user in stub.ListUsers(user_pb2.ListUsersRequest(limit=100)):
    print(user.name)
```

## Inspecting gRPC Without a Client

```bash
# like curl for gRPC
$ brew install grpcurl

# list services
$ grpcurl -plaintext localhost:50051 list

# call a method
$ grpcurl -plaintext \
  -d '{"user_id": "abc123"}' \
  localhost:50051 \
  UserService/GetUser
```

## When to Choose REST

- **Public APIs** where external developers will integrate — JSON over HTTP is universally understood
- **Browser-to-server** communication without a proxy layer
- **Simple CRUD** with standard tooling (Swagger, Postman, curl)
- **Small teams** where the overhead of `.proto` files and code generation isn't justified

## When to Choose gRPC

- **Internal microservices** communicating at high frequency
- **Streaming** — live feeds, bidirectional channels, large file uploads chunked over a stream
- **Multi-language** systems where a shared `.proto` contract prevents schema drift
- **Mobile clients** where payload size and battery life matter

## Conclusion

REST is the right default for most APIs — especially anything public-facing or browser-native. gRPC pays off when you're building a mesh of internal services where performance, strong typing, and streaming matter more than ecosystem breadth. The good news is they're not mutually exclusive: many systems use gRPC internally between services and REST externally for the public API, with a gateway layer translating between them.
