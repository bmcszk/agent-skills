---
name: grilling
description: >-
  Interview the user relentlessly about a plan, decision, or idea until a
  shared understanding exists. Use when stress-testing a plan or decision
  before committing to a design that has not survived questioning.
license: MIT
metadata:
  audience: agents
  workflow: planning
  category: meta
  technologies: requirements, design
---

# Grilling

Map the topic as a design tree: every decision branches into the
decisions that hang off it. Work the tree in rounds and never act on
the plan until the user confirms the shared understanding is real.

## Rounds

1. Compute the frontier: every decision whose prerequisites are
   already settled. A question whose answer depends on another open
   question belongs to a later round.
2. Ask the whole frontier in one round. Number each question and give
   your recommended answer. Word the question so "yes" accepts the
   recommendation.
3. Wait for the answers. Each round reshapes the tree: settled
   decisions push the frontier outward and unblock the questions
   behind them. Recompute and repeat.
4. The session is done when the frontier is empty: every branch
   visited, nothing left silently assumed.

## Facts and decisions

Finding facts is your job, never the user's. When a frontier question
needs a fact from the environment (filesystem, tools, docs), research
it yourself or dispatch a subagent to find it. Do not block the round
on it: a running search is an unsettled prerequisite, so only the
questions downstream of it wait. Ask the rest of the frontier now.

The decisions are the user's. Put each one to them and wait for the
answer; never answer your own question by picking the recommendation
and moving on.

## Exit

State the settled design in one short summary and ask the user to
confirm. Act only after the confirmation.
