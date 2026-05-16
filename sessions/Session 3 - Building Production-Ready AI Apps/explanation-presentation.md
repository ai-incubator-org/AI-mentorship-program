


















# Building Production-Ready AI Apps
## Architecture Patterns


May 2026 — adoption is huge.    May 2026 — trust is low.
─────────────────────────       ─────────────────────────
Airbnb:   60% AI-written        96% of devs don't fully
Anthropic: 59% daily eng        trust AI-generated code



Stripe:   1,000+ PRs/week       Only 48% always verify it
          unattended            before committing




Google:   75% AI-generated      Trust dropped 40% → 29%
                                in a single year


84% adopt. 29% trust. That is THE gap.



It has a name: a TRUST gap.

Today is about closing it.

Not by trusting MORE.
By building systems that make trust EARNABLE.




















## Two completely different things

AI IN product   = building products powered by AI
                  → chatbots, RAG, agents-as-features


AI FOR SDLC     = using AI agents as YOUR dev workflow
                  → planning, coding, reviewing, shipping



These need completely different architectures.
Today is entirely about the second.



## So what are we really doing today?

  We are designing the architecture that lets an engineer
  TRUST what an agent ships.


  harness - runtime environment - Claude code


  The "harness" IS that architecture.

  Every primitive we teach today is a trust mechanism.
  Every verification layer is a trust step.
  Every failure mode we name is a trust failure.

  Trust is the through-line.




















# Part 1 — Foundations

## What an LLM is (60-second mental model)


An LLM is a statistical model.


Given a sequence of tokens, it outputs a probability distribution
over the next token.



hi - hello, how are you?

message: "hi", from: "user" - hello, how are you?


The runtime samples one. Appends it to the sequence.
Runs the whole thing through the network again.
Repeats.



That's how it "writes."
Sampling in a loop. No magic.



## facts to burn in

The model is STATELESS between API calls.
   Every call is a fresh forward pass over whatever tokens you send.
   There is NO hidden memory inside the model.


## Where the "memory" actually comes from

The context window — system prompt, conversation, files, tool outputs —
is the model's ENTIRE working memory.


When ChatGPT seems to "remember" what you said earlier,
your client is replaying the transcript back into the context window.
Every. Single. Turn.


## And the first trust implication

The model has no continuity. It has not "earned" your trust by
working well yesterday — it is a new agent every call.

So trust has to be designed in, every turn.
That is what context engineering, and ultimately the harness, do.




















## What makes an LLM an agent

  An agent is an LLM running in a LOOP, given TOOLS to act with.

The loop:

  ┌──────────────────────────────────────────┐
  │  1. Read context                         │
  │  2. Decide next move                     │
  │  3. Call a tool                          │
  │  4. Observe result (appended to context) │
  │  5. Repeat — until "done"                │
  └──────────────────────────────────────────┘


Strip the hype: an agent is an LLM + tools + a loop.
Everything else is plumbing.



## Trust angle

  Each of these is a thing you have to TRUST:

    - the model (its training, its biases)
    - the tools (what they can touch)
    - the loop (when it stops, when it asks)
    - the context (what's in it, what's missing)

  These are your knobs. The harness is what tunes them.



claude code tool - bash, mcp, websearch.


















## Tools = the agent's hands


How the loop's "act" step actually works:

  Model emits → { "tool": "read_file", "args": {"path": "..."} }
  Runtime executes the tool
  Result appended to context as a new message
  Model sees it next turn → decides next action



Critical: what an agent can do is bounded by the tools it has.
No tool for Postgres? Can't touch your database. Period.

The tools you grant = the action space you have to trust.




















## A simple tool example

A tool DEFINITION — what the agent sees at session start:

  JSON RPC

  {
    "name": "read_file",
    "description": "Read the contents of a file",
    "input_schema": {
      "type": "object",
      "properties": {
        "path": { "type": "string" }
      },
      "required": ["path"]
    }
  }

The agent EMITS a tool call:

  { "tool": "read_file", "args": { "path": "src/index.ts" } }

The runtime EXECUTES and returns:

  "import express from 'express'..."   ← the file's contents

error case: "there is no such file"

The result is APPENDED to context as a message.
The agent sees it next turn → decides next action.

That's the whole shape. Every tool — Bash, Read, Write, Grep,
MCP servers — looks like this.




















## The integration problem (why MCP exists)

