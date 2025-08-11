# Inventory Plus

## Overview
**Inventory Plus** is a corporate inventory management system built with **Python 3** and the **Django** framework.  
It allows managing products, categories, suppliers, stock levels, and generating reports, with email notifications for low stock and expiry alerts.

---

## Features

### Product Management
- Add, edit, delete products (delete is admin-only).
- View product list and details.
- Search products.
- Update stock levels and view stock status.

### Category Management
- Add, edit, delete categories.
- View category list.

### Supplier Management
- Add, edit, delete suppliers.
- View supplier list and details with linked products.

### Reports
- Generate inventory and supplier reports (HTML + PDF).

### Notifications
- Low stock alerts via email.
- Expiry date alerts via email.

### Import/Export (Bonus)
- Import products from CSV.
- Export inventory data to CSV.

---

## Requirements

### Functional
- CRUD operations for products, categories, suppliers.
- Product and supplier search.
- Stock tracking and updates.
- Report generation.
- Email notifications for low stock and expiry.
- CSV import/export (Bonus).

### Non-Functional
- Responsive design.
- User-friendly interface.
- Secure data handling.
- Error logging.

---

## User Roles

- **Admin**: Full permissions on all features.
- **Employee**: Can view/update stock, add/edit products, view reports. No delete permissions or category/supplier management.

---

## Models & Relationships
- **Product**: Belongs to one category, can be supplied by multiple suppliers.
- **Category**
- **Supplier**

---

## UML
![UML Diagram](https://drive.google.com/uc?export=view&id=1wOF3lANAC_-M0qMTaNWkTiKCuKlNI_bI)

## Wireframe  
[View Wireframe on Figma](https://www.figma.com/design/Jg45ajSPbKujU8Ipb1VBZb/Stocker?node-id=0-1&t=PBy2ZmpmXDU3ZxZ8-1)

---

## Notes
- Best practices applied.
- Pagination and clear user feedback included.
