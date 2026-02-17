"""
Database Operations
CRUD operations for invoice system
Author: Bunny Rangu
Day: 5/30
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.database import Customer, Invoice, InvoiceItem


class DatabaseOperations:
    """Handle all database operations"""
    
    @staticmethod
    def create_or_get_customer(db: Session, customer_data: Dict) -> Customer:
        """
        Create new customer or get existing one by phone
        
        Args:
            db: Database session
            customer_data: Customer details dictionary
            
        Returns:
            Customer object
        """
        # Check if customer exists by phone
        existing = db.query(Customer).filter(
            Customer.phone == customer_data['phone']
        ).first()
        
        if existing:
            # Update existing customer details
            existing.name = customer_data['name']
            existing.email = customer_data.get('email', existing.email)
            existing.address = customer_data.get('address', existing.address)
            existing.gst_number = customer_data.get('gst_number', existing.gst_number)
            existing.state = customer_data.get('state', existing.state)
            existing.updated_at = datetime.now()
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new customer
        customer = Customer(
            name=customer_data['name'],
            phone=customer_data['phone'],
            email=customer_data.get('email', ''),
            address=customer_data.get('address', ''),
            gst_number=customer_data.get('gst_number', ''),
            state=customer_data.get('state', 'Telangana')
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    
    @staticmethod
    def create_invoice(db: Session, invoice_data: Dict) -> Invoice:
        """
        Create new invoice with items
        
        Args:
            db: Database session
            invoice_data: Complete invoice dictionary
            
        Returns:
            Invoice object
        """
        # Get or create customer
        customer = DatabaseOperations.create_or_get_customer(
            db, invoice_data['customer']
        )
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_data['invoice_number'],
            date=invoice_data['date'],
            time=invoice_data['time'],
            customer_id=customer.id,
            subtotal=invoice_data['totals']['subtotal'],
            total_cgst=invoice_data['totals']['total_cgst'],
            total_sgst=invoice_data['totals']['total_sgst'],
            total_gst=invoice_data['totals']['total_gst'],
            grand_total=invoice_data['totals']['grand_total'],
            total_items=invoice_data['totals']['total_items'],
            total_quantity=invoice_data['totals']['total_quantity'],
            notes=invoice_data.get('notes', ''),
            payment_status=invoice_data.get('payment_status', 'Pending'),
            payment_method=invoice_data.get('payment_method', ''),
            status=invoice_data.get('status', 'Draft')
        )
        db.add(invoice)
        db.flush()  # Get invoice.id without committing
        
        # Create invoice items
        for item_data in invoice_data['items']:
            item = InvoiceItem(
                invoice_id=invoice.id,
                name=item_data['name'],
                description=item_data.get('description', ''),
                hsn_code=item_data.get('hsn_code', ''),
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                subtotal=item_data['subtotal'],
                gst_rate=item_data['gst_rate'],
                cgst_rate=item_data['cgst_rate'],
                sgst_rate=item_data['sgst_rate'],
                cgst_amount=item_data['cgst_amount'],
                sgst_amount=item_data['sgst_amount'],
                total_gst=item_data['total_gst'],
                total_amount=item_data['total_amount']
            )
            db.add(item)
        
        db.commit()
        db.refresh(invoice)
        return invoice
    
    @staticmethod
    def get_invoice_by_number(db: Session, invoice_number: str) -> Optional[Invoice]:
        """
        Get invoice by invoice number
        
        Args:
            db: Database session
            invoice_number: Invoice number to find
            
        Returns:
            Invoice object or None
        """
        return db.query(Invoice).filter(
            Invoice.invoice_number == invoice_number
        ).first()
    
    @staticmethod
    def get_all_invoices(db: Session, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """
        Get all invoices with pagination
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of invoice objects
        """
        return db.query(Invoice).order_by(
            Invoice.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_customer_invoices(db: Session, customer_name: str) -> List[Invoice]:
        """
        Get all invoices for a customer
        
        Args:
            db: Database session
            customer_name: Customer name
            
        Returns:
            List of invoice objects
        """
        return db.query(Invoice).join(Customer).filter(
            Customer.name.ilike(f"%{customer_name}%")
        ).order_by(Invoice.created_at.desc()).all()
    
    @staticmethod
    def get_total_invoice_count(db: Session) -> int:
        """Get total number of invoices"""
        return db.query(Invoice).count()
    
    @staticmethod
    def get_next_invoice_number(db: Session) -> int:
        """Get next invoice counter number"""
        last_invoice = db.query(Invoice).order_by(
            Invoice.id.desc()
        ).first()
        
        if not last_invoice:
            return 1000
        
        # Extract number from invoice_number (format: INV-YYYY-NNNN)
        try:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            return last_number + 1
        except:
            return 1000
    
    @staticmethod
    def _invoice_to_dict(invoice: Invoice) -> Dict:
        """
        Convert Invoice object to dictionary
        
        Args:
            invoice: Invoice SQLAlchemy object
            
        Returns:
            Invoice dictionary
        """
        return {
            'invoice_number': invoice.invoice_number,
            'date': invoice.date,
            'time': invoice.time,
            'company': {
                'name': 'AI Tax Solutions',
                'address': 'Hyderabad, Telangana',
                'gst_number': '36AABCU9603R1ZM',
                'phone': '9876543210',
                'email': 'info@aitaxsolutions.com'
            },
            'customer': {
                'name': invoice.customer.name,
                'phone': invoice.customer.phone,
                'email': invoice.customer.email,
                'address': invoice.customer.address,
                'gst_number': invoice.customer.gst_number,
                'state': invoice.customer.state
            },
            'items': [
                {
                    'name': item.name,
                    'description': item.description,
                    'hsn_code': item.hsn_code,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'subtotal': item.subtotal,
                    'gst_rate': item.gst_rate,
                    'cgst_rate': item.cgst_rate,
                    'sgst_rate': item.sgst_rate,
                    'cgst_amount': item.cgst_amount,
                    'sgst_amount': item.sgst_amount,
                    'total_gst': item.total_gst,
                    'total_amount': item.total_amount
                }
                for item in invoice.items
            ],
            'totals': {
                'subtotal': invoice.subtotal,
                'total_cgst': invoice.total_cgst,
                'total_sgst': invoice.total_sgst,
                'total_gst': invoice.total_gst,
                'grand_total': invoice.grand_total,
                'total_items': invoice.total_items,
                'total_quantity': invoice.total_quantity
            },
            'notes': invoice.notes,
            'payment_status': invoice.payment_status,
            'payment_method': invoice.payment_method,
            'status': invoice.status,
            'created_at': invoice.created_at.isoformat()
        }


if __name__ == "__main__":
    print("Database operations module loaded successfully!")  