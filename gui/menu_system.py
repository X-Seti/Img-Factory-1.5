#this belongs in gui/ menu_system.py
# $vers" X-Seti - June26, 2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

#!/usr/bin/env python3
"""
IMG Factory Menu System - Menu Bar and Keyboard Shortcuts
Handles all menu creation and keyboard shortcuts
"""

from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtCore import Qt


def create_menu_bar(main_window):
    """Create and configure the main menu bar"""
    menubar = main_window.menuBar()
    
    # Get settings for icon display
    show_icons = True
    if hasattr(main_window, 'app_settings') and main_window.app_settings:
        show_icons = main_window.app_settings.current_settings.get("show_menu_icons", True)
    
    # Create all menus
    _create_file_menu(menubar, main_window, show_icons)
    _create_edit_menu(menubar, main_window, show_icons)
    _create_img_menu(menubar, main_window, show_icons)
    _create_entry_menu(menubar, main_window, show_icons)
    _create_tools_menu(menubar, main_window, show_icons)
    _create_view_menu(menubar, main_window, show_icons)
    _create_settings_menu(menubar, main_window, show_icons)
    _create_help_menu(menubar, main_window, show_icons)


def _create_file_menu(menubar, main_window, show_icons):
    """Create File menu"""
    file_menu = menubar.addMenu("&File")
    
    # New IMG Archive
    new_action = QAction("&New IMG Archive...", main_window)
    if show_icons:
        new_action.setIcon(QIcon.fromTheme("document-new"))
    new_action.setShortcut(QKeySequence.StandardKey.New)  # Ctrl+N
    new_action.setStatusTip("Create a new IMG archive")
    if hasattr(main_window, 'create_new_img'):
        new_action.triggered.connect(main_window.create_new_img)
    file_menu.addAction(new_action)
    
    file_menu.addSeparator()
    
    # Open IMG Archive
    open_action = QAction("&Open IMG Archive...", main_window)
    if show_icons:
        open_action.setIcon(QIcon.fromTheme("document-open"))
    open_action.setShortcut(QKeySequence.StandardKey.Open)  # Ctrl+O
    open_action.setStatusTip("Open an existing IMG archive")
    if hasattr(main_window, 'open_img_file'):
        open_action.triggered.connect(main_window.open_img_file)
    file_menu.addAction(open_action)
    
    # Recent Files submenu
    recent_menu = file_menu.addMenu("📂 Recent Files")
    if hasattr(main_window, 'populate_recent_files'):
        main_window.populate_recent_files(recent_menu)
    
    file_menu.addSeparator()
    
    # Close IMG Archive
    close_action = QAction("&Close Archive", main_window)
    if show_icons:
        close_action.setIcon(QIcon.fromTheme("window-close"))
    close_action.setShortcut(QKeySequence.StandardKey.Close)  # Ctrl+W
    close_action.setStatusTip("Close the current IMG archive")
    if hasattr(main_window, 'close_img_file'):
        close_action.triggered.connect(main_window.close_img_file)
    file_menu.addAction(close_action)
    
    file_menu.addSeparator()
    
    # Exit
    exit_action = QAction("E&xit", main_window)
    if show_icons:
        exit_action.setIcon(QIcon.fromTheme("application-exit"))
    exit_action.setShortcut(QKeySequence.StandardKey.Quit)  # Ctrl+Q
    exit_action.setStatusTip("Exit IMG Factory")
    exit_action.triggered.connect(main_window.close)
    file_menu.addAction(exit_action)


