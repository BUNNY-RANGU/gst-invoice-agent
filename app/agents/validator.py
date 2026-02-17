"""
Invoice Validator Agent
Validates all input data before processing
Author: Bunny Rangu
Day: 2/30
"""

import re
from datetime import datetime
from typing import Tuple, List, Dict


class InvoiceValidator:
    """
    Validates invoice data before processing
    Catches errors early - prevents bad data from entering system
    """
    
    # Valid GST rates
    VALID_GST_RATES = [0, 5, 12, 18, 28]
    
    # Valid GST number format (15 characters)
    GST_PATTERN = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    
    # Phone number pattern (10 digits)
    PHONE_PATTERN = r'^[6-9]\d{9}$'
    
    # Email pattern
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    @staticmethod
    def validate_customer_name(name: str) -> Tuple[bool, str]:
        """
        Validate customer name
        
        Args:
            name: Customer name string
            
        Returns:
            (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Customer name cannot be empty"
        
        if len(name.strip()) < 2:
            return False, "Customer name must be at least 2 characters"
        
        if len(name) > 100:
            return False, "Customer name too long (max 100 characters)"
        
        return True, "Valid"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate Indian phone number
        
        Args:
            phone: Phone number string
            
        Returns:
            (is_valid, error_message)
        """
        # Remove spaces and dashes
        phone_clean = phone.replace(" ", "").replace("-", "")
        
        if not re.match(InvoiceValidator.PHONE_PATTERN, phone_clean):
            return False, "Invalid phone number (must be 10 digits starting with 6-9)"
        
        return True, "Valid"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email address
        
        Args:
            email: Email string
            
        Returns:
            (is_valid, error_message)
        """
        if not email or not email.strip():
            return False, "Email cannot be empty"
        
        if not re.match(InvoiceValidator.EMAIL_PATTERN, email):
            return False, "Invalid email format"
        
        return True, "Valid"
    
    @staticmethod
    def validate_gst_number(gst_number: str) -> Tuple[bool, str]:
        """
        Validate GST number format
        
        Args:
            gst_number: GST number string
            
        Returns:
            (is_valid, error_message)
        """
        if not gst_number:
            return True, "Valid"  # GST number is optional
        
        if not re.match(InvoiceValidator.GST_PATTERN, gst_number):
            return False, "Invalid GST number format (must be 15 characters)"
        
        return True, "Valid"
    
    @staticmethod
    def validate_item_name(name: str) -> Tuple[bool, str]:
        """
        Validate item name
        
        Args:
            name: Item name string
            
        Returns:
            (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Item name cannot be empty"
        
        if len(name.strip()) < 2:
            return False, "Item name must be at least 2 characters"
        
        if len(name) > 200:
            return False, "Item name too long (max 200 characters)"
        
        return True, "Valid"
    
    @staticmethod
    def validate_price(price: float) -> Tuple[bool, str]:
        """
        Validate price
        
        Args:
            price: Price value
            
        Returns:
            (is_valid, error_message)
        """
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            return False, "Price must be a number"
        
        if price_float < 0:
            return False, "Price cannot be negative"
        
        if price_float > 10000000:  # 1 crore limit
            return False, "Price too high (max ₹1,00,00,000)"
        
        return True, "Valid"
    
    @staticmethod
    def validate_quantity(quantity: int) -> Tuple[bool, str]:
        """
        Validate quantity
        
        Args:
            quantity: Quantity value
            
        Returns:
            (is_valid, error_message)
        """
        try:
            qty_int = int(quantity)
        except (ValueError, TypeError):
            return False, "Quantity must be a whole number"
        
        if qty_int <= 0:
            return False, "Quantity must be positive"
        
        if qty_int > 100000:
            return False, "Quantity too high (max 1,00,000)"
        
        return True, "Valid"
    
    @staticmethod
    def validate_gst_rate(rate: int) -> Tuple[bool, str]:
        """
        Validate GST rate
        
        Args:
            rate: GST rate percentage
            
        Returns:
            (is_valid, error_message)
        """
        if rate not in InvoiceValidator.VALID_GST_RATES:
            return False, f"GST rate must be one of {InvoiceValidator.VALID_GST_RATES}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, str]:
        """
        Validate date string
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            (is_valid, error_message)
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Check if date is not in future
            if date_obj > datetime.now():
                return False, "Invoice date cannot be in the future"
            
            # Check if date is not too old (more than 3 years)
            years_diff = (datetime.now() - date_obj).days / 365
            if years_diff > 3:
                return False, "Invoice date too old (max 3 years ago)"
            
            return True, "Valid"
            
        except ValueError:
            return False, "Invalid date format (use YYYY-MM-DD)"
    
    @classmethod
    def validate_invoice_item(cls, item: Dict) -> Tuple[bool, str]:
        """
        Validate complete invoice item
        
        Args:
            item: Dictionary with item details
            
        Returns:
            (is_valid, error_message)
        """
        # Validate item name
        is_valid, msg = cls.validate_item_name(item.get('name', ''))
        if not is_valid:
            return False, f"Item name error: {msg}"
        
        # Validate price
        is_valid, msg = cls.validate_price(item.get('price', 0))
        if not is_valid:
            return False, f"Price error: {msg}"
        
        # Validate quantity
        is_valid, msg = cls.validate_quantity(item.get('quantity', 0))
        if not is_valid:
            return False, f"Quantity error: {msg}"
        
        # Validate GST rate
        is_valid, msg = cls.validate_gst_rate(item.get('gst_rate', 0))
        if not is_valid:
            return False, f"GST rate error: {msg}"
        
        return True, "Valid"
    
    @classmethod
    def validate_customer_details(cls, customer: Dict) -> Tuple[bool, str]:
        """
        Validate customer details
        
        Args:
            customer: Dictionary with customer details
            
        Returns:
            (is_valid, error_message)
        """
        # Validate name
        is_valid, msg = cls.validate_customer_name(customer.get('name', ''))
        if not is_valid:
            return False, msg
        
        # Validate phone
        is_valid, msg = cls.validate_phone(customer.get('phone', ''))
        if not is_valid:
            return False, msg
        
        # Validate email (if provided)
        if 'email' in customer and customer['email']:
            is_valid, msg = cls.validate_email(customer['email'])
            if not is_valid:
                return False, msg
        
        # Validate GST number (if provided)
        if 'gst_number' in customer and customer['gst_number']:
            is_valid, msg = cls.validate_gst_number(customer['gst_number'])
            if not is_valid:
                return False, msg
        
        return True, "Valid"


def test_validator():
    """Test function for validator"""
    print("🧪 TESTING INVOICE VALIDATOR AGENT\n")
    
    validator = InvoiceValidator()
    
    # Test 1: Valid customer name
    print("Test 1: Valid customer name")
    is_valid, msg = validator.validate_customer_name("Rajesh Kumar")
    print(f"✅ Result: {is_valid}, Message: {msg}\n")
    
    # Test 2: Invalid customer name (too short)
    print("Test 2: Invalid customer name (too short)")
    is_valid, msg = validator.validate_customer_name("R")
    print(f"❌ Result: {is_valid}, Message: {msg}\n")
    
    # Test 3: Valid phone number
    print("Test 3: Valid phone number")
    is_valid, msg = validator.validate_phone("9876543210")
    print(f"✅ Result: {is_valid}, Message: {msg}\n")
    
    # Test 4: Invalid phone number
    print("Test 4: Invalid phone number")
    is_valid, msg = validator.validate_phone("1234567890")
    print(f"❌ Result: {is_valid}, Message: {msg}\n")
    
    # Test 5: Valid email
    print("Test 5: Valid email")
    is_valid, msg = validator.validate_email("bunny@example.com")
    print(f"✅ Result: {is_valid}, Message: {msg}\n")
    
    # Test 6: Invalid email
    print("Test 6: Invalid email")
    is_valid, msg = validator.validate_email("not-an-email")
    print(f"❌ Result: {is_valid}, Message: {msg}\n")
    
    # Test 7: Valid GST number
    print("Test 7: Valid GST number")
    is_valid, msg = validator.validate_gst_number("29ABCDE1234F1Z5")
    print(f"✅ Result: {is_valid}, Message: {msg}\n")
    
    # Test 8: Valid invoice item
    print("Test 8: Valid invoice item")
    item = {
        'name': 'Laptop',
        'price': 50000,
        'quantity': 1,
        'gst_rate': 18
    }
    is_valid, msg = validator.validate_invoice_item(item)
    print(f"✅ Result: {is_valid}, Message: {msg}\n")
    
    # Test 9: Invalid invoice item (negative price)
    print("Test 9: Invalid invoice item (negative price)")
    item = {
        'name': 'Laptop',
        'price': -50000,
        'quantity': 1,
        'gst_rate': 18
    }
    is_valid, msg = validator.validate_invoice_item(item)
    print(f"❌ Result: {is_valid}, Message: {msg}\n")
    
    # Test 10: Valid customer details
    print("Test 10: Valid customer details")
    customer = {
        'name': 'Bunny Rangu',
        'phone': '9876543210',
        'email': 'bunny@example.com',
        'gst_number': '29ABCDE1234F1Z5'
    }
    is_valid, msg = validator.validate_customer_details(customer)
    print(f"✅ Result: {is_valid}, Message: {msg}\n")
    
    print("=" * 50)
    print("✅ ALL VALIDATION TESTS COMPLETED!")
    print("=" * 50)


if __name__ == "__main__":
    test_validator()