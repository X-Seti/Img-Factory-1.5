#this belongs in components/Img_Factory/img_factory_utility.py - Version: 1
# X-Seti - Oct27 2025 - IMG Factory 1.5 - Utility Methods

"""
Utility Methods
Helper functions, callbacks, and utility methods
"""

from typing import Optional

##Methods list -
# _unified_double_click_handler
# _unified_selection_handler
# _update_status_from_signal
# _update_ui_for_current_file
# add_update_button_states_stub
# apply_quick_fixes
# apply_search_and_performance_fixes
# debug_img_entries
# dump_function
# export_selected_function
# fix_close_manager_tab_reference
# fix_selection_callback_functions
# get_current_file_type
# has_col_file_loaded
# has_img_file_loaded
# import_function
# open_file_dialog
# patch_close_manager_for_robust_tabs
# remove_selected_function
# setup_missing_utility_functions
# split_via_function
# update_button_states


def export_selected_function(main_window):
    selected_tab, options = show_mirror_tab_selection(main_window, 'export')
    if selected_tab:
        start_export_operation(main_window, selected_tab, options)

# In core/import.py
def import_function(main_window):
    selected_tab, options = show_mirror_tab_selection(main_window, 'import')
    if selected_tab and options.get('import_files'):
        start_import_operation(main_window, selected_tab, options)

# In core/remove.py
def remove_selected_function(main_window):
    selected_tab, options = show_mirror_tab_selection(main_window, 'remove')
    if selected_tab:
        start_remove_operation(main_window, selected_tab, options)

# In core/dump.py
def dump_function(main_window):
    selected_tab, options = show_mirror_tab_selection(main_window, 'dump')
    if selected_tab:
        start_dump_operation(main_window, selected_tab, options)

def split_via_function(main_window):
    selected_tab, options = show_mirror_tab_selection(main_window, 'split_via')
    if selected_tab:
        split_methofrom methods.img_core_classes import IMGFile, COLFiled = options.get('split_method', 'size')  # 'size' or 'count'
        split_value = options.get('split_value', 50)
        start_split_operation(main_window, selected_tab, split_method, split_value)

def debug_img_entries(self): #vers 4
    """Debug function to check what entries are actually loaded"""
    if not self.current_img or not self.current_img.entries:
        self.log_message("❌ No IMG loaded or no entries found")
        return

    self.log_message(f"🔍 DEBUG: IMG file has {len(self.current_img.entries)} entries")

    # Count file types
    file_types = {}
    all_extensions = set()

    for i, entry in enumerate(self.current_img.entries):
        # Debug each entry
        self.log_message(f"Entry {i}: {entry.name}")

        # Extract extension both ways
        name_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else "NO_EXT"
        attr_ext = getattr(entry, 'extension', 'NO_ATTR').upper() if hasattr(entry, 'extension') and entry.extension else "NO_ATTR"

        all_extensions.add(name_ext)

        # Count by name-based extension
        file_types[name_ext] = file_types.get(name_ext, 0) + 1

        # Log extension differences
        if name_ext != attr_ext:
            self.log_message(f"Extension mismatch: name='{name_ext}' vs attr='{attr_ext}'")

    # Summary
    self.log_message(f"File type summary:")
    for ext, count in sorted(file_types.items()):
        self.log_message(f"  {ext}: {count} files")

    self.log_message(f"All extensions found: {sorted(all_extensions)}")

    # Check table row count vs entries count
    table_rows = self.gui_layout.table.rowCount()
    self.log_message(f"Table has {table_rows} rows, IMG has {len(self.current_img.entries)} entries")

    # Check if any rows are hidden
    hidden_count = 0
    for row in range(table_rows):
        if self.gui_layout.table.isRowHidden(row):
            hidden_count += 1

    self.log_message(f"Hidden rows: {hidden_count}")

    if hidden_count > 0:
        self.log_message("Some rows are hidden! Check the filter settings.")


