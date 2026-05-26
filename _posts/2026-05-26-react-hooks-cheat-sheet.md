---
layout: post
title: "React Hooks Reference: useState, useEffect, useRef, useMemo"
date: "2026-05-26 00:00:00 +0530"
slug: react-hooks-cheat-sheet
description: "A practical React Hooks reference — useState, useEffect, useRef, useMemo, useCallback, useContext, and how to write custom hooks, with real usage patterns."
categories: ["wiki", "Programming"]
tags: ["react", "hooks", "useState", "useEffect", "useRef", "useMemo", "frontend", "javascript", "cheatsheet"]
---

React Hooks replaced class components as the primary way to write React since their introduction in React 16.8. The core idea is simple: hooks are functions that let function components tap into React state and lifecycle features. In practice, knowing when and how to reach for each hook — and when not to — takes some experience. This reference covers every hook you'll use regularly.

## `useState`

`useState` adds local state to a function component. It returns the current value and a setter function.

```javascript
import { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);       // initial value: 0
    const [name, setName] = useState('');        // initial value: empty string
    const [items, setItems] = useState([]);      // initial value: array

    return (
        <button onClick={() => setCount(count + 1)}>
            Count: {count}
        </button>
    );
}
```

### Functional updates

When the new state depends on the previous state, use the functional form to avoid stale closures:

```javascript
// Potentially stale — count might be outdated in async contexts
setCount(count + 1);

// Safe — always uses the latest state
setCount(prev => prev + 1);
```

### Lazy initialization

If computing the initial state is expensive, pass a function — it only runs once:

```javascript
// Runs on every render (bad if getParsedData() is slow)
const [data, setData] = useState(getParsedData());

// Runs only on first render
const [data, setData] = useState(() => getParsedData());
```

### Object state

When state is an object, always spread the existing state — React replaces the whole state, it doesn't merge:

```javascript
const [form, setForm] = useState({ name: '', email: '' });

// Wrong — wipes out the 'email' field
setForm({ name: 'Alice' });

// Correct
setForm(prev => ({ ...prev, name: 'Alice' }));
```

## `useEffect`

`useEffect` runs side effects after render — data fetching, subscriptions, manually updating the DOM.

```javascript
import { useEffect } from 'react';

function UserProfile({ userId }) {
    const [user, setUser] = useState(null);

    useEffect(() => {
        fetch(`/api/users/${userId}`)
            .then(r => r.json())
            .then(setUser);
    }, [userId]);  // dependency array — re-runs when userId changes

    return user ? <div>{user.name}</div> : <div>Loading...</div>;
}
```

### Dependency array behavior

```javascript
useEffect(() => { /* runs after every render */ });

useEffect(() => { /* runs once on mount */ }, []);

useEffect(() => { /* runs when a or b changes */ }, [a, b]);
```

### Cleanup function

Return a function from `useEffect` to clean up subscriptions, timers, or event listeners:

```javascript
useEffect(() => {
    const timer = setInterval(() => setTick(t => t + 1), 1000);

    // Cleanup: called before next effect run and on unmount
    return () => clearInterval(timer);
}, []);
```

```javascript
useEffect(() => {
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
}, [handleResize]);
```

### Async in useEffect

`useEffect`'s callback can't be `async` directly — define an inner async function:

```javascript
useEffect(() => {
    let cancelled = false;

    async function fetchData() {
        const data = await getUser(userId);
        if (!cancelled) setUser(data);  // avoid setting state after unmount
    }

    fetchData();
    return () => { cancelled = true; };
}, [userId]);
```

## `useRef`

`useRef` holds a mutable value that persists across renders without triggering re-renders. Its primary uses are DOM references and storing values that shouldn't cause re-renders.

### DOM reference

```javascript
import { useRef } from 'react';

function TextInput() {
    const inputRef = useRef(null);

    const focusInput = () => inputRef.current.focus();

    return (
        <>
            <input ref={inputRef} type="text" />
            <button onClick={focusInput}>Focus</button>
        </>
    );
}
```

### Storing mutable values

Unlike state, changing a ref's `.current` doesn't re-render the component — useful for timers, previous values, and flags:

```javascript
function Stopwatch() {
    const [elapsed, setElapsed] = useState(0);
    const intervalRef = useRef(null);

    const start = () => {
        intervalRef.current = setInterval(
            () => setElapsed(e => e + 1),
            1000
        );
    };

    const stop = () => clearInterval(intervalRef.current);

    return <div>{elapsed}s <button onClick={start}>Start</button></div>;
}
```

### Tracking previous value

