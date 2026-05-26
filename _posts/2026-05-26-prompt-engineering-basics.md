---
layout: post
title: "Prompt Engineering Basics: Patterns That Actually Work"
date: "2026-05-26 00:00:00 +0530"
slug: prompt-engineering-basics
description: "A practical guide to prompt engineering — zero-shot, few-shot, chain-of-thought, role prompting, structured output, and patterns that reliably improve LLM responses."
categories: ["wiki", "Programming"]
tags: ["prompt engineering", "llm", "ai", "gpt", "claude", "prompts", "chain of thought", "few-shot", "generative ai"]
---

Prompt engineering is the practice of writing instructions that reliably get large language models to do what you want. It's part craft, part systems thinking, and part debugging — you write a prompt, observe the output, and iterate until the behavior is consistent. The patterns in this guide apply across models: Claude, GPT-4, Gemini, and most instruction-tuned LLMs respond to the same fundamental techniques.

## Zero-Shot Prompting

The simplest form: just ask. No examples, no scaffolding. Models pre-trained on vast text can handle many tasks zero-shot.

```python
prompt = "Translate this sentence to French: 'The train arrives at noon.'"
# → "Le train arrive à midi."

prompt = "What is the time complexity of binary search?"
# → "O(log n)..."

prompt = "Summarize this article in three bullet points:\n\n{article_text}"
```

Zero-shot works well for clear, unambiguous tasks. It breaks down when the task has many edge cases, requires specific formatting, or the desired output style is hard to describe in words.

## Few-Shot Prompting

Give the model examples of the input-output pairs you want, then present the actual input. The model learns the pattern from the examples.

```python
prompt = """Classify the sentiment of each tweet as Positive, Negative, or Neutral.

Tweet: "Just got my order! Love the quality, will definitely buy again!"
Sentiment: Positive

Tweet: "Been waiting 3 weeks for my delivery. Zero communication from support."
Sentiment: Negative

Tweet: "Package arrived. It's fine."
Sentiment: Neutral

Tweet: "The product works exactly as described in the listing."
Sentiment:"""
# → "Neutral" (or "Positive", depending on reasoning)
```

**Tips for few-shot examples:**
- Use 3–5 examples — more doesn't always help and costs tokens
- Cover edge cases and borderline inputs, not just easy ones
- Keep examples consistent in format
- Order matters slightly — later examples have more influence

## Chain-of-Thought (CoT)

For reasoning tasks (math, logic, multi-step problems), asking the model to "think step by step" dramatically improves accuracy. This is called Chain-of-Thought prompting.

**Without CoT:**
```
Q: Roger has 5 tennis balls. He buys 2 more cans of 3 balls each. How many does he have?
A: 11
```

**With CoT:**
```
Q: Roger has 5 tennis balls. He buys 2 more cans of 3 balls each. How many does he have?
A: Let me think through this step by step.
   Roger starts with 5 balls.
   He buys 2 cans × 3 balls = 6 more balls.
   Total: 5 + 6 = 11 balls.
   The answer is 11.
```

Both get the right answer here, but CoT prevents errors on harder problems where the model might otherwise "hallucinate" a plausible-sounding but wrong answer.

Trigger it explicitly:

```python
prompt = f"""Solve this problem step by step:

{problem}

Think through it carefully before giving your final answer."""
```

### Zero-Shot CoT

The phrase "Let's think step by step" or "Think through this carefully" appended to a prompt activates chain-of-thought reasoning without providing examples — surprisingly effective.

## Role Prompting

Assigning a role or persona can improve output quality for specialized tasks — not because the model "becomes" someone, but because the role activates relevant knowledge and tone patterns.

```python
system_prompt = """You are an experienced security engineer specializing in web application security.
When reviewing code, you focus on:
- Authentication and authorization flaws
- Input validation and injection vulnerabilities
- Sensitive data exposure
- Security misconfigurations
You give specific, actionable feedback and reference CVEs or OWASP categories where relevant."""
```

```python
system_prompt = """You are a technical writer creating documentation for developers.
Your documentation is:
- Clear and concise — no unnecessary words
- Structured with headers, code examples, and parameter tables
- Accurate — you only document what the code actually does"""
```

Role prompts work best in the system prompt (for APIs) rather than in the user message.

## Structured Output

When you need parseable output (JSON, YAML, tables), specify the exact format and optionally provide a schema:

```python
prompt = """Extract the following information from this job posting and return it as JSON.

Job posting:
{job_posting}

Return a JSON object with exactly these fields:
{
  "title": string,
  "company": string,
  "location": string,
  "remote": boolean,
  "salary_min": number or null,
  "salary_max": number or null,
  "required_skills": string[],
  "experience_years": number or null
}

Return only the JSON object, no explanation."""
```

