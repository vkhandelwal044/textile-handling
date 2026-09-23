from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import (
    transfer, customer, invoice, transfer_customer, transfer_link,
    allocation, reconciliation, traceability, payment_history
)

app = FastAPI(title="Textile Backend")

app.include_router(transfer.router)
app.include_router(customer.router)
app.include_router(invoice.router)
app.include_router(transfer_customer.router)
app.include_router(transfer_link.router)
app.include_router(allocation.router)
app.include_router(reconciliation.router)
app.include_router(traceability.router)
app.include_router(payment_history.router)

app.mount("/app", StaticFiles(directory="static", html=True), name="static")