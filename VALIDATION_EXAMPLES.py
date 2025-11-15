# EXAMPLES: How to fix core files to use universal file validation
# This shows the pattern to replace hardcoded IMG checks

"""
BEFORE (OLD WAY - Hardcoded IMG check):
==========================================
def export_selected_function(main_window):
    if not hasattr(main_window, 'current_img') or not main_window.current_img:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    # Rest of function...


AFTER (NEW WAY - Universal validation):
=========================================
from apps.methods.file_validation import validate_img_file

def export_selected_function(main_window):
    success, img_file = validate_img_file(main_window, "Export Selected")
    if not success:
        return False
    
    # Use img_file instead of main_window.current_img
    # Rest of function...
"""

# ==============================================================================
# EXAMPLE 1: Export function (apps/core/export.py)
# ==============================================================================

# OLD CODE:
def export_selected_function_OLD(main_window):
    """OLD VERSION - uses current_img"""
    if not hasattr(main_window, 'current_img') or not main_window.current_img:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    # Get selected entries
    selected = []
    for item in main_window.gui_layout.table.selectedItems():
        selected.append(item.row())
    
    if not selected:
        QMessageBox.warning(main_window, "No Selection", "No entries selected")
        return False
    
    # Export logic...
    for row in selected:
        entry = main_window.current_img.entries[row]
        # Export entry...

# NEW CODE:
def export_selected_function_NEW(main_window):
    """NEW VERSION - uses universal validation"""
    from apps.methods.file_validation import get_selected_entries_for_operation
    
    # Validate and get selected entries in one call
    success, selected_entries, img_file, file_type = get_selected_entries_for_operation(
        main_window, "Export Selected", required_type='IMG'
    )
    
    if not success:
        return False
    
    # Export logic - use selected_entries list directly
    for entry in selected_entries:
        # Export entry...
        pass


# ==============================================================================
# EXAMPLE 2: Import function (apps/core/impotr.py)
# ==============================================================================

# OLD CODE:
def import_function_OLD(main_window):
    """OLD VERSION"""
    if not hasattr(main_window, 'current_img') or not main_window.current_img:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    # Import logic...

# NEW CODE:
def import_function_NEW(main_window):
    """NEW VERSION"""
    from apps.methods.file_validation import validate_img_file
    
    success, img_file = validate_img_file(main_window, "Import")
    if not success:
        return False
    
    # Import logic - use img_file
    # img_file.add_entry(...)


# ==============================================================================
# EXAMPLE 3: Remove function (apps/core/remove.py)
# ==============================================================================

# OLD CODE:
def remove_selected_function_OLD(main_window):
    """OLD VERSION"""
    if not hasattr(main_window, 'current_img') or not main_window.current_img:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    # Get selected
    selected = []
    for item in main_window.gui_layout.table.selectedItems():
        selected.append(item.row())
    
    if not selected:
        return False
    
    # Remove logic...

# NEW CODE:
def remove_selected_function_NEW(main_window):
    """NEW VERSION"""
    from apps.methods.file_validation import get_selected_entries_for_operation
    
    success, selected_entries, img_file, file_type = get_selected_entries_for_operation(
        main_window, "Remove Selected", required_type='IMG'
    )
    
    if not success:
        return False
    
    # Remove logic - use selected_entries
    for entry in selected_entries:
        img_file.remove_entry(entry)


# ==============================================================================
# EXAMPLE 4: Dump function (apps/core/dump.py)
# ==============================================================================

# OLD CODE:
def dump_selected_function_OLD(main_window):
    """OLD VERSION"""
    if not hasattr(main_window, 'current_img') or not main_window.current_img:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    # Dump logic...

# NEW CODE:
def dump_selected_function_NEW(main_window):
    """NEW VERSION"""
    from apps.methods.file_validation import get_selected_entries_for_operation
    
    success, selected_entries, img_file, file_type = get_selected_entries_for_operation(
        main_window, "Dump Selected", required_type='IMG'
    )
    
    if not success:
        return False
    
    # Dump logic using selected_entries and img_file


# ==============================================================================
# EXAMPLE 5: COL operations (apps/core/imgcol_*.py)
# ==============================================================================

# OLD CODE:
def imgcol_convert_OLD(main_window):
    """OLD VERSION - only works with IMG"""
    if not hasattr(main_window, 'current_img') or not main_window.current_img:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    # Convert logic...

# NEW CODE:
def imgcol_convert_NEW(main_window):
    """NEW VERSION - works with both IMG and COL"""
    from apps.methods.file_validation import validate_any_file
    
    success, file_object, file_type = validate_any_file(main_window, "Convert COL")
    if not success:
        return False
    
    # Check what we got
    if file_type == 'IMG':
        # Convert COL entries in IMG
        pass
    elif file_type == 'COL':
        # Convert standalone COL
        pass
    else:
        QMessageBox.warning(main_window, "Wrong File Type", 
            f"Cannot convert: {file_type} files not supported")
        return False


# ==============================================================================
# EXAMPLE 6: Export Via (apps/core/export_via.py)
# ==============================================================================

# OLD CODE:
def export_via_function_OLD(main_window):
    """OLD VERSION"""
    if not hasattr(main_window, 'current_img') or not main_window.current_img:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    # Show IDE dialog...

# NEW CODE:
def export_via_function_NEW(main_window):
    """NEW VERSION - works with IMG or COL"""
    from apps.methods.file_validation import validate_any_file
    
    success, file_object, file_type = validate_any_file(main_window, "Export Via")
    if not success:
        return False
    
    # Route to appropriate handler
    if file_type == 'IMG':
        return _export_img_via_ide(main_window, file_object)
    elif file_type == 'COL':
        return _export_col_via_ide(main_window, file_object)
    else:
        QMessageBox.warning(main_window, "Unsupported Type", 
            f"Export Via not supported for {file_type} files")
        return False


# ==============================================================================
# QUICK REPLACEMENT GUIDE
# ==============================================================================

"""
FOR SINGLE FILE VALIDATION (Import, Rebuild, etc):
---------------------------------------------------
REPLACE THIS:
    if not hasattr(main_window, 'current_img') or not main_window.current_img:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False

WITH THIS:
    from apps.methods.file_validation import validate_img_file
    
    success, img_file = validate_img_file(main_window, "Operation Name")
    if not success:
        return False


FOR OPERATIONS NEEDING SELECTED ENTRIES (Export, Remove, Dump):
----------------------------------------------------------------
REPLACE THIS:
    if not hasattr(main_window, 'current_img') or not main_window.current_img:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    selected = []
    for item in main_window.gui_layout.table.selectedItems():
        selected.append(item.row())
    
    if not selected:
        QMessageBox.warning(main_window, "No Selection", "No entries selected")
        return False

WITH THIS:
    from apps.methods.file_validation import get_selected_entries_for_operation
    
    success, selected_entries, img_file, file_type = get_selected_entries_for_operation(
        main_window, "Operation Name", required_type='IMG'
    )
    
    if not success:
        return False
    
    # Use selected_entries list directly


FOR OPERATIONS THAT WORK WITH ANY FILE TYPE:
---------------------------------------------
REPLACE THIS:
    if not hasattr(main_window, 'current_img') or not main_window.current_img:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False

WITH THIS:
    from apps.methods.file_validation import validate_any_file
    
    success, file_object, file_type = validate_any_file(main_window, "Operation Name")
    if not success:
        return False
    
    # Check file_type and handle accordingly
"""