Most modern models (including Claude) support structured output natively. When using the API, you can often specify a JSON schema:

```python
import anthropic
import json

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You always respond with valid JSON. No markdown, no explanation.",
    messages=[{
        "role": "user",
        "content": f"Extract job details as JSON:\n\n{job_posting}"
    }]
)

data = json.loads(response.content[0].text)
print(data["title"])
```

**Tip:** Ask the model to output JSON in the system prompt, and include "no markdown, no explanation" — otherwise you often get the JSON wrapped in a code block with surrounding text.

## Prompt Decomposition

Break complex tasks into smaller, sequential prompts instead of asking for everything at once. This reduces errors and makes each step testable.

**One big prompt (fragile):**
```python
prompt = "Read this legal contract and tell me: (1) the parties involved, (2) key obligations, (3) termination conditions, (4) any unusual clauses, and (5) suggest three negotiation points."
```

**Decomposed (more reliable):**
```python
# Step 1: Extract facts
parties = llm.call("List the parties in this contract: {contract}")
obligations = llm.call("List the key obligations for each party: {contract}")

# Step 2: Analyze (using output from step 1)
risks = llm.call(f"Given these obligations: {obligations}\nIdentify unusual or risky clauses.")

# Step 3: Recommend (using all prior context)
recommendations = llm.call(f"Parties: {parties}\nObligations: {obligations}\nRisks: {risks}\n\nSuggest 3 negotiation points.")
```

## Reducing Hallucinations

LLMs confabulate — they generate plausible-sounding but incorrect information, especially about specific facts. Several techniques reduce this:

**Cite sources or say "I don't know":**
```python
system = """Answer based only on the provided context.
If the context doesn't contain the answer, say 'I don't have enough information to answer this.'
Do not use prior knowledge."""
```

**Ask for confidence:**
```python
prompt = """Answer this question, then rate your confidence from 1-10 and briefly explain why.

Question: {question}

Format:
Answer: [your answer]
Confidence: [1-10]
Reasoning: [why you are or aren't confident]"""
```

**Verification prompting:**
```python
# Step 1: Generate answer
answer = llm.call(f"Answer this: {question}")

# Step 2: Verify the answer
verified = llm.call(f"""Original question: {question}

Proposed answer: {answer}

Is this answer correct? Point out any errors or unsupported claims.
If it's correct, say 'Verified correct.'""")
```

## Formatting Best Practices

Clear prompts produce better results. The basics:

**Use delimiters to separate sections:**
```python
prompt = f"""Summarize the following article.

Article:
\"\"\"
{article_text}
\"\"\"

Write a 3-sentence summary in plain language."""
```

**Be explicit about constraints:**
```python
# Vague
prompt = "Write a short function in Python that reverses a string."

# Specific — better results
prompt = """Write a Python function that reverses a string.
Requirements:
- Function name: reverse_string
- Input: a single string parameter
- Return: the reversed string
- Handle empty strings
- No imports needed
- Include a docstring"""
```

**Negative instructions often backfire — use positive framing:**
```python
# Tends to produce the forbidden thing occasionally
"Don't include any technical jargon."

# More reliable
"Use plain language that a non-technical reader can understand."
```

## Testing Prompts Systematically

Treat prompts like code: version them, test them on diverse inputs, measure failure rates.

```python
import anthropic

client = anthropic.Anthropic()

def evaluate_prompt(system: str, test_cases: list[dict]) -> float:
    correct = 0
    for case in test_cases:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            system=system,
            messages=[{"role": "user", "content": case["input"]}]
        )
        output = response.content[0].text.strip()
        if case["expected"].lower() in output.lower():
            correct += 1
        else:
            print(f"FAIL: {case['input'][:50]}...")
            print(f"  Expected: {case['expected']}")
            print(f"  Got: {output[:100]}")

    return correct / len(test_cases)

test_cases = [
    {"input": "I love this product!", "expected": "Positive"},
    {"input": "Terrible experience.", "expected": "Negative"},
    {"input": "It arrived on time.", "expected": "Neutral"},
]

accuracy = evaluate_prompt(sentiment_system_prompt, test_cases)
print(f"Accuracy: {accuracy:.0%}")
```

## Conclusion

The most effective prompting techniques are: few-shot examples for output format consistency, chain-of-thought for reasoning tasks, structured output specs for parseable results, and decomposition for complex multi-step tasks. The most important meta-skill is treating prompt engineering as an iterative testing process — write a prompt, run it on diverse inputs, measure where it fails, and refine. Intuition helps, but systematic evaluation beats gut feel every time.
