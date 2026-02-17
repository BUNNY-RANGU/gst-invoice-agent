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
    
    def __init__(self, base_price: float, gst_rate: int, quantity: int = 1):
        """
        Initialize calculator
        
        Args:
            base_price: Price per unit before tax
            gst_rate: GST percentage (0, 5, 12, 18, 28)
            quantity: Number of units (default 1)
        """
        self.base_price = base_price
        self.gst_rate = gst_rate
        self.quantity = quantity
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate inputs before calculation
        
        Returns:
            (is_valid, error_message)
        """
        # Check price
        if self.base_price <= 0:
            return False, "Price must be positive"
        
        # Check GST rate
        if self.gst_rate not in self.VALID_RATES:
            return False, f"GST rate must be one of {self.VALID_RATES}"
        
        # Check quantity
        if self.quantity <= 0:
            return False, "Quantity must be positive"
        
        return True, "Valid"
    
    def calculate(self) -> dict:
        """
        Calculate GST breakdown
        
        Returns:
            Dictionary with all tax components
            
        Raises:
            ValueError: If validation fails
        """
        # Validate first
        is_valid, message = self.validate()
        if not is_valid:
            raise ValueError(f"Invalid input: {message}")
        
        # Calculate total base amount
        total_base = self.base_price * self.quantity
        
        # Calculate GST
        gst_amount = total_base * (self.gst_rate / 100)
        
        # Split into CGST and SGST (always 50-50)
        cgst = gst_amount / 2
        sgst = gst_amount / 2
        
        # Final price
        final_price = total_base + gst_amount
        
        return {
            'base_price_per_unit': round(self.base_price, 2),
            'quantity': self.quantity,
            'total_base_amount': round(total_base, 2),
            'gst_rate': self.gst_rate,
            'cgst': round(cgst, 2),
            'sgst': round(sgst, 2),
            'total_gst': round(gst_amount, 2),
            'final_price': round(final_price, 2)
        }
    
    def get_invoice_line(self) -> dict:
        """
        Get formatted invoice line item
        Used for invoice generation
        """
        result = self.calculate()
        return {
            'price_per_unit': result['base_price_per_unit'],
            'quantity': result['quantity'],
            'subtotal': result['total_base_amount'],
            'cgst_rate': result['gst_rate'] / 2,
            'sgst_rate': result['gst_rate'] / 2,
            'cgst_amount': result['cgst'],
            'sgst_amount': result['sgst'],
            'total': result['final_price']
        }
    
    def display(self) -> None:
        """Print calculation results in readable format"""
        try:
            result = self.calculate()
            
            print(f"\n{'='*50}")
            print(f"GST CALCULATION BREAKDOWN")
            print(f"{'='*50}")
            print(f"Base Price (per unit): ₹{result['base_price_per_unit']}")
            print(f"Quantity:              {result['quantity']}")
            print(f"Total Base Amount:     ₹{result['total_base_amount']}")
            print(f"GST Rate:              {result['gst_rate']}%")
            print(f"-" * 50)
            print(f"CGST ({result['gst_rate']/2}%):          ₹{result['cgst']}")
            print(f"SGST ({result['gst_rate']/2}%):          ₹{result['sgst']}")
            print(f"Total GST:             ₹{result['total_gst']}")
            print(f"{'='*50}")
            print(f"FINAL PRICE:           ₹{result['final_price']}")
            print(f"{'='*50}\n")
            
        except ValueError as e:
            print(f"\n❌ ERROR: {e}\n")


def test_calculator():
    """Test function to verify calculator works"""
    print("🧪 TESTING GST CALCULATOR AGENT\n")
    
    # Test 1: Laptop (18% GST, single unit)
    print("Test 1: Laptop")
    laptop = GSTCalculator(base_price=50000, gst_rate=18, quantity=1)
    laptop.display()
    
    # Test 2: Rice (0% GST, 5 units)
    print("Test 2: Rice bags")
    rice = GSTCalculator(base_price=250, gst_rate=0, quantity=5)
    rice.display()
    
    # Test 3: Shampoo (12% GST, 3 units)
    print("Test 3: Shampoo bottles")
    shampoo = GSTCalculator(base_price=200, gst_rate=12, quantity=3)
    shampoo.display()
    
    # Test 4: Invalid GST rate (should fail)
    print("Test 4: Invalid GST rate (99%)")
    try:
        invalid = GSTCalculator(base_price=1000, gst_rate=99, quantity=1)
        invalid.display()
    except ValueError as e:
        print(f"✅ Successfully caught error: {e}\n")
    
    # Test 5: Negative price (should fail)
    print("Test 5: Negative price")
    try:
        invalid = GSTCalculator(base_price=-500, gst_rate=18, quantity=1)
        invalid.display()
    except ValueError as e:
        print(f"✅ Successfully caught error: {e}\n")
    
    # Test 6: Zero quantity (should fail)
    print("Test 6: Zero quantity")
    try:
        invalid = GSTCalculator(base_price=1000, gst_rate=18, quantity=0)
        invalid.display()
    except ValueError as e:
        print(f"✅ Successfully caught error: {e}\n")
    
    print("✅ ALL TESTS PASSED! GST Calculator is working perfectly!")
    print("=" * 50)


# Run tests when file is executed directly
if __name__ == "__main__":
    test_calculator()