from app.database import Base, engine
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.transfer import Transfer
from app.models.transfer_link import TransferLink
from app.models.transfer_customer import TransferCustomer
from app.models.allocation import Allocation

Base.metadata.create_all(bind=engine)
print("Tables created successfully!")