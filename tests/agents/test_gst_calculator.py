"""
Unit tests for GST Calculator Agent
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.agents.gst_calculator import GSTCalculator
import pytest


def test_calculate_single_item_18_percent():
    """Test GST calculation with single item at 18%"""
    calc = GSTCalculator()
    
    items = [
        {
            'name': 'Laptop',
            'price': 10000,
            'quantity': 1,
            'gst_rate': 18
        }
    ]
    
    result = calc.calculate(items)
    
    assert result['subtotal'] == 10000
    assert result['total_gst'] == 1800
    assert result['grand_total'] == 11800


def test_calculate_multiple_items():
    """Test calculation with multiple items"""
    calc = GSTCalculator()
    
    items = [
        {'name': 'Laptop', 'price': 50000, 'quantity': 1, 'gst_rate': 18},
        {'name': 'Mouse', 'price': 500, 'quantity': 2, 'gst_rate': 18}
    ]
    
    result = calc.calculate(items)
    
    assert result['subtotal'] == 51000
    assert result['total_items'] == 2
    assert result['total_quantity'] == 3


def test_calculate_zero_gst():
    """Test calculation with 0% GST"""
    calc = GSTCalculator()
    
    items = [
        {'name': 'Book', 'price': 500, 'quantity': 1, 'gst_rate': 0}
    ]
    
    result = calc.calculate(items)
    
    assert result['subtotal'] == 500
    assert result['total_gst'] == 0
    assert result['grand_total'] == 500


def test_calculate_all_gst_rates():
    """Test all valid GST rates"""
    calc = GSTCalculator()
    
    for rate in [0, 5, 12, 18, 28]:
        items = [
            {'name': 'Test Item', 'price': 1000, 'quantity': 1, 'gst_rate': rate}
        ]
        result = calc.calculate(items)
        
        expected_gst = 1000 * rate / 100
        assert result['total_gst'] == expected_gst
        assert result['grand_total'] == 1000 + expected_gst


def test_calculate_5_percent_gst():
    """Test 5% GST calculation"""
    calc = GSTCalculator()
    
    items = [
        {'name': 'Item', 'price': 10000, 'quantity': 1, 'gst_rate': 5}
    ]
    
    result = calc.calculate(items)
    
    assert result['total_gst'] == 500
    assert result['grand_total'] == 10500


def test_calculate_12_percent_gst():
    """Test 12% GST calculation"""
    calc = GSTCalculator()
    
    items = [
        {'name': 'Item', 'price': 10000, 'quantity': 1, 'gst_rate': 12}
    ]
    
    result = calc.calculate(items)
    
    assert result['total_gst'] == 1200
    assert result['grand_total'] == 11200


def test_calculate_28_percent_gst():
    """Test 28% GST calculation"""
    calc = GSTCalculator()
    
    items = [
        {'name': 'Item', 'price': 10000, 'quantity': 1, 'gst_rate': 28}
    ]
    
    result = calc.calculate(items)
    
    assert result['total_gst'] == 2800
    assert result['grand_total'] == 12800


def test_validate_valid_items():
    """Test validation with valid items"""
    calc = GSTCalculator()
    
    items = [
        {'name': 'Laptop', 'price': 50000, 'quantity': 1, 'gst_rate': 18}
    ]
    
    result = calc.validate(items)
    
    assert result['valid'] == True


def test_validate_missing_fields():
    """Test validation with missing fields"""
    calc = GSTCalculator()
    
    items = [
        {'name': 'Laptop'}  # Missing price, quantity, gst_rate
    ]
    
    result = calc.validate(items)
    
    assert result['valid'] == False
    assert len(result['errors']) > 0


def test_valid_rates_constant():
    """Test VALID_RATES constant"""
    assert GSTCalculator.VALID_RATES == [0, 5, 12, 18, 28]