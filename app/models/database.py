"""
Database Models and Configuration
SQLAlchemy models for invoice system
Author: Bunny Rangu
Day: 5/30
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Create base class for models
Base = declarative_base()


class Customer(Base):
    """Customer model"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(10), nullable=False, unique=True, index=True)
    email = Column(String(100))
    address = Column(Text)
    gst_number = Column(String(15))
    state = Column(String(50), default="Telangana")
    
    # Relationship
    invoices = relationship("Invoice", back_populates="customer")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Customer(name='{self.name}', phone='{self.phone}')>"


class Invoice(Base):
    """Invoice model"""
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(String(10), nullable=False)
    due_date = Column(String(10))  # Add this line after the 'date' field
    time = Column(String(8), nullable=False)
    
    # Customer relationship
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    customer = relationship("Customer", back_populates="invoices")
    
    # Invoice totals
    subtotal = Column(Float, nullable=False)
    total_cgst = Column(Float, nullable=False)
    total_sgst = Column(Float, nullable=False)
    total_gst = Column(Float, nullable=False)
    grand_total = Column(Float, nullable=False)
    total_items = Column(Integer, nullable=False)
    total_quantity = Column(Integer, nullable=False)
    
    # Additional info
    notes = Column(Text)
    payment_status = Column(String(20), default="Pending")
    payment_method = Column(String(50))
    status = Column(String(20), default="Draft")
    
    # Relationship
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Invoice(number='{self.invoice_number}', total=₹{self.grand_total})>"


class InvoiceItem(Base):
    """Invoice item model"""
    __tablename__ = 'invoice_items'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Invoice relationship
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    invoice = relationship("Invoice", back_populates="items")
    
    # Item details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    hsn_code = Column(String(20))
    
    # Pricing
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    # GST breakdown
    gst_rate = Column(Float, nullable=False)
    cgst_rate = Column(Float, nullable=False)
    sgst_rate = Column(Float, nullable=False)
    cgst_amount = Column(Float, nullable=False)
    sgst_amount = Column(Float, nullable=False)
    total_gst = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<InvoiceItem(name='{self.name}', qty={self.quantity})>"

class Payment(Base):
    """Payment tracking model"""
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Invoice relationship
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    
    # Payment details
    payment_date = Column(String(10), nullable=False)
    payment_time = Column(String(8), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # UPI, Cash, Card, Bank Transfer
    transaction_id = Column(String(100))
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Payment(amount=₹{self.amount}, method={self.payment_method})>"
# Database connection setup
DATABASE_URL = "sqlite:///./gst_invoices.db"

class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100))
    is_active = Column(String(10), default="true")
    role = Column(String(20), default="user")  # admin, user
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables when module is imported
if __name__ == "__main__":
    print("Creating database tables...")
    init_database()
    print("Done!")