---
layout: post
title: "Dependency Injection Without a Framework"
date: "2026-09-02 00:00:00 +0530"
slug: dependency-injection-without-framework
description: "How to apply dependency injection in Python without a DI framework, using plain constructor injection to make code testable and swap implementations easily."
categories: ["wiki", "Programming"]
tags: ["dependency injection", "inversion of control", "python", "design patterns", "testing", "decoupling", "backend", "architecture"]
---

Dependency injection has a reputation for being a heavyweight, framework-driven concept — Spring's `@Autowired`, elaborate container configuration, XML wiring files from an earlier era of Java. That reputation is mostly earned by the frameworks, not the idea itself, which is genuinely simple: instead of a class constructing the things it depends on, those dependencies get handed to it from the outside. No framework, no container, no magic — just passing arguments to a constructor, and the testability and flexibility benefits show up immediately. This post covers how to do exactly that in plain code, and where a container-based framework eventually earns its keep.

## The Problem: Hardcoded Dependencies

A class that constructs its own dependencies internally looks innocuous at first:

```python
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase(connection_string="postgres://...")
        self.email_client = SendgridClient(api_key="...")
        self.payment_gateway = StripeGateway(api_key="...")

    def place_order(self, order):
        self.db.save(order)
        self.payment_gateway.charge(order.total, order.card)
        self.email_client.send(order.customer_email, "Order confirmed")
```

The problem surfaces the moment you try to test it. `place_order` can't be unit tested without a real Postgres connection, a real Stripe API key, and a real Sendgrid account — because `OrderService` has hardcoded exactly which concrete implementation of each dependency it uses, deep inside its own constructor, with no way to substitute a fake or a mock from outside.

## The Fix: Constructor Injection

Instead of constructing dependencies internally, accept them as constructor arguments:

```python
class OrderService:
    def __init__(self, db, email_client, payment_gateway):
        self.db = db
        self.email_client = email_client
        self.payment_gateway = payment_gateway

    def place_order(self, order):
        self.db.save(order)
        self.payment_gateway.charge(order.total, order.card)
        self.email_client.send(order.customer_email, "Order confirmed")
```

```python
# Production wiring — happens once, at application startup
order_service = OrderService(
    db=PostgresDatabase(connection_string="postgres://..."),
    email_client=SendgridClient(api_key="..."),
    payment_gateway=StripeGateway(api_key="..."),
)
```

```python
# Test wiring — completely different implementations, same class
def test_place_order_charges_correct_amount():
    fake_gateway = FakePaymentGateway()
    order_service = OrderService(
        db=InMemoryDatabase(),
        email_client=NoOpEmailClient(),
        payment_gateway=fake_gateway,
    )
    order_service.place_order(sample_order)
    assert fake_gateway.charged_amount == sample_order.total
```

`OrderService` itself hasn't changed at all between these two examples — the only difference is what gets passed to its constructor. This is the entire mechanism. No framework, no annotations, no container — just moving object construction from inside the class to outside it, at the point where the application is assembled.

## Why This Is Called "Inversion of Control"

The name sounds more abstract than the mechanism actually is. In the original version, `OrderService` controls which concrete `PaymentGateway` implementation it uses — it decides, internally, "I will use Stripe." In the injected version, that control is inverted: something *external* to `OrderService` decides which implementation it gets, and `OrderService` just declares "I need *something* that can charge a payment" without caring what it actually is.

```python
class PaymentGateway(Protocol):
    def charge(self, amount: int, card: str) -> bool: ...
```

Using a `Protocol` (Python's structural typing interface) or an abstract base class to express this dependency makes the inversion explicit in the type system: `OrderService` depends on the *shape* of a payment gateway, not any specific one, and anything satisfying that shape — Stripe, a test fake, a future PayPal implementation — can be substituted freely without `OrderService` itself changing at all.

## Composition Root: Where Wiring Actually Happens

Once multiple classes need dependencies injected, the natural next question is: where does all this construction actually happen? The answer is a single, deliberate place — often called the **composition root** — typically near the application's entry point, where every concrete object gets constructed and wired together exactly once.

```python
def build_application():
    db = PostgresDatabase(connection_string=config.DB_URL)
    email_client = SendgridClient(api_key=config.SENDGRID_KEY)
    payment_gateway = StripeGateway(api_key=config.STRIPE_KEY)

    order_service = OrderService(db, email_client, payment_gateway)
    inventory_service = InventoryService(db)
    notification_service = NotificationService(email_client)

    return App(order_service, inventory_service, notification_service)

app = build_application()
app.run()
```

This centralization matters more than it looks: every other class in the codebase can now be written and tested in complete isolation, without knowing anything about how the concrete production dependencies get constructed — that knowledge lives in exactly one place, the composition root, instead of being smeared across every class that happens to need a database connection.

## When a DI Framework Actually Earns Its Keep

Plain constructor injection scales further than most people expect — a codebase with dozens of services and a composition root that's a few hundred lines of explicit wiring is still perfectly manageable, and arguably more readable than the equivalent framework-managed configuration, since every dependency relationship is visible as plain code rather than inferred from annotations.

A DI framework (Spring, Guice, `punq`/`dependency-injector` in Python) starts earning its complexity when:

- **The dependency graph gets deep and highly reused.** If `Logger` needs to be injected into 40 different classes, manually threading it through 40 constructor calls in the composition root becomes real, repetitive toil that a framework's automatic resolution genuinely eliminates.
- **Dependencies need request-scoped or conditional lifetimes.** A framework's container can manage "one instance per HTTP request" or "singleton across the app" lifecycle rules declaratively — implementing this correctly by hand is exactly the kind of subtle, easy-to-get-wrong plumbing a mature framework has already solved.
- **Configuration-driven wiring is a real requirement** — swapping an entire implementation based on environment config (a different payment gateway per deployment environment, selected by a config flag rather than hardcoded in the composition root) is something frameworks handle declaratively that hand-rolled wiring makes more awkward.

## The Trade-off Worth Understanding

Manual constructor injection has one real cost: the composition root grows linearly with the size of the dependency graph, and very large applications can end up with sprawling wiring code that's tedious, if not actually complex, to maintain.

A DI framework's cost is the opposite kind: **the actual object graph becomes implicit**, discoverable only by running the application (or reading framework-specific annotations scattered across many files) rather than by reading one composition root top to bottom. This is a real, if often underweighted, cost — "where does this `PaymentGateway` instance actually come from" becomes a harder question to answer by reading code alone once a framework's automatic resolution is doing the wiring, versus a manual composition root where the answer is always "line 14 of `build_application()`."

## Conclusion

Dependency injection's core value — testability, and the ability to swap implementations without touching consuming code — comes entirely from the pattern of passing dependencies in rather than constructing them internally, and that pattern needs zero framework support to work. Plain constructor injection plus one explicit composition root scales further than its reputation suggests, and stays more legible than a framework-managed alternative for a meaningful range of application sizes. Reach for a framework once the dependency graph is genuinely large, deeply reused, or needs lifecycle/scoping rules that hand-written wiring makes tedious to get right — not by default, and not because "professional" codebases are assumed to need one.
