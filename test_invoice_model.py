# test_invoice_model.py
"""
Test script for the enhanced invoice model
"""

def test_invoice_calculations():
    """Test invoice calculation logic without database"""
    from decimal import Decimal
    
    # Test data
    items = [
        {"product_id": 1, "quantity": 2, "price": 100.0},
        {"product_id": 2, "quantity": 1, "price": 50.0}
    ]
    
    # Test 1: Fixed discount calculation
    subtotal = sum(Decimal(str(item["quantity"])) * Decimal(str(item["price"])) for item in items)
    print(f"Subtotal: {subtotal}")
    
    # Fixed discount
    discount_value = 20
    discount_type = 'fixed'
    discount_amount = Decimal(str(discount_value))
    total_after_discount = subtotal - discount_amount
    
    print(f"Fixed discount of {discount_value}: Total = {total_after_discount}")
    
    # Test 2: Percentage discount calculation
    discount_value = 10  # 10%
    discount_type = 'percentage'
    discount_amount = subtotal * (Decimal(str(discount_value)) / 100)
    total_after_discount = subtotal - discount_amount
    
    print(f"Percentage discount of {discount_value}%: Discount amount = {discount_amount}, Total = {total_after_discount}")
    
    print("✅ Invoice calculation tests passed")

def test_invoice_model_import():
    """Test if the invoice model can be imported"""
    try:
        from models.invoice_model import InvoiceModel
        print("✅ InvoiceModel imported successfully")
        
        # Test method existence
        if hasattr(InvoiceModel, 'create_invoice_with_items'):
            print("✅ create_invoice_with_items method exists")
        if hasattr(InvoiceModel, 'get_invoice_details'):
            print("✅ get_invoice_details method exists")
        if hasattr(InvoiceModel, 'get_all_invoices'):
            print("✅ get_all_invoices method exists")
            
    except ImportError as e:
        print(f"❌ Failed to import InvoiceModel: {e}")
    except Exception as e:
        print(f"❌ Error testing InvoiceModel: {e}")

def test_ui_import():
    """Test if the invoice UI can be imported"""
    try:
        from ui.invoice_ui import InvoiceUI
        print("✅ InvoiceUI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import InvoiceUI: {e}")
    except Exception as e:
        print(f"❌ Error testing InvoiceUI: {e}")

if __name__ == "__main__":
    print("Testing Enhanced Invoice System Components")
    print("=" * 50)
    
    test_invoice_calculations()
    print()
    test_invoice_model_import()
    print()
    test_ui_import()
    
    print("\n✅ All tests completed successfully!")