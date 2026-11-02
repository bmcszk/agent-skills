---
name: go-htmx-frontend
description: Use when building or reviewing Go server-rendered web UIs with Templ components, HTMX 2.x, Tailwind CSS v4 (standalone CLI, no Node.js), or Alpine.js. Covers Templ syntax and composition, HTMX partials and loading states, HTTP handlers that return HTML, forms with validation and CSRF, streaming, component and handler tests, and the build and deployment setup. Test layout and levels are in go-tests; real-browser tests are in go-browser-tests.
license: MIT
metadata:
  audience: developers
  workflow: development
  category: frontend
  technologies: go, htmx, templ, tailwind, alpinejs
---

# Go HTMX frontend

Build web UIs with Go using Templ, HTMX 2.x, Tailwind CSS v4 (standalone CLI), and Alpine.js only when a page needs client state.

Before you add a layer, a component library, or JavaScript, read [../go-dev/references/development-balance.md](../go-dev/references/development-balance.md). Match the existing structure of the project first.

## References

Read only the file the task needs. Do not load all of them for a small edit.

| Read | When |
|------|------|
| [references/templ.md](references/templ.md) | Installing Templ, writing components, layouts, children, loops, conditionals, or conditional classes |
| [references/htmx.md](references/htmx.md) | Installing HTMX or Alpine.js, writing `hx-*` attributes, partial updates, loading indicators, or `hx-on` events |
| [references/handlers.md](references/handlers.md) | Writing a handler that renders a component, serving full pages and HTMX partials from one route, request-scoped context, or streaming |
| [references/forms.md](references/forms.md) | Building a form, validation, form decoding, or CSRF protection |
| [references/tailwind.md](references/tailwind.md) | Installing the Tailwind standalone CLI, `@source` and `@theme` config, or build commands |
| [references/deployment.md](references/deployment.md) | The `justfile`, dev hot reload, the production build, or CI |
| [references/testing.md](references/testing.md) | Testing components, handlers, HTMX partials, or CSRF-protected forms |

## Official documentation

- https://templ.guide/
- https://templ.guide/server-side-rendering/htmx/
- https://templ.guide/syntax-and-usage/template-composition/
- https://templ.guide/syntax-and-usage/forms/
- https://htmx.org/docs/
- https://tailwindcss.com/blog/tailwindcss-v4
- https://templui.io/ (component library)

## Rules

1. Render HTML on the server. Use Alpine.js only for client state.
2. Use the Tailwind standalone CLI. Do not add npm, `package.json`, or `tailwind.config.js`. Tailwind v4 configures in CSS with `@theme`.
3. Pass request data (CSRF token, user, theme) from the handler into the component as parameters. Do not read security values from `ctx.Value`.
4. Check every `Render` error and log it. Never send an internal error text to the client.
5. Keep components small and explicit. Add an abstraction only when it removes duplication that exists now.
6. The pages work without JavaScript when the form has a real `action` and `method`. HTMX then upgrades it.