Before late 2024, every agent CLI shipped its own custom tool format:

   5 agent CLIs × 50 services
   = 250 bespoke integrations
   = every team rewriting the same Postgres glue for the 100th time

The same N×M mess editors had with language servers
before LSP. (VS Code, Vim, Emacs × Python, Rust, Go, ...)

LSP solved it for editors.
MCP solves it for agents.




















## MCP — Model Context Protocol — what it is

  An MCP server exposes capabilities to any MCP-speaking agent.
  An MCP client is your agent CLI.
  They speak a standard wire protocol.

Each server exposes THREE primitives:

  ┌─────────────┬───────────────────────────────────────┐
  │  tools      │  actions the agent can take          │
  │  resources  │  data the agent can read             │
  │  prompts    │  templated workflows                 │
  └─────────────┴───────────────────────────────────────┘

What this gets you:

  - Write ONE MCP server   → every MCP client can use it
  - Install ONE MCP server → your agent gains those capabilities

Open Linux Foundation standard since Dec 2025.
~10,000+ public MCP servers. Native in Claude Code, ChatGPT,
Cursor, Gemini, Microsoft Copilot.



## Trust angle on MCP

  Every MCP server you install EXPANDS the agent's action space.
  Every action is something you have to trust.


  "Install everything" is a trust posture problem,
  not just a token-budget problem.


  Curate tools the same way you curate context.




















## Context = everything the model sees this turn

Anatomy of an agent's context window:

  ┌────────────────────────────────────────────────────────┐
  │  System prompt                                         │
  │  → who the agent is, how it behaves                    │
  │    Set by the agent product (not you).                 │
  │    Claude Code's runs ~10K+ tokens.                    │
  ├────────────────────────────────────────────────────────┤
  │  Tool definitions                                      │
  │  → JSON schemas + descriptions for every tool          │
  │    Loaded at session start. A typical MCP setup        │
  │    can consume 5K–50K tokens before you type a char.   │
  ├────────────────────────────────────────────────────────┤
  │  Project context files (CLAUDE.md / AGENTS.md / skills)│
  │  → "what I always need to know about this codebase"    │
  │    Loaded every session. Keep tight (~few K tokens).   │
  ├────────────────────────────────────────────────────────┤
  │  Memory (long-term, cross-session)                     │
  │  → decisions, learnings, history from prior sessions   │
  │    File-backed; selectively loaded                     │
  ├────────────────────────────────────────────────────────┤
  │  Conversation history                                  │
  │  → the back-and-forth this session                     │
  │    Grows linearly with turns                           │
  ├────────────────────────────────────────────────────────┤
  │  Previous tool calls + results                         │
  │  → the agent's scratchpad: what it's done so far       │
  │    Biggest source of context bloat — one `read` of     │
  │    a 3000-line file dumps tens of thousands of tokens. │
  ├────────────────────────────────────────────────────────┤
  │  Current user turn                                     │
  │  → what just arrived. Only layer YOU control per req.  │
  └────────────────────────────────────────────────────────┘



  Quality of output ≤ quality of context.
  Trust in output ≤ trust in context.







model - prompt - context





my cat was sitting when I came to feed it.




"Attention is all you need" - 2017







## Why is the context window limited?
## Why do different models have different sizes?


### Reason 1 — Architecture: attention scales as n²

Transformer self-attention has every token "look at" every other
token. That's n × n = n² pairwise relationships.

  100K tokens   →  ~10 billion attention ops per layer
  1M tokens     →  ~1 trillion attention ops per layer

Double the context → quadruple the cost. Always.
Not fixable by faster GPUs — it's a property of the algorithm.



### Reason 2 — Memory: the KV cache

During generation, the model caches each prior token's keys & values
so it doesn't recompute them. The cache grows linearly with context.

  128K tokens on a Llama-70B-class model
  → ~40 GB of GPU memory PER USER, just for the cache

Long context isn't just slow — it's expensive in real $$ per call.



### Reason 3 — Training: models are trained at a max length

Models are pre-trained on sequences up to a fixed length.
Going beyond requires position-encoding tricks (YaRN, RoPE scaling).
Those tricks technically extend the window, but quality degrades:
training data has many short documents and few book-length ones,
so models simply have less practice with very long context.



### Why different models = different windows

