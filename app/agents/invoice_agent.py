"""
Invoice Agent - Main Orchestrator
Combines Validator + Calculator to create complete invoices
Author: Bunny Rangu
Day: 3/30
"""

from datetime import datetime
from typing import List, Dict, Tuple
from app.agents.validator import InvoiceValidator
from app.agents.gst_calculator import GSTCalculator


class InvoiceAgent:
    """
    Main invoice agent - orchestrates the entire invoice creation workflow
    
    Workflow:
    1. Validate customer details
    2. Validate all items
    3. Calculate GST for each item
    4. Generate invoice number
    5. Create complete invoice object
    6. Store invoice
    """
    
    def __init__(self):
        """Initialize the agent"""
        self.validator = InvoiceValidator()
        self.invoices = []  # In-memory storage (will become database later)
        self.invoice_counter = 1000  # Starting invoice number
        self.company_details = {
            'name': 'AI Tax Solutions',
            'address': 'Hyderabad, Telangana',
            'gst_number': '36AABCU9603R1ZM',  # Sample GST number
            'phone': '9876543210',
            'email': 'info@aitaxsolutions.com'
        }
    
    def generate_invoice_number(self) -> str:
        """
        Generate unique invoice number
        
        Returns:
            Invoice number in format: INV-YYYY-NNNN
        """
        year = datetime.now().year
        invoice_number = f"INV-{year}-{self.invoice_counter}"
        self.invoice_counter += 1
        return invoice_number
    
    def validate_customer(self, customer: Dict) -> Tuple[bool, str]:
        """
        Validate customer details
        
        Args:
            customer: Dictionary with customer details
            
        Returns:
            (is_valid, error_message)
        """
        return self.validator.validate_customer_details(customer)
    
    def validate_items(self, items: List[Dict]) -> Tuple[bool, str]:
        """
        Validate all invoice items
        
        Args:
            items: List of item dictionaries
            
        Returns:
            (is_valid, error_message)
        """
        if not items or len(items) == 0:
            return False, "Invoice must have at least one item"
        
        for idx, item in enumerate(items):
            is_valid, msg = self.validator.validate_invoice_item(item)
            if not is_valid:
                return False, f"Item {idx + 1} - {msg}"
        
        return True, "Valid"
    
    def calculate_item_totals(self, items: List[Dict]) -> List[Dict]:
        """
        Calculate GST and totals for all items
        
        Args:
            items: List of item dictionaries
            
        Returns:
            List of items with calculated GST amounts
        """
        calculated_items = []
        
        for item in items:
            # Create calculator for this item
            calculator = GSTCalculator(
                base_price=item['price'],
                gst_rate=item['gst_rate'],
                quantity=item['quantity']
            )
            
            # Get calculation result
            result = calculator.calculate()
            
            # Combine original item with calculations
            calculated_item = {
                'name': item['name'],
                'description': item.get('description', ''),
                'hsn_code': item.get('hsn_code', ''),  # HSN code (optional)
                'quantity': result['quantity'],
                'unit_price': result['base_price_per_unit'],
                'subtotal': result['total_base_amount'],
                'gst_rate': result['gst_rate'],
                'cgst_rate': result['gst_rate'] / 2,
                'sgst_rate': result['gst_rate'] / 2,
                'cgst_amount': result['cgst'],
                'sgst_amount': result['sgst'],
                'total_gst': result['total_gst'],
                'total_amount': result['final_price']
            }
            
            calculated_items.append(calculated_item)
        
        return calculated_items
    
    def calculate_invoice_totals(self, calculated_items: List[Dict]) -> Dict:
        """
        Calculate overall invoice totals
        
        Args:
            calculated_items: List of items with calculations
            
        Returns:
            Dictionary with total amounts
        """
        total_subtotal = sum(item['subtotal'] for item in calculated_items)
        total_cgst = sum(item['cgst_amount'] for item in calculated_items)
        total_sgst = sum(item['sgst_amount'] for item in calculated_items)
        total_gst = sum(item['total_gst'] for item in calculated_items)
        grand_total = sum(item['total_amount'] for item in calculated_items)
        
        return {
            'subtotal': round(total_subtotal, 2),
            'total_cgst': round(total_cgst, 2),
            'total_sgst': round(total_sgst, 2),
            'total_gst': round(total_gst, 2),
            'grand_total': round(grand_total, 2),
            'total_items': len(calculated_items),
            'total_quantity': sum(item['quantity'] for item in calculated_items)
        }
    
    def create_invoice(self, customer: Dict, items: List[Dict], notes: str = "") -> Dict:
        """
        Create complete invoice
        
        Args:
            customer: Customer details dictionary
            items: List of item dictionaries
            notes: Optional notes/terms
            
        Returns:
            Complete invoice dictionary or error
        """
        # Step 1: Validate customer
        is_valid, msg = self.validate_customer(customer)
        if not is_valid:
            return {
                'success': False,
                'error': f"Customer validation failed: {msg}"
            }
        
        # Step 2: Validate items
        is_valid, msg = self.validate_items(items)
        if not is_valid:
            return {
                'success': False,
                'error': f"Items validation failed: {msg}"
            }
        
        # Step 3: Calculate GST for all items
        calculated_items = self.calculate_item_totals(items)
        
        # Step 4: Calculate invoice totals
        totals = self.calculate_invoice_totals(calculated_items)
        
        # Step 5: Generate invoice number
        invoice_number = self.generate_invoice_number()
        
        # Step 6: Create invoice object
        invoice = {
            'invoice_number': invoice_number,
            'date': datetime.now().strftime("%Y-%m-%d"),
            'time': datetime.now().strftime("%H:%M:%S"),
            
            # Company details
            'company': self.company_details,
            
            # Customer details
            'customer': {
                'name': customer['name'],
                'phone': customer['phone'],
                'email': customer.get('email', ''),
                'address': customer.get('address', ''),
                'gst_number': customer.get('gst_number', ''),
                'state': customer.get('state', 'Telangana')
            },
            
            # Items
            'items': calculated_items,
            
            # Totals
            'totals': totals,
            
            # Additional info
            'notes': notes,
            'payment_status': 'Pending',
            'payment_method': '',
            
            # Metadata
            'created_at': datetime.now().isoformat(),
            'status': 'Draft'
        }
        
        # Step 7: Store invoice
        self.invoices.append(invoice)
        
        return {
            'success': True,
            'invoice': invoice,
            'message': f"Invoice {invoice_number} created successfully"
        }
    
    def get_invoice(self, invoice_number: str) -> Dict:
        """
        Retrieve invoice by number
        
        Args:
            invoice_number: Invoice number to find
            
        Returns:
            Invoice dictionary or None
        """
        for invoice in self.invoices:
            if invoice['invoice_number'] == invoice_number:
                return invoice
        return None
    
    def get_all_invoices(self) -> List[Dict]:
        """Get all invoices"""
        return self.invoices
    
    def get_customer_invoices(self, customer_name: str) -> List[Dict]:
        """
        Get all invoices for a specific customer
        
        Args:
            customer_name: Customer name
            
        Returns:
            List of invoices
        """
        return [
            inv for inv in self.invoices 
            if inv['customer']['name'].lower() == customer_name.lower()
        ]
    
    def display_invoice(self, invoice: Dict) -> None:
        """
        Display invoice in readable format
        
        Args:
            invoice: Invoice dictionary
        """
        print("\n" + "="*70)
        print(f"TAX INVOICE: {invoice['invoice_number']}")
        print("="*70)
        
        # Company details
        print(f"\nFROM:")
        print(f"{invoice['company']['name']}")
        print(f"{invoice['company']['address']}")
        print(f"GST: {invoice['company']['gst_number']}")
        print(f"Phone: {invoice['company']['phone']}")
        
        # Customer details
        print(f"\nTO:")
        print(f"{invoice['customer']['name']}")
        print(f"Phone: {invoice['customer']['phone']}")
        if invoice['customer']['email']:
            print(f"Email: {invoice['customer']['email']}")
        if invoice['customer']['gst_number']:
            print(f"GST: {invoice['customer']['gst_number']}")
        
        # Date
        print(f"\nDate: {invoice['date']}")
        print(f"Time: {invoice['time']}")
        
        # Items table
        print("\n" + "-"*70)
        print(f"{'Item':<25} {'Qty':<5} {'Price':<10} {'GST%':<6} {'Amount':<12}")
        print("-"*70)
        
        for item in invoice['items']:
            print(f"{item['name']:<25} {item['quantity']:<5} "
                  f"₹{item['unit_price']:<9} {item['gst_rate']:<6} "
                  f"₹{item['total_amount']:<11}")
        
        print("-"*70)
        
        # Totals
        totals = invoice['totals']
        print(f"\n{'Subtotal:':<50} ₹{totals['subtotal']:>15,.2f}")
        print(f"{'CGST:':<50} ₹{totals['total_cgst']:>15,.2f}")
        print(f"{'SGST:':<50} ₹{totals['total_sgst']:>15,.2f}")
        print(f"{'Total GST:':<50} ₹{totals['total_gst']:>15,.2f}")
        print("="*70)
        print(f"{'GRAND TOTAL:':<50} ₹{totals['grand_total']:>15,.2f}")
        print("="*70)
        
        if invoice['notes']:
            print(f"\nNotes: {invoice['notes']}")
        
        print(f"\nTotal Items: {totals['total_items']}")
        print(f"Total Quantity: {totals['total_quantity']}")
        print()


