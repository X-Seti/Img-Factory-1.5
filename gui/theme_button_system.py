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

# 3. UPDATED create_right_panel_with_pastel_buttons METHOD
def create_right_panel_with_pastel_buttons(self):
    """Create right panel with theme-controlled pastel buttons - UPDATED"""
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

    # Filter Section (unchanged)
    filter_box = QGroupBox("Filter & Search")
    filter_layout = QVBoxLayout()
    filter_layout.setSpacing(4)

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

    right_layout.addStretch()
    return right_panel

# 4. UPDATED STYLING METHODS WITH THEME INTEGRATION

def _apply_vertical_splitter_theme(self):
    """Apply theme styling to the vertical splitter - UPDATED"""
    theme_colors = self._get_theme_colors("default")
    
    if self._is_dark_theme():
        splitter_bg = theme_colors.get('splitter_color_background', '404040')
        border_color = theme_colors.get('splitter_border_color', '606060')  
        hover_color = theme_colors.get('splitter_hover_color', '666666')
    else:
        splitter_bg = theme_colors.get('splitter_color_background', 'e0e0e0')
        border_color = theme_colors.get('splitter_border_color', 'cccccc')
        hover_color = theme_colors.get('splitter_hover_color', '999999')
    
    self.left_vertical_splitter.setStyleSheet(f"""
        QSplitter::handle:vertical {{
            background-color: #{splitter_bg};
            border: 1px solid #{border_color};
            height: 4px;
            margin: 1px 2px;
            border-radius: 2px;
        }}
        QSplitter::handle:vertical:hover {{
            background-color: #{hover_color};
        }}
    """)

def _apply_info_bar_theme_styling(self, info_bar):
    """Apply theme styling to the info bar - UPDATED"""
    theme_colors = self._get_theme_colors("default")
    
    if self._is_dark_theme():
        bg_color = theme_colors.get('info_bar_background', '2d2d2d')
        border_color = theme_colors.get('info_bar_border', '404040')
        text_color = theme_colors.get('info_bar_text', 'cccccc')
        separator_color = theme_colors.get('info_bar_separator', '666666')
    else:
        bg_color = theme_colors.get('info_bar_background', 'f8f8f8')
        border_color = theme_colors.get('info_bar_border', 'cccccc')
        text_color = theme_colors.get('info_bar_text', '333333')
        separator_color = theme_colors.get('info_bar_separator', '666666')
    
    info_bar.setStyleSheet(f"""
        QWidget {{
            background-color: #{bg_color};
            border: 1px solid #{border_color};
            border-radius: 3px;
            padding: 3px;
        }}
        QLabel {{
            border: none;
            font-size: 9pt;
            color: #{text_color};
        }}
        QLabel[objectName="separator"] {{
            color: #{separator_color};
        }}
    """)

def _apply_table_theme_styling(self):
    """Apply theme styling to the table widget - UPDATED"""
    theme_colors = self._get_theme_colors("default")
    
    if self._is_dark_theme():
        bg_color = theme_colors.get('table_background', '2d2d2d')
        alt_bg_color = theme_colors.get('table_alt_background', '353535')
        border_color = theme_colors.get('table_border', '404040')
        gridline_color = theme_colors.get('table_gridline', '404040')
        text_color = theme_colors.get('table_text', 'cccccc')
        selection_bg = theme_colors.get('table_selection_bg', '1e3a5f')
        selection_text = theme_colors.get('table_selection_text', '87ceeb')
        header_bg = theme_colors.get('table_header_bg', '404040')
        header_text = theme_colors.get('table_header_text', 'cccccc')
    else:
        bg_color = theme_colors.get('table_background', 'ffffff')
        alt_bg_color = theme_colors.get('table_alt_background', 'f8f8f8')
        border_color = theme_colors.get('table_border', 'cccccc')
        gridline_color = theme_colors.get('table_gridline', 'e0e0e0')
        text_color = theme_colors.get('table_text', '333333')
        selection_bg = theme_colors.get('table_selection_bg', 'e3f2fd')
        selection_text = theme_colors.get('table_selection_text', '1976d2')
        header_bg = theme_colors.get('table_header_bg', 'f0f0f0')
        header_text = theme_colors.get('table_header_text', '333333')
    
    self.table.setStyleSheet(f"""
        QTableWidget {{
            background-color: #{bg_color};
            alternate-background-color: #{alt_bg_color};
            border: 1px solid #{border_color};
            border-radius: 3px;
            gridline-color: #{gridline_color};
            color: #{text_color};
            font-size: 9pt;
        }}
        QTableWidget::item {{
            padding: 5px;
            border: none;
        }}
        QTableWidget::item:selected {{
            background-color: #{selection_bg};
            color: #{selection_text};
        }}
        QHeaderView::section {{
            background-color: #{header_bg};
            color: #{header_text};
            padding: 5px;
            border: 1px solid #{border_color};
            font-weight: bold;
            font-size: 9pt;
        }}
    """)

