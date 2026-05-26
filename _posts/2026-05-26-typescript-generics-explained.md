---
layout: post
title: "TypeScript Generics Explained with Practical Examples"
date: "2026-05-26 00:00:00 +0530"
slug: typescript-generics-explained
description: "A practical guide to TypeScript generics — type parameters, constraints, multiple generics, generic functions, generic interfaces, and built-in utility types with real examples."
categories: ["Programming", "wiki"]
tags: ["typescript", "generics", "types", "frontend", "backend", "javascript", "tutorial", "type safety", "interfaces"]
---

Generics are the feature that separates basic TypeScript from truly expressive TypeScript. They let you write functions, classes, and interfaces that work over a range of types while preserving type safety — the same logic, without losing the type information that makes TypeScript useful. Once you understand them, you'll use them constantly.

## The Problem Generics Solve

Without generics, you face a choice: write a function for one specific type, or lose type information by using `any`.

```typescript
// Specific — only works for strings
function firstString(arr: string[]): string {
    return arr[0];
}

// Flexible but loses type info
function firstAny(arr: any[]): any {
    return arr[0];
}

const result = firstAny([1, 2, 3]);
result.toUpperCase();  // TypeScript allows this — but it will crash at runtime
```

Generics solve this by letting the function carry the type through:

```typescript
function first<T>(arr: T[]): T {
    return arr[0];
}

const num = first([1, 2, 3]);          // TypeScript infers: num is number
const str = first(['a', 'b', 'c']);    // str is string
const obj = first([{ id: 1 }]);        // obj is { id: number }

obj.toUpperCase();  // TypeScript error — { id: number } has no toUpperCase
```

`T` is a **type parameter** — a placeholder that TypeScript fills in based on what you pass. The type flows through and is preserved.

## Generic Functions

Type parameters go in angle brackets before the function's parameter list:

```typescript
function identity<T>(value: T): T {
    return value;
}

// TypeScript infers T from the argument
const a = identity(42);      // T = number
const b = identity('hello'); // T = string

// Or explicitly specify T
const c = identity<boolean>(true);
```

Multiple type parameters work just like multiple function parameters:

```typescript
function pair<A, B>(first: A, second: B): [A, B] {
    return [first, second];
}

const p = pair(1, 'hello');  // [number, string]
const q = pair(true, { id: 1 });  // [boolean, { id: number }]
```

A common generic pattern — transforming arrays:

```typescript
function map<T, U>(arr: T[], fn: (item: T) => U): U[] {
    return arr.map(fn);
}

const lengths = map(['hello', 'world'], s => s.length);  // number[]
const doubled = map([1, 2, 3], n => n * 2);              // number[]
```

## Generic Interfaces and Types

Generics work on interfaces and type aliases too:

```typescript
interface ApiResponse<T> {
    data: T;
    status: number;
    message: string;
}

interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    pageSize: number;
}

// Concrete types
type UserResponse = ApiResponse<User>;
type PostListResponse = PaginatedResponse<Post>;

function fetchUser(id: string): Promise<ApiResponse<User>> {
    return fetch(`/api/users/${id}`).then(r => r.json());
}
```

This pattern is useful for API response wrappers — define the envelope once, parameterize the payload type.

## Generic Classes

```typescript
class Stack<T> {
    private items: T[] = [];

    push(item: T): void {
        this.items.push(item);
    }

    pop(): T | undefined {
        return this.items.pop();
    }

    peek(): T | undefined {
        return this.items[this.items.length - 1];
    }

    get size(): number {
        return this.items.length;
    }
}

const numStack = new Stack<number>();
numStack.push(1);
numStack.push(2);
numStack.pop();   // number | undefined

const strStack = new Stack<string>();
strStack.push('hello');
strStack.push(42);  // TypeScript error — 42 is not a string
```

## Constraints: `extends`

Sometimes you want T to have certain properties — not completely unconstrained. Use `extends` to constrain the type parameter:

