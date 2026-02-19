"""
Audit Agent
Track and log all user actions for compliance
Author: Bunny Rangu
Day: 17/30
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.database import AuditLog, SessionLocal


class AuditAgent:
    """Handle all audit logging and tracking"""
    
    ACTION_TYPES = {
        'LOGIN': 'User logged in',
        'LOGOUT': 'User logged out',
        'CREATE_INVOICE': 'Invoice created',
        'UPDATE_INVOICE': 'Invoice updated',
        'DELETE_INVOICE': 'Invoice deleted',
        'CREATE_PAYMENT': 'Payment recorded',
        'UPDATE_PAYMENT': 'Payment updated',
        'SEND_EMAIL': 'Email sent',
        'DOWNLOAD_PDF': 'PDF downloaded',
        'EXPORT_DATA': 'Data exported',
        'IMPORT_DATA': 'Data imported',
        'SEARCH': 'Search performed',
        'VIEW': 'Record viewed'
    }
    
    @staticmethod
    def log_action(
        user: str,
        action: str,
        entity_type: str = None,
        entity_id: str = None,
        details: Dict = None,
        ip_address: str = None,
        status: str = 'success'
    ) -> Dict:
        """
        Log an action to audit trail
        
        Args:
            user: Username who performed action
            action: Action type (LOGIN, CREATE_INVOICE, etc.)
            entity_type: Type of entity (invoice, payment, customer)
            entity_id: ID of entity (invoice number, payment ID)
            details: Additional details as dictionary
            ip_address: User's IP address
            status: Action status (success, failed, error)
            
        Returns:
            Success/failure dictionary
        """
        db = SessionLocal()
        
        try:
            # Create audit log entry
            log = AuditLog(
                user=user,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                status=status
            )
            
            db.add(log)
            db.commit()
            db.refresh(log)
            
            return {
                'success': True,
                'log_id': log.id,
                'message': 'Action logged'
            }
            
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            db.close()
    
    @staticmethod
    def get_logs(
        user: str = None,
        action: str = None,
        entity_type: str = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve audit logs with filters
        
        Args:
            user: Filter by username
            action: Filter by action type
            entity_type: Filter by entity type
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of results
            
        Returns:
            List of audit log entries
        """
        db = SessionLocal()
        
        try:
            query = db.query(AuditLog)
            
            # Apply filters
            if user:
                query = query.filter(AuditLog.user == user)
            
            if action:
                query = query.filter(AuditLog.action == action)
            
            if entity_type:
                query = query.filter(AuditLog.entity_type == entity_type)
            
            if start_date:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(AuditLog.timestamp >= start)
            
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                end = end.replace(hour=23, minute=59, second=59)
                query = query.filter(AuditLog.timestamp <= end)
            
            # Order by most recent first
            query = query.order_by(AuditLog.timestamp.desc())
            
            # Limit results
            logs = query.limit(limit).all()
            
            # Convert to dictionaries
            result = []
            for log in logs:
                result.append({
                    'id': log.id,
                    'timestamp': log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'user': log.user,
                    'action': log.action,
                    'action_description': AuditAgent.ACTION_TYPES.get(log.action, log.action),
                    'entity_type': log.entity_type,
                    'entity_id': log.entity_id,
                    'details': json.loads(log.details) if log.details else None,
                    'ip_address': log.ip_address,
                    'status': log.status
                })
            
            return result
            
        finally:
            db.close()
    
    @staticmethod
    def get_user_activity(user: str, days: int = 30) -> Dict:
        """
        Get activity summary for a specific user
        
        Args:
            user: Username
            days: Number of days to look back
            
        Returns:
            Activity statistics
        """
        db = SessionLocal()
        
        try:
            # Get logs from last N days
            start_date = datetime.now() - timedelta(days=days)
            
            logs = db.query(AuditLog).filter(
                AuditLog.user == user,
                AuditLog.timestamp >= start_date
            ).all()
            
            # Calculate statistics
            total_actions = len(logs)
            
            # Count by action type
            action_counts = {}
            for log in logs:
                action_counts[log.action] = action_counts.get(log.action, 0) + 1
            
            # Count by status
            success_count = sum(1 for log in logs if log.status == 'success')
            failed_count = sum(1 for log in logs if log.status != 'success')
            
            # Most recent activity
            recent = logs[:5] if logs else []
            recent_activities = [
                {
                    'timestamp': log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'action': log.action,
                    'entity_type': log.entity_type,
                    'entity_id': log.entity_id
                }
                for log in recent
            ]
            
            return {
                'user': user,
                'period_days': days,
                'total_actions': total_actions,
                'success_count': success_count,
                'failed_count': failed_count,
                'action_breakdown': action_counts,
                'recent_activities': recent_activities
            }
            
        finally:
            db.close()
    
    @staticmethod
    def get_system_activity(days: int = 7) -> Dict:
        """
        Get overall system activity statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            System-wide statistics
        """
        db = SessionLocal()
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            logs = db.query(AuditLog).filter(
                AuditLog.timestamp >= start_date
            ).all()
            
            # Total actions
            total_actions = len(logs)
            
            # Unique users
            unique_users = len(set(log.user for log in logs))
            
            # Actions by user
            user_actions = {}
            for log in logs:
                user_actions[log.user] = user_actions.get(log.user, 0) + 1
            
            # Most active users
            top_users = sorted(
                user_actions.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Actions by type
            action_counts = {}
            for log in logs:
                action_counts[log.action] = action_counts.get(log.action, 0) + 1
            
            # Daily activity
            daily_counts = {}
            for log in logs:
                day = log.timestamp.strftime("%Y-%m-%d")
                daily_counts[day] = daily_counts.get(day, 0) + 1
            
            return {
                'period_days': days,
                'total_actions': total_actions,
                'unique_users': unique_users,
                'top_users': [{'user': u, 'actions': c} for u, c in top_users],
                'action_breakdown': action_counts,
                'daily_activity': daily_counts
            }
            
        finally:
            db.close()
    
    @staticmethod
    def export_audit_trail(
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Export complete audit trail for compliance
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Complete audit trail
        """
        return AuditAgent.get_logs(
            start_date=start_date,
            end_date=end_date,
            limit=10000  # High limit for export
        )


def test_audit_agent():
    """Test audit agent"""
    print("🧪 TESTING AUDIT AGENT\n")
    
    # Test 1: Log actions
    print("Test 1: Log actions")
    result = AuditAgent.log_action(
        user="bunny",
        action="CREATE_INVOICE",
        entity_type="invoice",
        entity_id="INV-2025-1000",
        details={"amount": 50000, "customer": "Test Customer"},
        ip_address="192.168.1.1"
    )
    print(f"✅ Logged: {result['message']}\n")
    
    result = AuditAgent.log_action(
        user="bunny",
        action="LOGIN",
        ip_address="192.168.1.1"
    )
    print(f"✅ Logged: {result['message']}\n")
    
    # Test 2: Get logs
    print("Test 2: Get logs")
    logs = AuditAgent.get_logs(user="bunny", limit=10)
    print(f"✅ Retrieved {len(logs)} logs\n")
    
    # Test 3: User activity
    print("Test 3: User activity")
    activity = AuditAgent.get_user_activity("bunny", days=30)
    print(f"✅ Total actions: {activity['total_actions']}")
    print(f"   Success: {activity['success_count']}\n")
    
    # Test 4: System activity
    print("Test 4: System activity")
    system = AuditAgent.get_system_activity(days=7)
    print(f"✅ Total actions: {system['total_actions']}")
    print(f"   Unique users: {system['unique_users']}\n")
    
    print("="*50)
    print("✅ AUDIT AGENT READY!")
    print("="*50)


if __name__ == "__main__":
    test_audit_agent()