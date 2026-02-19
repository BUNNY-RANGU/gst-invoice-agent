"""
Analytics Agent
Advanced analytics and business insights
Author: Bunny Rangu
Day: 12/30
"""

from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np


class AnalyticsAgent:
    """Generate advanced analytics and insights"""
    
    def revenue_trends(self, invoices: List[Dict], period: str = "monthly") -> Dict:
        """
        Calculate revenue trends over time
        
        Args:
            invoices: List of invoices
            period: 'daily', 'weekly', or 'monthly'
            
        Returns:
            Trend data with dates and amounts
        """
        if not invoices:
            return {"dates": [], "revenue": [], "gst": []}
        
        # Group by period
        revenue_by_period = defaultdict(float)
        gst_by_period = defaultdict(float)
        
        for inv in invoices:
            date = inv['date']
            
            if period == "monthly":
                period_key = date[:7]  # YYYY-MM
            elif period == "weekly":
                dt = datetime.strptime(date, "%Y-%m-%d")
                period_key = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
            else:  # daily
                period_key = date
            
            revenue_by_period[period_key] += inv['totals']['grand_total']
            gst_by_period[period_key] += inv['totals']['total_gst']
        
        # Sort by date
        sorted_periods = sorted(revenue_by_period.keys())
        
        return {
            "dates": sorted_periods,
            "revenue": [revenue_by_period[p] for p in sorted_periods],
            "gst": [gst_by_period[p] for p in sorted_periods]
        }
    
    def customer_lifetime_value(self, invoices: List[Dict]) -> List[Dict]:
        """
        Calculate customer lifetime value (CLV)
        
        Args:
            invoices: List of invoices
            
        Returns:
            List of customers with CLV metrics
        """
        customer_data = defaultdict(lambda: {
            'total_spent': 0,
            'invoice_count': 0,
            'first_purchase': None,
            'last_purchase': None,
            'avg_order_value': 0
        })
        
        for inv in invoices:
            customer = inv['customer']['name']
            date = inv['date']
            amount = inv['totals']['grand_total']
            
            customer_data[customer]['total_spent'] += amount
            customer_data[customer]['invoice_count'] += 1
            
            if not customer_data[customer]['first_purchase']:
                customer_data[customer]['first_purchase'] = date
            customer_data[customer]['last_purchase'] = date
        
        # Calculate CLV
        customers = []
        for name, data in customer_data.items():
            data['avg_order_value'] = data['total_spent'] / data['invoice_count']
            
            # Calculate days between first and last purchase
            if data['first_purchase'] != data['last_purchase']:
                first = datetime.strptime(data['first_purchase'], "%Y-%m-%d")
                last = datetime.strptime(data['last_purchase'], "%Y-%m-%d")
                days = (last - first).days
                data['purchase_frequency'] = data['invoice_count'] / max(days / 30, 1)  # Per month
            else:
                data['purchase_frequency'] = 1
            
            # Simple CLV = Avg Order Value × Purchase Frequency × 12 months
            data['clv'] = data['avg_order_value'] * data['purchase_frequency'] * 12
            
            customers.append({
                'name': name,
                **data
            })
        
        # Sort by CLV
        customers.sort(key=lambda x: x['clv'], reverse=True)
        
        return customers
    
    def gst_rate_analysis(self, invoices: List[Dict]) -> Dict:
        """
        Analyze revenue and GST by tax rate
        
        Args:
            invoices: List of invoices
            
        Returns:
            Breakdown by GST rate
        """
        rate_data = defaultdict(lambda: {
            'revenue': 0,
            'gst_collected': 0,
            'item_count': 0,
            'invoice_count': 0
        })
        
        for inv in invoices:
            for item in inv['items']:
                rate = item['gst_rate']
                rate_data[rate]['revenue'] += item['subtotal']
                rate_data[rate]['gst_collected'] += item['total_gst']
                rate_data[rate]['item_count'] += item['quantity']
            
            # Count unique rates per invoice
            unique_rates = set(item['gst_rate'] for item in inv['items'])
            for rate in unique_rates:
                rate_data[rate]['invoice_count'] += 1
        
        # Convert to list
        breakdown = [
            {
                'rate': rate,
                **data
            }
            for rate, data in sorted(rate_data.items())
        ]
        
        return {
            'breakdown': breakdown,
            'total_revenue': sum(d['revenue'] for d in breakdown),
            'total_gst': sum(d['gst_collected'] for d in breakdown)
        }
    
    def product_performance(self, invoices: List[Dict], top_n: int = 10) -> List[Dict]:
        """
        Analyze top-selling products
        
        Args:
            invoices: List of invoices
            top_n: Number of top products to return
            
        Returns:
            Top products by revenue and quantity
        """
        product_data = defaultdict(lambda: {
            'quantity_sold': 0,
            'revenue': 0,
            'gst_collected': 0,
            'avg_price': 0,
            'times_sold': 0
        })
        
        for inv in invoices:
            for item in inv['items']:
                name = item['name']
                product_data[name]['quantity_sold'] += item['quantity']
                product_data[name]['revenue'] += item['total_amount']
                product_data[name]['gst_collected'] += item['total_gst']
                product_data[name]['times_sold'] += 1
        
        # Calculate averages
        products = []
        for name, data in product_data.items():
            data['avg_price'] = data['revenue'] / data['quantity_sold']
            products.append({
                'name': name,
                **data
            })
        
        # Sort by revenue
        products.sort(key=lambda x: x['revenue'], reverse=True)
        
        return products[:top_n]
    
    def payment_insights(self, invoices: List[Dict]) -> Dict:
        """
        Analyze payment patterns
        
        Args:
            invoices: List of invoices
            
        Returns:
            Payment analytics
        """
        total = len(invoices)
        if total == 0:
            return {
                'total_invoices': 0,
                'paid': 0,
                'pending': 0,
                'partial': 0,
                'collection_rate': 0
            }
        
        status_count = defaultdict(int)
        total_amount = 0
        collected_amount = 0
        
        for inv in invoices:
            status_count[inv['payment_status']] += 1
            total_amount += inv['totals']['grand_total']
            
            if inv['payment_status'] == 'Paid':
                collected_amount += inv['totals']['grand_total']
        
        return {
            'total_invoices': total,
            'paid': status_count['Paid'],
            'pending': status_count['Pending'],
            'partial': status_count['Partial'],
            'paid_percentage': round(status_count['Paid'] / total * 100, 1),
            'collection_rate': round(collected_amount / total_amount * 100, 1) if total_amount > 0 else 0,
            'total_amount': total_amount,
            'collected_amount': collected_amount,
            'outstanding_amount': total_amount - collected_amount
        }
    
    def growth_metrics(self, invoices: List[Dict]) -> Dict:
        """
        Calculate growth metrics (MoM, QoQ)
        
        Args:
            invoices: List of invoices
            
        Returns:
            Growth percentages
        """
        if len(invoices) < 2:
            return {
                'mom_growth': 0,
                'qoq_growth': 0
            }
        
        # Group by month
        monthly_revenue = defaultdict(float)
        for inv in invoices:
            month = inv['date'][:7]  # YYYY-MM
            monthly_revenue[month] += inv['totals']['grand_total']
        
        sorted_months = sorted(monthly_revenue.keys())
        
        if len(sorted_months) < 2:
            return {'mom_growth': 0, 'qoq_growth': 0}
        
        # Month-over-Month growth
        current_month = monthly_revenue[sorted_months[-1]]
        previous_month = monthly_revenue[sorted_months[-2]]
        
        if previous_month > 0:
            mom_growth = ((current_month - previous_month) / previous_month) * 100
        else:
            mom_growth = 100 if current_month > 0 else 0
        
        # Quarter-over-Quarter (simplified)
        qoq_growth = 0
        if len(sorted_months) >= 6:
            current_quarter = sum(monthly_revenue[m] for m in sorted_months[-3:])
            previous_quarter = sum(monthly_revenue[m] for m in sorted_months[-6:-3])
            
            if previous_quarter > 0:
                qoq_growth = ((current_quarter - previous_quarter) / previous_quarter) * 100
        
        return {
            'mom_growth': round(mom_growth, 1),
            'qoq_growth': round(qoq_growth, 1),
            'current_month_revenue': current_month,
            'previous_month_revenue': previous_month
        }


