#this belongs in gui/ gui_layout.py - Version: 26
# X-Seti - JULY29 2025 - Img Factory 1.5 - GUI Layout Module

import os
import re
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QHeaderView, QAbstractItemView,
    QMenuBar, QStatusBar, QProgressBar, QTabWidget, QCheckBox, QSpinBox,
    QMessageBox, QSizePolicy, QButtonGroup, QListWidget, QListWidgetItem,
    QFormLayout, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QAction, QIcon, QShortcut, QKeySequence, QPalette, QTextCursor
from core.gui_search import ASearchDialog, SearchManager
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from components.img_creator import NewIMGDialog, IMGCreationThread
from components.ide_editor import open_ide_editor

#core
from core.impotr import import_files_function
from core.import_via import import_via_function
#from core.import_via import integrate_import_via_functions
from core.remove import remove_selected_function
from core.remove_via import integrate_remove_via_functions
from core.export import export_selected_function
# export_all_function, integrate_export_functions
from core.export_via import export_via_function
from core.quick_export import quick_export_function
from core.clean import integrate_clean_utilities
from core.rebuild import rebuild_current_img_native
from core.rebuild_all import rebuild_all_open_tabs
#from core.rebuild import rebuild_current_img #old function.
from core.dump import dump_all_function # dump_selected_function, integrate_dump_functions
from core.img_split import split_img, integrate_split_functions
from core.img_merger import merge_img_function
from core.convert import convert_img, convert_img_format
from core.rename import rename_entry
from core.reload import reload_current_file
from core.img_creator import create_new_img, detect_and_open_file, open_file_dialog, detect_file_type
from core.close import close_img_file, close_all_img, install_close_functions, setup_close_manager
from methods.colour_ui_for_loaded_img import integrate_color_ui_system
from gui.gui_context import open_col_editor_dialog

def edit_txd_file(main_window): #vers 2
    """Edit selected TXD file with TXD Editor"""
    try:
        entries_table = main_window.gui_layout.table
        selected_items = entries_table.selectedItems()
        if not selected_items:
            main_window.log_message("No TXD file selected")
            return

        row = selected_items[0].row()
        filename_item = entries_table.item(row, 0)
        filename = filename_item.text()

        if not filename.lower().endswith('.txd'):
            main_window.log_message("Selected file is not a TXD file")
            return

        from components.txd_editor import TXDEditor
        txd_editor = TXDEditor()
        txd_editor.show()
        main_window.log_message(f"TXD Editor opened for: {filename}")

    except Exception as e:
        main_window.log_message(f"Error opening TXD Editor: {e}")


