# V1 Plan: Payment Tracker

Goal: finish V1 so the whole payment pipeline is complete, accurate, and usable by my father on his own.
Work through the steps in order, one at a time. Every step ends with a test and a commit.

## Plain names (use these when explaining)

| Table | Plain name | One row means |
|---|---|---|
| customers | people | one customer |
| invoices | bills | one bill given to a customer |
| transfers | money hops | money moving one step: customer → Mauritius cargo → India cargo → business |
| transfer_customers | whose money | ₹X of this hop belongs to this customer |
| transfer_links | where it came from | ₹X of this hop came from that earlier hop |
| allocations | which bill it paid | ₹X of this customer's money paid that bill |

The same file name in `models/`, `schemas/` and `routers/` is one feature seen three ways:
- **model**: what the row looks like
- **schema**: what a form must contain before it's accepted
- **router**: what happens when it's saved or asked for

## V1 is done when

- [ ] My father enters a real, messy case from start to finish on `payment_tracker.html`, alone: no IDs, no `index.html`, no pgAdmin.
- [ ] Every bill shows the right status: Paid, Partly paid or Unpaid.
- [ ] Where's My Money shows each amount once, with the customer's name, and catches a deliberate mistake.
- [ ] Nothing can be half-saved or saved twice.
- [ ] Every test in the checklist below passes.

## Rules for every change

1. **One button = one request = one save, all or nothing.** The backend adds every row, then calls `db.commit()` once. If anything fails before that, `db.rollback()` and nothing is saved. Don't call the existing create functions inside a new endpoint if they commit on their own, because that breaks the all-or-nothing save.
2. **Never hard-delete real money records.** Mistakes are cancelled (step 8), not deleted.
3. **customer_id is a customer's identity, never their name.**
4. **Show names, not IDs,** on every screen my father uses.
5. **Each step:** plan first (Plan mode) → one small change at a time (Manual mode) → I test it myself → I commit → I explain it back after big steps.
6. **Explanations:** at most 5 short steps, plain words, using the plain names above.

## A. Safety first

- [ ] **1. Warm-up.** Remove the stray `"""hello"""` line in `app/routers/allocation.py`. Practise review → test → commit.
- [ ] **2. Stop double saves.**
  - Save buttons disable themselves while saving and re-enable after the reply.
  - The backend refuses a second "whose money" row for the same customer on the same hop.
  - Test: click Save twice fast → only one record. Send the same share twice in `/docs` → clear error.
- [ ] **3. Bill rules.**
  - Bill numbers must be unique. Check the test data for duplicates first. `create_tables.py` doesn't change existing tables, so a database-level rule needs a small migration script.
  - A bill can only be paid with its own customer's money.
  - Test: duplicate bill number → clear error. Kavya's money on Rohan's bill → clear error.

## B. One save per stage

- [ ] **4. Stage 1 in one save.** The hop and its "whose money" row go in one request. This is the smallest example of the pattern.
  - Test in `/docs`: send a customer ID that doesn't exist → error, and no new hop appears.
- [ ] **5. Stage 2 simplified, in one save.**
  - My father enters customer + amount only. The backend uses that customer's oldest waiting Stage-1 money and shows which payment it used.
  - **Decide here:** if the amount is more than the oldest payment's remaining money, take the rest from the next oldest, or refuse?
  - Test: amount more than the customer has waiting → the whole save is refused and no hop is created.
- [ ] **6. Stage 3 by bill, in one save.**
  - My father picks the Stage-2 hop, then adds lines of "bill number + amount".
  - One save records the hop, the "where it came from" link, the "whose money" rows and the "which bill it paid" rows.
  - One customer paying two bills in one hop = one "whose money" row + two "which bill it paid" rows.
  - `index.html` is no longer needed after this.
  - Test: bills update to Paid / Partly paid right away.

## C. Readable and fixable

