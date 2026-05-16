# Part 4 — The chosen harness

## What we're using (and why we picked it)

  OpenSpec  (spec / workflow spine)
       +
  Claude Code native primitives  (verification layer)




## OpenSpec — the spec spine

  - Lightweight: a few commands, two folders
  - Tool-agnostic (works with 25+ agent CLIs)
  - Brownfield-capable
  - Open source, ~48K★, MIT, Linux Foundation-aligned

  The cycle: propose → apply → archive
  Specs live in your repo. Compounding source of truth.



## Claude Code primitives — the verification layer

  - .claude/skills/          capability bundles (auto-loaded by description)
  - .claude/agents/          specialized reviewers with isolated context
  - .claude/hooks/           deterministic gates (PostToolUse, PreToolUse, Stop)
  - .claude/settings.json    wires it all together

  These cover the four verification layers from Part 3:
  mechanical · agentic · behavioral · human-gate.




## Honest split (the framing senior devs respect)

  The OpenSpec layer TRAVELS — works in Cursor, Codex CLI, Cline, etc.
  The Claude Code primitive layer is TOOL-SPECIFIC.


  Adopt OpenSpec wherever you go. Re-implement the verification
  layer in your chosen CLI. We don't paper over that split —
  we name it explicitly.




















## The bad approach (what most people start with)

  A single CLAUDE.md or AGENTS.md file in the repo root.
  Maybe a few hundred lines. Maybe a thousand.

  It works at first. Then it doesn't.

    - No spec for the system itself — only conventions
    - No change discipline — no propose/apply/archive
    - No versioned history of decisions
    - Compounds into a 3K-line "everything we ever learned" dump
    - Token cost: loaded every session, every turn

  → This is the COUNTER-EXAMPLE. The harness in our demo is
    built to do better. AGENTS.md / CLAUDE.md belongs as
    ONE LAYER of the harness, not the whole thing.



## The next-layer upgrade (when you outgrow OpenSpec alone)

  beads (Steve Yegge) — a Git-backed task graph and
  decision memory for agents. The "what are we doing"
  graph that lives outside the spec.

  Pet projects don't need it. Real long-horizon work does.
  We MENTION it. We DON'T demo it.




















# Part 5A — The demo project

## Ilm AI — Session Demo Edition

  What it is: a personal learning companion. You upload
  your own study materials (PDFs, notes, articles), organize
  them into collections, and the app helps you actually
  retain what you read — daily Telegram reminders, streak
  tracking, and (in the full capstone) AI chat, quizzes,
  and gap detection grounded in your own uploads.

  Demo edition = the non-AI core of YOUR OWN capstone —
  auth, materials library, Stripe subscription, Telegram bot.
  You add the AI features (RAG, agents, learning plans)
  on top during the rest of the incubator.



## At a glance

  Stack:    Next.js + Node.js + Postgres + S3 + Stripe + Telegram
  Scope:    4 features — Auth · Materials · Subscription · Telegram bot
  Branches: greenfield (built with OpenSpec) + brownfield (stripped)

  See project-spec.md for full specification.



## The repo at a glance

  ilm-ai-demo/
  ├── .claude/         ← Claude Code harness layer
  ├── openspec/        ← OpenSpec spec layer
  ├── app/             ← Next.js App Router
  ├── lib/             ← business logic
  ├── docker/          ← Docker Compose (postgres + minio)
  ├── tests/           ← Playwright + Vitest
  ├── AGENTS.md        ← cross-tool baseline (not standalone)
  ├── package.json
  └── README.md

  Branch 1 walks commit by commit — c0-scaffold → c5-final.




















# Part 5B — Branch 1 walkthrough (greenfield)

## Six checkpoints. One feature at a time.

  c0-scaffold      → harness wired in BEFORE any feature
  c1-auth          → user auth + profiles
  c2-materials     → personal materials library
  c3-subscription  → Stripe subscription & billing
  c4-telegram      → Telegram bot integration
  c5-final         → all 4 features shipped, all archived

  Switched live via `git checkout <branch>`.
  No live typing — every commit is pre-staged.




















## C0 — Initial scaffold + Claude primitives + OpenSpec

`git checkout c0-scaffold`

## What's in the commit

  ilm-ai-demo/
  ├── .claude/
  │   ├── settings.json           ← hooks + permissions
  │   ├── agents/                 ← (empty for now)
  │   ├── skills/                 ← OpenSpec workflow skills (from `openspec init`)
  │   │   ├── openspec-propose/SKILL.md
  │   │   ├── openspec-explore/SKILL.md
  │   │   ├── openspec-apply-change/SKILL.md
  │   │   └── openspec-archive-change/SKILL.md
  │   ├── commands/
  │   │   └── opsx/               ← OpenSpec slash commands (from `openspec init`)
  │   │       ├── propose.md
  │   │       ├── explore.md
  │   │       ├── apply.md
  │   │       └── archive.md
  │   └── hooks/                  ← (empty for now)
  ├── openspec/
  │   ├── config.yaml             ← project context + rules
  │   ├── specs/                  ← (empty — no shipped capabilities yet)
  │   └── changes/                ← (empty for now)
  ├── AGENTS.md                   ← cross-tool baseline (thin pointer)
  ├── app/                        ← scaffold home only (no links by design)
  ├── lib/db/schema.ts            ← empty drizzle schema
  ├── docker/docker-compose.yml   ← postgres + minio (no Redis)
  └── package.json




















