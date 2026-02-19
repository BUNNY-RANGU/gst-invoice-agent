"""
Bulk Operations Agent
Handle mass imports, exports, and batch operations
Author: Bunny Rangu
Day: 14/30
"""

import pandas as pd
from typing import List, Dict
from datetime import datetime
import csv
import io


class BulkOperations:
    """Handle bulk import/export and batch operations"""
    
    def import_customers_from_csv(self, csv_content: str) -> Dict:
        """
        Import multiple customers from CSV
        
        CSV Format:
        name,phone,email,address,gst_number,state
        
        Args:
            csv_content: CSV file content as string
            
        Returns:
            Success/failure with import stats
        """
        try:
            # Read CSV
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Validate required columns
            required = ['name', 'phone']
            missing = [col for col in required if col not in df.columns]
            
            if missing:
                return {
                    'success': False,
                    'error': f'Missing required columns: {", ".join(missing)}'
                }
            
            # Convert to list of dicts
            customers = []
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    customer = {
                        'name': str(row['name']),
                        'phone': str(row['phone']),
                        'email': str(row.get('email', '')),
                        'address': str(row.get('address', '')),
                        'gst_number': str(row.get('gst_number', '')),
                        'state': str(row.get('state', 'Telangana'))
                    }
                    customers.append(customer)
                except Exception as e:
                    errors.append(f'Row {idx + 2}: {str(e)}')
            
            return {
                'success': True,
                'customers': customers,
                'total': len(customers),
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def import_invoices_from_csv(self, csv_content: str) -> Dict:
        """
        Import multiple invoices from CSV
        
        CSV Format:
        customer_name,customer_phone,customer_email,item_name,item_price,quantity,gst_rate,notes
        
        Args:
            csv_content: CSV file content as string
            
        Returns:
            Success/failure with import stats
        """
        try:
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Validate required columns
            required = ['customer_name', 'customer_phone', 'item_name', 'item_price', 'quantity', 'gst_rate']
            missing = [col for col in required if col not in df.columns]
            
            if missing:
                return {
                    'success': False,
                    'error': f'Missing required columns: {", ".join(missing)}'
                }
            
            # Group by customer to create invoices
            invoices = []
            errors = []
            
            for customer_name in df['customer_name'].unique():
                try:
                    customer_rows = df[df['customer_name'] == customer_name]
                    first_row = customer_rows.iloc[0]
                    
                    # Build customer
                    customer = {
                        'name': str(first_row['customer_name']),
                        'phone': str(first_row['customer_phone']),
                        'email': str(first_row.get('customer_email', '')),
                        'address': str(first_row.get('customer_address', '')),
                        'gst_number': str(first_row.get('customer_gst', '')),
                        'state': str(first_row.get('customer_state', 'Telangana'))
                    }
                    
                    # Build items
                    items = []
                    for _, row in customer_rows.iterrows():
                        items.append({
                            'name': str(row['item_name']),
                            'description': str(row.get('item_description', '')),
                            'price': float(row['item_price']),
                            'quantity': int(row['quantity']),
                            'gst_rate': int(row['gst_rate'])
                        })
                    
                    invoices.append({
                        'customer': customer,
                        'items': items,
                        'notes': str(first_row.get('notes', ''))
                    })
                    
                except Exception as e:
                    errors.append(f'Customer {customer_name}: {str(e)}')
            
            return {
                'success': True,
                'invoices': invoices,
                'total': len(invoices),
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_customers_to_csv(self, customers: List[Dict]) -> str:
        """
        Export customers to CSV format
        
        Args:
            customers: List of customer dictionaries
            
        Returns:
            CSV content as string
        """
        if not customers:
            return ""
        
        # Prepare data
        rows = []
        for cust in customers:
            rows.append({
                'name': cust.get('name', ''),
                'phone': cust.get('phone', ''),
                'email': cust.get('email', ''),
                'address': cust.get('address', ''),
                'gst_number': cust.get('gst_number', ''),
                'state': cust.get('state', '')
            })
        
        # Convert to CSV
        df = pd.DataFrame(rows)
        return df.to_csv(index=False)
    
    def export_invoices_to_csv(self, invoices: List[Dict]) -> str:
        """
        Export invoices to CSV format
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            CSV content as string
        """
        if not invoices:
            return ""
        
        # Flatten invoices (one row per item)
        rows = []
        for inv in invoices:
            for item in inv['items']:
                rows.append({
                    'invoice_number': inv['invoice_number'],
                    'date': inv['date'],
                    'customer_name': inv['customer']['name'],
                    'customer_phone': inv['customer']['phone'],
                    'customer_email': inv['customer'].get('email', ''),
                    'item_name': item['name'],
                    'item_description': item.get('description', ''),
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price'],
                    'gst_rate': item['gst_rate'],
                    'total_amount': item['total_amount'],
                    'payment_status': inv['payment_status'],
                    'grand_total': inv['totals']['grand_total']
                })
        
        df = pd.DataFrame(rows)
        return df.to_csv(index=False)
    
    def generate_sample_customer_csv(self) -> str:
        """Generate sample customer CSV template"""
        sample = [
            {
                'name': 'John Doe',
                'phone': '9876543210',
                'email': 'john@example.com',
                'address': 'Mumbai, Maharashtra',
                'gst_number': '27ABCDE1234F1Z5',
                'state': 'Maharashtra'
            },
            {
                'name': 'Jane Smith',
                'phone': '9876543211',
                'email': 'jane@example.com',
                'address': 'Delhi',
                'gst_number': '',
                'state': 'Delhi'
            }
        ]
        
        df = pd.DataFrame(sample)
        return df.to_csv(index=False)
    
    def generate_sample_invoice_csv(self) -> str:
        """Generate sample invoice CSV template"""
        sample = [
            {
                'customer_name': 'John Doe',
                'customer_phone': '9876543210',
                'customer_email': 'john@example.com',
                'customer_address': 'Mumbai',
                'customer_gst': '27ABCDE1234F1Z5',
                'customer_state': 'Maharashtra',
                'item_name': 'Laptop',
                'item_description': 'Dell Inspiron',
                'item_price': 50000,
                'quantity': 1,
                'gst_rate': 18,
                'notes': 'Thank you!'
            },
            {
                'customer_name': 'Jane Smith',
                'customer_phone': '9876543211',
                'customer_email': 'jane@example.com',
                'customer_address': 'Delhi',
                'customer_gst': '',
                'customer_state': 'Delhi',
                'item_name': 'Mouse',
                'item_description': 'Wireless',
                'item_price': 500,
                'quantity': 2,
                'gst_rate': 18,
                'notes': 'Bulk order'
            }
        ]
        
        df = pd.DataFrame(sample)
        return df.to_csv(index=False)


def test_bulk_operations():
    """Test bulk operations"""
    print("🧪 TESTING BULK OPERATIONS\n")
    
    bulk = BulkOperations()
    
    # Test 1: Generate sample CSVs
    print("✅ Generating sample customer CSV...")
    customer_csv = bulk.generate_sample_customer_csv()
    print(f"   {len(customer_csv)} characters\n")
    
    print("✅ Generating sample invoice CSV...")
    invoice_csv = bulk.generate_sample_invoice_csv()
    print(f"   {len(invoice_csv)} characters\n")
    
    # Test 2: Import customers
    print("✅ Importing customers from CSV...")
    result = bulk.import_customers_from_csv(customer_csv)
    print(f"   Imported {result['total']} customers\n")
    
    # Test 3: Import invoices
    print("✅ Importing invoices from CSV...")
    result = bulk.import_invoices_from_csv(invoice_csv)
    print(f"   Imported {result['total']} invoices\n")
    
    print("="*50)
    print("✅ BULK OPERATIONS READY!")
    print("="*50)


if __name__ == "__main__":
    test_bulk_operations()