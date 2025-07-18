#this belongs in core/ loadcol.py - Version: 3
# X-Seti - July18 2025 - Img Factory 1.5 - COL Loading System Fixed

"""
COL Loading System - Fixed table structure conflicts
Ensures COL files use proper 6-column table structure
"""

import os
from typing import Optional, Any
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

## Methods list -
# load_col_file_safely
# validate_col_file
# setup_col_tab
# load_col_file_object
# populate_col_table
# update_col_info_bar
# setup_col_table_structure
# create_table_item


def load_col_file_safely(main_window, file_path: str) -> bool: #vers 3
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
        
        # Step 4: Setup table structure (6 columns for COL)
        setup_col_table_structure(main_window)
        
        # Step 5: Populate table with COL data
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


def validate_col_file(main_window, file_path: str) -> bool: #vers 3
    """Validate COL file before loading"""
    try:
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
        
    except Exception as e:
        main_window.log_message(f"❌ COL validation error: {str(e)}")
        return False


def setup_col_tab(main_window, file_path: str) -> Optional[int]: #vers 3
    """Setup or reuse tab for COL file"""
    try:
        file_name = os.path.basename(file_path)
        
        # Check if file already open
        for tab_index, file_info in main_window.open_files.items():
            if file_info.get('file_path') == file_path:
                main_window.main_tab_widget.setCurrentIndex(tab_index)
                main_window.log_message(f"📂 Switched to existing tab: {file_name}")
                return tab_index
        
        # Create new tab
        current_index = main_window.main_tab_widget.currentIndex()
        
        # Check if current tab is empty (no file loaded)
        if (current_index == 0 and 
            len(main_window.open_files) == 0 and 
            main_window.main_tab_widget.tabText(0) == "📁 No File"):
            
            # Use existing empty tab
            main_window.main_tab_widget.setTabText(0, f"📋 {file_name}")
            main_window.open_files[0] = {
                'file_path': file_path,
                'type': 'COL',
                'tab_name': f"📋 {file_name}"
            }
            return 0
        else:
            # Create new tab
            from PyQt6.QtWidgets import QWidget, QVBoxLayout
            
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add main UI to tab
            main_window.gui_layout.create_main_ui_with_splitters(tab_layout)
            
            # Add tab
            new_index = main_window.main_tab_widget.addTab(tab_widget, f"📋 {file_name}")
            main_window.main_tab_widget.setCurrentIndex(new_index)
            
            # Store file info
            main_window.open_files[new_index] = {
                'file_path': file_path,
                'type': 'COL',
                'tab_name': f"📋 {file_name}"
            }
            
            return new_index
            
    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
        return None


def load_col_file_object(main_window, file_path: str) -> Optional[Any]: #vers 3
    """Load COL file object"""
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


