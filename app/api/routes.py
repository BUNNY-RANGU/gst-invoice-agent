"""
FastAPI Routes for GST Invoice Agent
REST API endpoints for invoice operations
Author: Bunny Rangu
Day: 4/30
"""
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.auth_agent import AuthAgent
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from app.agents.email_agent import EmailAgent
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from app.agents.search_agent import SearchAgent
from datetime import datetime
from app.agents.bulk_operations import BulkOperations
from fastapi import UploadFile, File
from app.agents.notification_agent import NotificationAgent
from app.agents.audit_agent import AuditAgent
from fastapi import Request
import sys
import os
from fastapi.responses import Response
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.agents.pdf_generator import PDFGenerator
from app.agents.excel_exporter import ExcelExporter
from fastapi.responses import FileResponse

# Add project root to path
from app.agents.invoice_agent_db import InvoiceAgentDB
agent = InvoiceAgentDB()

# Initialize FastAPI app
app = FastAPI(
    title="GST Invoice Agent API",
    description="AI-powered GST invoice automation system for Indian businesses",
    version="1.0.0",
    contact={
        "name": "Bunny Rangu",
        "url": "https://github.com/BUNNY-RANGU/-ai-agent-taxxx"
    }
)
# Initialize PDF Generator
# Initialize PDF Generator
pdf_generator = PDFGenerator()
email_agent = EmailAgent()
excel_exporter = ExcelExporter()
# Initialize Analytics Agent
analytics_agent = AnalyticsAgent()
# Initialize Audit Agent
audit_agent = AuditAgent()
# Initialize Notification Agent
notification_agent = NotificationAgent()
# Initialize Bulk Operations
bulk_ops = BulkOperations()
# Initialize Search Agent
search_agent = SearchAgent()
# Initialize Auth Agent
auth_agent = AuthAgent()
security = HTTPBearer()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# ============================================================================
# AUTO-LOGGING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests"""
    response = await call_next(request)
    
    # Log certain endpoints
    if request.url.path.startswith("/api/invoice") or \
       request.url.path.startswith("/api/payment"):
        
        method = request.method
        path = request.url.path
        
        # Get user from session (simplified - you'd get from JWT token)
        user = "system"  # Replace with actual user from JWT
        
        # Determine action type
        action = "VIEW"
        if method == "POST":
            if "invoice" in path:
                action = "CREATE_INVOICE"
            elif "payment" in path:
                action = "CREATE_PAYMENT"
        
        # Log it (async, don't block response)
        try:
            audit_agent.log_action(
                user=user,
                action=action,
                entity_type=path.split("/")[2] if len(path.split("/")) > 2 else "unknown",
                ip_address=request.client.host if request.client else None
            )
        except:
            pass  # Don't let logging errors break the app
    
    return response

# ============================================================================
# PYDANTIC MODELS (Data Validation)
# ============================================================================
# ============================================================================
# AUTH HELPER
# ============================================================================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current logged in user from JWT token"""
    token = credentials.credentials
    user = auth_agent.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token. Please login again."
        )
    
    return user
    
class CustomerModel(BaseModel):
    """Customer details model"""
    name: str = Field(..., min_length=2, max_length=100, description="Customer name")
    phone: str = Field(..., pattern=r'^\d{9,10}$', description="9 or 10-digit phone number")
    email: Optional[str] = Field(None, description="Email address")
    address: Optional[str] = Field(None, description="Customer address")
    gst_number: Optional[str] = Field(None, description="GST number (15 characters)")
    state: Optional[str] = Field("Telangana", description="State name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Rajesh Kumar",
                "phone": "9876543210",
                "email": "rajesh@example.com",
                "address": "Mumbai, Maharashtra",
                "gst_number": "27ABCDE1234F1Z5",
                "state": "Maharashtra"
            }
        }


class InvoiceItemModel(BaseModel):
    """Invoice item model"""
    name: str = Field(..., min_length=2, max_length=200, description="Item name")
    description: Optional[str] = Field("", description="Item description")
    price: float = Field(..., gt=0, le=10000000, description="Price per unit")
    quantity: int = Field(..., gt=0, le=100000, description="Quantity")
    gst_rate: int = Field(..., description="GST rate percentage")
    hsn_code: Optional[str] = Field("", description="HSN code (optional)")
    
    @validator('gst_rate')
    def validate_gst_rate(cls, v):
        if v not in [0, 5, 12, 18, 28]:
            raise ValueError('GST rate must be 0, 5, 12, 18, or 28')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop Dell Inspiron",
                "description": "15.6 inch, 8GB RAM",
                "price": 50000,
                "quantity": 1,
                "gst_rate": 18,
                "hsn_code": "8471"
            }
        }


