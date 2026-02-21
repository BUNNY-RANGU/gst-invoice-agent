cat > DEPLOYMENT.md << 'EOF'
# Deployment Guide

## Option 1: Railway (Recommended for beginners)

### Why Railway?
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Built-in PostgreSQL
- ✅ Easy to use
- ✅ HTTPS included

### Prerequisites
- GitHub account
- Railway account (free)

### Steps
1. Push code to GitHub
2. Sign up at https://railway.app
3. Connect GitHub repository
4. Add PostgreSQL database
5. Set environment variables
6. Deploy!

Detailed steps coming in Day 27...

## Option 2: Render

### Why Render?
- ✅ Free tier
- ✅ Auto-deploy from GitHub
- ✅ Easy setup

## Option 3: Local Docker

### For Testing
```bash
docker build -t gst-invoice-agent .
docker run -p 8000:8000 gst-invoice-agent
```

## Environment Variables Needed
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
```

## Post-Deployment Checklist

- [ ] Test API endpoints
- [ ] Test authentication
- [ ] Create test invoice
- [ ] Test PDF generation
- [ ] Test email sending
- [ ] Check analytics
- [ ] Test backup/restore
EOF