```javascript
function usePrevious(value) {
    const ref = useRef();
    useEffect(() => { ref.current = value; });
    return ref.current;  // returns the value from the previous render
}
```

## `useMemo`

`useMemo` memoizes the result of an expensive computation — it only recomputes when its dependencies change.

```javascript
import { useMemo } from 'react';

function ProductList({ products, filter }) {
    const filtered = useMemo(
        () => products.filter(p => p.category === filter),
        [products, filter]  // only recompute when these change
    );

    return filtered.map(p => <ProductCard key={p.id} product={p} />);
}
```

**Don't overuse it.** `useMemo` has overhead — storing the cached value and comparing dependencies on every render. Only reach for it when you've profiled and confirmed a computation is actually slow. Filtering a 20-item array doesn't need `useMemo`.

## `useCallback`

`useCallback` memoizes a function reference — it returns the same function instance between renders unless dependencies change. This matters when passing callbacks to memoized child components.

```javascript
import { useCallback } from 'react';

function Parent() {
    const [count, setCount] = useState(0);

    // Without useCallback, this creates a new function on every render
    // — breaking React.memo on ExpensiveChild
    const handleClick = useCallback(() => {
        setCount(c => c + 1);
    }, []);  // empty deps: function never changes

    return <ExpensiveChild onClick={handleClick} />;
}

const ExpensiveChild = React.memo(({ onClick }) => {
    console.log('rendered');
    return <button onClick={onClick}>Click</button>;
});
```

`useCallback(fn, deps)` is equivalent to `useMemo(() => fn, deps)`.

## `useContext`

`useContext` reads a React context value — useful for sharing state like theme, auth, or locale without prop drilling.

```javascript
import { createContext, useContext, useState } from 'react';

const ThemeContext = createContext('light');

// Provide the context high in the tree
function App() {
    const [theme, setTheme] = useState('light');

    return (
        <ThemeContext.Provider value={theme}>
            <Page />
        </ThemeContext.Provider>
    );
}

// Consume anywhere in the tree without prop drilling
function Button() {
    const theme = useContext(ThemeContext);
    return <button className={`btn-${theme}`}>Click</button>;
}
```

## `useReducer`

`useReducer` is `useState` for complex state — when the next state depends on the previous state through multiple operations, or when state transitions have named actions.

```javascript
import { useReducer } from 'react';

function reducer(state, action) {
    switch (action.type) {
        case 'increment': return { count: state.count + 1 };
        case 'decrement': return { count: state.count - 1 };
        case 'reset':     return { count: 0 };
        default: throw new Error('Unknown action');
    }
}

function Counter() {
    const [state, dispatch] = useReducer(reducer, { count: 0 });

    return (
        <>
            <p>Count: {state.count}</p>
            <button onClick={() => dispatch({ type: 'increment' })}>+</button>
            <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
            <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
        </>
    );
}
```

## Custom Hooks

Custom hooks are functions that start with `use` and call other hooks. They're the primary way to extract and reuse stateful logic.

```javascript
function useFetch(url) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;
        setLoading(true);

        fetch(url)
            .then(r => r.json())
            .then(d => { if (!cancelled) { setData(d); setLoading(false); } })
            .catch(e => { if (!cancelled) { setError(e); setLoading(false); } });

        return () => { cancelled = true; };
    }, [url]);

    return { data, loading, error };
}

// Usage
function UserProfile({ id }) {
    const { data: user, loading, error } = useFetch(`/api/users/${id}`);

    if (loading) return <Spinner />;
    if (error)   return <Error message={error.message} />;
    return <div>{user.name}</div>;
}
```

## Hook Rules

Two rules that React enforces:

1. **Only call hooks at the top level** — never inside conditionals, loops, or nested functions. React relies on call order to associate state with the right hook.
2. **Only call hooks from React function components or custom hooks** — not regular JavaScript functions.

```javascript
// Wrong — conditional hook call
function Component({ condition }) {
    if (condition) {
        const [val, setVal] = useState(0);  // breaks rules
    }
}

// Right — condition inside the hook's effect
function Component({ condition }) {
    const [val, setVal] = useState(0);
    useEffect(() => {
        if (condition) { /* do something */ }
    }, [condition]);
}
```

## Conclusion

The hooks you'll use every day are `useState` for local state, `useEffect` for side effects with proper cleanup, and `useRef` for DOM access and mutable values that don't trigger renders. `useMemo` and `useCallback` are optimization tools — reach for them after profiling, not preemptively. Custom hooks are the right abstraction layer for shared stateful logic, keeping components readable and logic testable.
