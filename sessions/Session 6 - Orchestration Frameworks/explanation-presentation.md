











# Multi-Agent Orchestration
## Production Frameworks: LangChain + LangGraph

Session 1 promised: starting next session we cover AI IN PRODUCT.
This is that session.

──────────────────────────────────────────────────────────────────

Session 1 was AI for SDLC — the workflow YOU use to ship code.
                           Trust gap. Harness. Verification ladder.


Session 2 is AI in PRODUCT — the features your USERS experience.
                            Graphs. State. Orchestration. Evals.


Different audience, different architecture, same engineering rigor.















## The 2026 multi-agent gap

  Adoption: enormous.        Reliability: still bad.
  ──────────────────────     ────────────────────────────────
  Anthropic, Stripe,         MAST taxonomy (NeurIPS 2025):
  Cognition, GitHub —        14 failure modes in 1,600+ traces
  all shipping multi-agent
  in production              ~42% specification issues
                             ~37% inter-agent misalignment
  Databricks: 327% growth    ~21% verification gaps
  in 4 months
                             "The presence of a verifier
  Cost: ~15× chat tokens     is not a silver bullet."

  Most multi-agent demos die in production for ONE reason:
  the demo was THE AGENT. Production needs THE GRAPH.












## 0.2 Session 1 in four sentences (the load-bearing ones)

  1. THE HARNESS = the engineered environment around the agent.
       Agent = Model + Harness.
       You don't trust the MODEL. You trust the SYSTEM.
       "The walls matter more than the model." (Stripe Minions)


  2. THE HARNESS IS A SYSTEM — so it has BUGS.
       Anthropic's Apr 2026 postmortem: Claude Code degraded for
       6 WEEKS. Cause = three HARNESS changes. The MODEL never
       changed.
       → Treat your harness like production: regressions,
         observability, evals.


  3. VERIFICATION IS A LADDER — four kinds, all required:
       MECHANICAL   tests, types, lints, hooks   (100% compliance)
       AGENTIC      sub-agent reviewers (writer ≠ judge)
       BEHAVIORAL   run the real thing, watch it work
       HUMAN GATES  plan mode, PR review, explicit deploy


  4. OUTPUT IS BOUNDED BY PROMPT + CONTEXT.
       When output is wrong, suspect CONTEXT first.
       Context is the cap — you can't beat it by trying harder.



## Why we re-anchor this NOW

  Session 2 does TWO things to this frame:


   - KEEPS it. The S1 harness (OpenSpec + .claude primitives)
     wraps today's AI features UNCHANGED — same sub-agents,
     same hooks, same propose → apply → archive.


   - MIRRORS it, one level up:
       #4 output bounded by context  →  Part 2: reliability
            bounded by STATE + transitions
       #3 the verification ladder    →  Part 3: the production
            reliability ladder (schema · tracing · evals · HITL)
       #2 the harness is a system    →  your AI FEATURES are also
            a system with bugs. Same discipline.


  Hold these four. Every one comes back today.










## 0.1 The protocol landscape — where today sits

  Two open protocols frame the agent world. You met one last
  session. Know the other exists.


  ┌──────────────────────────────────────────────────────────────┐
  │  MCP  (Model Context Protocol)        — Session 1             │
  │     connects an agent to TOOLS & DATA.                       │
  │     VERTICAL: agent → database, API, file system.            │
  │                                                              │
  │  A2A  (Agent2Agent Protocol)          — today's map pin      │
  │     connects an agent to OTHER AGENTS.                       │
  │     HORIZONTAL: agent ↔ agent, across org / vendor / network.│
  └──────────────────────────────────────────────────────────────┘


  AI in SDLC - harness.
  AI in product as feature - today's session.

  ----
  Both are developed by us.

  A2A protocol is needed when our agent needs to communicate with remote agents.



  The A2A docs' own one-liner:
    "A2A is about agents PARTNERING on tasks;
     MCP is about agents USING capabilities."
  Complementary, NOT competing.



## What A2A actually is

  An open protocol for agents built by DIFFERENT teams / vendors /
  frameworks to discover each other and delegate work — WITHOUT
  sharing internal state, memory, or tools. Agents stay OPAQUE.


  Provenance:  Google, Apr 2025  →  Linux Foundation, Jun 2025
               →  v1.0.0 stable, Mar 2026.  150+ orgs.



## How it works — 5 steps

  1. DISCOVER  fetch the Agent Card at
              https://{domain}/.well-known/agent-card.json
  2. INSPECT   read its skills, capabilities, security schemes - authentication.
  3. SEND      start a Task via SendMessage / SendStreamingMessage
  4. WORK      remote agent runs; emits status + Artifacts
              (SSE stream / poll / webhook push)
  5. RESULT    Task hits a terminal state; collect Artifacts

  Plain web standards: HTTP, JSON-RPC 2.0 (or gRPC / REST), SSE.