def setup_col_table_structure(main_window) -> bool: #vers 3
    """Setup table structure for COL data (6 columns)"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return False
        
        table = main_window.gui_layout.table
        
        # Configure table for COL data (7 columns) - match original blue table
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
        ])
        
        # Set column widths
        table.setColumnWidth(0, 120)  # Model
        table.setColumnWidth(1, 60)   # Type
        table.setColumnWidth(2, 80)   # Size
        table.setColumnWidth(3, 80)   # Surfaces
        table.setColumnWidth(4, 80)   # Vertices
        table.setColumnWidth(5, 100)  # Collision
        table.setColumnWidth(6, 80)   # Status
        
        # Configure table properties
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSortingEnabled(True)
        
        main_window.log_message("✅ COL table structure setup (7 columns)")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL table: {str(e)}")
        return False


def populate_col_table(main_window, col_file: Any) -> None: #vers 4
    """Populate table with COL data using complete parser for real collision data"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return
        
        table = main_window.gui_layout.table
        
        # Use the new complete parser to get real collision data
        try:
            from components.col_parser_rebuild import parse_col_file_complete
            
            main_window.log_message("🔧 Using complete COL parser for real collision data")
            parsed_models = parse_col_file_complete(col_file.file_path, debug=True)
            
            if not parsed_models:
                main_window.log_message("⚠️ Complete parser found no models")
                table.setRowCount(0)
                return
            
            # Set row count
            table.setRowCount(len(parsed_models))
            
            # Populate rows with real parsed collision data
            for i, model in enumerate(parsed_models):
                try:
                    stats = model.get_collision_stats()
                    
                    # Column 0: Model name
                    table.setItem(i, 0, create_table_item(model.name))
                    
                    # Column 1: Type/Version
                    table.setItem(i, 1, create_table_item(model.version))
                    
                    # Column 2: Size
                    if model.size_bytes < 1024:
                        size_text = f"{model.size_bytes} B"
                    else:
                        size_text = f"{model.size_bytes // 1024} KB"
                    table.setItem(i, 2, create_table_item(size_text))
                    
                    # Column 3: Surfaces (spheres + boxes)
                    surface_count = stats['surface_count']
                    table.setItem(i, 3, create_table_item(str(surface_count)))
                    
                    # Column 4: Vertices
                    vertex_count = stats['vertex_count']
                    table.setItem(i, 4, create_table_item(str(vertex_count)))
                    
                    # Column 5: Collision (descriptive)
                    collision_parts = []
                    if stats['sphere_count'] > 0:
                        collision_parts.append(f"Spheres({stats['sphere_count']})")
                    if stats['box_count'] > 0:
                        collision_parts.append(f"Boxes({stats['box_count']})")
                    if stats['face_count'] > 0:
                        collision_parts.append(f"Mesh({stats['face_count']})")
                    
                    collision_text = ", ".join(collision_parts) if collision_parts else "None"
                    table.setItem(i, 5, create_table_item(collision_text))
                    
                    # Column 6: Status
                    if stats['total_elements'] > 0:
                        table.setItem(i, 6, create_table_item("✓ Loaded"))
                    else:
                        table.setItem(i, 6, create_table_item("⚠ Empty"))
                    
                    main_window.log_message(f"✅ Model {i} ({model.name}): {stats}")
                    
                except Exception as e:
                    main_window.log_message(f"⚠️ Error populating row {i}: {str(e)}")
                    # Fill with error data
                    table.setItem(i, 0, create_table_item(f"model_{i}"))
                    table.setItem(i, 1, create_table_item("ERROR"))
                    table.setItem(i, 2, create_table_item("0 B"))
                    table.setItem(i, 3, create_table_item("0"))
                    table.setItem(i, 4, create_table_item("0"))
                    table.setItem(i, 5, create_table_item("Parse Error"))
                    table.setItem(i, 6, create_table_item("❌ Error"))
            
            main_window.log_message(f"✅ COL table populated with real data: {len(parsed_models)} models")
            
        except ImportError:
            main_window.log_message("❌ Complete COL parser not available, using fallback")
            # Fallback to old method
            if not hasattr(col_file, 'models') or not col_file.models:
                table.setRowCount(0)
                return
                
            table.setRowCount(len(col_file.models))
            for i, model in enumerate(col_file.models):
                table.setItem(i, 0, create_table_item(getattr(model, 'name', f'model_{i}')))
                table.setItem(i, 1, create_table_item("COL"))
                table.setItem(i, 2, create_table_item("Unknown"))
                table.setItem(i, 3, create_table_item("0"))
                table.setItem(i, 4, create_table_item("0"))
                table.setItem(i, 5, create_table_item("No Parser"))
                table.setItem(i, 6, create_table_item("⚠ Limited"))
        
    except Exception as e:
        main_window.log_message(f"❌ Error populating COL table: {str(e)}")


def create_table_item(text: str) -> QTableWidgetItem: #vers 3
    """Create table item with proper formatting"""
    item = QTableWidgetItem(str(text))
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item


def update_col_info_bar(main_window, col_file: Any, file_path: str) -> None: #vers 3
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
            size_text = f"{file_size // 1024}KB" if file_size >= 1024 else f"{file_size}B"
            main_window.gui_layout.show_progress(-1, f"COL: {model_count} models ({size_text})")
        
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
    'setup_col_table_structure',
    'create_table_item'
]