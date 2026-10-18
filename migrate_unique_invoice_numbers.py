# One-time migration: make invoice numbers CAPITAL and unique in the
# existing database. create_tables.py only creates missing tables, it never
# changes an existing one, so this script does that change by hand.
#
# Run once from the project folder:  python migrate_unique_invoice_numbers.py
# It is safe to run again: if the rule already exists, it does nothing.

from sqlalchemy import text
from app.database import engine

CONSTRAINT_NAME = "invoices_invoice_number_key"

# engine.begin() runs everything below as ONE transaction: if any line fails,
# nothing at all is changed (all or nothing).
with engine.begin() as conn:
    already_there = conn.execute(
        text("SELECT 1 FROM pg_constraint WHERE conname = :name"),
        {"name": CONSTRAINT_NAME},
    ).first()
    if already_there:
        print("The unique rule already exists. Nothing to do.")
    else:
        # Stop before changing anything if two bills would end up with the same number.
        duplicates = conn.execute(text(
            "SELECT UPPER(TRIM(invoice_number)) AS number, COUNT(*) AS how_many "
            "FROM invoices GROUP BY UPPER(TRIM(invoice_number)) HAVING COUNT(*) > 1"
        )).all()
        if duplicates:
            for row in duplicates:
                print(f"Duplicate bill number: {row.number} appears {row.how_many} times")
            raise SystemExit("Fix these duplicates first. Nothing was changed.")

        # 1. Turn old small-letter numbers into capitals, e.g. var-001 -> VAR-001.
        changed = conn.execute(text(
            "UPDATE invoices SET invoice_number = UPPER(TRIM(invoice_number)) "
            "WHERE invoice_number <> UPPER(TRIM(invoice_number))"
        ))
        print(f"Bill numbers changed to capitals: {changed.rowcount}")

        # 2. Add the rule: PostgreSQL itself refuses a second bill with the same number.
        conn.execute(text(
            f"ALTER TABLE invoices ADD CONSTRAINT {CONSTRAINT_NAME} UNIQUE (invoice_number)"
        ))
        print("Unique rule added. Done.")
