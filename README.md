# agent-skills

Home-made agent skills ([SKILL.md spec](https://agentskills.io/specification)), shared across machines via the [`skills` CLI](https://skills.sh).

Install all:

```bash
npx skills add bmcszk/agent-skills --skill '*' -g
```

Install one:

```bash
npx skills add bmcszk/agent-skills --skill beans -g
```

Managed declaratively by [bmcszk/pot](https://github.com/bmcszk/pot) (chezmoi) via `~/.agents/.skill-lock.json`.
