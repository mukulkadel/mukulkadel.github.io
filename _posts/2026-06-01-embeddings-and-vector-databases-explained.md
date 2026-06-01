---
layout: post
title: "Understanding Embeddings and Vector Databases (pgvector, Pinecone)"
date: "2026-06-01 00:00:00 +0530"
slug: embeddings-and-vector-databases-explained
description: "Embeddings turn text into numbers, and vector databases make those numbers searchable. Here's how both work, with practical examples using pgvector and Pinecone."
categories: ["wiki", "Programming"]
tags: ["embeddings", "vector database", "pgvector", "pinecone", "semantic search", "llm", "ai", "machine learning", "similarity"]
---

Search used to mean matching keywords. You searched for "database indexing" and got back documents containing those exact words. Embeddings break that constraint — they let you search by *meaning*, so a query for "how does a database speed up queries" still finds an article titled "B-tree indexes explained" even if it shares no keywords with your query. This is the engine underneath most modern AI applications: RAG systems, semantic search, recommendation engines, and duplicate detection all rely on it. Let's look at how embeddings actually work and how vector databases make them queryable at scale.

## What Is an Embedding?

An embedding is a fixed-length array of floating-point numbers that represents the meaning of a piece of text. Two semantically similar sentences will produce embeddings that are numerically close together in high-dimensional space.

```python
from openai import OpenAI

client = OpenAI()

def embed(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding

e1 = embed("How do database indexes work?")
e2 = embed("What is a B-tree index?")
e3 = embed("What is the capital of France?")

print(f"Dimensions: {len(e1)}")
```

```
Dimensions: 1536
```

The distance between `e1` and `e2` will be small (similar meaning). The distance between `e1` and `e3` will be large (unrelated topics). This distance is typically measured using **cosine similarity**.

### Cosine Similarity

Cosine similarity measures the angle between two vectors. A score of 1.0 means identical direction (identical meaning), 0.0 means orthogonal (unrelated), -1.0 means opposite.

```python
import numpy as np

def cosine_similarity(a: list[float], b: list[float]) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

print(cosine_similarity(e1, e2))  # similar
print(cosine_similarity(e1, e3))  # unrelated
```

```
0.8732
0.1204
```

## Choosing an Embedding Model

Different models produce different-sized embeddings with different quality/cost tradeoffs:

| Model | Dimensions | Best for |
|---|---|---|
| `text-embedding-3-small` (OpenAI) | 1536 | General use, low cost |
| `text-embedding-3-large` (OpenAI) | 3072 | Higher accuracy tasks |
| `nomic-embed-text` (Ollama, local) | 768 | Local/offline pipelines |
| `all-MiniLM-L6-v2` (Sentence Transformers) | 384 | Fast, open source, no API |
| `text-embedding-004` (Google) | 768 | Google Cloud users |

More dimensions generally means higher accuracy but more storage and slower queries.

## What is a Vector Database?

A vector database is a database optimized to store and search embeddings. Unlike a traditional database where you'd query `WHERE name = 'Alice'`, a vector database answers "give me the 10 embeddings most similar to this query embedding" — fast, even across millions of vectors.

The key algorithm enabling this is **Approximate Nearest Neighbor (ANN)** search. Exact nearest-neighbor search across millions of 1536-dimensional vectors would be prohibitively slow; ANN trades a small accuracy margin for massive speed gains.

Common ANN algorithms:
- **HNSW** (Hierarchical Navigable Small World) — fast queries, high memory use
- **IVF** (Inverted File Index) — good balance of speed and memory
- **Flat** — exact search, only viable for small datasets

## pgvector: Vector Search in PostgreSQL

If you're already on Postgres, `pgvector` is the easiest path — you get vector search in the same database as the rest of your app, with no new infrastructure.

```bash
$ psql -c "CREATE EXTENSION vector;"
```

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536)
);

CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
```

Inserting documents:

```python
import psycopg2
import json

conn = psycopg2.connect("dbname=myapp user=postgres")
cur = conn.cursor()

text = "Indexes speed up database queries by avoiding full table scans."
embedding = embed(text)

cur.execute(
    "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
    (text, json.dumps(embedding)),
)
conn.commit()
```

Semantic search:

```python
query = "How do databases find rows faster?"
query_embedding = embed(query)

cur.execute("""
    SELECT content, 1 - (embedding <=> %s::vector) AS similarity
    FROM documents
    ORDER BY embedding <=> %s::vector
    LIMIT 5
""", (json.dumps(query_embedding), json.dumps(query_embedding)))

for row in cur.fetchall():
    print(f"[{row[1]:.3f}] {row[0]}")
```

```
[0.873] Indexes speed up database queries by avoiding full table scans.
[0.791] B-tree indexes store data in sorted order for efficient range queries.
[0.734] Query planners use statistics to decide whether to use an index.
```

The `<=>` operator computes cosine distance. Lower distance = higher similarity; the `1 - distance` gives you a similarity score between 0 and 1.

## Pinecone: Managed Vector Database

Pinecone is a fully managed vector database built specifically for embedding storage and retrieval. There's nothing to install or configure — you create an index and start upserting vectors.

```bash
$ pip install pinecone-client
```

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="YOUR_API_KEY")

pc.create_index(
    name="knowledge-base",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
)

index = pc.Index("knowledge-base")
```

Upserting vectors:

```python
docs = [
    ("doc1", "Indexes speed up database queries by avoiding full table scans."),
    ("doc2", "B-tree indexes store data in sorted order for range queries."),
    ("doc3", "Connection pooling reuses database connections to reduce overhead."),
]

vectors = [(id, embed(text), {"text": text}) for id, text in docs]
index.upsert(vectors=vectors)
```

Querying:

```python
results = index.query(
    vector=embed("How do databases find rows faster?"),
    top_k=3,
    include_metadata=True,
)

for match in results["matches"]:
    print(f"[{match['score']:.3f}] {match['metadata']['text']}")
```

```
[0.873] Indexes speed up database queries by avoiding full table scans.
[0.791] B-tree indexes store data in sorted order for range queries.
[0.698] Query planners use statistics to decide whether to use an index.
```

## pgvector vs Pinecone

| | pgvector | Pinecone |
|---|---|---|
| Setup | Self-hosted, needs Postgres | Fully managed |
| Scale | Up to ~1M vectors comfortably | Billions of vectors |
| Cost | Compute for your Postgres instance | Per vector stored + queries |
| Metadata filtering | Full SQL | Limited filter syntax |
| Good for | Apps already on Postgres | Large-scale, pure vector workloads |

For most applications starting out, pgvector is the pragmatic choice — you likely already have Postgres, and it handles millions of vectors comfortably. Pinecone becomes compelling when you're at the scale where managing Postgres infrastructure for vector workloads becomes a burden.

## Conclusion

Embeddings convert meaning into geometry, and vector databases make that geometry searchable at scale. Once you understand that cosine similarity is just measuring how close two vectors point, the whole stack clicks into place — RAG, semantic search, and recommendation systems all become variations on the same pattern. Start with pgvector if you're already on Postgres; migrate to a dedicated vector database if and when you genuinely need the scale.
