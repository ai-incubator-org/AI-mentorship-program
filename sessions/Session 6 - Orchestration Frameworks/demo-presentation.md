













## The demo project

  Ilm AI — Session Demo Edition
  (continued from Session 1)


  Same workspace. Same Postgres schema. Same auth + materials +
  Stripe + Telegram. Same .claude/ harness — 9 sub-agents,
  6 skills, 3 hooks.


  At end of Session 1: c5-final on `ilm-ai-demo`.
                       4 features shipped. ZERO AI.


  At end of Session 2: ai-c5-final on `ilm-ai-demo`.
                       AI orchestration layer added through
                       6 OpenSpec change cycles, on top of c5-final.


  Stack additions:    langchain v1, @langchain/langgraph 1.3.x,
                      @langchain/anthropic, @langchain/openai,
                      PostgresSaver (existing Postgres),
                      pre-extracted text column on materials.


  Branches you'll watch:
    ai-c0-scaffold  →  framework + plumbing
    ai-c1-companion →  SEQUENTIAL PIPELINE
    ai-c2-quiz      →  SEQUENTIAL MULTI-AGENT
    ai-c3-router    →  ROUTER
    ai-c4-planner   →  ORCHESTRATOR-WORKER (+ parallel fan-out)
    ai-c5-final     →  HITL + persistence + Telegram integration