## C0 — openspec/config.yaml (the project's context)

  schema: spec-driven

  context: |
    Project: Ilm AI Session Demo Edition
    Stack: Next.js 16, Node.js 24, PostgreSQL 18, S3-compatible
           storage, Stripe billing, Telegram via grammY,
           node-cron for scheduled jobs (in-process, no Redis).
    Architecture:
      - app/ contains route handlers (Next.js App Router)
      - lib/ contains business logic — auth/, storage/,
        stripe/, telegram/, dal/
      - lib/dal/ is the Data Access Layer —
        EVERY query MUST scope by session.userId
      - Drizzle ORM; Argon2id for password hashing
    Privacy: all user data is per-user private

  rules:
    proposal:
      - Include rollback plan for any change that touches data
      - State concrete success criteria
    specs:
      - Use RFC 2119 keywords (MUST, SHALL, SHOULD, MAY)
      - Use Given/When/Then format for scenarios
    tasks:
      - Group by phase (schema, implementation, tests, verification)
      - Number hierarchically (1.1, 1.2, 2.1...)
      - Follow existing patterns in lib/; run the relevant
        reviewer sub-agent before considering a task done

  Loaded by the agent on every OpenSpec command.
  A few dozen lines. Not a wiki dump.




















## C0 — .claude/settings.json (the harness wiring)

  {
    "permissions": {
      "deny": [
        "Bash(drizzle-kit push *)",
        "Bash(prisma db push *)",
        "Bash(git push --force *)",
        "Bash(aws s3 rm *)",
        "Bash(stripe charges *)"
      ]
    },
    "hooks": {
      "PreToolUse":  [Edit|MultiEdit|Write → guard-sensitive.js],
      "PostToolUse": [Edit|MultiEdit|Write → quality-check.js],
      "Stop":        [pnpm typecheck && pnpm lint && pnpm test:unit]
    }
  }


  permissions.deny    → Claude CANNOT run these. Not "won't" — cannot.
  PreToolUse hook     → blocks edits to .env / schema / webhook routes
  PostToolUse hook    → prettier + tsc + eslint + related tests
  Stop hook           → full quality gate at end of every turn



## C0 — AGENTS.md (8 lines, pointer-style)

  # Project agent guidance

  This project uses OpenSpec for spec discipline. Source of
  truth for *what the system does* lives in `openspec/specs/`.
  Source of truth for *how we work* lives in `openspec/config.yaml`.

  When making changes, follow the OpenSpec workflow:
    /opsx:propose  →  /opsx:apply  →  /opsx:archive

  Tools: pnpm typecheck · pnpm lint · pnpm test:unit · pnpm test:e2e


  This is what AGENTS.md SHOULD be: thin pointer, not a wiki.




















## C1 — Feature 1: Auth & user profiles

`git checkout c1-auth`

Commit: c1: add user auth (propose/apply/archive cycle 1 —
                            capability: user-auth)

