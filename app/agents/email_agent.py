"""
Email Agent
Send invoices via email with PDF attachment
Author: Bunny Rangu
Day: 8/30
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.agents.pdf_generator import PDFGenerator


class EmailAgent:
    """Send invoices via email"""
    
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        """
        Initialize email agent
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.pdf_generator = PDFGenerator()
    
    def create_email_html(self, invoice_data: Dict) -> str:
        """
        Create HTML email body
        
        Args:
            invoice_data: Invoice dictionary
            
        Returns:
            HTML email content
        """
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; }}
                    .invoice-box {{ background: #f3f4f6; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; border-top: 1px solid #e5e7eb; }}
                    .button {{ background: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Tax Invoice</h1>
                    <p>{invoice_data['company']['name']}</p>
                </div>
                
                <div class="content">
                    <p>Dear {invoice_data['customer']['name']},</p>
                    
                    <p>Thank you for your business! Please find your invoice attached.</p>
                    
                    <div class="invoice-box">
                        <h3>Invoice Details</h3>
                        <p><strong>Invoice Number:</strong> {invoice_data['invoice_number']}</p>
                        <p><strong>Date:</strong> {invoice_data['date']}</p>
                        <p><strong>Amount:</strong> ₹{invoice_data['totals']['grand_total']:,.2f}</p>
                        <p><strong>GST:</strong> ₹{invoice_data['totals']['total_gst']:,.2f}</p>
                    </div>
                    
                    <p>The invoice PDF is attached to this email.</p>
                    
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    
                    <p>Best regards,<br>
                    <strong>{invoice_data['company']['name']}</strong><br>
                    {invoice_data['company']['phone']}<br>
                    {invoice_data['company']['email']}</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this email.</p>
                    <p>{invoice_data['company']['name']} | {invoice_data['company']['address']}</p>
                </div>
            </body>
        </html>
        """
        return html
    
    def send_invoice_email(
        self,
        invoice_data: Dict,
        sender_email: str,
        sender_password: str,
        recipient_email: str = None
    ) -> Dict:
        """
        Send invoice via email
        
        Args:
            invoice_data: Complete invoice dictionary
            sender_email: Sender's email address
            sender_password: Sender's email password/app password
            recipient_email: Recipient email (defaults to customer email)
            
        Returns:
            Success/failure dictionary
        """
        try:
            # Use customer email if recipient not specified
            if recipient_email is None:
                recipient_email = invoice_data['customer'].get('email')
            
            if not recipient_email:
                return {
                    'success': False,
                    'error': 'No recipient email address provided'
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Invoice {invoice_data['invoice_number']} from {invoice_data['company']['name']}"
            
            # Create HTML body
            html_body = self.create_email_html(invoice_data)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Generate and attach PDF
            pdf_bytes = self.pdf_generator.generate_pdf_bytes(invoice_data)
            pdf_attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
            pdf_attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=f"{invoice_data['invoice_number']}.pdf"
            )
            msg.attach(pdf_attachment)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            return {
                'success': True,
                'message': f'Invoice sent to {recipient_email}',
                'recipient': recipient_email
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def test_email_agent():
    """Test email sending (dry run - no actual email sent)"""
    print("🧪 TESTING EMAIL AGENT\n")
    
    # Sample invoice data
    invoice_data = {
        'invoice_number': 'INV-2025-TEST',
        'date': '2025-02-14',
        'company': {
            'name': 'AI Tax Solutions',
            'address': 'Hyderabad, Telangana',
            'phone': '9876543210',
            'email': 'info@aitaxsolutions.com'
        },
        'customer': {
            'name': 'Test Customer',
            'email': 'test@example.com'
        },
        'totals': {
            'grand_total': 50000,
            'total_gst': 9000
        }
    }
    
    # Create agent
    agent = EmailAgent()
    
    # Test HTML generation
    html = agent.create_email_html(invoice_data)
    
    print("✅ Email HTML template generated successfully!")
    print(f"📧 Would send to: {invoice_data['customer']['email']}")
    print(f"📄 Subject: Invoice {invoice_data['invoice_number']}")
    print("\n💡 To actually send emails, you need:")
    print("   1. Gmail account with App Password enabled")
    print("   2. Call send_invoice_email() with credentials")
    print("\nEmail agent is ready! ✨")


if __name__ == "__main__":
    test_email_agent()