## ai-c0-scaffold — Framework wired in BEFORE any feature

  Commit: ai-c0: scaffold AI orchestration layer
          (langchain v1 + langgraph + checkpointer + extracted text)


  What's added:

    package.json
      + langchain                                  ^1.4.2
      + @langchain/core                            ^1.1.48
      + @langchain/anthropic                       ^1.4.0
      + @langchain/openai                          ^1.4.7
      + @langchain/langgraph                       ^1.3.2
      + @langchain/langgraph-checkpoint-postgres   ^1.0.1


    openspec/specs/ai-orchestration/spec.md       ← NEW canonical
    openspec/changes/archive/2026-05-15-add-ai-scaffold/


    .claude/agents/
      ├── graph-shape-reviewer.md       ← NEW
      └── schema-boundary-reviewer.md   ← NEW

    .claude/skills/ai-orchestration/    ← NEW project skill


    lib/ai/                              ← NEW directory
      ├── config.ts                      ← AI_ENABLED gate
      ├── models.ts                      ← Haiku/Sonnet/Opus factory
      ├── checkpointer.ts                ← PostgresSaver bootstrap
      ├── tools/materials.tools.ts
      ├── prompts/shared.prompt.ts
      ├── schemas/shared.schemas.ts
      └── graphs/ (empty until c1)


    lib/db/schema.ts                     ← + materials.extracted_text
                                           (// human-approved: 2026-05-15)
    lib/db/migrations/0005_materials_extracted_text.sql


    instrumentation.ts                   ← + await checkpointer.setup()


    CODEOWNERS                           ← + lib/ai/** requires review















## ai-c1-companion — SEQUENTIAL PIPELINE

  Commit: ai-c1: add learning companion
          (sequential pipeline — capability: ai-companion)


  What's added:

    openspec/specs/ai-companion/spec.md          ← NEW canonical

    .claude/agents/socratic-tone-reviewer.md     ← NEW


    lib/ai/
      ├── graphs/companion.graph.ts              ← the StateGraph
      ├── prompts/companion.prompt.ts            ← Socratic tutor
      ├── schemas/companion.schemas.ts           ← CompanionAnswer
      └── tools/materials.tools.ts               ← (extended)


    app/(app)/chat/
      ├── page.tsx
      ├── client.tsx                             ← uses SSE
      └── loading.tsx

    app/api/ai/companion/route.ts                ← streams the graph


    tests/unit/ai-companion-graph.test.ts
    tests/unit/companion-schema.test.ts
    tests/e2e/ai-chat.spec.ts



## The graph shape (sequential pipeline)


   START ──> fetchMaterial ──> groundAnswer ──> END


  State fields: messages, userId, materialId, materialText, answer.

  Models: Sonnet 4.6 for grounding (one model call per turn).

  Boundaries: every answer carries a CITATION (schema-enforced).















## ai-c2-quiz — SEQUENTIAL MULTI-AGENT

  Commit: ai-c2: add quiz orchestration
          (generator → grader → explainer — capability: ai-quiz)


  What's added:

    openspec/specs/ai-quiz/spec.md               ← NEW canonical

    .claude/agents/quiz-pedagogy-reviewer.md     ← NEW


    lib/ai/
      ├── graphs/quiz.graph.ts                   ← 3-agent pipeline
      ├── prompts/quiz-generator.prompt.ts
      ├── prompts/quiz-grader.prompt.ts
      ├── prompts/quiz-explainer.prompt.ts
      └── schemas/quiz.schemas.ts                ← 3 schemas


    app/(app)/quiz/
      ├── page.tsx
      ├── client.tsx                             ← streaming UI
      └── loading.tsx

    app/api/ai/quiz/route.ts


    lib/db/schema.ts        ← + quiz_sessions, quiz_answers
                              (// human-approved: 2026-05-19)
    lib/db/migrations/0006_quiz_history.sql


    tests/unit/quiz-graph.test.ts
    tests/unit/quiz-schemas.test.ts
    tests/e2e/ai-quiz.spec.ts



## The graph shape (sequential multi-agent)


   PHASE 1 — generate:
     START ──> generator ──> END
     (returns QuizQuestion to the UI)


   PHASE 2 — grade + explain (after the user picks):
     START ──> grader ──> explainer ──> END


  Models:
    generator   → Sonnet 4.6  (hard generation)
    grader      → NO MODEL    (deterministic comparison)
    explainer   → Sonnet 4.6  (substantial generation)


  Boundaries: QuizQuestion / GradeResult / Explanation
              (3 Zod schemas, strict tool use on Anthropic)















## ai-c2 schemas — the contract between agents

```typescript
export const QuizQuestion = z.object({
  question: z.string().min(10),
  choices: z.array(z.string().min(1)).length(4),
  correctIndex: z.number().int().min(0).max(3),
  concept: z.string(),
  citation: z.string(),
});

export const GradeResult = z.object({
  questionId: z.string(),
  studentAnswerIndex: z.number().int().min(0).max(3),
  isCorrect: z.boolean(),
  partialCredit: z.number().min(0).max(1),
});

export const Explanation = z.object({
  whyCorrect: z.string(),
  whyOthersWrong: z.array(z.string()).length(3),
  reviewSuggestion: z.string(),
});
```


  Three schemas. One contract per agent boundary.
  Strict tool use → grammar-constrained output → schema-guaranteed.















## ai-c3-router — ROUTER PATTERN

  Commit: ai-c3: add front-door router
          (router pattern — capability: ai-router)


  What's added:

    openspec/specs/ai-router/spec.md             ← NEW canonical

    .claude/agents/router-classifier-reviewer.md ← NEW


    lib/ai/
      ├── graphs/router.graph.ts                 ← the dispatcher
      ├── prompts/router.prompt.ts               ← Haiku-targeted
      └── schemas/router.schemas.ts              ← Intent enum


    app/(app)/assistant/                         ← unified front-door
      ├── page.tsx
      └── client.tsx

    app/api/ai/assistant/route.ts                ← single entry route


    tests/unit/router-graph.test.ts              ← 20 golden inputs
    tests/e2e/ai-assistant.spec.ts



## ai-c3 schema — Intent enum + confidence

```typescript
export const Intent = z.enum([
  "companion", "quiz", "plan", "gap_report", "unclear"
]);

export const RouterDecision = z.object({
  intent: Intent,
  confidence: z.number().min(0).max(1),
  clarification: z.string().nullable(),
});
```


## ai-c3 graph shape


              ┌────────┐
       ──>    │classify│   (Haiku 4.5)
              └───┬────┘
                  │ (route based on intent + confidence)
       ┌──────────┼──────────┬──────────┬──────────┐
       ▼          ▼          ▼          ▼          ▼
   companion   quiz       plan     gap_report  ask_clarify


  Confidence < 0.65 → ask_clarification (spec-enforced).
  Never silently misroute.















## ai-c4-planner — ORCHESTRATOR-WORKER (+ PARALLEL FAN-OUT)

  Commit: ai-c4: add learning plan generator
          (orchestrator-worker — capability: ai-plan)


  What's added:

    openspec/specs/ai-plan/spec.md               ← NEW canonical

    .claude/agents/
      ├── orchestrator-worker-reviewer.md        ← NEW
      └── plan-quality-reviewer.md               ← NEW


    lib/ai/
      ├── graphs/plan.graph.ts                   ← THE headline file
      ├── prompts/plan-orchestrator.prompt.ts
      ├── prompts/plan-worker.prompt.ts
      ├── prompts/plan-synthesizer.prompt.ts
      └── schemas/plan.schemas.ts                ← 3 schemas


    app/(app)/plan/
      ├── page.tsx
      ├── client.tsx           ← shows parallel worker progress
      └── loading.tsx

    app/api/ai/plan/route.ts


    lib/db/schema.ts        ← + learning_plans
                              (// human-approved: 2026-05-23)
    lib/db/migrations/0007_learning_plans.sql



## ai-c4 graph shape


           ┌──────────────────┐
           │   orchestrator   │  (Opus 4.7 — hard reasoning)
           │ picks K topics   │
           └────────┬─────────┘
                    │ (Send API — dynamic fan-out)
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    ┌────────┬────────┬────────┐
    │worker 1│worker 2│worker K│   (Sonnet 4.6 — parallel)
    └────┬───┴────┬───┴────┬───┘
         └────────┼────────┘
                  ▼
           ┌──────────────┐
           │ synthesizer  │  (Opus 4.7 — merge / reconcile)
           └──────────────┘


  K is decided AT RUNTIME by the orchestrator.
  Workers WRITE topicPlans in parallel — explicit reducer required:
    reducer: (a, b) => [...a, ...b]















## ai-c5-final — HITL + persistence + Telegram

  Commit: ai-c5: add gap detection + HITL + telegram integration
          (capability: ai-gap-detection)


  What's added:

    openspec/specs/ai-gap-detection/spec.md      ← NEW canonical

    .claude/agents/
      ├── hitl-gate-reviewer.md                  ← NEW
      └── telegram-graph-reviewer.md             ← NEW

    .claude/hooks/budget-guard.js                ← NEW PreToolUse hook


    lib/ai/
      ├── graphs/gap-detection.graph.ts          ← stateful + interrupt()
      ├── prompts/gap-orchestrator.prompt.ts
      ├── prompts/gap-worker.prompt.ts
      ├── prompts/gap-synthesizer.prompt.ts
      └── schemas/gap-detection.schemas.ts


    lib/telegram/commands/
      ├── quiz.ts                                ← NEW: /quiz <topic>
      └── gaps.ts                                ← NEW: /gaps


    lib/jobs/gap-report-weekly.ts                ← NEW: weekly cron


    app/(app)/gaps/
      ├── page.tsx
      └── client.tsx

    app/api/ai/gaps/route.ts


    lib/db/schema.ts        ← + concept_struggles
                              (// human-approved: 2026-05-24)



## ai-c5 graph shape — the full picture


  loadHistory ──> orchestrator ──> conceptWorker (×K, parallel) ──>
                                       │
                                       ▼
                                  synthesizer ──>
                                       │
                                       ▼
                                  ┌──────────┐
                                  │ INTERRUPT│ ← "Save this report?"
                                  └────┬─────┘
                                       │ (resume with Command)
                                       ▼
                                    commit ──> END


  PostgresSaver checkpointer:
    - state persists across the interrupt
    - user can approve days later — graph resumes correctly


  Telegram bot now calls the same graphs:
    /quiz <topic>  →  quizQuestionGraph.invoke(...)
    /gaps          →  gapDetectionGraph.stream(...)


  ONE orchestration layer; multiple UIs (web + Telegram).















## 5B-Live: live LangGraph stream

  Stay on ai-c5-final.


  ┌────────────────────────────────────────────────────────────────┐
  │  Tab 1: http://localhost:3000/quiz                             │
  │    Click "Start quiz on Distributed Systems Fundamentals"      │
  │    Watch the terminal — node-by-node graph events stream.      │
  │    Question appears. Pick WRONG answer (choice C).             │
  │    Watch grader (instant) + explainer (streamed).              │
  │    Explanation appears.                                        │
  │                                                                │
  │  → THE DELIBERATE FAILURE                                      │
  │    Edit lib/ai/prompts/quiz-explainer.prompt.ts                │
  │    Change "...MUST respond with JSON..."                       │
  │    To     "...Respond in prose."                               │
  │    Save. Re-run.                                               │
  │                                                                │
  │    Watch terminal:                                             │
  │      node=explainer status=schema_validation_failed            │
  │      middleware: tool_retry: retrying (attempt 2 of 3)         │
  │      node=explainer status=completed (recovered)               │
  │                                                                │
  │  → THE LANGSMITH TRACE                                         │
  │    Switch to Tab 2 (LangSmith).                                │
  │    Click into the most recent run.                             │
  │    Show the tree: grader · explainer (with retry).             │
  │    Click the explainer LLM span — exact prompt + response.     │
  └────────────────────────────────────────────────────────────────┘


  The user did not see the failure.
  The framework caught it. Retried. Recovered.

  Trust the schema. Not the prose.















## What you just saw

  Six checkpoints. One repo. One harness. Five graphs.

  ai-c0  →  framework wired in BEFORE any feature
  ai-c1  →  sequential pipeline (companion)
  ai-c2  →  sequential multi-agent (quiz)
  ai-c3  →  router (front-door)
  ai-c4  →  orchestrator-worker (plan, parallel fan-out)
  ai-c5  →  HITL + persistence + Telegram (gap detection)


  Every feature: typed graph + Zod boundaries + checkpointer
                  + tracing + per-node model picking + tests.


  Plus 1 live run with deliberate failure + automatic recovery.















## Monday-morning call-to-action

  This week, on your own pet project:

  1. Pick your hardest AI feature. Sketch its GRAPH on paper.
     Nodes. Edges. State fields. Boundaries with Zod schemas.

  2. Install LangChain + LangGraph + your provider package.
     Wire a PostgresSaver to your existing database.

  3. Implement the simplest possible version of the graph.
     Start with a sequential pipeline. Add agency only where
     a workflow can't do the job.

  4. Add ONE structured-output boundary. Make the next-stage
     agent assume the previous stage's typed output.

  5. Add tracing (LangSmith env vars). Look at one trace.
     You will already see something to fix.

  6. THEN add HITL on consequential actions. Then evals.


  Don't try to build everything at once. Ship the smallest
  possible graph; then add layers.















## The quality bar for your capstone

  Every AI feature you ship must be:
    - a typed GRAPH (not a free-form chat loop)
    - with Zod schemas at every node boundary
    - persisted via a checkpointer
    - traced (LangSmith or equivalent)
    - eval-ready (50-sample rubric per feature)
    - HITL-gated on consequential actions


  That's the bar. Beat it.


  The harness from Session 1 makes ALL OF THIS reviewable.
  Use it.