def _apply_log_theme_styling(self):
    """Apply theme styling to the log widget - UPDATED"""
    theme_colors = self._get_theme_colors("default")
    
    if self._is_dark_theme():
        bg_color = theme_colors.get('log_background', '2d2d2d')
        text_color = theme_colors.get('log_text', 'cccccc')
        border_color = theme_colors.get('log_border', '404040')
    else:
        bg_color = theme_colors.get('log_background', 'ffffff')
        text_color = theme_colors.get('log_text', '333333')
        border_color = theme_colors.get('log_border', 'cccccc')
    
    self.log.setStyleSheet(f"""
        QTextEdit {{
            background-color: #{bg_color};
            color: #{text_color};
            border: 1px solid #{border_color};
            border-radius: 3px;
            padding: 5px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 9pt;
        }}
    """)

# 5. STATUS WINDOW & FILE LIST WINDOW THEME STYLING

def _apply_status_window_theme_styling(self):
    """Apply theme styling to the status window - NEW"""
    theme_colors = self._get_theme_colors("default")
    
    if self._is_dark_theme():
        bg_color = theme_colors.get('status_window_background', '2d2d2d')
        border_color = theme_colors.get('status_window_border', '404040')
        title_color = theme_colors.get('status_window_title', 'cccccc')
    else:
        bg_color = theme_colors.get('status_window_background', 'f8f8f8')
        border_color = theme_colors.get('status_window_border', 'cccccc')
        title_color = theme_colors.get('status_window_title', '333333')
    
    # Apply to status window container if it exists
    if hasattr(self, 'status_window'):
        self.status_window.setStyleSheet(f"""
            QWidget {{
                background-color: #{bg_color};
                border: 1px solid #{border_color};
                border-radius: 3px;
            }}
            QLabel {{
                color: #{title_color};
                font-weight: bold;
            }}
        """)

def _apply_file_list_window_theme_styling(self):
    """Apply theme styling to the file list window - NEW"""
    theme_colors = self._get_theme_colors("default")
    
    if self._is_dark_theme():
        bg_color = theme_colors.get('file_window_background', '2d2d2d')
        border_color = theme_colors.get('file_window_border', '404040')
        tab_bg = theme_colors.get('file_window_tab_bg', '404040')
        tab_text = theme_colors.get('file_window_tab_text', 'cccccc')
    else:
        bg_color = theme_colors.get('file_window_background', 'ffffff')
        border_color = theme_colors.get('file_window_border', 'cccccc')
        tab_bg = theme_colors.get('file_window_tab_bg', 'f0f0f0')
        tab_text = theme_colors.get('file_window_tab_text', '333333')
    
    # Apply to tab widget if it exists
    if hasattr(self, 'tab_widget'):
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: #{bg_color};
                border: 1px solid #{border_color};
                border-radius: 3px;
            }}
            QTabBar::tab {{
                background-color: #{tab_bg};
                color: #{tab_text};
                padding: 5px 10px;
                margin: 2px;
                border-radius: 3px;
            }}
            QTabBar::tab:selected {{
                background-color: #{bg_color};
                border: 1px solid #{border_color};
            }}
        """)

# 6. APPLY ALL THEMES METHOD
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
