"""
Payment Operations
Handle payment tracking and updates
Author: Bunny Rangu
Day: 9/30
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.database import Invoice, Payment


class PaymentOperations:
    """Handle all payment-related operations"""
    
    @staticmethod
    def add_payment(
        db: Session,
        invoice_id: int,
        amount: float,
        payment_method: str,
        transaction_id: str = "",
        notes: str = ""
    ) -> Payment:
        """
        Record a payment for an invoice
        
        Args:
            db: Database session
            invoice_id: Invoice ID
            amount: Payment amount
            payment_method: Payment method (UPI, Cash, Card, etc.)
            transaction_id: Transaction reference
            notes: Additional notes
            
        Returns:
            Payment object
        """
        # Create payment record
        payment = Payment(
            invoice_id=invoice_id,
            payment_date=datetime.now().strftime("%Y-%m-%d"),
            payment_time=datetime.now().strftime("%H:%M:%S"),
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            notes=notes
        )
        
        db.add(payment)
        
        # Update invoice payment status
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            total_paid = PaymentOperations.get_total_paid(db, invoice_id) + amount
            
            if total_paid >= invoice.grand_total:
                invoice.payment_status = "Paid"
            elif total_paid > 0:
                invoice.payment_status = "Partial"
            else:
                invoice.payment_status = "Pending"
            
            invoice.payment_method = payment_method
        
        db.commit()
        db.refresh(payment)
        
        return payment
    
    @staticmethod
    def get_total_paid(db: Session, invoice_id: int) -> float:
        """
        Get total amount paid for an invoice
        
        Args:
            db: Database session
            invoice_id: Invoice ID
            
        Returns:
            Total paid amount
        """
        payments = db.query(Payment).filter(
            Payment.invoice_id == invoice_id
        ).all()
        
        return sum(p.amount for p in payments)
    
    @staticmethod
    def get_payment_history(db: Session, invoice_id: int) -> List[Dict]:
        """
        Get payment history for an invoice
        
        Args:
            db: Database session
            invoice_id: Invoice ID
            
        Returns:
            List of payment dictionaries
        """
        payments = db.query(Payment).filter(
            Payment.invoice_id == invoice_id
        ).order_by(Payment.created_at.desc()).all()
        
        return [
            {
                'id': p.id,
                'date': p.payment_date,
                'time': p.payment_time,
                'amount': p.amount,
                'method': p.payment_method,
                'transaction_id': p.transaction_id,
                'notes': p.notes
            }
            for p in payments
        ]
    
    @staticmethod
    def get_outstanding_invoices(db: Session) -> List[Invoice]:
        """
        Get all unpaid or partially paid invoices
        
        Args:
            db: Database session
            
        Returns:
            List of outstanding invoices
        """
        return db.query(Invoice).filter(
            Invoice.payment_status.in_(["Pending", "Partial"])
        ).order_by(Invoice.date.desc()).all()
    
    @staticmethod
    def get_overdue_invoices(db: Session) -> List[Invoice]:
        """
        Get invoices past their due date
        
        Args:
            db: Database session
            
        Returns:
            List of overdue invoices
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        return db.query(Invoice).filter(
            Invoice.payment_status.in_(["Pending", "Partial"]),
            Invoice.due_date < today,
            Invoice.due_date.isnot(None)
        ).order_by(Invoice.due_date).all()
    
    @staticmethod
    def update_invoice_due_date(
        db: Session,
        invoice_id: int,
        due_date: str
    ) -> Invoice:
        """
        Set or update invoice due date
        
        Args:
            db: Database session
            invoice_id: Invoice ID
            due_date: Due date (YYYY-MM-DD)
            
        Returns:
            Updated invoice
        """
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if invoice:
            invoice.due_date = due_date
            db.commit()
            db.refresh(invoice)
        
        return invoice


if __name__ == "__main__":
    print("✅ Payment operations module loaded!")
    