def _unified_double_click_handler(self, row, filename, item): #vers 2
    """Handle double-click through unified system"""
    # Get the actual filename from the first column (index 0)
    if row < self.gui_layout.table.rowCount():
        name_item = self.gui_layout.table.item(row, 0)
        if name_item:
            actual_filename = name_item.text()
            self.log_message(f"Double-clicked: {actual_filename}")

            # Show file info if IMG is loaded
            if self.current_img and row < len(self.current_img.entries):
                entry = self.current_img.entries[row]
                from methods.img_core_classes import format_file_size
                self.log_message(f"File info: {entry.name} ({format_file_size(entry.size)})")
        else:
            self.log_message(f"Double-clicked row {row} (no filename found)")
    else:
        self.log_message(f"Double-clicked: {filename}")


def _unified_selection_handler(self, selected_rows, selection_count): #vers 1
    """Handle selection changes through unified system"""
    # Update button states based on selection
    has_selection = selection_count > 0
    self._update_button_states(has_selection)

    # Log selection (unified approach - no spam)
    if selection_count == 0:
        # Don't log "Ready" for empty selection to reduce noise
        pass
    elif selection_count == 1:
        # Get filename of selected item
        if selected_rows and len(selected_rows) > 0:
            row = selected_rows[0]
            if row < self.gui_layout.table.rowCount():
                name_item = self.gui_layout.table.item(row, 0)
                if name_item:
                    self.log_message(f"Selected: {name_item.text()}")

def setup_missing_utility_functions(self): #vers 1
    """Add missing utility functions that selection callbacks need"""

    # Simple file type detection functions - MISSING FUNCTIONS
    self.has_col = lambda name: name.lower().endswith('.col') if name else False
    self.has_dff = lambda name: name.lower().endswith('.dff') if name else False
    self.has_txd = lambda name: name.lower().endswith('.txd') if name else False
    self.get_entry_type = lambda name: name.split('.')[-1].upper() if name and '.' in name else "Unknown"

    self.log_message("Missing utility functions added")



def fix_selection_callback_functions(main_window): #vers 1
    """Add missing selection callback functions to main window"""
    try:
        # Add the missing has_* functions
        main_window.has_col = has_col
        main_window.has_dff = has_dff
        main_window.has_txd = has_txd
        main_window.get_entry_type = get_entry_type

        # Add other common utility functions that might be missing
        def get_selected_entry_name():
            """Get name of currently selected entry"""
            try:
                if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
                    table = main_window.gui_layout.table
                    current_row = table.currentRow()
                    if current_row >= 0:
                        name_item = table.item(current_row, 0)
                        if name_item:
                            return name_item.text()
                return None
            except:
                return None


        def get_selected_entries_count():
            """Get count of selected entries"""
            try:
                if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
                    table = main_window.gui_layout.table
                    return len(table.selectedItems())
                return 0
            except:
                return 0

        # Add utility functions to main window
        main_window.get_selected_entry_name = get_selected_entry_name
        main_window.get_selected_entries_count = get_selected_entries_count

        main_window.log_message("Selection callback functions fixed")
        return True

    except Exception as e:
        main_window.log_message(f"Selection callback fix failed: {e}")
        return False

def fix_close_manager_tab_reference(main_window): #vers 1
    """Fix close manager missing main_tab_widget reference#"""
    try:
        if hasattr(main_window, 'close_manager'):
            # Add missing reference
            main_window.close_manager.main_tab_widget = main_window.main_tab_widget
            main_window.log_message("Close manager tab reference fixed")
            return True
    except Exception as e:
        main_window.log_message(f"Close manager fix failed: {str(e)}")
    return False


def update_button_states(self, has_selection): #vers 4
    """Update button enabled/disabled states based on selection"""
    # Check what's loaded
    has_img = self.current_img is not None
    has_col = self.current_col is not None
    has_txd = hasattr(self, 'current_txd') and self.current_txd is not None

    # Log the button state changes for debugging
    self.log_message(f"Button states updated: selection={has_selection}, img_loaded={has_img}, col_loaded={has_col}, txd_loaded={has_txd}")

    # Find buttons in GUI layout and update their states
    # These buttons need both an IMG and selection
    selection_dependent_buttons = ['export_btn', 'export_selected_btn', 'remove_btn', 'remove_selected_btn', 'reload_btn', 'extract_btn', 'quick_export_btn']

    for btn_name in selection_dependent_buttons:
        if hasattr(self.gui_layout, btn_name):
            button = getattr(self.gui_layout, btn_name)
            if hasattr(button, 'setEnabled'):
                # Enable for IMG files with selection, open edit for COL and TXD - TODO
                button.setEnabled(has_selection and has_img and has_col and has_txd)

    # These buttons only need an IMG (no selection required) - DISABLE for COL and TXD
    img_dependent_buttons = [
        'import_btn', 'import_files_btn', 'rebuild_btn', 'close_btn',
        'validate_btn', 'refresh_btn', 'reload_btn'
    ]

    for btn_name in img_dependent_buttons:
        if hasattr(self.gui_layout, btn_name):
            button = getattr(self.gui_layout, btn_name)
            if hasattr(button, 'setEnabled'):
                # Special handling for rebuild - disable for COL and TXD files
                if btn_name == 'rebuild_btn':
                    button.setEnabled(has_img and not has_col and not has_txd)
                else:
                    # Import/Close/Validate work for IMG or COL, but open TXD - TODO
                    button.setEnabled((has_img or has_col) and has_txd)