## What's incrementally new

  openspec/
  ├── changes/archive/
  │   └── 2026-04-18-add-user-auth/      ← change history preserved
  │       ├── proposal.md
  │       ├── design.md
  │       ├── tasks.md
  │       └── specs/user-auth/spec.md     ← delta spec
  └── specs/
      └── user-auth/spec.md               ← canonical capability spec

  .claude/agents/
  ├── security-auditor.md                 ← NEW reviewer
  ├── oauth-flow-reviewer.md              ← NEW reviewer
  └── dal-isolation-reviewer.md           ← NEW reviewer

  app/
  ├── page.tsx                            ← REAL landing page now
  ├── error.tsx · not-found.tsx           ← global error + styled 404
  ├── icon.svg                            ← brand favicon
  ├── (app)/layout.tsx + nav.tsx          ← shared nav (Profile · Sign out)
  ├── (app)/profile/loading.tsx           ← route-scoped loading UI
  ├── (auth)/login + signup
  └── api/auth/[...nextauth]/route.ts

  lib/
  ├── auth.ts · auth/password.ts · auth/schemas.ts
  ├── config/integrations.ts              ← graceful demo-mode predicate
  ├── dal/users.ts · dal/sessions.ts      ← scoped by session.userId
  └── db/schema.ts + migrations/0001_user_auth.sql

  middleware.ts                           ← protect /(app)/*

  tests/unit + tests/e2e/auth.spec.ts     ← Playwright




















## C1 — the proposal (scope discipline made visible)

  # Proposal: add-user-auth

  ## Intent
  Enable users to sign up, sign in, and manage profile data so
  that the rest of the application has a notion of "the
  current user."

  ## Scope
  **In scope:**
    - Email/password sign-up + login
    - Google OAuth sign-in
    - JWT session in HttpOnly cookies
    - Profile page (name, email, learning goal, target date)
    - Private-per-user data isolation enforced via DAL

  **Out of scope:**
    - Email verification (deferred to next change)
    - Password reset flow (deferred to next change)
    - 2FA (deferred)

  ## Rollback plan
  - Drop tables: users, accounts, sessions, verification_tokens
  - Remove middleware and auth lib
  - No data loss risk pre-launch


  "Out of scope" is as loud as "in scope."
  This is how you stop an agent's scope creep.




















## C1 — the spec delta (RFC 2119 + Given/When/Then)

  ## ADDED Requirements

  ### Requirement: Email/Password Sign-Up
  The system MUST allow a visitor to create an account using
  email and password, hashing the password with Argon2id
  (m=19456, t=2, p=1) before storage.

  #### Scenario: Successful signup
  - WHEN a visitor submits a valid email and a password
    meeting policy (≥10 chars)
  - THEN a User row is created, an HttpOnly+Secure session
    cookie is set, and the response redirects to /profile

  #### Scenario: Duplicate email
  - WHEN signup is attempted with an email that already exists
  - THEN respond with 409 and a generic "email already
    registered" message that does NOT leak whether the email
    belongs to a Google-OAuth-only account

  ### Requirement: Per-User Data Isolation
  All data-access functions in lib/dal/ MUST require a userId
  parameter sourced from the session, not from request input.
  Cross-user access MUST return 404 (not 403) so existence is
  not leaked.


  Format enforced by `rules.specs` in config.yaml.




















## C1 — the security-auditor sub-agent

  ---
  name: security-auditor
  description: Use when changes touch auth, sessions, cookies,
    password handling, or any API route reading user identity.
    Reviews for OWASP Top 10 issues. Read-only.
  tools: Read, Grep, Glob
  model: opus
  ---

  You are a security auditor for code that handles auth.

  For each diff:
    1. Identify what auth-related code changed.
    2. Run the OWASP Top 10 checklist against it.
    3. Specifically verify:
       - Passwords hashed with Argon2id or bcrypt cost ≥12
         (NEVER SHA, NEVER plain)
       - JWTs have an `exp` claim
       - Cookies are HttpOnly + Secure + SameSite=Strict
       - No secrets are logged
       - Login endpoints have rate limiting
       - DAL queries scope by session.userId, not request input
       - Cross-user errors return 404, not 403
    4. Output: CRITICAL / HIGH / MEDIUM / LOW with line refs.


  tools: Read, Grep, Glob   → cannot edit. Reviewer, not writer.
  Trust mechanism: specialization makes verification possible.



## C1 — verification layers, all four wired

  Mechanical   Vitest unit + tsc + lint via hooks
  Agentic      security-auditor + oauth-flow + dal-isolation reviewers
  Behavioral   Playwright E2E (login → edit profile → logout)
  Human gate   schema.ts edit blocked by guard-sensitive
               (requires explicit human-approved marker)



## C1 — the app is navigable from feature one

  app/page.tsx                  real landing — Sign up / Log in CTAs
  app/(app)/layout.tsx + nav.tsx  shared shell + nav (Profile · Sign out)
  app/error.tsx · not-found.tsx   global error + styled 404 UI
  app/(app)/profile/loading.tsx   route-scoped loading UI

  The nav GROWS A LINK per feature. Each checkpoint is a
  coherent, clickable demo of what's shipped so far.
  Not a backend with no front door.




















## C2 — Feature 2: Personal materials library

`git checkout c2-materials`

Commit: c2: add materials library (cycle 2 — capability:
                                   materials-library)

## What's new

  openspec/
  ├── changes/archive/2026-04-22-add-materials-library/
  │   └── proposal · design · tasks · specs/materials-library/spec.md
  └── specs/materials-library/spec.md          ← NEW canonical spec

  .claude/
  ├── agents/file-upload-security-reviewer.md  ← NEW
  └── skills/upload-handling/                  ← NEW project skill
      ├── SKILL.md
      └── references/presign-policy.md

  app/
  ├── page.tsx                                 ← 2 feature cards now
  ├── (app)/nav.tsx                            ← gains a Library link
  └── (app)/library/
      ├── page.tsx
      ├── collections-panel.tsx                ← empty states
      ├── material-list.tsx                    ← empty states
      ├── upload-panel.tsx
      └── [collectionId]/
          ├── page.tsx
          └── not-found.tsx                    ← segment-scoped 404
                                                 (cross-user → 404, never 403)
  app/api/uploads/presign/route.ts             ← presigned POST endpoint

  lib/storage/
  ├── s3.ts · presign.ts                       ← buildPresignedPost (POST)
  ├── validate.ts                              ← magic-byte check
  └── keys.ts                                  ← UUID keys (never user-supplied)
  lib/dal/materials.ts · collections.ts

  tests/unit/validate.test.ts                  ← golden files: real + spoofed
  tests/e2e/materials.spec.ts                  ← spoofed extension rejected
  tests/e2e/responsive.spec.ts                 ← mobile-viewport nav check



## Two things to point at

  1. The specs/ directory is COMPOUNDING.
     user-auth + materials-library now. After C3, C4 →
     four capabilities, four folders, one spec.md each.
     System documentation, built incrementally,
     kept in sync by propose/apply/archive.

  2. A new primitive: the project-local skill.




















## C2 — .claude/skills/upload-handling/SKILL.md

  ---
  name: upload-handling
  description: Project conventions for handling user file
    uploads — presigned POST, magic-byte validation, UUID
    keys, MIME allowlist. Use when implementing or modifying
    any file-upload code path.
  user-invocable: false
  paths: lib/storage/**, app/api/uploads/**
  ---

  ## Upload conventions for this project

  1. Always use presigned POST, never presigned PUT.
     PUT cannot enforce file size; POST policy conditions are
     validated server-side by S3.

  2. Allowed MIME types: application/pdf,
     application/vnd.openxmlformats-officedocument.
     wordprocessingml.document, text/plain.

  3. Max file size: 25 MB. Enforce in the POST policy
     AND server-side.

  4. Magic-byte validation is REQUIRED after upload.
     Content-Type header is client-supplied and trivially
     spoofed. Use the `file-type` package.

  5. Object keys are UUIDs, NEVER user-supplied filenames.
     Format: users/<userId>/<materialUUID>.

  6. Bucket is private. Serve downloads via a server-action
     that verifies session.userId, returns a 5-min
     presigned GET. Content-Disposition: attachment.


  Skills = KNOWLEDGE. Sub-agents = REVIEWERS.
  user-invocable: false → hidden from /menu; auto-loaded
  when description + paths match the work at hand.

  Auto-load is the default for every skill. This is
  LangChain's `write` lever — saved outside the window,
  pulled in only when needed.




















## C2 — the presign code (10 lines, doctrine-shaped)

  import { randomUUID } from "node:crypto";
  import { createPresignedPost } from "@aws-sdk/s3-presigned-post";
  import { s3 } from "./s3";

  const ALLOWED = new Set([
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
  ]);

  export async function buildUploadUrl(userId: string, mime: string) {
    if (!ALLOWED.has(mime)) throw new Error("unsupported type");
    const materialId = randomUUID();
    const key = `users/${userId}/${materialId}`;
    return createPresignedPost(s3, {
      Bucket: process.env.S3_BUCKET!,
      Key: key,
      Conditions: [
        ["content-length-range", 1, 25 * 1024 * 1024],
        ["eq", "$Content-Type", mime],
      ],
      Expires: 300,
    });
  }


  Content-length-range + Content-Type conditions enforced by S3.
  Magic-byte check runs server-side after upload (validate.ts).
  Golden-file unit test proves spoofed `.pdf` with PE headers rejected.




















## C3 — Feature 3: Stripe subscription & billing

`git checkout c3-subscription`

Commit: c3: add stripe subscription (cycle 3 —
                                     capability: subscriptions)

The highest-stakes feature in the demo.
This is where agentic verification earns its rent.

## What Stripe itself documents agents get wrong

  - Missing signature verification
  - Parsing JSON BEFORE verifying signature
  - 4xx on unknown events  →  Stripe retry storms
  - No idempotency on event processing


## What's new

  openspec/
  ├── changes/archive/2026-04-28-add-subscriptions/
  └── specs/subscriptions/spec.md              ← NEW

  .claude/
  ├── agents/
  │   ├── webhook-security-reviewer.md         ← NEW
  │   ├── webhook-idempotency-reviewer.md      ← NEW
  │   └── stripe-state-reviewer.md             ← NEW
  └── skills/stripe-webhooks/                  ← NEW project skill

  app/
  ├── page.tsx                                 ← 3 feature cards
  ├── (app)/nav.tsx                            ← gains Billing link
  └── (app)/billing/
      ├── page.tsx
      ├── billing-actions.tsx                  ← graceful demo-mode
      ├── billing-history.tsx                  ← in-app history (honest empty)
      └── loading.tsx
  app/api/stripe/
  ├── checkout/route.ts                        ← clean 503 on placeholder keys
  ├── portal/route.ts                          ← clean 503 on placeholder keys
  └── webhook/route.ts                         ← THE critical route

  lib/stripe/
  ├── client.ts · products.ts · billing-history.ts
  └── webhook/
      ├── verify.ts                            ← constructEvent on req.text()
      ├── idempotency.ts                       ← insert-then-process
      └── handlers/{checkoutCompleted,
                   subscriptionUpdated,
                   subscriptionDeleted,
                   paymentFailed}.ts
  lib/dal/subscription.ts                      ← getActiveTier(userId)

  CODEOWNERS                                   ← NEW: webhook route human gate

  tests/unit/webhook-verify · webhook-idempotency
  tests/scripts/test-webhook-replay.sh         ← double-deliver test




















## C3 — the idempotency requirement (spec-level guarantee)

  ### Requirement: Idempotent Event Processing
  The system MUST process each delivered webhook event at
  most once via a UNIQUE constraint on stripe_events.event_id.
  Re-delivery of an event the system has already processed
  MUST return 200 without re-running side effects.

  #### Scenario: Duplicate delivery
  - GIVEN a webhook event with event.id "evt_abc123" has
    been processed and committed
  - WHEN Stripe re-delivers the same event
  - THEN the handler returns 200, no side effect runs,
    no duplicate row is created

  #### Scenario: Crash between insert and side effect
  - GIVEN the handler has inserted into stripe_events but
    crashed before the side effect
  - WHEN Stripe re-delivers the event
  - THEN the handler detects the existing row with
    status='queued' and re-runs the side effect




















## C3 — the webhook-security-reviewer sub-agent

  ---
  name: webhook-security-reviewer
  description: Use when a change touches /api/stripe/webhook,
    /api/telegram/webhook, or any external webhook receiver.
    Reviews signature verification, raw-body handling,
    idempotency, and HTTP status codes. Read-only.
  tools: Read, Grep, Glob
  model: opus
  ---

  For each diff that touches a webhook route:

  1. Confirm the raw request body is read via `req.text()`
     (App Router) — NOT `req.json()`. JSON parsing changes
     whitespace and breaks signature verification.

  2. Confirm signature is verified via the provider SDK
     (`stripe.webhooks.constructEvent` for Stripe) —
     NEVER hand-rolled HMAC.

  3. Confirm the webhook secret comes from process.env,
     NEVER a literal.

  4. Confirm there is a UNIQUE constraint on the event_id
     table (idempotency).

  5. Confirm unknown event types return 200, NOT 4xx —
     Stripe retries 4xx.

  6. Confirm business logic and the idempotency insert
     are in the SAME transaction.

  7. Confirm subscription state in handlers is REFETCHED
     from the Stripe API, not trusted from payload
     (defends against out-of-order delivery).

  Output as: APPROVE or REQUEST_CHANGES with line-specific
  feedback.


  Seven specific checks. Read-only. Runs against every diff
  that touches a webhook route. The spec demands the
  guarantee — the reviewer enforces it.




















## C3 — the handler itself (20 lines)

  export async function POST(req: NextRequest) {
    const sig = req.headers.get("stripe-signature");
    if (!sig) return new NextResponse("missing signature",
                                      { status: 400 });

    const rawBody = await req.text();   // NEVER req.json()

    let event;
    try {
      event = stripe.webhooks.constructEvent(
        rawBody, sig, process.env.STRIPE_WEBHOOK_SECRET!);
    } catch (err) {
      return new NextResponse("invalid signature",
                              { status: 400 });
    }

    const isNew = await recordEvent(event.id, event.type);
    if (!isNew) return NextResponse.json({ received: true });
      // ↑ idempotent replay — unique-constraint short-circuit

    try {
      await dispatch(event);
    } catch (err) {
      console.error("handler failed", { id: event.id, err });
      // log; do NOT 5xx unless we want a retry storm
    }

    return NextResponse.json({ received: true });
  }



## C3 — verification layers, all four wired

  Mechanical   webhook-verify + webhook-idempotency unit tests
  Agentic      webhook-security + webhook-idempotency
               + stripe-state reviewers
  Behavioral   test-webhook-replay.sh fires all 4 event types,
               double-delivers each via Stripe CLI
  Human gate   CODEOWNERS on app/api/stripe/webhook/route.ts
               (first appears at C3, with the route it protects)



## C3 — the UI keeps pace

  nav             gains a Billing link
  page.tsx        gains the subscription card (3 of 4 now)
  (app)/billing/  current plan + in-app history + upgrade controls

  On placeholder Stripe keys, billing runs in honest DEMO MODE:
    - controls visibly disabled
    - checkout + portal routes return clean 503
    - history view shows truthful empty/demo state

  The harness DEGRADES GRACEFULLY instead of throwing
  an opaque error mid-demo.




















## C4 — Feature 4: Telegram bot integration

`git checkout c4-telegram`

Commit: c4: add telegram bot (cycle 4 — capability: telegram-bot)

## What's new (highlights)

  openspec/
  ├── changes/archive/2026-05-02-add-telegram-bot/
  └── specs/telegram-bot/spec.md             ← NEW

  .claude/
  ├── agents/
  │   ├── telegram-security-reviewer.md      ← NEW
  │   └── job-reliability-reviewer.md        ← NEW: cron-job reliability
  │                                            (idempotent bodies, overlap
  │                                             guard, timezone schedules,
  │                                             failure logging)
  └── hooks/
      └── token-leak-check.js                ← NEW: scans diffs for bot-token regex

  app/
  ├── page.tsx                               ← 4 feature cards (all)
  ├── (app)/profile/telegram-section.tsx     ← NEW: in-app linkage UI
  │                                            (generate code · reminder time
  │                                             · linked state · unlink)
  └── api/telegram/webhook/route.ts

  instrumentation.ts                         ← NEW: register() starts
                                               node-cron at boot
                                               (nodejs-runtime guarded)

  lib/telegram/
  ├── bot.ts                                 ← grammY Bot instance
  ├── linkCode.ts                            ← mintLinkCode (wires UI above)
  ├── commands/start.ts · status.ts          ← /start <code> linkage
  └── middleware/rateLimit.ts
  lib/jobs/
  ├── scheduler.ts                           ← node-cron schedules
  ├── reminder.ts                            ← daily reminder
  └── streak.ts                              ← streak check




















## C4 — the one-time hashed link-code requirement

  ### Requirement: One-Time Hashed Link Codes
  Account linkage MUST use one-time codes that are stored
  hashed (SHA-256), TTL ≤ 300 seconds, max 5 verification
  attempts before the code is invalidated.

  #### Scenario: Successful linkage
  - WHEN the bot receives /start with a valid unexpired
    code payload
  - THEN the user's telegram_chat_id is set and the
    code is invalidated

  #### Scenario: Expired code
  - WHEN the bot receives /start with a payload that has
    exceeded TTL
  - THEN the bot replies "this link expired, generate a
    new one" and increments no attempt counter
    (no oracle for valid-but-expired vs invalid)



## C4 — .claude/hooks/token-leak-check.js

  #!/usr/bin/env node
  // PreToolUse hook: block edits that introduce Telegram bot tokens.
  // Format: <bot_id>:<35 char base64-ish>
  const TOKEN_RE = /\b\d{8,10}:[A-Za-z0-9_-]{35}\b/;

  const stdin = await new Response(process.stdin).text();
  const { tool_input } = JSON.parse(stdin);

  const content = tool_input?.content
                ?? tool_input?.new_string ?? "";

  if (TOKEN_RE.test(content)) {
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason:
          "Detected something that looks like a Telegram " +
          "bot token. Use process.env.TELEGRAM_BOT_TOKEN " +
          "instead."
      }
    }));
    process.exit(0);
  }
  process.exit(0);


  Mechanical verification at its purest:
    - Not a model judgment
    - Not "the agent decided"
    - A regex script returning structured `deny` JSON
    - Deterministic. Cannot be argued with.

  Bot-token leaks are a documented attack class.
  This hook makes them a STRUCTURAL impossibility.



## C4 — verification layers, all four wired

  Mechanical   token-leak-check.js + unit tests on linkage flow
  Agentic      telegram-security + job-reliability reviewers
  Behavioral   integration test via telegram-test-api (in-process)
  Human gate   setWebhook URL changes require approval



## C4 — F4's user-facing half ships here

  app/(app)/profile/telegram-section.tsx
      generate one-time code · pick reminder time
      · see linked state · unlink
      (wires up lib/telegram/linkCode.ts's mintLinkCode)

  instrumentation.ts
      Next.js boot hook → register() starts node-cron once
      (nodejs-runtime guarded → daily reminder + streak jobs
       actually run)

  The spec's linkage flow can be PERFORMED BY CLICKING.




















## C5 — Final state recap

`git checkout c5-final`

Commit: c5: branch-1 final state (all 4 features shipped,
                                  all changes archived)

## openspec/

  openspec/
  ├── config.yaml
  ├── specs/
  │   ├── user-auth/spec.md
  │   ├── materials-library/spec.md
  │   ├── subscriptions/spec.md
  │   └── telegram-bot/spec.md
  └── changes/
      └── archive/
          ├── 2026-04-18-add-user-auth/
          ├── 2026-04-22-add-materials-library/
          ├── 2026-04-28-add-subscriptions/
          └── 2026-05-02-add-telegram-bot/


## .claude/

  .claude/
  ├── settings.json
  ├── agents/                          ← 9 sub-agent reviewers
  │   ├── security-auditor.md
  │   ├── oauth-flow-reviewer.md
  │   ├── dal-isolation-reviewer.md
  │   ├── file-upload-security-reviewer.md
  │   ├── webhook-security-reviewer.md
  │   ├── webhook-idempotency-reviewer.md
  │   ├── stripe-state-reviewer.md
  │   ├── telegram-security-reviewer.md
  │   └── job-reliability-reviewer.md
  ├── skills/                          ← 4 OpenSpec + 2 project
  │   ├── openspec-propose/SKILL.md
  │   ├── openspec-explore/SKILL.md
  │   ├── openspec-apply-change/SKILL.md
  │   ├── openspec-archive-change/SKILL.md
  │   ├── upload-handling/             ← project skill
  │   └── stripe-webhooks/             ← project skill
  ├── hooks/                           ← 3 hooks
  │   ├── guard-sensitive.js
  │   ├── quality-check.js
  │   └── token-leak-check.js
  └── commands/
      └── opsx/
          ├── propose.md
          ├── explore.md
          ├── apply.md
          └── archive.md



## What's standing now

  4 shipped capabilities       each documented in openspec/specs/
  4 archived changes           each with proposal · design · tasks · deltas
  9 sub-agents                 reviewers, all read-only
  6 skills                     4 OpenSpec workflow + 2 project
  3 hooks                      guard-sensitive · quality-check · token-leak

  A new engineer joining tomorrow can read the specs to
  understand what the system DOES, and read the archive
  to understand WHY decisions were made and HOW they were
  validated.

  None of these primitives are exotic — they're all standard
  Claude Code + OpenSpec. The discipline is in COMPOSING them.

  And the app itself is a complete, clickable product:
  landing lists all 4 features · nav carries Library · Profile
  · Billing · Sign out · every route has loading / error /
  empty states. First-time visitor signs up, lands, uses
  every feature by clicking. That's the bar.




















# Part 5B-Live — Live cycle, end to end

## What the audience just saw was steady state.
## Now: the WORKFLOW. Monday morning. Live.

## The feature

  Add a "favorite" flag to materials.
  A user can star a material in their library.
  The star persists. Only the owner can toggle it.

  Why this feature:
    - Small enough to apply live in 5–7 minutes
    - Touches the schema   → guard-sensitive hook fires
    - Touches the DAL      → dal-isolation-reviewer fires
    - Visible payoff       → click a star, it sticks
    - EXTENDS materials-library    → ## MODIFIED Requirements
                                    delta pattern, not just ADDED




















## Step 1 — Propose (~60 seconds)

  /opsx:propose add-material-favorites

What appears:

  openspec/changes/add-material-favorites/
  ├── proposal.md
  ├── tasks.md
  └── specs/materials-library/spec.md   ← delta (MODIFIED + ADDED)

(design.md is generated only when a change needs it —
 a one-column favorites flag typically won't produce one.)


The proposal (open quickly):

  # Proposal: add-material-favorites

  ## Intent
  Let users mark materials as favorites for quick access.

  ## Scope
  **In scope:**
    - Add `is_favorite` boolean column on materials
    - DAL function: toggleFavorite(userId, materialId)
    - API route: POST /api/materials/[id]/favorite
    - UI: star toggle on library list

  **Out of scope:**
    - Favorite collections (separate change)
    - Sort/filter by favorite (separate change)

  ## Rollback plan
  - Drop column materials.is_favorite
    (no data loss in pre-launch state)




















## Step 2 — Apply (~3–5 minutes, the bulk)

  /opsx:apply add-material-favorites

The agent works through tasks.md. Watch two load-bearing beats:


## Beat 1 — guard-sensitive hook fires on the schema edit

  Migration edit attempt on lib/db/schema.ts
        ↓
  PreToolUse hook reads the edit payload
        ↓
  No `// human-approved: 2026-05-16` marker found
        ↓
  Hook returns deny → edit blocked
        ↓
  Agent reads rejection reason
        ↓
  Agent re-attempts with the marker → edit succeeds


  Mechanical verification, live. Hook stops a real class
  of mistakes — silent schema drift. The agent cannot skip
  this. Not "usually." Never.



## Beat 2 — dal-isolation-reviewer reviews toggleFavorite

  "Let's have the dal-isolation-reviewer check this."

  Read-only sub-agent (tools: Read, Grep, Glob).
  Cannot edit. Reviews the new DAL function to confirm
  it scopes by session.userId, not request input.

  Approves. Agent continues.


## Remaining apply steps (narrate lightly)

  - new API route at app/api/materials/[id]/favorite/route.ts
  - UI: star button added to app/(app)/library/page.tsx
  - unit test at tests/unit/dal-materials-favorite.test.ts
    proves non-owner cannot toggle
  - Stop hook runs full quality gate → tests pass



## Step 3 — Archive (~30 seconds)

  /opsx:archive add-material-favorites

What happens:

  delta in changes/add-material-favorites/specs/
            materials-library/spec.md
        ↓ merges into ↓
  openspec/specs/materials-library/spec.md

  change folder moves to
  changes/archive/2026-05-16-add-material-favorites/



## Step 4 — Final state

  - openspec/specs/materials-library/spec.md
    → new Requirement appended at the bottom
  - openspec/changes/archive/
    → five archived changes now (original four + today's)



## Five minutes ago this feature didn't exist.

  Now it's   specified · shipped · tested · verified · archived.

  That is the workflow.
  That is what every feature looks like.
  That is what you do for breakfast as an AI-driven engineer
  in 2026.




















# Part 5C — Brownfield onboarding

`git checkout branch-2-brownfield`

## The brownfield state

  Same project. Full feature set intact.
  Auth · materials · billing · Telegram bot — all working.

  But:
    - openspec/ directory is GONE — no specs, no changes, no config
    - .claude/ is UNCHANGED — agents, hooks, skills, settings still present
    - AGENTS.md exists but is generic / pre-OpenSpec style

  This is what a typical existing project looks like in May 2026.
  Tests, code, conventions — but no formal spec layer.
  Most of your work codebases look more like this than like Branch 1.

  Question: how do you adopt OpenSpec into this?
  Without rewriting history?




















## 5C.1 — Run `openspec init` live

  openspec init

Interactive wizard — three prompts:

  ┌──────────────────────────────┬──────────────────────────────┐
  │  Which AI tools to configure?│  Claude Code                 │
  │  Workflow profile?           │  core                        │
  │  Project config (config.yaml)│  Accept starter — edit later │
  └──────────────────────────────┴──────────────────────────────┘

Completes in under 1 second. Output:

  OpenSpec Setup Complete
  Created: Claude Code
  4 skills and 4 commands in .claude/
  Config: openspec/config.yaml (schema: spec-driven)

  Restart your IDE for slash commands to take effect.



## What `init` generates

  openspec/
  ├── config.yaml             ← starter — needs human edits
  ├── specs/                  ← empty
  └── changes/
      └── archive/            ← empty (pre-created)

  .claude/
  ├── skills/
  │   ├── openspec-propose/SKILL.md        ← NEW
  │   ├── openspec-explore/SKILL.md        ← NEW
  │   ├── openspec-apply-change/SKILL.md   ← NEW
  │   └── openspec-archive-change/SKILL.md ← NEW
  ├── commands/
  │   └── opsx/                            ← NEW (produces the /opsx: prefix)
  │       ├── propose.md
  │       ├── explore.md
  │       ├── apply.md
  │       └── archive.md
  └── (existing agents, hooks, settings UNCHANGED)


  Purely additive. Existing primitives untouched.

  Naming note: skill DIRECTORY names are openspec-* (e.g.
  openspec-apply-change), while the slash command stays
  /opsx:apply. Two different names for the two layers.

  The slash commands need an IDE reload to appear — that's
  what the "Restart your IDE" line is telling you. (For this
  demo, init was run ahead of time and Claude Code restarted,
  so /opsx:* is already live.)




















## 5C.2 — Edit config.yaml to teach OpenSpec the project

The init-generated starter has ONE live line plus commented
examples. We uncomment and fill in `context` (and optionally
`rules`) live:

  schema: spec-driven

  context: |
    Project: Ilm AI (production codebase, brownfield)
    Stack: Next.js 16, Node.js 24, PostgreSQL 18,
           S3-compatible storage, Stripe billing,
           Telegram via grammY, node-cron for scheduled jobs.
    Architecture: app/ for routes, lib/ for business logic,
                  lib/dal/ for queries.
    Existing capabilities (to formalize as specs over time):
      - user-auth         (in lib/auth/, app/(auth)/)
      - materials-library (in lib/storage/, app/api/uploads/)
      - subscriptions     (in lib/stripe/, app/api/stripe/)
      - telegram-bot      (in lib/telegram/, app/api/telegram/)

  rules:
    proposal:
      - Include rollback plan for any change touching data
    specs:
      - Use RFC 2119 keywords; Given/When/Then scenarios


  Existing capabilities listed — they exist IN CODE,
  not yet AS SPECS. That's the honest reality of brownfield:
  specs/ starts empty. You write specs AS YOU TOUCH THE CODE.
  Every new change, every refactor, every bug fix is the
  moment to formalize the spec for that capability.

  Don't try to spec everything at once.




















## 5C.3 — First brownfield change

  /opsx:propose add password reset flow

About a minute or two. Agent reads the auth code
(lib/auth/, app/(auth)/, lib/db/schema.ts) and writes:

  openspec/changes/add-password-reset/
  ├── .openspec.yaml
  ├── proposal.md
  ├── design.md              ← present: schema blocks tasks
  │                            on both design AND specs, so
  │                            propose generates design.md
  │                            to unblock tasks. For password
  │                            reset it's warranted anyway —
  │                            new email dependency, new data
  │                            model, enumeration concerns.
  ├── tasks.md
  └── specs/user-auth/spec.md   ← delta: ## ADDED Requirements
                                  (no prior canonical spec yet)


  When this change archives, the delta becomes the canonical
  spec for user-auth. From then on, future changes MODIFY
  or extend it.

  Five minutes ago: no spec layer.
  Now: spec layer + first change. From here on, every new
  feature goes through propose/apply/archive — same as Branch 1.



## Honest note on `/opsx:onboard`

  OpenSpec has an `/opsx:onboard` workflow.

  What it IS:    a guided ~15–20 min tutorial. Scans your
                 code to pick ONE small real task (a TODO,
                 missing error handling), then walks you
                 through one complete propose/apply/archive
                 cycle with narration.

  What it is NOT: a bulk spec generator. It does NOT generate
                  specs for every existing capability.

  One caveat:    `onboard` is NOT in the `core` profile we
                 installed — ships only with `custom`. Init
                 with `custom` if you want it in the menu.

  For brownfield: propose ONE CHANGE AT A TIME, the way we
  just did. Spec coverage grows incrementally. Don't wait,
  and don't try to spec everything at once.




















# Part 5D — Closing

## Recap of what you just saw

  Branch 1: greenfield. 4 features. Full propose/apply/archive
            each. 9 sub-agents, 3 hooks, 6 skills
            (4 OpenSpec workflow + 2 project).
            Specs compound. Changes archive.
            Verification is layered.

  Branch 2: brownfield. OpenSpec stripped.
            `openspec init` + edit config.yaml + first
            /opsx:propose.
            Five minutes from zero to a working harness
            on existing code.




















## Monday-morning call-to-action

  This week, on your own pet project:

    1. Decide on your agent CLI
       (Claude Code, Cursor, Codex, opencode, ...).

    2. Run `openspec init`.
       Edit config.yaml with your stack + conventions.

    3. Write ONE AGENTS.md.
       Short. Pointer-style. Not a wiki.

    4. Add ONE PostToolUse hook:
       prettier + lint + type-check.

    5. Pick your first feature.
       Run /opsx:propose. Walk it through.

    6. Add a reviewer sub-agent the FIRST time
       you find one type of mistake repeating.


  Don't try to set up everything before you ship anything.

  Ship the smallest possible harness. Ratchet from there.




















## The quality bar for your capstone

  The bar is what you just saw on Branch 1.

  Every PR you submit during this incubator should be:

    - Spec-backed
          propose/apply/archive on its OpenSpec change

    - Verified at all four layers
          mechanical · agentic · behavioral · human

    - Reviewable by a senior engineer
          without ever knowing AI wrote it


  That's the FLOOR.

  Beat it.
