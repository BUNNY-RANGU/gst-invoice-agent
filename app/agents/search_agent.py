"""
Advanced Search Agent
Powerful filtering and search for invoices
Author: Bunny Rangu
Day: 15/30
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re


class SearchAgent:
    """Advanced search and filtering for invoices"""
    
    @staticmethod
    def filter_by_date_range(
        invoices: List[Dict],
        start_date: str = None,
        end_date: str = None,
        preset: str = None
    ) -> List[Dict]:
        """
        Filter invoices by date range
        
        Args:
            invoices: List of invoices
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            preset: Quick filter ('today', 'this_week', 'this_month', 'this_quarter', 'this_year')
            
        Returns:
            Filtered invoices
        """
        if not invoices:
            return []
        
        # Handle preset filters
        today = datetime.now().date()
        
        if preset == 'today':
            start_date = today.strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        
        elif preset == 'this_week':
            start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        
        elif preset == 'this_month':
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        
        elif preset == 'this_quarter':
            quarter = (today.month - 1) // 3
            start_month = quarter * 3 + 1
            start_date = today.replace(month=start_month, day=1).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        
        elif preset == 'this_year':
            start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        
        elif preset == 'last_30_days':
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        
        # Filter by date range
        if start_date or end_date:
            filtered = []
            for inv in invoices:
                inv_date = inv['date']
                
                if start_date and inv_date < start_date:
                    continue
                if end_date and inv_date > end_date:
                    continue
                
                filtered.append(inv)
            
            return filtered
        
        return invoices
    
    @staticmethod
    def filter_by_amount_range(
        invoices: List[Dict],
        min_amount: float = None,
        max_amount: float = None
    ) -> List[Dict]:
        """
        Filter invoices by total amount
        
        Args:
            invoices: List of invoices
            min_amount: Minimum amount
            max_amount: Maximum amount
            
        Returns:
            Filtered invoices
        """
        if not invoices:
            return []
        
        filtered = []
        for inv in invoices:
            total = inv['totals']['grand_total']
            
            if min_amount is not None and total < min_amount:
                continue
            if max_amount is not None and total > max_amount:
                continue
            
            filtered.append(inv)
        
        return filtered
    
    @staticmethod
    def filter_by_payment_status(
        invoices: List[Dict],
        statuses: List[str]
    ) -> List[Dict]:
        """
        Filter invoices by payment status
        
        Args:
            invoices: List of invoices
            statuses: List of statuses to include ['Paid', 'Pending', 'Partial']
            
        Returns:
            Filtered invoices
        """
        if not invoices or not statuses:
            return invoices
        
        return [inv for inv in invoices if inv['payment_status'] in statuses]
    
    @staticmethod
    def filter_by_gst_rate(
        invoices: List[Dict],
        gst_rates: List[int]
    ) -> List[Dict]:
        """
        Filter invoices by GST rate
        
        Args:
            invoices: List of invoices
            gst_rates: List of GST rates to include [0, 5, 12, 18, 28]
            
        Returns:
            Filtered invoices
        """
        if not invoices or not gst_rates:
            return invoices
        
        filtered = []
        for inv in invoices:
            # Check if any item has the specified GST rate
            has_rate = any(
                item['gst_rate'] in gst_rates
                for item in inv['items']
            )
            
            if has_rate:
                filtered.append(inv)
        
        return filtered
    
    @staticmethod
    def search_by_customer(
        invoices: List[Dict],
        query: str,
        fuzzy: bool = True
    ) -> List[Dict]:
        """
        Search invoices by customer name
        
        Args:
            invoices: List of invoices
            query: Search query
            fuzzy: Enable fuzzy matching
            
        Returns:
            Matching invoices
        """
        if not invoices or not query:
            return invoices
        
        query = query.lower().strip()
        
        if fuzzy:
            # Fuzzy search - matches partial strings
            return [
                inv for inv in invoices
                if query in inv['customer']['name'].lower()
            ]
        else:
            # Exact match
            return [
                inv for inv in invoices
                if inv['customer']['name'].lower() == query
            ]
    
    @staticmethod
    def search_by_invoice_number(
        invoices: List[Dict],
        query: str
    ) -> List[Dict]:
        """
        Search invoices by invoice number
        
        Args:
            invoices: List of invoices
            query: Invoice number or partial number
            
        Returns:
            Matching invoices
        """
        if not invoices or not query:
            return invoices
        
        query = query.upper().strip()
        
        return [
            inv for inv in invoices
            if query in inv['invoice_number'].upper()
        ]
    
    @staticmethod
    def search_by_item(
        invoices: List[Dict],
        query: str
    ) -> List[Dict]:
        """
        Search invoices by item name
        
        Args:
            invoices: List of invoices
            query: Item name search
            
        Returns:
            Matching invoices
        """
        if not invoices or not query:
            return invoices
        
        query = query.lower().strip()
        
        filtered = []
        for inv in invoices:
            # Check if any item matches
            has_item = any(
                query in item['name'].lower()
                for item in inv['items']
            )
            
            if has_item:
                filtered.append(inv)
        
        return filtered
    
    @staticmethod
    def advanced_search(
        invoices: List[Dict],
        filters: Dict
    ) -> List[Dict]:
        """
        Apply multiple filters at once
        
        Args:
            invoices: List of invoices
            filters: Dictionary of filter parameters
            
        Returns:
            Filtered invoices
        """
        result = invoices
        
        # Date range
        if filters.get('date_preset') or filters.get('start_date') or filters.get('end_date'):
            result = SearchAgent.filter_by_date_range(
                result,
                start_date=filters.get('start_date'),
                end_date=filters.get('end_date'),
                preset=filters.get('date_preset')
            )
        
        # Amount range
        if filters.get('min_amount') is not None or filters.get('max_amount') is not None:
            result = SearchAgent.filter_by_amount_range(
                result,
                min_amount=filters.get('min_amount'),
                max_amount=filters.get('max_amount')
            )
        
        # Payment status
        if filters.get('payment_statuses'):
            result = SearchAgent.filter_by_payment_status(
                result,
                filters['payment_statuses']
            )
        
        # GST rates
        if filters.get('gst_rates'):
            result = SearchAgent.filter_by_gst_rate(
                result,
                filters['gst_rates']
            )
        
        # Customer search
        if filters.get('customer_query'):
            result = SearchAgent.search_by_customer(
                result,
                filters['customer_query'],
                fuzzy=filters.get('fuzzy_search', True)
            )
        
        # Invoice number
        if filters.get('invoice_number'):
            result = SearchAgent.search_by_invoice_number(
                result,
                filters['invoice_number']
            )
        
        # Item search
        if filters.get('item_query'):
            result = SearchAgent.search_by_item(
                result,
                filters['item_query']
            )
        
        return result
    
    @staticmethod
    def get_filter_summary(filters: Dict, result_count: int) -> str:
        """
        Generate human-readable summary of active filters
        
        Args:
            filters: Applied filters
            result_count: Number of results
            
        Returns:
            Summary string
        """
        parts = []
        
        if filters.get('date_preset'):
            parts.append(f"{filters['date_preset'].replace('_', ' ')}")
        elif filters.get('start_date') or filters.get('end_date'):
            if filters.get('start_date') and filters.get('end_date'):
                parts.append(f"from {filters['start_date']} to {filters['end_date']}")
            elif filters.get('start_date'):
                parts.append(f"from {filters['start_date']}")
            elif filters.get('end_date'):
                parts.append(f"until {filters['end_date']}")
        
        if filters.get('min_amount') or filters.get('max_amount'):
            if filters.get('min_amount') and filters.get('max_amount'):
                parts.append(f"₹{filters['min_amount']:,.0f} - ₹{filters['max_amount']:,.0f}")
            elif filters.get('min_amount'):
                parts.append(f"≥ ₹{filters['min_amount']:,.0f}")
            elif filters.get('max_amount'):
                parts.append(f"≤ ₹{filters['max_amount']:,.0f}")
        
        if filters.get('payment_statuses'):
            parts.append(f"status: {', '.join(filters['payment_statuses'])}")
        
        if filters.get('customer_query'):
            parts.append(f"customer: {filters['customer_query']}")
        
        if not parts:
            return f"Showing all {result_count} invoices"
        
        return f"Showing {result_count} invoices: {' | '.join(parts)}"


def test_search_agent():
    """Test search agent"""
    print("🧪 TESTING SEARCH AGENT\n")
    
    # Sample data
    sample_invoices = [
        {
            'invoice_number': 'INV-2025-1001',
            'date': '2025-02-01',
            'customer': {'name': 'John Doe'},
            'items': [{'name': 'Laptop', 'gst_rate': 18}],
            'totals': {'grand_total': 50000},
            'payment_status': 'Paid'
        },
        {
            'invoice_number': 'INV-2025-1002',
            'date': '2025-02-15',
            'customer': {'name': 'Jane Smith'},
            'items': [{'name': 'Mouse', 'gst_rate': 12}],
            'totals': {'grand_total': 5000},
            'payment_status': 'Pending'
        }
    ]
    
    # Test filters
    print("✅ Test 1: Filter by date range")
    result = SearchAgent.filter_by_date_range(sample_invoices, preset='this_month')
    print(f"   Found {len(result)} invoices\n")
    
    print("✅ Test 2: Filter by amount")
    result = SearchAgent.filter_by_amount_range(sample_invoices, min_amount=10000)
    print(f"   Found {len(result)} invoices ≥ ₹10,000\n")
    
    print("✅ Test 3: Search by customer")
    result = SearchAgent.search_by_customer(sample_invoices, 'john')
    print(f"   Found {len(result)} invoices for 'john'\n")
    
    print("✅ Test 4: Advanced multi-filter")
    filters = {
        'payment_statuses': ['Paid'],
        'min_amount': 10000
    }
    result = SearchAgent.advanced_search(sample_invoices, filters)
    print(f"   Found {len(result)} invoices\n")
    
    summary = SearchAgent.get_filter_summary(filters, len(result))
    print(f"   Summary: {summary}\n")
    
    print("="*50)
    print("✅ SEARCH AGENT READY!")
    print("="*50)


if __name__ == "__main__":
    test_search_agent()