def _update_status_from_signal(self, message): #vers 3
    """Update status from unified signal system"""
    # Update status bar if available
    if hasattr(self, 'statusBar') and self.statusBar():
        self.statusBar().showMessage(message)

    # Also update GUI layout status if available
    if hasattr(self.gui_layout, 'status_label'):
        self.gui_layout.status_label.setText(message)


#these need to be checked
def add_update_button_states_stub(main_window): #vers 1
    """Add stub for _update_button_states to prevent selection callback errors"""

def _update_button_states_stub(has_selection):
    """Stub for button state updates - handled by connections.py"""
    pass  # Do nothing - connections.py handles this

    main_window._update_button_states = _update_button_states_stub
    main_window.log_message("Button states stub added")


def apply_quick_fixes(main_window): #vers 2
    """Apply all quick fixes for missing methods"""
    try:
        fixes_applied = 0

        # Fix 1: Add missing COL UI update method (uses proper methods/)
        if not hasattr(main_window, '_update_ui_for_loaded_col'):
            setattr(main_window, '_update_ui_for_loaded_col',
                lambda: _update_ui_for_loaded_col(main_window))
            setattr(main_window, '_basic_col_table_fallback',
                lambda file_name: _basic_col_table_fallback(main_window, file_name))
            fixes_applied += 1

        # Fix 2: Fix close manager tab reference
        if fix_close_manager_tab_reference(main_window):
            fixes_applied += 1

        # Fix 3: Add button states stub
        add_update_button_states_stub(main_window)
        fixes_applied += 1

        main_window.log_message(f"Applied {fixes_applied} quick fixes")
        return True

    except Exception as e:
        main_window.log_message(f"Quick fixes failed: {str(e)}")
        return False


def handle_col_file_open(self, file_path: str): #vers 4
    """Handle opening of COL files"""
    try:
        if file_path.lower().endswith('.col'):
            self.log_message(f"Loading COL file: {os.path.basename(file_path)}")

            if hasattr(self, 'load_col_file_safely'):
                success = self.load_col_file_safely(file_path)
                if success:
                    self.log_message("COL file loaded successfully")
                else:
                    self.log_message("Failed to load COL file")
                return success
            else:
                self.log_message("COL integration not available")
                return False

        return False

    except Exception as e:
        self.log_message(f"Error handling COL file: {str(e)}")
        return False

def _reindex_open_files_robust(self, removed_index): #vers 1
    """ROBUST: Reindex with data preservation"""
    try:
        if not hasattr(self.main_window, 'open_files'):
            return

        self.log_message(f"ROBUST reindexing after removing tab {removed_index}")

        # STEP 1: Preserve data for all remaining tabs
        preserved_data = {}
        for tab_index in list(self.main_window.open_files.keys()):
            if tab_index != removed_index:
                if hasattr(self.main_window, 'preserve_tab_table_data'):
                    self.main_window.preserve_tab_table_data(tab_index)

        # STEP 2: Reindex open_files (same as before)
        new_open_files = {}
        sorted_items = sorted(self.main_window.open_files.items())

        new_index = 0
        for old_index, file_info in sorted_items:
            if old_index == removed_index:
                self.log_message(f"Skipping removed tab {old_index}")
                continue

            new_open_files[new_index] = file_info
            self.log_message(f"Tab {old_index} → Tab {new_index}: {file_info.get('tab_name', 'Unknown')}")
            new_index += 1

        self.main_window.open_files = new_open_files

        # STEP 3: Restore data for all tabs in their new positions
        for new_tab_index in new_open_files.keys():
            if hasattr(self.main_window, 'restore_tab_table_data'):
                self.main_window.restore_tab_table_data(new_tab_index)

        self.log_message("ROBUST reindexing complete with data preservation")

        # STEP 4: Update current tab references
        current_index = self.main_window.main_tab_widget.currentIndex()
        if hasattr(self.main_window, 'update_tab_manager_references'):
            self.main_window.update_tab_manager_references(current_index)

    except Exception as e:
        self.log_message(f"Error in robust reindexing: {str(e)}")


