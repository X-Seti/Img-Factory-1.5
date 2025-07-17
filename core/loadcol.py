#this belongs in core/ loadcol.py - Version: 2
# X-Seti - July17 2025 - Img Factory 1.5 - Unified COL Loading System

"""
Complete COL Loading System
All COL loading functions consolidated into one file to eliminate conflicts
"""

import os
import struct
from typing import Optional, Any

## Methods list -
# load_col_file_safely
# validate_col_file
# setup_col_tab
# load_col_file_object
# populate_col_table
# update_col_info_bar
# validate_col_file_structure
# setup_col_table_structure


def load_col_file_safely(main_window, file_path: str) -> bool: #vers 1
    """Load COL file safely with proper validation and tab management"""
    try:
        main_window.log_message(f"🔧 Loading COL: {os.path.basename(file_path)}")
        
        # Step 1: Validate file
        if not validate_col_file(main_window, file_path):
            return False
        
        # Step 2: Setup tab
        tab_index = setup_col_tab(main_window, file_path)
        if tab_index is None:
            return False
        
        # Step 3: Load COL file object
        col_file = load_col_file_object(main_window, file_path)
        if col_file is None:
            return False
        
        # Step 4: Setup table structure
        setup_col_table_structure(main_window)
        
        # Step 5: Populate table
        populate_col_table(main_window, col_file)
        
        # Step 6: Update main window state
        main_window.current_col = col_file
        main_window.open_files[tab_index]['file_object'] = col_file
        
        # Step 7: Update info bar
        update_col_info_bar(main_window, col_file, file_path)
        
        main_window.log_message(f"✅ COL file loaded: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return False


def validate_col_file(main_window, file_path: str) -> bool: #vers 1
    """Validate COL file before loading"""
    try:
        # Check file exists
        if not os.path.exists(file_path):
            main_window.log_message(f"❌ COL file not found: {file_path}")
            return False
        
        # Check file is readable
        if not os.access(file_path, os.R_OK):
            main_window.log_message(f"❌ Cannot read COL file: {file_path}")
            return False
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size < 32:
            main_window.log_message(f"❌ COL file too small ({file_size} bytes)")
            return False
        
        # Check file structure
        is_valid, message = validate_col_file_structure(file_path)
        if not is_valid:
            main_window.log_message(f"❌ COL validation failed: {message}")
            return False
        
        main_window.log_message(f"✅ COL validation passed: {message}")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ COL validation error: {str(e)}")
        return False


def validate_col_file_structure(file_path: str) -> tuple[bool, str]: #vers 1
    """Validate COL file structure and format"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8)
            
        if len(header) < 8:
            return False, "File too small for COL header"
        
        # Check for COL signatures
        signature = header[:4]
        if signature == b'COLL':
            return True, "COL1 format detected"
        elif signature == b'COL\x02':
            return True, "COL2 format detected"
        elif signature == b'COL\x03':
            return True, "COL3 format detected"
        elif signature == b'COL\x04':
            return True, "COL4 format detected"
        else:
            # Try numeric header
            try:
                version = struct.unpack('<I', signature)[0]
                if 1 <= version <= 4:
                    return True, f"COL version {version} detected"
            except:
                pass
            
            return False, f"Unknown COL format signature: {signature.hex()}"
            
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def setup_col_tab(main_window, file_path: str) -> Optional[int]: #vers 1
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
        
        main_window.log_message(f"✅ COL tab setup: {tab_name}")
        return current_index
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
        return None


def load_col_file_object(main_window, file_path: str) -> Optional[Any]: #vers 1
    """Load COL file object from disk"""
    try:
        from components.col_core_classes import COLFile
        
        main_window.log_message("📖 Loading COL file data...")
        col_file = COLFile(file_path)
        
        if not col_file.load():
            error_details = getattr(col_file, 'load_error', 'Unknown loading error')
            main_window.log_message(f"❌ Failed to load COL file: {error_details}")
            return None
        
        model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
        main_window.log_message(f"✅ COL file loaded: {model_count} models")
        return col_file
        
    except ImportError as e:
        main_window.log_message(f"❌ COL core classes not available: {str(e)}")
        return None
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return None


def setup_col_table_structure(main_window) -> None: #vers 1
    """Setup table structure for COL data display"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return
        
        table = main_window.gui_layout.table
        
        # Configure table for COL data (6 columns)
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Model", "Name", "Spheres", "Boxes", "Triangles", "Size"
        ])
        
        # Set column widths
        table.setColumnWidth(0, 60)   # Model
        table.setColumnWidth(1, 200)  # Name
        table.setColumnWidth(2, 80)   # Spheres
        table.setColumnWidth(3, 80)   # Boxes
        table.setColumnWidth(4, 100)  # Triangles
        table.setColumnWidth(5, 80)   # Size
        
        main_window.log_message("✅ COL table structure setup")
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL table: {str(e)}")