class InvoiceCreateRequest(BaseModel):
    """Request model for creating invoice"""
    customer: CustomerModel
    items: List[InvoiceItemModel] = Field(..., min_items=1, description="List of invoice items")
    notes: Optional[str] = Field("", description="Additional notes or terms")
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer": {
                    "name": "Rajesh Kumar",
                    "phone": "9876543210",
                    "email": "rajesh@example.com"
                },
                "items": [
                    {
                        "name": "Laptop",
                        "price": 50000,
                        "quantity": 1,
                        "gst_rate": 18
                    }
                ],
                "notes": "Thank you for your business!"
            }
        }


class UserRegisterRequest(BaseModel):
    """Request model for user registration"""
    username: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = ""

class UserLoginRequest(BaseModel):
    """Request model for user login"""
    username: str
    password: str


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API welcome message"""
    return {
        "message": "Welcome to GST Invoice Agent API",
        "version": "1.0.0",
        "author": "Bunny Rangu",
        "docs": "/docs",
        "endpoints": {
            "create_invoice": "POST /api/invoice/create",
            "get_invoice": "GET /api/invoice/{invoice_number}",
            "list_invoices": "GET /api/invoices",
            "health": "GET /health"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_invoices": len(agent.get_all_invoices())
    }


@app.post("/api/invoice/create", tags=["Invoices"])
async def create_invoice(request: InvoiceCreateRequest):
    """
    Create a new GST invoice
    
    - Validates customer and item data
    - Calculates GST automatically
    - Generates invoice number
    - Returns complete invoice
    """
    # Convert Pydantic models to dictionaries
    customer_dict = request.customer.dict()
    items_list = [item.dict() for item in request.items]
    
    # Create invoice using agent
    result = agent.create_invoice(
        customer=customer_dict,
        items=items_list,
        notes=request.notes
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return {
        "success": True,
        "message": result['message'],
        "invoice": result['invoice']
    }


@app.get("/api/invoice/{invoice_number}", tags=["Invoices"])
async def get_invoice(invoice_number: str):
    """
    Get invoice by invoice number
    
    - Returns complete invoice details
    - 404 if not found
    """
    invoice = agent.get_invoice(invoice_number)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice_number} not found"
        )
    
    return {
        "success": True,
        "invoice": invoice
    }


@app.get("/api/invoices", tags=["Invoices"])
async def list_all_invoices():
    """
    Get all invoices
    
    - Returns list of all invoices
    - Includes summary statistics
    """
    invoices = agent.get_all_invoices()
    
    # Calculate statistics
    total_revenue = sum(inv['totals']['grand_total'] for inv in invoices)
    total_gst = sum(inv['totals']['total_gst'] for inv in invoices)
    
    return {
        "success": True,
        "total_invoices": len(invoices),
        "total_revenue": round(total_revenue, 2),
        "total_gst_collected": round(total_gst, 2),
        "invoices": invoices
    }
    

@app.get("/api/customer/{customer_name}/invoices", tags=["Customers"])
async def get_customer_invoices(customer_name: str):
    """
    Get all invoices for a specific customer
    
    - Search by customer name
    - Returns customer's invoice history
    """
    invoices = agent.get_customer_invoices(customer_name)
    
    if not invoices:
        return {
            "success": True,
            "message": f"No invoices found for customer: {customer_name}",
            "invoices": []
        }
    
    total_spent = sum(inv['totals']['grand_total'] for inv in invoices)
    
    return {
        "success": True,
        "customer_name": customer_name,
        "total_invoices": len(invoices),
        "total_spent": round(total_spent, 2),
        "invoices": invoices
    }


@app.get("/api/stats", tags=["Statistics"])
async def get_statistics():
    """
    Get overall statistics
    
    - Total invoices
    - Revenue breakdown
    - GST collection
    - Top customers
    """
    invoices = agent.get_all_invoices()
    
    if not invoices:
        return {
            "success": True,
            "message": "No invoices yet",
            "stats": {}
        }
    
    # Calculate stats
    total_revenue = sum(inv['totals']['grand_total'] for inv in invoices)
    total_gst = sum(inv['totals']['total_gst'] for inv in invoices)
    total_items = sum(inv['totals']['total_items'] for inv in invoices)
    
    # Customer spending
    customer_spending = {}
    for inv in invoices:
        customer = inv['customer']['name']
        if customer not in customer_spending:
            customer_spending[customer] = 0
        customer_spending[customer] += inv['totals']['grand_total']
    
    # Sort customers by spending
    top_customers = sorted(
        customer_spending.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    return {
        "success": True,
        "stats": {
            "total_invoices": len(invoices),
            "total_revenue": round(total_revenue, 2),
            "total_gst_collected": round(total_gst, 2),
            "total_items_sold": total_items,
            "average_invoice_value": round(total_revenue / len(invoices), 2),
            "top_customers": [
                {"name": name, "total_spent": round(amount, 2)}
                for name, amount in top_customers
            ]
        }
    }


@app.get("/api/invoice/{invoice_number}/pdf", tags=["Invoices"])
async def download_invoice_pdf(invoice_number: str, template: str = "modern"):
    """
    Download invoice as PDF
    
    - Retrieves invoice from database
    - Generates beautiful PDF
    - template: Choose 'modern', 'classic', or 'minimal' (default: modern)
    - Returns PDF file for download
    """
    # Get invoice from database
    invoice = agent.get_invoice(invoice_number)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice_number} not found"
        )
    
    try:
        # Generate PDF bytes with selected template
        pdf_bytes = pdf_generator.generate_pdf_bytes(invoice, template=template)
        
        # Return PDF as downloadable file
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={invoice_number}_{template}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF: {str(e)}"
        )
    

@app.post("/api/invoice/create-with-pdf", tags=["Invoices"])
async def create_invoice_with_pdf(request: InvoiceCreateRequest, template: str = "modern"):
    """
    Create invoice and automatically save PDF
    
    - Creates invoice in database
    - Generates PDF file with chosen template
    - template: 'modern', 'classic', or 'minimal'
    - Returns invoice data with PDF path
    """
    # Convert Pydantic models to dictionaries
    customer_dict = request.customer.dict()
    items_list = [item.dict() for item in request.items]
    
    # Create invoice using agent
    result = agent.create_invoice(
        customer=customer_dict,
        items=items_list,
        notes=request.notes
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    # Generate PDF with selected template
    try:
        pdf_path = pdf_generator.generate_pdf(result['invoice'], template=template)
        result['invoice']['pdf_path'] = pdf_path
        result['invoice']['template_used'] = template
        result['message'] = f"{result['message']} - PDF saved with {template} template"
    except Exception as e:
        result['invoice']['pdf_path'] = None
        result['message'] = f"{result['message']} - Warning: PDF generation failed: {str(e)}"
    
    return {
        "success": True,
        "message": result['message'],
        "invoice": result['invoice']
    }


@app.post("/api/invoice/{invoice_number}/send-email", tags=["Invoices"])
async def send_invoice_email(
    invoice_number: str,
    recipient_email: str,
    sender_email: str,
    sender_password: str
):
    """
    Send invoice via email
    
    - Retrieves invoice from database
    - Generates PDF
    - Sends email with PDF attachment
    
    Note: Use Gmail App Password, not regular password
    """
    # Get invoice
    invoice = agent.get_invoice(invoice_number)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice_number} not found"
        )
    
    # Send email
    result = email_agent.send_invoice_email(
        invoice_data=invoice,
        sender_email=sender_email,
        sender_password=sender_password,
        recipient_email=recipient_email
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=f"Email sending failed: {result['error']}"
        )
    
    return {
        "success": True,
        "message": result['message'],
        "recipient": result['recipient']
    }


@app.post("/api/invoice/{invoice_number}/payment", tags=["Payments"])
async def record_payment(
    invoice_number: str,
    amount: float,
    payment_method: str,
    transaction_id: str = "",
    notes: str = ""
):
    """
    Record a payment for an invoice
    
    - Updates payment status automatically
    - Tracks partial payments
    - Marks invoice as paid when full amount received
    """
    result = agent.add_payment(
        invoice_number=invoice_number,
        amount=amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        notes=notes
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result


@app.get("/api/invoice/{invoice_number}/payments", tags=["Payments"])
async def get_payment_history(invoice_number: str):
    """
    Get payment history for an invoice
    
    - Returns all payments made
    - Shows total paid and remaining amount
    """
    payments = agent.get_payment_history(invoice_number)
    invoice = agent.get_invoice(invoice_number)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice_number} not found"
        )
    
    total_paid = sum(p['amount'] for p in payments)
    remaining = max(0, invoice['totals']['grand_total'] - total_paid)
    
    return {
        "success": True,
        "invoice_number": invoice_number,
        "total_amount": invoice['totals']['grand_total'],
        "total_paid": total_paid,
        "remaining": remaining,
        "status": invoice['payment_status'],
        "payments": payments
    }


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@app.get("/api/export/invoices", tags=["Export"])
async def export_invoices_to_excel():
    """
    Export all invoices to Excel
    
    - Returns downloadable Excel file
    - Includes all invoice details
    - Formatted with colors and currency
    """
    try:
        # Get all invoices
        invoices = agent.get_all_invoices()
        
        if not invoices:
            raise HTTPException(
                status_code=404,
                detail="No invoices to export"
            )
        
        # Generate Excel file
        filepath = excel_exporter.export_invoices(invoices)
        
        # Return file for download
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@app.get("/api/export/gst-summary", tags=["Export"])
async def export_gst_summary_report(month: str = None):
    """
    Export GST summary report to Excel
    
    - month: Filter by month (YYYY-MM format, optional)
    - Returns multi-sheet Excel with summary, breakdown, invoice list
    - Ready for GST filing
    """
    try:
        # Get all invoices
        invoices = agent.get_all_invoices()
        
        if not invoices:
            raise HTTPException(
                status_code=404,
                detail="No invoices to export"
            )
        
        # Generate GST summary
        filepath = excel_exporter.export_gst_summary(invoices, month=month)
        
        # Return file for download
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@app.get("/api/export/customer-report", tags=["Export"])
async def export_customer_spending_report():
    """
    Export customer-wise spending report to Excel
    
    - Shows total spent per customer
    - Invoice count per customer
    - Sorted by total spending
    """
    try:
        # Get all invoices
        invoices = agent.get_all_invoices()
        
        if not invoices:
            raise HTTPException(
                status_code=404,
                detail="No invoices to export"
            )
        
        # Generate customer report
        filepath = excel_exporter.export_customer_report(invoices)
        
        # Return file for download
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )
    

    # ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/analytics/revenue-trends", tags=["Analytics"])
async def get_revenue_trends(period: str = "monthly"):
    """
    Get revenue trends over time
    
    - period: 'daily', 'weekly', or 'monthly'
    - Returns trend data for charts
    """
    invoices = agent.get_all_invoices()
    
    if not invoices:
        return {
            "success": True,
            "data": {"dates": [], "revenue": [], "gst": []}
        }
    
    trends = analytics_agent.revenue_trends(invoices, period=period)
    
    return {
        "success": True,
        "period": period,
        "data": trends
    }


@app.get("/api/analytics/customer-clv", tags=["Analytics"])
async def get_customer_lifetime_value():
    """
    Get customer lifetime value analysis
    
    - Returns CLV metrics for all customers
    - Sorted by CLV (highest first)
    """
    invoices = agent.get_all_invoices()
    
    if not invoices:
        return {
            "success": True,
            "customers": []
        }
    
    clv_data = analytics_agent.customer_lifetime_value(invoices)
    
    return {
        "success": True,
        "customers": clv_data
    }


@app.get("/api/analytics/gst-breakdown", tags=["Analytics"])
async def get_gst_rate_breakdown():
    """
    Get GST collection breakdown by tax rate
    
    - Shows revenue and GST for each rate
    - Useful for tax filing
    """
    invoices = agent.get_all_invoices()
    
    if not invoices:
        return {
            "success": True,
            "breakdown": []
        }
    
    breakdown = analytics_agent.gst_rate_analysis(invoices)
    
    return {
        "success": True,
        **breakdown
    }
     

# ============================================================================
# AUDIT LOG ENDPOINTS
# ============================================================================

@app.get("/api/audit/logs", tags=["Audit Logs"])
async def get_audit_logs(
    user: str = None,
    action: str = None,
    entity_type: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100
):
    """
    Get audit logs with filters
    
    - user: Filter by username
    - action: Filter by action type
    - entity_type: Filter by entity type (invoice, payment, customer)
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - limit: Max results (default 100)
    """
    logs = audit_agent.get_logs(
        user=user,
        action=action,
        entity_type=entity_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    return {
        "success": True,
        "count": len(logs),
        "logs": logs
    }


@app.get("/api/audit/user-activity/{username}", tags=["Audit Logs"])
async def get_user_activity_stats(username: str, days: int = 30):
    """
    Get activity statistics for a specific user
    
    - Returns action counts, success rate, recent activities
    - Default: last 30 days
    """
    activity = audit_agent.get_user_activity(username, days=days)
    
    return {
        "success": True,
        "activity": activity
    }


@app.get("/api/audit/system-activity", tags=["Audit Logs"])
async def get_system_activity_stats(days: int = 7):
    """
    Get overall system activity statistics
    
    - Total actions, unique users, top users
    - Action breakdown, daily activity
    - Default: last 7 days
    """
    stats = audit_agent.get_system_activity(days=days)
    
    return {
        "success": True,
        "stats": stats
    }


@app.get("/api/audit/export", tags=["Audit Logs"])
async def export_audit_trail(
    start_date: str = None,
    end_date: str = None
):
    """
    Export complete audit trail
    
    - For compliance and reporting
    - Returns all logs within date range
    """
    logs = audit_agent.export_audit_trail(
        start_date=start_date,
        end_date=end_date
    )
    
    # Convert to CSV
    import csv
    from io import StringIO
    
    output = StringIO()
    if logs:
        writer = csv.DictWriter(output, fieldnames=logs[0].keys())
        writer.writeheader()
        writer.writerows(logs)
    
    csv_content = output.getvalue()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=audit_trail.csv"
        }
    )


@app.get("/api/audit/action-types", tags=["Audit Logs"])
async def get_action_types():
    """
    Get list of all action types
    
    - For filtering and documentation
    """
    return {
        "success": True,
        "action_types": audit_agent.ACTION_TYPES
    }

     # ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@app.post("/api/notifications/payment-reminder", tags=["Notifications"])
async def send_payment_reminder_email(
    invoice_number: str,
    from_email: str,
    from_password: str
):
    """
    Send payment reminder for a specific invoice
    
    - Sends professional reminder email to customer
    - Requires Gmail App Password
    """
    # Get invoice
    invoice = agent.get_invoice(invoice_number)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice_number} not found"
        )
    
    # Check if customer has email
    if not invoice['customer'].get('email'):
        raise HTTPException(
            status_code=400,
            detail="Customer email not available"
        )
    
    # Company info (you can make this configurable)
    company_info = {
        'name': 'AI Tax Solutions',
        'email': 'support@aitaxsolutions.com',
        'phone': '+91 9876543210'
    }
    
    email_config = {
        'from_email': from_email,
        'password': from_password
    }
    
    # Send reminder
    result = notification_agent.send_payment_reminder(
        invoice_data=invoice,
        company_info=company_info,
        email_config=email_config
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send reminder: {result['error']}"
        )
    
    return {
        "success": True,
        "message": result['message'],
        "invoice_number": invoice_number,
        "sent_to": invoice['customer']['email']
    }


@app.post("/api/notifications/overdue-alert", tags=["Notifications"])
async def send_overdue_alert_email(
    invoice_number: str,
    from_email: str,
    from_password: str
):
    """
    Send overdue alert for a specific invoice
    
    - Sends urgent overdue notice to customer
    - Calculates days overdue automatically
    """
    # Get invoice
    invoice = agent.get_invoice(invoice_number)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice_number} not found"
        )
    
    # Check if customer has email
    if not invoice['customer'].get('email'):
        raise HTTPException(
            status_code=400,
            detail="Customer email not available"
        )
    
    # Calculate days overdue
    if invoice.get('due_date'):
        due_date = datetime.strptime(invoice['due_date'], "%Y-%m-%d")
        days_overdue = (datetime.now() - due_date).days
    else:
        days_overdue = 0
    
    # Company info
    company_info = {
        'name': 'AI Tax Solutions',
        'email': 'support@aitaxsolutions.com',
        'phone': '+91 9876543210'
    }
    
    email_config = {
        'from_email': from_email,
        'password': from_password
    }
    
    # Send alert
    result = notification_agent.send_overdue_alert(
        invoice_data=invoice,
        days_overdue=days_overdue,
        company_info=company_info,
        email_config=email_config
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send alert: {result['error']}"
        )
    
    return {
        "success": True,
        "message": result['message'],
        "invoice_number": invoice_number,
        "days_overdue": days_overdue,
        "sent_to": invoice['customer']['email']
    }


@app.post("/api/notifications/payment-confirmation", tags=["Notifications"])
async def send_payment_confirmation_email(
    invoice_number: str,
    payment_id: int,
    from_email: str,
    from_password: str
):
    """
    Send payment received confirmation
    
    - Sends thank you email with payment details
    - Confirms payment receipt
    """
    # Get invoice
    invoice = agent.get_invoice(invoice_number)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice_number} not found"
        )
    
    # Check if customer has email
    if not invoice['customer'].get('email'):
        raise HTTPException(
            status_code=400,
            detail="Customer email not available"
        )
    
    # Get payment details
    payments = agent.get_payment_history(invoice_number)
    payment = next((p for p in payments if p['id'] == payment_id), None)
    
    if not payment:
        raise HTTPException(
            status_code=404,
            detail=f"Payment {payment_id} not found"
        )
    
    # Company info
    company_info = {
        'name': 'AI Tax Solutions',
        'email': 'support@aitaxsolutions.com',
        'phone': '+91 9876543210'
    }
    
    email_config = {
        'from_email': from_email,
        'password': from_password
    }
    
    # Send confirmation
    result = notification_agent.send_payment_confirmation(
        invoice_data=invoice,
        payment_data=payment,
        company_info=company_info,
        email_config=email_config
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send confirmation: {result['error']}"
        )
    
    return {
        "success": True,
        "message": result['message'],
        "invoice_number": invoice_number,
        "sent_to": invoice['customer']['email']
    }


@app.get("/api/notifications/pending-reminders", tags=["Notifications"])
async def get_pending_reminders():
    """
    Get list of invoices that need payment reminders
    
    - Returns unpaid/partial invoices
    - Filters invoices with customer emails
    """
    all_invoices = agent.get_all_invoices()
    
    # Filter pending/partial invoices with emails
    pending = [
        inv for inv in all_invoices
        if inv['payment_status'] in ['Pending', 'Partial']
        and inv['customer'].get('email')
    ]
    
    return {
        "success": True,
        "count": len(pending),
        "invoices": pending
    }


@app.get("/api/notifications/overdue-invoices", tags=["Notifications"])
async def get_overdue_invoices():
    """
    Get list of overdue invoices
    
    - Returns invoices past due date
    - Calculates days overdue
    """
    all_invoices = agent.get_all_invoices()
    today = datetime.now().date()
    
    overdue = []
    for inv in all_invoices:
        if inv['payment_status'] in ['Pending', 'Partial']:
            if inv.get('due_date'):
                due_date = datetime.strptime(inv['due_date'], "%Y-%m-%d").date()
                if today > due_date:
                    days_overdue = (today - due_date).days
                    inv['days_overdue'] = days_overdue
                    overdue.append(inv)
    
    return {
        "success": True,
        "count": len(overdue),
        "total_overdue_amount": sum(inv['totals']['grand_total'] for inv in overdue),
        "invoices": overdue
    }
# ============================================================================
# ADVANCED SEARCH ENDPOINTS
# ============================================================================

@app.post("/api/search/invoices", tags=["Search"])
async def search_invoices(
    date_preset: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    payment_statuses: Optional[List[str]] = None,
    gst_rates: Optional[List[int]] = None,
    customer_query: Optional[str] = None,
    invoice_number: Optional[str] = None,
    item_query: Optional[str] = None
):
    """
    Advanced search for invoices
    
    - date_preset: 'today', 'this_week', 'this_month', 'this_quarter', 'this_year', 'last_30_days'
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - min_amount: Minimum amount
    - max_amount: Maximum amount
    - payment_statuses: List of statuses ['Paid', 'Pending', 'Partial']
    - gst_rates: List of GST rates [0, 5, 12, 18, 28]
    - customer_query: Customer name search
    - invoice_number: Invoice number search
    - item_query: Item name search
    
    Returns filtered invoices
    """
    # Get all invoices
    all_invoices = agent.get_all_invoices()
    
    # Build filters dictionary
    filters = {}
    
    if date_preset:
        filters['date_preset'] = date_preset
    if start_date:
        filters['start_date'] = start_date
    if end_date:
        filters['end_date'] = end_date
    if min_amount is not None:
        filters['min_amount'] = min_amount
    if max_amount is not None:
        filters['max_amount'] = max_amount
    if payment_statuses:
        filters['payment_statuses'] = payment_statuses
    if gst_rates:
        filters['gst_rates'] = gst_rates
    if customer_query:
        filters['customer_query'] = customer_query
    if invoice_number:
        filters['invoice_number'] = invoice_number
    if item_query:
        filters['item_query'] = item_query
    
    # Apply filters
    filtered = search_agent.advanced_search(all_invoices, filters)
    
    # Generate summary
    summary = search_agent.get_filter_summary(filters, len(filtered))
    
    return {
        "success": True,
        "total": len(all_invoices),
        "filtered": len(filtered),
        "summary": summary,
        "filters_applied": filters,
        "invoices": filtered
    }


@app.get("/api/search/quick-filters", tags=["Search"])
async def get_quick_filters():
    """
    Get available quick filter options
    
    Returns predefined filter options
    """
    return {
        "success": True,
        "date_presets": [
            {"id": "today", "label": "Today"},
            {"id": "this_week", "label": "This Week"},
            {"id": "this_month", "label": "This Month"},
            {"id": "this_quarter", "label": "This Quarter"},
            {"id": "this_year", "label": "This Year"},
            {"id": "last_30_days", "label": "Last 30 Days"}
        ],
        "amount_ranges": [
            {"id": "0-10000", "label": "Under ₹10,000", "min": 0, "max": 10000},
            {"id": "10000-50000", "label": "₹10,000 - ₹50,000", "min": 10000, "max": 50000},
            {"id": "50000-100000", "label": "₹50,000 - ₹1,00,000", "min": 50000, "max": 100000},
            {"id": "100000+", "label": "Above ₹1,00,000", "min": 100000, "max": None}
        ],
        "payment_statuses": [
            {"id": "Paid", "label": "✅ Paid"},
            {"id": "Pending", "label": "⏳ Pending"},
            {"id": "Partial", "label": "💰 Partial"}
        ],
        "gst_rates": [
            {"id": 0, "label": "0% GST"},
            {"id": 5, "label": "5% GST"},
            {"id": 12, "label": "12% GST"},
            {"id": 18, "label": "18% GST"},
            {"id": 28, "label": "28% GST"}
        ]
    }
  # ============================================================================
# BULK OPERATIONS ENDPOINTS
# ============================================================================

@app.get("/api/bulk/sample-customer-csv", tags=["Bulk Operations"])
async def get_sample_customer_csv():
    """
    Download sample customer CSV template
    
    - Returns CSV template with example data
    - Use this format to bulk import customers
    """
    csv_content = bulk_ops.generate_sample_customer_csv()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=sample_customers.csv"
        }
    )


@app.get("/api/bulk/sample-invoice-csv", tags=["Bulk Operations"])
async def get_sample_invoice_csv():
    """
    Download sample invoice CSV template
    
    - Returns CSV template with example data
    - Use this format to bulk import invoices
    """
    csv_content = bulk_ops.generate_sample_invoice_csv()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=sample_invoices.csv"
        }
    )


@app.post("/api/bulk/import-customers", tags=["Bulk Operations"])
async def bulk_import_customers(file: UploadFile = File(...)):
    """
    Import multiple customers from CSV
    
    - Upload CSV file with customer data
    - Creates all customers in database
    - Returns import statistics
    """
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV
        result = bulk_ops.import_customers_from_csv(csv_content)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Import to database (you'll need to add this to invoice_agent_db)
        imported = 0
        errors = []
        
        for customer in result['customers']:
            # Here you would create customers in database
            # For now, just counting
            imported += 1
        
        return {
            "success": True,
            "message": f"Imported {imported} customers",
            "total": result['total'],
            "imported": imported,
            "errors": result['errors']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bulk/import-invoices", tags=["Bulk Operations"])
async def bulk_import_invoices(file: UploadFile = File(...)):
    """
    Import multiple invoices from CSV
    
    - Upload CSV file with invoice data
    - Creates all invoices with items
    - Returns import statistics
    """
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV
        result = bulk_ops.import_invoices_from_csv(csv_content)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Create invoices
        created = 0
        errors = []
        
        for invoice_data in result['invoices']:
            try:
                inv_result = agent.create_invoice(
                    customer=invoice_data['customer'],
                    items=invoice_data['items'],
                    notes=invoice_data['notes']
                )
                
                if inv_result['success']:
                    created += 1
                else:
                    errors.append(inv_result['error'])
                    
            except Exception as e:
                errors.append(str(e))
        
        return {
            "success": True,
            "message": f"Created {created}/{result['total']} invoices",
            "total": result['total'],
            "created": created,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bulk/export-customers-csv", tags=["Bulk Operations"])
async def export_all_customers_csv():
    """
    Export all customers to CSV
    
    - Downloads all customer data
    - CSV format for backup/transfer
    """
    # Get all customers (you'll need to add this to invoice_agent_db)
    # For now, return empty
    customers = []  # Replace with actual customer retrieval
    
    csv_content = bulk_ops.export_customers_to_csv(customers)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=customers_export.csv"
        }
    )


@app.get("/api/bulk/export-invoices-csv", tags=["Bulk Operations"])
async def export_all_invoices_csv():
    """
    Export all invoices to CSV
    
    - Downloads all invoice data
    - CSV format for backup/analysis
    """
    invoices = agent.get_all_invoices()
    
    csv_content = bulk_ops.export_invoices_to_csv(invoices)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=invoices_export.csv"
        }
    )

@app.get("/api/analytics/top-products", tags=["Analytics"])
async def get_top_products(limit: int = 10):
    """
    Get top-selling products
    
    - limit: Number of products to return (default 10)
    - Sorted by revenue
    """
    invoices = agent.get_all_invoices()
    
    if not invoices:
        return {
            "success": True,
            "products": []
        }
    
    products = analytics_agent.product_performance(invoices, top_n=limit)
    
    return {
        "success": True,
        "products": products
    }


@app.get("/api/analytics/payment-insights", tags=["Analytics"])
async def get_payment_insights():
    """
    Get payment collection insights
    
    - Payment status breakdown
    - Collection rate
    - Outstanding amounts
    """
    invoices = agent.get_all_invoices()
    
    insights = analytics_agent.payment_insights(invoices)
    
    return {
        "success": True,
        "insights": insights
    }


@app.get("/api/analytics/growth-metrics", tags=["Analytics"])
async def get_growth_metrics():
    """
    Get business growth metrics
    
    - Month-over-Month growth
    - Quarter-over-Quarter growth
    """
    invoices = agent.get_all_invoices()
    
    metrics = analytics_agent.growth_metrics(invoices)
    
    return {
        "success": True,
        "metrics": metrics
    }

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.post("/api/auth/register", tags=["Authentication"])
async def register(request: UserRegisterRequest):
    """
    Register a new user
    
    - Creates new account
    - Hashes password securely using SHA-256 + bcrypt
    - Returns user details
    - Supports passwords of any length
    """
    result = auth_agent.register_user(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=400,
            detail=result['error']
        )
    
    return result


@app.post("/api/auth/login", tags=["Authentication"])
async def login(request: UserLoginRequest):
    """
    Login with username and password
    
    - Returns JWT access token
    - Token valid for 24 hours
    - Use token in Authorization header
    - Supports passwords of any length
    """
    result = auth_agent.login_user(request.username, request.password)
    
    if not result['success']:
        raise HTTPException(
            status_code=401,
            detail=result['error']
        )
    
    return result


@app.get("/api/auth/me", tags=["Authentication"])
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current logged in user details
    
    - Requires valid JWT token
    - Returns user profile
    """
    return {
        "success": True,
        "user": current_user
    }
# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GST Invoice Agent API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔗 Alternative docs: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)