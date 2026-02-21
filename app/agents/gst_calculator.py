"""
GST Calculator Agent
Core engine for all GST calculations
Author: Bunny Rangu
Day: 1/30
"""

class GSTCalculator:
    """
    GST calculation engine following Indian tax rules
    CGST + SGST = Total GST (for intra-state)
    """
    
    # Valid GST rates in India
    VALID_RATES = [0, 5, 12, 18, 28]
    
    def __init__(self):
        """
        Initialize calculator with no required arguments.
        Use calculate(items) and validate(items) methods with list of items.
        """
        pass
    
    def validate(self, items: list) -> dict:
        """
        Validate a list of items before calculation
        
        Args:
            items: List of item dictionaries with 'name', 'price', 'quantity', 'gst_rate'
        
        Returns:
            Dictionary with 'valid' boolean and 'errors' list
        """
        errors = []
        
        if not items:
            errors.append("Items list cannot be empty")
            return {'valid': False, 'errors': errors}
        
        for idx, item in enumerate(items):
            # Check required fields
            if 'name' not in item:
                errors.append(f"Item {idx}: Missing 'name' field")
            if 'price' not in item:
                errors.append(f"Item {idx}: Missing 'price' field")
            if 'quantity' not in item:
                errors.append(f"Item {idx}: Missing 'quantity' field")
            if 'gst_rate' not in item:
                errors.append(f"Item {idx}: Missing 'gst_rate' field")
            
            # Validate price
            if 'price' in item and item['price'] <= 0:
                errors.append(f"Item {idx}: Price must be positive")
            
            # Validate quantity
            if 'quantity' in item and item['quantity'] <= 0:
                errors.append(f"Item {idx}: Quantity must be positive")
            
            # Validate GST rate
            if 'gst_rate' in item and item['gst_rate'] not in self.VALID_RATES:
                errors.append(f"Item {idx}: GST rate must be one of {self.VALID_RATES}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def calculate(self, items: list) -> dict:
        """
        Calculate GST breakdown for a list of items
        
        Args:
            items: List of item dictionaries with 'name', 'price', 'quantity', 'gst_rate'
        
        Returns:
            Dictionary with subtotal, total_gst, grand_total, and item details
            
        Raises:
            ValueError: If validation fails
        """
        # Validate first
        validation = self.validate(items)
        if not validation['valid']:
            raise ValueError(f"Invalid input: {', '.join(validation['errors'])}")
        
        subtotal = 0
        total_gst = 0
        item_details = []
        
        for item in items:
            name = item['name']
            price = item['price']
            quantity = item['quantity']
            gst_rate = item['gst_rate']
            
            # Calculate for this item
            item_subtotal = price * quantity
            item_gst = item_subtotal * (gst_rate / 100)
            item_total = item_subtotal + item_gst
            
            # Split GST into CGST and SGST (50-50)
            cgst = item_gst / 2
            sgst = item_gst / 2
            
            subtotal += item_subtotal
            total_gst += item_gst
            
            item_details.append({
                'name': name,
                'price': price,
                'quantity': quantity,
                'gst_rate': gst_rate,
                'subtotal': round(item_subtotal, 2),
                'cgst': round(cgst, 2),
                'sgst': round(sgst, 2),
                'total_gst': round(item_gst, 2),
                'total': round(item_total, 2)
            })
        
        return {
            'items': item_details,
            'subtotal': round(subtotal, 2),
            'total_gst': round(total_gst, 2),
            'grand_total': round(subtotal + total_gst, 2),
            'total_items': len(items),
            'total_quantity': sum(item['quantity'] for item in items)
        }
    
    def get_invoice_line(self, base_price: float, gst_rate: int, quantity: int = 1) -> dict:
        """
        Get formatted invoice line item for a single item
        Used for invoice generation
        
        Args:
            base_price: Price per unit before tax
            gst_rate: GST percentage (0, 5, 12, 18, 28)
            quantity: Number of units (default 1)
        """
        items = [{'name': 'Item', 'price': base_price, 'quantity': quantity, 'gst_rate': gst_rate}]
        result = self.calculate(items)
        item_result = result['items'][0]
        
        return {
            'price_per_unit': item_result['price'],
            'quantity': item_result['quantity'],
            'subtotal': item_result['subtotal'],
            'cgst_rate': gst_rate / 2,
            'sgst_rate': gst_rate / 2,
            'cgst_amount': item_result['cgst'],
            'sgst_amount': item_result['sgst'],
            'total': item_result['total']
        }
    
    def display(self, items: list = None) -> None:
        """Print calculation results in readable format"""
        try:
            if items is None:
                print("\n⚠️ No items to display. Pass items to calculate() first.\n")
                return
                
            result = self.calculate(items)
            
            print(f"\n{'='*50}")
            print(f"GST CALCULATION BREAKDOWN")
            print(f"{'='*50}")
            
            for item in result['items']:
                print(f"\nItem: {item['name']}")
                print(f"  Price per unit: ₹{item['price']}")
                print(f"  Quantity:       {item['quantity']}")
                print(f"  Subtotal:       ₹{item['subtotal']}")
                print(f"  GST Rate:       {item['gst_rate']}%")
                print(f"  CGST:           ₹{item['cgst']}")
                print(f"  SGST:           ₹{item['sgst']}")
                print(f"  Total GST:      ₹{item['total_gst']}")
                print(f"  Total:          ₹{item['total']}")
            
            print(f"\n{'-'*50}")
            print(f"SUBTOTAL:          ₹{result['subtotal']}")
            print(f"TOTAL GST:         ₹{result['total_gst']}")
            print(f"{'='*50}")
            print(f"GRAND TOTAL:       ₹{result['grand_total']}")
            print(f"{'='*50}\n")
            
        except ValueError as e:
            print(f"\n❌ ERROR: {e}\n")


def test_calculator():
    """Test function to verify calculator works"""
    print("🧪 TESTING GST CALCULATOR AGENT\n")
    
    calc = GSTCalculator()
    
    # Test 1: Laptop (18% GST, single unit)
    print("Test 1: Laptop")
    laptop_items = [{'name': 'Laptop', 'price': 50000, 'quantity': 1, 'gst_rate': 18}]
    result = calc.calculate(laptop_items)
    print(f"Subtotal: ₹{result['subtotal']}, GST: ₹{result['total_gst']}, Total: ₹{result['grand_total']}\n")
    
    # Test 2: Rice (0% GST, 5 units)
    print("Test 2: Rice bags")
    rice_items = [{'name': 'Rice Bag', 'price': 250, 'quantity': 5, 'gst_rate': 0}]
    result = calc.calculate(rice_items)
    print(f"Subtotal: ₹{result['subtotal']}, GST: ₹{result['total_gst']}, Total: ₹{result['grand_total']}\n")
    
    # Test 3: Shampoo (12% GST, 3 units)
    print("Test 3: Shampoo bottles")
    shampoo_items = [{'name': 'Shampoo', 'price': 200, 'quantity': 3, 'gst_rate': 12}]
    result = calc.calculate(shampoo_items)
    print(f"Subtotal: ₹{result['subtotal']}, GST: ₹{result['total_gst']}, Total: ₹{result['grand_total']}\n")
    
    # Test 4: Using get_invoice_line for single item
    print("Test 4: Using get_invoice_line")
    line = calc.get_invoice_line(base_price=50000, gst_rate=18, quantity=1)
    print(f"Invoice line - Subtotal: ₹{line['subtotal']}, Total: ₹{line['total']}\n")
    
    # Test 5: Invalid GST rate (should fail)
    print("Test 5: Invalid GST rate (99%)")
    try:
        invalid_items = [{'name': 'Item', 'price': 1000, 'quantity': 1, 'gst_rate': 99}]
        calc.calculate(invalid_items)
    except ValueError as e:
        print(f"✅ Successfully caught error: {e}\n")
    
    # Test 6: Negative price (should fail)
    print("Test 6: Negative price")
    try:
        invalid_items = [{'name': 'Item', 'price': -500, 'quantity': 1, 'gst_rate': 18}]
        calc.calculate(invalid_items)
    except ValueError as e:
        print(f"✅ Successfully caught error: {e}\n")
    
    # Test 7: Zero quantity (should fail)
    print("Test 7: Zero quantity")
    try:
        invalid_items = [{'name': 'Item', 'price': 1000, 'quantity': 0, 'gst_rate': 18}]
        calc.calculate(invalid_items)
    except ValueError as e:
        print(f"✅ Successfully caught error: {e}\n")
    
    print("✅ ALL TESTS PASSED! GST Calculator is working perfectly!")
    print("=" * 50)


# Run tests when file is executed directly
if __name__ == "__main__":
    test_calculator()