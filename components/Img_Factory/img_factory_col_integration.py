#this belongs in components/Img_Factory/img_factory_col_integration.py - Version: 2
# X-Seti - Oct27 2025 - IMG Factory 1.5 - COL Integration Methods

"""
COL Integration Methods
Handles COL file loading, display, and integration with IMG system
"""

from typing import Optional
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from methods.svg_shared_icons import get_col_file_icon, get_shield_icon
from methods.img_core_classes import IMGFile
from methods.col_core_classes import COLFile
import os

##Methods list -
# _estimate_col_model_size_bytes
# _load_col_as_generic_file
# _load_col_file_in_new_tab
# _on_col_loaded
# _on_col_table_double_click
# _populate_col_table_img_format
# _setup_col_integration_safely
# _update_ui_for_loaded_col
# disable_col_debug
# enable_col_debug
# get_col_model_details_for_display
# handle_col_file_open
# load_col_file_safely
# setup_col_integration
# setup_debug_controls
# show_col_model_details_img_style
# toggle_col_debug

def setup_col_integration(self): #vers 2 #Restored
    """Setup complete COL integration with IMG Factory"""
    try:
        self.log_message("Setting up COL integration...")

        # Enable COL debug based on main debug state
        if hasattr(self, 'debug_enabled') and self.debug_enabled:
            set_col_debug_enabled(True)
        else:
            set_col_debug_enabled(False)

        # Setup complete COL integration
        success = setup_complete_col_integration(self)

        if success:
            self.log_message("COL integration completed successfully")

            # Add COL file loading capability
            self.load_col_file_safely = lambda file_path: load_col_file_safely(self, file_path)

            # Mark COL as available
            self.col_integration_active = True

        else:
            self.log_message("COL integration failed")

        return success

    except Exception as e:
        self.log_message(f"Error setting up COL integration: {str(e)}")
        return False


def _update_ui_for_loaded_col(self): #vers 1 #restore
    """Update UI when COL file is loaded - Uses proper methods/populate_col_table.py"""
    if not hasattr(self, 'current_col') or not self.current_col:
        self.log_message("_update_ui_for_loaded_col called but no current_col")
        return

    try:
        # Update window title
        if hasattr(self.current_col, 'file_path'):
            file_name = os.path.basename(self.current_col.file_path)
            self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        # Use proper COL table population from methods/
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
            try:
                # Import the proper COL table functions
                from methods.populate_col_table import setup_col_table_structure, populate_table_with_col_data_debug

                # Setup COL table structure (proper headers and widths)
                setup_col_table_structure(self)

                # Populate with actual COL data using the methods system
                populate_table_with_col_data_debug(self, self.current_col)

                model_count = len(self.current_col.models) if hasattr(self.current_col, 'models') else 0
                self.log_message(f"COL table populated with {model_count} models")

            except ImportError as e:
                self.log_message(f"COL methods not available: {str(e)}")
                # Fallback to basic display
                self._basic_col_table_fallback(file_name)

        # Update status
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, "COL loaded")

        self.log_message("COL UI updated successfully")

    except Exception as e:
        self.log_message(f"Error updating COL UI: {str(e)}")

# FIX: Close manager tab widget issue
def fix_close_manager_tab_reference(main_window): #vers 1
    #"""Fix close manager missing main_tab_widget reference#"""
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


# MASTER FIX FUNCTION
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

def create_new_img(self): #vers 5
    """Show new IMG creation dialog - FIXED: No signal connections"""

def select_all_entries(self): #vers 3
    """Select all entries in current table"""
    if hasattr(self.gui_layout, 'table') and self.gui_layout.table:
        self.gui_layout.table.selectAll()
        self.log_message("Selected all entries")


def validate_img(self): #vers 4
    """Validate current IMG file"""
    if not self.current_img:
        self.log_message("No IMG file loaded")
        return

    try:
        from methods.img_validation import IMGValidator
        validation = IMGValidator.validate_img_file(self.current_img)
        if validation.is_valid:
            self.log_message("IMG validation passed")
        else:
            self.log_message(f"IMG validation issues: {validation.get_summary()}")
    except Exception as e:
        self.log_message(f"Validation error: {str(e)}")


