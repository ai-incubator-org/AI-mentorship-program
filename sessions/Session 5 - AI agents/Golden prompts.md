# Tab 1

I am building Ilm AI — a personal AI learning companion. Users upload their own

materials (PDFs, DOCX, plain text), and the app becomes a tutor for that material.

Core features I must ship:

1\. Auth (email \+ Google OAuth), user profiles with learning stats and a goal \+ target date

2\. Personal knowledge base — upload, chunk, embed, store in a vector DB, organise into topics

3\. AI chat companion — strictly grounded in the user's uploads, cites the source section,

   responds in Uzbek/Russian/English, warm \+ Socratic tone

4\. Quiz mode — 3 difficulty levels, MCQ \+ short answer \+ open-ended, with explanations

5\. Knowledge gap detection — agent with memory that updates after every session

6\. Learning plan generator — agent with tools, day-by-day plan to the user's goal date

7\. Telegram bot — daily reminders, on-demand 5-question quizzes, streak notifications

8\. Payment — free vs premium tier, Payme/Click for UZ, Stripe for international, webhooks

DO NOT WRITE ANY CODE YET. Your task right now:

1\. Read this brief and ask me 5 sharp clarifying questions you would ask a real client

   before starting. Pick the questions that would change the architecture the most if I

   answered them differently.

2\. Then propose a CLAUDE.md file for the root of this project, covering: project goals,

   tech stack decisions, file/folder conventions, naming conventions, testing rules,

   security rules (no secrets in repo, JWT auth), and how you should behave on every

   future prompt (e.g. always plan before refactoring, always cite docs, always write

   tests for new endpoints).

# Tab 2

Based on the architecture we agreed on, write a plan to scaffold the repository.  
Include:  
\- Folder structure for backend (FastAPI) and frontend (Next.js \+ Tailwind)  
\- The exact files you will create in step 1 (don't write them yet, just list)  
\- Docker setup: a Dockerfile per service \+ a docker-compose.yml for local dev  
  (Postgres with pgvector, backend, frontend, redis if needed)  
\- .env.example with every variable I will eventually need (OpenAI/Anthropic key,  
  database URL, JWT secret, Google OAuth client ID, Telegram bot token, Payme/Click  
  keys, S3 keys, Sentry DSN)  
\- .gitignore that prevents secrets, node\_modules, .venv, \_\_pycache\_\_, .next from  
  being committed  
\- README skeleton  
Then list the order you will create everything in. Do not write the files yet.

# Tab 3

Plan the authentication system.  
Requirements:  
\- Email \+ password sign-up and login  
\- Google OAuth as an alternative  
\- JWT-based session, with refresh token  
\- Password reset via email  
\- Each user has a profile: name, learning goal (text), target date (date),  
  preferred language (uz/ru/en)  
Output:  
1\. The DB schema (Postgres tables: users, auth\_providers, refresh\_tokens, profiles)  
2\. The API endpoints with method \+ path \+ request/response shape  
3\. Frontend pages and components needed  
4\. The security checklist (password hashing with bcrypt, rate limiting on login,  
   JWT secret rotation, HTTPOnly cookies, CSRF strategy)  
5\. What tests we will write  
\`\`\`

# Tab 4

Implement the plan. Start with the database migration, then the backend endpoints,  
then the frontend pages. Write tests for each backend endpoint as you go. Stop and  
show me after every endpoint so I can review before moving to the next.  
