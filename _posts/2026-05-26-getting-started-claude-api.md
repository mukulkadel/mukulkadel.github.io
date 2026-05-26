---
layout: post
title: "Getting Started with the Claude API: Your First AI-Powered App"
date: "2026-05-26 00:00:00 +0530"
slug: getting-started-claude-api
description: "A hands-on guide to building your first app with the Claude API — authentication, sending messages, system prompts, streaming responses, and handling errors."
categories: ["Programming", "Tutorials"]
tags: ["claude", "anthropic", "llm", "ai", "api", "python", "tutorial", "generative ai", "chatbot", "sdk"]
---

The Claude API gives you programmatic access to Anthropic's Claude models — the same intelligence behind Claude.ai, exposed as a simple HTTP API with official SDKs for Python and TypeScript. Whether you're building a chatbot, a document summarizer, a code reviewer, or an AI-powered CLI tool, the setup is the same. This guide gets you from API key to working application.

## Setup

Install the Anthropic Python SDK:

```bash
$ pip install anthropic
```

Get your API key from the Anthropic Console and store it as an environment variable:

```bash
$ export ANTHROPIC_API_KEY="sk-ant-..."
```

Never hardcode the key in source files — read it from the environment.

## Your First Message

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY automatically

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain recursion in one paragraph."}
    ]
)

print(message.content[0].text)
```

```
$ python main.py
Recursion is a programming technique where a function calls itself to solve a
problem by breaking it down into smaller instances of the same problem. Each
recursive call works on a smaller input until it reaches a base case — a
condition that returns a result directly without further recursion — and then
the results cascade back up through all the calls. A classic example is
computing factorials: factorial(5) calls factorial(4), which calls
factorial(3), and so on until factorial(1) returns 1, and the chain resolves
back upward: 1 × 2 × 3 × 4 × 5 = 120.
```

## The Messages API Structure

Every request sends a list of `messages` with alternating `user` and `assistant` roles:

```python
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=[
        {"role": "user", "content": "What is the capital of France?"},
        {"role": "assistant", "content": "The capital of France is Paris."},
        {"role": "user", "content": "What's the population of that city?"},
    ]
)
```

The `messages` list is how you maintain conversation context — include the full history of the conversation in each request. Claude doesn't maintain state between requests; you do.

The response object:

```python
print(message.model)              # claude-sonnet-4-6
print(message.stop_reason)        # "end_turn" or "max_tokens"
print(message.usage.input_tokens)  # tokens in your messages
print(message.usage.output_tokens) # tokens in the response
print(message.content[0].text)    # the response text
```

## System Prompts

A system prompt sets the context, persona, and instructions for Claude's behavior. It's the first thing in the request, before the conversation:

```python
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="""You are a senior code reviewer specializing in Python.
When reviewing code, you:
- Point out bugs and potential exceptions
- Suggest more idiomatic Python patterns
- Comment on readability and maintainability
- Keep feedback actionable and specific""",
    messages=[
        {"role": "user", "content": """Please review this function:

def get_user(id):
    users = load_all_users()
    for u in users:
        if u['id'] == id:
            return u
"""}
    ]
)

print(message.content[0].text)
```

## Streaming Responses

For long responses, streaming lets you display text as it's generated rather than waiting for the full response:

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=[{"role": "user", "content": "Write a short story about a robot."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print()  # newline after streaming completes

# Access final message after stream
final = stream.get_final_message()
print(f"\nTokens used: {final.usage.input_tokens + final.usage.output_tokens}")
```

## Building a Simple Chatbot

A complete interactive chatbot that maintains conversation history:

```python
import anthropic

client = anthropic.Anthropic()
conversation_history = []

def chat(user_message: str) -> str:
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="You are a helpful assistant. Be concise and direct.",
        messages=conversation_history
    )

    assistant_message = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message

def main():
    print("Chat with Claude (type 'quit' to exit)\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        response = chat(user_input)
        print(f"Claude: {response}\n")

if __name__ == "__main__":
    main()
```

```
$ python chatbot.py
Chat with Claude (type 'quit' to exit)

You: What's 15% of 240?
Claude: 15% of 240 is 36.

You: And 20% of that result?
Claude: 20% of 36 is 7.2.
```

## Error Handling

The SDK raises specific exceptions you should handle:

```python
import anthropic

client = anthropic.Anthropic()

try:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(message.content[0].text)

except anthropic.AuthenticationError:
    print("Invalid API key — check ANTHROPIC_API_KEY")

except anthropic.RateLimitError as e:
    print(f"Rate limit hit — back off and retry: {e}")

except anthropic.APIStatusError as e:
    print(f"API error {e.status_code}: {e.message}")
```

For production, add exponential backoff on rate limit errors:

```python
import time
import anthropic

def create_with_retry(client, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt  # 1s, 2s, 4s
            print(f"Rate limited. Waiting {wait}s...")
            time.sleep(wait)
```

## Choosing a Model

| Model | Best for |
|-------|----------|
| `claude-opus-4-7` | Complex reasoning, nuanced writing, difficult coding tasks |
| `claude-sonnet-4-6` | Balanced performance and cost — the everyday workhorse |
| `claude-haiku-4-5-20251001` | Fast, inexpensive — classification, extraction, simple Q&A |

Start with Sonnet. Switch to Opus for tasks where quality matters more than cost; switch to Haiku for high-volume, simpler tasks.

## Token Limits and Cost

Each model has a context window — the maximum total tokens (input + output) per request. Pricing is per million tokens, billed separately for input and output.

```python
# Estimate token count before sending (rough: 1 token ≈ 4 characters)
def estimate_tokens(text: str) -> int:
    return len(text) // 4

# Or use the SDK's token counting endpoint
count = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "Your long text here..."}]
)
print(f"Input tokens: {count.input_tokens}")
```

## TypeScript Example

The TypeScript SDK follows the same pattern:

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();  // reads ANTHROPIC_API_KEY

const message = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 1024,
    messages: [{ role: 'user', content: 'Hello, Claude!' }],
});

console.log(message.content[0].type === 'text' ? message.content[0].text : '');
```

## Conclusion

The Claude API is straightforward: create a client, pass a `messages` array with user/assistant turns, and optionally a `system` prompt to set behavior. The key things to internalize are: Claude is stateless (you manage conversation history), use streaming for real-time UX, and pick the right model tier for your use case. From this foundation you can build summarizers, code reviewers, document chatbots, and anything else that needs language understanding.
