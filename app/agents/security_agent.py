"""
Security Agent
API rate limiting and security features
Author: Bunny Rangu
Day: 20/30
"""

from typing import Dict
from datetime import datetime, timedelta
from collections import defaultdict
import time


class SecurityAgent:
    """Handle API security and rate limiting"""
    
    def __init__(self):
        # In-memory rate limit tracker
        # In production, use Redis for distributed systems
        self.request_counts = defaultdict(list)
        self.blocked_ips = set()
        
        # Rate limit rules (requests per time window)
        self.RATE_LIMITS = {
            'default': {'requests': 100, 'window': 60},  # 100 requests per minute
            'auth': {'requests': 5, 'window': 60},  # 5 login attempts per minute
            'search': {'requests': 30, 'window': 60},  # 30 searches per minute
            'export': {'requests': 10, 'window': 60},  # 10 exports per minute
            'email': {'requests': 20, 'window': 60}  # 20 emails per minute
        }
    
    def check_rate_limit(self, identifier: str, limit_type: str = 'default') -> Dict:
        """
        Check if request is within rate limits
        
        Args:
            identifier: IP address or user ID
            limit_type: Type of limit to check
            
        Returns:
            Dictionary with allowed status and retry info
        """
        # Check if IP is blocked
        if identifier in self.blocked_ips:
            return {
                'allowed': False,
                'reason': 'IP blocked',
                'retry_after': 3600  # 1 hour
            }
        
        # Get rate limit config
        config = self.RATE_LIMITS.get(limit_type, self.RATE_LIMITS['default'])
        max_requests = config['requests']
        window_seconds = config['window']
        
        # Get current time
        now = time.time()
        
        # Clean old requests outside window
        cutoff_time = now - window_seconds
        self.request_counts[identifier] = [
            req_time for req_time in self.request_counts[identifier]
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        current_count = len(self.request_counts[identifier])
        
        if current_count >= max_requests:
            # Calculate retry after
            oldest_request = min(self.request_counts[identifier])
            retry_after = int(oldest_request + window_seconds - now)
            
            return {
                'allowed': False,
                'reason': f'Rate limit exceeded: {max_requests} requests per {window_seconds}s',
                'retry_after': max(retry_after, 1),
                'current_count': current_count,
                'limit': max_requests
            }
        
        # Add current request
        self.request_counts[identifier].append(now)
        
        return {
            'allowed': True,
            'current_count': current_count + 1,
            'limit': max_requests,
            'remaining': max_requests - current_count - 1,
            'reset_at': int(now + window_seconds)
        }
    
    def block_ip(self, ip_address: str, duration_hours: int = 24):
        """
        Block an IP address
        
        Args:
            ip_address: IP to block
            duration_hours: How long to block (default 24 hours)
        """
        self.blocked_ips.add(ip_address)
        # In production, store in database with expiry
        return {
            'success': True,
            'message': f'IP {ip_address} blocked for {duration_hours} hours'
        }
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            return {
                'success': True,
                'message': f'IP {ip_address} unblocked'
            }
        return {
            'success': False,
            'message': f'IP {ip_address} was not blocked'
        }
    
    def get_rate_limit_stats(self, identifier: str = None) -> Dict:
        """
        Get rate limit statistics
        
        Args:
            identifier: Specific identifier or None for all
        """
        if identifier:
            return {
                'identifier': identifier,
                'request_count': len(self.request_counts.get(identifier, [])),
                'is_blocked': identifier in self.blocked_ips
            }
        
        return {
            'total_identifiers': len(self.request_counts),
            'total_requests': sum(len(reqs) for reqs in self.request_counts.values()),
            'blocked_ips': len(self.blocked_ips),
            'rate_limits': self.RATE_LIMITS
        }
    
    @staticmethod
    def validate_request_headers(headers: Dict) -> Dict:
        """
        Validate security headers
        
        Args:
            headers: Request headers dictionary
            
        Returns:
            Validation result
        """
        issues = []
        
        # Check for suspicious patterns
        user_agent = headers.get('user-agent', '').lower()
        if not user_agent or 'bot' in user_agent or 'crawler' in user_agent:
            issues.append('Suspicious user agent')
        
        # Check content type for POST requests
        content_type = headers.get('content-type', '')
        if content_type and 'application/json' not in content_type:
            issues.append('Invalid content type')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def get_security_headers() -> Dict:
        """
        Get recommended security headers for responses
        
        Returns:
            Dictionary of security headers
        """
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }


def test_security_agent():
    """Test security agent"""
    print("🧪 TESTING SECURITY AGENT\n")
    
    security = SecurityAgent()
    
    # Test 1: Normal rate limiting
    print("Test 1: Check rate limits")
    for i in range(5):
        result = security.check_rate_limit("192.168.1.1", "default")
        print(f"   Request {i+1}: {'✅ Allowed' if result['allowed'] else '❌ Blocked'}")
    print()
    
    # Test 2: Rate limit exceeded
    print("Test 2: Exceed rate limit")
    for i in range(102):
        result = security.check_rate_limit("192.168.1.2", "default")
    
    if not result['allowed']:
        print(f"✅ Rate limit working: {result['reason']}")
        print(f"   Retry after: {result['retry_after']}s\n")
    
    # Test 3: IP blocking
    print("Test 3: Block IP")
    security.block_ip("192.168.1.3")
    result = security.check_rate_limit("192.168.1.3", "default")
    print(f"✅ Blocked IP: {result['reason']}\n")
    
    # Test 4: Get stats
    print("Test 4: Get statistics")
    stats = security.get_rate_limit_stats()
    print(f"✅ Total identifiers: {stats['total_identifiers']}")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Blocked IPs: {stats['blocked_ips']}\n")
    
    print("="*50)
    print("✅ SECURITY AGENT READY!")
    print("="*50)


if __name__ == "__main__":
    test_security_agent()