def test_analytics_agent():
    """Test analytics agent"""
    print("🧪 TESTING ANALYTICS AGENT\n")
    
    # Sample data
    sample_invoices = [
        {
            'invoice_number': 'INV-2025-1001',
            'date': '2025-01-15',
            'customer': {'name': 'Customer A'},
            'items': [
                {'name': 'Product X', 'quantity': 2, 'unit_price': 1000, 'subtotal': 2000, 'gst_rate': 18, 'total_gst': 360, 'total_amount': 2360}
            ],
            'totals': {'grand_total': 2360, 'total_gst': 360},
            'payment_status': 'Paid'
        },
        {
            'invoice_number': 'INV-2025-1002',
            'date': '2025-02-10',
            'customer': {'name': 'Customer B'},
            'items': [
                {'name': 'Product Y', 'quantity': 1, 'unit_price': 5000, 'subtotal': 5000, 'gst_rate': 12, 'total_gst': 600, 'total_amount': 5600}
            ],
            'totals': {'grand_total': 5600, 'total_gst': 600},
            'payment_status': 'Pending'
        }
    ]
    
    analytics = AnalyticsAgent()
    
    print("✅ Revenue Trends:")
    trends = analytics.revenue_trends(sample_invoices, period="monthly")
    print(f"   Dates: {trends['dates']}")
    print(f"   Revenue: {trends['revenue']}\n")
    
    print("✅ Customer Lifetime Value:")
    clv = analytics.customer_lifetime_value(sample_invoices)
    for c in clv:
        print(f"   {c['name']}: ₹{c['clv']:.2f} CLV\n")
    
    print("✅ GST Rate Analysis:")
    gst = analytics.gst_rate_analysis(sample_invoices)
    print(f"   {len(gst['breakdown'])} tax rates analyzed\n")
    
    print("✅ Product Performance:")
    products = analytics.product_performance(sample_invoices)
    for p in products:
        print(f"   {p['name']}: ₹{p['revenue']:.2f} revenue\n")
    
    print("✅ Payment Insights:")
    payment = analytics.payment_insights(sample_invoices)
    print(f"   Collection Rate: {payment['collection_rate']}%\n")
    
    print("="*50)
    print("✅ ANALYTICS AGENT READY!")
    print("="*50)


if __name__ == "__main__":
    test_analytics_agent()