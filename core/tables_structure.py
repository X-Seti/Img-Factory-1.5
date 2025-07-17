#this belongs in core/ tables_structure.py - Version: 2
# X-Seti - July16 2025 - IMG Factory 1.5 - Table Structure Functions

"""
Table Structure Functions
Handles table population and setup for both IMG and COL files
"""

import os
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

# Methods list.
# estimate_col_model_size_bytes
# format_file_size
# populate_col_table_img_format
# populate_col_table_enhanced
# populate_img_table
# reset_table_styling
# setup_col_table_structure


def estimate_col_model_size_bytes(model): #vers 4
    """Estimate COL model size in bytes (similar to IMG entry sizes)"""
    try:
        if not hasattr(model, 'get_stats'):
            return 1024  # Default 1KB

        stats = model.get_stats()

        # Rough estimation based on collision elements
        size = 100  # Base model overhead (header, name, etc.)
        size += stats.get('spheres', 0) * 16     # 16 bytes per sphere
        size += stats.get('boxes', 0) * 24       # 24 bytes per box
        size += stats.get('vertices', 0) * 12    # 12 bytes per vertex
        size += stats.get('faces', 0) * 8        # 8 bytes per face
        size += stats.get('face_groups', 0) * 8  # 8 bytes per face group

        # Add version-specific overhead
        if hasattr(model, 'version') and hasattr(model.version, 'value'):
            if model.version.value >= 3:
                size += stats.get('shadow_vertices', 0) * 12
                size += stats.get('shadow_faces', 0) * 8
                size += 64  # COL3+ additional headers
            elif model.version.value >= 2:
                size += 48  # COL2 headers

        return max(size, 64)  # Minimum 64 bytes

    except Exception:
        return 1024  # Default 1KB on error


def format_file_size(size_bytes): #vers 4
    """Format file size same as IMG entries"""
    try:
        # Use the same formatting as IMG entries
        try:
            from components.img_core_classes import format_file_size
            return format_file_size(size_bytes)
        except:
            pass

        # Fallback formatting (same logic as IMG)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes // 1024} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes // (1024 * 1024)} MB"
        else:
            return f"{size_bytes // (1024 * 1024 * 1024)} GB"

    except Exception:
        return f"{size_bytes} bytes"


def populate_col_table_img_format(table: QTableWidget, col_file, file_name): #vers 4
    """Populate table with COL models using same format as IMG entries"""
    # Keep the same 7-column format as IMG files
    table.setColumnCount(7)
    table.setHorizontalHeaderLabels([
        "Name", "Type", "Size", "Offset", "Version", "Compression", "Status"
    ])

    if not col_file or not hasattr(col_file, 'models') or not col_file.models:
        # Show the file itself if no models
        table.setRowCount(1)

        try:
            file_size = os.path.getsize(col_file.file_path) if col_file and hasattr(col_file, 'file_path') and col_file.file_path else 0
            size_text = format_file_size(file_size)
        except:
            size_text = "Unknown"

        items = [
            (file_name, "COL", size_text, "0x0", "Unknown", "None", "No Models")
        ]

        for row, item_data in enumerate(items):
            for col, value in enumerate(item_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, col, item)

        print(f"DEBUG: COL file loaded but no models found")
        return

    # Show individual models in IMG entry format
    models = col_file.models
    table.setRowCount(len(models))

    print(f"DEBUG: Populating table with {len(models)} COL models")

    virtual_offset = 0x0  # Virtual offset for COL models

    for row, model in enumerate(models):
        try:
            # Name - use model name or generate one
            model_name = getattr(model, 'name', f"Model_{row}") if hasattr(model, 'name') and model.name else f"Model_{row}"
            table.setItem(row, 0, QTableWidgetItem(model_name))

            # Type - just "COL" (like IMG shows "DFF", "TXD", etc.)
            table.setItem(row, 1, QTableWidgetItem("COL"))

            # Size - estimate COL model size
            try:
                model_size = estimate_col_model_size_bytes(model)
                size_text = format_file_size(model_size)
            except:
                size_text = "1 KB"
            table.setItem(row, 2, QTableWidgetItem(size_text))

            # Virtual offset (increment for each model)
            table.setItem(row, 3, QTableWidgetItem(f"0x{virtual_offset:X}"))
            virtual_offset += 1024  # Increment by 1KB for next model

            # Version - try to get COL version
            try:
                if hasattr(model, 'version') and hasattr(model.version, 'name'):
                    version_text = model.version.name
                elif hasattr(model, 'version') and hasattr(model.version, 'value'):
                    version_text = f"COL{model.version.value}"
                else:
                    version_text = "COL"
            except:
                version_text = "COL"
            table.setItem(row, 4, QTableWidgetItem(version_text))

            # Compression - COL models aren't typically compressed
            table.setItem(row, 5, QTableWidgetItem("None"))

            # Status - always Ready for COL models
            table.setItem(row, 6, QTableWidgetItem("Ready"))

            # Make all items read-only
            for col in range(7):
                item = table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        except Exception as e:
            print(f"DEBUG: Error populating COL model {row}: {str(e)}")
            # Create fallback row (same as IMG error handling)
            table.setItem(row, 0, QTableWidgetItem(f"Model_{row}"))
            table.setItem(row, 1, QTableWidgetItem("COL"))
            table.setItem(row, 2, QTableWidgetItem("0 B"))
            table.setItem(row, 3, QTableWidgetItem("0x0"))
            table.setItem(row, 4, QTableWidgetItem("Unknown"))
            table.setItem(row, 5, QTableWidgetItem("None"))
            table.setItem(row, 6, QTableWidgetItem("Error"))

    print(f"DEBUG: Table populated with {len(models)} COL models (IMG format)")


