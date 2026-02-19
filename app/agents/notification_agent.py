"""
Notification Agent
Automated email notifications and reminders
Author: Bunny Rangu
Day: 16/30
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template


class NotificationAgent:
    """Handle all automated notifications and reminders"""
    
    def __init__(self):
        self.templates = {
            'payment_reminder': self._get_payment_reminder_template(),
            'overdue_alert': self._get_overdue_alert_template(),
            'payment_received': self._get_payment_received_template(),
            'weekly_summary': self._get_weekly_summary_template()
        }
    
    def _get_payment_reminder_template(self) -> str:
        """Payment reminder email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
                .invoice-box { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }
                .amount { font-size: 28px; font-weight: bold; color: #667eea; }
                .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💰 Payment Reminder</h1>
                </div>
                <div class="content">
                    <p>Dear {{ customer_name }},</p>
                    
                    <p>This is a friendly reminder about your pending invoice:</p>
                    
                    <div class="invoice-box">
                        <h3>Invoice Details</h3>
                        <p><strong>Invoice Number:</strong> {{ invoice_number }}</p>
                        <p><strong>Invoice Date:</strong> {{ invoice_date }}</p>
                        <p><strong>Due Date:</strong> {{ due_date }}</p>
                        <p><strong>Amount Due:</strong> <span class="amount">₹{{ amount_due }}</span></p>
                    </div>
                    
                    <p>Please process the payment at your earliest convenience.</p>
                    
                    <p>If you have already made the payment, please disregard this reminder.</p>
                    
                    <p>Thank you for your business!</p>
                    
                    <div class="footer">
                        <p>{{ company_name }}</p>
                        <p>{{ company_email }} | {{ company_phone }}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_overdue_alert_template(self) -> str:
        """Overdue invoice alert template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
                .alert-box { background: #fee2e2; border-left: 4px solid #dc2626; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .amount { font-size: 28px; font-weight: bold; color: #dc2626; }
                .days-overdue { background: #dc2626; color: white; padding: 5px 15px; border-radius: 20px; display: inline-block; margin: 10px 0; }
                .footer { text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ OVERDUE INVOICE ALERT</h1>
                </div>
                <div class="content">
                    <p>Dear {{ customer_name }},</p>
                    
                    <div class="alert-box">
                        <h3>⚠️ Payment Overdue</h3>
                        <p>Your invoice is <span class="days-overdue">{{ days_overdue }} days overdue</span></p>
                    </div>
                    
                    <h3>Invoice Details</h3>
                    <p><strong>Invoice Number:</strong> {{ invoice_number }}</p>
                    <p><strong>Invoice Date:</strong> {{ invoice_date }}</p>
                    <p><strong>Due Date:</strong> {{ due_date }}</p>
                    <p><strong>Amount Due:</strong> <span class="amount">₹{{ amount_due }}</span></p>
                    
                    <p><strong>Please make the payment immediately to avoid any late fees.</strong></p>
                    
                    <p>If you have any questions or concerns, please contact us.</p>
                    
                    <div class="footer">
                        <p>{{ company_name }}</p>
                        <p>{{ company_email }} | {{ company_phone }}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_payment_received_template(self) -> str:
        """Payment received confirmation template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
                .success-box { background: #d1fae5; border-left: 4px solid #059669; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .amount { font-size: 28px; font-weight: bold; color: #059669; }
                .checkmark { font-size: 48px; color: #059669; }
                .footer { text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="checkmark">✅</div>
                    <h1>Payment Received!</h1>
                </div>
                <div class="content">
                    <p>Dear {{ customer_name }},</p>
                    
                    <div class="success-box">
                        <h3>✅ Payment Confirmed</h3>
                        <p>We have received your payment of <span class="amount">₹{{ payment_amount }}</span></p>
                    </div>
                    
                    <h3>Payment Details</h3>
                    <p><strong>Invoice Number:</strong> {{ invoice_number }}</p>
                    <p><strong>Payment Date:</strong> {{ payment_date }}</p>
                    <p><strong>Payment Method:</strong> {{ payment_method }}</p>
                    {% if transaction_id %}
                    <p><strong>Transaction ID:</strong> {{ transaction_id }}</p>
                    {% endif %}
                    <p><strong>Amount Paid:</strong> ₹{{ payment_amount }}</p>
                    {% if remaining_amount > 0 %}
                    <p><strong>Remaining Balance:</strong> ₹{{ remaining_amount }}</p>
                    {% else %}
                    <p style="color: #059669; font-weight: bold;">✅ Invoice Fully Paid!</p>
                    {% endif %}
                    
                    <p>Thank you for your prompt payment!</p>
                    
                    <div class="footer">
                        <p>{{ company_name }}</p>
                        <p>{{ company_email }} | {{ company_phone }}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_weekly_summary_template(self) -> str:
        """Weekly business summary template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
                .stat-box { background: white; padding: 15px; border-radius: 8px; margin: 10px 0; display: flex; justify-content: space-between; align-items: center; }
                .stat-value { font-size: 24px; font-weight: bold; color: #667eea; }
                .alert { background: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; border-radius: 8px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Weekly Business Summary</h1>
                    <p>{{ week_start }} to {{ week_end }}</p>
                </div>
                <div class="content">
                    <h3>This Week's Performance</h3>
                    
                    <div class="stat-box">
                        <span>New Invoices</span>
                        <span class="stat-value">{{ new_invoices }}</span>
                    </div>
                    
                    <div class="stat-box">
                        <span>Revenue Generated</span>
                        <span class="stat-value">₹{{ revenue }}</span>
                    </div>
                    
                    <div class="stat-box">
                        <span>Payments Received</span>
                        <span class="stat-value">₹{{ payments_received }}</span>
                    </div>
                    
                    <div class="stat-box">
                        <span>Outstanding Amount</span>
                        <span class="stat-value">₹{{ outstanding }}</span>
                    </div>
                    
                    {% if overdue_count > 0 %}
                    <div class="alert">
                        <h4>⚠️ Attention Required</h4>
                        <p><strong>{{ overdue_count }} overdue invoices</strong> totaling ₹{{ overdue_amount }}</p>
                        <p>Please follow up on these payments.</p>
                    </div>
                    {% endif %}
                    
                    <div class="footer">
                        <p>{{ company_name }}</p>
                        <p>Automated Weekly Report</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str,
        from_password: str
    ) -> Dict:
        """
        Send email notification
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML email body
            from_email: Sender email
            from_password: Sender email password/app password
            
        Returns:
            Success/failure dictionary
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = from_email
            message['To'] = to_email
            
            # Attach HTML
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(from_email, from_password)
                server.send_message(message)
            
            return {
                'success': True,
                'message': f'Email sent to {to_email}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_payment_reminder(
        self,
        invoice_data: Dict,
        company_info: Dict,
        email_config: Dict
    ) -> Dict:
        """Send payment reminder email"""
        
        template = Template(self.templates['payment_reminder'])
        
        html = template.render(
            customer_name=invoice_data['customer']['name'],
            invoice_number=invoice_data['invoice_number'],
            invoice_date=invoice_data['date'],
            due_date=invoice_data.get('due_date', 'Upon receipt'),
            amount_due=f"{invoice_data['totals']['grand_total']:,.2f}",
            company_name=company_info['name'],
            company_email=company_info['email'],
            company_phone=company_info['phone']
        )
        
        return self.send_email(
            to_email=invoice_data['customer']['email'],
            subject=f"Payment Reminder - Invoice {invoice_data['invoice_number']}",
            html_content=html,
            from_email=email_config['from_email'],
            from_password=email_config['password']
        )
    
    def send_overdue_alert(
        self,
        invoice_data: Dict,
        days_overdue: int,
        company_info: Dict,
        email_config: Dict
    ) -> Dict:
        """Send overdue invoice alert"""
        
        template = Template(self.templates['overdue_alert'])
        
        html = template.render(
            customer_name=invoice_data['customer']['name'],
            invoice_number=invoice_data['invoice_number'],
            invoice_date=invoice_data['date'],
            due_date=invoice_data.get('due_date', 'N/A'),
            amount_due=f"{invoice_data['totals']['grand_total']:,.2f}",
            days_overdue=days_overdue,
            company_name=company_info['name'],
            company_email=company_info['email'],
            company_phone=company_info['phone']
        )
        
        return self.send_email(
            to_email=invoice_data['customer']['email'],
            subject=f"⚠️ OVERDUE - Invoice {invoice_data['invoice_number']}",
            html_content=html,
            from_email=email_config['from_email'],
            from_password=email_config['password']
        )
    
    def send_payment_confirmation(
        self,
        invoice_data: Dict,
        payment_data: Dict,
        company_info: Dict,
        email_config: Dict
    ) -> Dict:
        """Send payment received confirmation"""
        
        template = Template(self.templates['payment_received'])
        
        html = template.render(
            customer_name=invoice_data['customer']['name'],
            invoice_number=invoice_data['invoice_number'],
            payment_date=payment_data['date'],
            payment_method=payment_data['method'],
            transaction_id=payment_data.get('transaction_id'),
            payment_amount=f"{payment_data['amount']:,.2f}",
            remaining_amount=invoice_data['totals']['grand_total'] - payment_data['amount'],
            company_name=company_info['name'],
            company_email=company_info['email'],
            company_phone=company_info['phone']
        )
        
        return self.send_email(
            to_email=invoice_data['customer']['email'],
            subject=f"✅ Payment Received - Invoice {invoice_data['invoice_number']}",
            html_content=html,
            from_email=email_config['from_email'],
            from_password=email_config['password']
        )


def test_notification_agent():
    """Test notification agent"""
    print("🧪 TESTING NOTIFICATION AGENT\n")
    
    notif = NotificationAgent()
    
    print("✅ Payment Reminder Template")
    print(f"   Template loaded: {len(notif.templates['payment_reminder'])} chars\n")
    
    print("✅ Overdue Alert Template")
    print(f"   Template loaded: {len(notif.templates['overdue_alert'])} chars\n")
    
    print("✅ Payment Received Template")
    print(f"   Template loaded: {len(notif.templates['payment_received'])} chars\n")
    
    print("✅ Weekly Summary Template")
    print(f"   Template loaded: {len(notif.templates['weekly_summary'])} chars\n")
    
    print("="*50)
    print("✅ NOTIFICATION AGENT READY!")
    print("="*50)


if __name__ == "__main__":
    test_notification_agent()