def show_gui_settings(self): #vers 5
    """Show GUI settings dialog"""
    self.log_message("GUI settings requested")
    try:
        from utils.app_settings_system import SettingsDialog
        dialog = SettingsDialog(self.app_settings, self)
        dialog.exec()
    except Exception as e:
        self.log_message(f"Settings dialog error: {str(e)}")


def show_about(self):
    """Show about dialog"""
    QMessageBox.about(self, "About IMG Factory 1.5", "IMG Factory 1.5\nAdvanced IMG Archive Management\nX-Seti 2025")


def enable_col_debug(self): #vers 2 #restore
    """Enable COL debug output"""
    # Set debug flag on all loaded COL files
    if hasattr(self, 'current_col') and self.current_col:
        self.current_col._debug_enabled = True

    # Set global flag for future COL files
    import methods.col_core_classes as col_module
    col_module._global_debug_enabled = True

    self.log_message("COL debug output enabled")


def disable_col_debug(self): #vers 2 #restore
    """Disable COL debug output"""
    # Set debug flag on all loaded COL files
    if hasattr(self, 'current_col') and self.current_col:
        self.current_col._debug_enabled = False

    # Set global flag for future COL files
    import methods.col_core_classes as col_module
    col_module._global_debug_enabled = False

    self.log_message("COL debug output disabled")

def toggle_col_debug(self): #vers 2 #restore
    """Toggle COL debug output"""
    try:
        import methods.col_core_classes as col_module
        debug_enabled = getattr(col_module, '_global_debug_enabled', False)

        if debug_enabled:
            self.disable_col_debug()
        else:
            self.enable_col_debug()

    except Exception as e:
        self.log_message(f"Debug toggle error: {e}")


def setup_debug_controls(self): #vers 2 #restore
    """Setup debug control shortcuts - ADD THIS TO __init__"""
    try:
        from PyQt6.QtGui import QShortcut, QKeySequence

        # Ctrl+Shift+D for debug toggle
        debug_shortcut = QShortcut(QKeySequence("Ctrl+Shift+D"), self)
        debug_shortcut.activated.connect(self.toggle_col_debug)

        # Start with debug disabled for performance
        self.disable_col_debug()

        self.log_message("Debug controls ready (Ctrl+Shift+D to toggle COL debug)")

    except Exception as e:
        self.log_message(f"Debug controls error: {e}")
#cut here
def _create_ui(self): #vers 11
    """Create the main user interface - WITH TABS FIXED"""
    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    # Main layout
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(5, 5, 5, 5)

    # Create main tab widget for file handling
    self.main_tab_widget = QTabWidget()
    self.main_tab_widget.setTabsClosable(True)
    self.main_tab_widget.setMovable(True)

    # Initialize open files tracking (for migration)
    if not hasattr(self, 'open_files'):
        self.open_files = {}

    # Create initial empty tab
    self._create_initial_tab()

    # Setup close manager BEFORE tab system
    self.close_manager = install_close_functions(self)

    # Setup NEW tab system
    #setup_tab_system(self)

    # Migrate existing tabs if any
    if self.open_files:
        migrate_tabs(self)

    # Add tab widget to main layout
    main_layout.addWidget(self.main_tab_widget)

    # Create GUI layout system (single instance)
    self.gui_layout.create_status_bar()
    self.gui_layout.apply_table_theme()

    # Setup unified signal system
    self.setup_unified_signals()


def _create_initial_tab(self): #vers 4
    #./components/img_close_functions.py: - def _create_initial_tab[self]
    """Create initial empty tab"""
    # Create tab widget
    tab_widget = QWidget()
    tab_layout = QVBoxLayout(tab_widget)
    tab_layout.setContentsMargins(0, 0, 0, 0)

    # Create GUI layout for this tab
    self.gui_layout.create_main_ui_with_splitters(tab_layout)

    # Add tab with "No file" label
    self.main_tab_widget.addTab(tab_widget, "No File")


def _find_table_in_tab(self, tab_widget): #vers 1
    """Find the table widget in a specific tab - HELPER METHOD"""
    try:
        if not tab_widget:
            return None

        # Method 1: Check for dedicated_table attribute (robust system)
        if hasattr(tab_widget, 'dedicated_table'):
            return tab_widget.dedicated_table

        # Method 2: Search recursively through widget hierarchy
        from PyQt6.QtWidgets import QTableWidget

        def find_table_recursive(widget):
            if isinstance(widget, QTableWidget):
                return widget
            for child in widget.findChildren(QTableWidget):
                return child  # Return first table found
            return None

        table = find_table_recursive(tab_widget)
        if table:
            return table

        # Method 3: Check standard locations
        if hasattr(tab_widget, 'table'):
            return tab_widget.table

        return None

    except Exception as e:
        self.log_message(f"Error finding table in tab: {str(e)}")
        return None