- [ ] **7. Rebuild Where's My Money.** One line per customer payment, one status, with the customer's name. No amount appears in more than one place.
- [ ] **8. Cancel entry.**
  - Each entry gets a Cancel button with a required reason. The entry is marked cancelled (status `cancelled` plus the reason). Nothing is deleted.
  - Totals, checks, bill status and Where's My Money ignore cancelled entries.
  - An entry that later stages depend on can't be cancelled. Cancel the later one first.
  - Needs a small migration for the reason column (like the photo column). If `status` is a database enum rather than plain text, adding `cancelled` needs a migration too.
  - Test: cancel a mistyped Stage 1 → it stops counting; re-enter it correctly. Try cancelling a Stage 1 that a Stage 2 uses → refused.
- [ ] **9. Customer names in `/docs`.** Transfer listings show names and dates, not just IDs.

## D. Go live

- [ ] **10. Fresh start.**
  - Create a new, empty database for real data and keep the current one for testing. Switch between them with `DATABASE_URL` in `.env`.
  - Remove the name-matching fallback in `traceability.py`. It only exists for old test data.
- [ ] **11. Final test.** Run the checklist below on the real database, then the real case with my father, then the mentor's four questions.

## Test checklist (step 11)

**Normal flow**
- [ ] Two customers, Stage 1 each, one Stage 2 hop for both, Stage 3 by bill → both bills Paid.
- [ ] A bill paid in part → Partly paid, with the right amount still owed.
- [ ] One customer pays two bills in one Stage 3 hop.
- [ ] Two Stage 3 entries on different days from the same Stage 2 hop.

**Mistakes the system must stop**
- [ ] Double click on Save → one record.
- [ ] Shares adding up to more than the hop → refused with a clear message.
- [ ] Customer A's money on customer B's bill → refused.
- [ ] Duplicate bill number → refused.
- [ ] A save where one line is invalid → nothing at all is saved.
- [ ] Cancelling an entry that later stages depend on → refused.

**Mistakes the system must show**
- [ ] Stage 2 forwards less than Stage 1 received → Where's My Money shows it once, with the name and the difference.
- [ ] Money received at Stage 3 but not matched to a bill → shown once, with the name.

**Fixing a mistake**
- [ ] Cancel a wrong entry and re-enter it → totals and bill status are correct.

**With my father**
- [ ] He enters one real, messy past case alone.
- [ ] Mentor's four questions: Is this clearer than WhatsApp and memory? Can you see where money is stuck? Can you see what each customer owes? Would you use this?

## Not in V1

Cargo person records, customer photos, automatic bill numbers, MUR currency, a database lock for two people saving at the exact same moment, the Sales Manager, and the full UI redesign. During V1, screens change only as much as each step needs.

## After V1

### 1. UI redesign (first, right after V1)

The current screens work but look plain. The redesign should feel like a textile business's own tool: clear for my father first, beautiful second. 2D, not 3D.

Ideas to start from:
- **Money as a thread.** Each customer payment is drawn as a thread running Customer → Mauritius cargo → India cargo → Business. A thread that reaches the end = matched. A thread that stops = money waiting. A frayed or broken thread = a mismatch. This could become the new Where's My Money.
- **Textile colours.** Indigo blue, deep red, turmeric yellow and cotton cream, with light fabric textures (handloom weave, block-print borders) used sparingly.
- **Bills as paper.** Each bill looks like a bill-book page with a "PAID" or "PARTLY PAID" stamp. Cancelled entries get a "CANCELLED" stamp.
- **Owner's home screen.** Three big numbers: money on the way, money received this month, money still owed on bills.
- **Keep:** English / Hindi / Gujarati, large readable text, and a layout that fits the device my father actually uses (phone or laptop).

Process: first, 2–3 mockups to compare with my father before any code changes. Then rebuild screen by screen, one commit per screen.

### 2. College topics

Login → automated tests (pytest) → Docker → cloud database → deploy → GitHub Actions.