def populate_col_table_enhanced(main_window, col_file): #vers 2
    """Populate table using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager

        display_manager = COLDisplayManager(main_window)
        display_manager.populate_col_table(col_file)
        main_window.log_message("✅ Enhanced COL table populated")

    except Exception as e:
        main_window.log_message(f"❌ Enhanced table population failed: {str(e)}")
        raise


def populate_img_table(table: QTableWidget, img_file): #vers 4
    """Populate table with IMG file entries"""
    if not img_file or not img_file.entries:
        table.setRowCount(0)
        return

    entries = img_file.entries
    print(f"DEBUG: Populating table with {len(entries)} entries")

    # Clear existing data first
    table.setRowCount(0)
    table.setRowCount(len(entries))

    for row, entry in enumerate(entries):
        # Name
        table.setItem(row, 0, QTableWidgetItem(entry.name))

        # Type (file extension) - FIXED: Always use name-based detection
        if '.' in entry.name:
            file_type = entry.name.split('.')[-1].upper()
        else:
            file_type = "Unknown"
        table.setItem(row, 1, QTableWidgetItem(file_type))

        # Size
        try:
            from components.img_core_classes import format_file_size
            size_text = format_file_size(entry.size)
        except:
            size_text = f"{entry.size} bytes"
        table.setItem(row, 2, QTableWidgetItem(size_text))

        # Offset
        table.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:X}"))

        # Version
        version = "Unknown"
        try:
            if hasattr(entry, 'get_version_text') and callable(entry.get_version_text):
                version = entry.get_version_text()
            elif hasattr(entry, 'version') and entry.version:
                version = str(entry.version)
            else:
                # Provide sensible defaults based on file type
                if file_type in ['DFF', 'TXD']:
                    version = "RenderWare"
                elif file_type == 'COL':
                    version = "COL"
                elif file_type == 'IFP':
                    version = "IFP"
                elif file_type == 'WAV':
                    version = "Audio"
                elif file_type == 'SCM':
                    version = "Script"
                else:
                    version = "Unknown"
        except Exception as e:
            print(f"DEBUG: Version detection error for {entry.name}: {e}")
            version = "Unknown"

        table.setItem(row, 4, QTableWidgetItem(version))

        # Compression
        compression = "None"
        try:
            if hasattr(entry, 'compression_type') and entry.compression_type:
                compression = str(entry.compression_type)
            elif hasattr(entry, 'compressed') and entry.compressed:
                compression = "Compressed"
        except:
            compression = "None"

        table.setItem(row, 5, QTableWidgetItem(compression))

        # Status
        status = "Ready"
        try:
            if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                status = "New"
            elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                status = "Modified"
        except:
            status = "Ready"

        table.setItem(row, 6, QTableWidgetItem(status))

        # Make items read-only
        for col in range(7):
            item = table.item(row, col)
            if item:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

    print(f"DEBUG: Table population complete.")


def reset_table_styling(main_window): #vers 4
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


def setup_col_table_structure(main_window): #vers 4
    """Setup table structure for COL data"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return False

        table = main_window.gui_layout.table

        # Set up 7-column structure (same as IMG)
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Offset", "Version", "Compression", "Status"
        ])

        # Configure table properties
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSortingEnabled(True)

        # Auto-resize columns
        header = table.horizontalHeader()
        if hasattr(header, 'setSectionResizeMode'):
            from PyQt6.QtWidgets import QHeaderView
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name column
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Offset
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Version
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Compression
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Status

        main_window.log_message("✅ COL table structure setup complete")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL table structure: {str(e)}")
        return False


# Export functions
__all__ = [
    'estimate_col_model_size_bytes',
    'format_file_size',
    'populate_col_table_img_format', 
    'populate_col_table_enhanced',
    'populate_img_table',
    'reset_table_styling',
    'setup_col_table_structure'
]
