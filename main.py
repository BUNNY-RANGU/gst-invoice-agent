"""
GST Invoice Agent - Main Entry Point
Author: Bunny Rangu
Day: 4/30
"""

import uvicorn
from app.api.routes import app

if __name__ == "__main__":
    print("="*60)
    print("🚀 GST INVOICE AGENT API")
    print("="*60)
    print("📖 Interactive API Docs: http://localhost:8000/docs")
    print("📚 Alternative Docs: http://localhost:8000/redoc")
    print("🌐 API Base URL: http://localhost:8000")
    print("="*60)
    print("\n✅ Server starting...\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