def patch_close_manager_for_robust_tabs(main_window): #vers 1
    """Patch existing close manager to use robust tab system"""
    try:
        if hasattr(main_window, 'close_manager'):
            # Replace the reindex method with robust version
            original_reindex = main_window.close_manager._reindex_open_files

            def robust_reindex_wrapper(removed_index):
                return _reindex_open_files_robust(main_window.close_manager, removed_index)

            main_window.close_manager._reindex_open_files = robust_reindex_wrapper
            main_window.log_message("Close manager patched for robust tabs")
            return True
        else:
            main_window.log_message("No close manager found to patch")
            return False

    except Exception as e:
        main_window.log_message(f"Error patching close manager: {str(e)}")
        return False


def _update_ui_for_current_file(self): #vers 5
    """Update UI for currently selected file"""
    if self.current_img:
        self.log_message("Updating UI for IMG file")
        self._update_ui_for_loaded_img()
    elif self.current_col:
        self.log_message("Updating UI for COL file")
        self._update_ui_for_loaded_col()
    else:
        self.log_message("Updating UI for no file")
        self._update_ui_for_no_img()


def load_col_file_safely(self, file_path): #vers 4
    """Load COL file safely - Use the actual COL loading function"""
    try:
        # Import and use the real COL loading function
        from col_parsing_functions import load_col_file_safely as real_load_col
        success = real_load_col(self, file_path)
        if success:
            self.log_message(f"COL file loaded: {os.path.basename(file_path)}")
        return success
    except Exception as e:
        self.log_message(f"Error loading COL file: {str(e)}")
        return False


def _load_col_as_generic_file(self, file_path): #vers 1
    """Load COL as generic file when COL classes aren't available"""
    try:
        # Create simple COL representation
        self.current_col = {
            "file_path": file_path, "type": "COL", "size": os.path.getsize(file_path)
        }

        # Update UI
        self._update_ui_for_loaded_col()

        self.log_message(f"Loaded COL (generic): {os.path.basename(file_path)}")

    except Exception as e:
        self.log_message(f"Error loading COL as generic: {str(e)}")


def get_current_file_type(main_window) -> str: #vers 1
    """Get the current file type (IMG or COL)"""
    try:
        if hasattr(main_window, 'current_col') and main_window.current_col:
            return 'COL'
        elif hasattr(main_window, 'current_img') and main_window.current_img:
            return 'IMG'
        else:
            return 'UNKNOWN'
    except:
        return 'UNKNOWN'

def has_col_file_loaded(main_window) -> bool: #vers 1
    """Check if a COL file is currently loaded - REPLACES has_col"""
    try:
        return hasattr(main_window, 'current_col') and main_window.current_col is not None
    except:
        return False

def has_img_file_loaded(main_window) -> bool: #vers 1
    """Check if an IMG file is currently loaded"""
    try:
        return hasattr(main_window, 'current_img') and main_window.current_img is not None
    except:
        return False

def open_file_dialog(main_window): #vers 8
    """Unified file dialog for IMG, COL, and TXD files"""
    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        "Open Archive",
        "",
        "All Supported (*.img *.col *.txd);;IMG Archives (*.img);;COL Archives (*.col);;TXD Textures (*.txd);;All Files (*)"
    )

    if file_path:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.txd':
            load_txd_file(main_window, file_path)
        elif file_ext == '.col':
            # Create new tab for COL
            if hasattr(main_window, '_load_col_file_in_new_tab'):
                main_window._load_col_file_in_new_tab(file_path)
            else:
                main_window.load_col_file_safely(file_path)
        else:  # .img
            # Create new tab for IMG
            if hasattr(main_window, '_load_img_file_in_new_tab'):
                main_window._load_img_file_in_new_tab(file_path)
            else:
                main_window.load_img_file(file_path)


    def _on_img_load_progress(self, progress: int, status: str): #vers 5
    """Handle IMG loading progress updates - UPDATED: Uses unified progress system"""
    try:
        from methods.progressbar_functions import update_progress
        update_progress(self, progress, status)
    except ImportError:
        # Fallback for systems without unified progress
        self.log_message(f"Progress: {progress}% - {status}")


