"""
PDF Generator Agent
Converts invoice data to beautiful PDF (Windows-friendly version)
Author: Bunny Rangu
Day: 6/30
"""

from xhtml2pdf import pisa
from jinja2 import Template
import os
from typing import Dict, List
import sys
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class PDFGenerator:
    """Generate professional PDF invoices with multiple templates"""
    
    TEMPLATES = {
        'modern': 'invoice_templates/modern.html',
        'classic': 'invoice_templates/classic.html',
        'minimal': 'invoice_templates/minimal.html'
    }
    
    def __init__(self, template: str = 'modern'):
        """
        Initialize PDF generator
        
        Args:
            template: Template name ('modern', 'classic', or 'minimal')
        """
        self.set_template(template)
    
    def set_template(self, template: str):
        """
        Set the template to use
        
        Args:
            template: Template name
        """
        if template not in self.TEMPLATES:
            template = 'modern'  # Default
        
        current_dir = os.path.dirname(__file__)
        template_path = os.path.join(
            current_dir, 
            '../templates', 
            self.TEMPLATES[template]
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template_content = f.read()
        
        self.current_template = template
    
    def generate_pdf(self, invoice_data: Dict, output_path: str = None, template: str = None) -> str:
        """
        Generate PDF from invoice data
        
        Args:
            invoice_data: Complete invoice dictionary
            output_path: Path to save PDF (optional)
            template: Template to use (optional, overrides default)
            
        Returns:
            Path to generated PDF file
        """
        # Use specified template if provided
        if template and template != self.current_template:
            self.set_template(template)
        
        # Create Jinja2 template
        template_obj = Template(self.template_content)
        
        # Render HTML with invoice data
        html_content = template_obj.render(**invoice_data)
        
        # Generate output path if not provided
        if output_path is None:
            invoices_dir = 'invoices'
            if not os.path.exists(invoices_dir):
                os.makedirs(invoices_dir)
            
            output_path = os.path.join(
                invoices_dir,
                f"{invoice_data['invoice_number']}.pdf"
            )
        
        # Generate PDF
        with open(output_path, 'w+b') as pdf_file:
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=pdf_file,
                encoding='utf-8'
            )
        
        if pisa_status.err:
            raise Exception(f"PDF generation failed: {pisa_status.err}")
        
        return output_path
    
    def generate_pdf_bytes(self, invoice_data: Dict, template: str = None) -> bytes:
        """
        Generate PDF as bytes (for API responses)
        
        Args:
            invoice_data: Complete invoice dictionary
            template: Template to use (optional)
            
        Returns:
            PDF file as bytes
        """
        # Use specified template if provided
        if template and (not hasattr(self, 'current_template') or template != self.current_template):
            self.set_template(template)
        
        # Create Jinja2 template
        template_obj = Template(self.template_content)
        
        # Render HTML with invoice data
        html_content = template_obj.render(**invoice_data)
        
        # Generate PDF bytes
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(
            html_content,
            dest=pdf_buffer,
            encoding='utf-8'
        )
        
        if pisa_status.err:
            raise Exception(f"PDF generation failed: {pisa_status.err}")
        
        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()
        
        return pdf_bytes

    @staticmethod
    def get_available_templates() -> List[str]:
        """Get list of available template names"""
        return list(PDFGenerator.TEMPLATES.keys())

def test_pdf_generator():
    """Test PDF generation"""
    print("🧪 TESTING PDF GENERATOR (Windows Version)\n")
    
    # Sample invoice data
    invoice_data = {
        'invoice_number': 'INV-2025-1001',
        'date': '2025-02-14',
        'time': '10:30:00',
        'status': 'PAID',
        'payment_status': 'Paid',
        'payment_method': 'UPI',
        'company': {
            'name': 'AI Tax Solutions',
            'address': 'Hyderabad, Telangana',
            'gst_number': '36AABCU9603R1ZM',
            'phone': '9876543210',
            'email': 'info@aitaxsolutions.com'
        },
        'customer': {
            'name': 'Bunny Rangu',
            'phone': '9876543210',
            'email': 'bunny@example.com',
            'address': 'Hyderabad, Telangana',
            'gst_number': '36ABCDE1234F1Z5',
            'state': 'Telangana'
        },
        'items': [
            {
                'name': 'MacBook Pro 16"',
                'description': 'M3 Max, 64GB RAM, 1TB SSD',
                'hsn_code': '8471',
                'quantity': 1,
                'unit_price': 350000,
                'subtotal': 350000,
                'gst_rate': 18,
                'cgst_rate': 9,
                'sgst_rate': 9,
                'cgst_amount': 31500,
                'sgst_amount': 31500,
                'total_gst': 63000,
                'total_amount': 413000
            },
            {
                'name': 'Magic Mouse',
                'description': 'Wireless, Rechargeable',
                'hsn_code': '8471',
                'quantity': 2,
                'unit_price': 8000,
                'subtotal': 16000,
                'gst_rate': 18,
                'cgst_rate': 9,
                'sgst_rate': 9,
                'cgst_amount': 1440,
                'sgst_amount': 1440,
                'total_gst': 2880,
                'total_amount': 18880
            }
        ],
        'totals': {
            'subtotal': 366000,
            'total_cgst': 32940,
            'total_sgst': 32940,
            'total_gst': 65880,
            'grand_total': 431880,
            'total_items': 2,
            'total_quantity': 3
        },
        'notes': 'Thank you for your business! Payment received via UPI.'
    }
    
    # Generate PDF
    generator = PDFGenerator()
    
    try:
        pdf_path = generator.generate_pdf(invoice_data)
        print(f"✅ PDF generated successfully!")
        print(f"📄 Saved to: {pdf_path}")
        print(f"\n✨ Open the PDF to see your invoice!")
        print(f"\n💡 Location: {os.path.abspath(pdf_path)}")
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")


if __name__ == "__main__":
    test_pdf_generator()