def _log_current_tab_state(self, tab_index): #vers 1
    """Log current tab state for debugging export issues - HELPER METHOD"""
    try:
        # Log file state
        if self.current_img:
            entry_count = len(self.current_img.entries) if self.current_img.entries else 0
            self.log_message(f"State: IMG with {entry_count} entries")
        elif self.current_col:
            if hasattr(self.current_col, 'models'):
                model_count = len(self.current_col.models) if self.current_col.models else 0
                self.log_message(f"State: COL with {model_count} models")
            else:
                self.log_message(f"State: COL file loaded")
        else:
            self.log_message(f"State: No file loaded")

        # Log table state
        if hasattr(self.gui_layout, 'table') and self.gui_layout.table:
            table = self.gui_layout.table
            row_count = table.rowCount() if table else 0
            self.log_message(f"Table: {row_count} rows in gui_layout.table")
        else:
            self.log_message(f"Table: No table reference in gui_layout")

    except Exception as e:
        self.log_message(f"Error logging tab state: {str(e)}")


def ensure_current_tab_references_valid(self): #vers 1
    """Ensure current tab references are valid before export operations - PUBLIC METHOD"""
    try:
        current_index = self.main_tab_widget.currentIndex()
        if current_index == -1:
            return False

        # Force update tab references
        self._on_tab_changed(current_index)

        # Verify we have valid references
        has_valid_file = self.current_img is not None or self.current_col is not None
        has_valid_table = hasattr(self.gui_layout, 'table') and self.gui_layout.table is not None

        if has_valid_file and has_valid_table:
            self.log_message(f"Tab references validated for export operations")
            return True
        else:
            self.log_message(f"Invalid tab references - File: {has_valid_file}, Table: {has_valid_table}")
            return False

    except Exception as e:
        self.log_message(f"Error validating tab references: {str(e)}")
        return False


def _update_info_bar_for_current_file(self): #vers 1
    """Update info bar based on current file type"""
    try:
        if self.current_img:
            # Update for IMG file
            entry_count = len(self.current_img.entries) if self.current_img.entries else 0
            file_path = getattr(self.current_img, 'file_path', 'Unknown')

            if hasattr(self.gui_layout, 'info_label') and self.gui_layout.info_label:
                self.gui_layout.info_label.setText(f"IMG: {os.path.basename(file_path)} | {entry_count} entries")

        elif self.current_col:
            # Update for COL file
            model_count = len(self.current_col.models) if hasattr(self.current_col, 'models') and self.current_col.models else 0
            file_path = getattr(self.current_col, 'file_path', 'Unknown')

            if hasattr(self.gui_layout, 'info_label') and self.gui_layout.info_label:
                self.gui_layout.info_label.setText(f"COL: {os.path.basename(file_path)} | {model_count} models")

    except Exception as e:
        self.log_message(f"Error updating info bar: {str(e)}")


def setup_robust_tab_system(self): #vers 1
    """Setup robust tab system during initialization"""
    try:
        # Import and install robust tab system
        from core.robust_tab_system import install_robust_tab_system

        if install_robust_tab_system(self):
            self.log_message("Robust tab system ready")

            # Run initial integrity check
            if hasattr(self, 'validate_tab_data_integrity'):
                self.validate_tab_data_integrity()

            return True
        else:
            self.log_message("Failed to setup robust tab system")
            return False

    except ImportError:
        self.log_message("⚠Robust tab system not available - using basic system")
        return False
    except Exception as e:
        self.log_message(f"Error setting up robust tab system: {str(e)}")
        return False


# CLOSE MANAGER INTEGRATION

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


# INTEGRATION PATCH FOR EXISTING CLOSE MANAGER

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

def open_img_file(self): #vers 2
    """Open file dialog - FIXED: Call imported function correctly"""
    try:
        open_file_dialog(self)  # Call function with self parameter
    except Exception as e:
        self.log_message(f"Error opening file dialog: {str(e)}")

