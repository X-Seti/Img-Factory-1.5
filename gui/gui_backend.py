#this belongs in gui/gui_backend.py - Version: 1 
# X-Seti - July14 2025 - Img Factory 1.5
# GUI backend functionality separated from layout

#This file belongs to gui/gui_layput - extra methods

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QProgressBar, QTextEdit, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon


class ButtonDisplayMode:
    """Button display mode constants"""
    TEXT_ONLY = "text_only"
    ICONS_ONLY = "icons_only" 
    ICONS_WITH_TEXT = "icons_with_text"


class GUIBackend:
    """Backend functionality for GUI layout"""
    
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
        self.button_connections()
        
        # Theme colors cache
        self._theme_colors_cache = {}
    
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
            btn.setToolTip(btn.full_text)
            
        elif self.button_display_mode == ButtonDisplayMode.ICONS_ONLY:
            btn.setText("")
            if hasattr(btn, 'icon_name'):
                btn.setIcon(self._safe_load_icon(btn.icon_name))
            btn.setToolTip(btn.full_text)
            
        elif self.button_display_mode == ButtonDisplayMode.ICONS_WITH_TEXT:
            btn.setText(btn.short_text)
            if hasattr(btn, 'icon_name'):
                btn.setIcon(self._safe_load_icon(btn.icon_name))
            btn.setToolTip(btn.full_text)
    
    def _safe_load_icon(self, icon_name):
        """Safely load icon with fallback"""
        if not icon_name:
            return QIcon()
        
        try:
            # Try theme icon first
            theme_icon = QIcon.fromTheme(icon_name)
            if theme_icon and not theme_icon.isNull():
                return theme_icon
        except Exception:
            pass
        
        # Try local icon paths
        try:
            icon_paths = [
                f"icons/{icon_name}.png",
                f"gui/icons/{icon_name}.png",
                f"resources/icons/{icon_name}.png"
            ]
            
            for path in icon_paths:
                import os
                if os.path.exists(path):
                    local_icon = QIcon(path)
                    if local_icon and not local_icon.isNull():
                        return local_icon
        except Exception:
            pass
        
        # Return empty icon as fallback
        return QIcon()

    # Right-click context menu for detailed file info
    def create_file_info_popup(self, file_type, file_path, file_object):
        """Create detailed file info popup (right-click context menu)"""
        from PyQt6.QtWidgets import QMenu, QAction, QMessageBox

        menu = QMenu(self.main_window)

        # File info action
        info_action = QAction("📋 Detailed File Information", self.main_window)
        info_action.triggered.connect(lambda: self._show_detailed_file_info(file_type, file_path, file_object))
        menu.addAction(info_action)

        # Properties action
        props_action = QAction("🔍 File Properties", self.main_window)
        props_action.triggered.connect(lambda: self._show_file_properties(file_type, file_path, file_object))
        menu.addAction(props_action)

        menu.addSeparator()

        # File operations
        if file_type == "IMG":
            validate_action = QAction("✅ Validate IMG", self.main_window)
            validate_action.triggered.connect(lambda: self.main_window.validate_img())
            menu.addAction(validate_action)

        return menu

    def _show_detailed_file_info(self, file_type, file_path, file_object):
        """Show detailed file information dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QDialogButtonBox

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"{file_type} File Information")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        # File path
        path_label = QLabel(f"<b>File Path:</b> {file_path}")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)

        # File details
        details_text = QTextEdit()
        details_text.setReadOnly(True)

        # Format details based on file type
        if file_type == "IMG" and file_object:
            details = f"""
    File Format: {file_object.version.name if hasattr(file_object, 'version') else 'Unknown'}
    Total Entries: {len(file_object.entries) if hasattr(file_object, 'entries') else 0}
    File Size: {os.path.getsize(file_path) if os.path.exists(file_path) else 0} bytes
    Creation Date: {os.path.getctime(file_path) if os.path.exists(file_path) else 'Unknown'}
            """
            details_text.setPlainText(details)

        layout.addWidget(details_text)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.exec()

    def _show_file_properties(self, file_type, file_path, file_object):
        """Show file properties dialog"""
        from PyQt6.QtWidgets import QMessageBox

        if os.path.exists(file_path):
            stat = os.stat(file_path)
            size = stat.st_size
            modified = stat.st_mtime

            from datetime import datetime
            mod_time = datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M:%S")

            QMessageBox.information(
                self.main_window,
                f"{file_type} File Properties",
                f"File: {os.path.basename(file_path)}\n"
                f"Path: {file_path}\n"
                f"Size: {size:,} bytes\n"
                f"Modified: {mod_time}\n"
                f"Type: {file_type} Archive"
            )
        else:
            QMessageBox.warning(self.main_window, "File Not Found", f"File not found: {file_path}")

    # Update table context menu to include file info
    def setup_table_context_menu(self):
        """Setup context menu for the table"""
        if hasattr(self, 'table'):
            self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self._show_table_context_menu)

    def _show_table_context_menu(self, position):
        """Show context menu for table"""
        if hasattr(self, 'table'):
            # Get current file info
            current_type = self._get_current_file_type()
            current_file = self._get_current_file()

            if current_file:
                menu = self.create_file_info_popup(current_type, current_file.get('path', ''), current_file.get('object'))
                menu.exec(self.table.mapToGlobal(position))

    def _get_current_file_type(self):
        """Get currently selected file type"""
        if hasattr(self, 'main_type_tabs'):
            index = self.main_type_tabs.currentIndex()
            return ["IMG", "COL", "TXD"][index] if 0 <= index < 3 else "IMG"
        return "IMG"

    def _get_current_file(self):
        """Get current file information"""
        # Return current file info from main window
        if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
            return {
                'path': self.main_window.current_img.file_path,
                'object': self.main_window.current_img
            }
        return None

    def button_connections(self):
        """all button connections"""
        try:
            from PyQt6.QtWidgets import QPushButton

            # Find all buttons and fix their connections
            all_buttons = self.findChildren(QPushButton)

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

            return True

        except Exception as e:
            self.log_message(f"❌ Error fixing buttons: {str(e)}")
            return False

    def update_info_labels(self, file_name="No file loaded", entry_count=0, file_size=0, format_version="Unknown"):
        """Update information bar labels"""
        if hasattr(self, 'file_name_label'):
            self.file_name_label.setText(f"File: {file_name}")
        if hasattr(self, 'entry_count_label'):
            self.entry_count_label.setText(f"Entries: {entry_count}")
        if hasattr(self, 'file_size_label'):
            self.file_size_label.setText(f"Size: {file_size} bytes")
        if hasattr(self, 'format_version_label'):
            self.format_version_label.setText(f"Format: {format_version}")

    def enable_buttons_by_context(self, img_loaded=False, entries_selected=False):
        """Enable/disable buttons based on context"""
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
                elif button_action in ["import", "import_via", "update_list", "select_all", "sel_inverse", "sort"]:
                    btn.setEnabled(img_loaded)

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

    def _update_ui_for_loaded_col(self):
        """Update UI when COL file is loaded - FIXED to use col_tab_integration"""
        try:
            if hasattr(self, 'load_col_file_safely'):
                # Use the method provided by col_tab_integration
                from components.col_tabs_functions import update_ui_for_loaded_col
                update_ui_for_loaded_col(self)
            else:
                # Fallback implementation
                self.log_message("⚠️ COL Fintegration not fully loaded, using fallback")
                if hasattr(self, 'gui_layout') and self.gui_layout.table:
                    self.gui_layout.table.setRowCount(1)
                    col_name = os.path.basename(self.current_col.file_path) if hasattr(self.current_col, 'file_path') else "Unknown"
                    items = [
                        (col_name, "COL", "Unknown", "0x0", "COL", "None", "Loaded")
                    ]

                    for row, item_data in enumerate(items):
                        for col, value in enumerate(item_data):
                            item = QTableWidgetItem(str(value))
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                            self.gui_layout.table.setItem(row, col, item)

                # Update status
                if hasattr(self, 'statusBar') and self.statusBar():
                    self.statusBar().showMessage(f"COL file loaded: {col_name}")

        except Exception as e:
            self.log_message(f"❌ Error updating UI for COL: {str(e)}")

    def handle_action(self, action_name):
        """Handle unified action signals - UPDATED with missing methods"""
        try:
            action_map = {
                # File operations
                'create_new_img': self.create_new_img,
                'open_img_file': self.open_img_file,
                'reload_ing': self.reload_table,
                #placeholder button
                'close_img_file': self.close_img_file,
                'close_all': self.close_manager.close_all_tabs if hasattr(self, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'close_all_img': self.close_all_img,
                # IMG operations
                'rebuild_img': self.rebuild_img,
                'rebuild_img_as': self.rebuild_img_as,
                'rebuild_all_img': self.rebuild_all_img,
                'merge_img': self.merge_img,
                'split_img': self.split_img,
                'convert_img_format': self.convert_img_format,
                # Entry operations
                'import_files': self.import_files,
                'import_via': self.import_files_via,
                'refresh_table': self.refresh_table,
                'export_selected': self.export_selected,
                'export_via': self.export_selected_via,
                'Quick_export':self.quick_export_selected,
                'remove_selected': self.remove_selected,
                'remove_via': self.remove_via_entries,
                'select_all_entries': self.select_all_entries,
                'dump': self.dump_entries,
                #other
                'rename': self.rename_selected,
                'replace': self.replace_selected,
                'select': self.select,
                'select_all': self.select_all_entries,
                'Inverse': self.select_inverse,
                'Sort': self.sort_entries,
                'Pin selected': self.pin_selected_entries,

                # System
                #'show_search_dialog': self.show_search_dialog,
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
                'new_img': self.create_new_img,
                'open_img_file': self.open_img_dialog,
                'reload_ing': self.reload_table,
                #placeholder button
                'close_img': self.close_manager.close_img_file if hasattr(self, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'exit': self.close,
                'close_all': self.close_manager.close_all_tabs if hasattr(self, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'close_all_img': self.close_all_img,
                # IMG operations
                'rebuild_img': self.rebuild_img,
                'rebuild_img_as': self.rebuild_img_as,
                'img_rebuild': self.rebuild_img,
                'img_rebuild_as': self.rebuild_img_as,
                'rebuild_all_img': self.rebuild_all_img,
                'merge_img': self.merge_img,
                'split_img': self.split_img,
                'convert_img_format': self.convert_img_format,
                # Entry operations
                'entry_import': self.import_files,
                'import_files': self.import_files,
                'import_via': self.import_files_via,
                'refresh_table': self.refresh_table,
                'export_selected': self.export_selected,
                'entry_export': self.export_selected,
                'export_via': self.export_selected_via,
                'Quick_export':self.quick_export_selected,
                'entry_remove': self.remove_selected,
                'remove_selected': self.remove_selected,
                'remove_via': self.remove_via_entries,
                'select_all_entries': self.select_all_entries,
                'dump': self.dump_entries,
                #other
                #'find': self.show_search_dialog,
                'rename': self.rename_selected,
                'replace': self.replace_selected,
                'select': self.select,
                'select_all': self.select_all_entries,
                'Inverse': self.select_inverse,
                'Sort': self.sort_entries,
                'Pin selected': self.pin_selected_entries,
            }

            if hasattr(self, 'menu_bar_system') and hasattr(self.menu_bar_system, 'set_callbacks'):
                self.menu_bar_system.set_callbacks(menu_callbacks)

            self.log_message("✅ Menu connections established (unified file loading)")

        except Exception as e:
            self.log_message(f"❌ Menu connection error: {str(e)}")

# Export classes
__all__ = [
    'GUIBackend',
    'ButtonDisplayMode'
]