## One concrete example — when you actually need it

  Your company's TRAVEL agent must book a flight — but the
  AIRLINE runs its OWN booking agent.

   - You DON'T own it (their firewall, data, fare rules).
   - It's a real AGENT, not a tool: checks availability, applies
     rules, may ask back "window or aisle?", holds the booking.


  Your agent →  reads the airline's Agent Card ("book-flight")
            →  authenticates across the org boundary
            →  sends a Task: "SFO→NYC, Dec 3, under $400"
            →  airline agent streams "3 options" → pauses
               input-required: "confirm the $380 one?" → books
            →  returns the Artifact: the confirmed itinerary


  Why nothing else fits:
   - can't be an MCP tool   (not yours; it negotiates, not one-shot)
   - can't share typed state (different company, different network)
   → you need a standard, authenticated, async, agent↔agent
     protocol. That's A2A.



## Why it is NOT in today's demo

  Our agents live in ONE process, ONE graph. They talk via shared
  TYPED STATE — simpler, faster, safer.

  Reach for A2A only when the other agent ISN'T YOURS —
  cross-org, cross-vendor, cross-network.

  Today: orchestration INSIDE one app.
  A2A = the map pin for "later, across a trust boundary."






















## The through-line for the next 2 hours

  In PRODUCTION, you ship the GRAPH, not the agent.


  Every primitive we teach today is a graph component.
  Every failure mode is a graph-shape failure.
  Every framework decision is which graph abstraction you accept.


  "Workflows first. Add agency only where it pays for itself."
                                             — Anthropic, Dec 2024



  graph:

  node or item of graph or component.

  edges - connection.

  {
    start: ['student'],
    student: ['teacher', 'another student'],
    teacher: ['end'],
    end
  }








# Part 1 — Foundations

## 1.0 Quick recap: what is an agent?  (60-second callback to S1)

  Agent = LLM + tools + a LOOP.


  ┌──────────────────────────────────────────┐
  │  1. Read context                         │
  │  2. Decide next move                     │
  │  3. Call a tool                          │
  │  4. Observe result (appended to context) │
  │  5. Repeat — until "done"                │
  └──────────────────────────────────────────┘


  The model is STATELESS. Context is the only lever.
  Quality of output ≤ quality of context. (S1 corollary.)



## What changed since Session 1

  Session 1: this agent runs in YOUR workflow.
             Goal = ship good code. Audience = you.


  Session 2: this agent runs in YOUR PRODUCT.
             Goal = deliver a feature. Audience = your users.


  Same primitive. Different blast radius.
  Different reliability bar. Different cost ceiling.















## 1.1 Why one agent isn't enough

  Five reasons. Each one is a Session-1 failure mode applied
  inside a product.

  ─────────────────────────────────────────────────────────

  1. CONTEXT BLOAT
     One mega-agent with all the tools = fighting its own
     context window. (S1: context rot, lost-in-the-middle.)
     Cost goes up. Quality goes down.


  2. SPECIALIZATION
     "Generate a quiz question" and "grade an answer" need
     OPPOSITE prompts. Crowd them into one system prompt and
     they cancel each other out.


  3. FAILURE CONTAINMENT
     If the grader hallucinates, that bad data MUST NOT enter
     the generator's context. (S1: context poisoning.)
     One bad turn poisoning the rest = a known accelerant.


  4. COST & LATENCY
     Routing a message: Haiku 4.5 at $1 input / $5 output.
     Hard reasoning: Opus 4.7 at $5 / $25.
     5× cost difference. Use the cheapest model that works.


  5. AUDITABILITY
     Separate the WRITER from the JUDGE. (S1's agentic
     verification, now inside the product.)
     Anthropic Code Review (Apr 2026):
       16% → 54% substantive PR comments after rollout.
       Built on this exact principle.















## 1.2 Workflows vs agents (Anthropic, Dec 2024 — VERBATIM)

  WORKFLOWS = systems where LLMs and tools are orchestrated
              through PREDEFINED CODE PATHS.


  AGENTS    = systems where LLMs DYNAMICALLY DIRECT their own
              processes and tool usage.


  Same paper, one sentence later:

    "Finding the simplest solution possible,
     and only increasing complexity when needed."


  "Most production systems are workflows.
   Agents are for tasks where the path can't be written down."





## What this means in code

  Workflow:    your CODE calls the LLM in a specific order.
               (LangGraph: a StateGraph with deterministic edges.)

A -> B -> C

A -> B -> A | C ->| C



  Agent:       the LLM decides which tool to call when.
               (LangGraph: createAgent / a ReAct loop.)

LLM with tools + loop.



  Multi-agent: multiple specialized agents collaborate via
               a graph YOU define.
               (LangGraph: multiple agent nodes + edges + state.)


  All three coexist in a real product. Same graph.















## 1.3 The four canonical patterns

  Every production multi-agent system in 2026 is one of these
  four (or a composition of them). Each one is a graph shape.
  Each one has a canonical Anthropic name + a LangGraph term.

  We'll use ONE Ilm AI example per pattern so they're concrete.