Vendors pick different points on the cost / quality curve:

  - Smaller models (Haiku 4.5 → 200K) keep cache small for $/speed
  - Bigger models (Opus 4.7 → 1M) eat the cost for long-horizon work
  - State-space hybrids (Mamba, Jamba) escape O(n²) — different math
  - Mixture-of-experts (Llama 4 Scout → 10M) decouples cost from size


Pick window size by workload. It is NOT a free dimension.




















## Current context windows (May 2026)

Claude Opus 4.7      1M tokens
Claude Sonnet 4.6    1M tokens
Claude Haiku 4.5     200K
GPT-5.5              1M (API) / 400K (Codex)
Gemini 3.1 Pro       1M (with a cost cliff above 200K)
Grok 4.3             1M
Llama 4 Scout        10M (open weight)

But — bigger window ≠ bigger usable memory.
              ≠ more trustworthy output.

Evidence next.




















## Context is a finite resource with diminishing returns

The mental shift you have to internalize:

  Bigger window  ≠  bigger usable memory.
  More tokens    ≠  better performance.
  More context   ≠  more trustworthy output.

Models have an "attention budget."
Every token you add depletes it.



Good context engineering = the SMALLEST set of high-signal tokens
that gets the job done. Not the largest.


And: each pitfall below is a TRUST failure mode.




















## Four named failure modes — four shapes of trust failure



### 1. Lost in the middle  →  position-based trust failure
LLMs attend best to the BEGINNING and the END of context.
The middle is systematically under-used.

Even in May 2026, on frontier models, this is still measurable.
On the NoLiMa benchmark (ICML 2025), models that score near-perfect
at short context drop to 50% or worse when forced to retrieve
from the middle of 32K+ contexts.

→ Implication: put high-stakes tokens at the EDGES of context.
   Trust degrades by POSITION in the window.




### 2. Context rot  →  capacity-based trust failure
Across 18 frontier models tested in 2025, accuracy degrades
smoothly as input length grows — even on trivial tasks.

For a 1M-token-window model, noticeable degradation typically
kicks in around 300–400K tokens. Sometimes earlier.

→ Implication: design as if every token has a cost.
   Trust degrades by VOLUME of context.




### 3. Context poisoning  →  the cleanest trust failure
Once a hallucination or error enters the context, the model
cites it instead of correcting it. Errors self-amplify.

Worked example: DeepMind ran Gemini 2.5 Pro on Pokémon. The agent
hallucinated some game state — a level it wasn't actually at.
That bad state entered the running context. The agent then chased
goals that didn't exist. For hours. Built increasingly nonsensical
strategies on top of the bad premise — and DEFENDED them.

→ Implication: validate generated content BEFORE letting it
   re-enter the next turn. Once it's in, it propagates.
   The agent now TRUSTS its own hallucination.





### 4. Context drift  →  trust decay over a session
Long sessions silently lose track of original constraints.
The constraint is technically still in the window — but later
turns reweight attention away from it.

Worked example: pair-programming session. Turn 3 you said
"no new dependencies, pure standard library." Turn 30, the agent
proposes adding three libraries. The "no new deps" sentence is
still in context. It just stopped winning the attention auction.



→ Implication: re-anchor goals periodically.
   Trust DECAYS over time inside a single session.




















All four failure modes share one thing:
they erode TRUST in agent output.



The mental shift this section earns:



  From "fill the context"
  To   "CURATE the context"



  From "hope the agent gets it right"
  To   "engineer for trustworthy output"



  Doing this turn-by-turn doesn't scale.
  The discipline has a name.




















## Context engineering — the discipline


Definition: curating and maintaining the optimal set of tokens
during inference — including everything that lands in the window
outside the prompt itself.



  Named and popularized June 2025 by Karpathy and Lütke, in the
  same week. The name caught fire in days.


  Anthropic's canonical deep-dive: "Effective context engineering
  for AI agents" (September 2025).



## Context engineering DOES NOT replace prompt engineering.
## It SUBSUMES it.




  Prompt engineering = writing the prompt
  Context engineering = engineering the WHOLE window
                        (system prompt, tools, history, files,
                         retrieval, sub-agent isolation, compaction...)



## The working scaffold (LangChain, 2025)

  Four levers, four buckets:

  ┌─────────────┬─────────────────────────────────────────┐
  │  WRITE      │  Save state OUTSIDE the window          │
  │  SELECT     │  Pull the right tokens IN at runtime    │
  │  COMPRESS   │  Summarize / trim to keep window lean   │
  │  ISOLATE    │  Use sub-agents with their own windows  │
  └─────────────┴─────────────────────────────────────────┘

  offload - separate file for specific work completion.


  claude code - we are talking with

  explore - triggered by main agent and main agent provide the prompt.
  returns its results to main agent.


  Every advanced technique you'll see in this session
  falls into one of these four.



