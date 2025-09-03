#this belongs in utils/ theme_button_system.py - Version: 1
# X-Seti - September02 2025 - IMG Factory 1.5 - Theme Button System for Settings Demo

"""
Theme Button System for Settings Demo - MOVED FROM GUI
Used only for demo/preview functions in app_settings_system.py
"""

# THEME-CONTROLLED BUTTON SYSTEM & STYLING UPDATES

# 1. BUTTON THEME TEMPLATES
def _get_button_theme_template(self, theme_name="default"):
    """Get button color templates based on theme"""
    
    if self._is_dark_theme():
        return {
            # Dark Theme Button Colors
            'create_action': '#2D4A4A',     # Dark teal for create/new actions
            'open_action': '#2D3A4F',       # Dark blue for open/load actions  
            'reload_action': '#3A4A2D',     # Dark green for refresh/reload
            'close_action': '#4A3A2D',      # Dark orange for close actions
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
            'reload_action': '#F9FBE7',     # Light green for refresh/reload  
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

# 2. UPDATED BUTTON DATA ARRAYS (Using theme templates)
def _get_img_buttons_data(self):
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

def _get_entry_buttons_data(self):
    """Get Entry buttons data with theme colors"""
    colors = self._get_button_theme_template()
    return [
        ("Import", "import", "document-import", colors['import_action'], "import_files"),
        ("Import via", "import_via", "document-import", colors['import_action'], "import_files_via"),
        ("Refresh", "update", "view-refresh", colors['reload_action'], "refresh_table"),
        ("Export", "export", "document-export", colors['export_action'], "export_selected"),
        ("Export via", "export_via", "document-export", colors['export_action'], "export_selected_via"),
        ("Quick Exp", "quick_export", "document-send", colors['export_action'], "quick_export_selected"),
        ("Remove", "remove", "edit-delete", colors['remove_action'], "remove_selected"),
        ("Remove via", "remove_via", "document-remvia", colors['remove_action'], "remove_via_entries"),
        ("Dump", "dump", "document-dump", colors['merge_action'], "dump_entries"),
        ("Rename", "rename", "edit-rename", colors['edit_action'], "rename_selected"),
        ("Replace", "replace", "edit-copy", colors['edit_action'], "replace_selected"),
        ("Select All", "select_all", "edit-select-all", colors['select_action'], "select_all_entries"),
        ("Inverse", "sel_inverse", "edit-select", colors['select_action'], "select_inverse"),
        ("Sort via", "sort", "view-sort", colors['select_action'], "sort_entries"),
        ("Pin selected", "pin_selected", "pin", colors['select_action'], "pin_selected_entries"),
    ]

def _get_options_buttons_data(self):
    """Get Options buttons data with theme colors"""
    colors = self._get_button_theme_template()
    return [
        ("Col Edit", "col_edit", "col-edit", colors['editor_col'], "edit_col_file"),
        ("Txd Edit", "txd_edit", "txd-edit", colors['editor_txd'], "edit_txd_file"),
        ("DFF Edit", "dff_edit", "dff-edit", colors['editor_dff'], "edit_dff_file"),
        ("IPF Edit", "ipf_edit", "ipf-edit", colors['editor_data'], "edit_ipf_file"),
        ("IDE Edit", "ide_edit", "ide-edit", colors['editor_map'], "edit_ide_file"),
        ("IPL Edit", "ipl_edit", "ipl-edit", colors['editor_map'], "edit_ipl_file"),
        ("DAT Edit", "dat_edit", "dat-edit", colors['editor_data'], "edit_dat_file"),
        ("     ", "space", "placeholder", colors['placeholder'], "useless_button"),
        ("Batch", "batch", "batch-edit", colors['editor_script'], "batch_process"),
    ]

# APPLY ALL THEMES METHOD
def apply_all_window_themes(self):
    """Apply theme styling to all windows - NEW"""
    self._apply_table_theme_styling()
    self._apply_log_theme_styling()
    self._apply_vertical_splitter_theme()
    self._apply_status_window_theme_styling()
    self._apply_file_list_window_theme_styling()
    
    # Apply to info bar if it exists
    if hasattr(self, 'info_bar'):
        self._apply_info_bar_theme_styling(self.info_bar)
