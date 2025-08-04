# Inventory Management System with Enhanced Invoice System

A comprehensive inventory management application with a professional invoice system built with Python and Tkinter.

## ✨ Recent Enhancements

The application has been significantly enhanced with a robust invoice system that addresses previous limitations and provides a professional invoicing experience.

### 🆕 New Features

- **Enhanced Invoice Model**: Proper transaction handling, customer information, dual discount types
- **Dedicated Invoice UI**: Tab-based interface with real-time calculations and receipt generation
- **Updated Dashboard**: Organized interface with statistics and improved navigation
- **Receipt Generation**: Automatic receipt creation and saving
- **Invoice History**: Browse and search past invoices with detailed views
- **Error Handling**: Comprehensive validation and error handling throughout

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- MySQL Server
- Required Python packages:
  ```bash
  pip install mysql-connector-python
  ```

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd freeproject
   ```

2. Install dependencies:
   ```bash
   pip install mysql-connector-python
   ```

3. Set up the database:
   - Create a MySQL database named `sharp_db`
   - Import the database schema from `sql/sharp_sb.sql`
   - Update database credentials in `database/db_connection.py`

4. Run the application:
   ```bash
   python main.py
   ```

### Default Login Credentials

- **Admin**: username: `admin`, password: `1`
- **Worker**: username: `worker`, password: `2`

## 📋 Features

### Core Functionality
- **User Authentication**: Role-based access (Admin/Worker)
- **Product Management**: Add, view, and manage inventory
- **Invoice Creation**: Professional invoicing with customer information
- **Stock Management**: Automatic inventory updates
- **Receipt Generation**: Formatted receipts saved as text files

### Enhanced Invoice System
- **Customer Information**: Store customer name and phone number
- **Dual Discount Types**: Fixed amount or percentage-based discounts
- **Real-time Calculations**: Live updates of totals and discounts
- **Stock Validation**: Prevents overselling with clear error messages
- **Transaction Safety**: Database rollback on errors
- **Invoice History**: Browse, search, and view past invoices
- **Receipt Printing**: Generate and save professional receipts

### Dashboard Features
- **Inventory Overview**: Complete product listing with statistics
- **Real-time Statistics**: Total products, stock value, revenue tracking
- **Admin Tools**: Product management for administrators
- **Navigation**: Easy access to invoice system and other features

## 🖥️ User Interface

### Main Dashboard
- **Inventory Overview Tab**: Product management and statistics
- **Quick Sale Tab**: Legacy invoice functionality
- **Invoice System Button**: Access to enhanced invoice features

### Invoice System
- **Create Invoice Tab**: 
  - Customer information input
  - Enhanced product selection
  - Real-time discount and total calculations
  - Receipt generation
- **Invoice History Tab**:
  - Browse all past invoices
  - Search and filter functionality
  - Detailed invoice views
  - Receipt regeneration

## 📁 Project Structure

```
├── main.py                   # Application entry point
├── models/
│   ├── invoice_model.py      # Enhanced invoice model
│   ├── product_model.py      # Product management
│   └── user_model.py         # User authentication
├── ui/
│   ├── login_ui.py          # Login interface
│   ├── new_windo.py         # Main dashboard
│   └── invoice_ui.py        # Enhanced invoice interface
├── database/
│   ├── db_connection.py     # Database connection
│   └── schema_update.py     # Optional schema enhancements
├── sql/
│   └── sharp_sb.sql         # Database schema
└── receipts/                # Generated receipts directory
```

## 🔧 Database Schema

### Core Tables
- **users**: User authentication and roles
- **products**: Product inventory and pricing
- **invoices**: Invoice headers with customer info
- **invoice_items**: Individual invoice line items

### Enhanced Fields (Optional)
The system supports extended invoice fields:
- `customer_name`: Customer name
- `customer_phone`: Customer phone number
- `discount_type`: Discount type (fixed/percentage)
- `subtotal`: Subtotal before discount

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Test invoice calculations
python test_invoice_model.py

# Test UI structure
python test_ui_structure.py

# Run comprehensive demo
python demo_invoice_system.py
```

## 📖 Documentation

Detailed documentation is available in:
- `INVOICE_SYSTEM_DOCUMENTATION.md`: Comprehensive feature documentation
- `demo_invoice_system.py`: Interactive feature demonstration

## 🔄 Migration and Compatibility

The enhanced system is designed for seamless integration:
- **Backward Compatibility**: All existing functionality preserved
- **Database Flexibility**: Works with both basic and enhanced schemas
- **Legacy Support**: Original quick sale functionality remains available
- **No Breaking Changes**: Existing code continues to work

## 🛠️ Development

### Adding New Features
The modular design makes it easy to extend:
- Models: Add new data models in the `models/` directory
- UI Components: Create new interfaces in the `ui/` directory
- Database: Extend schema using migration scripts

### Error Handling
The system includes comprehensive error handling:
- Input validation with user-friendly messages
- Database transaction safety with rollback
- Stock validation to prevent overselling
- Graceful handling of connection issues

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

## 📧 Support

For support and questions, please open an issue in the repository.