def open_file_dialog(self): #vers 1
    """Unified file dialog - imported from core"""
    from core.open_img import open_file_dialog
    return open_file_dialog(self)

def _clean_on_img_loaded(self, img_file: IMGFile): #vers 6
    """Handle IMG loading - USES ISOLATED FILE WINDOW"""
    try:
        # Store the loaded IMG file
        current_index = self.main_tab_widget.currentIndex()
        if current_index in self.open_files:
            self.open_files[current_index]['file_object'] = img_file

        # Set current IMG reference
        self.current_img = img_file
        # CRITICAL: Store file object in tab tracking for tab switching
        current_index = self.main_tab_widget.currentIndex()
        if current_index in self.open_files:
            self.open_files[current_index]['file_object'] = img_file
            self.log_message(f"IMG file object stored in tab {current_index}")

        # Use isolated file window update
        success = self.gui_layout.update_file_window_only(img_file)

        # Properly hide progress and ensure GUI visibility
        self.gui_layout.hide_progress_properly()

        if success:
            self.log_message(f"Loaded (isolated): {os.path.basename(img_file.file_path)} ({len(img_file.entries)} entries)")

    except Exception as e:
        self.log_message(f"Loading error: {str(e)}")


def reload_table(self): #vers 1
    """Reload current file - called by reload button"""
    return self.reload_current_file()


def load_file_unified(self, file_path: str): #vers 8
    """Unified file loader for IMG and COL files"""
    try:
        if not file_path or not os.path.exists(file_path):
            self.log_message("File not found")
            return False

        file_ext = file_path.lower().split('.')[-1]
        file_name = os.path.basename(file_path)

        if file_ext == 'img':
            self._load_img_file_in_new_tab(file_path)  # ← Starts threading
            return True  # ← Return immediately, let threading finish
            try:
                # Import IMG loading components directly
                from methods.img_core_classes import IMGFile
                from methods.populate_img_table import populate_img_table

                # Create IMG file object
                img_file = IMGFile(file_path)

                if not img_file.open():
                    self.log_message(f"Failed to open IMG file: {img_file.get_error()}")
                    return False

                # Set as current IMG file #hangs after second img added?
                #self.current_img = img_file

                # CRITICAL: Setup IMG table structure (6 columns)
                if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
                    table = self.gui_layout.table
                    # Reset to IMG structure
                    table.setColumnCount(6)
                    table.setHorizontalHeaderLabels([
                        "Name", "Type", "Size", "Offset", "RW Version", "Info"
                    ])
                    # Set IMG column widths
                    table.setColumnWidth(0, 200)  # Name
                    table.setColumnWidth(1, 80)   # Type
                    table.setColumnWidth(2, 100)  # Size
                    table.setColumnWidth(3, 100)  # Offset
                    table.setColumnWidth(4, 120)  # RW Version
                    table.setColumnWidth(5, 150)  # Info

                # Populate table with IMG data using proper method

                populate_img_table(table, img_file)

                # Update window title
                self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

                # Update info panel/status
                entry_count = len(img_file.entries) if img_file.entries else 0
                file_size = os.path.getsize(file_path)

                self.log_message(f"IMG file loaded: {entry_count} entries")
                return True

            except Exception as img_error:
                self.log_message(f"Error loading IMG file: {str(img_error)}")
                return False

        elif file_ext == 'col':
            # COL file loading (unchanged - working correctly)
            if hasattr_open_txd_workshop(self, 'load_col_file_safely'):
                self.log_message(f"Loading COL file: {file_name}")
                success = self.load_col_file_safely(file_path)
                if success:
                    self.log_message("COL file loaded successfully")
                else:
                    self.log_message("Failed to load COL file")
                return success
            else:
                self.log_message("COL integration not available")
                return False

        else:
            self.log_message(f"Unsupported file type: {file_ext}")
            return False

    except Exception as e:
        self.log_message(f"Error loading file: {str(e)}")
        import traceback
        traceback.print_exc()  # Debug info
        return False


def _load_img_file_in_new_tab(self, file_path): #vers [your_version + 1]
    """Load IMG file in new tab"""
    try:
        import os
        self.log_message(f"Loading IMG in new tab: {os.path.basename(file_path)}")

        # Create new tab first
        #tab_index = self.create_tab(file_path, 'IMG', None)

        # Then load IMG using your existing thread loader
        if self.load_thread and self.load_thread.isRunning():
            return

        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress_updated.connect(self._on_img_load_progress)
        self.load_thread.loading_finished.connect(self._on_img_loaded)
        self.load_thread.loading_error.connect(self._on_img_load_error)
        self.load_thread.start()

    except Exception as e:
        self.log_message(f"Error loading IMG in new tab: {str(e)}")