def test_invoice_agent():
    """Test the invoice agent"""
    print("🧪 TESTING INVOICE AGENT\n")
    
    # Create agent
    agent = InvoiceAgent()
    
    # Test 1: Create invoice with valid data
    print("Test 1: Creating invoice with valid data")
    print("-" * 50)
    
    customer = {
        'name': 'Rajesh Kumar',
        'phone': '9876543210',
        'email': 'rajesh@example.com',
        'address': 'Mumbai, Maharashtra',
        'gst_number': '27ABCDE1234F1Z5'
    }
    
    items = [
        {
            'name': 'Laptop Dell Inspiron',
            'description': '15.6 inch, 8GB RAM',
            'price': 50000,
            'quantity': 1,
            'gst_rate': 18
        },
        {
            'name': 'Wireless Mouse',
            'description': 'Logitech M185',
            'price': 500,
            'quantity': 2,
            'gst_rate': 18
        },
        {
            'name': 'HDMI Cable',
            'price': 300,
            'quantity': 1,
            'gst_rate': 18
        }
    ]
    
    result = agent.create_invoice(customer, items, notes="Thank you for your business!")
    
    if result['success']:
        print(f"✅ {result['message']}")
        agent.display_invoice(result['invoice'])
    else:
        print(f"❌ Error: {result['error']}")
    
    # Test 2: Create another invoice
    print("\nTest 2: Creating second invoice")
    print("-" * 50)
    
    customer2 = {
        'name': 'Priya Sharma',
        'phone': '8765432109',
        'email': 'priya@example.com'
    }
    
    items2 = [
        {
            'name': 'Rice (Premium)',
            'price': 250,
            'quantity': 5,
            'gst_rate': 0
        },
        {
            'name': 'Cooking Oil (Fortune)',
            'price': 150,
            'quantity': 2,
            'gst_rate': 5
        }
    ]
    
    result2 = agent.create_invoice(customer2, items2)
    
    if result2['success']:
        print(f"✅ {result2['message']}")
        agent.display_invoice(result2['invoice'])
    else:
        print(f"❌ Error: {result2['error']}")
    
    # Test 3: Invalid customer data
    print("\nTest 3: Testing with invalid customer phone")
    print("-" * 50)
    
    invalid_customer = {
        'name': 'Test User',
        'phone': '123',  # Invalid phone
        'email': 'test@example.com'
    }
    
    result3 = agent.create_invoice(invalid_customer, items)
    print(f"❌ Expected error: {result3['error']}")
    
    # Test 4: Get all invoices
    print("\nTest 4: Retrieving all invoices")
    print("-" * 50)
    all_invoices = agent.get_all_invoices()
    print(f"✅ Total invoices created: {len(all_invoices)}")
    for inv in all_invoices:
        print(f"  - {inv['invoice_number']}: {inv['customer']['name']} - ₹{inv['totals']['grand_total']}")
    
    print("\n" + "="*70)
    print("✅ ALL INVOICE AGENT TESTS COMPLETED!")
    print("="*70)


if __name__ == "__main__":
    test_invoice_agent()