## Pattern 1 — SEQUENTIAL PIPELINE
   (Anthropic: prompt chaining · LangGraph: chain of nodes)


       ┌────────┐    ┌────────┐    ┌────────┐
   ──> │   A    │ ─> │   B    │ ─> │   C    │ ──> result
       └────────┘    └────────┘    └────────┘


  Use: a task decomposes into fixed sequential subtasks.
       Each step's output is the next step's input.
       Trades latency for accuracy.


  Ilm AI example:
    Companion chat = fetch_material → ground_answer → cite_source
    Three steps, fixed order, gate between #2 and #3 if no
    grounding found.


  Failure mode: hidden coupling — step B silently assumes step A
                emits a certain field. Schemas at boundaries fix
                this.



## Pattern 2 — ROUTER
   (Anthropic: routing · LangGraph: conditional edge from a
                                    classifier node)


                ┌────────┐
                │ router │
                └────┬───┘
            ┌───────┼────────┬────────┐
            ▼       ▼        ▼        ▼
        ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
        │  A   │ │  B   │ │  C   │ │  D   │
        └──────┘ └──────┘ └──────┘ └──────┘


  Use: distinct input categories are handled BETTER separately
       than by one generalist.
       The classifier should be CHEAP (Haiku 4.5).


  Ilm AI example:
    Front-door dispatcher: user sends a message →
    Haiku classifier returns one of:
      "companion" | "quiz" | "plan" | "gap-report"
    → run the corresponding sub-graph.


  Failure mode: misroute. Always have a fallback "ask for
                clarification" path; never silently choose the
                wrong specialist.



## Pattern 3 — PARALLEL FAN-OUT
   (Anthropic: parallelization — two variants:
      SECTIONING (different subtasks)  ·  VOTING (same task N×)
   LangGraph: array-returning conditional edge / Send API)


           ┌────────┐
       ──> │planner │ ──>  ┌──────┐
           └────────┘  ┌──>│  A   │──┐
                       │   └──────┘  │
                       │   ┌──────┐  │   ┌─────────────┐
                       ├──>│  B   │──┼──>│ synthesizer │ ──>
                       │   └──────┘  │   └─────────────┘
                       │   ┌──────┐  │
                       └──>│  C   │──┘
                           └──────┘


  Sectioning: different subtasks in parallel (one per topic).
  Voting:     same task N times for confidence (3 graders,
              majority wins).


  Ilm AI example (sectioning):
    Learning plan = planner picks 4 topics →
    4 worker agents in parallel, one per topic →
    synthesizer merges into a unified 4-week plan.


  Failure mode: race conditions / colliding state writes.
                LangGraph forces you to declare a REDUCER
                on any channel multiple branches write to.



## Pattern 4 — ORCHESTRATOR–WORKER
   (Anthropic: orchestrator-workers · LangGraph: supervisor /
                                                 hierarchical)


           ┌──────────────┐
       ──> │ orchestrator │ ──> [decides at RUNTIME how many
           └──────┬───────┘      workers, what each does]
                  │
            ┌─────┼─────┐
            ▼     ▼     ▼
        ┌─────┬─────┬─────┐
        │ W1  │ W2  │ W3  │
        └──┬──┴──┬──┴──┬──┘
           └─────┼─────┘
                 ▼
           ┌──────────────┐
       ──> │ synthesizer  │ ──> result
           └──────────────┘


  Use: subtasks decided AT RUNTIME (not knowable in advance).
       Most powerful and most failure-prone pattern.


  Ilm AI example:
    Gap-report agent over quiz history:
      orchestrator reads N quiz sessions →
      decides which K concepts to dig into →
      spawns K worker agents (one per concept) →
      synthesizes a personalized gaps report.


  Anthropic's own multi-agent research system (Jun 2025):
    Lead Opus + N Sonnet sub-agents.
    +90.2% over single-agent Opus on internal evals.
    BUT: 15× chat-equivalent token usage.



## The four patterns — recap card

  SEQUENTIAL  →  fixed steps, A→B→C
  ROUTER      →  classifier dispatches to specialists
  PARALLEL    →  N agents in parallel, merged
  ORCHESTRATOR→  runtime-decided subtasks, spawned & synthesized


  Every production multi-agent system is one of these,
  OR a composition of them.


  The 5th worth knowing — EVALUATOR-OPTIMIZER:
    a refinement loop — generator + critic, iterate to quality.
    Anthropic Code Review uses this on top of parallel fan-out.















## 1.4 Multi-agent failure modes  (MAST, NeurIPS 2025)

  Cemri et al. hand-annotated 1,600+ multi-agent traces across
  7 frameworks. 14 failure modes in 3 categories:


  ┌────────────────────────────────────────────────────────────┐
  │ FC1 — SPECIFICATION ISSUES                            42%  │
  │   1.1 Disobey task spec                10.98%              │
  │   1.3 Step repetition                  17.14%              │
  │   1.5 Unaware of termination conditions 9.82%              │
  │                                                            │
  │ FC2 — INTER-AGENT MISALIGNMENT                        37%  │
  │   2.2 Fail to ask for clarification   11.65%              │
  │   2.3 Task derailment                   7.15%              │
  │   2.6 Reasoning-action mismatch        13.98%              │
  │                                                            │
  │ FC3 — TASK VERIFICATION                              21%  │
  │   3.1 Premature termination             7.82%              │
  │   3.2 No or incomplete verification     6.82%              │
  │   3.3 Incorrect verification            6.66%              │
  └────────────────────────────────────────────────────────────┘


  Verbatim: "The presence of a verifier is NOT a silver bullet."