class IMGFactoryGUILayout:
    """Handles the complete GUI layout for IMG Factory 1.5 with theme system"""
    
    def __init__(self, main_window): #vers 2
        """Initialize GUI layout with theme-controlled components"""
        self.main_window = main_window
        self.table = None
        self.log = None
        self.main_splitter = None
        self.img_buttons = []
        self.entry_buttons = []
        self.options_buttons = []

        # Status bar components
        self.status_bar = None
        self.status_label = None
        self.progress_bar = None
        self.img_info_label = None

        # Tab-related components
        self.main_type_tabs = None
        self.tab_widget = None
        self.left_vertical_splitter = None
        self.status_window = None
        self.info_bar = None
        self.tearoff_button = None

        # Initialize method_mappings FIRST before buttons
        self.method_mappings = self._create_method_mappings()


    def _create_method_mappings(self): #vers 5
        """Create centralized method mappings for all buttons"""
        method_mappings = {
            # IMG/COL Operations
            'create_new_img': lambda: create_new_img(self.main_window),
            'open_img_file': lambda: open_file_dialog(self.main_window),
            'reload_table': lambda: reload_current_file(self.main_window),
            'useless_button': lambda: self._safe_log("🎯 useless_button!"),
            'close_img_file': lambda: close_img_file(self.main_window),
            'close_all_img': lambda: close_all_img(self.main_window),
            'rebuild_img': lambda: rebuild_current_img_native(self.main_window),
            #'rebuild_all_img': lambda: integrate_batch_rebuild_functions(self.main_window),
            'rebuild_all_img': lambda: rebuild_all_open_tabs(self.main_window),
            'save_img_entry': lambda: save_img_entry_function(self.main_window),
            'merge_img': lambda: merge_img_function(self.main_window),
            'split_img': lambda: split_img(self.main_window),
            'convert_img_format': lambda: convert_img_format(self.main_window),

            # Import methods
            'import_files': lambda: import_files_function(self.main_window),
            'import_files_via': lambda: import_via_function(self.main_window),
            'refresh_table': lambda: self._log_missing_method('refresh_table'),

            # Export methods
            'export_selected': lambda: self.main_window.export_selected(),
            'export_selected_via': lambda: self.main_window.export_via(),
            'quick_export_selected': lambda: self.main_window.quick_export(),
            'dump_entries': lambda: self.main_window.dump_all(),

            # Remove methods
            'remove_selected': lambda: remove_selected_function(self.main_window),
            'remove_via_entries': lambda: remove_via_entries_function(self.main_window),

            # Selection methods
            'select_all_entries': lambda: self._log_missing_method('select_all_entries'),
            'select_inverse': lambda: self._log_missing_method('select_inverse'),
            'sort_entries': lambda: self._log_missing_method('sort_entries'),
            'pin_selected_entries': lambda: self._log_missing_method('pin_selected_entries'),

            # Edit methods
            'rename_selected': lambda: self._log_missing_method('rename_selected'),
            'replace_selected': lambda: self._log_missing_method('replace_selected'),

            # Editor methods
            'edit_col_file': lambda: open_col_editor_dialog(self.main_window),
            'edit_txd_file': lambda: edit_txd_file(self.main_window),
            'edit_dff_file': lambda: self._log_missing_method('edit_dff_file'),
            'edit_ipf_file': lambda: self._log_missing_method('edit_ipf_file'),
            'edit_ide_file': lambda: open_ide_editor(self.main_window),
            'edit_ipl_file': lambda: self._log_missing_method('edit_ipl_file'),
            'edit_dat_file': lambda: self._log_missing_method('edit_dat_file'),
            'edit_zones_cull': lambda: self._log_missing_method('edit_zones_cull'),
            'edit_weap_file': lambda: self._log_missing_method('edit_weap_file'),
            'edit_vehi_file': lambda: self._log_missing_method('edit_vehi_file'),
            'edit_peds_file': lambda: self._log_missing_method('edit_peds_file'),
            'edit_radar_map': lambda: self._log_missing_method('edit_radar_map'),
            'edit_paths_map': lambda: self._log_missing_method('edit_paths_map'),
            'edit_waterpro': lambda: self._log_missing_method('edit_waterpro'),
            'edit_weather': lambda: self._log_missing_method('edit_weather'),
            'edit_2dfx': lambda: self._log_missing_method('edit_2dfx'),
            'edit_objects': lambda: self._log_missing_method('edit_objects'),
            'editscm': lambda: self._log_missing_method('editscm'),
            'editgxt': lambda: self._log_missing_method('editgxt'),
            'editmenu': lambda: self._log_missing_method('editmenu'),
        }

        print(f"✅ Method mappings created: {len(method_mappings)} methods")
        return method_mappings


    def _log_missing_method(self, method_name): #vers 1
        """Log missing method - unified placeholder"""
        if hasattr(self.main_window, 'log_message') and hasattr(self.main_window, 'gui_layout'):
            self.main_window.log_message(f"⚠️ Method '{method_name}' not yet implemented")
        else:
            print(f"⚠️ Method '{method_name}' not yet implemented")



    def _get_button_theme_template(self, theme_name="default"): #vers 2
        """Get button color templates based on theme"""
        if self._is_dark_theme():
            return {
                # Dark Theme Button Colors
                'create_action': '#3D5A5A',     # Dark teal for create/new actions
                'open_action': '#3D4A5F',       # Dark blue for open/load actions
                'reload_action': '#2D4A3A',     # Dark green for refresh/reload
                'close_action': '#5A4A3D',      # Dark orange for close actions
                'build_action': '#2D4A3A',      # Dark mint for build/rebuild
                'save_action': '#4A2D4A',       # Dark purple for save actions
                'merge_action': '#3A2D4A',      # Dark violet for merge/split
                'convert_action': '#4A4A2D',    # Dark yellow for convert
                'import_action': '#2D4A4F',     # Dark cyan for import
                'export_action': '#2D4A3A',     # Dark emerald for export
                'remove_action': '#4A2D2D',     # Dark red for remove/delete
                'edit_action': '#4A3A2D',       # Dark amber for edit actions
                'select_action': '#3A4A2D',     # Dark lime for select actions
                'editor_col': '#2D3A4F',        # Dark blue for COL editor
                'editor_txd': '#4A2D4A',        # Dark magenta for TXD editor
                'editor_dff': '#2D4A4F',        # Dark cyan for DFF editor
                'editor_data': '#3A4A2D',       # Dark olive for data editors
                'editor_map': '#4A2D4A',        # Dark purple for map editors
                'editor_vehicle': '#2D4A3A',    # Dark teal for vehicle editors
                'editor_script': '#4A3A2D',     # Dark gold for script editors
                'placeholder': '#2A2A2A',       # Dark gray for spacers
            }
        else:
            return {
                # Light Theme Button Colors
                'create_action': '#EEFAFA',     # Light teal for create/new actions
                'open_action': '#E3F2FD',       # Light blue for open/load actions
                'reload_action': '#E8F5E8',     # Light green for refresh/reload
                'close_action': '#FFF3E0',      # Light orange for close actions
                'build_action': '#E8F5E8',      # Light mint for build/rebuild
                'save_action': '#F8BBD9',       # Light pink for save actions
                'merge_action': '#F3E5F5',      # Light violet for merge/split
                'convert_action': '#FFF8E1',    # Light yellow for convert
                'import_action': '#E1F5FE',     # Light cyan for import
                'export_action': '#E8F5E8',     # Light emerald for export
                'remove_action': '#FFEBEE',     # Light red for remove/delete
                'edit_action': '#FFF8E1',       # Light amber for edit actions
                'select_action': '#F1F8E9',     # Light lime for select actions
                'editor_col': '#E3F2FD',        # Light blue for COL editor
                'editor_txd': '#F8BBD9',        # Light pink for TXD editor
                'editor_dff': '#E1F5FE',        # Light cyan for DFF editor
                'editor_data': '#D3F2AD',       # Light lime for data editors
                'editor_map': '#F8BBD9',        # Light pink for map editors
                'editor_vehicle': '#E3F2BD',    # Light olive for vehicle editors
                'editor_script': '#FFD0BD',     # Light peach for script editors
                'placeholder': '#FEFEFE',       # Light gray for spacers
            }


    def _get_img_buttons_data(self): #vers 3
        """Get IMG buttons data with theme colors"""
        colors = self._get_button_theme_template()
        return [
            ("Create", "new", "document-new", colors['create_action'], "create_new_img"),
            ("Open", "open", "document-open", colors['open_action'], "open_img_file"),
            ("Reload", "reload", "document-reload", colors['reload_action'], "reload_table"),
            ("     ", "space", "placeholder", colors['placeholder'], "useless_button"),
            ("Close", "close", "window-close", colors['close_action'], "close_img_file"),
            ("Close All", "close_all", "edit-clear", colors['close_action'], "close_all_img"),
            ("Rebuild", "rebuild", "view-rebuild", colors['build_action'], "rebuild_img"),
            ("Rebuild All", "rebuild_all", "document-save", colors['build_action'], "rebuild_all_img"),
            ("Save Entry", "save_entry", "document-save-entry", colors['save_action'], "save_img_entry"),
            ("Merge", "merge", "document-merge", colors['merge_action'], "merge_img"),
            ("Split via", "split", "edit-cut", colors['merge_action'], "split_img"),
            ("Convert", "convert", "transform", colors['convert_action'], "convert_img_format"),
        ]

    def _get_entry_buttons_data(self): #vers 3
        """Get Entry buttons data with theme colors"""
        colors = self._get_button_theme_template()
        return [
            ("Import", "import", "document-import", colors['import_action'], "import_files"),
            ("Import via", "import_via", "document-import", colors['import_action'], "import_files_via"),
            ("Refresh", "update", "view-refresh", colors['reload_action'], "refresh_table"),
            ("Export", "export", "document-export", colors['export_action'], "export_selected"),
            ("Export via", "export_via", "document-export", colors['export_action'], "export_selected_via"),
            ("Dump", "dump", "document-dump", colors['merge_action'], "dump_entries"),
            #("Quick Exp", "quick_export", "document-send", colors['export_action'], "quick_export_selected"),
            ("Remove", "remove", "edit-delete", colors['remove_action'], "remove_selected"),
            ("Remove via", "remove_via", "document-remvia", colors['remove_action'], "remove_via_entries"),
            ("Replace", "replace", "edit-copy", colors['edit_action'], "replace_selected"),
            ("Rename", "rename", "edit-rename", colors['edit_action'], "rename_selected"),
            ("Select All", "select_all", "edit-select-all", colors['select_action'], "select_all_entries"),
            ("Inverse", "sel_inverse", "edit-select", colors['select_action'], "select_inverse"),
            ("Sort via", "sort", "view-sort", colors['select_action'], "sort_entries"),
            ("Pin selected", "pin_selected", "pin", colors['select_action'], "pin_selected_entries"),
        ]

    def _get_options_buttons_data(self): #vers 3
        """Get Options buttons data with theme colors"""
        colors = self._get_button_theme_template()
        return [
            ("Col Edit", "col_edit", "col-edit", colors['editor_col'], "edit_col_file"),
            ("Txd Edit", "txd_edit", "txd-edit", colors['editor_txd'], "edit_txd_file"),
            ("Dff Edit", "dff_edit", "dff-edit", colors['editor_dff'], "edit_dff_file"),
            ("Ipf Edit", "ipf_edit", "ipf-edit", colors['editor_data'], "edit_ipf_file"),
            ("IDE Edit", "ide_edit", "ide-edit", colors['editor_data'], "edit_ide_file"),
            ("IPL Edit", "ipl_edit", "ipl-edit", colors['editor_data'], "edit_ipl_file"),
            ("Dat Edit", "dat_edit", "dat-edit", colors['editor_data'], "edit_dat_file"),
            ("Zons Cull Ed", "zones_cull", "zones-cull", colors['editor_data'], "edit_zones_cull"),
            ("Weap Edit", "weap_edit", "weap-edit", colors['editor_vehicle'], "edit_weap_file"),
            ("Vehi Edit", "vehi_edit", "vehi-edit", colors['editor_vehicle'], "edit_vehi_file"),
            ("Peds Edit", "peds_edit", "peds-edit", colors['editor_vehicle'], "edit_peds_file"),
            ("Radar Map", "radar_map", "radar-map", colors['editor_map'], "edit_radar_map"),
            ("Paths Map", "paths_map", "paths-map", colors['editor_map'], "edit_paths_map"),
            ("Waterpro", "timecyc", "timecyc", colors['editor_data'], "edit_waterpro"),
            ("Weather", "timecyc", "timecyc", colors['editor_data'], "edit_weather"),
            ("Handling", "handling", "handling", colors['editor_vehicle'], "edit_handling"),
            ("Objects", "ojs_breakble", "ojs-breakble", colors['editor_data'], "edit_objects"),
            ("SCM code", "scm_code", "scm-code", colors['editor_script'], "editscm"),
            ("GXT font", "gxt_font", "gxt-font", colors['editor_script'], "editgxt"),
            ("Menu Edit", "menu_font", "menu-font", colors['editor_script'], "editmenu"),
        ]


    def _is_dark_theme(self): #vers 2
        """Detect if the application is using a dark theme"""
        try:
            # Method 1: Check if main window has theme property or setting
            if hasattr(self.main_window, 'current_theme'):
                return 'dark' in self.main_window.current_theme.lower()
            
            # Method 2: Check app_settings for theme
            if hasattr(self.main_window, 'app_settings'):
                current_settings = getattr(self.main_window.app_settings, 'current_settings', {})
                theme_name = current_settings.get('theme', '').lower()
                if theme_name:
                    return 'dark' in theme_name
            
            # Method 3: Check if you have a theme_mode property
            if hasattr(self, 'theme_mode'):
                return self.theme_mode == 'dark'

            # Method 4: Check application palette as fallback
            from PyQt6.QtWidgets import QApplication
            palette = QApplication.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            # If window background is darker, assume dark theme
            return window_color.lightness() < 128

        except Exception as e:
            # Fallback to light theme if detection fails
            print(f"Theme detection failed: {e}, defaulting to light theme")
            return False


    def set_theme_mode(self, theme_name): #vers 2
        """Set the current theme mode and refresh all styling"""
        self.theme_mode = 'dark' if 'dark' in theme_name.lower() else 'light'
        print(f"Theme mode set to: {self.theme_mode}")
        
        # Force refresh all buttons with new theme colors
        self._refresh_all_buttons()
        
        # Apply all window themes
        self.apply_all_window_themes()


    def _setup_tearoff_button_for_tabs(self): #vers 1
        """Setup tearoff button in tab widget corner"""
        try:
            # Create tearoff button with square arrow icon
            self.tearoff_button = QPushButton("⧉")  # Square with arrow symbol
            self.tearoff_button.setFixedSize(24, 24)
            self.tearoff_button.setToolTip("Tear off tab widget to separate window")

            # Apply theme-aware styling
            self._apply_tearoff_button_theme()

            # Connect to tearoff handler
            self.tearoff_button.clicked.connect(self._handle_tab_widget_tearoff)

            # Set as corner widget on the right side of tabs
            self.tab_widget.setCornerWidget(self.tearoff_button, Qt.Corner.TopRightCorner)

            self.main_window.log_message("✅ Tearoff button added to tab widget corner")

        except Exception as e:
            self.main_window.log_message(f"❌ Error setting up tearoff button: {str(e)}")


    def _apply_tearoff_button_theme(self): #vers 1
        """Apply theme-aware styling to tearoff button"""
        if not self.tearoff_button:
            return

        is_dark = self._is_dark_theme()

        if is_dark:
            # Dark theme tearoff button
            button_style = """
                QPushButton {
                    border: 1px solid {border_color};
                    border-radius: 1px;
                    background-color: {button_bg};
                    color: {text_color};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: {hover_bg};
                    border: 1px solid {border_color};
                    color: {text_secondary};
                }
                QPushButton:pressed {
                    background-color: {pressed_bg};
                    border: 1px solid {border_color};
                    color: {text_primary};
                }
            """
        else:
            # Light theme tearoff button
            button_style = """
                QPushButton {
                    border: 1px solid {border_color};
                    border-radius: 1px;
                    background-color: {button_bg};
                    color: {text_color};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: {hover_bg};
                    border: 1px solid {border_color};
                    color: {text_secondary};
                }
                QPushButton:pressed {
                    background-color: {pressed_bg};
                    border: 1px solid {border_color};
                    color: {text_primary};
                }

            """

        self.tearoff_button.setStyleSheet(button_style)


    # FIXED TEAROFF METHODS

    def _handle_tab_widget_tearoff(self): #vers 2
        """Handle tearoff button click for tab widget - FIXED"""
        try:
            if not self.tab_widget:
                return

            # Check if already torn off
            if hasattr(self.tab_widget, 'is_torn_off') and self.tab_widget.is_torn_off:
                # Dock it back
                self._dock_tab_widget_back()
                return

            # Store original parent info BEFORE removing from layout
            original_parent = self.tab_widget.parent()
            original_layout = original_parent.layout() if original_parent else None

            if not original_parent or not original_layout:
                self.main_window.log_message("❌ Cannot tear off: no parent layout found")
                return

            # Store references on tab widget BEFORE manipulation
            self.tab_widget.original_parent = original_parent
            self.tab_widget.original_layout = original_layout

            # Import tearoff system
            try:
                from gui.tear_off import TearOffPanel
            except ImportError:
                self.main_window.log_message("❌ TearOffPanel not available")
                return

            # Create tearoff panel WITHOUT a layout initially
            panel_id = "file_tabs_panel"
            title = "File Tabs"
            tearoff_panel = TearOffPanel(panel_id, title, self.main_window)

            # Create layout for tearoff panel if it doesn't have one
            if not tearoff_panel.layout():
                tearoff_panel_layout = QVBoxLayout(tearoff_panel)
                tearoff_panel_layout.setContentsMargins(2, 2, 2, 2)
            else:
                tearoff_panel_layout = tearoff_panel.layout()

            # Remove tab widget from current parent layout
            original_layout.removeWidget(self.tab_widget)

            # Add tab widget to tearoff panel
            tearoff_panel_layout.addWidget(self.tab_widget)

            # Store tearoff panel reference
            self.tab_widget.tearoff_panel = tearoff_panel
            self.tab_widget.is_torn_off = True

            # Update button appearance
            self._update_tearoff_button_state(True)

            # Show tearoff panel
            tearoff_panel.show()
            tearoff_panel.raise_()

            # Position near cursor
            from PyQt6.QtGui import QCursor
            cursor_pos = QCursor.pos()
            tearoff_panel.move(cursor_pos.x() - 100, cursor_pos.y() - 50)

            self.main_window.log_message("🔗 Tab widget torn off to separate window")

        except Exception as e:
            self.main_window.log_message(f"❌ Error handling tab widget tearoff: {str(e)}")
            import traceback
            traceback.print_exc()

    def _dock_tab_widget_back(self): #vers 2
        """Dock torn off tab widget back to main window - FIXED"""
        try:
            # Check if actually torn off
            if not hasattr(self.tab_widget, 'is_torn_off') or not self.tab_widget.is_torn_off:
                self.main_window.log_message("⚠️ Tab widget is not torn off")
                return

            # Get stored references with safety checks
            original_parent = getattr(self.tab_widget, 'original_parent', None)
            original_layout = getattr(self.tab_widget, 'original_layout', None)
            tearoff_panel = getattr(self.tab_widget, 'tearoff_panel', None)

            # Validate we have the required references
            if not original_parent:
                self.main_window.log_message("❌ Cannot dock back: no original parent stored")
                return

            if not original_layout:
                self.main_window.log_message("❌ Cannot dock back: no original layout stored")
                return

            # Verify original parent still exists and has layout
            try:
                if original_parent.layout() != original_layout:
                    self.main_window.log_message("⚠️ Original layout changed, using current layout")
                    original_layout = original_parent.layout()
                    if not original_layout:
                        self.main_window.log_message("❌ Original parent no longer has a layout")
                        return
            except:
                self.main_window.log_message("❌ Original parent is no longer valid")
                return

            # Remove from tearoff panel first
            if tearoff_panel:
                try:
                    tearoff_panel_layout = tearoff_panel.layout()
                    if tearoff_panel_layout:
                        tearoff_panel_layout.removeWidget(self.tab_widget)
                    tearoff_panel.hide()
                    tearoff_panel.deleteLater()
                except Exception as e:
                    self.main_window.log_message(f"⚠️ Error cleaning up tearoff panel: {str(e)}")

            # Add back to original parent layout
            try:
                original_layout.addWidget(self.tab_widget)
            except Exception as e:
                self.main_window.log_message(f"❌ Error adding back to original layout: {str(e)}")
                return

            # Clean up references
            try:
                delattr(self.tab_widget, 'original_parent')
                delattr(self.tab_widget, 'original_layout')
                delattr(self.tab_widget, 'tearoff_panel')
                delattr(self.tab_widget, 'is_torn_off')
            except:
                pass  # Attributes might not exist

            # Update button appearance
            self._update_tearoff_button_state(False)

            # Force widget to show and update
            self.tab_widget.show()
            self.tab_widget.update()

            self.main_window.log_message("🔗 Tab widget docked back to main window")

        except Exception as e:
            self.main_window.log_message(f"❌ Error docking tab widget back: {str(e)}")
            import traceback
            traceback.print_exc()

    def _update_tearoff_button_state(self, is_torn_off): #vers 2
        """Update tearoff button appearance based on state - SAFER VERSION"""
        try:
            if not hasattr(self, 'tearoff_button') or not self.tearoff_button:
                return

            if is_torn_off:
                self.tearoff_button.setText("⧈")  # Different icon when torn off
                self.tearoff_button.setToolTip("Dock tab widget back to main window")
            else:
                self.tearoff_button.setText("⧉")  # Original icon when docked
                self.tearoff_button.setToolTip("Tear off tab widget to separate window")

            # Reapply theme styling to ensure consistency
            if hasattr(self, '_apply_tearoff_button_theme'):
                self._apply_tearoff_button_theme()

        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ Error updating tearoff button state: {str(e)}")
            else:
                print(f"⚠️ Error updating tearoff button state: {str(e)}")


    def _refresh_all_buttons(self): #vers 4
        """Refresh all buttons with current theme colors"""
        try:
            # Get new theme colors
            img_colors = self._get_img_buttons_data()
            entry_colors = self._get_entry_buttons_data() 
            options_colors = self._get_options_buttons_data()
            
            # Update IMG buttons
            if hasattr(self, 'img_buttons'):
                for i, btn in enumerate(self.img_buttons):
                    if i < len(img_colors):
                        label, action_type, icon, color, method_name = img_colors[i]
                        self._update_button_theme(btn, color)
            
            # Update Entry buttons
            if hasattr(self, 'entry_buttons'):
                for i, btn in enumerate(self.entry_buttons):
                    if i < len(entry_colors):
                        label, action_type, icon, color, method_name = entry_colors[i]
                        self._update_button_theme(btn, color)
                        
            # Update Options buttons
            if hasattr(self, 'options_buttons'):
                for i, btn in enumerate(self.options_buttons):
                    if i < len(options_colors):
                        label, action_type, icon, color, method_name = options_colors[i]
                        self._update_button_theme(btn, color)
                        
            print(f"✅ Refreshed {len(self.img_buttons + self.entry_buttons + self.options_buttons)} buttons for theme")
                        
        except Exception as e:
            print(f"❌ Error refreshing buttons: {e}")

    def add_txd_editor_button(self): #vers 3
        """Add TXD Editor button to toolbar"""
        if hasattr(self.main_window, 'button_panel'):
            txd_button = QPushButton("TXD Editor")
            txd_button.clicked.connect(self.launch_txd_editor)
            txd_button.setToolTip("Open TXD Texture Editor")
            self.main_window.button_panel.addWidget(txd_button)

    def launch_txd_editor(self): #vers 1
        """Launch TXD Editor"""
        try:
            if not self.main_window.txd_editor:
                from components.txd_editor import TXDEditor
                self.main_window.txd_editor = TXDEditor()
            self.main_window.txd_editor.show()
            self.main_window.txd_editor.raise_()
        except Exception as e:
            self.main_window.log_message(f"Failed to launch TXD Editor: {e}")

    def _update_button_theme(self, btn, bg_color): #vers 2
        """Update a single button's theme styling"""
        try:
            is_dark_theme = self._is_dark_theme()

            if is_dark_theme:
                # Dark theme styling
                button_bg = self._darken_color(bg_color, 0.4)
                border_color = self._lighten_color(bg_color, 1.3)
                text_color = self._lighten_color(bg_color, 1.5)
                hover_bg = self._darken_color(bg_color, 0.3)
                hover_border = self._lighten_color(bg_color, 1.4)
                pressed_bg = self._darken_color(bg_color, 0.5)
            else:
                # Light theme styling
                button_bg = bg_color
                border_color = self._darken_color(bg_color, 0.6)
                text_color = self._darken_color(bg_color, 1.8)
                hover_bg = self._darken_color(bg_color, 0.9)
                hover_border = self._darken_color(bg_color, 0.5)
                pressed_bg = self._darken_color(bg_color, 0.8)


            # Apply updated styling
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {button_bg};
                    border: 1px solid {border_color};
                    border-radius: 3px;
                    padding: 2px 6px;
                    font-size: 8pt;
                    font-weight: bold;
                    color: {text_color};
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                    border: 1px solid {hover_border};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_bg};
                }}
            """)
        except Exception as e:
            print(f"❌ Error updating button theme: {e}")


    def create_pastel_button(self, label, action_type, icon, bg_color, method_name): #vers 3
        """Create a button with pastel coloring that adapts to light/dark themes"""
        btn = QPushButton(label)
        btn.setMaximumHeight(22)
        btn.setMinimumHeight(20)

        # Detect if we're using a dark theme
        is_dark_theme = self._is_dark_theme()

        if is_dark_theme:
            # Dark theme: darker pastel background, lighter edges, light text
            button_bg = self._darken_color(bg_color, 0.4)  # Much darker pastel
            border_color = self._lighten_color(bg_color, 1.3)  # Light border
            text_color = self._lighten_color(bg_color, 1.5)   # Light text
            hover_bg = self._darken_color(bg_color, 0.3)      # Slightly lighter on hover
            hover_border = self._lighten_color(bg_color, 1.4)  # Even lighter border on hover
            pressed_bg = self._darken_color(bg_color, 0.5)    # Darker when pressed
        else:
            # Light theme: light pastel background, dark edges, dark text
            button_bg = bg_color  # Original pastel color
            border_color = self._darken_color(bg_color, 0.6)  # Dark border
            text_color = self._darken_color(bg_color, 1.8)    # Dark text
            hover_bg = self._darken_color(bg_color, 0.9)      # Slightly darker on hover
            hover_border = self._darken_color(bg_color, 0.5)  # Darker border on hover
            pressed_bg = self._darken_color(bg_color, 0.8)    # Darker when pressed

        # Apply theme-aware styling
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_bg};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 8pt;
                font-weight: bold;
                color: {text_color};
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                border: 1px solid {hover_border};
            }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
            }}
        """)

        # Set action type property
        btn.setProperty("action-type", action_type)

        # Connect to method_mappings
        try:
            if method_name in self.method_mappings:
                btn.clicked.connect(self.method_mappings[method_name])
                if hasattr(self.main_window, 'gui_layout'):
                    print(f"✅ Connected '{label}' to method_mappings[{method_name}]")
            else:
                btn.clicked.connect(lambda: self._safe_log(f"⚠️ Method '{method_name}' not in method_mappings"))
                if hasattr(self.main_window, 'gui_layout'):
                    print(f"⚠️ Method '{method_name}' not found in method_mappings for '{label}'")
        except Exception as e:
            if hasattr(self.main_window, 'gui_layout'):
                print(f"❌ Error connecting button '{label}': {e}")
            btn.clicked.connect(lambda: self._safe_log(f"Button '{label}' connection error"))

        return btn


    def _lighten_color(self, color, factor): #vers 2
        """Lighten a hex color by factor (>1.0 lightens, <1.0 darkens)"""
        try:
            if not color.startswith('#'):
                return color
            
            color = color.lstrip('#')
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
            # Lighten by moving towards white
            r = min(255, int(r + (255 - r) * (factor - 1.0)))
            g = min(255, int(g + (255 - g) * (factor - 1.0)))
            b = min(255, int(b + (255 - b) * (factor - 1.0)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color


    def _darken_color(self, color, factor): #vers 2
        """Darken a hex color by factor (0.0-1.0, where 0.8 = 20% darker)"""
        try:
            if not color.startswith('#'):
                return color
                
            color = color.lstrip('#')
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
            # Darken by multiplying by factor
            r = max(0, int(r * factor))
            g = max(0, int(g * factor))
            b = max(0, int(b * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color


    def _get_short_text(self, label): #vers 1
        """Get short text for button"""
        short_map = {
            "Create": "New", "Open": "Open", "Reload": "Reload", "     ": " ",
            "Close": "Close", "Close All": "Close A", "Rebuild": "Rebld",
            "Rebuild All": "Rebld Al", "Save Entry": "Save", "Merge": "Merge",
            "Split via": "Split", "Convert": "Conv", "Import": "Imp",
            "Import via": "Imp via", "Refresh": "Refresh", "Export": "Exp",
            "Export via": "Exp via", "Quick Exp": "Q Exp", "Remove": "Rem",
            "Remove via": "Rem via", "Dump": "Dump", "Pin selected": "Pin",
            "Rename": "Rename", "Replace": "Replace", "Select All": "Select",
            "Inverse": "Inverse", "Sort via": "Sort", "Col Edit": "Col Edit",
            "Txd Edit": "Txd Edit", "Dff Edit": "Dff Edit", "Ipf Edit": "Ipf Edit",
            "IDE Edit": "IDE Edit", "IPL Edit": "IPL Edit", "Dat Edit": "Dat Edit",
            "Zons Cull Ed": "Zons Cull", "Weap Edit": "Weap Edit", "Vehi Edit": "Vehi Edit",
            "Peds Edit": "Peds Edit", "Radar Map": "Radar Map", "Paths Map": "Paths Map",
            "Waterpro": "Waterpro", "Weather": "Weather", "Handling": "Handling",
            "Objects": "Objects", "SCM code": "SCM Code", "GXT font": "GXT Edit",
            "Menu Edit": "Menu Ed",
        }
        return short_map.get(label, label)


    def create_main_ui_with_splitters(self, main_layout): #vers 3
        """Create the main UI with correct 3-section layout"""
        # Create main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - vertical layout with 3 sections
        left_panel = self._create_left_three_section_panel()
        
        # Right side - control buttons with pastel colors
        right_panel = self.create_right_panel_with_pastel_buttons()
        
        # Add panels to splitter
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(right_panel)
        
        # Set splitter proportions and force constraints
        self.main_splitter.setSizes([1000, 280])  # Fixed right panel to 280px
        
        # Add size constraints to force the right panel width
        right_panel.setMaximumWidth(280)  # Fixed at 280px
        right_panel.setMinimumWidth(280)  # Fixed at 280px
        
        # Style the main horizontal splitter handle with theme colors
        self._apply_main_splitter_theme()
        
        # Prevent panels from collapsing completely
        self.main_splitter.setCollapsible(0, False)  # Left panel
        self.main_splitter.setCollapsible(1, False)  # Right panel
        
        # Add splitter to main layout
        main_layout.addWidget(self.main_splitter)


    def _create_left_three_section_panel(self): #vers 3
        """Create left panel with 3 sections: File Window, Status Window"""
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(3, 3, 3, 3)
        left_layout.setSpacing(0)  # No spacing - splitter handles this

        # Create vertical splitter for the sections
        self.left_vertical_splitter = QSplitter(Qt.Orientation.Vertical)

        # 1. MIDDLE: File Window (table with sub-tabs)
        file_window = self._create_file_window()
        self.left_vertical_splitter.addWidget(file_window)

        # 2. BOTTOM: Status Window (log and status)
        status_window = self.create_status_window()
        self.left_vertical_splitter.addWidget(status_window)

        # Set section proportions: File(760px), Status(200px)
        self.left_vertical_splitter.setSizes([760, 200])

        # Prevent sections from collapsing completely
        self.left_vertical_splitter.setCollapsible(0, True)  # File window
        self.left_vertical_splitter.setCollapsible(1, True)  # Status window

        # Apply theme styling to vertical splitter
        self._apply_vertical_splitter_theme()

        left_layout.addWidget(self.left_vertical_splitter)
        return left_container


    def _create_file_window(self): #vers 3
        """Create file window with tabs for different views"""
        file_window = QWidget()
        file_layout = QVBoxLayout(file_window)
        file_layout.setContentsMargins(5, 5, 5, 5)
        file_layout.setSpacing(3)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: File Entries (main table)
        entries_tab = QWidget()
        entries_layout = QVBoxLayout(entries_tab)
        entries_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Num", "Name", "Extension", "Size", "Hash", "Hex", "Version", "Compression", "Status"
        ])
        
        # Table configuration
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSortingEnabled(True)
        
        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Num
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Extension
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Hash
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Hex Value
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Version
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Compression
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)  # Status
        
        # Apply theme styling to table
        self._apply_table_theme_styling()
        
        entries_layout.addWidget(self.table)
        self.tab_widget.addTab(entries_tab, "File Entries")
        

        # Tab 2: Directory Tree (placeholder for integration)
        tree_tab = QWidget()
        tree_layout = QVBoxLayout(tree_tab)
        tree_layout.setContentsMargins(0, 0, 0, 0)

        # Placeholder content - will be replaced by integration
        placeholder_label = QLabel("🌳 Directory Tree")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("font-size: 14px; color: #888; font-style: italic;")
        tree_layout.addWidget(placeholder_label)

        info_label = QLabel("Directory tree will appear here after integration.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #666; font-size: 12px;")
        tree_layout.addWidget(info_label)

        tree_layout.addStretch()

        # Add the tab to the widget
        self.tab_widget.addTab(tree_tab, "Directory Tree")
        
        # Tab 3: Search Results (future enhancement)
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        search_layout.setContentsMargins(0, 0, 0, 0)

        search_placeholder = QLabel("Search results will be displayed here")
        search_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_placeholder.setStyleSheet("font-style: italic;")
        search_layout.addWidget(search_placeholder)

        self.tab_widget.addTab(search_tab, "Search Results")

        # Apply theme styling to file window tabs
        self._apply_file_list_window_theme_styling()

        self._setup_tearoff_button_for_tabs()

        file_layout.addWidget(self.tab_widget)
        return file_window


    def create_right_panel_with_pastel_buttons(self): #vers 2
        """Create right panel with theme-controlled pastel buttons"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(6)

        # IMG Section with theme colors
        img_box = QGroupBox("IMG, COL, TXD Files")
        img_layout = QGridLayout()
        img_layout.setSpacing(2)
        
        # Use theme-controlled button data
        img_buttons_data = self._get_img_buttons_data()
        
        for i, (label, action_type, icon, color, method_name) in enumerate(img_buttons_data):
            btn = self.create_pastel_button(label, action_type, icon, color, method_name)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.img_buttons.append(btn)
            img_layout.addWidget(btn, i // 3, i % 3)
        
        img_box.setLayout(img_layout)
        right_layout.addWidget(img_box)

        # Entries Section with theme colors  
        entries_box = QGroupBox("File Entries")
        entries_layout = QGridLayout()
        entries_layout.setSpacing(2)
        
        # Use theme-controlled button data
        entry_buttons_data = self._get_entry_buttons_data()
        
        for i, (label, action_type, icon, color, method_name) in enumerate(entry_buttons_data):
            btn = self.create_pastel_button(label, action_type, icon, color, method_name)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.entry_buttons.append(btn)
            entries_layout.addWidget(btn, i // 3, i % 3)
        
        entries_box.setLayout(entries_layout)
        right_layout.addWidget(entries_box)

        # Options Section with theme colors
        options_box = QGroupBox("Editing Options")
        options_layout = QGridLayout()
        options_layout.setSpacing(2)
        
        # Use theme-controlled button data
        options_buttons_data = self._get_options_buttons_data()
        
        for i, (label, action_type, icon, color, method_name) in enumerate(options_buttons_data):
            btn = self.create_pastel_button(label, action_type, icon, color, method_name)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.options_buttons.append(btn)
            options_layout.addWidget(btn, i // 3, i % 3)
        
        options_box.setLayout(options_layout)
        right_layout.addWidget(options_box)

        # Filter Section
        filter_box = QGroupBox("Filter & Search")
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(4)

        # Filter controls
        filter_controls = QHBoxLayout()
        filter_combo = QComboBox()
        filter_combo.addItems(["All Files", "DFF Models", "TXD Textures", "COL Collision", "IFP Animations"])
        filter_controls.addWidget(QLabel("Type:"))
        filter_controls.addWidget(filter_combo)
        filter_layout.addLayout(filter_controls)

        search_controls = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search filename...")
        search_controls.addWidget(QLabel("Search:"))
        search_controls.addWidget(search_input)
        filter_layout.addLayout(search_controls)

        filter_box.setLayout(filter_layout)
        right_layout.addWidget(filter_box)

        # Add stretch to push everything up
        right_layout.addStretch()
        return right_panel


    def create_status_window(self): #vers 4
        """Create status window with log"""
        self.status_window = QWidget()
        status_layout = QVBoxLayout(self.status_window)
        status_layout.setContentsMargins(5, 5, 5, 5)
        status_layout.setSpacing(3)

        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("Activity Log")
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        title_layout.addWidget(title_label)

        # Status indicators
        title_layout.addStretch()

        # Status label
        self.status_label = QLabel("Ready")
        title_layout.addWidget(self.status_label)
        status_layout.addLayout(title_layout)

        # Log with scrollbars
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Activity log will appear here...")

        # Enable scrollbars for log
        self.log.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.log.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Apply theme styling to log
        self._apply_log_theme_styling()
        status_layout.addWidget(self.log)

        # Apply theme styling to status window
        self._apply_status_window_theme_styling()
        
        return self.status_window


    def _apply_table_theme_styling(self): #vers 5
        """Apply theme styling to the table widget"""
        theme_colors = self._get_theme_colors("default")

        # Use standard theme variables from app_settings_system.py
        panel_bg = theme_colors.get('panel_bg', '#ffffff')
        bg_secondary = theme_colors.get('bg_secondary', '#f8f9fa')
        bg_tertiary = theme_colors.get('bg_tertiary', '#e9ecef')
        border = theme_colors.get('border', '#dee2e6')
        text_primary = theme_colors.get('text_primary', '#000000')
        text_secondary = theme_colors.get('text_secondary', '#495057')
        accent_primary = theme_colors.get('accent_primary', '#1976d2')

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {bg_secondary};
                alternate-background-color: {bg_tertiary};
                border: 1px solid {border};
                border-radius: 3px;
                gridline-color: {border};
                color: {text_primary};
                font-size: 9pt;
            }}
            QTableWidget::item {{
                padding: 5px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {accent_primary};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {panel_bg};
                color: {text_secondary};
                padding: 5px;
                border: 1px solid {border};
                font-weight: bold;
                font-size: 9pt;
            }}
        """)


    def _apply_main_splitter_theme(self): #vers 6
        """Apply theme styling to main horizontal splitter"""
        theme_colors = self._get_theme_colors("default")

        # Extract variables FIRST
        bg_secondary = theme_colors.get('bg_secondary', '#f8f9fa')
        bg_primary = theme_colors.get('bg_primary', '#ffffff')
        bg_tertiary = theme_colors.get('bg_tertiary', '#e9ecef')

        self.main_splitter.setStyleSheet(f"""
            QSplitter::handle:horizontal {{
                background-color: {bg_secondary};
                border: 1px solid {bg_primary};
                border-left: 1px solid {bg_tertiary};
                width: 8px;
                margin: 2px 1px;
                border-radius: 3px;
            }}

            QSplitter::handle:horizontal:hover {{
                background-color: {bg_primary};
                border-color: {bg_tertiary};
            }}

            QSplitter::handle:horizontal:pressed {{
                background-color: {bg_tertiary};
            }}
        """)


    def _apply_vertical_splitter_theme(self): #vers 6
        """Apply theme styling to the vertical splitter"""
        theme_colors = self._get_theme_colors("default")

        # Extract variables FIRST
        bg_secondary = theme_colors.get('bg_secondary', '#f8f9fa')
        bg_tertiary = theme_colors.get('bg_tertiary', '#e9ecef')

        self.left_vertical_splitter.setStyleSheet(f"""
            QSplitter::handle:vertical {{
                background-color: {bg_secondary};
                border: 1px solid {bg_tertiary};
                height: 4px;
                margin: 1px 2px;
                border-radius: 2px;
            }}
            QSplitter::handle:vertical:hover {{
                background-color: {bg_tertiary};
            }}
        """)


    def _apply_log_theme_styling(self): #vers 7
        """Apply theme styling to the log widget"""
        theme_colors = self._get_theme_colors("default")

        # Extract variables FIRST
        panel_bg = theme_colors.get('panel_bg', '#f0f0f0')
        text_primary = theme_colors.get('text_primary', '#000000')
        border = theme_colors.get('border', '#dee2e6')

        self.log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {panel_bg};
                color: {text_primary};
                border: 1px solid {border};
                border-radius: 3px;
                padding: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }}
        """)

    def _apply_status_window_theme_styling(self): #vers 1
        """Apply theme styling to the status window"""
        theme_colors = self._get_theme_colors("default")
        if hasattr(self, 'status_window'):
             # Extract variables FIRST
            panel_bg = theme_colors.get('panel_bg', '#f0f0f0')
            text_primary = theme_colors.get('text_primary', '#000000')
            border = theme_colors.get('border', '#dee2e6')

            self.status_window.setStyleSheet(f"""
                QWidget {{
                    background-color: {panel_bg};
                    border: 1px solid {border};
                    border-radius: 3px;
                }}
                QLabel {{
                    color: #{text_primary};
                    font-weight: bold;
                }}
            """)


    def _apply_file_list_window_theme_styling(self): #vers 7
        """Apply theme styling to the file list window"""
        theme_colors = self._get_theme_colors("default")

        # Extract variables FIRST
        bg_secondary = theme_colors.get('bg_secondary', '#f8f9fa')
        border = theme_colors.get('border', '#dee2e6')
        button_normal = theme_colors.get('button_normal', '#e0e0e0')
        text_primary = theme_colors.get('text_primary', '#000000')
        bg_tertiary = theme_colors.get('bg_tertiary', '#e9ecef')

        if hasattr(self, 'tab_widget'):
            self.tab_widget.setStyleSheet(f"""
                QTabWidget::pane {{
                    background-color: {bg_secondary};
                    border: 1px solid {border};
                    border-radius: 3px;
                }}
                QTabBar::tab {{
                    background-color: {button_normal};
                    color: {text_primary};
                    padding: 5px 10px;
                    margin: 2px;
                    border-radius: 3px;
                }}
                QTabBar::tab:selected {{
                    background-color: {bg_tertiary};
                    border: 1px solid {border};
                }}
            """)


    def _get_theme_colors(self, theme_name): #vers 3
        """Get theme colors - properly connected to app_settings_system"""
        try:
            # Method 1: Use app_settings get_theme_colors() method
            if hasattr(self.main_window, 'app_settings') and hasattr(self.main_window.app_settings, 'get_theme_colors'):
                colors = self.main_window.app_settings.get_theme_colors()
                if colors:
                    print(f"✅ Using app_settings theme colors: {len(colors)} colors loaded")
                    return colors

            # Method 2: Try direct theme access
            if hasattr(self.main_window, 'app_settings') and hasattr(self.main_window.app_settings, 'themes'):
                current_theme = self.main_window.app_settings.current_settings.get("theme", "IMG_Factory")
                theme_data = self.main_window.app_settings.themes.get(current_theme, {})
                colors = theme_data.get('colors', {})
                if colors:
                    print(f"✅ Using direct theme access: {current_theme}")
                    return colors

        except Exception as e:
            print(f"❌ Theme color lookup error: {e}")

        # Fallback with proper theme variables
        print("⚠️ Using fallback theme colors")
        is_dark = self._is_dark_theme()
        if is_dark:
            return {
                'bg_primary': '#2b2b2b', 'bg_secondary': '#3c3c3c', 'bg_tertiary': '#4a4a4a',
                'panel_bg': '#333333', 'text_primary': '#ffffff', 'text_secondary': '#cccccc',
                'border': '#666666', 'accent_primary': '#0078d4', 'button_normal': '#404040'
            }
        else:
            return {
                'bg_primary': '#ffffff', 'bg_secondary': '#f8f9fa', 'bg_tertiary': '#e9ecef',
                'panel_bg': '#f0f0f0', 'text_primary': '#000000', 'text_secondary': '#495057',
                'border': '#dee2e6', 'accent_primary': '#1976d2', 'button_normal': '#e0e0e0'
            }


    def apply_all_window_themes(self): #vers 1
        """Apply theme styling to all windows"""
        if hasattr(self, 'tearoff_button') and self.tearoff_button:
            self._apply_tearoff_button_theme()

        self._apply_table_theme_styling()
        self._apply_log_theme_styling()
        self._apply_vertical_splitter_theme()
        self._apply_main_splitter_theme()
        self._apply_status_window_theme_styling()
        self._apply_file_list_window_theme_styling()


    def apply_table_theme(self): #vers 1
        """Legacy method - Apply theme styling to table and related components"""
        # This method is called by main application for compatibility
        self.apply_all_window_themes()


    def _safe_log(self, message): #vers 1
        """Safe logging that won't cause circular dependency"""
        if hasattr(self.main_window, 'log_message') and hasattr(self.main_window, 'gui_layout'):
            self.main_window.log_message(message)
        else:
            print(f"GUI Layout: {message}")

    def log_message(self, message): #vers 1
        """Add message to activity log"""
        if self.log:
            from PyQt6.QtCore import QDateTime
            timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
            self.log.append(f"[{timestamp}] {message}")
            # Auto-scroll to bottom
            self.log.verticalScrollBar().setValue(
                self.log.verticalScrollBar().maximum()
            )

    # SETTINGS & CONFIGURATION
    def apply_settings_changes(self, settings): #vers 1
        """Apply settings changes to the GUI layout"""
        try:
            # Apply tab settings if they exist
            if any(key.startswith('tab_') or key in ['main_tab_height', 'individual_tab_height', 'tab_font_size', 'tab_padding', 'tab_container_height'] for key in settings.keys()):
                main_height = settings.get("main_tab_height", 30)
                tab_height = settings.get("individual_tab_height", 24)
                font_size = settings.get("tab_font_size", 9)
                padding = settings.get("tab_padding", 4)
                container_height = settings.get("tab_container_height", 40)

                self._apply_dynamic_tab_styling(
                    main_height, tab_height, font_size, padding, container_height
                )

            # Apply button icon settings
            if 'show_button_icons' in settings:
                self._update_button_icons_state(settings['show_button_icons'])

            # Apply other GUI settings as needed
            if 'table_row_height' in settings:
                self._update_table_row_height(settings['table_row_height'])

            if 'widget_spacing' in settings:
                self._update_widget_spacing(settings['widget_spacing'])

            # Apply theme changes
            if 'theme_changed' in settings:
                self.apply_all_window_themes()

        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Error applying settings changes: {str(e)}")

    def _update_table_row_height(self, height): #vers 1
        """Update table row height"""
        try:
            if hasattr(self, 'table') and self.table:
                self.table.verticalHeader().setDefaultSectionSize(height)
        except Exception:
            pass

    def _update_widget_spacing(self, spacing): #vers 1
        """Update widget spacing"""
        try:
            if hasattr(self, 'main_splitter') and self.main_splitter:
                # Update splitter spacing
                self.main_splitter.setHandleWidth(max(4, spacing))
        except Exception:
            pass

    # RESPONSIVE DESIGN & ADAPTIVE LAYOUT
    def handle_resize_event(self, event): #vers 1
        """Handle window resize to adapt button text"""
        if self.main_splitter:
            sizes = self.main_splitter.sizes()
            if len(sizes) > 1:
                right_panel_width = sizes[1]
                self.adapt_buttons_to_width(right_panel_width)

    def adapt_buttons_to_width(self, width): #vers 1
        """Adapt button text based on available width"""
        all_buttons = []
        if hasattr(self, 'img_buttons'):
            all_buttons.extend(self.img_buttons)
        if hasattr(self, 'entry_buttons'):
            all_buttons.extend(self.entry_buttons)
        if hasattr(self, 'options_buttons'):
            all_buttons.extend(self.options_buttons)
        
        for button in all_buttons:
            if hasattr(button, 'full_text'):
                if width > 280:
                    button.setText(button.full_text)
                elif width > 200:
                    # Medium text - remove some words
                    text = button.full_text.replace(' via', '>').replace(' lst', '')
                    button.setText(text)
                elif width > 150:
                    button.setText(button.short_text)
                else:
                    # Icon only mode
                    button.setText("")

    # PROGRESS & STATUS MANAGEMENT

    def show_progress(self, value, text="Working..."): #vers 1
        """Show progress using unified progress system"""
        try:
            from methods.progressbar import show_progress as unified_show_progress
            unified_show_progress(self.main_window, value, text)
        except ImportError:
            # Fallback to old system if unified not available
            if hasattr(self.main_window, 'show_progress'):
                self.main_window.show_progress(text, 0, 100)
                self.main_window.update_progress(value)
            elif hasattr(self.main_window, 'progress_bar'):
                self.main_window.progress_bar.setValue(value)
                self.main_window.progress_bar.setVisible(value >= 0)
            else:
                # Final fallback to status bar
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(f"{text} ({value}%)")

    def hide_progress(self): #vers 1
        """Hide progress using unified progress system"""
        try:
            from methods.progressbar import hide_progress as unified_hide_progress
            unified_hide_progress(self.main_window, "Ready")
        except ImportError:
            # Fallback to old system
            if hasattr(self.main_window, 'hide_progress'):
                self.main_window.hide_progress()
            elif hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("Ready")

    def update_file_info(self, info_text): #vers 1
        """Update file info using unified progress for completion"""
        if hasattr(self.main_window, 'update_img_status'):
            # Extract info from text if possible
            if "entries" in info_text:
                try:
                    count = int(info_text.split()[0])
                    self.main_window.update_img_status(entry_count=count)
                except:
                    pass

    def create_status_bar(self): #vers 1
        """Create status bar with unified progress integration"""
        try:
            from gui.status_bar import create_status_bar
            create_status_bar(self.main_window)

            # Integrate unified progress system
            try:
                from methods.progressbar import integrate_progress_system
                integrate_progress_system(self.main_window)
                self.log_message("✅ Status bar with unified progress created")
            except ImportError:
                self.log_message("✅ Status bar created (unified progress not available)")

        except ImportError:
            # Fallback - create basic status bar
            from PyQt6.QtWidgets import QStatusBar
            self.main_window.setStatusBar(QStatusBar())
            self.main_window.statusBar().showMessage("Ready")
            self.log_message("⚠️ Basic status bar created (gui.status_bar not available)")
        except Exception as e:
            self.log_message(f"❌ Status bar creation error: {str(e)}")


# LEGACY COMPATIBILITY FUNCTIONS

def create_control_panel(main_window): #vers 1
    """Create the main control panel - LEGACY FUNCTION"""
    # Redirect to new method for compatibility
    if hasattr(main_window, 'gui_layout'):
        return main_window.gui_layout.create_right_panel_with_pastel_buttons()
    return None


__all__ = [
    'IMGFactoryGUILayout',
    'create_control_panel',  # Legacy compatibility
]