def _update_ui_for_no_img(self): #vers 6
    """Update UI when no IMG file is loaded - UPDATED: Uses unified progress system"""
    # Clear current data
    self.current_img = None
    self.current_col = None
    self.current_txd = None

    # Update window title
    self.setWindowTitle("IMG Factory 1.5")

    # Clear table if it exists
    if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
        self.gui_layout.table.setRowCount(0)

    # Reset progress using unified system
    try:
        from methods.progressbar_functions import hide_progress
        hide_progress(self, "Ready")
    except ImportError:
        # Fallback for old systems
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, "Ready")

    # Update file info
    if hasattr(self.gui_layout, 'update_img_info'):
        self.gui_layout.update_img_info("No IMG loaded")

    # Reset any status labels
    if hasattr(self, 'file_path_label'):
        self.file_path_label.setText("No file loaded")
    if hasattr(self, 'version_label'):
        self.version_label.setText("---")
    if hasattr(self, 'entry_count_label'):
        self.entry_count_label.setText("0")
    if hasattr(self, 'img_status_label'):
        self.img_status_label.setText("No IMG loaded")

    # Disable buttons that require an IMG to be loaded
    buttons_to_disable = [
        'close_img_btn', 'rebuild_btn', 'rebuild_as_btn', 'validate_btn',
        'import_btn', 'export_all_btn', 'export_selected_btn'
    ]

    for btn_name in buttons_to_disable:
        if hasattr(self.gui_layout, btn_name):
            button = getattr(self.gui_layout, btn_name)
            if hasattr(button, 'setEnabled'):
                button.setEnabled(False)

def _on_img_load_error(self, error_message: str): #vers 4
    """Handle IMG loading error - UPDATED: Uses unified progress system"""
    self.log_message(f" {error_message}")

    # Hide progress using unified system
    try:
        from methods.progressbar_functions import hide_progress
        hide_progress(self, "Load failed")
    except ImportError:
        # Fallback for old systems
        if hasattr(self.gui_layout, 'hide_progress'):
            self.gui_layout.hide_progress()

    QMessageBox.critical(self, "IMG Load Error", error_message)

    # Add this to __init__ method after GUI creation:
    def integrate_unified_progress_system(self): #vers 1
    """Integrate unified progress system - call in __init__"""
    try:
        from methods.progressbar_functions import integrate_progress_system
        integrate_progress_system(self)
        self.log_message("Unified progress system integrated")
    except ImportError:
        self.log_message("Unified progress system not available - using fallback")
    except Exception as e:
        self.log_message(f"Progress system integration failed: {str(e)}")


