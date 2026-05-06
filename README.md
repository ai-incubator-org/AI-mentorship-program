# 🤖 AI Mentorship Program

> **A 5-week intensive mentorship program for developers building real AI-powered products.**  
> Top participants advance to the **AI Incubator** — the next stage of growth.

---

## What Is This Program?

The AI Mentorship Program is a structured, hands-on learning experience for developers who want to go beyond tutorials and build production-grade AI applications. Over 5 weeks and 16 sessions, participants learn the full stack of modern AI engineering — from LLM fundamentals to multi-agent systems, RAG pipelines, deployment, and monitoring.

This is not a course. It is a mentorship program. You will be expected to build, ship, and demonstrate real work.

---

## The Capstone Project: Ilm AI

Every participant builds **Ilm AI** — a personal AI learning companion that helps anyone study any material they bring to it. A user uploads their own documents (textbooks, course transcripts, research papers, notes), and Ilm AI becomes their tutor: quizzing them, explaining their mistakes, finding gaps in their understanding, and generating a personalised learning plan.

Ilm AI is built for learners in Uzbekistan and Central Asia, with full support for Uzbek, Russian, and English.

📄 **[Read the full project brief →](https://docs.google.com/document/d/12Tn0PtOv4hkg_lhAlP7xuzT2yNsxUScDIjwqjRIXl-Q/edit?tab=t.0)**

---

## Program Schedule

The program runs from **12 May to 14 June 2025** across 5 weeks and 16 sessions.

| # | Date | Day | Session |
|---|------|-----|---------|
| S1 | 12 May | Tuesday | Program Orientation & AI Landscape Overview |
| S2 | 14 May | Thursday | LLM Fundamentals: Tokens, Context, Temperature & Prompting |
| S3 | 16 May | Saturday | Building Production-Ready AI Apps: Architecture Patterns |
| S4 | 19 May | Tuesday | Semantic Search, Vector Embeddings & RAG Systems |
| S5 | 21 May | Thursday | AI Agents: Tools, Memory & Planning Patterns |
| S6 | 23 May | Saturday | Orchestration Frameworks: LangChain / LlamaIndex |
| S7 | 26 May | Tuesday | External Integrations: APIs, Databases & Webhooks |
| S8 | 28 May | Thursday | Multi-Agent Systems, Coordination Patterns & AI Security |
| S9 | 30 May | Saturday | Data Engineering: Scalable Pipelines & Feature Systems |
| S10 | 2 June | Tuesday | ML Paradigms: Supervised, Unsupervised, RL & Self-Supervised |
| S11 | 4 June | Thursday | Generative Models: Diffusion, VAEs & GANs Overview |
| S12 | 6 June | Saturday | Deployment Pipelines: Docker, CI/CD & Cloud Environments |
| S13 | 9 June | Tuesday | Production ML: Monitoring, Evaluation & Optimization |
| S14 | 11 June | Thursday | Multimodal AI |
| S15 | 13 June | Saturday | Final Project Q&A |
| S16 | 14 June | Sunday | Final Project Q&A |

---

## Project Milestones

Participants work on Ilm AI in parallel with the sessions.

| Week | Milestone | What to Have Working |
|------|-----------|----------------------|
| Week 1 (after S1–S4) | Foundation | Auth working, file upload and processing pipeline running, basic RAG chat answering questions from uploaded documents |
| Week 2 (after S5–S8) | Core Features | Quiz mode live, learning plan agent generating plans, Telegram bot sending reminders and running quizzes |
| Week 3 (after S9–S11) | Polish & Integrate | Knowledge gap detection running across sessions, payment flow integrated in test mode, UI complete and mobile-friendly |
| Week 4 (after S12–S14) | Ship It | Deployed to production, CI/CD running on push, monitoring in place, 50 evaluation samples rated |

---

## What You Will Build (MVP)

All participants must ship the following features:

- **User Authentication & Profiles** — sign up, log in (email or Google OAuth), personal learning dashboard
- **Personal Knowledge Base** — upload PDFs, Word documents, plain text; materials are chunked, embedded, and stored in a vector database
- **AI Learning Companion** — conversational chat grounded strictly in uploaded materials, with citations and multilingual support (Uzbek, Russian, English)
- **Quiz & Practice Mode** — AI-generated questions at multiple difficulty levels, with explanations after each answer
- **Knowledge Gap Detection** — identifies concepts the user consistently struggles with across sessions
- **Learning Plan Generator** — AI agent that creates a day-by-day plan based on uploaded materials, detected gaps, and the user's goal date
- **Telegram Bot Integration** — daily reminders, on-demand 5-question quizzes, streak notifications
- **Payment & Premium Tier** — Payme / Click (Uzbekistan) or Stripe integration; free and premium tiers

---

## Tech Stack (Recommended)

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (React), Tailwind CSS |
| Backend | FastAPI (Python) or Node.js / Express |
| LLM | OpenAI GPT-4o or Anthropic Claude |
| Orchestration | LangChain or LlamaIndex |
| Vector DB | Pinecone, Weaviate, or pgvector |
| Database | PostgreSQL |
| File Storage | AWS S3 or Supabase Storage |
| Deployment | Docker, Docker Compose, GitHub Actions CI/CD |
| Hosting | Railway, Render, or a VPS (DigitalOcean / Hetzner / Beeline Cloud UZ) |
| Payments | Payme, Click, or Stripe |
| Messaging | Telegram Bot API |

---

## Final Deliverables

Each participant (or team of two) must submit:

1. **Live URL** — a working, publicly accessible deployment
2. **GitHub Repository** — clean code with a README covering setup, architecture diagram, and API docs
3. **5-minute Demo Video** — walkthrough of the full user journey: sign up → upload → chat → quiz → learning plan → payment
4. **Evaluation Report** — at least 50 AI companion responses rated on accuracy, groundedness, helpfulness, and tone
5. **1-page Reflection** — what was hardest to build, what you would do differently, and what you learned

---

## Evaluation Rubric

| Category | Weight | What Reviewers Look For |
|----------|--------|-------------------------|
| RAG Quality | 20% | Answers are grounded in uploaded materials — no hallucinated content |
| Agent Behaviour | 15% | Learning plan and gap detection work correctly and improve with each session |
| Code Quality | 15% | Clean structure, meaningful error handling, no hardcoded secrets |
| Deployment | 15% | App is live, CI/CD runs on push, production environment is stable |
| Product Thinking | 15% | A real person can sign up and use this without any instructions |
| Integrations | 10% | Telegram bot and payment flow both work end-to-end |
| Evaluation & Monitoring | 10% | LLM calls are logged, evaluation rubric applied and documented |

**Bonus points** for shipping a stretch feature and for getting at least 3 real people to use the product before the final demo.

---

## What Comes Next: The AI Incubator

The top participants from this program will be selected to advance to the **AI Incubator** — the next phase of the programme. The Incubator is for those who have demonstrated they can build and ship, and are ready to take their idea further.

Selection is based on project quality, code standards, product thinking, and the ability to get real users.

---

## Resources

- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [LlamaIndex Getting Started](https://docs.llamaindex.ai/en/stable/)
- [Telegram Bot API Docs](https://core.telegram.org/bots/api)
- [Payme Integration Guide](https://developer.paycom.uz/)
- [Click Integration Guide](https://docs.click.uz/)
- [pgvector on Supabase](https://supabase.com/docs/guides/database/extensions/pgvector)
- [GitHub Actions CI/CD Guide](https://docs.github.com/en/actions)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)

---

*Ilm AI — because learning is not a phase of life. It is life.*  
*AI Mentorship Program · Uzbekistan · 2025*
