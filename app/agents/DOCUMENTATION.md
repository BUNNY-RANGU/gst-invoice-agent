cat > DOCUMENTATION.md << 'EOF'
# GST Invoice Agent - Complete Documentation

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/BUNNY-RANGU/gst-invoice-agent
cd gst-invoice-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Application
```bash
# Terminal 1 - API Server
python main.py

# Terminal 2 - Streamlit UI
streamlit run streamlit_app.py
```

### Access
- **API Documentation:** http://localhost:8000/docs
- **Web Interface:** http://localhost:8501

## 📚 Features

### Core Features
- ✅ GST calculation (0%, 5%, 12%, 18%, 28%)
- ✅ Professional PDF invoice generation
- ✅ 3 invoice templates (Modern, Classic, Minimal)
- ✅ Customer management
- ✅ Payment tracking
- ✅ Email automation

### Advanced Features
- ✅ User authentication (JWT)
- ✅ Advanced analytics dashboard
- ✅ Bulk import/export (CSV)
- ✅ Advanced search & filters
- ✅ Automated notifications
- ✅ Audit logs
- ✅ Recurring invoices
- ✅ Backup & restore
- ✅ API rate limiting

## 🏗️ Architecture

### Technology Stack
- **Backend:** FastAPI, SQLAlchemy
- **Database:** SQLite (production: PostgreSQL)
- **Frontend:** Streamlit
- **PDF:** xhtml2pdf
- **Email:** SMTP
- **Auth:** JWT, bcrypt

### Project Structure
```
gst-invoice-agent/
├── app/
│   ├── agents/          # Business logic
│   ├── api/             # REST API
│   ├── models/          # Database models
│   └── templates/       # PDF templates
├── tests/               # Test suite
├── backups/             # Database backups
├── invoices/            # Generated PDFs
├── streamlit_app.py     # Web UI
├── main.py              # API server
└── requirements.txt     # Dependencies
```

## 🔐 Security

### Authentication
- JWT tokens (24-hour expiry)
- bcrypt password hashing
- Session management

### API Security
- Rate limiting (100 req/min)
- CORS configuration
- Security headers
- IP blocking

## 📊 API Endpoints

### Core Endpoints
- `POST /api/invoice/create` - Create invoice
- `GET /api/invoices` - List all invoices
- `GET /api/invoice/{number}` - Get specific invoice
- `POST /api/invoice/{number}/payment` - Record payment
- `GET /api/invoice/{number}/pdf` - Download PDF

### Advanced Endpoints
- `POST /api/search/invoices` - Advanced search
- `POST /api/bulk/import-invoices` - Bulk import
- `POST /api/recurring/create` - Create recurring invoice
- `POST /api/backup/create` - Create backup
- `GET /api/analytics/*` - Analytics endpoints

Full API documentation: http://localhost:8000/docs

## 🎨 Invoice Templates

### Modern Template
- Colorful gradient design
- Purple/blue theme
- Best for: Tech companies, startups

### Classic Template
- Black & white professional
- Traditional layout
- Best for: Law firms, accounting

### Minimal Template
- Clean, elegant design
- Simple typography
- Best for: Freelancers, consultants

## 📧 Email Configuration

### Gmail Setup
1. Enable 2-Factor Authentication
2. Go to Google Account → Security
3. Create App Password
4. Use app password in the system

### Email Features
- Invoice delivery
- Payment reminders
- Overdue alerts
- Payment confirmations

## 💾 Backup & Restore

### Create Backup
```python
# Via UI: Backup page → Create Backup
# Via API: POST /api/backup/create
```

### Restore
```python
# Via UI: Backup page → Select backup → Restore
# Via API: POST /api/backup/restore/{filename}
```

## 🧪 Testing

### Run Tests
```bash
pytest
pytest --cov=app --cov-report=html
```

### Test Coverage
- Unit tests: 90%+
- API tests: 85%+
- Overall: 80%+

## 🚀 Deployment

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your-secret-key-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### Production Checklist
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong SECRET_KEY
- [ ] Configure CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Set up automated backups
- [ ] Configure email settings
- [ ] Set rate limits appropriately

## 📈 Performance

### Optimization Tips
- Index frequently queried fields
- Use connection pooling
- Cache static data
- Compress responses
- Use CDN for static files

## 🐛 Troubleshooting

### Common Issues

**API not starting:**
- Check if port 8000 is available
- Verify database connection
- Check virtual environment

**Email not sending:**
- Verify Gmail app password
- Check firewall settings
- Ensure SMTP access enabled

**PDF generation failing:**
- Check template files exist
- Verify write permissions
- Check disk space

## 📞 Support

- **Issues:** GitHub Issues
- **Email:** your@email.com
- **Docs:** This file

## 📄 License

MIT License - Free to use and modify

## 🙏 Credits

Built by **Bunny Rangu** as a 30-day B.Tech project.

Technology powered by FastAPI, Streamlit, and SQLAlchemy.
EOF