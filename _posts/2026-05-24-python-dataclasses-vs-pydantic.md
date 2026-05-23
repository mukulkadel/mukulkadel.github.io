---
layout: post
title: "Python Dataclasses vs Pydantic: When to Use Which"
date: "2026-05-24 00:00:00 +0530"
slug: python-dataclasses-vs-pydantic
description: "A practical comparison of Python dataclasses and Pydantic models — covering validation, serialization, performance, and when each tool is the right choice."
categories: ["Programming", "wiki"]
tags: ["python", "pydantic", "dataclasses", "validation", "type hints", "models", "fastapi", "backend", "comparison"]
---

Python's `dataclasses` module and the Pydantic library solve similar problems — defining structured data with type hints — but they make very different trade-offs. Dataclasses are lightweight and part of the standard library; Pydantic adds runtime validation, coercion, and serialization at the cost of a dependency. Knowing when each is appropriate saves you from over-engineering simple code or under-protecting API boundaries.

## Python Dataclasses

`dataclasses` (added in Python 3.7) auto-generates `__init__`, `__repr__`, and `__eq__` from class annotations. It's great for data containers where you control all the inputs.

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: Optional[str] = None
    tags: list[str] = field(default_factory=list)

user = User(id=1, name="Alice")
print(user)
# User(id=1, name='Alice', email=None, tags=[])
```

Key features:

```python
@dataclass(frozen=True)   # immutable, hashable
@dataclass(order=True)    # enables <, >, <=, >=
@dataclass(slots=True)    # faster attribute access (Python 3.10+)
```

**What dataclasses don't do**: they don't validate types at runtime. Passing `id="not-an-int"` will work without complaint.

```python
user = User(id="oops", name="Bob")  # no error raised
print(user.id)  # "oops"
```

## Pydantic Models

Pydantic validates data at construction time and coerces values when it can do so safely. It's the foundation of FastAPI and is a natural fit for anything that handles external data.

```python
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    tags: list[str] = []

user = User(id="42", name="Alice")  # "42" is coerced to int
print(user.id)  # 42

User(id="oops", name="Bob")
# ValidationError: id: Input should be a valid integer
```

Pydantic v2 (released 2023) is significantly faster than v1 thanks to a Rust core. Install it with:

```bash
$ pip install pydantic[email]
```

## Validation and Coercion

Pydantic distinguishes between **strict mode** (no coercion) and **lax mode** (the default, which coerces `"42"` → `42`):

```python
from pydantic import BaseModel

class StrictUser(BaseModel):
    model_config = {"strict": True}
    id: int

StrictUser(id="42")
# ValidationError — string not accepted in strict mode
```

Custom validators:

```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    name: str
    price: float

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be positive")
        return v
```

## Serialization

Pydantic models serialize to dict and JSON out of the box:

```python
user = User(id=1, name="Alice", tags=["admin"])
print(user.model_dump())
# {'id': 1, 'name': 'Alice', 'email': None, 'tags': ['admin']}

print(user.model_dump_json())
# '{"id":1,"name":"Alice","email":null,"tags":["admin"]}'

# Parse from dict or JSON
user2 = User.model_validate({"id": 2, "name": "Bob"})
user3 = User.model_validate_json('{"id": 3, "name": "Carol"}')
```

With dataclasses, you get none of this for free — you'd reach for `dataclasses.asdict()` (which gives a plain dict but doesn't serialize custom types) or a library like `marshmallow`.

## Nested Models and Composition

Both work with nesting, but Pydantic validates the whole tree:

```python
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str

class Customer(BaseModel):
    name: str
    address: Address

customer = Customer(
    name="Alice",
    address={"street": "123 Main St", "city": "Mumbai"}  # dict is auto-converted
)
print(customer.address.city)  # Mumbai
```

With dataclasses, you'd need to construct `Address` explicitly.

## Performance

For pure in-memory data containers with no external input, dataclasses are faster — no validation overhead. For request/response parsing, Pydantic v2's Rust core is fast enough that the overhead is negligible at typical API volumes.

A rough guide:

| Scenario | Use |
|---|---|
| Internal data transfer, known inputs | `dataclass` |
| Config objects from env or YAML | `dataclass` or `pydantic` |
| API request/response bodies | `pydantic` |
| FastAPI path parameters and bodies | `pydantic` (mandatory) |
| CLI argument parsing | `dataclass` + `argparse` |
| Database ORM row mapping | `pydantic` or ORM-specific models |

## Using Both Together

You can use `pydantic.dataclasses.dataclass` to get Pydantic validation with dataclass syntax:

```python
from pydantic.dataclasses import dataclass

@dataclass
class Item:
    id: int
    name: str
    price: float

Item(id="5", name="Widget", price="9.99")
# id coerced to 5, price coerced to 9.99
```

This is useful when you want the ergonomics of `@dataclass` (frozen, slots, etc.) but still need runtime validation.

## Conclusion

The decision is straightforward once you know the boundary: if data comes from outside your process — an HTTP request, a config file, a message queue — use Pydantic to validate and coerce it at the entry point. For data that stays inside your application and whose shape you fully control, a plain `dataclass` is lighter and just as clear. In FastAPI projects, Pydantic is a given; everywhere else, let the source of the data make the decision for you.
