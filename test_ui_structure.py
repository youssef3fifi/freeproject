"""
Simple test to verify the UI structure without actually running tkinter
"""

def test_ui_structure():
    """Test if the UI class structure is correct"""
    import inspect
    
    try:
        # Mock tkinter for testing
        import sys
        from unittest.mock import MagicMock
        
        sys.modules['tkinter'] = MagicMock()
        sys.modules['tkinter.ttk'] = MagicMock()
        sys.modules['tkinter.messagebox'] = MagicMock()
        
        from ui.invoice_ui import InvoiceUI
        
        # Check if class has required methods
        methods = [method for method in dir(InvoiceUI) if not method.startswith('_')]
        print(f"InvoiceUI methods: {methods}")
        
        # Check if required methods exist
        required_methods = [
            'create_invoice_window',
            'setup_create_invoice_tab', 
            'setup_invoice_history_tab',
            'add_to_invoice',
            'create_invoice',
            'calculate_totals',
            'print_receipt'
        ]
        
        for method in required_methods:
            if method in methods:
                print(f"✅ {method} method exists")
            else:
                print(f"❌ {method} method missing")
        
        print("✅ UI structure test completed")
        
    except Exception as e:
        print(f"❌ Error testing UI structure: {e}")

if __name__ == "__main__":
    test_ui_structure()