## Trust framing

  Context engineering is trust engineering at scale.
  Each lever — write, select, compress, isolate —
  is a trust mechanism.




















## What you'll actually use (May 2026)

### Mainstream paid
- Claude Code (Anthropic)        Pro $20 / Max $100 / Max20x $200
- Codex / Codex CLI (OpenAI)     Plus $20 / Pro $100 or $200
- Cursor                          Pro $20 / Ultra $200
- Windsurf (Cognition / Devin)    Pro $20 / Max $200



### Free / low-cost
- PI agent
- aider (CLI, free, bring-your-own API key)
- opencode (SST) / Crush (Charm) — free, BYO key kimik2.6
- Cline (VS Code/JetBrains extension) — free, BYO key
- OpenRouter — gateway across 400+ models. Free tier exists
               (20 req/min, 50 req/day) for trying without a card.



I'll demo in Claude Code. The patterns travel.




















## Where Part 1 lands

  An agent is an LLM + tools + a loop.
  The loop reads context, decides, acts, observes — repeats.

  The model's only working memory is context.
  Quality of output ≤ quality of context.
  TRUST in output ≤ TRUST in context.

  Curating context is its own discipline: context engineering.
  Four levers — write, select, compress, isolate.
  All four are trust mechanisms.


  claude code - first prompt, second prompt.


  Doing this turn-by-turn does NOT scale.
  Building trustworthy AI-driven dev requires a system.

  That system has a name.




















# Part 2 — The harness, and the operating principle

## The architecture of trust

  Engineer-agent trust has two problems to solve:



  - The model is stateless. Your trust isn't.
    Every call is a clean slate; you have history with this codebase.



  - You can mechanically verify some things.
    Most things, you can't.



  The harness is how engineers solve both.
  It IS the architecture of trust.





## What is a harness, precisely

  A harness is the engineered environment around an AI agent —
  the system of context files, skills, sub-agents, hooks, slash
  commands, conventions, and verification layers — that ensures
  the agent receives the right prompt and the right context at
  the right moment for every task it performs.



  The harness is NOT the agent.
  It is everything that WRAPS the agent.



  Analogy: an IDE is a developer's harness. File tree, syntax
  highlighting, debugger, test runner, lint, terminal — all
  wrap around a text editor. The agent's harness is the system
  that wraps the LLM.




















## Why this matters

  gemma 4, 31B - local run with 24GB
  qwen 3.5 9b - 6GB

  A decent model with a great harness beats a great model with a
  bad harness. Every senior practitioner who has built both will
  tell you this.


  Same model + bad harness  =  Top 30 on Terminal Bench
  Same model + good harness =  Top 5



  The model is the constant. The HARNESS is the variable.