def _load_txd_file_in_new_tab(self, file_path): #vers 1
    """Load TXD file in new tab"""
    try:
        import os

        # Create new tab for TXD
        #tab_index = self.create_tab(file_path, 'TXD', None)

        # Update tab to show it's a TXD
        file_name = os.path.basename(file_path)[:-4]  # Remove .txd
        self.main_tab_widget.setTabText(tab_index, f"{file_name}") #TODO SVG icon

        # Open TXD Workshop for this file
        from components.Txd_Editor.txd_workshop import open_txd_workshop
        self.txd_workshop = open_txd_workshop(self, file_path)

        if workshop:
            self.log_message(f"TXD loaded in tab {tab_index}: {file_name}")

    except Exception as e:
        self.log_message(f"Error loading TXD in tab:_open_txd_workshop {str(e)}")

def _load_col_file_in_new_tab(self, file_path): #vers [your_version + 1]
    """Load COL file in new tab"""
    try:
        import os
        self.log_message(f"Loading COL in new tab: {os.path.basename(file_path)}")

        # Don't create tab here if load_col_file_safely creates one
        # Just call the loader directly
        if hasattr(self, 'load_col_file_safely'):
            self.load_col_file_safely(file_path)
        else:
            self.log_message("Error: No COL loading method found")

    except Exception as e:
        self.log_message(f"Error loading COL in new tab: {str(e)}")


def _open_txd_workshop(self, file_path=None): #vers 2
    """Open TXD Workshop - connects to tab switching"""
    from components.Txd_Editor.txd_workshop import open_txd_workshop

    if not file_path:
        if hasattr(self, 'current_img') and self.current_img:
            file_path = self.current_img.file_path

    workshop = open_txd_workshop(self, file_path)

    if workshop:
        if not hasattr(self, 'txd_workshops'):
            self.txd_workshops = []

        self.txd_workshops.append(workshop)

        # Connect workshop to tab changes
        self.main_tab_widget.currentChanged.connect(
            lambda idx: self._update_workshop_on_tab_change(workshop, idx)
        )

        workshop.workshop_closed.connect(lambda: self._on_workshop_closed(workshop))
        self.log_message(f"Workshop opened and connected ({len(self.txd_workshops)} total)")

    return workshop


def _update_workshop_on_tab_change(self, workshop, tab_index): #vers 1
    """Update specific workshop when tab changes"""
    if not workshop or not workshop.isVisible():
        return

    tab_widget = self.main_tab_widget.widget(tab_index)
    if not tab_widget:
        return

    file_path = getattr(tab_widget, 'file_path', None)
    if file_path:
        if file_path.lower().endswith('.txd'):
            workshop.open_txd_file(file_path)
        elif file_path.lower().endswith('.img'):
            workshop.load_from_img_archive(file_path)

def _on_workshop_closed(self, workshop): #vers 1
    """Remove closed workshop from tracking list"""
    if hasattr(self, 'txd_workshops') and workshop in self.txd_workshops:
        self.txd_workshops.remove(workshop)
        self.log_message(f"Workshop closed ({len(self.txd_workshops)} remaining)")


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
            self.log_message(f"❌ Error populating COL model {row}: {str(e)}")
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


def _on_load_progress(self, progress: int, status: str): #vers 4
    """Handle loading progress updates"""
    if hasattr(self.gui_layout, 'show_progress'):
        self.gui_layout.show_progress(progress, status)
    else:
        self.log_message(f"Progress: {progress}% - {status}")



