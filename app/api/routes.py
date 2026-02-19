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
from datetime import datetime
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
    phone: str = Field(..., pattern=r'^[6-9]\d{9}$', description="10-digit phone number")
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
async def download_invoice_pdf(invoice_number: str):
    """
    Download invoice as PDF
    
    - Retrieves invoice from database
    - Generates beautiful PDF
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
        # Generate PDF bytes
        pdf_bytes = pdf_generator.generate_pdf_bytes(invoice)
        
        # Return PDF as downloadable file
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={invoice_number}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF: {str(e)}"
        )


@app.post("/api/invoice/create-with-pdf", tags=["Invoices"])
async def create_invoice_with_pdf(request: InvoiceCreateRequest):
    """
    Create invoice and automatically save PDF
    
    - Creates invoice in database
    - Generates PDF file
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
    
    # Generate PDF
    try:
        pdf_path = pdf_generator.generate_pdf(result['invoice'])
        result['invoice']['pdf_path'] = pdf_path
        result['message'] = f"{result['message']} - PDF saved to {pdf_path}"
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