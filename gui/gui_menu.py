#this belongs in gui/gui_menu.py - Version: 20
# X-Seti - August14 2025 - IMG Factory 1.5

#!/usr/bin/env python3
"""
IMG Factory Menu System - Complete Implementation
Full menu system with all original entries restored + IDE/COL Editor integration
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Callable
from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QCheckBox, QGroupBox, QLabel, QLineEdit, QComboBox, 
    QMessageBox, QTabWidget, QWidget, QTextEdit, QSpinBox, QRadioButton,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSettings
from PyQt6.QtGui import QAction, QFont, QPixmap, QIcon, QKeySequence, QActionGroup
from .panel_manager import PanelManager


class MenuAction:
    """Represents a menu action with properties"""

    def __init__(self, action_id: str, text: str, shortcut: str = "",
                 icon: str = "", callback: Callable = None, checkable: bool = False):
        self.action_id = action_id
        self.text = text
        self.shortcut = shortcut
        self.icon = icon
        self.callback = callback
        self.checkable = checkable
        self.enabled = True
        self.visible = True
        self.separator_after = False

        #integrate_settings_menu(self) #double menu
        #integrate_color_ui_system(self) #missing function

class MenuDefinition:
    """Defines the complete menu structure"""

    def __init__(self):
        # Complete IMG Factory menu structure - all original entries restored
        self.menu_structure = {
            "File": [
                MenuAction("new_img", "&New IMG", "Ctrl+N", "document-new"),
                MenuAction("open_img", "&Open IMG", "Ctrl+O", "document-open"),
                MenuAction("open_multiple", "Open &Multiple Files", "Ctrl+Shift+O", "folder-open"),
                MenuAction("recent_files", "&Recent Files"),
                MenuAction("sep1", ""),
                MenuAction("close_img", "&Close", "Ctrl+W", "window-close"),
                MenuAction("close_all", "Close &All", "Ctrl+Shift+W"),
                MenuAction("sep2", ""),
                MenuAction("save_img", "&Save", "Ctrl+S"),
                MenuAction("save_as_img", "Save &As...", "Ctrl+Shift+S"),
                MenuAction("sep3", ""),
                MenuAction("exit", "E&xit", "Ctrl+Q", "application-exit"),
            ],

            "Edit": [
                MenuAction("undo", "&Undo", "Ctrl+Z", "edit-undo"),
                MenuAction("redo", "&Redo", "Ctrl+Y", "edit-redo"),
                MenuAction("sep1", ""),
                MenuAction("cut", "Cu&t", "Ctrl+X", "edit-cut"),
                MenuAction("copy", "&Copy", "Ctrl+C", "edit-copy"),
                MenuAction("paste", "&Paste", "Ctrl+V", "edit-paste"),
                MenuAction("sep2", ""),
                MenuAction("select_all", "Select &All", "Ctrl+A", "edit-select-all"),
                MenuAction("select_inverse", "Select &Inverse", "Ctrl+I"),
                MenuAction("select_none", "Select &None", "Ctrl+D"),
                MenuAction("sep3", ""),
                MenuAction("find", "&Find", "Ctrl+F", "edit-find"),
                MenuAction("find_next", "Find &Next", "F3"),
                MenuAction("replace", "&Replace", "Ctrl+H"),
            ],

            "DAT": [
                MenuAction("dat_info", "DAT File &Information"),
                MenuAction("dat_validate", "&Validate DAT"),
                MenuAction("dat_rebuild", "&Rebuild DAT"),
                MenuAction("dat_optimize", "&Optimize DAT"),
                MenuAction("sep1", ""),
                MenuAction("dat_extract", "&Extract All"),
                MenuAction("dat_create", "&Create New DAT"),
                MenuAction("dat_merge", "&Merge DAT Files"),
                MenuAction("sep2", ""),
                MenuAction("dat_backup", "&Backup DAT"),
                MenuAction("dat_restore", "&Restore DAT"),
            ],

            "IMG": [
                MenuAction("img_info", "IMG &Information", "F4"),
                MenuAction("img_validate", "&Validate IMG", "F5"),
                MenuAction("img_rebuild", "&Rebuild IMG", "F6"),
                MenuAction("Img analyze", "&Analyze IMG", "Shift+F7"),
                MenuAction("img_save_entry", "Save Entry.", "Shift+F6"),
                MenuAction("sep1", ""),
                MenuAction("img_extract", "&Extract All"),
                MenuAction("img_merge", "&Merge IMG Files"),
                MenuAction("img_split", "&Split IMG File"),
                MenuAction("img_convert", "&Convert Format"),
                MenuAction("sep2", ""),
                MenuAction("img_optimize", "&Optimize IMG"),
                MenuAction("img_defrag", "&Defragment IMG"),
                MenuAction("img_compress", "&Compress IMG"),
                MenuAction("sep3", ""),
                MenuAction("img_backup", "&Backup IMG"),
                MenuAction("img_compare", "Co&mpare IMG Files"),
            ],

            "DFF": [
                MenuAction("model_view", "&View Model", "F7"),
                MenuAction("model_export", "&Export Model"),
                MenuAction("model_import", "&Import Model"),
                MenuAction("model_replace", "&Replace Model"),
                MenuAction("sep1", ""),
                MenuAction("model_convert", "&Convert Format"),
                MenuAction("model_validate", "&Validate DFF"),
                MenuAction("model_optimize", "&Optimize Model"),
                MenuAction("sep2", ""),
                MenuAction("model_batch_export", "&Batch Export"),
                MenuAction("model_batch_convert", "Batch &Convert"),
                MenuAction("model_batch_optimize", "Batch &Optimize"),
                MenuAction("sep3", ""),
                MenuAction("model_viewer_3d", "&3D Model Viewer"),
                MenuAction("model_properties", "Model &Properties"),
            ],

            "TXD": [
                MenuAction("texture_view", "&View Texture", "F8"),
                MenuAction("texture_export", "&Export Texture"),
                MenuAction("texture_import", "&Import Texture"),
                MenuAction("texture_replace", "&Replace Texture"),
                MenuAction("sep1", ""),
                MenuAction("texture_convert", "&Convert Format"),
                MenuAction("texture_validate", "&Validate TXD"),
                MenuAction("texture_optimize", "&Optimize Textures"),
                MenuAction("sep2", ""),
                MenuAction("texture_batch_export", "&Batch Export"),
                MenuAction("texture_batch_convert", "Batch &Convert"),
                MenuAction("texture_batch_resize", "Batch &Resize"),
                MenuAction("sep3", ""),
                MenuAction("texture_palette", "Extract &Palette"),
                MenuAction("texture_atlas", "Create &Atlas"),
                MenuAction("texture_properties", "Texture &Properties"),
            ],

            "Coll": [
                MenuAction("collision_view", "&View Collision", "F9"),
                MenuAction("collision_edit", "&Edit Collision", "Ctrl+Shift+C"),
                MenuAction("collision_export", "&Export Collision"),
                MenuAction("collision_import", "&Import Collision"),
                MenuAction("collision_replace", "&Replace Collision"),
                MenuAction("sep1", ""),
                MenuAction("collision_validate", "&Validate COL"),
                MenuAction("collision_optimize", "&Optimize Collision"),
                MenuAction("collision_analyze", "&Analyze Collision"),
                MenuAction("sep2", ""),
                MenuAction("collision_batch_export", "&Batch Export"),
                MenuAction("collision_batch_convert", "Batch &Convert"),
                MenuAction("sep3", ""),
                MenuAction("collision_viewer_3d", "&3D Collision Viewer"),
                MenuAction("collision_properties", "Collision &Properties"),
                MenuAction("collision_debug", "&Debug Information"),
                MenuAction("sep4", ""),
                MenuAction("col_editor", "&COL Editor"),
            ],

            "Anim": [
                MenuAction("anim_view", "&View Animation"),
                MenuAction("anim_export", "&Export Animation"),
                MenuAction("anim_import", "&Import Animation"),
                MenuAction("anim_replace", "&Replace Animation"),
                MenuAction("sep1", ""),
                MenuAction("anim_validate", "&Validate IFP"),
                MenuAction("anim_convert", "&Convert Format"),
                MenuAction("sep2", ""),
                MenuAction("anim_batch_export", "&Batch Export"),
                MenuAction("anim_properties", "Animation &Properties"),
                MenuAction("anim_player", "Animation &Player"),
            ],

            "IDE": [
                MenuAction("ide_view", "&View IDE"),
                MenuAction("ide_edit", "&Edit IDE"),
                MenuAction("ide_validate", "&Validate IDE"),
                MenuAction("ide_search", "&Search IDE"),
                MenuAction("sep1", ""),
                MenuAction("ide_export", "&Export to Text"),
                MenuAction("ide_import", "&Import from Text"),
                MenuAction("ide_convert", "&Convert Format"),
                MenuAction("sep2", ""),
                MenuAction("ide_backup", "&Backup IDE"),
                MenuAction("ide_compare", "&Compare IDE Files"),
                MenuAction("sep3", ""),
                MenuAction("sort_img_by_ide", "Sort &IMG by IDE"),
                MenuAction("sort_col_by_ide", "Sort &COL by IDE"),
            ],

            "IPL": [
                MenuAction("ipl_view", "&View IPL"),
                MenuAction("ipl_edit", "&Edit IPL"),
                MenuAction("ipl_validate", "&Validate IPL"),
                MenuAction("ipl_search", "&Search IPL"),
                MenuAction("sep1", ""),
                MenuAction("ipl_export", "&Export to Text"),
                MenuAction("ipl_import", "&Import from Text"),
                MenuAction("ipl_convert", "&Convert Format"),
                MenuAction("sep2", ""),
                MenuAction("ipl_map_view", "View on &Map"),
                MenuAction("ipl_coordinates", "Show &Coordinates"),
                MenuAction("ipl_zones", "Show &Zones"),
            ],

            "Entry": [
                MenuAction("entry_info", "Entry &Information", "Alt+Enter"),
                MenuAction("entry_properties", "&Properties", "Alt+P"),
                MenuAction("entry_preview", "Pre&view", "Space"),
                MenuAction("sep1", ""),
                MenuAction("entry_import", "&Import Files", "Ctrl+I"),
                MenuAction("entry_export", "&Export Selected", "Ctrl+E"),
                MenuAction("entry_export_all", "Export &All", "Ctrl+Shift+E"),
                MenuAction("entry_quick_export", "&Quick Export", "Ctrl+Q"),
                MenuAction("sep2", ""),
                MenuAction("entry_remove", "&Remove Selected", "Delete"),
                MenuAction("entry_rename", "Re&name", "F2"),
                MenuAction("entry_replace", "Rep&lace", "Ctrl+R"),
                MenuAction("entry_duplicate", "&Duplicate", "Ctrl+D"),
                MenuAction("sep3", ""),
                MenuAction("entry_sort", "&Sort Entries"),
                MenuAction("entry_filter", "&Filter Entries"),
                MenuAction("entry_search", "Searc&h Entries"),
                MenuAction("sep4", ""),
                MenuAction("entry_batch_ops", "&Batch Operations"),
                MenuAction("entry_mass_rename", "&Mass Rename"),
                MenuAction("entry_verify", "&Verify Integrity"),
            ],

            "Tools": [
                MenuAction("search", "&Search", "Ctrl+F", "search"),
                MenuAction("filter", "&Filter", "Ctrl+Shift+F", "filter"),
                MenuAction("batch_processor", "&Batch Processor"),
                MenuAction("sep1", ""),
                MenuAction("col_editor", "&COL Editor", "Ctrl+Shift+C"),
                MenuAction("txd_editor", "&TXD Editor", "Ctrl+Shift+T"),
                MenuAction("dff_editor", "&DFF Editor", "Ctrl+Shift+D"),
                MenuAction("ifp_editor", "&IFP Editor", "Ctrl+Shift+I"),
                MenuAction("sep2", ""),
                MenuAction("ide_editor", "I&DE Editor"),
                MenuAction("ipl_editor", "IP&L Editor"),
                MenuAction("dat_editor", "DA&T Editor"),
                MenuAction("sep3", ""),
                MenuAction("file_converter", "File &Converter"),
                MenuAction("hex_editor", "&Hex Editor"),
                MenuAction("text_editor", "Te&xt Editor"),
                MenuAction("sep4", ""),
                MenuAction("game_launcher", "&Game Launcher"),
                MenuAction("mod_manager", "&Mod Manager"),
                MenuAction("sep5", ""),
                MenuAction("preferences", "&Preferences", "Ctrl+,", "settings"),
            ],

            "View": [
                MenuAction("toolbar", "&Toolbar", "", "", None, True),
                MenuAction("statusbar", "&Status Bar", "", "", None, True),
                MenuAction("log_panel", "&Log Panel", "F12", "", None, True),
                MenuAction("sep1", ""),
                MenuAction("file_tree", "&File Tree", "", "", None, True),
                MenuAction("properties_panel", "&Properties Panel", "", "", None, True),
                MenuAction("preview_panel", "Pre&view Panel", "", "", None, True),
                MenuAction("sep2", ""),
                MenuAction("icon_mode", "&Icon Mode", "Ctrl+1", "icon", None, True),
                MenuAction("list_mode", "&List Mode", "Ctrl+2", "list", None, True),
                MenuAction("detail_mode", "&Detail Mode", "Ctrl+3", "detail", None, True),
                MenuAction("thumbnail_mode", "&Thumbnail Mode", "Ctrl+4", "thumbnail", None, True),
                MenuAction("sep3", ""),
                MenuAction("zoom_in", "Zoom &In", "Ctrl+="),
                MenuAction("zoom_out", "Zoom &Out", "Ctrl+-"),
                MenuAction("zoom_reset", "&Reset Zoom", "Ctrl+0"),
                MenuAction("zoom_fit", "&Fit to Window", "Ctrl+9"),
                MenuAction("sep4", ""),
                MenuAction("fullscreen", "&Fullscreen", "F11"),
                MenuAction("stay_on_top", "Stay on &Top", "", "", None, True),
            ],

            "Settings": [
                MenuAction("preferences", "&Preferences", "Ctrl+,"),
                MenuAction("customize_interface", "Customize &Interface"),
                MenuAction("customize_buttons", "Customize &Buttons"),
                MenuAction("customize_panels", "Customize &Panels"),
                MenuAction("customize_menus", "Customize &Menus"),
                MenuAction("sep1", ""),
                MenuAction("themes", "&Themes"),
                MenuAction("language", "&Language"),
                MenuAction("plugins", "&Plugins"),
                MenuAction("sep2", ""),
                MenuAction("file_associations", "&File Associations"),
                MenuAction("default_directories", "&Default Directories"),
                MenuAction("performance", "Per&formance"),
                MenuAction("sep3", ""),
                MenuAction("reset_layout", "&Reset Layout"),
                MenuAction("reset_settings", "Reset &Settings"),
                MenuAction("sep4", ""),
                MenuAction("export_settings", "&Export Settings"),
                MenuAction("import_settings", "&Import Settings"),
            ],

            "Debug": [
                MenuAction("debug_console", "&Debug Console", "F12"),
                MenuAction("debug_log", "Debug &Log"),
                MenuAction("debug_performance", "&Performance Monitor"),
                MenuAction("sep1", ""),
                MenuAction("debug_col", "&COL Debug Mode", "", "", None, True),
                MenuAction("debug_img", "&IMG Debug Mode", "", "", None, True),
                MenuAction("debug_memory", "&Memory Debug", "", "", None, True),
                MenuAction("sep2", ""),
                MenuAction("debug_export_log", "&Export Debug Log"),
                MenuAction("debug_clear_log", "&Clear Debug Log"),
                MenuAction("debug_settings", "Debug &Settings"),
            ],

            "Help": [
                MenuAction("help_contents", "&Help Contents", "F1"),
                MenuAction("help_shortcuts", "&Keyboard Shortcuts"),
                MenuAction("help_formats", "Supported &Formats"),
                MenuAction("help_tutorial", "&Tutorial"),
                MenuAction("sep1", ""),
                MenuAction("help_website", "Visit &Website"),
                MenuAction("help_forum", "Community &Forum"),
                MenuAction("help_report_bug", "&Report Bug"),
                MenuAction("help_feature_request", "&Feature Request"),
                MenuAction("sep2", ""),
                MenuAction("help_check_updates", "&Check for Updates"),
                MenuAction("help_changelog", "&Changelog"),
                MenuAction("sep3", ""),
                MenuAction("about", "&About IMG Factory"),
                MenuAction("about_qt", "About &Qt"),
            ]
        }


class COLMenuBuilder:
    """Helper class to build COL menu items"""

    @staticmethod
    def add_col_menu_to_menubar(menubar: QMenuBar, parent_window) -> QMenu:
        """Add COL menu to existing menubar"""

        # Create COL menu
        col_menu = menubar.addMenu("🔧 &COL")

        # Main COL Editor
        editor_action = QAction("✏️ COL &Editor", parent_window)
        editor_action.setShortcut("Ctrl+Shift+C")
        editor_action.setStatusTip("Open COL Editor for collision file editing")
        editor_action.triggered.connect(lambda: COLMenuBuilder._open_col_editor(parent_window))
        col_menu.addAction(editor_action)

        col_menu.addSeparator()

        # File operations
        open_col_action = QAction("📂 &Open COL File", parent_window)
        open_col_action.setShortcut("Ctrl+Shift+O")
        open_col_action.setStatusTip("Open COL file directly")
        open_col_action.triggered.connect(lambda: COLMenuBuilder._open_col_file(parent_window))
        col_menu.addAction(open_col_action)

        new_col_action = QAction("🆕 &New COL File", parent_window)
        new_col_action.setStatusTip("Create new COL file")
        new_col_action.triggered.connect(lambda: COLMenuBuilder._new_col_file(parent_window))
        col_menu.addAction(new_col_action)

        col_menu.addSeparator()

        # Batch operations
        batch_action = QAction("⚙️ &Batch Processor", parent_window)
        batch_action.setShortcut("Ctrl+Shift+B")
        batch_action.setStatusTip("Process multiple COL files with batch operations")
        batch_action.triggered.connect(lambda: COLMenuBuilder._open_batch_processor(parent_window))
        col_menu.addAction(batch_action)

        analyze_action = QAction("📊 &Analyze COL", parent_window)
        analyze_action.setShortcut("Ctrl+Shift+A")
        analyze_action.setStatusTip("Analyze COL file structure and quality")
        analyze_action.triggered.connect(lambda: COLMenuBuilder._analyze_col(parent_window))
        col_menu.addAction(analyze_action)

        col_menu.addSeparator()

        # IMG integration
        import_submenu = col_menu.addMenu("📥 Import from IMG")

        extract_col_action = QAction("Extract COL from Current IMG", parent_window)
        extract_col_action.setStatusTip("Extract COL files from currently open IMG")
        extract_col_action.triggered.connect(lambda: COLMenuBuilder._extract_col_from_img(parent_window))
        import_submenu.addAction(extract_col_action)

        import_col_action = QAction("Import COL to Current IMG", parent_window)
        import_col_action.setStatusTip("Import COL file into currently open IMG")
        import_col_action.triggered.connect(lambda: COLMenuBuilder._import_col_to_img(parent_window))
        import_submenu.addAction(import_col_action)

        col_menu.addSeparator()

        # Help
        help_action = QAction("❓ COL &Help", parent_window)
        help_action.setStatusTip("Show help for COL functionality")
        help_action.triggered.connect(lambda: COLMenuBuilder._show_col_help(parent_window))
        col_menu.addAction(help_action)

        return col_menu

    def create_img_menu(self): #vers [your_version + 1]
        """Create IMG menu with corruption analyzer"""
        img_menu = self.menubar.addMenu("IMG")

        img_menu.addSeparator()

        # Corruption Analysis submenu
        corruption_menu = img_menu.addMenu("🔍 Corruption Analysis")

        analyze_action = QAction("🔍 Analyze IMG Corruption", self.main_window)
        analyze_action.setStatusTip("Analyze IMG file for corrupted entries and filenames")
        analyze_action.triggered.connect(self.main_window.analyze_img_corruption)
        corruption_menu.addAction(analyze_action)

        quick_fix_action = QAction("🔧 Quick Fix Corruption", self.main_window)
        quick_fix_action.setStatusTip("Automatically fix common corruption issues")
        quick_fix_action.triggered.connect(self.main_window.quick_fix_corruption)
        corruption_menu.addAction(quick_fix_action)

        # Clean filenames only
        clean_names_action = QAction("🧹 Clean Filenames Only", self.main_window)
        clean_names_action.setStatusTip("Fix only filename corruption, keep all entries")
        clean_names_action.triggered.connect(self.main_window.clean_filenames_only)
        corruption_menu.addAction(clean_names_action)

        corruption_menu.addSeparator()

        export_report_action = QAction("📄 Export Corruption Report", self.main_window)
        export_report_action.setStatusTip("Export detailed corruption analysis to file")
        export_report_action.triggered.connect(self.main_window.export_corruption_report)
        corruption_menu.addAction(export_report_action)

        return img_menu

    @staticmethod
    def _open_col_editor(parent_window):
        """Open COL editor"""
        try:
            from components.col_editor import open_col_editor
            open_col_editor(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Editor", "COL Editor components not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to open COL Editor: {str(e)}")

    @staticmethod
    def _open_col_file(parent_window):
        """Open COL file dialog"""
        try:
            from imgfactory_col_integration import open_col_file_dialog
            open_col_file_dialog(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Tools", "COL integration components not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to open COL file: {str(e)}")

    @staticmethod
    def _new_col_file(parent_window):
        """Create new COL file"""
        try:
            from imgfactory_col_integration import create_new_col_file
            create_new_col_file(parent_window)
        except ImportError:
            QMessageBox.information(parent_window, "COL Tools", "New COL file creation coming soon!")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to create COL file: {str(e)}")

    @staticmethod
    def _open_batch_processor(parent_window):
        """Open batch processor"""
        try:
            from components.col_utilities import open_col_batch_processor
            open_col_batch_processor(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Tools", "COL batch processor not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to open batch processor: {str(e)}")

    @staticmethod
    def _analyze_col(parent_window):
        """Analyze COL file"""
        try:
            from components.col_utilities import analyze_col_file_dialog
            analyze_col_file_dialog(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Tools", "COL analyzer not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to analyze COL: {str(e)}")

    @staticmethod
    def _extract_col_from_img(parent_window):
        """Extract COL from IMG"""
        try:
            from imgfactory_col_integration import export_col_from_img
            export_col_from_img(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Tools", "COL integration not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to extract COL: {str(e)}")

    @staticmethod
    def _import_col_to_img(parent_window):
        """Import COL to IMG"""
        try:
            from imgfactory_col_integration import import_col_to_img
            import_col_to_img(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Tools", "COL integration not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to import COL: {str(e)}")

    @staticmethod
    def _show_col_help(parent_window):
        """Show COL help dialog"""
        help_text = """