def _populate_col_table_img_format(self, col_file, file_name):
    """Populate table with COL models using same format as IMG entries""" #vers 2 #restare
    from PyQt6.QtWidgets import QTableWidgetItem
    from PyQt6.QtCore import Qt

    table = self.gui_layout.table

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
            size_text = self._format_file_size(file_size)
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

        self.log_message(f"COL file loaded but no models found")
        return

    # Show individual models in IMG entry format
    models = col_file.models
    table.setRowCount(len(models))

    self.log_message(f"Populating table with {len(models)} COL models")

    virtual_offset = 0x0  # Virtual offset for COL models

    for row, model in enumerate(models):
        try:
            # Name - use model name or generate one
            model_name = getattr(model, 'name', f"Model_{row}") if hasattr(model, 'name') and model.name else f"Model_{row}"
            table.setItem(row, 0, QTableWidgetItem(model_name))

            # Type - just "COL" (like IMG shows "DFF", "TXD", etc.)
            table.setItem(row, 1, QTableWidgetItem("COL"))

            # Size - estimate model size in same format as IMG
            estimated_size = self._estimate_col_model_size_bytes(model)
            size_text = self._format_file_size(estimated_size)
            table.setItem(row, 2, QTableWidgetItem(size_text))

            # Offset - virtual hex offset (like IMG entries)
            offset_text = f"0x{virtual_offset:X}"
            table.setItem(row, 3, QTableWidgetItem(offset_text))
            virtual_offset += estimated_size  # Increment for next model

            # Version - show just the COL version number (1, 2, 3, or 4)
            if hasattr(model, 'version') and hasattr(model.version, 'value'):
                version_text = str(model.version.value)  # Just "1", "2", "3", or "4"
            elif hasattr(model, 'version'):
                version_text = str(model.version)
            else:
                version_text = "Unknown"
            table.setItem(row, 4, QTableWidgetItem(version_text))

            # Compression - always None for COL models
            table.setItem(row, 5, QTableWidgetItem("None"))

            # Status - based on model content (like IMG status)
            stats = model.get_stats() if hasattr(model, 'get_stats') else {}
            total_elements = stats.get('total_elements', 0)

            if total_elements == 0:
                status = "Empty"
            elif total_elements > 500:
                status = "Complex"
            elif total_elements > 100:
                status = "Medium"
            else:
                status = "Ready"
            table.setItem(row, 6, QTableWidgetItem(status))

            # Make all items read-only (same as IMG)
            for col in range(7):
                item = table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        except Exception as e:
            self.log_message(f"Error populating COL model {row}: {str(e)}")
            # Create fallback row (same as IMG error handling)
            table.setItem(row, 0, QTableWidgetItem(f"Model_{row}"))
            table.setItem(row, 1, QTableWidgetItem("COL"))
            table.setItem(row, 2, QTableWidgetItem("0 B"))
            table.setItem(row, 3, QTableWidgetItem("0x0"))
            table.setItem(row, 4, QTableWidgetItem("Unknown"))
            table.setItem(row, 5, QTableWidgetItem("None"))
            table.setItem(row, 6, QTableWidgetItem("Error"))

    self.log_message(f"Table populated with {len(models)} COL models (IMG format)")

def _estimate_col_model_size_bytes(self, model): #vers 2 #restare
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

def apply_search_and_performance_fixes(self): #vers 2
    """Apply search and performance fixes"""
    try:
        self.log_message("🔧 Applying search and performance fixes...")

        # 1. Setup our new consolidated search system
        from core.guisearch import install_search_system
        if install_search_system(self):
            self.log_message("New search system installed")
        else:
            self.log_message("Search system setup failed")

        # 2. COL debug control (keep your existing code)
        try:
            def toggle_col_debug():
                """Simple COL debug toggle"""
                try:
                    import methods.col_core_classes as col_module
                    current = getattr(col_module, '_global_debug_enabled', False)
                    col_module._global_debug_enabled = not current

                    if col_module._global_debug_enabled:
                        self.log_message("COL debug enabled")
                    else:
                        self.log_message("COL debug disabled")

                except Exception as e:
                    self.log_message(f"COL debug toggle error: {e}")

            # Add to main window
            self.toggle_col_debug = toggle_col_debug

            # Start with debug disabled for performance
            import methods.col_core_classes as col_module
            col_module._global_debug_enabled = False

            self.log_message("COL performance mode enabled")

        except Exception as e:
            self.log_message(f"COL setup issue: {e}")

        self.log_message("Search and performance fixes applied")

    except Exception as e:
        self.log_message(f"Apply fixes error: {e}")


__all__ = [
    'setup_missing_utility_functions',
    'debug_img_entries',
    '_unified_double_click_handler',
    '_unified_selection_handler',
    'update_button_states',
    '_update_status_from_signal',
    '_update_ui_for_current_file',
    'get_current_file_type',
    'has_col_file_loaded',
    'has_img_file_loaded',
    'apply_search_and_performance_fixes',
    'export_selected_function',
    'import_function',
    'remove_selected_function',
    'dump_function',
    'split_via_function',
    'fix_selection_callback_functions',
    'fix_close_manager_tab_reference',
    'add_update_button_states_stub',
    'apply_quick_fixes',
    'patch_close_manager_for_robust_tabs',
    'open_file_dialog'
]
