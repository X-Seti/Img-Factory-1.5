#this belongs in gui/ gui_infobar.py - Version: 1
# X-Seti - July16 2025 - IMG Factory 1.5 - Info Bar Functions

"""
Info Bar Functions
Handles info bar updates for both IMG and COL files
"""


def update_col_info_bar_enhanced(main_window, col_file, file_path):
    """Update info bar using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager
        
        display_manager = COLDisplayManager(main_window)
        display_manager.update_col_info_bar(col_file, file_path)
        main_window.log_message("✅ Enhanced info bar updated")
        
    except Exception as e:
        main_window.log_message(f"❌ Enhanced info bar update failed: {str(e)}")
        raise


def update_img_info_bar(main_window, img_file, file_path):
    """Update info bar for IMG files"""
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'update_img_info'):
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            main_window.gui_layout.update_img_info(f"IMG: {file_name}")
        
        # Update entry count and file size
        if hasattr(main_window, 'gui_layout'):
            entry_count = len(img_file.entries) if img_file.entries else 0
            main_window.gui_layout.show_progress(-1, f"Loaded: {entry_count} entries")
        
        main_window.log_message("✅ IMG info bar updated")
        
    except Exception as e:
        main_window.log_message(f"❌ IMG info bar update failed: {str(e)}")


# Export functions
__all__ = [
    'update_col_info_bar_enhanced',
    'update_img_info_bar'
]