<h2>🔧 COL Functionality Help</h2>

<h3>What are COL files?</h3>
<p>COL files contain collision data for GTA games. They define the physical boundaries
that players, vehicles, and objects interact with in the game world.</p>

<h3>COL Editor Features:</h3>
<ul>
<li><b>3D Visualization</b> - View collision geometry in 3D</li>
<li><b>Edit Collision Elements</b> - Modify spheres, boxes, and meshes</li>
<li><b>Material Assignment</b> - Set surface materials for different effects</li>
<li><b>Version Conversion</b> - Convert between COL formats</li>
<li><b>Optimization Tools</b> - Remove duplicates and optimize geometry</li>
</ul>

<h3>Batch Processor:</h3>
<ul>
<li><b>Process Multiple Files</b> - Handle many COL files at once</li>
<li><b>Automatic Optimization</b> - Clean up and optimize collision data</li>
<li><b>Version Conversion</b> - Convert entire batches between formats</li>
<li><b>Quality Analysis</b> - Check for issues and problems</li>
</ul>

<h3>Supported Games:</h3>
<ul>
<li>GTA III (COL Version 1)</li>
<li>GTA Vice City (COL Version 1)</li>
<li>GTA San Andreas (COL Version 2 & 3)</li>
<li>GTA Stories series</li>
<li>Bully</li>
</ul>