## "But isn't this just weak models?" — NO. STRUCTURE bugs.

  A smarter model loops less and derails less. It does NOT invent
  your stop conditions, your shared state, or your handoff
  contracts. The fix is the SYSTEM, not the model.

  ┌────────────────────────┬───────────────────────────┬────────────────────────────┐
  │ Failure (model-indep.) │ Why it happens             │ Correct approach           │
  ├────────────────────────┼───────────────────────────┼────────────────────────────┤
  │ Unaware of termination │ no stop condition was      │ explicit edges to END +    │
  │                        │ ever written              │ a step/budget counter      │
  ├────────────────────────┼───────────────────────────┼────────────────────────────┤
  │ Step repetition /      │ two nodes hand back & forth│ named edges + recursion    │
  │ loops                  │ with no cycle-break rule   │ limit — topology forbids it│
  ├────────────────────────┼───────────────────────────┼────────────────────────────┤
  │ Conflicting parallel   │ workers can't see each     │ share FULL state + pin     │
  │ decisions              │ other; implicit choices    │ cross-cutting decisions    │
  │                        │ that won't merge           │ UPSTREAM in orchestrator   │
  ├────────────────────────┼───────────────────────────┼────────────────────────────┤
  │ Fail to ask for        │ path to ANSWER, no path    │ explicit clarification     │
  │ clarification          │ to ASK → it guesses        │ BRANCH (conf < 0.65)       │
  ├────────────────────────┼───────────────────────────┼────────────────────────────┤
  │ Lost info in handoff   │ B got A's final message,   │ pass full TYPED STATE,     │
  │                        │ not A's reasoning          │ not a relayed summary      │
  ├────────────────────────┼───────────────────────────┼────────────────────────────┤
  │ Weak / missing         │ check was a vibe, or       │ SCHEMA enforcement at      │
  │ verification           │ skipped under pressure     │ every boundary + det. checks│
  └────────────────────────┴───────────────────────────┴────────────────────────────┘

  DoD - Definition of Done.

  The MODEL supplies intelligence. The SYSTEM supplies structure.
  A better model raises the floor — it never supplies the
  structure for you. Every fix above is in the demo.



## And the headline cost number you must know

  Anthropic's multi-agent research system (Jun 2025):
    multi-agent ≈ 15× chat tokens.
    single-agent agentic ≈ 4× chat tokens.

  80% of performance variance = just token spend.

  Multi-agent works because it spends more.
  Not because it's magic.















## Where Part 1 lands

  - One agent = LLM + tools + loop.        (S1 callback)
  - One agent isn't enough for product features:
      context bloat, specialization, failure containment,
      cost/latency, auditability.
  - The taxonomy: workflows first, agents only where needed.
  - The four patterns: SEQUENTIAL · ROUTER · PARALLEL · ORCHESTRATOR.
  - The data: MAST — 14 failure modes; the 15× token reality.


  Multi-agent works when it's a GRAPH, not a chat.
  Reliability comes from EXPLICITNESS, not from cleverness.















# Part 2 — The operating principle

## The principle

  A multi-agent system's reliability is BOUNDED
  by the EXPLICITNESS of its STATE/context and its TRANSITIONS.

  output token is bounded by input token.



## What "state" means here (it's BIGGER than messages)

  STATE = all the user + session + application context
          the graph carries at every step.


           messages            — the conversation
       +   userId, tenantId    — WHO is asking
       +   tier, language,     — application state about the user
           preferences
       +   current material,   — session state
           selected topic,
           pending question
       +   intermediate        — what the graph has computed so far
           agent outputs
       +   memory references   — what we know about the user from
                                 PRIOR sessions


  S1 said "context" = the LLM's token window.
  S2 says "state"   = the user/app context the graph CARRIES
                      and every node SEES.


  Same discipline. One level up.



## Corollaries you'll catch yourself using daily

  1. When output is wrong, suspect STATE first.
     (Mirror of S1: when output is wrong, suspect CONTEXT first.)
     What did this agent actually see about the USER, the SESSION,
     the prior turn — not what did you ASSUME it saw.


  2. Emergent "let them talk it out" systems do NOT ship.
     Every production multi-agent system in 2026 is a graph
     with named nodes and named edges.


  3. The orchestrator is PRODUCT CODE, not a prompt.
     It's the deterministic part you write — and review,
     and test, and version.















## 2.2 The Cognition framing (the load-bearing quotes)

  Walden Yan, Cognition, Jun 2025 — "Don't Build Multi-Agents":


  ┌────────────────────────────────────────────────────────────┐
  │  Principle 1                                               │
  │                                                            │
  │  "Share context, and share full agent traces,              │
  │   not just individual messages."                           │
  │                                                            │
  │                                                            │
  │  Principle 2                                               │
  │                                                            │
  │  "Actions carry implicit decisions, and conflicting        │
  │   decisions carry bad results."                            │
  └────────────────────────────────────────────────────────────┘


  Their conclusion: default to a SINGLE-THREADED linear agent
  with an LLM-based history compressor for long sessions.


  Their warning (verbatim):
    "Running multiple agents in collaboration only results in
     fragile systems."















