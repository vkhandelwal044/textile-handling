# Me
I'm a 3rd-year CS student and this is my first backend project.
I know C, C++ and SQL basics. I'm new to Python web apps, FastAPI and JavaScript,
and I find it hard to follow how a project's files and functions connect.

# This project
Payment tracker for my family's textile business. It follows foreign (Mauritius)
customers' payments through two cargo persons until the money reaches the business.
Stack: FastAPI, PostgreSQL, SQLAlchemy models (app/models), Pydantic schemas
(app/schemas), routers (app/routers). My father uses static/payment_tracker.html.

# How to work with me
- Before editing, explain your plan in plain words: which files, which functions, why.
- Make one small change at a time, then stop so I can review it.
- Explain every new term. For every function you add or change, say what goes in,
  what comes out, and who calls it.
- After each change, tell me exactly how to test it myself (/docs or the screen).
- Don't run git commit or git push. I do those myself.
- Never open, print or edit .env.
- Don't quiz me in the middle of a step. After a big step, ask me to explain it back,
  and tell me plainly if my explanation is vague or wrong.

# Project rules
- customer_id is a customer's identity, never their name.
- Never hard-delete real financial records.
- New customers are created only through "+ Add New Customer", never by typing a new name.