```typescript
// T must have a length property
function longest<T extends { length: number }>(a: T, b: T): T {
    return a.length >= b.length ? a : b;
}

longest('hello', 'hi');        // works — strings have length
longest([1, 2, 3], [1, 2]);    // works — arrays have length
longest(10, 20);               // TypeScript error — numbers have no length
```

A very common pattern — `keyof` constraints ensure you only access keys that exist:

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
    return obj[key];
}

const user = { name: 'Alice', age: 30, email: 'alice@example.com' };

getProperty(user, 'name');    // string
getProperty(user, 'age');     // number
getProperty(user, 'phone');   // TypeScript error — 'phone' is not in user
```

## Default Type Parameters

Type parameters can have defaults, just like function parameters:

```typescript
interface Container<T = string> {
    value: T;
    label: string;
}

const c1: Container = { value: 'hello', label: 'name' };    // T defaults to string
const c2: Container<number> = { value: 42, label: 'age' };  // T = number
```

## Conditional Types

A more advanced feature — types that change based on a condition:

```typescript
type IsArray<T> = T extends any[] ? true : false;

type A = IsArray<string[]>;  // true
type B = IsArray<number>;    // false

// Unwrap array type
type Unwrap<T> = T extends (infer U)[] ? U : T;

type C = Unwrap<string[]>;  // string
type D = Unwrap<number>;    // number
```

The `infer` keyword captures a type within the conditional — `infer U` says "call whatever is in the array position U."

## Built-in Utility Types

TypeScript ships with generic utility types that are useful daily:

```typescript
interface User {
    id: number;
    name: string;
    email: string;
    password: string;
}

// Partial<T> — all properties optional
type PartialUser = Partial<User>;
// { id?: number; name?: string; email?: string; password?: string }

// Required<T> — all properties required
type RequiredUser = Required<PartialUser>;

// Pick<T, K> — select specific properties
type PublicUser = Pick<User, 'id' | 'name' | 'email'>;
// { id: number; name: string; email: string }

// Omit<T, K> — exclude specific properties
type SafeUser = Omit<User, 'password'>;
// { id: number; name: string; email: string }

// Readonly<T> — all properties readonly
type ReadonlyUser = Readonly<User>;

// Record<K, V> — create an object type with specific keys and value type
type UserMap = Record<string, User>;
// { [key: string]: User }

// ReturnType<T> — extract the return type of a function
function getUser(): User { /* ... */ return {} as User; }
type UserType = ReturnType<typeof getUser>;  // User

// Parameters<T> — extract function parameter types as a tuple
function createUser(name: string, email: string): User { /* ... */ return {} as User; }
type CreateUserParams = Parameters<typeof createUser>;  // [string, string]
```

## A Real-World Example: Generic Repository

Generics shine when building shared infrastructure:

```typescript
interface Entity {
    id: string;
}

class Repository<T extends Entity> {
    private items = new Map<string, T>();

    findById(id: string): T | undefined {
        return this.items.get(id);
    }

    save(item: T): void {
        this.items.set(item.id, item);
    }

    findAll(): T[] {
        return Array.from(this.items.values());
    }

    findWhere(predicate: (item: T) => boolean): T[] {
        return this.findAll().filter(predicate);
    }
}

interface User extends Entity {
    name: string;
    email: string;
}

interface Post extends Entity {
    title: string;
    authorId: string;
}

const userRepo = new Repository<User>();
const postRepo = new Repository<Post>();

userRepo.save({ id: '1', name: 'Alice', email: 'alice@example.com' });
const alice = userRepo.findById('1');   // User | undefined
alice?.name;    // TypeScript knows this is a string

postRepo.findWhere(p => p.authorId === '1');  // Post[]
```

One `Repository` class, fully type-safe for any entity type.

## Conclusion

Generics enable you to write once and type correctly for many — the key insight is that type parameters are to types what function parameters are to values. Start with generic functions (the most common use case), then move to generic interfaces for shared shapes like API responses, then constraints when you need T to satisfy a specific structure. The built-in utility types (`Partial`, `Pick`, `Omit`, `Record`) solve common transformation problems without needing to define new types from scratch.