def _create_edit_menu(menubar, main_window, show_icons):
    """Create Edit menu"""
    edit_menu = menubar.addMenu("&Edit")
    
    # Select All
    select_all_action = QAction("Select &All Entries", main_window)
    if show_icons:
        select_all_action.setIcon(QIcon.fromTheme("edit-select-all"))
    select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)  # Ctrl+A
    select_all_action.setStatusTip("Select all entries in the table")
    if hasattr(main_window, 'select_all_entries'):
        select_all_action.triggered.connect(main_window.select_all_entries)
    edit_menu.addAction(select_all_action)
    
    # Invert Selection
    invert_action = QAction("&Invert Selection", main_window)
    invert_action.setShortcut("Ctrl+I")
    invert_action.setStatusTip("Invert the current selection")
    if hasattr(main_window, 'invert_selection'):
        invert_action.triggered.connect(main_window.invert_selection)
    edit_menu.addAction(invert_action)
    
    edit_menu.addSeparator()
    
    # Find
    find_action = QAction("&Find...", main_window)
    if show_icons:
        find_action.setIcon(QIcon.fromTheme("edit-find"))
    find_action.setShortcut(QKeySequence.StandardKey.Find)  # Ctrl+F
    find_action.setStatusTip("Search for entries")
    if hasattr(main_window, 'show_search_dialog'):
        find_action.triggered.connect(main_window.show_search_dialog)
    edit_menu.addAction(find_action)


def _create_img_menu(menubar, main_window, show_icons):
    """Create IMG menu"""
    img_menu = menubar.addMenu("&IMG")
    
    # Rebuild
    rebuild_action = QAction("&Rebuild", main_window)
    if show_icons:
        rebuild_action.setIcon(QIcon.fromTheme("view-refresh"))
    rebuild_action.setShortcut("Ctrl+R")
    rebuild_action.setStatusTip("Rebuild the current IMG archive")
    if hasattr(main_window, 'rebuild_img'):
        rebuild_action.triggered.connect(main_window.rebuild_img)
    img_menu.addAction(rebuild_action)
    
    # Rebuild As
    rebuild_as_action = QAction("Rebuild &As...", main_window)
    if show_icons:
        rebuild_as_action.setIcon(QIcon.fromTheme("document-save-as"))
    rebuild_as_action.setShortcut("Ctrl+Shift+R")
    rebuild_as_action.setStatusTip("Rebuild the IMG archive with a new name")
    if hasattr(main_window, 'rebuild_img_as'):
        rebuild_as_action.triggered.connect(main_window.rebuild_img_as)
    img_menu.addAction(rebuild_as_action)
    
    img_menu.addSeparator()
    
    # Merge
    merge_action = QAction("&Merge with...", main_window)
    if show_icons:
        merge_action.setIcon(QIcon.fromTheme("document-merge"))
    merge_action.setStatusTip("Merge another IMG archive into this one")
    if hasattr(main_window, 'merge_img'):
        merge_action.triggered.connect(main_window.merge_img)
    img_menu.addAction(merge_action)
    
    # Split
    split_action = QAction("&Split...", main_window)
    if show_icons:
        split_action.setIcon(QIcon.fromTheme("edit-cut"))
    split_action.setStatusTip("Split the IMG archive into multiple files")
    if hasattr(main_window, 'split_img'):
        split_action.triggered.connect(main_window.split_img)
    img_menu.addAction(split_action)
    
    img_menu.addSeparator()
    
    # Convert
    convert_action = QAction("&Convert Format...", main_window)
    if show_icons:
        convert_action.setIcon(QIcon.fromTheme("document-save-as"))
    convert_action.setStatusTip("Convert IMG to different format/version")
    if hasattr(main_window, 'convert_img_format'):
        convert_action.triggered.connect(main_window.convert_img_format)
    img_menu.addAction(convert_action)
    
    img_menu.addSeparator()
    
    # Properties
    properties_action = QAction("&Properties...", main_window)
    if show_icons:
        properties_action.setIcon(QIcon.fromTheme("document-properties"))
    properties_action.setShortcut("Alt+Return")
    properties_action.setStatusTip("Show IMG archive properties")
    if hasattr(main_window, 'show_img_properties'):
        properties_action.triggered.connect(main_window.show_img_properties)
    img_menu.addAction(properties_action)