def get_entry_rw_version(self, entry, extension): #vers 3
    """Detect RW version from entry file data"""
    try:
        # Skip non-RW files
        if extension not in ['DFF', 'TXD']:
            return "Unknown"

        # Check if entry already has version info
        if hasattr(entry, 'get_version_text') and callable(entry.get_version_text):
            return entry.get_version_text()

        # Try to get file data using different methods
        file_data = None

        # Method 1: Direct data access
        if hasattr(entry, 'get_data'):
            try:
                file_data = entry.get_data()
            except:
                pass

        # Method 2: Extract data method
        if not file_data and hasattr(entry, 'extract_data'):
            try:
                file_data = entry.extract_data()
            except:
                pass

        # Method 3: Read directly from IMG file
        if not file_data:
            try:
                if (hasattr(self, 'current_img') and
                    hasattr(entry, 'offset') and
                    hasattr(entry, 'size') and
                    self.current_img and
                    self.current_img.file_path):

                    with open(self.current_img.file_path, 'rb') as f:
                        f.seek(entry.offset)
                        # Only read the header (12 bytes) for efficiency
                        file_data = f.read(min(entry.size, 12))
            except Exception as e:
                print(f"DEBUG: Failed to read file data for {entry.name}: {e}")
                return "Unknown"

        # Parse RW version from file header
        if file_data and len(file_data) >= 12:
            import struct
            try:
                # RW version is stored at offset 8-12 in RW files
                rw_version = struct.unpack('<I', file_data[8:12])[0]

                if rw_version > 0:
                    version_name = get_rw_version_name(rw_version)
                    print(f"DEBUG: Found RW version 0x{rw_version:X} ({version_name}) for {entry.name}")
                    return f"RW {version_name}"
                else:
                    print(f"DEBUG: Invalid RW version (0) for {entry.name}")
                    return "Unknown"

            except struct.error as e:
                print(f"DEBUG: Struct unpack error for {entry.name}: {e}")
                return "Unknown"
        else:
            print(f"DEBUG: Insufficient file data for {entry.name} (need 12 bytes, got {len(file_data) if file_data else 0})")
            return "Unknown"

    except Exception as e:
        print(f"DEBUG: RW version detection error for {entry.name}: {e}")
        return "Unknown"


def format_file_size(size_bytes): #vers 2 #Restore
    """Format file size same as IMG entries"""
    try:
        # Use the same formatting as IMG entries
        try:
            from methods.img_core_classes import format_file_size
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


def get_col_model_details_for_display(self, model, row_index): #vers 2 #Restore
    """Get COL model details in same format as IMG entry details"""
    try:
        stats = model.get_stats() if hasattr(model, 'get_stats') else {}

        details = {
            'name': getattr(model, 'name', f"Model_{row_index}") if hasattr(model, 'name') and model.name else f"Model_{row_index}",
            'type': "COL",
            'size': self._estimate_col_model_size_bytes(model),
            'version': str(model.version.value) if hasattr(model, 'version') and hasattr(model.version, 'value') else "Unknown",
            'elements': stats.get('total_elements', 0),
            'spheres': stats.get('spheres', 0),
            'boxes': stats.get('boxes', 0),
            'faces': stats.get('faces', 0),
            'vertices': stats.get('vertices', 0),
        }

        if hasattr(model, 'bounding_box') and model.bounding_box:
            bbox = model.bounding_box
            if hasattr(bbox, 'center') and hasattr(bbox, 'radius'):
                details.update({
                    'bbox_center': (bbox.center.x, bbox.center.y, bbox.center.z),
                    'bbox_radius': bbox.radius,
                })
                if hasattr(bbox, 'min') and hasattr(bbox, 'max'):
                    details.update({
                        'bbox_min': (bbox.min.x, bbox.min.y, bbox.min.z),
                        'bbox_max': (bbox.max.x, bbox.max.y, bbox.max.z),
                    })

        return details

    except Exception as e:
        self.log_message(f"Error getting COL model details: {str(e)}")
        return {
            'name': f"Model_{row_index}",
            'type': "COL",
            'size': 0,
            'version': "Unknown",
            'elements': 0,
        }

