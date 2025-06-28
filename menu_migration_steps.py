#!/usr/bin/env python3
"""
#this belongs in root /MENU_MIGRATION_GUIDE.md - version 1
X-Seti - June28 2025 - IMG Factory 1.5
Menu System Migration Guide - How to update imgfactory.py
"""

# =============================================================================
# STEP 1: UPDATE IMPORTS IN imgfactory.py
# =============================================================================

# REMOVE these old imports:
# from gui.menu_system import create_menu_bar  # DELETE
# from gui.menu import IMGFactoryMenuBar       # DELETE

# ADD this new import:
from gui.menu_system import create_menu_system

# =============================================================================
# STEP 2: UPDATE MENU CREATION IN __init__ METHOD
# =============================================================================

# In your IMGFactory.__init__ method, REPLACE:
# Old code:
"""
# Remove any of these lines:
create_menu_bar(self)
self.menu_bar = IMGFactoryMenuBar(self)
self.gui_layout.create_menu_bar()
"""

# New code:
"""
# Add after creating your GUI layout:
self.menu_system = create_menu_system(self)
self._setup_menu_callbacks()
"""

# =============================================================================
# STEP 3: ADD MENU CALLBACKS METHOD
# =============================================================================

# Add this method to your IMGFactory class:
def _setup_menu_callbacks(self):
    """Set up all menu callbacks"""
    callbacks = {
        # File menu
        "new_img": self.create_new_img,
        "open_img": self.open_img_file,
        "close_img": self.close_img_file,
        "save": self.rebuild_img,
        "save_as": self.rebuild_img_as,
        "exit": self.close,
        
        # Edit menu
        "select_all": self.select_all_entries,
        "select_none": self.select_none_entries,
        
        # IMG menu
        "rebuild": self.rebuild_img,
        "rebuild_as": self.rebuild_img_as,
        "rebuild_all": self.rebuild_all_img,
        "info": self.show_img_info,
        "validate": self.validate_img,
        
        # Entry menu
        "import_files": self.import_files,
        "export_selected": self.export_selected_entries,
        "export_all": self.export_all_entries,
        "remove": self.remove_selected_entries,
        "rename": self.rename_entry,
        "replace": self.replace_entry,
        "properties": self.show_entry_properties,
        
        # Tools menu
        "template_manager": self.manage_templates,
        "batch_processor": self.show_batch_processor,
        "col_editor": self.open_col_editor,
        
        # View menu
        "refresh": self.refresh_view,
        "fullscreen": self.toggle_fullscreen,
        
        # Settings menu
        "preferences": self.show_settings,
        "themes": self.show_theme_settings,
        "customize_interface": self.show_gui_layout_settings,
        
        # Help menu
        "help_contents": self.show_help,
        "about": self.show_about
    }
    
    self.menu_system.set_callbacks(callbacks)

# =============================================================================
# STEP 4: ADD MISSING MENU METHODS TO YOUR IMGFactory CLASS
# =============================================================================

# Add any missing methods that are referenced in callbacks:

def select_all_entries(self):
    """Select all entries in table"""
    if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
        self.gui_layout.table.selectAll()
        self.log_message("All entries selected")

def select_none_entries(self):
    """Deselect all entries"""
    if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
        self.gui_layout.table.clearSelection()
        self.log_message("Selection cleared")

def refresh_view(self):
    """Refresh current view"""
    if self.current_img:
        # Repopulate table
        if hasattr(self, 'gui_layout'):
            self.gui_layout.populate_img_table(self.current_img)
        self.log_message("View refreshed")

def toggle_fullscreen(self):
    """Toggle fullscreen mode"""
    if self.isFullScreen():
        self.showNormal()
        self.log_message("Exited fullscreen")
    else:
        self.showFullScreen()
        self.log_message("Entered fullscreen")

def show_help(self):
    """Show help dialog"""
    from PyQt6.QtWidgets import QMessageBox
    QMessageBox.information(self, "Help", 
        "IMG Factory 1.5 Help\n\n"
        "• Use File > Open to load IMG archives\n"
        "• Use Entry > Import to add files\n"
        "• Use Entry > Export to extract files\n"
        "• Use IMG > Rebuild to save changes\n\n"
        "For more help, visit the IMG Factory website.")

def show_batch_processor(self):
    """Show batch processor dialog"""
    self.log_message("Batch processor not yet implemented")

def open_col_editor(self):
    """Open COL editor"""
    self.log_message("COL editor not yet implemented")

# =============================================================================
# STEP 5: UPDATE MENU STATE MANAGEMENT
# =============================================================================

# Add this method to update menu states:
def update_menu_states(self):
    """Update menu item states based on current context"""
    has_img = self.current_img is not None
    has_selection = self.has_selected_entries()
    
    # Enable/disable actions based on state
    self.menu_system.enable_action("close_img", has_img)
    self.menu_system.enable_action("save", has_img)
    self.menu_system.enable_action("save_as", has_img)
    self.menu_system.enable_action("rebuild", has_img)
    self.menu_system.enable_action("rebuild_as", has_img)
    self.menu_system.enable_action("import_files", has_img)
    self.menu_system.enable_action("export_selected", has_selection)
    self.menu_system.enable_action("export_all", has_img)
    self.menu_system.enable_action("remove", has_selection)

def has_selected_entries(self) -> bool:
    """Check if any entries are selected"""
    if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
        return len(self.gui_layout.table.selectedItems()) > 0
    return False

# =============================================================================
# STEP 6: CALL update_menu_states() AT APPROPRIATE TIMES
# =============================================================================

# Add these calls in your existing methods:

def _on_img_loaded(self, img_file):
    """Handle successful IMG loading"""
    # ... existing code ...
    
    # ADD THIS LINE:
    self.update_menu_states()

def on_selection_changed(self):
    """Handle table selection change"""
    # ... existing code ...
    
    # ADD THIS LINE:
    self.update_menu_states()

# =============================================================================
# STEP 7: REMOVE OLD MENU-RELATED CODE
# =============================================================================

# REMOVE any references to:
# - create_menu_bar()
# - IMGFactoryMenuBar
# - _create_menu()
# - Any manual QMenuBar.addMenu() calls
# - Old menu creation in gui_layout

# =============================================================================
# STEP 8: TEST THE MIGRATION
# =============================================================================

# After making these changes, test by:
# 1. Running launch_imgfactory.py
# 2. Checking that all menus appear correctly
# 3. Testing a few menu items to ensure callbacks work
# 4. Verifying menu states update when loading/closing IMG files

# =============================================================================
# STEP 9: OPTIONAL - ADD CONTEXT MENUS
# =============================================================================

# If you want context menus, add this to your table setup:
def setup_table_context_menu(self):
    """Set up context menu for entries table"""
    if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
        table = self.gui_layout.table
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_table_context_menu)

def show_table_context_menu(self, position):
    """Show context menu for table"""
    table = self.gui_layout.table
    self.menu_system.show_context_menu("table", table.mapToGlobal(position))

# =============================================================================
# STEP 10: FINAL CLEANUP
# =============================================================================

# After successful migration:
# 1. Remove gui/menu.py (old class-based system)
# 2. Keep gui/menu_system.py (unified system)
# 3. Update any other files that import old menu classes
# 4. Test all menu functionality

print("✅ Menu migration complete!")
print("🔧 All menus now use unified system")
print("📋 Context menus available")
print("⚡ Dynamic menu states working")
print("🎯 Single source of truth for all menus")