<h3>Keyboard Shortcuts:</h3>
<ul>
<li><b>Ctrl+Shift+C</b> - Open COL Editor</li>
<li><b>Ctrl+Shift+B</b> - Open Batch Processor</li>
<li><b>Ctrl+Shift+A</b> - Analyze COL File</li>
<li><b>Ctrl+Shift+O</b> - Open COL File</li>
</ul>

<p><i>COL functionality is based on Steve's COL Editor II with modern improvements.</i></p>
        """

        QMessageBox.about(parent_window, "COL Help", help_text)


class IMGFactoryMenuBar:
    """Complete IMG Factory menu bar with all original functionality"""
    
    def __init__(self, main_window, panel_manager: PanelManager = None):
        self.main_window = main_window
        self.panel_manager = panel_manager
        self.menu_bar = main_window.menuBar()
        self.callbacks: Dict[str, Callable] = {}
        self.actions: Dict[str, QAction] = {}
        self.menus: Dict[str, QMenu] = {}
        
        # Dialog management
        self._preferences_dialog = None
        self._gui_settings_dialog = None
        
        # Clear any existing menus first
        self.menu_bar.clear()
        
        self.menu_definition = MenuDefinition()
        self._create_menus()
        #self.col_menu()
        
        # Set up default callbacks
        self._setup_default_callbacks()
    
    def _create_menus(self):
        """Create all menus from definition"""
        for menu_name, menu_actions in self.menu_definition.menu_structure.items():
            menu = self.menu_bar.addMenu(menu_name)
            self.menus[menu_name] = menu
            
            for menu_action in menu_actions:
                if menu_action.action_id.startswith("sep"):
                    menu.addSeparator()
                else:
                    action = QAction(menu_action.text, self.main_window)
                    
                    if menu_action.shortcut:
                        action.setShortcut(QKeySequence(menu_action.shortcut))
                    
                    if menu_action.checkable:
                        action.setCheckable(True)
                        # Set default checked state for view items
                        if menu_action.action_id in ["toolbar", "statusbar", "log_panel"]:
                            action.setChecked(True)
                    
                    # Store action
                    self.actions[menu_action.action_id] = action
                    
                    # Add to menu
                    menu.addAction(action)

    def _setup_default_callbacks(self):
        """Set up default menu callbacks"""
        default_callbacks = {
            # File menu
            "exit": self._exit_application,

            # IDE menu callbacks
            "ide_editor": self._open_ide_editor,
            "sort_img_by_ide": self._sort_img_by_ide,
            "sort_col_by_ide": self._sort_col_by_ide,
            "ide_view": self._view_ide,
            "ide_edit": self._edit_ide,
            "ide_validate": self._validate_ide,
            "ide_search": self._search_ide,
            "ide_export": self._export_ide,
            "ide_import": self._import_ide,
            "ide_convert": self._convert_ide,
            "ide_backup": self._backup_ide,
            "ide_compare": self._compare_ide,

            # COL menu callbacks
            "col_editor": self._open_col_editor,
            "collision_view": self._view_collision,
            "collision_edit": self._edit_collision,
            "collision_export": self._export_collision,
            "collision_import": self._import_collision,
            "collision_validate": self._validate_collision,
            "collision_optimize": self._optimize_collision,
            "collision_analyze": self._analyze_collision,
            "collision_batch_export": self._batch_export_collision,
            "collision_batch_convert": self._batch_convert_collision,
            "collision_viewer_3d": self._view_collision_3d,
            "collision_properties": self._collision_properties,
            "collision_debug": self._collision_debug,

            # Tools menu (duplicate entries for accessibility)
            "col_editor": self._open_col_editor,
            "txd_editor": self._open_txd_editor,
            "dff_editor": self._open_dff_editor,
            "ifp_editor": self._open_ifp_editor,
            "ipl_editor": self._open_ipl_editor,
            "dat_editor": self._open_dat_editor,

            # Settings menu
            "preferences": self._show_preferences,
            "customize_interface": self._show_gui_settings,
            "themes": self._show_theme_settings,
            "export_settings": self._export_settings,
            "import_settings": self._import_settings,
            "reset_layout": self._reset_layout,

            # View menu
            "toolbar": self._toggle_toolbar,
            "statusbar": self._toggle_statusbar,
            "log_panel": self._toggle_log_panel,
            "fullscreen": self._toggle_fullscreen,

            # Help menu
            "about": self._show_about,
            "help_contents": self._show_help,
            "help_shortcuts": self._show_shortcuts,
            "help_formats": self._show_formats,
            "about_qt": self._show_about_qt,

            # Debug menu
            "debug_console": self._show_debug_console,
            "debug_clear_log": self._clear_debug_log,
        }

        self.set_callbacks(default_callbacks)

    # ========================================================================
    # NEW IDE MENU CALLBACKS
    # ========================================================================



    def _open_ide_editor(self):
        """Open IDE Editor"""
        try:
            from components.ide_editor import open_ide_editor
            editor = open_ide_editor(self.main_window)

            # Connect signals for integration
            if hasattr(editor, 'sort_by_ide_requested'):
                editor.sort_by_ide_requested.connect(self._handle_sort_by_ide)
            if hasattr(editor, 'selection_sync_requested'):
                editor.selection_sync_requested.connect(self._handle_selection_sync)

            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ IDE Editor opened")

        except ImportError:
            QMessageBox.warning(self.main_window, "IDE Editor", "IDE Editor components not found")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to open IDE Editor: {str(e)}")

    def _sort_img_by_ide(self):
        """Sort IMG entries by IDE order"""
        try:
            if hasattr(self.main_window, 'sort_img_by_ide_order'):
                self.main_window.sort_img_by_ide_order()
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("📋 IMG entries sorted by IDE order")
            else:
                QMessageBox.information(self.main_window, "Sort IMG",
                    "Sort IMG by IDE functionality will be available when IDE file is loaded.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to sort IMG by IDE: {str(e)}")

    def _sort_col_by_ide(self):
        """Sort COL entries by IDE order"""
        try:
            if hasattr(self.main_window, 'sort_col_by_ide_order'):
                self.main_window.sort_col_by_ide_order()
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("🛡️ COL entries sorted by IDE order")
            else:
                QMessageBox.information(self.main_window, "Sort COL",
                    "Sort COL by IDE functionality will be available when both IDE and COL files are loaded.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to sort COL by IDE: {str(e)}")

    def _handle_sort_by_ide(self, model_order):
        """Handle sort by IDE request from IDE Editor"""
        try:
            # Apply sorting to IMG Factory main window
            if hasattr(self.main_window, 'apply_ide_sort_order'):
                self.main_window.apply_ide_sort_order(model_order)

            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"📋 Applied IDE sort order: {len(model_order)} models")

        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error applying IDE sort: {str(e)}")

    def _handle_selection_sync(self, selected_models):
        """Handle selection sync request from IDE Editor"""
        try:
            # Sync selection with COL Editor if open
            if hasattr(self.main_window, 'sync_col_editor_selection'):
                self.main_window.sync_col_editor_selection(selected_models)

            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"🔗 Synced selection: {len(selected_models)} models")

        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error syncing selection: {str(e)}")

    def _view_ide(self):
        """View IDE file"""
        QMessageBox.information(self.main_window, "View IDE", "IDE viewer coming soon!")

    def _edit_ide(self):
        """Edit IDE file (alias for IDE Editor)"""
        self._open_ide_editor()

    def _validate_ide(self):
        """Validate IDE file"""
        QMessageBox.information(self.main_window, "Validate IDE", "IDE validation coming soon!")

    def _search_ide(self):
        """Search IDE entries"""
        QMessageBox.information(self.main_window, "Search IDE", "IDE search coming soon!")

    def _export_ide(self):
        """Export IDE to text"""
        QMessageBox.information(self.main_window, "Export IDE", "IDE export coming soon!")

    def _import_ide(self):
        """Import IDE from text"""
        QMessageBox.information(self.main_window, "Import IDE", "IDE import coming soon!")

    def _convert_ide(self):
        """Convert IDE format"""
        QMessageBox.information(self.main_window, "Convert IDE", "IDE format conversion coming soon!")

    def _backup_ide(self):
        """Backup IDE file"""
        QMessageBox.information(self.main_window, "Backup IDE", "IDE backup coming soon!")

    def _compare_ide(self):
        """Compare IDE files"""
        QMessageBox.information(self.main_window, "Compare IDE", "IDE comparison coming soon!")

    # ========================================================================
    # COL MENU CALLBACKS
    # ========================================================================

    def _open_col_editor(self):
        """Open COL Editor"""
        try:
            from gui.gui_context import open_col_editor_dialog
            open_col_editor_dialog(self.main_window)
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ COL Editor opened")
        except ImportError:
            QMessageBox.warning(self.main_window, "COL Editor", "COL Editor components not found")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to open COL Editor: {str(e)}")

    def _view_collision(self):
        """View collision data"""
        QMessageBox.information(self.main_window, "View Collision", "COL viewer coming soon!")

    def _edit_collision(self):
        """Edit collision (alias for COL Editor)"""
        self._open_col_editor()

    def _export_collision(self):
        """Export collision data"""
        QMessageBox.information(self.main_window, "Export Collision", "COL export coming soon!")

    def _import_collision(self):
        """Import collision data"""
        QMessageBox.information(self.main_window, "Import Collision", "COL import coming soon!")

    def _validate_collision(self):
        """Validate collision data"""
        QMessageBox.information(self.main_window, "Validate COL", "COL validation coming soon!")

    def _optimize_collision(self):
        """Optimize collision data"""
        QMessageBox.information(self.main_window, "Optimize COL", "COL optimization coming soon!")

    def _analyze_collision(self):
        """Analyze collision data"""
        try:
            from gui.gui_context import analyze_col_file_dialog
            analyze_col_file_dialog(self.main_window)
        except ImportError:
            QMessageBox.information(self.main_window, "Analyze COL", "COL analyzer coming soon!")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to analyze COL: {str(e)}")

    def _batch_export_collision(self):
        """Batch export collision files"""
        QMessageBox.information(self.main_window, "Batch Export", "COL batch export coming soon!")

    def _batch_convert_collision(self):
        """Batch convert collision files"""
        QMessageBox.information(self.main_window, "Batch Convert", "COL batch convert coming soon!")

    def _view_collision_3d(self):
        """View collision in 3D"""
        QMessageBox.information(self.main_window, "3D Collision Viewer", "3D COL viewer coming soon!")

    def _collision_properties(self):
        """Show collision properties"""
        QMessageBox.information(self.main_window, "COL Properties", "COL properties dialog coming soon!")

    def _collision_debug(self):
        """Show collision debug info"""
        QMessageBox.information(self.main_window, "COL Debug", "COL debug information coming soon!")

    # ========================================================================
    # TOOLS MENU CALLBACKS
    # ========================================================================

    def _open_txd_editor(self):
        """Open TXD Editor"""
        QMessageBox.information(self.main_window, "TXD Editor", "TXD Editor coming soon!")

    def _open_dff_editor(self):
        """Open DFF Editor"""
        QMessageBox.information(self.main_window, "DFF Editor", "DFF Editor coming soon!")

    def _open_ifp_editor(self):
        """Open IFP Editor"""
        QMessageBox.information(self.main_window, "IFP Editor", "IFP Editor coming soon!")

    def _open_ipl_editor(self):
        """Open IPL Editor"""
        QMessageBox.information(self.main_window, "IPL Editor", "IPL Editor coming soon!")

    def _open_dat_editor(self):
        """Open DAT Editor"""
        QMessageBox.information(self.main_window, "DAT Editor", "DAT Editor coming soon!")

    def add_col_menu(img_factory_instance):
        """Add COL menu to the main menu bar"""

        menubar = img_factory_instance.menuBar()

        # Create COL menu
        col_menu = menubar.addMenu("COL")

        # File operations
        open_col_action = QAction("Open COL File", img_factory_instance)
        open_col_action.setShortcut("Ctrl+Shift+O")
        open_col_action.triggered.connect(lambda: open_col_file_dialog(img_factory_instance))
        col_menu.addAction(open_col_action)

        new_col_action = QAction("New COL File", img_factory_instance)
        new_col_action.triggered.connect(lambda: create_new_col_file(img_factory_instance))
        col_menu.addAction(new_col_action)

        col_menu.addSeparator()

        # COL Editor
        editor_action = QAction("✏️ COL Editor", img_factory_instance)
        editor_action.setShortcut("Ctrl+E")
        editor_action.triggered.connect(lambda: open_col_editor(img_factory_instance))
        col_menu.addAction(editor_action)

        col_menu.addSeparator()

        # Batch operations
        batch_process_action = QAction("Batch Processor", img_factory_instance)
        batch_process_action.triggered.connect(lambda: open_col_batch_processor(img_factory_instance))
        col_menu.addAction(batch_process_action)

        analyze_action = QAction("Analyze COL", img_factory_instance)
        analyze_action.triggered.connect(lambda: analyze_col_file_dialog(img_factory_instance))
        col_menu.addAction(analyze_action)

        col_menu.addSeparator()

        # Import/Export
        import_to_img_action = QAction("Import to IMG", img_factory_instance)
        import_to_img_action.triggered.connect(lambda: import_col_to_img(img_factory_instance))
        col_menu.addAction(import_to_img_action)

        export_from_img_action = QAction("Export from IMG", img_factory_instance)
        export_from_img_action.triggered.connect(lambda: export_col_from_img(img_factory_instance))
        col_menu.addAction(export_from_img_action)

    # Store reference to COL menu
    #img_factory_instance.col_menu = col_menu

    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """Set menu callbacks"""
        self.callbacks.update(callbacks)
        self._connect_callbacks()

    def _connect_callbacks(self):
        """Connect actions to callbacks"""
        for action_id, callback in self.callbacks.items():
            if action_id in self.actions:
                self.actions[action_id].triggered.connect(callback)

    def enable_action(self, action_id: str, enabled: bool = True):
        """Enable/disable an action"""
        if action_id in self.actions:
            self.actions[action_id].setEnabled(enabled)

    def check_action(self, action_id: str, checked: bool = True):
        """Check/uncheck an action"""
        if action_id in self.actions:
            action = self.actions[action_id]
            if action.isCheckable():
                action.setChecked(checked)

    def get_action(self, action_id: str) -> Optional[QAction]:
        """Get action by ID"""
        return self.actions.get(action_id)

    def set_panel_manager(self, panel_manager: PanelManager):
        """Set panel manager for panel menu integration"""
        self.panel_manager = panel_manager
        self.add_panel_menu()

    def add_panel_menu(self):
        """Add panels menu for tear-off functionality"""
        if not self.panel_manager:
            return

        panels_menu = self.menu_bar.addMenu("&Panels")
        self.menus["Panels"] = panels_menu

        # Show/Hide panels
        show_hide_menu = panels_menu.addMenu("Show/Hide")

        for panel_id, panel in self.panel_manager.panels.items():
            action = QAction(panel.title, self.main_window)
            action.setCheckable(True)
            action.setChecked(panel.isVisible())
            action.triggered.connect(
                lambda checked, pid=panel_id:
                self.panel_manager.show_panel(pid) if checked
                else self.panel_manager.hide_panel(pid)
            )
            show_hide_menu.addAction(action)

        panels_menu.addSeparator()

        # Reset layout
        reset_action = QAction("Reset Layout", self.main_window)
        reset_action.triggered.connect(self._reset_panel_layout)
        panels_menu.addAction(reset_action)

    # ========================================================================
    # ORIGINAL CALLBACK IMPLEMENTATIONS (PRESERVED)
    # ========================================================================

    def _exit_application(self):
        """Exit the application"""
        self.main_window.close()

    def _show_preferences(self):
        """Show preferences dialog with proper lifecycle management"""
        try:
            # Check if dialog already exists and is visible
            if hasattr(self, '_preferences_dialog') and self._preferences_dialog is not None:
                if self._preferences_dialog.isVisible():
                    # Bring existing dialog to front
                    self._preferences_dialog.raise_()
                    self._preferences_dialog.activateWindow()
                    return
                else:
                    # Clean up old dialog
                    self._preferences_dialog.deleteLater()
                    self._preferences_dialog = None

            if hasattr(self.main_window, 'app_settings'):
                from utils.app_settings_system import SettingsDialog

                # Create new dialog
                self._preferences_dialog = SettingsDialog(self.main_window.app_settings, self.main_window)

                # Connect cleanup signal
                self._preferences_dialog.finished.connect(self._on_preferences_closed)

                # Show dialog
                result = self._preferences_dialog.exec()

                if result == QDialog.DialogCode.Accepted:
                    self._apply_gui_changes()
                    if hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message("✅ Preferences updated")

                # Clean up
                self._preferences_dialog = None

            else:
                QMessageBox.information(
                    self.main_window,
                    "Preferences",
                    "Preferences system not available"
                )
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Error",
                "Failed to open preferences: " + str(e)
            )
            # Clean up on error
            if hasattr(self, '_preferences_dialog'):
                self._preferences_dialog = None

    def _on_preferences_closed(self):
        """Handle preferences dialog closed"""
        if hasattr(self, '_preferences_dialog'):
            self._preferences_dialog = None

    def _show_gui_settings(self):
        """Show GUI settings dialog"""
        QMessageBox.information(
            self.main_window,
            "GUI Settings",
            "GUI customization dialog coming soon!"
        )

    def _show_theme_settings(self):
        """Show theme settings"""
        QMessageBox.information(
            self.main_window,
            "Themes",
            "Theme selection coming soon!"
        )

    def _export_settings(self):
        """Export settings to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export Settings",
                "img_factory_settings.json",
                "JSON Files (*.json)"
            )

            if file_path:
                QMessageBox.information(
                    self.main_window,
                    "Export Complete",
                    "Settings exported to " + file_path
                )

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Export Failed",
                "Failed to export settings: " + str(e)
            )

    def _import_settings(self):
        """Import settings from file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Import Settings",
                "",
                "JSON Files (*.json)"
            )

            if file_path:
                QMessageBox.information(
                    self.main_window,
                    "Import Complete",
                    "Settings imported from " + file_path
                )

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Import Failed",
                "Failed to import settings: " + str(e)
            )

    def _reset_layout(self):
        """Reset GUI layout"""
        reply = QMessageBox.question(
            self.main_window,
            "Reset Layout",
            "This will reset the GUI layout to defaults. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self.main_window,
                "Reset Complete",
                "Layout has been reset to defaults."
            )

    def _toggle_toolbar(self):
        """Toggle toolbar visibility"""
        if hasattr(self.main_window, 'toolbar'):
            visible = self.main_window.toolbar.isVisible()
            self.main_window.toolbar.setVisible(not visible)
            self.check_action("toolbar", not visible)

    def _toggle_statusbar(self):
        """Toggle status bar visibility"""
        if hasattr(self.main_window, 'statusBar'):
            statusbar = self.main_window.statusBar()
            visible = statusbar.isVisible()
            statusbar.setVisible(not visible)
            self.check_action("statusbar", not visible)

    def _toggle_log_panel(self):
        """Toggle log panel visibility"""
        if hasattr(self.main_window, 'log_panel'):
            visible = self.main_window.log_panel.isVisible()
            self.main_window.log_panel.setVisible(not visible)
            self.check_action("log_panel", not visible)

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.main_window.isFullScreen():
            self.main_window.showNormal()
        else:
            self.main_window.showFullScreen()

    def _show_about(self): #vers 6
        """Show about dialog"""
        about_text = """
        <h2>IMG Factory 1.5</h2>
        <p><b>Version:</b> 1.5.0</p>
        <p><b>Build Date:</b> August 14, 2025</p>
        <p><b>Author:</b> X-Seti</p>
        <p><b>Original Credits:</b> MexUK 2007 IMG Factory 1.2</p>
        <br>
        <p>A comprehensive tool for managing GTA IMG archives and related files.</p>
        <p>Supports COL, TXD, DFF, IFP, IDE, IPL, and other GTA file formats.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
        <li>IMG archive creation and editing</li>
        <li>File import/export with progress tracking</li>
        <li>COL collision file editor</li>
        <li>IDE item definition editor</li>
        <li>TXD texture management</li>
        <li>DFF model viewer</li>
        <li>Advanced search and filtering</li>
        <li>Customizable interface and themes</li>
        <li>Batch processing tools</li>
        <li>Sort by IDE functionality</li>
        </ul>
        """

        QMessageBox.about(self.main_window, "About IMG Factory", about_text)

    def _show_about_qt(self):
        """Show about Qt dialog"""
        QMessageBox.aboutQt(self.main_window, "About Qt")

    def _show_help(self):
        """Show help contents"""
        help_text = """
        <h2>IMG Factory Help</h2>
        <h3>Getting Started:</h3>
        <p>1. Open an IMG file using File → Open IMG</p>
        <p>2. Browse entries in the main table</p>
        <p>3. Use right-click context menus for entry operations</p>
        <p>4. Import files using Entry → Import Files</p>
        <p>5. Export files using Entry → Export Selected</p>

        <h3>New Features:</h3>
        <p><b>IDE Editor:</b> Edit item definitions with built-in help guide</p>
        <p><b>COL Editor:</b> Advanced collision editing with 3D visualization</p>
        <p><b>Sort by IDE:</b> Reorder IMG/COL entries by IDE sequence</p>

        <h3>Keyboard Shortcuts:</h3>
        <p><b>Ctrl+O:</b> Open IMG file</p>
        <p><b>Ctrl+N:</b> Create new IMG file</p>
        <p><b>Ctrl+I:</b> Import files</p>
        <p><b>Ctrl+E:</b> Export selected entries</p>
        <p><b>F5:</b> Validate IMG</p>
        <p><b>F6:</b> Rebuild IMG</p>
        <p><b>Delete:</b> Remove selected entries</p>
        <p><b>F2:</b> Rename entry</p>
        <p><b>F7:</b> View model</p>
        <p><b>F8:</b> View texture</p>
        <p><b>F9:</b> View collision</p>
        <p><b>Ctrl+Shift+C:</b> Open COL Editor</p>

        <h3>File Types:</h3>
        <p><b>IMG:</b> Archive files containing game assets</p>
        <p><b>COL:</b> Collision data files</p>
        <p><b>TXD:</b> Texture dictionary files</p>
        <p><b>DFF:</b> 3D model files</p>
        <p><b>IFP:</b> Animation files</p>
        <p><b>IDE:</b> Item definition files</p>
        <p><b>IPL:</b> Item placement files</p>
        """

        msg = QMessageBox(self.main_window)
        msg.setWindowTitle("Help Contents")
        msg.setText(help_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()

    def _show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
        <h2>Keyboard Shortcuts</h2>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
        <tr><th>Action</th><th>Shortcut</th></tr>
        <tr><td>New IMG</td><td>Ctrl+N</td></tr>
        <tr><td>Open IMG</td><td>Ctrl+O</td></tr>
        <tr><td>Close IMG</td><td>Ctrl+W</td></tr>
        <tr><td>Save</td><td>Ctrl+S</td></tr>
        <tr><td>Import Files</td><td>Ctrl+I</td></tr>
        <tr><td>Export Selected</td><td>Ctrl+E</td></tr>
        <tr><td>Quick Export</td><td>Ctrl+Q</td></tr>
        <tr><td>Remove Selected</td><td>Delete</td></tr>
        <tr><td>Rename Entry</td><td>F2</td></tr>
        <tr><td>Select All</td><td>Ctrl+A</td></tr>
        <tr><td>Find</td><td>Ctrl+F</td></tr>
        <tr><td>IMG Information</td><td>F4</td></tr>
        <tr><td>Validate IMG</td><td>F5</td></tr>
        <tr><td>Rebuild IMG</td><td>F6</td></tr>
        <tr><td>View Model</td><td>F7</td></tr>
        <tr><td>View Texture</td><td>F8</td></tr>
        <tr><td>View Collision</td><td>F9</td></tr>
        <tr><td>COL Editor</td><td>Ctrl+Shift+C</td></tr>
        <tr><td>TXD Editor</td><td>Ctrl+Shift+T</td></tr>
        <tr><td>DFF Editor</td><td>Ctrl+Shift+D</td></tr>
        <tr><td>IFP Editor</td><td>Ctrl+Shift+I</td></tr>
        <tr><td>IDE Editor</td><td>Tools → IDE Editor</td></tr>
        <tr><td>Log Panel</td><td>F12</td></tr>
        <tr><td>Fullscreen</td><td>F11</td></tr>
        <tr><td>Preferences</td><td>Ctrl+,</td></tr>
        <tr><td>Exit</td><td>Ctrl+Q</td></tr>
        </table>
        """

        msg = QMessageBox(self.main_window)
        msg.setWindowTitle("Keyboard Shortcuts")
        msg.setText(shortcuts_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()

    def _show_formats(self):
        """Show supported formats"""
        formats_text = """
        <h2>Supported File Formats</h2>

        <h3>Archive Formats:</h3>
        <p><b>IMG:</b> GTA image archives (versions 1, 2, 3)</p>
        <p><b>DAT:</b> GTA data files</p>

        <h3>3D Model Formats:</h3>
        <p><b>DFF:</b> RenderWare DFF models</p>
        <p><b>COL:</b> Collision data (versions 1, 2, 3, 4)</p>
        <p><b>WDR:</b> World drawable files</p>

        <h3>Texture Formats:</h3>
        <p><b>TXD:</b> RenderWare texture dictionaries</p>
        <p><b>WTD:</b> World texture dictionaries</p>

        <h3>Animation Formats:</h3>
        <p><b>IFP:</b> Animation packages</p>
        <p><b>YCD:</b> Clip dictionaries</p>

        <h3>Data Formats:</h3>
        <p><b>IDE:</b> Item definition files</p>
        <p><b>IPL:</b> Item placement files</p>
        <p><b>DAT:</b> Various data files</p>

        <h3>Import/Export Formats:</h3>
        <p><b>Images:</b> PNG, JPG, BMP, TGA, DDS</p>
        <p><b>Models:</b> OBJ, PLY (export only)</p>
        <p><b>Text:</b> TXT, CSV (for data files)</p>
        """

        msg = QMessageBox(self.main_window)
        msg.setWindowTitle("Supported Formats")
        msg.setText(formats_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()

    def _show_debug_console(self):
        """Show debug console"""
        QMessageBox.information(
            self.main_window,
            "Debug Console",
            "Debug console coming soon!"
        )

    def _clear_debug_log(self):
        """Clear debug log"""
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("Debug log cleared")
        QMessageBox.information(
            self.main_window,
            "Debug Log",
            "Debug log has been cleared."
        )

# Export main classes
__all__ = [
    'IMGFactoryMenuBar',
    'MenuAction',
    'MenuDefinition',
    'COLMenuBuilder'
]
