"""
Invoice Agent with Database Support
Updated version using SQLAlchemy database
Author: Bunny Rangu
Day: 5/30
"""
from app.models.payment_operations import PaymentOperations
from app.models.database import Invoice  # Add this if not already there
from datetime import datetime
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.agents.validator import InvoiceValidator
from app.agents.gst_calculator import GSTCalculator
from app.models.database import SessionLocal, init_database
from app.models.db_operations import DatabaseOperations


class InvoiceAgentDB:
    """Invoice agent with database persistence"""
    
    def __init__(self):
        """Initialize invoice agent"""
        self.validator = InvoiceValidator()
        self.calculator = GSTCalculator(base_price=0, gst_rate=0)
        self.db_ops = DatabaseOperations()
        init_database()
    
    def get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def create_invoice(
        self,
        customer: Dict,
        items: List[Dict],
        notes: str = ""
    ) -> Dict:
        """
        Create a new invoice with database persistence
        
        Args:
            customer: Customer information dict
            items: List of item dicts
            notes: Additional notes
            
        Returns:
            Result dictionary with success/error and invoice data
        """
        # Step 1: Validate customer
        is_valid, msg = self.validator.validate_customer_details(customer)
        if not is_valid:
            return {'success': False, 'error': f"Customer validation failed: {msg}"}
        
        # Step 2: Validate items
        if not items:
            return {'success': False, 'error': "Invoice must have at least one item"}
            
        for i, item in enumerate(items):
            is_valid, msg = self.validator.validate_invoice_item(item)
            if not is_valid:
                return {'success': False, 'error': f"Item {i+1} validation failed: {msg}"}
        
        # Step 3: Calculate GST for each item
        calculated_items = []
        for item in items:
            calculator = GSTCalculator(
                base_price=item['price'],
                gst_rate=item['gst_rate'],
                quantity=item['quantity']
            )
            calc = calculator.calculate()
            calculated_items.append({
                'name': item['name'],
                'description': item.get('description', ''),
                'hsn_code': item.get('hsn_code', ''),
                'quantity': calc['quantity'],
                'unit_price': calc['base_price_per_unit'],
                'subtotal': calc['total_base_amount'],
                'gst_rate': calc['gst_rate'],
                'cgst_rate': calc['gst_rate'] / 2,
                'sgst_rate': calc['gst_rate'] / 2,
                'cgst_amount': calc['cgst'],
                'sgst_amount': calc['sgst'],
                'total_gst': calc['total_gst'],
                'total_amount': calc['final_price']
            })
            
        # Step 4: Calculate overall totals
        total_subtotal = sum(item['subtotal'] for item in calculated_items)
        total_cgst = sum(item['cgst_amount'] for item in calculated_items)
        total_sgst = sum(item['sgst_amount'] for item in calculated_items)
        total_gst = sum(item['total_gst'] for item in calculated_items)
        grand_total = sum(item['total_amount'] for item in calculated_items)
        
        totals = {
            'subtotal': round(total_subtotal, 2),
            'total_cgst': round(total_cgst, 2),
            'total_sgst': round(total_sgst, 2),
            'total_gst': round(total_gst, 2),
            'grand_total': round(grand_total, 2),
            'total_items': len(calculated_items),
            'total_quantity': sum(item['quantity'] for item in calculated_items)
        }
        
        # Step 5: Generate invoice number
        invoice_number = self._generate_invoice_number()
        
        # Step 6: Create invoice data structure
        invoice_data = {
            'invoice_number': invoice_number,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'status': 'DRAFT',
            'payment_status': 'Pending',
            'payment_method': None,
            'customer': customer,
            'items': calculated_items,
            'totals': totals,
            'notes': notes
        }
        
        # Step 7: Save to database
        db = self.get_db()
        try:
            # Use DatabaseOperations.create_invoice instead of save_invoice
            saved_invoice = self.db_ops.create_invoice(db, invoice_data)
            return {
                'success': True,
                'message': f'Invoice {saved_invoice.invoice_number} created successfully',
                'invoice': self._invoice_model_to_dict(saved_invoice)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Database error: {str(e)}"
            }
        finally:
            db.close()
    
    def get_invoice(self, invoice_number: str) -> Dict:
        """Get invoice by number"""
        db = self.get_db()
        try:
            invoice = self.db_ops.get_invoice_by_number(db, invoice_number)
            if invoice:
                return self._invoice_model_to_dict(invoice)
            return None
        finally:
            db.close()
    
    def get_all_invoices(self) -> List[Dict]:
        """Get all invoices"""
        db = self.get_db()
        try:
            invoices = self.db_ops.get_all_invoices(db)
            return [self._invoice_model_to_dict(inv) for inv in invoices]
        finally:
            db.close()
    
    def get_customer_invoices(self, customer_name: str) -> List[Dict]:
        """Get invoices for a specific customer"""
        db = self.get_db()
        try:
            invoices = self.db_ops.get_invoices_by_customer(db, customer_name)
            return [self._invoice_model_to_dict(inv) for inv in invoices]
        finally:
            db.close()
    
    def add_payment(
        self,
        invoice_number: str,
        amount: float,
        payment_method: str,
        transaction_id: str = "",
        notes: str = ""
    ) -> Dict:
        """
        Record a payment for an invoice
        
        Args:
            invoice_number: Invoice number
            amount: Payment amount
            payment_method: Payment method
            transaction_id: Transaction ID (optional)
            notes: Payment notes (optional)
            
        Returns:
            Success/failure dictionary
        """
        db = self.get_db()
        
        try:
            # Get invoice
            invoice = db.query(Invoice).filter(
                Invoice.invoice_number == invoice_number
            ).first()
            
            if not invoice:
                return {
                    'success': False,
                    'error': f'Invoice {invoice_number} not found'
                }
            
            # Add payment
            payment = PaymentOperations.add_payment(
                db=db,
                invoice_id=invoice.id,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                notes=notes
            )
            
            # Get updated totals
            total_paid = PaymentOperations.get_total_paid(db, invoice.id)
            remaining = invoice.grand_total - total_paid
            
            return {
                'success': True,
                'message': f'Payment of ₹{amount:,.2f} recorded',
                'payment_id': payment.id,
                'total_paid': total_paid,
                'remaining': max(0, remaining),
                'status': invoice.payment_status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            db.close()
    
    def get_payment_history(self, invoice_number: str) -> List[Dict]:
        """Get payment history for an invoice"""
        db = self.get_db()
        
        try:
            invoice = db.query(Invoice).filter(
                Invoice.invoice_number == invoice_number
            ).first()
            
            if not invoice:
                return []
            
            return PaymentOperations.get_payment_history(db, invoice.id)
            
        finally:
            db.close()
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        db = self.get_db()
        try:
            # Get current year
            year = datetime.now().year
            
            # Get next number from database
            next_number = self.db_ops.get_next_invoice_number(db)
            
            # Generate number (e.g., INV-2025-1001)
            return f"INV-{year}-{next_number}"
        finally:
            db.close()
    
    def _invoice_model_to_dict(self, invoice_model) -> Dict:
        """Convert SQLAlchemy model to dictionary"""
        return {
            'id': invoice_model.id,
            'invoice_number': invoice_model.invoice_number,
            'date': invoice_model.date,
            'due_date': invoice_model.due_date,
            'time': invoice_model.time,
            'status': invoice_model.status,
            'payment_status': invoice_model.payment_status,
            'payment_method': invoice_model.payment_method,
            'company': {
                'name': 'AI Tax Solutions',
                'address': 'Hyderabad, Telangana',
                'gst_number': '36AABCU9603R1ZM',
                'phone': '9876543210',
                'email': 'info@aitaxsolutions.com'
            },
            'customer': {
                'name': invoice_model.customer.name,
                'phone': invoice_model.customer.phone,
                'email': invoice_model.customer.email,
                'address': invoice_model.customer.address,
                'gst_number': invoice_model.customer.gst_number,
                'state': invoice_model.customer.state
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
                for item in invoice_model.items
            ],
            'totals': {
                'subtotal': invoice_model.subtotal,
                'total_cgst': invoice_model.total_cgst,
                'total_sgst': invoice_model.total_sgst,
                'total_gst': invoice_model.total_gst,
                'grand_total': invoice_model.grand_total,
                'total_items': invoice_model.total_items,
                'total_quantity': invoice_model.total_quantity
            },
            'notes': invoice_model.notes
        }
    
    def display_invoice(self, invoice_data: Dict):
        """Display invoice in console (for testing)"""
        print("\n" + "="*60)
        print(f"🧾 INVOICE: {invoice_data['invoice_number']}")
        print("="*60)
        print(f"📅 Date: {invoice_data['date']} | ⏰ Time: {invoice_data['time']}")
        print(f"📊 Status: {invoice_data['status']} | 💰 Payment: {invoice_data['payment_status']}")
        print()
        
        # Company Info
        company = invoice_data['company']
        print("🏢 FROM:")
        print(f"   {company['name']}")
        print(f"   📍 {company['address']}")
        print(f"   📞 {company['phone']} | ✉️  {company['email']}")
        print(f"   🔖 GST: {company['gst_number']}")
        print()
        
        # Customer Info
        customer = invoice_data['customer']
        print("👤 TO:")
        print(f"   {customer['name']}")
        print(f"   📞 {customer['phone']}")
        if customer['email']:
            print(f"   ✉️  {customer['email']}")
        if customer['address']:
            print(f"   📍 {customer['address']}")
        if customer['gst_number']:
            print(f"   🔖 GST: {customer['gst_number']}")
        print()
        
        # Items Table
        print("📋 ITEMS:")
        print("-" * 80)
        print(f"{'Item':<25} {'Qty':<5} {'Rate':<12} {'GST%':<6} {'Amount':<12}")
        print("-" * 80)
        
        for item in invoice_data['items']:
            name = item['name'][:22] + "..." if len(item['name']) > 22 else item['name']
            print(f"{name:<25} {item['quantity']:<5} ₹{item['unit_price']:<11,.2f} "
                  f"{item['gst_rate']:<6} ₹{item['total_amount']:<11,.2f}")
        
        print("-" * 80)
        
        # Totals
        totals = invoice_data['totals']
        print(f"{'Subtotal:':<50} ₹{totals['subtotal']:>15,.2f}")
        print(f"{'CGST:':<50} ₹{totals['total_cgst']:>15,.2f}")
        print(f"{'SGST:':<50} ₹{totals['total_sgst']:>15,.2f}")
        print(f"{'Total GST:':<50} ₹{totals['total_gst']:>15,.2f}")
        print("=" * 80)
        print(f"{'GRAND TOTAL:':<50} ₹{totals['grand_total']:>15,.2f}")
        print("=" * 80)
        
        if invoice_data['notes']:
            print(f"\n📝 Notes: {invoice_data['notes']}")


def test_invoice_agent():
    """Test the database-backed invoice agent"""
    print("🧪 TESTING DATABASE INVOICE AGENT\n")
    
    agent = InvoiceAgentDB()
    
    # Test data
    customer = {
        'name': 'Rajesh Kumar',
        'phone': '9876543210',
        'email': 'rajesh@example.com',
        'address': 'Mumbai, Maharashtra',
        'gst_number': '27ABCDE1234F1Z5',
        'state': 'Maharashtra'
    }
    
    items = [
        {
            'name': 'Laptop Dell Inspiron',
            'description': '15.6 inch, 8GB RAM, 512GB SSD',
            'price': 50000,
            'quantity': 1,
            'gst_rate': 18,
            'hsn_code': '8471'
        },
        {
            'name': 'Wireless Mouse',
            'description': 'Bluetooth, Rechargeable',
            'price': 1500,
            'quantity': 2,
            'gst_rate': 18,
            'hsn_code': '8471'
        }
    ]
    
    # Create invoice
    result = agent.create_invoice(
        customer=customer,
        items=items,
        notes='Thank you for your business!'
    )
    
    if result['success']:
        print("✅ Invoice created successfully!")
        print(f"🧾 Invoice Number: {result['invoice']['invoice_number']}")
        print(f"💰 Total Amount: ₹{result['invoice']['totals']['grand_total']:,.2f}")
        
        # Display invoice
        agent.display_invoice(result['invoice'])
        
        # Test getting invoice
        invoice = agent.get_invoice(result['invoice']['invoice_number'])
        if invoice:
            print(f"\n✅ Retrieved invoice: {invoice['invoice_number']}")
        
        # Test listing all invoices
        all_invoices = agent.get_all_invoices()
        print(f"\n📊 Total invoices in database: {len(all_invoices)}")
        
    else:
        print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    test_invoice_agent()