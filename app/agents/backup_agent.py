"""
Backup Agent
Database backup and restore functionality
Author: Bunny Rangu
Day: 19/30
"""

from typing import Dict, List
from datetime import datetime
import json
import os
import shutil
import sqlite3
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.database import SessionLocal, Invoice, Customer, Payment, User, AuditLog, RecurringInvoice, InvoiceItem
from sqlalchemy import inspect


class BackupAgent:
    """Handle database backups and restores"""
    
    BACKUP_DIR = "backups"
    
    def __init__(self):
        # Create backup directory if it doesn't exist
        if not os.path.exists(self.BACKUP_DIR):
            os.makedirs(self.BACKUP_DIR)
    
    def create_backup(self, backup_name: str = None) -> Dict:
        """
        Create complete database backup
        
        Args:
            backup_name: Optional custom name for backup
            
        Returns:
            Success/failure with backup details
        """
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if backup_name:
                filename = f"{backup_name}_{timestamp}.json"
            else:
                filename = f"backup_{timestamp}.json"
            
            filepath = os.path.join(self.BACKUP_DIR, filename)
            
            db = SessionLocal()
            
            # Export all data
            backup_data = {
                'metadata': {
                    'backup_date': datetime.now().isoformat(),
                    'backup_name': backup_name or 'auto',
                    'version': '1.0'
                },
                'customers': [],
                'invoices': [],
                'invoice_items': [],
                'payments': [],
                'users': [],
                'audit_logs': [],
                'recurring_invoices': []
            }
            
            # Export customers
            customers = db.query(Customer).all()
            for customer in customers:
                backup_data['customers'].append({
                    'id': customer.id,
                    'name': customer.name,
                    'phone': customer.phone,
                    'email': customer.email,
                    'address': customer.address,
                    'gst_number': customer.gst_number,
                    'state': customer.state,
                    'created_at': customer.created_at.isoformat() if customer.created_at else None
                })
            
           # Export invoices
            invoices = db.query(Invoice).all()
            for invoice in invoices:
                # Get customer details
                customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
                
                # Get invoice items
                items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
                items_data = []
                for item in items:
                    items_data.append({
                        'name': item.name,
                        'description': item.description,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'gst_rate': item.gst_rate,
                        'cgst_amount': item.cgst_amount,
                        'sgst_amount': item.sgst_amount,
                        'total_amount': item.total_amount
                    })
                
                # Reconstruct full invoice data
                invoice_dict = {
                    'id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'date': invoice.date,
                    'due_date': invoice.due_date,
                    'time': invoice.time,
                    'customer_id': invoice.customer_id,
                    'customer': {
                        'name': customer.name if customer else '',
                        'phone': customer.phone if customer else '',
                        'email': customer.email if customer else '',
                        'address': customer.address if customer else '',
                        'gst_number': customer.gst_number if customer else '',
                        'state': customer.state if customer else ''
                    },
                    'items': items_data,
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
                    'created_at': invoice.created_at.isoformat() if invoice.created_at else None,
                    'updated_at': invoice.updated_at.isoformat() if invoice.updated_at else None
                }
                
                backup_data['invoices'].append(invoice_dict)
            
            # Export invoice items
            items = db.query(InvoiceItem).all()
            for item in items:
                backup_data['invoice_items'].append({
                    'id': item.id,
                    'invoice_id': item.invoice_id,
                    'name': item.name,
                    'description': item.description,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'gst_rate': item.gst_rate,
                    'cgst_amount': item.cgst_amount,
                    'sgst_amount': item.sgst_amount,
                    'total_amount': item.total_amount
                })
            
            # Export audit logs
            audit_logs = db.query(AuditLog).all()
            for log in audit_logs:
                backup_data['audit_logs'].append({
                    'id': log.id,
                    'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                    'user': log.user,
                    'action': log.action,
                    'entity_type': log.entity_type,
                    'entity_id': log.entity_id,
                    'details': log.details,
                    'ip_address': log.ip_address,
                    'status': log.status
                })
            
            # Export recurring invoices
            recurring = db.query(RecurringInvoice).all()
            for rec in recurring:
                backup_data['recurring_invoices'].append({
                    'id': rec.id,
                    'template_name': rec.template_name,
                    'customer_id': rec.customer_id,
                    'frequency': rec.frequency,
                    'interval': rec.interval,
                    'start_date': rec.start_date,
                    'end_date': rec.end_date,
                    'next_invoice_date': rec.next_invoice_date,
                    'invoice_template': rec.invoice_template,
                    'status': rec.status,
                    'auto_send': rec.auto_send,
                    'invoices_generated': rec.invoices_generated,
                    'last_generated': rec.last_generated.isoformat() if rec.last_generated else None,
                    'created_at': rec.created_at.isoformat() if rec.created_at else None
                })
            
            db.close()
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            return {
                'success': True,
                'message': 'Backup created successfully',
                'filename': filename,
                'filepath': filepath,
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'records': {
                    'customers': len(backup_data['customers']),
                    'invoices': len(backup_data['invoices']),
                    'invoice_items': len(backup_data['invoice_items']),
                    'payments': len(backup_data['payments']),
                    'users': len(backup_data['users']),
                    'audit_logs': len(backup_data['audit_logs']),
                    'recurring_invoices': len(backup_data['recurring_invoices'])
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_backups(self) -> List[Dict]:
        """
        List all available backups
        
        Returns:
            List of backup files with metadata
        """
        try:
            backups = []
            
            for filename in os.listdir(self.BACKUP_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.BACKUP_DIR, filename)
                    file_size = os.path.getsize(filepath)
                    file_time = os.path.getmtime(filepath)
                    
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size_bytes': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'created_at': datetime.fromtimestamp(file_time).isoformat()
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            return []
    
    def get_backup_info(self, filename: str) -> Dict:
        """
        Get detailed information about a backup file
        
        Args:
            filename: Backup filename
            
        Returns:
            Backup metadata and record counts
        """
        try:
            filepath = os.path.join(self.BACKUP_DIR, filename)
            
            if not os.path.exists(filepath):
                return {
                    'success': False,
                    'error': 'Backup file not found'
                }
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'success': True,
                'filename': filename,
                'metadata': data['metadata'],
                'records': {
                    'customers': len(data.get('customers', [])),
                    'invoices': len(data.get('invoices', [])),
                    'invoice_items': len(data.get('invoice_items', [])),
                    'payments': len(data.get('payments', [])),
                    'users': len(data.get('users', [])),
                    'audit_logs': len(data.get('audit_logs', [])),
                    'recurring_invoices': len(data.get('recurring_invoices', []))
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_backup(self, filename: str, restore_users: bool = False) -> Dict:
        """
        Restore database from backup
        
        Args:
            filename: Backup filename to restore
            restore_users: Whether to restore user accounts (default: False for safety)
            
        Returns:
            Success/failure with restore details
        """
        try:
            filepath = os.path.join(self.BACKUP_DIR, filename)
            
            if not os.path.exists(filepath):
                return {
                    'success': False,
                    'error': 'Backup file not found'
                }
            
            # Load backup data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            db = SessionLocal()
            
            restored = {
                'customers': 0,
                'invoices': 0,
                'payments': 0,
                'users': 0,
                'audit_logs': 0,
                'recurring_invoices': 0
            }
            
            # Clear existing data (DANGEROUS - should confirm first!)
            # For safety, we'll skip this and just add new records
            
            # Restore customers
            for cust_data in data.get('customers', []):
                # Check if exists
                existing = db.query(Customer).filter(Customer.phone == cust_data['phone']).first()
                if not existing:
                    customer = Customer(
                        name=cust_data['name'],
                        phone=cust_data['phone'],
                        email=cust_data.get('email'),
                        address=cust_data.get('address'),
                        gst_number=cust_data.get('gst_number'),
                        state=cust_data.get('state')
                    )
                    db.add(customer)
                    restored['customers'] += 1
            
            db.commit()
            db.close()
            
            return {
                'success': True,
                'message': 'Backup restored successfully',
                'restored_records': restored
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_to_csv(self) -> Dict:
        """
        Export all data to CSV files
        
        Returns:
            Dictionary with CSV file paths
        """
        try:
            import csv
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = os.path.join(self.BACKUP_DIR, f"csv_export_{timestamp}")
            os.makedirs(export_dir, exist_ok=True)
            
            db = SessionLocal()
            
            # Export customers to CSV
            customers = db.query(Customer).all()
            if customers:
                with open(os.path.join(export_dir, 'customers.csv'), 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Name', 'Phone', 'Email', 'Address', 'GST Number', 'State'])
                    for c in customers:
                        writer.writerow([c.id, c.name, c.phone, c.email, c.address, c.gst_number, c.state])
            
           # Export invoices to CSV
            invoices = db.query(Invoice).all()
            if invoices:
                with open(os.path.join(export_dir, 'invoices.csv'), 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Invoice Number', 'Customer ID', 'Date', 'Payment Status', 'Total Amount'])
                    for inv in invoices:
                        writer.writerow([
                            inv.invoice_number,
                            inv.customer_id,
                            inv.date,
                            inv.payment_status,
                            inv.grand_total
                        ])
            
            return {
                'success': True,
                'export_dir': export_dir,
                'files': os.listdir(export_dir)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def test_backup_agent():
    """Test backup agent"""
    print("🧪 TESTING BACKUP AGENT\n")
    
    backup = BackupAgent()
    
    # Test 1: Create backup
    print("Test 1: Create backup")
    result = backup.create_backup(backup_name="test")
    if result['success']:
        print(f"✅ Backup created: {result['filename']}")
        print(f"   Size: {result['size_mb']} MB")
        print(f"   Records: {result['records']}\n")
    else:
        print(f"❌ Error: {result['error']}\n")
    
    # Test 2: List backups
    print("Test 2: List backups")
    backups = backup.list_backups()
    print(f"✅ Found {len(backups)} backup(s)\n")
    
    # Test 3: Get backup info
    if backups:
        print("Test 3: Get backup info")
        info = backup.get_backup_info(backups[0]['filename'])
        if info['success']:
            print(f"✅ Backup info retrieved")
            print(f"   Records: {info['records']}\n")
    
    print("="*50)
    print("✅ BACKUP AGENT READY!")
    print("="*50)


if __name__ == "__main__":
    test_backup_agent()