def _create_entry_menu(menubar, main_window, show_icons):
    """Create Entry menu"""
    entry_menu = menubar.addMenu("&Entry")
    
    # Import
    import_action = QAction("&Import Files...", main_window)
    if show_icons:
        import_action.setIcon(QIcon.fromTheme("document-import"))
    import_action.setShortcut("Ctrl+Shift+I")
    import_action.setStatusTip("Import files into the IMG archive")
    if hasattr(main_window, 'import_files'):
        import_action.triggered.connect(main_window.import_files)
    entry_menu.addAction(import_action)
    
    entry_menu.addSeparator()
    
    # Export Selected
    export_selected_action = QAction("&Export Selected...", main_window)
    if show_icons:
        export_selected_action.setIcon(QIcon.fromTheme("document-export"))
    export_selected_action.setShortcut("Ctrl+E")
    export_selected_action.setStatusTip("Export selected entries")
    if hasattr(main_window, 'export_selected_entries'):
        export_selected_action.triggered.connect(main_window.export_selected_entries)
    entry_menu.addAction(export_selected_action)
    
    # Export All
    export_all_action = QAction("Export &All...", main_window)
    export_all_action.setShortcut("Ctrl+Shift+E")
    export_all_action.setStatusTip("Export all entries")
    if hasattr(main_window, 'export_all_entries'):
        export_all_action.triggered.connect(main_window.export_all_entries)
    entry_menu.addAction(export_all_action)
    
    entry_menu.addSeparator()
    
    # Remove Selected
    remove_action = QAction("&Remove Selected", main_window)
    if show_icons:
        remove_action.setIcon(QIcon.fromTheme("edit-delete"))
    remove_action.setShortcut(QKeySequence.StandardKey.Delete)
    remove_action.setStatusTip("Remove selected entries from the archive")
    if hasattr(main_window, 'remove_selected_entries'):
        remove_action.triggered.connect(main_window.remove_selected_entries)
    entry_menu.addAction(remove_action)
    
    entry_menu.addSeparator()
    
    # Rename
    rename_action = QAction("Re&name...", main_window)
    rename_action.setShortcut("F2")
    rename_action.setStatusTip("Rename the selected entry")
    if hasattr(main_window, 'rename_entry'):
        rename_action.triggered.connect(main_window.rename_entry)
    entry_menu.addAction(rename_action)
    
    # Replace
    replace_action = QAction("&Replace...", main_window)
    replace_action.setShortcut("Ctrl+H")
    replace_action.setStatusTip("Replace the selected entry with a new file")
    if hasattr(main_window, 'replace_entry'):
        replace_action.triggered.connect(main_window.replace_entry)
    entry_menu.addAction(replace_action)


def _create_tools_menu(menubar, main_window, show_icons):
    """Create Tools menu"""
    tools_menu = menubar.addMenu("&Tools")
    
    # Validate Archive
    validate_action = QAction("&Validate Archive", main_window)
    if show_icons:
        validate_action.setIcon(QIcon.fromTheme("tools-check-spelling"))
    validate_action.setShortcut("F9")
    validate_action.setStatusTip("Validate the IMG archive for errors")
    if hasattr(main_window, 'validate_img'):
        validate_action.triggered.connect(main_window.validate_img)
    tools_menu.addAction(validate_action)
    
    tools_menu.addSeparator()
    
    # Template Manager
    templates_action = QAction("&Template Manager...", main_window)
    if show_icons:
        templates_action.setIcon(QIcon.fromTheme("folder-templates"))
    templates_action.setStatusTip("Manage IMG creation templates")
    if hasattr(main_window, 'manage_templates'):
        templates_action.triggered.connect(main_window.manage_templates)
    tools_menu.addAction(templates_action)
    
    # Quick Start Wizard
    wizard_action = QAction("&Quick Start Wizard...", main_window)
    if show_icons:
        wizard_action.setIcon(QIcon.fromTheme("tools-wizard"))
    wizard_action.setStatusTip("Launch the quick start wizard")
    if hasattr(main_window, 'show_quick_start_wizard'):
        wizard_action.triggered.connect(main_window.show_quick_start_wizard)
    tools_menu.addAction(wizard_action)


