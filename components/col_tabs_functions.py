#this belongs in components/ col_tabs_function.py - Version: 3
# X-Seti - July08 2025 - COL Tabs Integration for IMG Factory 1.5

"""
COL Tabs Integration - CLEAN VERSION
Handles tab creation, management and display for COL files
Uses enhanced display and parser only
"""

import os
from PyQt6.QtWidgets import QTableWidgetItem

def reset_table_styling(main_window):
    """Completely reset table styling to default"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return
        
        table = main_window.gui_layout.table
        header = table.horizontalHeader()
        
        # Clear all styling
        table.setStyleSheet("")
        header.setStyleSheet("")
        table.setObjectName("")
        
        # Reset to basic alternating colors
        table.setAlternatingRowColors(True)
        
        main_window.log_message("🔧 Table styling completely reset")
        
    except Exception as e:
        main_window.log_message(f"⚠️ Error resetting table styling: {str(e)}")

def setup_col_tab_integration(main_window):
    """Setup COL tab integration with main window"""
    try:
        # Add COL loading method to main window
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)
        
        # Add styling reset method
        main_window._reset_table_styling = lambda: reset_table_styling(main_window)
        
        main_window.log_message("✅ COL tab integration ready")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ COL tab integration failed: {str(e)}")
        return False

def load_col_file_safely(main_window, file_path):
    """Load COL file safely with proper tab management"""
    try:
        # Validate file
        if not _validate_col_file(main_window, file_path):
            return False
        
        # Setup tab
        tab_index = _setup_col_tab(main_window, file_path)
        if tab_index is None:
            return False
        
        # Load COL file
        col_file = _load_col_file(main_window, file_path)
        if col_file is None:
            return False
        
        # Setup table structure for COL data
        _setup_col_table_structure(main_window)
        
        # Populate table with enhanced COL data
        _populate_col_table_enhanced(main_window, col_file)
        
        # Update main window state
        main_window.current_col = col_file
        main_window.open_files[tab_index]['file_object'] = col_file
        
        # Update info bar with enhanced data
        _update_col_info_bar_enhanced(main_window, col_file, file_path)
        
        main_window.log_message(f"✅ COL file loaded: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return False

def _populate_col_table_enhanced(main_window, col_file):
    """Populate table using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager
        
        display_manager = COLDisplayManager(main_window)
        display_manager.populate_col_table(col_file)
        main_window.log_message("✅ Enhanced COL table populated")
        
    except Exception as e:
        main_window.log_message(f"❌ Enhanced table population failed: {str(e)}")
        raise

def _update_col_info_bar_enhanced(main_window, col_file, file_path):
    """Update info bar using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager
        
        display_manager = COLDisplayManager(main_window)
        display_manager.update_col_info_bar(col_file, file_path)
        main_window.log_message("✅ Enhanced info bar updated")
        
    except Exception as e:
        main_window.log_message(f"❌ Enhanced info bar update failed: {str(e)}")
        raise

def _validate_col_file(main_window, file_path):
    """Validate COL file before loading"""
    if not os.path.exists(file_path):
        main_window.log_message(f"❌ COL file not found: {file_path}")
        return False
    
    if not os.access(file_path, os.R_OK):
        main_window.log_message(f"❌ Cannot read COL file: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    if file_size < 32:
        main_window.log_message(f"❌ COL file too small ({file_size} bytes)")
        return False
    
    return True

def _setup_col_tab(main_window, file_path):
    """Setup or reuse tab for COL file"""
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        
        # Check if current tab is empty
        if not hasattr(main_window, 'open_files') or current_index not in main_window.open_files:
            main_window.log_message("Using current tab for COL file")
        else:
            main_window.log_message("Creating new tab for COL file")
            if hasattr(main_window, 'close_manager'):
                main_window.close_manager.create_new_tab()
                current_index = main_window.main_tab_widget.currentIndex()
            else:
                main_window.log_message("⚠️ Close manager not available")
                return None
        
        # Setup tab info
        file_name = os.path.basename(file_path)
        file_name_clean = file_name[:-4] if file_name.lower().endswith('.col') else file_name
        tab_name = f"🛡️ {file_name_clean}"
        
        # Store tab info
        if not hasattr(main_window, 'open_files'):
            main_window.open_files = {}
        
        main_window.open_files[current_index] = {
            'type': 'COL',
            'file_path': file_path,
            'file_object': None,
            'tab_name': tab_name
        }
        
        # Update tab name
        main_window.main_tab_widget.setTabText(current_index, tab_name)
        
        return current_index
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
        return None

def _load_col_file(main_window, file_path):
    """Load COL file object"""
    try:
        from components.col_core_classes import COLFile
        
        main_window.log_message("📖 Loading COL file data...")
        col_file = COLFile(file_path)
        
        if not col_file.load():
            error_details = getattr(col_file, 'load_error', 'Unknown loading error')
            main_window.log_message(f"❌ Failed to load COL file: {error_details}")
            return None
        
        return col_file
        
    except ImportError as e:
        main_window.log_message(f"❌ COL core classes not available: {str(e)}")
        return None
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return None

def _setup_col_table_structure(main_window):
    """Setup table structure for COL data display with enhanced usability"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return
        
        table = main_window.gui_layout.table
        
        # Configure table for COL data (7 columns)
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
        ])
        
        # Enable column dragging and resizing
        from PyQt6.QtWidgets import QHeaderView
        header = table.horizontalHeader()
        header.setSectionsMovable(True)  # Allow dragging columns
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # Allow resizing
        header.setDefaultSectionSize(120)  # Default column width
        
        # Set specific column widths for better visibility
        table.setColumnWidth(0, 150)  # Model name - wider for readability
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 100)  # Size
        table.setColumnWidth(3, 80)   # Surfaces
        table.setColumnWidth(4, 80)   # Vertices
        table.setColumnWidth(5, 200)  # Collision - wider for collision types
        table.setColumnWidth(6, 80)   # Status
        
        # Enable alternating row colors with light blue theme
        table.setAlternatingRowColors(True)
        
        # Set object name for specific styling
        table.setObjectName("col_table")
        
        # Apply COL-specific styling ONLY to this table
        col_table_style = """
            QTableWidget#col_table {
                alternate-background-color: #E3F2FD;
                background-color: #F5F5F5;
                gridline-color: #CCCCCC;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            QTableWidget#col_table::item {
                padding: 4px;
                border-bottom: 1px solid #E0E0E0;
                background-color: transparent;
            }
            QTableWidget#col_table::item:alternate {
                background-color: #E3F2FD;
            }
            QTableWidget#col_table::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """
        
        # Apply header styling separately to avoid affecting other headers
        header_style = """
            background-color: #BBDEFB;
            color: #1976D2;
            font-weight: bold;
            border: 1px solid #90CAF9;
            padding: 6px;
        """
        
        # Apply table styling
        table.setStyleSheet(col_table_style)
        
        # Apply header styling directly to the header widget
        header = table.horizontalHeader()
        header.setStyleSheet(f"""
            QHeaderView::section {{
                {header_style}
            }}
            QHeaderView::section:hover {{
                background-color: #90CAF9;
            }}
        """)
        
        # Clear existing data
        table.setRowCount(0)
        
        main_window.log_message("🔧 Table structure configured for COL data with scoped styling")
        
    except Exception as e:
        main_window.log_message(f"⚠️ Error setting up table structure: {str(e)}")