## In trust terms


  The thing your engineer trust (or doesn't) is NOT the model.
  It is the SYSTEM that the model and your code operate in.


  Agent = Model + Harness.
  Trust = trust in the system. Not trust in the model.



  This is why "the walls matter more than the model."
  (Stripe Minions architecture, 1,000+ unattended PRs/week.)




















## The operating principle

  An agent's output quality is BOUNDED by the quality of the
  prompt and context it receives.



  Corollary 1: when the output is wrong, suspect context first.



  Corollary 2 (the trust corollary):
    Your TRUST in output is bounded by what you can VERIFY.
    If you can't verify it, you can't trust it.

    "You don't trust. You instrument."




















## Why this matters in practice

Anthropic's own April 2026 postmortem: Claude Code degraded
for 6 weeks. Cause was three overlapping HARNESS changes —
a caching bug, a verbosity prompt change, a reasoning-effort
default change. The model didn't change. The harness did.
Productivity tanked across thousands of teams.

Trust crisis. Six weeks long. From harness changes alone.



→ Your harness IS the system. Treat it like one.
   It has bugs, regressions, observability concerns.




















## The bridge: why architecture comes first


  The harness is what delivers perfect prompt + perfect context
  CONSISTENTLY and AT SCALE — not one prompt at a time.



  Hand-crafting per turn doesn't scale.
  Hand-crafting TRUST per turn doesn't scale either.



  Therefore the first move in any AI-driven project is
  designing the harness — and with it, the trust architecture.


  Architecture before code.


## The ratchet: how trust GROWS

  Every failure feeds back into the harness as a permanent rule.
  A new hook. A new line in AGENTS.md. A new sub-agent. A new gate.


  "Every line in a good AGENTS.md should be traceable back to
   a specific thing that went wrong."


  Failures stop being one-off stories. They become signals.
  And the harness ratchets — trust accumulates layer by layer.




















# Part 3 — Architecture


## Critical scope clarification



  We are designing the DEV-ENVIRONMENT harness architecture.
  The system that wraps the agent.



  We are NOT designing the PRODUCT'S architecture.
  That is project-specific. Out of scope today.



  These are two different architecture jobs. Don't conflate them.

  (Your capstone has both. Today, we only do the first.)



## Trust framing

  Trust is engineered, not assumed.
  The harness is engineered architecture.
  This is the engineering work, not faith work.




















## The central question

  "What harness should I build so that any agent running in it has
   enough context, the right prompts, and the means to verify its
   own output — sufficient to build my whole application?"

## In trust terms (same question, sharpened)

  "What harness lets me TRUST what an agent ships,
   for every task I will ever delegate to it?"

  Train both versions. They're the planning move.




















## Components of a complete harness — each one a TRUST mechanism

  Context engineering layers:


    Persistent context files       → shared expectations
                                     (AGENTS.md / CLAUDE.md / skill files)
                                     trust contract between you and the agent


    Skills                         → bounded capability
                                     trust SCOPE — what the agent can do


    Sub-agents                     → isolated context per role
                                     verifiable trust per sub-task
                                     ("specialization makes verification possible")


    Hooks                          → deterministic gates
                                     trust the LINTER, not the agent


    Slash commands                 → explicit invocation
                                     consent boundary — the agent never decides
                                     when to /deploy


    Memory                         → durable cross-session state
                                     (with provenance — memory can poison)

    Tool definitions / MCP servers → the action space
                                     what the agent can REACH



  Plus: the development loop itself — plan → implement → check → iterate
  Plus: a verification system — the trust ladder (next section)




















## Verification = the trust ladder

  Senior devs trust AI-driven code when verification is
  something they can REASON about.

  Each layer of the ladder earns a SPECIFIC KIND of trust:

  ┌──────────────────────────────────────────────────────────┐
  │  1. MECHANICAL  — deterministic, 100% compliance         │
  │     Tests, types, lints, CI, hooks.                      │
  │     The agent CANNOT skip a hook. Not "usually." Always. │
  │     Prompts get 70-90% compliance. Hooks get 100%.       │
  │     That gap is where production failures live.          │
  │                                                          │
  │  2. AGENTIC  — multiple perspectives, separation of      │
  │                writer and judge                          │
  │     Sub-agent reviews — security, code-review,           │
  │     second-opinion.                                      │
  │     An agent grading its own work is sycophantic.        │
  │     Separate the writer from the judge.                  │
  │                                                          │
  │  3. BEHAVIORAL  — did the thing actually WORK            │
  │     Real test execution the agent can run and read.      │
  │     E2E with Playwright. Runtime checks.                 │
  │     Mechanical catches syntax. Behavioral catches lies.  │
  │                                                          │
  │  4. HUMAN GATES  — irreducible judgment                  │
  │     Plan mode. PR review. Explicit deploy commands.      │
  │     "You are not relying on the agent's good intentions; │
  │      the TOOLS are gated."                               │
  │                                                          │
  └──────────────────────────────────────────────────────────┘

  A complete harness has ALL FOUR.
  Each layer is a trust step on the ladder.

## The single most important empirical fact in this whole session

  Prompt-based instructions to the agent: 70-90% compliance.
  Hooks (deterministic gates):           100% compliance.

  The gap between 70-90% and 100% is exactly where production
  failures happen. The 10-30% the agent skips IS the failure.

  Hooks remove that gap. Entirely.

  Trust the LINTER. Not the agent.




















## Where Part 3 lands

  - The harness is the ARCHITECTURE OF TRUST between engineer
    and agent.
  - It includes: context files, skills, sub-agents, hooks,
    slash commands, memory, tools — each a trust mechanism.
  - Verification is layered: mechanical, agentic, behavioral, human.
    Each layer is a step on the trust ladder.
  - The harness earns trust. Layer by layer. Ratchet by ratchet.

  Now: I'll show you a real one.
