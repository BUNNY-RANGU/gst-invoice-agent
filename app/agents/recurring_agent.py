"""
Recurring Invoice Agent
Automate recurring invoice generation
Author: Bunny Rangu
Day: 18/30
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.database import RecurringInvoice, Customer, SessionLocal


class RecurringAgent:
    """Handle recurring invoice templates and generation"""
    
    FREQUENCIES = {
        'daily': {'name': 'Daily', 'days': 1},
        'weekly': {'name': 'Weekly', 'days': 7},
        'biweekly': {'name': 'Bi-weekly', 'days': 14},
        'monthly': {'name': 'Monthly', 'days': 30},
        'quarterly': {'name': 'Quarterly', 'days': 90},
        'yearly': {'name': 'Yearly', 'days': 365}
    }
    
    @staticmethod
    def create_recurring_invoice(
        template_name: str,
        customer_data: Dict,
        items: List[Dict],
        frequency: str,
        start_date: str,
        end_date: str = None,
        auto_send: bool = False,
        notes: str = ""
    ) -> Dict:
        """
        Create a recurring invoice template
        
        Args:
            template_name: Name for this recurring invoice
            customer_data: Customer details
            items: List of invoice items
            frequency: daily, weekly, monthly, yearly
            start_date: When to start (YYYY-MM-DD)
            end_date: When to stop (optional)
            auto_send: Auto-send via email when generated
            notes: Invoice notes
            
        Returns:
            Success/failure with template ID
        """
        db = SessionLocal()
        
        try:
            # Validate frequency
            if frequency not in RecurringAgent.FREQUENCIES:
                return {
                    'success': False,
                    'error': f'Invalid frequency. Must be one of: {list(RecurringAgent.FREQUENCIES.keys())}'
                }
            
            # Find or create customer
            customer = db.query(Customer).filter(
                Customer.phone == customer_data['phone']
            ).first()
            
            if not customer:
                customer = Customer(**customer_data)
                db.add(customer)
                db.flush()
            
            # Prepare invoice template
            template_data = {
                'customer': customer_data,
                'items': items,
                'notes': notes
            }
            
            # Calculate next invoice date
            next_date = start_date
            
            # Create recurring invoice
            recurring = RecurringInvoice(
                template_name=template_name,
                customer_id=customer.id,
                frequency=frequency,
                start_date=start_date,
                end_date=end_date,
                next_invoice_date=next_date,
                invoice_template=json.dumps(template_data),
                auto_send="true" if auto_send else "false",
                status="active"
            )
            
            db.add(recurring)
            db.commit()
            db.refresh(recurring)
            
            return {
                'success': True,
                'message': f'Recurring invoice "{template_name}" created',
                'template_id': recurring.id,
                'next_invoice_date': next_date
            }
            
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            db.close()
    
    @staticmethod
    def get_due_invoices() -> List[Dict]:
        """
        Get recurring invoices that are due for generation
        
        Returns:
            List of recurring invoices due today or past due
        """
        db = SessionLocal()
        
        try:
            today = datetime.now().date().strftime("%Y-%m-%d")
            
            # Get active recurring invoices due today or before
            recurring_list = db.query(RecurringInvoice).filter(
                RecurringInvoice.status == "active",
                RecurringInvoice.next_invoice_date <= today
            ).all()
            
            result = []
            for rec in recurring_list:
                # Check if end date passed
                if rec.end_date and rec.end_date < today:
                    rec.status = "completed"
                    db.commit()
                    continue
                
                result.append({
                    'id': rec.id,
                    'template_name': rec.template_name,
                    'frequency': rec.frequency,
                    'next_invoice_date': rec.next_invoice_date,
                    'customer_id': rec.customer_id,
                    'invoice_template': json.loads(rec.invoice_template),
                    'auto_send': rec.auto_send == "true"
                })
            
            return result
            
        finally:
            db.close()
    
    @staticmethod
    def generate_invoice_from_template(template_id: int) -> Dict:
        """
        Generate an invoice from recurring template
        
        Args:
            template_id: Recurring invoice template ID
            
        Returns:
            Generated invoice data
        """
        db = SessionLocal()
        
        try:
            recurring = db.query(RecurringInvoice).filter(
                RecurringInvoice.id == template_id
            ).first()
            
            if not recurring:
                return {
                    'success': False,
                    'error': 'Template not found'
                }
            
            # Parse template
            template_data = json.loads(recurring.invoice_template)
            
            # Calculate next invoice date
            current_next = datetime.strptime(recurring.next_invoice_date, "%Y-%m-%d")
            freq_days = RecurringAgent.FREQUENCIES[recurring.frequency]['days']
            new_next = current_next + timedelta(days=freq_days)
            
            # Update recurring invoice
            recurring.next_invoice_date = new_next.strftime("%Y-%m-%d")
            recurring.invoices_generated += 1
            recurring.last_generated = datetime.now()
            
            # Check if should complete
            if recurring.end_date and new_next.strftime("%Y-%m-%d") > recurring.end_date:
                recurring.status = "completed"
            
            db.commit()
            
            return {
                'success': True,
                'invoice_data': template_data,
                'template_id': template_id,
                'auto_send': recurring.auto_send == "true"
            }
            
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            db.close()
    
    @staticmethod
    def get_all_recurring() -> List[Dict]:
        """Get all recurring invoice templates"""
        db = SessionLocal()
        
        try:
            recurring_list = db.query(RecurringInvoice).all()
            
            result = []
            for rec in recurring_list:
                template_data = json.loads(rec.invoice_template)
                
                result.append({
                    'id': rec.id,
                    'template_name': rec.template_name,
                    'customer_name': template_data['customer']['name'],
                    'frequency': rec.frequency,
                    'frequency_name': RecurringAgent.FREQUENCIES[rec.frequency]['name'],
                    'start_date': rec.start_date,
                    'end_date': rec.end_date,
                    'next_invoice_date': rec.next_invoice_date,
                    'status': rec.status,
                    'auto_send': rec.auto_send == "true",
                    'invoices_generated': rec.invoices_generated,
                    'last_generated': rec.last_generated.strftime("%Y-%m-%d %H:%M:%S") if rec.last_generated else None
                })
            
            return result
            
        finally:
            db.close()
    
    @staticmethod
    def update_status(template_id: int, status: str) -> Dict:
        """
        Update recurring invoice status
        
        Args:
            template_id: Template ID
            status: active, paused, cancelled, completed
        """
        db = SessionLocal()
        
        try:
            recurring = db.query(RecurringInvoice).filter(
                RecurringInvoice.id == template_id
            ).first()
            
            if not recurring:
                return {
                    'success': False,
                    'error': 'Template not found'
                }
            
            recurring.status = status
            db.commit()
            
            return {
                'success': True,
                'message': f'Status updated to {status}'
            }
            
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            db.close()


def test_recurring_agent():
    """Test recurring agent"""
    print("🧪 TESTING RECURRING AGENT\n")
    
    # Test 1: Create recurring invoice
    print("Test 1: Create recurring invoice")
    result = RecurringAgent.create_recurring_invoice(
        template_name="Monthly Rent - ABC Corp",
        customer_data={
            'name': 'ABC Corporation',
            'phone': '9876543210',
            'email': 'abc@example.com',
            'address': 'Mumbai'
        },
        items=[
            {
                'name': 'Office Rent',
                'price': 50000,
                'quantity': 1,
                'gst_rate': 18
            }
        ],
        frequency='monthly',
        start_date='2025-02-01',
        end_date='2025-12-31',
        auto_send=True
    )
    print(f"✅ {result['message']}\n")
    
    # Test 2: Get all recurring
    print("Test 2: Get all recurring invoices")
    all_recurring = RecurringAgent.get_all_recurring()
    print(f"✅ Found {len(all_recurring)} recurring invoice(s)\n")
    
    # Test 3: Get due invoices
    print("Test 3: Get due invoices")
    due = RecurringAgent.get_due_invoices()
    print(f"✅ {len(due)} invoice(s) due for generation\n")
    
    print("="*50)
    print("✅ RECURRING AGENT READY!")
    print("="*50)


if __name__ == "__main__":
    test_recurring_agent()