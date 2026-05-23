---
layout: post
title: "Understanding WebSockets vs HTTP Long Polling"
date: "2026-05-23 00:00:00 +0530"
slug: websockets-vs-http-long-polling
description: "Compare WebSockets, HTTP long polling, and Server-Sent Events for real-time features — with code examples and guidance on when to choose each approach."
categories: ["wiki", "Programming"]
tags: ["websockets", "http", "long polling", "real-time", "web development", "networking", "backend", "api", "sse", "node.js", "server-sent events"]
---

Building real-time features — live notifications, chat, dashboards, collaborative editing — forces a fundamental question: how do you push data from server to client without the client asking for it? HTTP was designed as a request-response protocol, which means clients ask and servers answer. Every technique for real-time communication is a workaround for this constraint, and each one trades different things.

## Short Polling

The simplest approach: the client asks repeatedly on a timer.

```javascript
// Client polls every 2 seconds
setInterval(async () => {
    const res = await fetch('/api/notifications');
    const data = await res.json();
    if (data.length > 0) updateUI(data);
}, 2000);
```

**The problem**: 99% of these requests return nothing. You're hammering your server with empty responses, adding latency proportional to your polling interval, and keeping connections open on every client constantly.

Short polling is only acceptable for very infrequent updates (check every 5–10 minutes) or during development when you want something working fast.

## Long Polling

Long polling is the first real step toward real-time. The client sends a request, and the server holds it open until new data is available (or a timeout fires):

```python
# Flask server — holds the request open
from flask import Flask, Response
import time

app = Flask(__name__)

@app.route('/poll')
def poll():
    timeout = time.time() + 30  # hold for up to 30 seconds
    while time.time() < timeout:
        new_data = check_for_updates()
        if new_data:
            return {'data': new_data}
        time.sleep(0.5)
    return {'data': None}  # timeout, client re-polls
```

```javascript
// Client re-establishes the connection immediately after each response
async function longPoll() {
    try {
        const res = await fetch('/poll');
        const data = await res.json();
        if (data.data) updateUI(data.data);
    } finally {
        longPoll();  // immediately start next poll
    }
}
longPoll();
```

Long polling reduces unnecessary traffic compared to short polling. The server only responds when there's something to say. But it still creates one HTTP request per update cycle, and the overhead of HTTP headers and connection setup adds up.

## Server-Sent Events (SSE)

SSE is the underappreciated middle ground. The client opens a single HTTP connection and the server streams events down it indefinitely, using a simple text format:

```python
# Flask SSE server
from flask import Flask, Response, stream_with_context
import time, json

app = Flask(__name__)

@app.route('/events')
def events():
    def generate():
        while True:
            data = get_new_data()
            if data:
                yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)
    return Response(stream_with_context(generate()),
                    mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache',
                             'X-Accel-Buffering': 'no'})
```

```javascript
// Client
const es = new EventSource('/events');
es.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
};
es.onerror = () => {
    // Browser automatically reconnects
};
```

SSE uses regular HTTP, works through proxies and firewalls, is natively supported by browsers, and the browser handles reconnection automatically. The limitation: it's one-directional (server → client only). You send client updates via separate POST requests.

## WebSockets

WebSockets provide a full-duplex, persistent connection. After an initial HTTP upgrade handshake, both sides can send messages at any time:

```
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
```

After the handshake, the connection is raw WebSocket — no HTTP overhead per message.

```javascript
// Node.js server with the 'ws' library
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
    ws.on('message', (message) => {
        console.log('Received:', message.toString());
        // Broadcast to all connected clients
        wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(message.toString());
            }
        });
    });

    ws.send(JSON.stringify({ type: 'welcome', message: 'Connected' }));
});
```

```javascript
// Browser client
const ws = new WebSocket('wss://example.com/ws');

ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'chat', text: 'Hello!' }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
};

ws.onclose = () => {
    // Implement reconnection logic yourself
    setTimeout(connect, 3000);
};
```

## Comparison

| | Short Polling | Long Polling | SSE | WebSockets |
|---|---|---|---|---|
| **Direction** | Client → Server | Client → Server | Server → Client | Bidirectional |
| **Latency** | High (interval-based) | Low | Low | Very low |
| **Connection overhead** | High | Medium | Low (single conn) | Lowest |
| **Proxy/firewall friendly** | Yes | Yes | Yes | Sometimes |
| **Browser reconnect** | Manual | Manual | Automatic | Manual |
| **HTTP/2 compatible** | Yes | Yes | Yes | No (separate protocol) |
| **Server complexity** | Low | Medium | Medium | High |

## When to Use What

**Short polling** — Only for non-urgent checks (every few minutes). Checking if a background job finished every 10 seconds is fine.

**Long polling** — Good fallback when WebSocket support is uncertain, or for simple notification scenarios where you want HTTP semantics and standard load balancer behavior.

**Server-Sent Events** — The best choice for server-to-client streams: live dashboards, activity feeds, log tails, price tickers. Works through HTTP/2 multiplexing with zero extra configuration. Use it more often than you think to.

**WebSockets** — Necessary when you need bidirectional, low-latency communication: chat, multiplayer games, collaborative editors, live trading platforms. The added complexity (connection management, reconnection logic, proxy configuration) is worth it when the use case genuinely requires it.

## Conclusion

The right choice comes down to whether you need bidirectional communication. If you only need server-to-client streaming, SSE is simpler and more widely compatible than WebSockets. If you need the client to also stream data to the server continuously, WebSockets are the right tool. Long polling is the robust fallback for environments where you can't control the infrastructure. Most "real-time" features — notifications, feeds, live stats — are server-to-client and belong on SSE, not WebSockets.
