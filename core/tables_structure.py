#this belongs in core/ tables_structure.py - Version: 2
# X-Seti - July16 2025 - IMG Factory 1.5 - Table Structure Functions

"""
Table Structure Functions
Handles table population and setup for both IMG and COL files
"""

import os
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from methods.populate_img_table import populate_img_table
from methods.populate_col_table import populate_col_table


# Methods list.
# estimate_col_model_size_bytes
# format_file_size
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


# Export functions
__all__ = [
    'estimate_col_model_size_bytes',
    'format_file_size',
    'reset_table_styling',
    'setup_col_table_structure'
]
