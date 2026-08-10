# Reference and Goal Resolution

Velvet Language treats conversational references and goals as bounded working state, not intuition and not canonical memory.

## Reference Resolution

References such as `it`, `that`, `that one`, `the other module`, or `the engine one` must resolve only against caller-supplied candidates from trusted current context.

The resolver may use:

- semantic match
- recency
- conversational role
- active subject context

It must not invent a referent.

If the best candidate is weak or too close to another plausible candidate, Velvet should ask for clarification instead of silently choosing.

## Goal Lifecycle

Conversation goals may be:

- `active`
- `blocked`
- `satisfied`
- `abandoned`

A goal may declare required information slots. Resolving those slots can satisfy the goal. Slotless goals may be explicitly completed when the requested communicative task is done.

Blocked is not complete. Abandoned is not complete.

## Boundary

Reference and goal state are ephemeral language-working state. They do not:

- become canonical memory automatically
- grant authority
- prove identity
- authorize action
- alter Runtime state
- bypass Core learning or memory admission

Long-lived retention must pass through the existing governed memory and continuity paths.
