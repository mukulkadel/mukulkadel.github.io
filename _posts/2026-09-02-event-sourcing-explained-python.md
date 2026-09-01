---
layout: post
title: "Event Sourcing Explained with a Practical Python Example"
date: "2026-09-02 00:00:00 +0530"
slug: event-sourcing-explained-python
description: "A practical introduction to event sourcing with a working Python example, covering append-only event logs, state reconstruction, and snapshotting."
categories: ["wiki", "Programming"]
tags: ["event sourcing", "events", "python", "backend", "architecture", "audit log", "state", "database", "design patterns"]
---

Most applications store current state and overwrite it as things change — an account's balance is a single number in a row, updated in place with every transaction, and the history of how it got there is gone unless you separately logged it. Event sourcing inverts this: instead of storing current state, you store the complete sequence of events that led to it, and current state becomes something you *compute* by replaying that sequence, not something you store directly. This post walks through the idea with a working Python example, and covers where it genuinely pays off versus where it's needless complexity.

## The Core Idea

In a traditional model, an operation like "withdraw $50" directly mutates a stored balance:

```python
account.balance -= 50
save(account)
```

The database now reflects the current balance — but nothing about *how* it got there. If a bug caused an incorrect withdrawal three days ago, there's no record to inspect; the balance is just wrong, with no trail explaining why.

Event sourcing stores the withdrawal itself as an immutable fact, and the balance becomes a value derived by replaying every event from the beginning:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class MoneyDeposited:
    account_id: str
    amount: int
    occurred_at: datetime

@dataclass(frozen=True)
class MoneyWithdrawn:
    account_id: str
    amount: int
    occurred_at: datetime
```

```python
events = [
    MoneyDeposited("acc_1", 200, datetime(2026, 1, 1)),
    MoneyWithdrawn("acc_1", 50, datetime(2026, 1, 3)),
    MoneyDeposited("acc_1", 100, datetime(2026, 1, 5)),
]

def current_balance(events):
    balance = 0
    for event in events:
        if isinstance(event, MoneyDeposited):
            balance += event.amount
        elif isinstance(event, MoneyWithdrawn):
            balance -= event.amount
    return balance

current_balance(events)  # 250
```

Nothing here directly stores "the balance is 250" — it's derived, on demand, by folding over the full event history. This is the entire conceptual core of event sourcing: **the event log is the source of truth; current state is a projection of it, always reconstructible, never itself the primary stored fact.**

## A Working Example: An Account Aggregate

A more complete implementation wraps this in an **aggregate** — an object that both enforces business rules on new events and knows how to rebuild its own state from history:

```python
class InsufficientFundsError(Exception):
    pass

class Account:
    def __init__(self, account_id):
        self.account_id = account_id
        self.balance = 0
        self.uncommitted_events = []

    @classmethod
    def from_history(cls, account_id, events):
        account = cls(account_id)
        for event in events:
            account._apply(event)
        return account

    def deposit(self, amount, occurred_at):
        event = MoneyDeposited(self.account_id, amount, occurred_at)
        self._apply(event)
        self.uncommitted_events.append(event)

    def withdraw(self, amount, occurred_at):
        if amount > self.balance:
            raise InsufficientFundsError(f"balance {self.balance} < {amount}")
        event = MoneyWithdrawn(self.account_id, amount, occurred_at)
        self._apply(event)
        self.uncommitted_events.append(event)

    def _apply(self, event):
        if isinstance(event, MoneyDeposited):
            self.balance += event.amount
        elif isinstance(event, MoneyWithdrawn):
            self.balance -= event.amount
```

```python
account = Account.from_history("acc_1", events)
account.balance  # 250

account.withdraw(300, datetime.now())
# InsufficientFundsError: balance 250 < 300
```

The validation (`InsufficientFundsError`) happens *before* an event is created — an event, once created, represents a fact that already happened and is never itself invalid. This is a deliberate and important distinction from a command: `withdraw(300, ...)` is a request that can be rejected; `MoneyWithdrawn(amount=300, ...)` would be a historical fact that, if it existed, would need to be treated as having genuinely occurred.

## Persisting and Replaying Events

The event store itself is conceptually simple — an append-only log, keyed by aggregate ID:

```python
class InMemoryEventStore:
    def __init__(self):
        self._streams = {}

    def append(self, account_id, events):
        self._streams.setdefault(account_id, []).extend(events)

    def load(self, account_id):
        return self._streams.get(account_id, [])