## 2.3 The orchestrator's five jobs (framework-agnostic)

  Every production orchestrator does these five things.
  Pick your framework based on how it handles them.


  ┌─────────────────────────────────────────────────────────────┐
  │ 1. ROUTE       — pick which agent acts next                 │
  │ 2. STATE       — define what each agent sees & writes       │
  │ 3. PERSIST     — checkpoint state for resume / replay       │
  │ 4. FAIL        — handle timeouts, retries, fallbacks        │
  │ 5. GATE        — pause for human-in-the-loop where needed   │
  └─────────────────────────────────────────────────────────────┘


  These map directly to LangGraph primitives (Part 4):
  conditional edges · typed state · checkpointers · retry
  policies · interrupt() + humanInTheLoopMiddleware.



## The bridge to architecture

  The orchestration layer is what delivers EXPLICIT STATE
  and EXPLICIT TRANSITIONS consistently and at scale —
  not one feature at a time.

  Hand-rolling per-feature doesn't scale.

  Therefore the first move in any AI-in-product project
  is designing the orchestration architecture.















# Part 3 — Architecture

## Scope discipline (recall from Session 1)

  Session 1: we designed the DEV-ENVIRONMENT harness.
  Session 2: we now also design the PRODUCT'S multi-agent
             architecture.


  Both exist in real projects. Same engineering rigor.
  Different code, different verification, different SLAs.


  Today is the PRODUCT side, exclusively.


  Recall: every Session-1 verification layer
  (mechanical · agentic · behavioral · human-gate)
  still applies to your AI features.
  We're just adding new ones SPECIFIC to multi-agent.















## 3.2 The component list — production multi-agent

  Every production multi-agent system has these eight components.
  Each one extends a Session-1 concept.
  The FIRST one is the load-bearing one: it's what S1's "context"
  becomes in a graph-shaped world.


  ┌──────────────────────────┬─────────────────────────┬──────────────────────┐
  │ Component                │ Purpose                 │ S1 concept extended  │
  ├──────────────────────────┼─────────────────────────┼──────────────────────┤
  │ USER / APP CONTEXT       │ typed state every node  │ context engineering, │
  │   (the typed `State`)    │ sees — userId, tenant,  │ now applied to       │
  │                          │ tier, language, current │ user+session+app     │
  │                          │ session, prior outputs, │ data instead of      │
  │                          │ memory refs, messages   │ raw model tokens     │
  ├──────────────────────────┼─────────────────────────┼──────────────────────┤
  │ NODES (agents/tools)     │ specialized work units  │ the agent primitive  │
  ├──────────────────────────┼─────────────────────────┼──────────────────────┤
  │ EDGES                    │ transition logic        │ replaces "let the    │
  │  (det. + conditional)    │                         │  agent decide it"    │
  ├──────────────────────────┼─────────────────────────┼──────────────────────┤
  │ TOOLS                    │ DB, APIs, computation   │ MCP / tool use       │
  │                          │ (closed over userId —   │  (per-user scoping   │
  │                          │  the model cannot       │   bound at the       │
  │                          │  impersonate)           │   closure, not the   │
  │                          │                         │   tool call)         │
  ├──────────────────────────┼─────────────────────────┼──────────────────────┤
  │ MEMORY                   │ short-term (per run)    │ "isolate" lever      │
  │                          │ + long-term (across)    │ + cross-session      │
  │                          │ — both keyed by user    │   user profile       │
  ├──────────────────────────┼─────────────────────────┼──────────────────────┤
  │ CHECKPOINTER             │ durable per-step state  │ verification         │
  │   (keyed by thread_id =  │ snapshot                │  (replay = audit)    │
  │    user-${id}-${feat})   │                         │                      │
  ├──────────────────────────┼─────────────────────────┼──────────────────────┤
  │ HITL GATES               │ explicit pause points   │ human-gate verif     │
  ├──────────────────────────┼─────────────────────────┼──────────────────────┤
  │ OBSERVABILITY            │ tracing + cost/latency  │ verification ladder  │
  │                          │ + per-node evals        │                      │
  └──────────────────────────┴─────────────────────────┴──────────────────────┘


  Plus, cross-cutting:
   - safety boundaries (per-agent tool scopes,
                        prompt-injection defenses)
   - budget guards (cost caps per run, cheap-model fallback)



## The first row, unpacked — because this is where it lives

  STATE is not a bag of data. It IS your user/application context,
  promoted to first-class typed schema.


  Typical Ilm AI graph state fields:

    userId            — from the authenticated session,
                        bound at the route-handler boundary
    tier              — free / premium (gates feature access)
    language          — en / ru / uz (gates reply language)
    materialId        — the user's currently-selected material
    materialText      — fetched per-run by a DAL-scoped node
    intent            — last classification from the router
    messages          — conversation history (this turn)
    intermediate      — sub-agent outputs collected so far
    memoryRefs        — pointers into cross-session memory


  Bound at graph invocation. Typed end-to-end. Schema-validated.
  EVERY node sees it. EVERY transition can read AND write it.


  This is how the user-context "follows" the user across:
    - many agents in one turn   (handoffs)
    - many turns in one session (thread_id + checkpointer)
    - many sessions             (long-term memory layer)















