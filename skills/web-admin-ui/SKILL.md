---
name: web-admin-ui
description: Use when driving a web admin UI or admin SPA to find, set, or verify a setting - mapping the real capability set from routes and source, driving settings through models, and verifying state where the human looks.
license: MIT
metadata:
  audience: agents
  workflow: verification
  category: web
  technologies: browser-automation, admin-interfaces, spa
---

# Web admin UI mapping

The menu is a VIEW, not the capability list: firmware hides routes
the backend still serves, and a menu-driven inventory misses them.

## Map first, click second

- Enumerate the route registry from the console namespace, not from
  the menu: the router table lists every view the build ships.
- Fetch the view HTML and the module source and grep both for the
  setting's name; a setting absent from source is absent from the
  firmware, while a setting absent from the menu may still work.
- Bind the widget to its model instance, and the model to its RPC
  data block: the chain names the exact call that changes state.

## Drive and verify

- Drive settings through the model, with the server ACK as the dirty
  flag: a UI toggle without an ACK changed pixels, not state.
- Verify where the human looks: the live widget DOM plus a
  screenshot in context. A model reload is not a persistence check;
  re-read the served state after a fresh page load.
- Hidden-route negatives are unproven while routes stay intact: a
  hidden menu entry does not prove removal.
- An eyewitness observation (the widget really shows the value)
  outranks a negative dump from a route scan.
- An eval one-expression timeout is a lost value: stash long-lived
  objects on `window` before the long call.
- Bare thenables need `Promise.resolve()` before `await`-chaining
  with other promises, or the chain throws.

## Reporting

Distinguish hidden-in-this-mode from removed-in-this-firmware: the
first is a menu problem, the second a capability change, and the
report that merges them sends the reader to fix the wrong layer.
