# AGENT GUIDELINES

## Philosophy

The primary objective is to produce software that is:

- Simple
- Maintainable
- Modular
- Secure
- Efficient
- High quality

Always favor simplicity over complexity. Every decision should prioritize long-term maintainability instead of short-term convenience.

> "The best code is code that doesn't need to exist."

---

# Core Development Principles

## Simplicity First

- Always implement the simplest solution that fully solves the problem.
- Avoid unnecessary abstractions.
- Prefer readable code over clever code.
- Keep functions short and focused.
- Avoid premature optimization unless performance is a proven bottleneck.

---

## Clean Code

Code should be:

- Clear
- Concise
- Self-explanatory
- Consistent

Avoid:

- Dead code
- Redundant logic
- Excessive nesting
- Unused variables
- Magic numbers
- Duplicate implementations

If functionality already exists, reuse it.

---

## Don't Repeat Yourself (DRY)

Never duplicate:

- Functions
- Components
- Business logic
- Utility methods

Instead:

- Refactor common logic
- Create reusable modules
- Centralize shared functionality

---

## Separation of Concerns

Maintain clear responsibilities.

Each module should have one primary responsibility.

Avoid:

- God classes
- Massive utility files
- Excessive fragmentation

Balance modularity with practicality.

---

## Component-Based Architecture

Design everything to be reusable whenever appropriate.

Examples:

- Components
- Services
- Utilities
- Hooks
- Middleware
- Models

Every feature should be easily maintainable and replaceable.

---

# Architecture

## MVC

Follow the MVC architecture whenever applicable.

- Models → Data
- Views → Presentation
- Controllers → Business Logic

Never mix responsibilities.

---

## Centralization

Common functionality should exist in one location.

Examples:

- Utility functions
- API helpers
- Constants
- Theme configuration
- Validation
- Configuration files

Avoid scattered duplicate implementations.

---

## Modularity

Features should be:

- Independent
- Reusable
- Loosely coupled

Changing one module should have minimal impact on others.

---

# Performance

Performance takes priority over unnecessary visual effects.

Prioritize:

- Efficient algorithms
- Reduced bundle size
- Minimal dependencies
- Fast loading
- Efficient rendering
- Memory efficiency

Avoid expensive operations unless necessary.

---

# Security

Always follow security best practices.

Examples include:

- Validate all user input.
- Sanitize outputs where applicable.
- Never expose secrets or credentials.
- Use environment variables for sensitive configuration.
- Apply the principle of least privilege.
- Prevent common vulnerabilities (XSS, CSRF, SQL Injection, etc.).
- Prefer secure defaults.

Never sacrifice security for convenience.

---

# Bug Fixing

When fixing bugs:

1. Identify the root cause.
2. Limit the scope of changes.
3. Avoid unnecessary refactoring.
4. Preserve existing functionality.
5. Verify affected features after the fix.

Do not rewrite unrelated code.

---

# Dependencies

Minimize dependencies.

Before adding a package:

1. Can it be solved with native language features?
2. Can existing project utilities solve it?
3. Is the dependency actively maintained?
4. Is it truly necessary?

Only introduce new libraries when they provide significant value.

---

# Frontend Guidelines

## Design Philosophy

Design should be:

- Minimal
- Functional
- Consistent

Prefer:

- Solid colors
- Clean spacing
- Clear typography
- Simple layouts

Avoid unnecessary:

- Gradients
- Heavy animations
- Decorative effects
- Visual clutter

Functionality comes before aesthetics.

---

## Styling

Do not scatter styling throughout the codebase.

Prefer:

- Centralized theme configuration
- Shared Tailwind utilities
- Reusable style components

Avoid excessive inline styling unless required.

---

# Code Organization

Organize projects with logical folder structures.

Prefer grouping by feature rather than file type when appropriate.

Example:

```
src/
    components/
    pages/
    services/
    controllers/
    models/
    utils/
    hooks/
    constants/
    assets/
```

---

# Naming

Use meaningful names.

Variables should describe data.

Functions should describe actions.

Components should describe purpose.

Avoid abbreviations unless universally understood.

---

# Documentation

Document:

- Complex algorithms
- Public APIs
- Non-obvious decisions

Do not document obvious code.

The code itself should remain readable.

---

# Error Handling

Never silently ignore errors.

- Fail gracefully.
- Return meaningful messages.
- Log useful debugging information.
- Avoid exposing sensitive internal details.

---

# Testing Mindset

Whenever making changes:

- Consider edge cases.
- Consider invalid inputs.
- Preserve backward compatibility.
- Ensure existing functionality continues to work.

---

# Decision Hierarchy

When making engineering decisions, prioritize in this order:

1. Correctness
2. Security
3. Simplicity
4. Maintainability
5. Performance
6. Reusability
7. Scalability
8. Developer convenience

---

# Additional Engineering Principles

## Architecture

Adopt the architectural pattern that best fits the chosen framework while maintaining a clear separation of concerns.

- Separate presentation, business logic, and data access whenever practical.
- Design modules with a single, well-defined responsibility.
- Favor high cohesion and low coupling.
- Build systems that are easy to extend without modifying unrelated components.

---

## Business Logic

Business rules should be centralized and independent of presentation.

Avoid placing business logic inside:
- Views
- Controllers
- Routes
- Templates
- UI Components

Presentation layers should primarily:
- Receive input
- Validate input
- Delegate work to the appropriate business layer
- Return responses

---

## Database Design

Design databases with data integrity as the highest priority.

- Normalize data unless denormalization provides measurable benefits.
- Define proper relationships and constraints.
- Avoid duplicated or inconsistent data.
- Use transactions for operations involving multiple related records.
- Preserve historical and financial records whenever possible.

---

## Configuration

Configuration should never be scattered throughout the codebase.

Centralize:
- Environment variables
- Application settings
- Constants
- Feature flags

Avoid hardcoded values unless they are true constants.

---

## Logging

Logging should assist debugging and auditing without exposing sensitive information.

Log:
- Errors
- Warnings
- Significant business events

Never log:
- Passwords
- Authentication tokens
- Secrets
- Sensitive personal information

---

## Critical Operations

Operations involving financial, medical, legal, or security-sensitive data should prioritize:

1. Correctness
2. Data Integrity
3. Auditability
4. Traceability

Prefer immutable history over destructive modifications whenever practical.

---

## Version Control

Each commit should represent one logical change.

Avoid:
- Mixing unrelated features
- Large unreviewable commits
- Temporary debugging code

Write clear commit messages that explain the purpose of the change.

---

## Testing Philosophy

Prioritize testing:

- Business rules
- Edge cases
- Input validation
- Security-sensitive functionality

Test behavior rather than implementation details.

---

## Documentation

Code should explain *how* the system works.

Documentation should explain:
- Why a decision was made
- Design constraints
- Architectural decisions
- Assumptions

Avoid documenting obvious code.

---

## Engineering Principle

When multiple valid implementations exist, choose the one that:

- Is easiest to understand
- Is easiest to maintain
- Introduces the least unnecessary complexity
- Solves the problem correctly

Avoid clever solutions when a straightforward solution achieves the same result.

# General Rules

- Keep implementations as small as reasonably possible.
- Build reusable solutions.
- Avoid unnecessary complexity.
- Avoid overengineering.
- Favor composition over inheritance when appropriate.
- Write code that another developer can understand immediately.
- Every line of code should provide clear value.
- If a feature or abstraction is not needed today, avoid adding it.
- Make incremental, targeted changes rather than broad rewrites.
- Consistency across the codebase is more valuable than personal preference.

