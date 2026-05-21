# Project Requirements — AI Mentorship Program

> Every participant builds an AI app **individually** and documents the build in public.
> This document explains what we'd like you to share, how often, and in what format.

---

## Why we ask for this

We care about the **process**: how you think, where you get stuck, how you unstick yourself, and how consistently you ship. The diary + video format makes that process visible to your peers, your mentors, and to your future self.

Most reviewing in this program is **peer-led** — other participants read your diary and watch your Loom each week, and mentors spot-check. So you're really writing for someone who is _also_ building something hard right now.

If we can share your work, we can help you improve it. That's the whole point.

---

## 1. Project options

You may pick **one** of the following and stick with it for the duration of the program. Switching halfway makes it hard for whoever is reviewing you to follow the thread, so pick something you're genuinely excited to commit to.

### Option A — Ilm AI (default)

Build **Ilm AI**, the AI learning companion described in the [program README](./README.md#the-capstone-project-ilm-ai). This is the recommended path. The brief, milestones, and tech stack are already defined, so you can spend your energy on building rather than on scoping. If you're not sure which option to pick, pick this one.

### Option B — Your own startup idea

If you're already working on a startup or have a concrete product idea you want to push forward, you're welcome to use the program for that instead. The same rules apply — diary, Loom videos, with one extra responsibility: **you scope your own features**, because we don't know your project as well as you do. You're still expected to apply what mentors teach you throughout the program, to hit the same weekly milestones (see below), and to meet the [Final Deliverables](./README.md#final-deliverables) listed in the program README.

If you pick Option B, please write a short pitch in your repo's `README.md`: what it is, who it's for, what the first shippable slice looks like, and how you'll hit each of the four weekly milestones below. Your peers and mentors will review against that pitch, so it's worth taking 30 minutes to write it carefully.

### Shared milestones (both options)

Both options are held to the **same weekly milestones**, taken from the [program README](./README.md#project-milestones):

| Week                   | Milestone          | What to have working                                                                                                   |
| ---------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| Week 1 (after S1–S4)   | Foundation         | Auth working, file upload and processing pipeline running, basic RAG chat answering questions from uploaded documents  |
| Week 2 (after S5–S8)   | Core Features      | Quiz mode live, learning plan agent generating plans, Telegram bot sending reminders and running quizzes               |
| Week 3 (after S9–S11)  | Polish & Integrate | Knowledge gap detection running across sessions, payment flow integrated in test mode, UI complete and mobile-friendly |
| Week 4 (after S12–S14) | Ship It            | Deployed to production, CI/CD running on push, monitoring in place, 50 evaluation samples rated                        |

- **Option A (Ilm AI):** these are the literal features you build.
- **Option B (own startup):** treat these as **structural milestones**. Your product may not have a "quiz mode" or a "Telegram bot", but it should hit the equivalent stage at each point:
  - **Week 1 — Foundation:** auth, core data pipeline, smallest end-to-end slice of your product working.
  - **Week 2 — Core Features:** the two or three things your product is fundamentally for, working.
  - **Week 3 — Polish & Integrate:** the integrations that make it real (payments if relevant, UI complete, mobile-friendly).
  - **Week 4 — Ship It:** deployed to production, CI/CD on push, monitoring in place, evaluation pass on the AI parts.

If your Option B product genuinely doesn't have an analogue for one of the items (e.g. no payment flow because it's an internal tool), please write a short note in your README explaining what you're substituting and why.

For everyone, please also read the [Final Deliverables](./README.md#final-deliverables) and [Evaluation Rubric](./README.md#evaluation-rubric) in the program README — that's what your final demo is judged against.

---

## 2. GitHub repository

Please have **one GitHub URL** ready to be shared with us. There are two acceptable paths — pick the one that fits your situation.

### Path A — Public project repo (preferred)

If your project is **open and you're happy to share the code**, share the repo containing your application. The `diary/` folder (described below) lives inside this repo at the root.

```
your-project/
├── README.md
├── src/
├── ...
└── diary/          ← required
    ├── 2026-05-21.md
    └── 2026-05-23.md
```

### Path B — Private startup → separate diary repo

If you're building a startup and you'd rather not expose your codebase, that's completely fine. In that case, please create a **public GitHub repository** just for your diary. It doesn't need to contain any application code.

```
your-name-ai-mentorship/
├── README.md       ← your name and short description of what you are building
└── diary/          ← required
    ├── 2026-05-21.md
    └── 2026-05-23.md
```

Whichever path you pick, the only firm rule is: **the diary itself needs to be public**. If your peers and mentors can't read your progress, they can't follow along to assess and help.

---

## 3. Diary entries

### Location and naming

- All entries live inside the `diary/` folder.
- One markdown file per entry.
- File name format: `YYYY-MM-DD.md` (e.g. `2026-05-21.md`).

### Cadence

| Requirement      | Rule                                                                                                            |
| ---------------- | --------------------------------------------------------------------------------------------------------------- |
| **Hard minimum** | **2 entries per week**, every week starting from week 2 (so 4 weeks × 2 = 8 entries minimum across the program) |
| **Stretch**      | 3 or 4 entries per week is wonderful if you can sustain it                                                      |
| **Ceiling**      | 1 entry per day                                                                                                 |

### What every entry should contain

Each markdown file should include these five sections, in this order:

1. **What was done** — concrete tasks finished or progress made since the previous entry, what you applied from the sessions you learnt from mentors
2. **Problems encountered** — bugs, blockers, things that didn't work, things you didn't understand. These are the most useful sections for peers to read, be open.
3. **Solutions (if any)** — how you got past the problem, or why it's still open. "Still stuck" is a perfectly valid answer.
4. **Next plan** — what you intend to do before the next entry.
5. **Time spent** — total hours since the previous entry (a rough number is fine, e.g. _~6h_).

If a section doesn't apply this time (e.g. no problems today), just write _"None"_ — please keep the heading so the structure stays consistent.

### Entry template

Copy this into each new file:

```markdown
# 2026-05-21

**Time spent since last entry:** ~4h

## What was done

- ...

## Problems encountered

- ...

## Solutions

- ...

## Next plan

- ...

## Demo video

- [Loom — title of video](https://www.loom.com/share/...) ← if you recorded one this entry
```

---

## 4. Loom demo videos

Recording yourself walking through what you built is one of the fastest ways to see weak spots in your own thinking — and it gives your peers and mentors something concrete to react to, which makes their feedback much more useful.

### Rules

- Record with **Loom**: https://www.loom.com/
- **Maximum 5 minutes per video** — this is the limit on Loom's free tier, and it also happens to be about the right length for a focused demo.
- **Up to 2 videos per week.** More than that becomes hard to watch carefully; please pick the moments worth showing.
- Embed the Loom link inside the diary entry where you describe the work, under a `## Demo video` heading (see template above).

### What a good Loom covers

- **Demo** — show the feature working end-to-end as a user would experience it.
- **Code review** — bird's-eye walkthrough of code you wrote: structure, the interesting bits, the parts you're unsure about.
- **Debug session** — explain a bug you hit and how you fixed it.

Pick one moment that's worth narrating and go deep on that.

---

## 5. Submission checklist

By the end of the program please make sure you have:

- [ ] GitHub URL submitted (Path A or Path B) — same URL for the whole program. We'll share detailed instructions on where to submit by the end of this week hopefully.
- [ ] `diary/` folder with **at least two entries per week**, every week starting from week 2 (4 weeks in total).
- [ ] Every entry contains the five required sections.
- [ ] At least **one Loom video per week** linked from a diary entry.
- [ ] All entries committed and pushed.

The `README.md` at the root of your repo should state your name and the project you're building.

---

## 6. Common pitfalls

- **Backfilling a week of entries on Sunday night.** It's pretty visible in the commit timestamps, and the content tends to feel shallow even to the person writing it. Try to write entries close to when the work actually happens — it's also less painful that way.
- **Pasting commit messages as the entry.** The diary is for reflection, not a changelog. We're more interested in what you _thought_ than just what you _did_.
- **Skipping "Problems encountered" because nothing went wrong.** It's normal — and good — to hit walls. Those are often the most valuable moments to capture for your future self and for peers who might be stuck on the same thing.
- **Loom videos that are read-throughs of slides.** Please show the running app or the actual code, not a deck.
- **Private repo with the diary folder.** Even on Path B, the diary repo needs to be **public** so peers and mentors can read it.

_Questions about these requirements? Please ask in the Telegram mentorship group._