def populate_col_table(main_window, col_file: Any) -> None: #vers 1
    """Populate table with COL data"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return
        
        table = main_window.gui_layout.table
        
        if not hasattr(col_file, 'models') or not col_file.models:
            main_window.log_message("⚠️ No COL models to display")
            table.setRowCount(0)
            return
        
        # Set row count
        table.setRowCount(len(col_file.models))
        
        # Populate rows
        for i, model in enumerate(col_file.models):
            try:
                # Model index
                table.setItem(i, 0, create_table_item(f"#{i+1}"))
                
                # Model name
                model_name = getattr(model, 'name', f'Model_{i+1}')
                table.setItem(i, 1, create_table_item(model_name))
                
                # Collision data counts
                sphere_count = len(getattr(model, 'spheres', []))
                box_count = len(getattr(model, 'boxes', []))
                triangle_count = len(getattr(model, 'faces', []))
                
                table.setItem(i, 2, create_table_item(str(sphere_count)))
                table.setItem(i, 3, create_table_item(str(box_count)))
                table.setItem(i, 4, create_table_item(str(triangle_count)))
                
                # Size estimate
                size_estimate = (sphere_count * 20) + (box_count * 48) + (triangle_count * 36)
                table.setItem(i, 5, create_table_item(f"{size_estimate}b"))
                
            except Exception as e:
                main_window.log_message(f"⚠️ Error populating row {i}: {str(e)}")
                # Fill with placeholder data
                table.setItem(i, 0, create_table_item(f"#{i+1}"))
                table.setItem(i, 1, create_table_item("Error"))
                table.setItem(i, 2, create_table_item("?"))
                table.setItem(i, 3, create_table_item("?"))
                table.setItem(i, 4, create_table_item("?"))
                table.setItem(i, 5, create_table_item("?"))
        
        main_window.log_message(f"✅ COL table populated: {len(col_file.models)} models")
        
    except Exception as e:
        main_window.log_message(f"❌ Error populating COL table: {str(e)}")


def create_table_item(text: str):
    """Create table item with proper formatting"""
    try:
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item
    except ImportError:
        # Fallback for missing PyQt6
        return None


def update_col_info_bar(main_window, col_file: Any, file_path: str) -> None: #vers 1
    """Update info bar with COL file information"""
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
        
        # Update window title
        main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")
        
        # Update info labels if they exist
        if hasattr(main_window, 'file_path_label'):
            main_window.file_path_label.setText(file_path)
        
        if hasattr(main_window, 'version_label'):
            main_window.version_label.setText("COL")
        
        if hasattr(main_window, 'entry_count_label'):
            main_window.entry_count_label.setText(str(model_count))
        
        # Update status bar
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(-1, f"COL: {model_count} models ({file_size} bytes)")
        
        main_window.log_message(f"✅ COL info bar updated: {file_name}")
        
    except Exception as e:
        main_window.log_message(f"❌ Error updating COL info bar: {str(e)}")


# Export functions
__all__ = [
    'load_col_file_safely',
    'validate_col_file',
    'setup_col_tab',
    'load_col_file_object',
    'populate_col_table',
    'update_col_info_bar',
    'validate_col_file_structure',
    'setup_col_table_structure'
]