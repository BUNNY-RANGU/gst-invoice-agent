"""
Integration tests for API endpoints
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi.testclient import TestClient
from app.api.routes import app
import pytest


client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'


def test_get_statistics():
    """Test statistics endpoint"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert 'success' in data


def test_rate_limit_config():
    """Test rate limit configuration endpoint"""
    response = client.get("/api/security/rate-limits")
    assert response.status_code == 200
    data = response.json()
    assert 'success' in data
    assert 'rate_limits' in data


def test_backup_list():
    """Test backup list endpoint"""
    response = client.get("/api/backup/list")
    assert response.status_code == 200
    data = response.json()
    assert 'success' in data
    assert 'backups' in data


def test_frequency_options():
    """Test recurring frequency options"""
    response = client.get("/api/recurring/frequencies")
    assert response.status_code == 200
    data = response.json()
    assert 'success' in data
    assert 'frequencies' in data


def test_all_recurring():
    """Test get all recurring invoices"""
    response = client.get("/api/recurring/all")
    assert response.status_code == 200
    data = response.json()
    assert 'success' in data
    assert 'recurring_invoices' in data


def test_pending_reminders():
    """Test pending reminders endpoint"""
    response = client.get("/api/notifications/pending-reminders")
    assert response.status_code == 200
    data = response.json()
    assert 'success' in data


def test_quick_filters():
    """Test quick filters endpoint"""
    response = client.get("/api/search/quick-filters")
    assert response.status_code == 200
    data = response.json()
    assert 'success' in data
    assert 'date_presets' in data


def test_security_stats():
    """Test security statistics"""
    response = client.get("/api/security/stats")
    assert response.status_code == 200
    data = response.json()
    assert 'success' in data
    assert 'stats' in data