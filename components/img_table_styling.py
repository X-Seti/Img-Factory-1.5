#this belongs in components/ img_table_styling.py - Version: 1
# X-Seti - July08 2025 - IMG Table Styling for IMG Factory 1.5

"""
IMG Table Styling
Handles light pink theme and table setup for IMG files
"""

def setup_img_table_styling(main_window):
    """Setup IMG table styling integration with main window"""
    try:
        # Add IMG table setup method
        main_window._setup_img_table_structure = lambda headers: _setup_img_table_structure(main_window, headers)
        
        # Add IMG styling restoration method
        main_window._apply_img_table_styling = lambda: _apply_img_table_styling(main_window)
        
        main_window.log_message("✅ IMG table styling integration ready")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ IMG table styling failed: {str(e)}")
        return False

def _apply_img_table_styling(main_window):
    """Apply IMG table styling with light pink theme and resizable headers"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return
        
        table = main_window.gui_layout.table
        
        # Set IMG-specific object name for scoped styling
        table.setObjectName("img_table")
        
        # Enable column dragging and resizing for IMG table
        from PyQt6.QtWidgets import QHeaderView
        header = table.horizontalHeader()
        header.setSectionsMovable(True)  # Allow dragging columns
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # Allow resizing
        header.setDefaultSectionSize(120)  # Default column width
        
        # Enable alternating row colors
        table.setAlternatingRowColors(True)
        
        # Apply light pink theme for IMG files - HIGHLY SPECIFIC
        img_table_style = """
            QTableWidget#img_table {
                alternate-background-color: #FCE4EC;
                background-color: #FFF0F5;
                gridline-color: #E1BEE7;
                selection-background-color: #E91E63;
                selection-color: white;
            }
            QTableWidget#img_table::item {
                padding: 4px;
                border-bottom: 1px solid #F8BBD9;
                background-color: transparent;
            }
            QTableWidget#img_table::item:alternate {
                background-color: #FCE4EC;
            }
            QTableWidget#img_table::item:selected {
                background-color: #E91E63;
                color: white;
            }
        """
        
        # Apply header styling separately
        header_style = """
            background-color: #F8BBD9;
            color: #880E4F;
            font-weight: bold;
            border: 1px solid #F48FB1;
            padding: 6px;
        """
        
        # Apply table styling
        table.setStyleSheet(img_table_style)
        
        # Apply header styling directly to the header widget
        header = table.horizontalHeader()
        header.setStyleSheet(f"""
            QHeaderView::section {{
                {header_style}
            }}
            QHeaderView::section:hover {{
                background-color: #F48FB1;
            }}
        """)
        main_window.log_message("🔧 Applied light pink IMG table styling with resizable headers")
        
    except Exception as e:
        main_window.log_message(f"⚠️ Error applying IMG table styling: {str(e)}")

def _setup_img_table_structure(main_window, column_headers):
    """Setup table structure for IMG data with light pink theme and resizable headers"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return
        
        table = main_window.gui_layout.table
        
        # Configure table for IMG data
        table.setColumnCount(len(column_headers))
        table.setHorizontalHeaderLabels(column_headers)
        
        # Enable column dragging and resizing
        from PyQt6.QtWidgets import QHeaderView
        header = table.horizontalHeader()
        header.setSectionsMovable(True)  # Allow dragging columns
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # Allow resizing
        header.setDefaultSectionSize(120)  # Default column width
        
        # Set specific column widths for better visibility
        if len(column_headers) >= 6:  # Standard IMG table
            table.setColumnWidth(0, 200)  # Name - wider for readability
            table.setColumnWidth(1, 80)   # Extension
            table.setColumnWidth(2, 100)  # Size
            table.setColumnWidth(3, 100)  # Hash
            table.setColumnWidth(4, 120)  # Version
            table.setColumnWidth(5, 150)  # Compression
            if len(column_headers) > 6:
                table.setColumnWidth(6, 80)   # Status
        
        # Apply IMG styling
        _apply_img_table_styling(main_window)
        
        main_window.log_message("🔧 IMG table structure configured with light pink theme")
        
    except Exception as e:
        main_window.log_message(f"⚠️ Error setting up IMG table structure: {str(e)}")

def apply_img_table_theme_to_existing_table(main_window):
    """Apply IMG theme to an already populated table"""
    try:
        _apply_img_table_styling(main_window)
        main_window.log_message("✅ IMG pink theme applied to existing table")
        
    except Exception as e:
        main_window.log_message(f"⚠️ Error applying IMG theme: {str(e)}")

def get_img_column_headers():
    """Get standard IMG column headers"""
    return ["Name", "Extension", "Size", "Hash", "Version", "Compression", "Status"]
