#this belongs in gui/gui_backend.py - Version: 2
# X-Seti - July15 2025 - Img Factory 1.5
# GUI backend functionality - Clean version with core function integration

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QProgressBar, QTextEdit, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
import os

# Import core functions
try:
    from core.remove import remove_selected_function, remove_via_entries_function
    from core.export import export_selected_function, export_via_function, quick_export_function, dump_all_function
    from core.importer import import_files_function, import_via_function  # Much cleaner!
    from core.utils import get_selected_entries, refresh_table
    CORE_FUNCTIONS_AVAILABLE = True
    print("✅ Core functions imported successfully")
except ImportError as e:
    print(f"⚠️ Core functions not available: {e}")
    CORE_FUNCTIONS_AVAILABLE = False


class ButtonDisplayMode:
    """Button display mode constants"""
    TEXT_ONLY = "text_only"
    ICONS_ONLY = "icons_only" 
    ICONS_WITH_TEXT = "icons_with_text"


class GUIBackend:
    """Backend functionality for GUI layout - COMPLETE WITH CORE FUNCTIONS"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.button_display_mode = ButtonDisplayMode.TEXT_ONLY  # Default: no icons
        
        # Button collections
        self.img_buttons = []       # _update_all_button_displays
        self.entry_buttons = []     # _update_all_button_displays
        self.options_buttons = []   # _update_all_button_displays
        
        # UI References
        self.table = None           # setup_table_context_menu
        self.log = None
        self.status_label = None    # possible conflict
        self.tab_widget = None      # possible conflict
        
        # Theme colors cache
        self._theme_colors_cache = {}
        
        # Initialize core functions and button connections
        self.integrate_core_functions()
        self.button_connections()
    
    def integrate_core_functions(self):
        """Integrate core functions - PRESERVES EXISTING FUNCTIONALITY"""
        # Check if core functions are available by trying to import them
        try:
            from core.remove import remove_selected_function, remove_via_entries_function
            from core.exporter import export_selected_function, export_via_function, quick_export_function, dump_all_function
            from core.importer import import_files_function, import_via_function
            from core.utils import get_selected_entries, refresh_table
            core_available = True
        except ImportError as e:
            self.log_message(f"⚠️ Core functions not available: {e}")
            self._setup_fallback_methods()
            return False
        
        if not core_available:
            self.log_message("⚠️ Core functions not available - using fallback methods")
            self._setup_fallback_methods()
            return False
        
        try:
            # Remove functions
            if not hasattr(self, 'remove_via_entries'):
                self.remove_via_entries = lambda: remove_via_entries_function(self.main_window)
                
            if not hasattr(self, 'remove_selected') or not callable(getattr(self, 'remove_selected', None)):
                self.remove_selected = lambda: remove_selected_function(self.main_window)
            
            # Export functions  
            if not hasattr(self, 'export_selected_via'):
                self.export_selected_via = lambda: export_via_function(self.main_window)
                
            if not hasattr(self, 'quick_export_selected'):
                self.quick_export_selected = lambda: quick_export_function(self.main_window)
                
            if not hasattr(self, 'dump_entries'):
                self.dump_entries = lambda: dump_all_function(self.main_window)
                
            if not hasattr(self, 'export_selected') or not callable(getattr(self, 'export_selected', None)):
                self.export_selected = lambda: export_selected_function(self.main_window)
            
            # Import functions
            if not hasattr(self, 'import_files_via'):
                self.import_files_via = lambda: import_via_function(self.main_window)
                
            if not hasattr(self, 'import_files') or not callable(getattr(self, 'import_files', None)):
                self.import_files = lambda: import_files_function(self.main_window)
            
            # Utility functions
            if not hasattr(self, 'refresh_table') or not callable(getattr(self, 'refresh_table', None)):
                self.refresh_table = lambda: refresh_table(self.main_window)
                
            if not hasattr(self, 'get_selected_entries') or not callable(getattr(self, 'get_selected_entries', None)):
                self.get_selected_entries = lambda: get_selected_entries(self.main_window)
            
            self.log_message("✅ Core functions integrated into GUI backend")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Failed to integrate core functions: {str(e)}")
            self._setup_fallback_methods()
            return False

    def _setup_fallback_methods(self):
        """Setup fallback methods when core functions aren't available"""
        # Add basic fallback implementations
        if not hasattr(self, 'remove_via_entries'):
            self.remove_via_entries = lambda: self.log_message("⚠️ Remove via entries not available")
        if not hasattr(self, 'dump_entries'):
            self.dump_entries = lambda: self.log_message("⚠️ Dump entries not available")
        if not hasattr(self, 'export_selected_via'):
            self.export_selected_via = lambda: self.log_message("⚠️ Export via not available")
        if not hasattr(self, 'quick_export_selected'):
            self.quick_export_selected = lambda: self.log_message("⚠️ Quick export not available")
        if not hasattr(self, 'import_files_via'):
            self.import_files_via = lambda: self.log_message("⚠️ Import via not available")
        if not hasattr(self, 'refresh_table'):
            self.refresh_table = lambda: self.log_message("⚠️ Refresh table not available")
    
    def log_message(self, message):
        """Log message - safe fallback"""
        try:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(message)
            else:
                print(f"GUI Backend: {message}")
        except Exception:
            print(f"GUI Backend: {message}")
    
    def set_button_display_mode(self, mode):
        """Set button display mode and update all buttons"""
        if mode not in [ButtonDisplayMode.TEXT_ONLY, ButtonDisplayMode.ICONS_ONLY, ButtonDisplayMode.ICONS_WITH_TEXT]:
            return False
        
        self.button_display_mode = mode
        self._update_all_button_displays()
        return True
    
    def _update_all_button_displays(self):
        """Update display for all buttons based on current mode"""
        all_buttons = self.img_buttons + self.entry_buttons + self.options_buttons
        
        for btn in all_buttons:
            self._update_button_display(btn)
    
    def _update_button_display(self, btn):
        """Update individual button display based on mode"""
        if not hasattr(btn, 'full_text') or not hasattr(btn, 'short_text'):
            return
        
        if self.button_display_mode == ButtonDisplayMode.TEXT_ONLY:
            btn.setText(btn.short_text)
            btn.setIcon(QIcon())  # Remove icon
        elif self.button_display_mode == ButtonDisplayMode.ICONS_ONLY:
            btn.setText("")
            if hasattr(btn, 'icon_name'):
                btn.setIcon(QIcon.fromTheme(btn.icon_name))
        else:  # ICONS_WITH_TEXT
            btn.setText(btn.full_text)
            if hasattr(btn, 'icon_name'):
                btn.setIcon(QIcon.fromTheme(btn.icon_name))

    def handle_action(self, action_name):
        """Handle unified action signals - COMPLETE with all methods"""
        try:
            action_map = {
                # File operations
                'create_new_img': getattr(self.main_window, 'create_new_img', lambda: self.log_message("Create new IMG not available")),
                'open_img_file': getattr(self.main_window, 'open_img_file', lambda: self.log_message("Open IMG file not available")),
                'reload_img': getattr(self.main_window, 'reload_table', lambda: self.log_message("Reload not available")),
                
                # Close operations
                'close_img': getattr(self.main_window, 'close_img_file', lambda: self.log_message("Close IMG not available")),
                'exit': getattr(self.main_window, 'close', lambda: self.log_message("Exit not available")),
                'close_all': getattr(self.main_window.close_manager, 'close_all_tabs', lambda: self.log_message("Close manager not available")) if hasattr(self.main_window, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'close_all_img': getattr(self.main_window, 'close_all_img', lambda: self.log_message("Close all IMG not available")),
                
                # IMG operations
                'rebuild_img': getattr(self.main_window, 'rebuild_img', lambda: self.log_message("Rebuild IMG not available")),
                'rebuild_img_as': getattr(self.main_window, 'rebuild_img_as', lambda: self.log_message("Rebuild IMG as not available")),
                'rebuild_all_img': getattr(self.main_window, 'rebuild_all_img', lambda: self.log_message("Rebuild all IMG not available")),
                'merge_img': getattr(self.main_window, 'merge_img', lambda: self.log_message("Merge IMG not available")),
                'split_img': getattr(self.main_window, 'split_img', lambda: self.log_message("Split IMG not available")),
                'convert_img_format': getattr(self.main_window, 'convert_img_format', lambda: self.log_message("Convert IMG format not available")),
                
                # Entry operations - Core functions integrated
                'import_files': self.import_files,
                'import_via': self.import_files_via,
                'refresh_table': self.refresh_table,
                'export_selected': self.export_selected,
                'export_via': self.export_selected_via,
                'Quick_export': self.quick_export_selected,
                'remove_selected': self.remove_selected,
                'remove_via': self.remove_via_entries,
                'dump': self.dump_entries,
                
                # Selection operations
                'select_all_entries': getattr(self.main_window, 'select_all_entries', lambda: self.log_message("Select all not available")),
                'Inverse': getattr(self.main_window, 'select_inverse', lambda: self.log_message("Select inverse not available")),
                'Sort': getattr(self.main_window, 'sort_entries', lambda: self.log_message("Sort entries not available")),
                
                # Edit operations
                'rename': getattr(self.main_window, 'rename_selected', lambda: self.log_message("Rename not available")),
                'replace': getattr(self.main_window, 'replace_selected', lambda: self.log_message("Replace not available")),
                'Pin selected': getattr(self.main_window, 'pin_selected_entries', lambda: self.log_message("Pin selected not available")),
            }

            if action_name in action_map:
                self.log_message(f"🎯 Action: {action_name}")
                action_map[action_name]()
            else:
                self.log_message(f"⚠️ Method '{action_name}' not implemented")

        except Exception as e:
            self.log_message(f"❌ Action error ({action_name}): {str(e)}")

    def setup_menu_connections(self):
        """Setup menu connections - UPDATED for unified file loading"""
        try:
            menu_callbacks = {
                'new_img': getattr(self.main_window, 'create_new_img', lambda: self.log_message("Create new IMG not available")),
                'open_img_file': getattr(self.main_window, 'open_img_dialog', lambda: self.log_message("Open IMG dialog not available")),
                'reload_img': getattr(self.main_window, 'reload_table', lambda: self.log_message("Reload not available")),
                
                # Close operations
                'close_img': getattr(self.main_window.close_manager, 'close_img_file', lambda: self.log_message("Close manager not available")) if hasattr(self.main_window, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'exit': getattr(self.main_window, 'close', lambda: self.log_message("Exit not available")),
                'close_all': getattr(self.main_window.close_manager, 'close_all_tabs', lambda: self.log_message("Close manager not available")) if hasattr(self.main_window, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'close_all_img': getattr(self.main_window, 'close_all_img', lambda: self.log_message("Close all IMG not available")),
                
                # IMG operations
                'rebuild_img': getattr(self.main_window, 'rebuild_img', lambda: self.log_message("Rebuild IMG not available")),
                'rebuild_img_as': getattr(self.main_window, 'rebuild_img_as', lambda: self.log_message("Rebuild IMG as not available")),
                'rebuild_all_img': getattr(self.main_window, 'rebuild_all_img', lambda: self.log_message("Rebuild all IMG not available")),
                'merge_img': getattr(self.main_window, 'merge_img', lambda: self.log_message("Merge IMG not available")),
                'split_img': getattr(self.main_window, 'split_img', lambda: self.log_message("Split IMG not available")),
                'convert_img_format': getattr(self.main_window, 'convert_img_format', lambda: self.log_message("Convert IMG format not available")),
                
                # Entry operations - Core functions
                'entry_import': self.import_files,
                'import_files': self.import_files,
                'import_via': self.import_files_via,
                'refresh_table': self.refresh_table,
                'export_selected': self.export_selected,
                'entry_export': self.export_selected,
                'export_via': self.export_selected_via,
                'Quick_export': self.quick_export_selected,
                'entry_remove': self.remove_selected,
                'remove_selected': self.remove_selected,
                'remove_via': self.remove_via_entries,
                'select_all_entries': getattr(self.main_window, 'select_all_entries', lambda: self.log_message("Select all not available")),
                'dump': self.dump_entries,
                
                # Other operations
                'rename': getattr(self.main_window, 'rename_selected', lambda: self.log_message("Rename not available")),
                'replace': getattr(self.main_window, 'replace_selected', lambda: self.log_message("Replace not available")),
                'select': getattr(self.main_window, 'select', lambda: self.log_message("Select not available")),
                'Inverse': getattr(self.main_window, 'select_inverse', lambda: self.log_message("Select inverse not available")),
                'Sort': getattr(self.main_window, 'sort_entries', lambda: self.log_message("Sort entries not available")),
                'Pin selected': getattr(self.main_window, 'pin_selected_entries', lambda: self.log_message("Pin selected not available")),
            }

            if hasattr(self.main_window, 'menu_bar_system') and hasattr(self.main_window.menu_bar_system, 'set_callbacks'):
                self.main_window.menu_bar_system.set_callbacks(menu_callbacks)

            self.log_message("✅ Menu connections established (unified file loading)")

        except Exception as e:
            self.log_message(f"❌ Menu connection error: {str(e)}")

    def button_connections(self):
        """Fix button connections and text"""
        try:
            from PyQt6.QtWidgets import QPushButton

            # Find all buttons and fix their connections
            all_buttons = self.main_window.findChildren(QPushButton)

            for btn in all_buttons:
                btn_text = btn.text()

                # Change "Update List" to "Refresh"
                if any(text in btn_text.lower() for text in ["update list", "update lst"]):
                    btn.setText("🔄 Refresh")
                    try:
                        btn.clicked.disconnect()
                    except:
                        pass
                    btn.clicked.connect(self.refresh_table)
                    self.log_message(f"🔧 Changed '{btn_text}' to 'Refresh'")

                # Fix export button connections
                elif "Export via" in btn_text:
                    try:
                        btn.clicked.disconnect()
                    except:
                        pass
                    btn.clicked.connect(self.export_selected_via)
                    self.log_message(f"🔧 Fixed '{btn_text}' button")

                elif "Quick" in btn_text and "Export" in btn_text:
                    try:
                        btn.clicked.disconnect()
                    except:
                        pass
                    btn.clicked.connect(self.quick_export_selected)
                    self.log_message(f"🔧 Fixed '{btn_text}' button")

            self.log_message("✅ Button connections fixed")
            return True

        except Exception as e:
            self.log_message(f"❌ Error fixing buttons: {str(e)}")
            return False

    def update_info_labels(self, file_name="No file loaded", entry_count=0, file_size=0, format_version="Unknown"):
        """Update information bar labels"""
        try:
            if hasattr(self.main_window, 'file_name_label'):
                self.main_window.file_name_label.setText(f"File: {file_name}")
            if hasattr(self.main_window, 'entry_count_label'):
                self.main_window.entry_count_label.setText(f"Entries: {entry_count}")
            if hasattr(self.main_window, 'file_size_label'):
                self.main_window.file_size_label.setText(f"Size: {file_size} bytes")
            if hasattr(self.main_window, 'format_version_label'):
                self.main_window.format_version_label.setText(f"Format: {format_version}")
        except Exception as e:
            self.log_message(f"❌ Error updating info labels: {str(e)}")

    def enable_buttons_by_context(self, img_loaded=False, entries_selected=False):
        """Enable/disable buttons based on context"""
        try:
            # IMG buttons that need an IMG loaded
            img_dependent_buttons = ["close", "rebuild", "rebuild_as", "rebuild_all", "merge", "split", "convert"]

            # Entry buttons that need entries selected
            selection_dependent_buttons = ["export", "export_via", "quick_export", "remove", "rename", "replace", "pin_selected"]

            # Update IMG buttons
            for btn in self.img_buttons:
                if hasattr(btn, 'full_text'):
                    button_action = btn.full_text.lower().replace(" ", "_")
                    if button_action in img_dependent_buttons:
                        btn.setEnabled(img_loaded)

            # Update Entry buttons
            for btn in self.entry_buttons:
                if hasattr(btn, 'full_text'):
                    button_action = btn.full_text.lower().replace(" ", "_")
                    if button_action in selection_dependent_buttons:
                        btn.setEnabled(entries_selected and img_loaded)
                    elif button_action in ["import", "import_via", "refresh", "select_all", "sel_inverse", "sort"]:
                        btn.setEnabled(img_loaded)
        except Exception as e:
            self.log_message(f"❌ Error enabling buttons: {str(e)}")

    def create_adaptive_button(self, label, action_type=None, icon=None, callback=None, bold=False):
        """Create adaptive button with theme support"""
        btn = QPushButton(label)

        # Set font
        font = btn.font()
        if bold:
            font.setBold(True)
        btn.setFont(font)

        # Set icon if provided
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))

        # Connect callback if provided
        if callback:
            btn.clicked.connect(callback)
        else:
            btn.setEnabled(False)  # Disable buttons without callbacks

        return btn

    def themed_button(self, label, action_type=None, icon=None, bold=False):
        """Legacy method for compatibility"""
        return self.create_adaptive_button(label, action_type, icon, None, bold)

    def setup_table_context_menu(self):
        """Setup context menu for the table"""
        try:
            if hasattr(self.main_window, 'table'):
                self.main_window.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                self.main_window.table.customContextMenuRequested.connect(self._show_table_context_menu)
        except Exception as e:
            self.log_message(f"❌ Error setting up table context menu: {str(e)}")

    def _show_table_context_menu(self, position):
        """Show context menu for table"""
        try:
            if hasattr(self.main_window, 'table'):
                # Get current file info
                current_type = self._get_current_file_type()
                current_file = self._get_current_file()

                if current_file and hasattr(self.main_window, 'create_file_info_popup'):
                    menu = self.main_window.create_file_info_popup(current_type, current_file.get('path', ''), current_file.get('object'))
                    menu.exec(self.main_window.table.mapToGlobal(position))
        except Exception as e:
            self.log_message(f"❌ Error showing context menu: {str(e)}")

    def _get_current_file_type(self):
        """Get currently selected file type"""
        try:
            if hasattr(self.main_window, 'main_type_tabs'):
                index = self.main_window.main_type_tabs.currentIndex()
                return ["IMG", "COL", "TXD"][index] if 0 <= index < 3 else "IMG"
            return "IMG"
        except Exception:
            return "IMG"

    def _get_current_file(self):
        """Get current file information"""
        try:
            # Return current file info from main window
            if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                return {
                    'path': getattr(self.main_window.current_img, 'file_path', 'Unknown'),
                    'object': self.main_window.current_img
                }
            return None
        except Exception:
            return None

# Export classes
__all__ = [
    'GUIBackend',
    'ButtonDisplayMode'
]