def _create_view_menu(menubar, main_window, show_icons):
    """Create View menu"""
    view_menu = menubar.addMenu("&View")
    
    # Refresh
    refresh_action = QAction("&Refresh", main_window)
    if show_icons:
        refresh_action.setIcon(QIcon.fromTheme("view-refresh"))
    refresh_action.setShortcut("F5")
    refresh_action.setStatusTip("Refresh the entry list")
    if hasattr(main_window, 'refresh_table'):
        refresh_action.triggered.connect(main_window.refresh_table)
    view_menu.addAction(refresh_action)
    
    view_menu.addSeparator()
    
    # Show/Hide columns submenu
    columns_menu = view_menu.addMenu("&Columns")
    if hasattr(main_window, 'toggle_column_visibility'):
        column_names = ["ID", "Type", "Name", "Offset", "Size", "Version", "Compression", "Status"]
        for i, col_name in enumerate(column_names):
            action = columns_menu.addAction(f"Show {col_name}")
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(lambda checked, col=i: main_window.toggle_column_visibility(col, checked))
    
    view_menu.addSeparator()
    
    # Canvas Display Settings
    canvas_menu = view_menu.addMenu("&Canvas Display")
    
    # Grid options
    grid_action = canvas_menu.addAction("Show &Grid")
    grid_action.setCheckable(True)
    grid_action.setChecked(True)
    grid_action.setShortcut("Ctrl+G")
    
    # Grid style submenu
    grid_style_menu = canvas_menu.addMenu("Grid &Style")
    grid_styles = ["Dotted Line", "Solid Line", "Dashed Line"]
    for style in grid_styles:
        action = grid_style_menu.addAction(style)
        action.setCheckable(True)
        if style == "Dotted Line":
            action.setChecked(True)
    
    # Colors submenu
    colors_menu = canvas_menu.addMenu("&Colors")
    colors_menu.addAction("Background Color...")
    colors_menu.addAction("Foreground Color...")
    colors_menu.addAction("Grid Color...")


def _create_settings_menu(menubar, main_window, show_icons):
    """Create Settings menu"""
    settings_menu = menubar.addMenu("&Settings")
    
    # Preferences
    prefs_action = QAction("&Preferences...", main_window)
    if show_icons:
        prefs_action.setIcon(QIcon.fromTheme("preferences-system"))
    prefs_action.setShortcut("Ctrl+,")
    prefs_action.setStatusTip("Open application preferences")
    if hasattr(main_window, 'show_preferences'):
        prefs_action.triggered.connect(main_window.show_preferences)
    settings_menu.addAction(prefs_action)
    
    settings_menu.addSeparator()
    
    # Theme submenu
    theme_menu = settings_menu.addMenu("&Theme")
    if hasattr(main_window, 'change_theme'):
        themes = ["IMG Factory", "IMG Factory Dark", "LCARS", "Windows 95", "Clean Light"]
        for theme in themes:
            action = theme_menu.addAction(theme)
            action.triggered.connect(lambda checked, t=theme: main_window.change_theme(t))


def _create_help_menu(menubar, main_window, show_icons):
    """Create Help menu"""
    help_menu = menubar.addMenu("&Help")
    
    # About
    about_action = QAction("&About IMG Factory...", main_window)
    if show_icons:
        about_action.setIcon(QIcon.fromTheme("help-about"))
    about_action.setStatusTip("About IMG Factory")
    if hasattr(main_window, 'show_about'):
        about_action.triggered.connect(main_window.show_about)
    help_menu.addAction(about_action)
    
    # About Qt
    about_qt_action = QAction("About &Qt...", main_window)
    about_qt_action.triggered.connect(lambda: main_window.app.aboutQt())
    help_menu.addAction(about_qt_action)


# Keyboard shortcuts registration
def register_global_shortcuts(main_window):
    """Register global keyboard shortcuts"""
    shortcuts = [
        ("Ctrl+F", "show_search_dialog"),
        ("Ctrl+G", "toggle_grid_display"),
        ("F1", "show_help"),
        ("F11", "toggle_fullscreen"),
        ("Escape", "cancel_operation"),
    ]
    
    for shortcut, method_name in shortcuts:
        if hasattr(main_window, method_name):
            action = QAction(main_window)
            action.setShortcut(shortcut)
            action.triggered.connect(getattr(main_window, method_name))
            main_window.addAction(action)
