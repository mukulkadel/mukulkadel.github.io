---
layout: post
title: "Local LLMs with Ollama: Run AI on Your MacBook"
date: "2026-06-01 00:00:00 +0530"
slug: local-llms-with-ollama
description: "Ollama makes running open-source LLMs like Llama 3, Mistral, and Phi-3 on your Mac as easy as a brew install. Here's everything you need to get started."
categories: ["Tutorials", "Programming"]
tags: ["ollama", "llm", "local ai", "macos", "llama", "mistral", "open source ai", "tutorial", "privacy", "offline"]
---

Running an LLM locally used to require a powerful NVIDIA GPU, a Linux machine, and a PhD in CUDA debugging. Ollama changed that. With a single command you can pull and run models like Llama 3, Mistral, Phi-3, and Qwen2 directly on your Mac — including Apple Silicon machines, where unified memory makes inference surprisingly fast. Everything stays on-device, which matters when you're working with proprietary code or sensitive documents.

## Installing Ollama

```bash
$ brew install ollama
```

Then start the background service:

```bash
$ ollama serve
```

```
time=2026-01-15T09:22:01.432Z level=INFO source=routes.go msg="Listening on 127.0.0.1:11434"
```

Leave that running in a terminal, or configure it as a launch agent so it starts automatically at login.

## Pulling and Running a Model

```bash
$ ollama pull llama3.2
```

```
pulling manifest
pulling 8eeb52dfb3bb... 100% ▕████████████████████▏ 2.0 GB
pulling 966de95ca8a6... 100% ▕████████████████████▏ 1.4 KB
verifying sha256 digest
writing manifest
success
```

Once pulled, start an interactive session:

```bash
$ ollama run llama3.2
>>> What is the capital of France?
Paris.

>>> /bye
```

Or send a single prompt non-interactively:

```bash
$ echo "Summarize the CAP theorem in two sentences." | ollama run llama3.2
```

```
The CAP theorem states that a distributed system can only guarantee two of three
properties simultaneously: Consistency, Availability, and Partition tolerance.
In the presence of a network partition, you must choose between keeping data
consistent across nodes or keeping the system available.
```

## Choosing a Model

Different models suit different tasks. Here are the most useful ones for developers:

| Model | Pull command | Best for |
|---|---|---|
| Llama 3.2 (3B) | `ollama pull llama3.2` | Fast general chat, low memory usage |
| Llama 3.1 (8B) | `ollama pull llama3.1` | Balanced quality and speed |
| Mistral (7B) | `ollama pull mistral` | Instruction following, coding |
| Phi-3 Mini | `ollama pull phi3:mini` | Very fast, works on 8 GB RAM |
| Qwen2.5-Coder | `ollama pull qwen2.5-coder` | Code generation and review |
| Deepseek-R1 | `ollama pull deepseek-r1` | Reasoning-heavy tasks |
| nomic-embed-text | `ollama pull nomic-embed-text` | Embeddings for RAG pipelines |

Check your available RAM before choosing — models load entirely into memory. A 7B model needs ~4.5 GB, 13B needs ~8 GB, 70B needs ~40 GB.

```bash
$ system_profiler SPHardwareDataType | grep Memory
      Memory: 16 GB
```

## Using the REST API

Ollama exposes a local REST API on port 11434, making it easy to call from any language or to drop into apps that already talk to the OpenAI API.

```bash
$ curl http://localhost:11434/api/generate \
    -d '{
      "model": "llama3.2",
      "prompt": "Write a Python one-liner that reverses a list.",
      "stream": false
    }'
```

```json
{
  "model": "llama3.2",
  "response": "reversed_list = original_list[::-1]",
  "done": true,
  "total_duration": 1234567890
}
```

### Using with the Python Client

```bash
$ pip install ollama
```

```python
import ollama

response = ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Explain async/await in Python in 3 bullet points."}],
)
print(response["message"]["content"])
```

```
• async def marks a function as a coroutine — it doesn't run until awaited.
• await suspends the current coroutine and yields control to the event loop.
• This lets a single thread handle many I/O-bound tasks concurrently without blocking.
```

### OpenAI-Compatible Endpoint

Ollama also exposes an OpenAI-compatible endpoint so you can use it as a drop-in replacement in apps built against the OpenAI SDK — no code changes needed beyond the base URL.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

response = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "What's the time complexity of merge sort?"}],
)
print(response.choices[0].message.content)
```

```
Merge sort has O(n log n) time complexity for best, average, and worst cases.
It achieves this by recursively dividing the array in half (log n levels) and
merging each level in O(n) time.
```

## Customizing Models with Modelfiles

You can create a custom model persona using a `Modelfile` — similar to a Dockerfile but for LLMs.

```
FROM llama3.2

SYSTEM """
You are a senior code reviewer. When reviewing code, focus on:
- Correctness and edge cases
- Performance implications
- Security vulnerabilities
Respond concisely. Point out issues directly without preamble.
"""

PARAMETER temperature 0.2
PARAMETER top_p 0.9
```

```bash
$ ollama create code-reviewer -f Modelfile
$ ollama run code-reviewer
>>> Review this: def divide(a, b): return a / b
Missing division-by-zero check. Raises ZeroDivisionError on b=0.
Fix: if b == 0: raise ValueError("divisor cannot be zero")
```

## Running Embeddings Locally

For RAG pipelines where you want everything private and offline:

```bash
$ ollama pull nomic-embed-text
```

```python
import ollama

response = ollama.embeddings(
    model="nomic-embed-text",
    prompt="The quick brown fox jumps over the lazy dog.",
)
print(f"Dimensions: {len(response['embedding'])}")
```

```
Dimensions: 768
```

You can plug this directly into any vector database that accepts float arrays — Chroma, pgvector, or Qdrant.

## Conclusion

Ollama removes the friction from local AI experimentation — installation takes two minutes, model switching is a single command, and the OpenAI-compatible API means you can swap it into most existing projects immediately. For work involving sensitive code, internal documents, or just wanting zero latency and no API costs, running locally is a practical choice, not just a novelty. Start with `llama3.2` for general tasks and `qwen2.5-coder` for anything code-related.
