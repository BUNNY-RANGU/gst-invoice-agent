"""
Excel Export Agent
Export invoices and reports to Excel
Author: Bunny Rangu
Day: 10/30
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict
import os


class ExcelExporter:
    """Export invoices and reports to Excel"""
    
    def __init__(self):
        """Initialize Excel exporter"""
        # Create exports directory
        self.exports_dir = 'exports'
        if not os.path.exists(self.exports_dir):
            os.makedirs(self.exports_dir)
    
    def export_invoices(self, invoices: List[Dict], filename: str = None) -> str:
        """
        Export invoices to Excel
        
        Args:
            invoices: List of invoice dictionaries
            filename: Output filename (optional)
            
        Returns:
            Path to generated Excel file
        """
        if not invoices:
            raise ValueError("No invoices to export")
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"invoices_{timestamp}.xlsx"
        
        filepath = os.path.join(self.exports_dir, filename)
        
        # Prepare data for export
        rows = []
        for inv in invoices:
            for item in inv['items']:
                rows.append({
                    'Invoice Number': inv['invoice_number'],
                    'Date': inv['date'],
                    'Customer Name': inv['customer']['name'],
                    'Customer Phone': inv['customer']['phone'],
                    'Customer Email': inv['customer'].get('email', ''),
                    'Customer GST': inv['customer'].get('gst_number', ''),
                    'Item Name': item['name'],
                    'Item Description': item.get('description', ''),
                    'HSN Code': item.get('hsn_code', ''),
                    'Quantity': item['quantity'],
                    'Unit Price': item['unit_price'],
                    'Subtotal': item['subtotal'],
                    'GST Rate (%)': item['gst_rate'],
                    'CGST': item['cgst_amount'],
                    'SGST': item['sgst_amount'],
                    'Total GST': item['total_gst'],
                    'Total Amount': item['total_amount'],
                    'Payment Status': inv['payment_status'],
                    'Payment Method': inv.get('payment_method', ''),
                })
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Create Excel writer with formatting
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Invoices', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Invoices']
            
            # Add formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#2563eb',
                'font_color': 'white',
                'border': 1
            })
            
            currency_format = workbook.add_format({'num_format': '₹#,##0.00'})
            
            # Format header row
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Format currency columns
            currency_cols = ['Unit Price', 'Subtotal', 'CGST', 'SGST', 'Total GST', 'Total Amount']
            for col_name in currency_cols:
                if col_name in df.columns:
                    col_idx = df.columns.get_loc(col_name)
                    worksheet.set_column(col_idx, col_idx, 12, currency_format)
            
            # Auto-fit columns
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, min(max_len, 30))
        
        return filepath
    
    def export_gst_summary(self, invoices: List[Dict], month: str = None, filename: str = None) -> str:
        """
        Export GST summary report
        
        Args:
            invoices: List of invoice dictionaries
            month: Month filter (YYYY-MM) (optional)
            filename: Output filename (optional)
            
        Returns:
            Path to generated Excel file
        """
        if not invoices:
            raise ValueError("No invoices to export")
        
        # Filter by month if provided
        if month:
            invoices = [inv for inv in invoices if inv['date'].startswith(month)]
        
        if not invoices:
            raise ValueError(f"No invoices found for {month}")
        
        # Generate filename
        if filename is None:
            month_str = month.replace('-', '_') if month else datetime.now().strftime("%Y%m")
            filename = f"gst_summary_{month_str}.xlsx"
        
        filepath = os.path.join(self.exports_dir, filename)
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Total Invoices',
                    'Total Revenue',
                    'Total CGST Collected',
                    'Total SGST Collected',
                    'Total GST Collected',
                    'Average Invoice Value'
                ],
                'Value': [
                    len(invoices),
                    sum(inv['totals']['grand_total'] for inv in invoices),
                    sum(inv['totals']['total_cgst'] for inv in invoices),
                    sum(inv['totals']['total_sgst'] for inv in invoices),
                    sum(inv['totals']['total_gst'] for inv in invoices),
                    sum(inv['totals']['grand_total'] for inv in invoices) / len(invoices)
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format summary
            worksheet = writer.sheets['Summary']
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#2563eb',
                'font_color': 'white'
            })
            
            currency_format = workbook.add_format({'num_format': '₹#,##0.00'})
            
            for col_num, value in enumerate(summary_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            worksheet.set_column(1, 1, 15, currency_format)
            worksheet.set_column(0, 0, 25)
            
            # GST Rate-wise breakdown
            gst_breakdown = {}
            for inv in invoices:
                for item in inv['items']:
                    rate = item['gst_rate']
                    if rate not in gst_breakdown:
                        gst_breakdown[rate] = {
                            'taxable_value': 0,
                            'cgst': 0,
                            'sgst': 0,
                            'total_gst': 0
                        }
                    gst_breakdown[rate]['taxable_value'] += item['subtotal']
                    gst_breakdown[rate]['cgst'] += item['cgst_amount']
                    gst_breakdown[rate]['sgst'] += item['sgst_amount']
                    gst_breakdown[rate]['total_gst'] += item['total_gst']
            
            breakdown_rows = []
            for rate, values in sorted(gst_breakdown.items()):
                breakdown_rows.append({
                    'GST Rate (%)': rate,
                    'Taxable Value': values['taxable_value'],
                    'CGST': values['cgst'],
                    'SGST': values['sgst'],
                    'Total GST': values['total_gst']
                })
            
            breakdown_df = pd.DataFrame(breakdown_rows)
            breakdown_df.to_excel(writer, sheet_name='GST Breakdown', index=False)
            
            # Format breakdown
            worksheet = writer.sheets['GST Breakdown']
            for col_num, value in enumerate(breakdown_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            for i in range(1, 5):
                worksheet.set_column(i, i, 15, currency_format)
            
            # Invoice list
            invoice_list = []
            for inv in invoices:
                invoice_list.append({
                    'Invoice Number': inv['invoice_number'],
                    'Date': inv['date'],
                    'Customer': inv['customer']['name'],
                    'Subtotal': inv['totals']['subtotal'],
                    'CGST': inv['totals']['total_cgst'],
                    'SGST': inv['totals']['total_sgst'],
                    'Total GST': inv['totals']['total_gst'],
                    'Grand Total': inv['totals']['grand_total'],
                    'Payment Status': inv['payment_status']
                })
            
            invoice_df = pd.DataFrame(invoice_list)
            invoice_df.to_excel(writer, sheet_name='Invoice List', index=False)
            
            # Format invoice list
            worksheet = writer.sheets['Invoice List']
            for col_num, value in enumerate(invoice_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            for i in range(3, 8):
                worksheet.set_column(i, i, 12, currency_format)
        
        return filepath
    
    def export_customer_report(self, invoices: List[Dict], filename: str = None) -> str:
        """
        Export customer-wise report
        
        Args:
            invoices: List of invoice dictionaries
            filename: Output filename (optional)
            
        Returns:
            Path to generated Excel file
        """
        if not invoices:
            raise ValueError("No invoices to export")
        
        # Generate filename
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"customer_report_{timestamp}.xlsx"
        
        filepath = os.path.join(self.exports_dir, filename)
        
        # Aggregate by customer
        customer_data = {}
        for inv in invoices:
            customer_name = inv['customer']['name']
            if customer_name not in customer_data:
                customer_data[customer_name] = {
                    'phone': inv['customer']['phone'],
                    'email': inv['customer'].get('email', ''),
                    'invoice_count': 0,
                    'total_amount': 0,
                    'total_gst': 0,
                    'last_invoice_date': inv['date']
                }
            
            customer_data[customer_name]['invoice_count'] += 1
            customer_data[customer_name]['total_amount'] += inv['totals']['grand_total']
            customer_data[customer_name]['total_gst'] += inv['totals']['total_gst']
            
            # Update last invoice date
            if inv['date'] > customer_data[customer_name]['last_invoice_date']:
                customer_data[customer_name]['last_invoice_date'] = inv['date']
        
        # Create DataFrame
        rows = []
        for name, data in customer_data.items():
            rows.append({
                'Customer Name': name,
                'Phone': data['phone'],
                'Email': data['email'],
                'Total Invoices': data['invoice_count'],
                'Total Amount': data['total_amount'],
                'Total GST Paid': data['total_gst'],
                'Last Invoice Date': data['last_invoice_date']
            })
        
        df = pd.DataFrame(rows)
        df = df.sort_values('Total Amount', ascending=False)
        
        # Export to Excel
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Customer Report', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Customer Report']
            
            # Formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#2563eb',
                'font_color': 'white'
            })
            
            currency_format = workbook.add_format({'num_format': '₹#,##0.00'})
            
            # Apply formats
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            worksheet.set_column(4, 5, 15, currency_format)
            
            # Auto-fit columns
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, min(max_len, 25))
        
        return filepath


def test_excel_exporter():
    """Test Excel export"""
    print("🧪 TESTING EXCEL EXPORTER\n")
    
    # Sample invoice data
    sample_invoices = [
        {
            'invoice_number': 'INV-2025-1001',
            'date': '2025-02-14',
            'customer': {
                'name': 'Test Customer 1',
                'phone': '9876543210',
                'email': 'test1@example.com',
                'gst_number': '27ABCDE1234F1Z5'
            },
            'items': [
                {
                    'name': 'Product A',
                    'description': 'Test product',
                    'hsn_code': '8471',
                    'quantity': 2,
                    'unit_price': 5000,
                    'subtotal': 10000,
                    'gst_rate': 18,
                    'cgst_amount': 900,
                    'sgst_amount': 900,
                    'total_gst': 1800,
                    'total_amount': 11800
                }
            ],
            'totals': {
                'subtotal': 10000,
                'total_cgst': 900,
                'total_sgst': 900,
                'total_gst': 1800,
                'grand_total': 11800
            },
            'payment_status': 'Paid',
            'payment_method': 'UPI'
        }
    ]
    
    exporter = ExcelExporter()
    
    try:
        # Test invoice export
        filepath = exporter.export_invoices(sample_invoices)
        print(f"✅ Invoice export created: {filepath}")
        
        # Test GST summary
        gst_filepath = exporter.export_gst_summary(sample_invoices, month='2025-02')
        print(f"✅ GST summary created: {gst_filepath}")
        
        # Test customer report
        customer_filepath = exporter.export_customer_report(sample_invoices)
        print(f"✅ Customer report created: {customer_filepath}")
        
        print(f"\n📂 All exports saved to: {os.path.abspath(exporter.exports_dir)}")
        print("✨ Excel exporter ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_excel_exporter()