```

```python
store = InMemoryEventStore()

account = Account("acc_1")
account.deposit(200, datetime(2026, 1, 1))
account.withdraw(50, datetime(2026, 1, 3))
store.append("acc_1", account.uncommitted_events)

# Later, in a different process entirely:
reloaded_events = store.load("acc_1")
reloaded_account = Account.from_history("acc_1", reloaded_events)
reloaded_account.balance  # 150
```

A production event store (EventStoreDB, or a table in a regular database with an `event_type`, `payload`, `stream_id`, and `sequence_number` column) works the same way conceptually — append new events to a stream, load a stream to reconstruct current state — with the real infrastructure additionally providing durability, concurrency control on appends (preventing two concurrent writers from both appending event #5 to the same stream), and often built-in subscription mechanisms for other services to react to new events as they're appended.

## Snapshotting: Solving the Replay-Cost Problem

Replaying every event from the beginning of time works fine for an account with a dozen transactions. It becomes a real performance problem for an aggregate with hundreds of thousands of events — reconstructing current state on every read by replaying the entire history is wasteful when most of that history hasn't mattered to the current state's shape in a long time.

**Snapshotting** solves this by periodically persisting the *computed* current state alongside a marker of how far the event log had progressed at that point, so future reconstructions only need to replay events *since* the snapshot:

```python
@dataclass
class Snapshot:
    account_id: str
    balance: int
    event_count: int

def load_with_snapshot(store, snapshots, account_id):
    snapshot = snapshots.get(account_id)
    if snapshot:
        account = Account(account_id)
        account.balance = snapshot.balance
        all_events = store.load(account_id)
        new_events = all_events[snapshot.event_count:]
    else:
        account = Account(account_id)
        new_events = store.load(account_id)

    for event in new_events:
        account._apply(event)
    return account
```

Snapshots are purely a performance optimization — they're derived, disposable, and always reconstructible from the event log alone. Deleting every snapshot and rebuilding them from scratch by replaying the full event history should always produce identical results; if it doesn't, that's a sign the snapshotting logic has a bug, not that the snapshot itself was ever a genuine second source of truth.

## The Real Benefits

**A genuine, complete audit trail.** Every change is a permanently recorded fact with a timestamp — not bolted on as a separate audit-logging concern, but the primary storage mechanism itself. For domains with real compliance or dispute-resolution requirements (financial transactions, healthcare records), this is often the actual reason event sourcing gets chosen.

**Temporal queries — "what did this look like at time T."** Because state is a fold over events up to some point, reconstructing state *as of* any past moment is just replaying events up to that moment instead of all of them — a query that's genuinely difficult to answer from a traditional mutate-in-place model without separately maintained history tables.

**Natural fit for event-driven and CQRS architectures.** An event-sourced write model produces, as its natural byproduct, exactly the stream of events a [[cqrs]] read-model projector needs to consume — the two patterns pair unusually well because one produces precisely what the other needs.

## The Real Costs

**Query complexity for anything beyond the current-state view.** "Show me every account with a balance over $10,000" is a trivial query against a traditional balance column; against pure event-sourced storage, it requires either maintaining a separate queryable projection (which is, in effect, CQRS) or replaying every account's full history on every such query, which doesn't scale.

**Schema evolution is genuinely harder.** Old events, recorded years ago in an old shape, need to remain replayable forever — you can't retroactively "migrate" historical events the way you'd run a database migration on a mutable table, since the events themselves are the permanent historical record. Handling this usually means versioned event types and upcasting logic that translates old event shapes into new ones at replay time, which is real ongoing engineering overhead.

**It's a genuinely unfamiliar mental model for most teams.** Debugging "why is this aggregate's state wrong" means reasoning about a sequence of events and a fold function, not inspecting one row — a real cost for team onboarding and day-to-day debugging that's easy to underestimate before adopting the pattern.

## Conclusion

Event sourcing's core trade is storing the complete history of *what happened* instead of just the current result, in exchange for genuine audit trails, natural temporal queries, and a clean fit with event-driven architectures — at the cost of harder ad-hoc querying (usually requiring a separate projection layer) and real ongoing complexity in evolving event schemas over time. It's a strong fit for domains where the history itself has business value — financial ledgers, compliance-heavy systems, anything where "what happened and when" matters as much as "what's true now" — and a poor fit for a straightforward CRUD application where nobody has ever actually needed to answer "what did this look like last Tuesday."