## 3.3 The PRODUCTION RELIABILITY LADDER
   (the multi-agent analog of S1's verification ladder)


  Each layer earns a specific kind of trust.


  ┌──────────────────────────────────────────────────────────────┐
  │ 1. SCHEMA ENFORCEMENT                                        │
  │    Zod schemas at every node boundary.                       │
  │    Invalid output CANNOT leave a node.                       │
  │    Grammar-constrained at the provider when supported:       │
  │      Anthropic strict tools = provably valid JSON.           │
  │    "Trust the schema, not the prose."                        │
  │                                                              │
  │ 2. TRACING                                                   │
  │    Every run is replayable.                                  │
  │    LangSmith renders multi-agent runs as a TREE.             │
  │    You can answer: "what did the grader actually see?"       │
  │    "Trust what you can replay, not what you can hope."       │
  │                                                              │
  │ 3. EVALS                                                     │
  │    Regression tests for agent quality.                       │
  │    50-sample rubric (the capstone's requirement) lives here. │
  │    Trajectory match + LLM-as-judge.                          │
  │    "Trust what you measured, not what you remember."         │
  │                                                              │
  │ 4. HITL GATES                                                │
  │    Consequential actions require explicit acceptance.        │
  │    "Don't surface a 4-week plan to the user without          │
  │     a confirm step. Don't auto-spend $10 of Opus tokens."    │
  │    "Trust the human on the hard ones."                       │
  └──────────────────────────────────────────────────────────────┘


  A complete multi-agent system has ALL FOUR.

  Mirror to Session 1's ladder:
    mechanical · agentic · behavioral · human-gate.















## 3.4 The central question

  Train yourself to ask it on every AI feature:


  ┌────────────────────────────────────────────────────────────┐
  │  "What graph should I compile so that every AI feature my  │
  │   product ships is TYPED, TRACED, DEBUGGABLE, and          │
  │   VERIFIABLE — sufficient for the lifetime of the          │
  │   feature?"                                                │
  └────────────────────────────────────────────────────────────┘


  Notice what it does NOT ask:
    - what model to use     (downstream — per-node decision)
    - which framework        (downstream — Part 4)
    - whether multi-agent    (downstream — pattern-by-pattern)


  Get the GRAPH right first. The rest follows.















# Part 4 — The chosen frameworks (LOCKED)

## What we're using (and why we picked it)


   LangChain v1   (integration layer)
        +
   LangGraph 1.3.x   (orchestration layer)


   TypeScript/JavaScript. Runs in the same Next.js process
   as the rest of the app.



## Why (the rationale for the record)

  - The capstone brief explicitly recommends LangChain.
  - LangChain 1.0 went GA Oct 2025; LTS commitment.
  - LangGraph is the de-facto production graph runtime in May 2026
    (Anthropic, LinkedIn, Klarna, Uber, Replit, etc.).
  - Native TypeScript — Next.js, no Python service split.
  - Patterns transfer to ANY orchestrator (hand-rolled,
    Anthropic Managed Agents, OpenAI Agents SDK).



## Selection philosophy (locked, carried from S1)

  We do NOT survey existing approaches in the session.
  We picked one. We teach it.















## 4.2 The honest split (the framing senior devs respect)


  ┌──────────────────────────────────────────────────────────────┐
  │  LangChain v1     →   INTEGRATION layer                      │
  │  ─────────────                                               │
  │   - models (ChatAnthropic, ChatOpenAI, ...)                  │
  │   - tools (tool() + Zod)                                     │
  │   - middleware (HITL, retries, prompt caching, summarize)    │
  │   - structured output (providerStrategy, toolStrategy)       │
  │   - createAgent factory (single-agent ReAct loop)            │
  │                                                              │
  │  CONVENIENT but NOT THE ONLY WAY.                            │
  │  You can call provider SDKs directly and lose very little.   │
  └──────────────────────────────────────────────────────────────┘


  ┌──────────────────────────────────────────────────────────────┐
  │  LangGraph 1.3.x  →   ORCHESTRATION layer                    │
  │  ───────────────                                             │
  │   - StateGraph (typed state with reducers)                   │
  │   - addEdge / addConditionalEdges                            │
  │   - ToolNode + Command primitive                             │
  │   - interrupt() + breakpoints (HITL)                         │
  │   - MemorySaver / PostgresSaver / SqliteSaver                │
  │   - .stream() with values/updates/messages/tools modes       │
  │                                                              │
  │  THIS is where the actual production value is.               │
  │  Even if you abandon LangChain elsewhere,                    │
  │  the LangGraph patterns transfer.                            │
  └──────────────────────────────────────────────────────────────┘















## 4.3 The framework surface — concrete

### Install (May 2026)

   pnpm add langchain @langchain/core \
           @langchain/anthropic @langchain/openai \
           @langchain/langgraph \
           @langchain/langgraph-checkpoint-postgres \
           zod


### Versions you'll see in package.json (verified 2026-05-24)

   langchain                            1.4.x
   @langchain/core                      1.1.x
   @langchain/anthropic                 1.4.x
   @langchain/langgraph                 1.3.x
   @langchain/langgraph-checkpoint-postgres  1.0.x


### Anthropic model IDs (current production)

   claude-opus-4-7      Opus 4.7   1M ctx   $5 / $25 per MTok
   claude-sonnet-4-6    Sonnet 4.6 1M ctx   $3 / $15
   claude-haiku-4-5     Haiku 4.5  200K     $1 / $5

   IDs are PINNED snapshots — no floating aliases since 4.6.















### A typed StateGraph — the canonical shape

```typescript
import { StateGraph, Annotation, MessagesAnnotation,
         START, END } from "@langchain/langgraph";
import { ChatAnthropic } from "@langchain/anthropic";

// 1. STATE — typed, with reducers
const State = Annotation.Root({
  ...MessagesAnnotation.spec,
  intent: Annotation<string>(),
  materialId: Annotation<string>(),
  citations: Annotation<string[]>({
    reducer: (a, b) => [...a, ...b],
    default: () => [],
  }),
});

// 2. MODEL (per-node — Haiku for cheap, Sonnet/Opus for hard)
const haiku = new ChatAnthropic({ model: "claude-haiku-4-5" });
const sonnet = new ChatAnthropic({ model: "claude-sonnet-4-6" });

// 3. NODES (each node: (state) => partial state update)
const router = async (state) => {
  const classification = await haiku.withStructuredOutput(
    z.object({ intent: z.enum(["companion", "quiz", "plan"]) })
  ).invoke([new HumanMessage(state.messages.at(-1).content)]);
  return { intent: classification.intent };
};

// 4. GRAPH
const graph = new StateGraph(State)
  .addNode("router", router)
  .addNode("companion", companionNode)
  .addNode("quiz", quizNode)
  .addNode("plan", planNode)
  .addEdge(START, "router")
  .addConditionalEdges("router", (s) => s.intent,
    { companion: "companion", quiz: "quiz", plan: "plan" })
  .addEdge("companion", END)
  .addEdge("quiz", END)
  .addEdge("plan", END)
  .compile();
```















### Handoffs via the Command primitive

```typescript
import { Command } from "@langchain/langgraph";

const planAgent = async (state) => {
  if (needsClarification(state)) {
    return new Command({
      goto: "ask_user",
      update: { pendingQuestion: "...?" },
    });
  }
  return { plan: await generatePlan(state) };
};

// When a tool returns a Command (used in handoffs across agents):
const transferToSpecialist = tool(
  async (_, config) =>
    new Command({
      goto: "specialist",
      update: { messages: [new ToolMessage({
                  content: "Transferred",
                  tool_call_id: config.toolCallId,
                })] },
    }),
  { name: "transfer", description: "Hand off to specialist",
    schema: z.object({}) },
);
```















### Structured outputs at every boundary — Zod is the contract

```typescript
import { z } from "zod";

const QuizQuestion = z.object({
  question: z.string().describe("Plain language; one concept"),
  choices: z.array(z.string()).length(4),
  correct: z.number().int().min(0).max(3),
  concept: z.string().describe("The single concept tested"),
  citation: z.string().describe("section/page from the material"),
});

// Use 1: ON A MODEL — withStructuredOutput
const generator = new ChatAnthropic({ model: "claude-sonnet-4-6" })
  .withStructuredOutput(QuizQuestion);

const q = await generator.invoke([...]);
// q is { question, choices, correct, concept, citation } — TYPED.


// Use 2: INSIDE createAgent — responseFormat
import { createAgent, providerStrategy } from "langchain";

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [readMaterial, ...],
  systemPrompt: QUIZ_GENERATOR_PROMPT,
  responseFormat: providerStrategy(QuizQuestion),
});

const result = await agent.invoke({ messages: [...] });
const typed = result.structuredResponse;
```















### Checkpointer + HITL — durable graphs

```typescript
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
import { interrupt } from "@langchain/langgraph";

const checkpointer = PostgresSaver.fromConnString(
  process.env.DATABASE_URL!
);
await checkpointer.setup();  // idempotent; run once at boot

const graph = new StateGraph(State)
  .addNode("planner", planner)
  .addNode("await_approval", async (state) => {
    const decision = interrupt({
      plan: state.draftPlan,
      question: "Save this plan?",
    });
    return decision === "approve"
      ? { status: "approved" }
      : { status: "rejected" };
  })
  .addNode("commit", commitNode)
  .addEdge(START, "planner")
  .addEdge("planner", "await_approval")
  .addConditionalEdges("await_approval", (s) =>
    s.status === "approved" ? "commit" : END)
  .addEdge("commit", END)
  .compile({ checkpointer });

// Drive it
const cfg = { configurable: { thread_id: `user-${userId}-plan` } };
const r1 = await graph.invoke({ ... }, cfg);
//   r1.__interrupt__ is present — UI shows "Save this plan?" button

// After the human clicks Approve:
const r2 = await graph.invoke(
  new Command({ resume: "approve" }), cfg
);
```















### Streaming for the UI + prompt caching for cost

```typescript
// Streaming a graph run from a Next.js Route Handler
export const runtime = "nodejs";

export async function POST(req: Request) {
  const { messages, threadId } = await req.json();
  const cfg = { configurable: { thread_id: threadId },
                streamMode: ["messages", "updates"] };

  const stream = new ReadableStream({
    async start(controller) {
      const enc = new TextEncoder();
      for await (const [mode, chunk] of await graph.stream(
        { messages }, cfg
      )) {
        controller.enqueue(
          enc.encode(`data: ${JSON.stringify({ mode, chunk })}\n\n`)
        );
      }
      controller.close();
    },
  });
  return new Response(stream, {
    headers: { "Content-Type": "text/event-stream",
               "Cache-Control": "no-cache, no-transform" },
  });
}


// streamMode — the menu (library-defined; you pick per feature)
//   values   — the WHOLE state after each step
//   updates  — just the partial diff a node returned   ← progress
//   messages — LLM tokens, token-by-token              ← typewriter
//   custom   — anything you emit via config.writer({}) ← app events
//   tools    — tool start/end/error events
//   debug    — maximal detail
// Pass an array → multiplexed [mode, chunk] tuples.
// We use ["messages","updates"]: tokens + node progress.


// Prompt caching — 90% input cost reduction on cache hits
import { anthropicPromptCachingMiddleware } from "langchain";

const agent = createAgent({
  model: "claude-sonnet-4-6",
  systemPrompt: LONG_SYSTEM_PROMPT,  // cached
  tools: [...],                       // cached
  middleware: [anthropicPromptCachingMiddleware({ ttl: "5m" })],
});
```















## 4.4 The anti-pattern: free-form multi-agent chat

  ┌──────────────────────────────────────────────────────────────┐
  │  "Let N agents converse with each other and figure it out."  │
  │                                                              │
  │  AutoGen GroupChatManager. Unconstrained CrewAI configs.     │
  │  Anything where the orchestration is implicit in prompts,    │
  │  not in code.                                                │
  │                                                              │
  │  Looks magical in demos.                                     │
  │  Falls over in production.                                   │
  └──────────────────────────────────────────────────────────────┘


  Why it fails (Cognition's two principles, restated):

   1. Context is dispersed — agents see truncated views,
      miss reasoning, conflict with each other.
   2. Implicit decisions accumulate — when synthesizer tries
      to merge, results conflict and cannot be reconciled.


  What to do instead:


  ┌──────────────────────────────────────────────────────────────┐
  │  GRAPH-SHAPED orchestration:                                 │
  │    - Explicit state schema                                   │
  │    - Explicit named nodes                                    │
  │    - Explicit edges (deterministic or condition-coded)       │
  │    - Explicit structured outputs at every boundary           │
  │    - Explicit handoffs via Command                           │
  └──────────────────────────────────────────────────────────────┘


  This is what every production multi-agent system in 2026
  actually looks like.


  Receipts:
   - Anthropic Code Review (Apr 2026): parallel agents + verifier
   - Anthropic Research System (Jun 2025): orchestrator + workers
   - Stripe Minions (Mar 2026): hybrid workflow + agentic nodes
   - Cognition Devin: single-threaded with managed sub-Devins

  All four are GRAPHS. None of them are chat rooms.















## 4.5 Observability — LangSmith (next-layer mention)

  When you turn on LangSmith env vars:
     LANGSMITH_TRACING=true
     LANGSMITH_API_KEY=lsv2_pt_...
     LANGSMITH_PROJECT=ilm-ai-prod


  Every LangGraph run auto-traces:
   - each node as a child span
   - each LLM call with token counts + cost
   - each tool call with args + result
   - multi-agent runs as a TREE


  You can answer in 10 seconds:
   "Why did the grader give a 3 for that question?"
   - replay the exact node, exact input, exact tool calls.


  For your capstone's 50-sample eval rubric:
   - dataset of inputs + reference outputs in LangSmith
   - trajectory match (did the right nodes fire?)
   - LLM-as-judge on final outputs


  This is the layer that turns the graph into a production system.















## Where the presentation half lands

  - You ship the GRAPH, not the agent.
  - One agent isn't enough; multi-agent is a GRAPH of agents.
  - Four patterns: sequential, router, parallel, orchestrator.
  - Reliability is BOUNDED by state + transitions.
  - Four production layers: schema, tracing, evals, HITL.
  - Anchor: LangChain v1 + LangGraph 1.3.x.
  - Anti-pattern: free-form multi-agent chat.


  Now: a real one. Built on YOUR OWN capstone's bones.





withStructuredOutput - does not just give template to agent.

LLM always produces 1 token at a time.


      90%, 75%,  70%
hi -> hi, hello, hey

top k - maximum amount of possible tokens to pick from
top p - statistical percentage of each token.


withStructuredOutput always requires the agent to use specific JSON

{ 
  "text": "some text",
  
}