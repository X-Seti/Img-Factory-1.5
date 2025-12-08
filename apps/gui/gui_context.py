#this belongs in gui/gui_context.py - Version: 10
# X-Seti - August07 2025 - IMG Factory 1.5 - Context Menu Setup Functions

"""
Context Menu Setup Functions - Handles right-click context menu setup
All actual functionality has been moved to apps/core/right_click_actions.py
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

# Import all functionality from right_click_actions
from apps.core.right_click_actions import (
    copy_table_row,
    copy_filename_only,
    copy_file_summary,
    enhanced_context_menu_event,  # Centralized context menu function
    get_selected_entry_info,
    show_entry_properties,
    edit_col_from_img_entry,
    view_col_collision,
    analyze_col_from_img_entry,
    edit_col_collision,
    edit_dff_model,
    edit_txd_textures,
    view_dff_model,
    view_txd_textures,
    replace_selected_entry,
    open_col_editor_dialog,
    open_col_batch_proc_dialog,
    open_col_file_dialog,
    analyze_col_file_dialog
)

##Methods list -
# add_col_context_menu_to_entries_table
# add_img_context_menu_to_entries_table


def add_col_context_menu_to_entries_table(main_window): #vers 5
    """Add enhanced COL context menu to entries table"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return False

        entries_table = main_window.gui_layout.table

        # Set up custom context menu
        entries_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        entries_table.customContextMenuRequested.connect(
            lambda pos: enhanced_context_menu_event(main_window, 
                type('MockEvent', (), {'pos': lambda: pos, 'globalPos': lambda: entries_table.mapToGlobal(pos)})())
        )

        main_window.log_message("✅ Enhanced COL context menu added to entries table")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Error adding COL context menu: {str(e)}")
        return False


def add_img_context_menu_to_entries_table(main_window): #vers 6
    """Add IMG-specific context menu items to entries table"""
    # Use the enhanced COL context menu which handles all file types
    return add_col_context_menu_to_entries_table(main_window)


# Export functions
__all__ = [
    'add_col_context_menu_to_entries_table',
    'add_img_context_menu_to_entries_table', 
    'analyze_col_file_dialog',
    'analyze_col_from_img_entry',
    'edit_col_collision',
    'edit_col_from_img_entry',
    'enhanced_context_menu_event',
    'get_selected_entry_info',
    'open_col_batch_proc_dialog',
    'open_col_editor_dialog',
    'open_col_file_dialog',
    'show_entry_properties',
    'view_col_collision',
    'view_dff_model',
    'view_txd_textures',
    'edit_dff_model',
    'edit_txd_textures',
    'replace_selected_entry',
    'copy_table_row',
    'copy_filename_only',
    'copy_file_summary'
]