---
layout: post
title: "TypeScript for JavaScript Developers: A Quick-Start Guide"
date: "2026-05-24 00:00:00 +0530"
slug: typescript-for-javascript-developers
description: "A practical introduction to TypeScript for JavaScript developers — covering types, interfaces, generics, and the tooling setup you need to get productive fast."
categories: ["Programming", "Tutorials"]
tags: ["typescript", "javascript", "types", "frontend", "backend", "node", "tutorial", "interfaces", "generics"]
---

If you've been writing JavaScript for a while, you've probably hit the moment where a function receives the wrong shape of data and fails silently, or you have to dig through three files to figure out what properties an object actually has. TypeScript fixes these problems by adding a static type layer on top of JavaScript — and because TypeScript compiles to plain JavaScript, you can adopt it incrementally without rewriting anything.

## Setting Up TypeScript

```bash
$ npm install -D typescript
$ npx tsc --init
```

```
Created a new tsconfig.json with TS 5.x defaults.
```

The generated `tsconfig.json` controls compilation. For a Node.js project, the relevant options are:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "outDir": "dist",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src/**/*"]
}
```

Run the compiler:

```bash
$ npx tsc
$ npx tsc --watch   # re-compiles on save
```

## Basic Types

TypeScript infers types wherever it can, so you don't need to annotate everything:

```typescript
let count = 0           // inferred: number
let name = "Mukul"      // inferred: string
let active = true       // inferred: boolean

let score: number = 100 // explicit annotation
```

The types you'll use most often:

```typescript
let id: number = 42
let label: string = "hello"
let done: boolean = false
let tags: string[] = ["a", "b", "c"]
let pair: [string, number] = ["age", 30]  // tuple
let anything: unknown = getData()          // prefer over `any`
```

## Functions

Annotate parameters and return types:

```typescript
function add(a: number, b: number): number {
    return a + b
}

const greet = (name: string): string => `Hello, ${name}!`

// Optional and default parameters
function connect(host: string, port: number = 5432, ssl?: boolean): void {
    console.log(`Connecting to ${host}:${port}`)
}
```

If a function never returns (throws or loops forever), annotate it `: never`.

## Interfaces and Type Aliases

Both let you name the shape of an object. Use **interfaces** when you expect the type to be extended or implemented; use **type aliases** for unions, tuples, and computed shapes.

```typescript
interface User {
    id: number
    name: string
    email?: string  // optional
}

type Status = "active" | "inactive" | "banned"  // union

type ApiResponse<T> = {
    data: T
    status: number
    message: string
}
```

Interfaces can extend each other:

```typescript
interface AdminUser extends User {
    permissions: string[]
}
```

## Narrowing and Type Guards

TypeScript tracks types through control flow. When you check `typeof` or `instanceof`, it narrows the type inside that branch:

```typescript
function printId(id: string | number) {
    if (typeof id === "string") {
        console.log(id.toUpperCase())  // TypeScript knows id is string here
    } else {
        console.log(id.toFixed(2))     // and number here
    }
}
```

For custom types, use a **type guard**:

```typescript
function isUser(obj: unknown): obj is User {
    return typeof obj === "object" && obj !== null && "id" in obj
}
```

## Generics

Generics let you write functions and classes that work with any type while still being type-safe:

```typescript
function first<T>(arr: T[]): T | undefined {
    return arr[0]
}

const n = first([1, 2, 3])     // inferred: number | undefined
const s = first(["a", "b"])    // inferred: string | undefined
```

A common pattern is generic constraints — requiring that `T` has certain properties:

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
    return obj[key]
}

const user: User = { id: 1, name: "Alice" }
const name = getProperty(user, "name")  // string
// getProperty(user, "missing")         // compile error
```

## Enums vs Const Objects

TypeScript has `enum`, but many teams prefer `const` objects with `as const` because they produce no extra runtime code:

```typescript
// enum approach
enum Direction { Up, Down, Left, Right }

// const object approach (preferred)
const Direction = {
    Up: "UP",
    Down: "DOWN",
    Left: "LEFT",
    Right: "RIGHT",
} as const

type Direction = typeof Direction[keyof typeof Direction]
// "UP" | "DOWN" | "LEFT" | "RIGHT"
```

## Utility Types

TypeScript ships with a set of built-in generic helpers:

```typescript
interface User {
    id: number
    name: string
    email: string
    password: string
}

type PublicUser = Omit<User, "password">            // remove a key
type PartialUser = Partial<User>                     // all keys optional
type RequiredUser = Required<PartialUser>             // all keys required
type ReadonlyUser = Readonly<User>                   // immutable
type UserIdName = Pick<User, "id" | "name">          // select keys
type UserRecord = Record<string, User>               // dictionary
```

These save you from writing repetitive type definitions.

## Working with Async Code

Async functions return `Promise<T>`:

```typescript
async function fetchUser(id: number): Promise<User> {
    const res = await fetch(`/api/users/${id}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res.json() as Promise<User>
}
```

## Migrating a JavaScript File

You don't have to rewrite everything at once. Start by renaming a `.js` file to `.ts`, then fix the errors TypeScript surfaces. Set `"allowJs": true` in `tsconfig.json` to let `.js` and `.ts` files coexist during the transition:

```json
{
  "compilerOptions": {
    "allowJs": true,
    "checkJs": false
  }
}
```

Setting `"checkJs": true` later lets TypeScript type-check your remaining JavaScript files without fully converting them.

## Conclusion

TypeScript's biggest win isn't catching bugs — it's making your codebase self-documenting. When every function signature tells you exactly what it accepts and returns, you spend less time reading implementation details and more time building things. Start by enabling `"strict": true`, annotate your function boundaries first, and let inference handle the rest. You'll find that most of the friction disappears after the first few hours, and you'll struggle to go back to untyped JavaScript.
