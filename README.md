# 🧾 GST Invoice Agent

AI-powered GST invoice automation system for Indian businesses.

## 🚀 Live Project
**Built in public - 30 day challenge!**

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI
- **Database:** SQLAlchemy, SQLite
- **Frontend:** Streamlit
- **PDF:** xhtml2pdf
- **Excel:** openpyxl, xlsxwriter
- **Email:** SMTP (Gmail)

## ✅ Progress (10/30 Days)

### Day 1: GST Calculator Agent
- Core GST calculation engine
- CGST/SGST breakdown
- Input validation

### Day 2: Validation Agent
- Customer data validation
- Phone/Email/GST validation
- Error handling

### Day 3: Invoice Orchestrator
- Combined all agents
- Auto invoice numbering
- Complete invoice generation

### Day 4: REST API
- FastAPI backend
- 7 endpoints
- Auto-generated docs at /docs

### Day 5: Database
- SQLAlchemy integration
- Permanent data storage
- Customer management

### Day 6: PDF Generation
- Professional PDF invoices
- Beautiful HTML template
- Download via API

### Day 7: Web Frontend
- Streamlit UI
- Dashboard with charts
- Invoice creation form

### Day 8: Email Automation
- Send invoices via email
- PDF attachment
- Gmail SMTP integration

### Day 9: Payment Tracking
- Record payments
- Payment history
- Auto-update status

### Day 10: Excel Export
- Export invoices to Excel
- GST summary report
- Customer report

### Day 11: User Authentication
- JWT token authentication ✅
- Secure password hashing (bcrypt) ✅
- Login/Register system ✅
- Protected API endpoints ✅
- Session management ✅
- Logout functionality ✅

## 🚀 Features
- ✅ Automated GST calculation (CGST/SGST)
- ✅ Professional PDF invoices
- ✅ Customer management
- ✅ Payment tracking
- ✅ Excel reports
- ✅ Email automation
- ✅ REST API with docs
- ✅ Database persistence
- ✅ Beautiful web UI

## 📦 Installation

### 1. Clone the repo
```bash
git clone https://github.com/BUNNY-RANGU/gst-invoice-agent.git
cd gst-invoice-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run API server
```bash
python main.py
```

### 5. Run Streamlit UI
```bash
streamlit run streamlit_app.py
```

## 🔗 API Endpoints
- `POST /api/invoice/create` - Create invoice
- `GET /api/invoice/{id}` - Get invoice
- `GET /api/invoices` - List all invoices
- `POST /api/invoice/{id}/payment` - Record payment
- `GET /api/invoice/{id}/pdf` - Download PDF
- `POST /api/invoice/{id}/send-email` - Send email
- `GET /api/export/invoices` - Export to Excel
- `GET /api/export/gst-summary` - GST report
- `GET /api/stats` - Statistics

## 👨‍💻 Developer
**Bunny Rangu**
B.Tech CSE, 2nd Year
Python Full Stack Developer
Building AI Agents

## 📅 Timeline
- **Start:** February 12, 2026
- **Target:** 30 days
- **Current:** Day 10/30

---
⭐ Star this repo if you find it useful!
Built with ❤️ in Hyderabad, India