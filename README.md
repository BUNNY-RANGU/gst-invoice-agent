# 🧾 GST Invoice Agent - AI-Powered Invoice Automation

**Complete invoice management system with GST calculation, automated workflows, and enterprise features.**

Built by **Bunny Rangu** | 30-Day B.Tech Project | Production-Ready

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🎯 What is this?

A complete **GST invoice automation system** with professional PDF generation, payment tracking, analytics, and recurring invoices. Built for Indian businesses.

**Perfect for:** Freelancers, Small Businesses, Startups, Accountants, Consultants

---

## ✨ Key Features

### 📄 Invoice Management
- Professional PDF generation (3 templates)
- GST calculation (0%, 5%, 12%, 18%, 28%)
- Customer management
- Payment tracking
- Email delivery

### 📊 Advanced Features
- Real-time analytics dashboard
- Recurring invoice automation
- Advanced search & filters
- Bulk import/export
- Automated payment reminders
- Complete audit trail
- Backup & restore

### 🔒 Security
- JWT authentication
- API rate limiting
- Encrypted passwords
- Audit logging
- Role-based access

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/BUNNY-RANGU/gst-invoice-agent
cd gst-invoice-agent
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Run Application
```bash
# Terminal 1 - API
python main.py

# Terminal 2 - UI
streamlit run streamlit_app.py
```

### 3. Access
- **Web UI:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

### 4. First Login
- Register a new account
- Start creating invoices!

---

## 📸 Screenshots

### Dashboard
<img width="1919" height="885" alt="image" src="https://github.com/user-attachments/assets/2aa5f4bb-b167-4f5d-9958-94c3cc493364" />

### Invoice PDF
<img width="1045" height="838" alt="image" src="https://github.com/user-attachments/assets/0a6fded6-e5fa-4caa-a98b-f18ac5da752d" />

### Analytics
<img width="1587" height="871" alt="image" src="https://github.com/user-attachments/assets/80320b7f-eeb1-402e-bf8f-7b170095d96e" />

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite / PostgreSQL |
| Authentication | JWT + bcrypt |
| PDF Generation | xhtml2pdf |
| Email | SMTP |
| Testing | pytest |

---

## 📚 Documentation

- **[Complete Documentation](DOCUMENTATION.md)**
- **[API Documentation](http://localhost:8000/docs)**
- **[Architecture Guide](ARCHITECTURE.md)**

---

## 🏗️ Project Structure
```
gst-invoice-agent/
├── app/
│   ├── agents/          # Business logic (12 agents)
│   ├── api/             # REST API (50+ endpoints)
│   ├── models/          # Database models
│   └── templates/       # Invoice templates
├── tests/               # Test suite (18 tests)
├── streamlit_app.py     # Web interface
└── main.py             # API server
```

---

## 🎯 Features Breakdown

### Days 1-10: Foundation
✅ GST Calculator
✅ Validation Engine
✅ Invoice Orchestrator
✅ REST API
✅ Database Layer
✅ PDF Generation
✅ Web Frontend
✅ Email Automation
✅ Payment Tracking
✅ Excel Export

### Days 11-20: Advanced Features
✅ User Authentication
✅ Advanced Analytics
✅ Invoice Templates
✅ Bulk Operations
✅ Advanced Search
✅ Notifications
✅ Audit Logs
✅ Recurring Invoices
✅ Backup System
✅ API Security

### Days 21-30: Polish & Deploy
✅ Testing Suite
✅ Documentation
✅ Code Quality
✅ Performance Optimization
✅ Deployment Ready

---

## 📈 Stats

- **21 Days** of development
- **12 Agents** (business logic modules)
- **50+ API Endpoints**
- **3 Invoice Templates**
- **18 Test Cases**
- **10 Pages** in web UI
- **80%+ Code Coverage**

---

## 🚀 Deployment

### Local Development
```bash
python main.py
streamlit run streamlit_app.py
```

### Production (Railway/Render)
See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment guide.

---

## 🧪 Testing
```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# View coverage
open htmlcov/index.html
```

---

## 📊 Performance

- **API Response Time:** < 100ms
- **PDF Generation:** < 2 seconds
- **Concurrent Users:** 50+
- **Database Queries:** Optimized with indexes

---

## 🔐 Security Features

- JWT token authentication
- bcrypt password hashing
- API rate limiting (100 req/min)
- CORS configuration
- Security headers
- IP blocking
- Audit trail logging

---

## 🎨 Invoice Templates

1. **Modern** - Colorful gradient design
2. **Classic** - Professional black & white
3. **Minimal** - Clean and elegant

---

## 📧 Email Features

- Invoice delivery
- Payment reminders
- Overdue alerts
- Payment confirmations
- Weekly summaries

---

## 💾 Backup & Restore

- One-click database backup
- JSON export format
- CSV data export
- Point-in-time restore
- Automated backup scheduling

---

## 🌟 Use Cases

### For Freelancers
- Professional invoices
- Payment tracking
- Client management

### For Small Businesses
- GST compliance
- Bulk invoice generation
- Analytics dashboard

### For Accountants
- Multiple client support
- Audit trail
- Report generation

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 👨‍💻 Author

**Bunny Rangu**
- GitHub: [@BUNNY-RANGU](https://github.com/BUNNY-RANGU)
- LinkedIn: [Bunny Rangu](https://linkedin.com/in/bunny-rangu)
- Email: bunny@example.com

---

## 🙏 Acknowledgments

- FastAPI team for amazing framework
- Streamlit for beautiful UI components
- Python community for excellent libraries

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/BUNNY-RANGU/gst-invoice-agent/issues)
- **Discussions:** [GitHub Discussions](https://github.com/BUNNY-RANGU/gst-invoice-agent/discussions)
- **Email:** support@example.com

---

## 🎉 Project Status

**Status:** ✅ Production Ready

**Version:** 1.0.0

**Last Updated:** February 2026

---

**⭐ Star this repo if you found it helpful!**

**🔥 Built with passion in 30 days!**