def show_col_model_details_img_style(self, model_index): #vers 2 #Restore
    """Show COL model details in same style as IMG entry details"""
    try:
        if (not hasattr(self, 'current_col') or
            not hasattr(self.current_col, 'models') or
            model_index >= len(self.current_col.models)):
            return

        model = self.current_col.models[model_index]
        details = self.get_col_model_details_for_display(model, model_index)

        from PyQt6.QtWidgets import QMessageBox

        info_lines = []
        info_lines.append(f"Name: {details['name']}")
        info_lines.append(f"Type: {details['type']}")
        info_lines.append(f"Size: {self._format_file_size(details['size'])}")
        info_lines.append(f"Version: {details['version']}")
        info_lines.append("")
        info_lines.append("Collision Data:")
        info_lines.append(f"  Total Elements: {details['elements']}")
        info_lines.append(f"  Spheres: {details['spheres']}")
        info_lines.append(f"  Boxes: {details['boxes']}")
        info_lines.append(f"  Faces: {details['faces']}")
        info_lines.append(f"  Vertices: {details['vertices']}")

        if 'bbox_center' in details:
            info_lines.append("")
            info_lines.append("Bounding Box:")
            center = details['bbox_center']
            info_lines.append(f"  Center: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
            info_lines.append(f"  Radius: {details['bbox_radius']:.2f}")

        QMessageBox.information(
            self,
            f"COL Model Details - {details['name']}",
            "\n".join(info_lines)
        )

    except Exception as e:
        self.log_message(f"Error showing COL model details: {str(e)}")


def _on_col_table_double_click(self, item): #vers 2 #Restore
    """Handle double-click on COL table item - IMG style"""
    try:
        if hasattr(self, 'current_col') and hasattr(self.current_col, 'models'):
            row = item.row()
            self.show_col_model_details_img_style(row)
        else:
            self.log_message("No COL models available for details")
    except Exception as e:
        self.log_message(f"Error handling COL table double-click: {str(e)}")

def _on_col_loaded(self, col_file): #vers 1 #Restore
    """Handle COL file loaded - UPDATED with styling"""
    try:
        self.current_col = col_file
        # Store COL file in tab tracking
        current_index = self.main_tab_widget.currentIndex()

        if hasattr(self, 'open_files') and current_index in self.open_files:
            self.open_files[current_index]['file_object'] = col_file
            self.log_message(f"COL file object stored in tab {current_index}")

        # Apply COL tab styling if available
        if hasattr(self, '_apply_individual_col_tab_style'):
            self._apply_individual_col_tab_style(current_index)

        # Update file info in open_files (same as IMG)
        if current_index in self.open_files:
            self.open_files[current_index]['file_object'] = col_file
            self.log_message(f"Updated tab {current_index} with loaded COL")
        else:
            self.log_message(f"Tab {current_index} not found in open_files") #TODO warning svg icon

        # Apply enhanced COL tab styling after loading
        if hasattr(self, '_apply_individual_col_tab_style'):
            self._apply_individual_col_tab_style(current_index)

        # Update UI for loaded COL
        if hasattr(self, '_update_ui_for_loaded_col'):
            self._update_ui_for_loaded_col()

        # Update window title to show current file
        file_name = os.path.basename(col_file.file_path) if hasattr(col_file, 'file_path') else "Unknown COL"
        self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        model_count = len(col_file.models) if hasattr(col_file, 'models') and col_file.models else 0
        self.log_message(f"Loaded: {file_name} ({model_count} models)")

        # Hide progress and show COL-specific status
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, f"COL loaded: {model_count} models")

    except Exception as e:
        self.log_message(f"Error in _on_col_loaded: {str(e)}")
        if hasattr(self, '_on_col_load_error'):
            self._on_col_load_error(str(e))


def _setup_col_integration_safely(self):
    """Setup COL integration safely"""
    try:
        if COL_SETUP_FUNCTION:
            result = COL_SETUP_FUNCTION(self)
            if result:
                self.log_message("COL functionality integrated")
            else:
                self.log_message("COL integration returned False")
        else:
            self.log_message("COL integration function not available")
    except Exception as e:
        self.log_message(f"COL integration error: {str(e)}")

def _on_load_progress(self, progress: int, status: str): #vers 2 #Restore
    """Handle loading progress updates"""
    if hasattr(self.gui_layout, 'show_progress'):
        self.gui_layout.show_progress(progress, status)
    else:
        self.log_message(f"Progress: {progress}% - {status}")


__all__ = [
    'setup_col_integration',
    '_update_ui_for_loaded_col',
    'handle_col_file_open',
    'enable_col_debug',
    'disable_col_debug',
    'toggle_col_debug',
    'setup_debug_controls',
    'load_col_file_safely',
    '_load_col_as_generic_file',
    '_load_col_file_in_new_tab',
    '_populate_col_table_img_format',
    '_estimate_col_model_size_bytes',
    'get_col_model_details_for_display',
    'show_col_model_details_img_style',
    '_on_col_table_double_click',
    '_on_col_loaded',
    '_setup_col_integration_safely'
]
