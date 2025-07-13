#this belongs in gui/ gui_layout.py - Version: 6
# X-Seti - July13 2025 - Img Factory 1.5  
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Factory GUI Layout - MASTER FILE with YOUR EXACT ORIGINAL THEME
Preserves ALL your original pastel colors, button layout, and styling
Only fixes: "Update List" → "Refresh", button conflicts, adds search
"""

import os
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QLabel,
    QPushButton, QGroupBox, QLineEdit, QComboBox, QCheckBox,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QShortcut, QKeySequence

# Import utilities from cleaned panel_controls
from .panel_controls import (
    create_pastel_button, lighten_color, darken_color, get_short_text,
    update_button_states, placeholder_function
)

# SEARCH DIALOG - WORKING SEARCH FUNCTIONALITY

class SearchDialog(QDialog):
    """Advanced search dialog for finding entries"""
    
    search_requested = pyqtSignal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Entries - IMG Factory")
        self.setMinimumSize(400, 300)
        self.setModal(True)
        self._create_ui()
    
    def _create_ui(self):
        """Create search dialog UI"""
        layout = QVBoxLayout(self)
        
        # Search input
        search_group = QGroupBox("Search Criteria")
        search_layout = QVBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        self.search_input.returnPressed.connect(self._do_search)
        search_layout.addWidget(self.search_input)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.case_sensitive_check = QCheckBox("Case sensitive")
        options_layout.addWidget(self.case_sensitive_check)
        
        self.whole_word_check = QCheckBox("Whole word")
        options_layout.addWidget(self.whole_word_check)
        
        self.regex_check = QCheckBox("Regular expression")
        options_layout.addWidget(self.regex_check)
        
        search_layout.addLayout(options_layout)
        
        # File type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("File type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "All Files", "Models (DFF)", "Textures (TXD)",
            "Collision (COL)", "Animation (IFP)", "Audio (WAV)", "Scripts (SCM)"
        ])
        type_layout.addWidget(self.type_combo)
        search_layout.addLayout(type_layout)
        
        layout.addWidget(search_group)
        
        # Results
        self.results_label = QLabel("Enter search criteria and click Find")
        layout.addWidget(self.results_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.find_btn = QPushButton("Find")
        self.find_btn.clicked.connect(self._do_search)
        self.find_btn.setDefault(True)
        button_layout.addWidget(self.find_btn)
        
        self.find_next_btn = QPushButton("Find Next")
        self.find_next_btn.setEnabled(False)
        button_layout.addWidget(self.find_next_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on search input
        self.search_input.setFocus()
    
    def _do_search(self):
        """Perform search"""
        search_text = self.search_input.text().strip()
        if not search_text:
            return
        
        options = {
            'case_sensitive': self.case_sensitive_check.isChecked(),
            'whole_word': self.whole_word_check.isChecked(),
            'regex': self.regex_check.isChecked(),
            'file_type': self.type_combo.currentText()
        }
        
        self.search_requested.emit(search_text, options)
        self.results_label.setText(f"Searching for '{search_text}'...")
        self.find_next_btn.setEnabled(True)


# MAIN GUI LAYOUT CLASS - WITH YOUR EXACT ORIGINAL THEME

class IMGFactoryGUILayout(QWidget):
    """
    MASTER GUI Layout Class - With YOUR EXACT ORIGINAL THEME PRESERVED
    Only fixes conflicts, adds search, changes "Update List" → "Refresh"
    """
    
    # Signals
    entry_selected = pyqtSignal(int)
    entries_changed = pyqtSignal()
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Initialize components
        self.table = None
        self.log = None  
        self.status_label = None
        self.main_splitter = None
        self.search_input = None
        self.search_dialog = None
        self.current_search_matches = []
        self.current_search_index = -1
        
        # Button references
        self.img_buttons = []
        self.entry_buttons = []
        self.tool_buttons = []
        
        # Create the layout
        self._create_main_layout()
        self._setup_search_functionality() 
        self._apply_theme_styling()
    
    def _create_main_layout(self):
        """Create the main layout structure"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        # Main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Table and log
        left_widget = self._create_left_panel()
        self.main_splitter.addWidget(left_widget)
        
        # Right side - Button panels with YOUR EXACT THEME
        right_widget = self._create_right_panel_with_exact_theme()
        self.main_splitter.addWidget(right_widget)
        
        # Set initial splitter sizes
        self.main_splitter.setSizes([600, 300])
        
        layout.addWidget(self.main_splitter)
    
    def _create_left_panel(self):
        """Create left panel with table and log"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        
        # Quick search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Quick Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search entries...")
        self.search_input.textChanged.connect(self._quick_search)
        search_layout.addWidget(self.search_input)
        
        advanced_search_btn = QPushButton("Advanced...")
        advanced_search_btn.clicked.connect(self._show_advanced_search)
        search_layout.addWidget(advanced_search_btn)
        
        left_layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Size", "Offset"])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        left_layout.addWidget(self.table, 2)  # Table takes 2/3 of space
        
        # Status and log section
        status_log_widget = self._create_status_log_section()
        left_layout.addWidget(status_log_widget, 1)  # Log takes 1/3 of space
        
        return left_widget
    
    def _create_status_log_section(self):
        """Create status and log section"""
        status_window = QWidget()
        status_layout = QVBoxLayout(status_window)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(2)
        
        # Status label
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Activity Log"))
        title_layout.addStretch()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #e8f5e8;
                border: 1px solid #4caf50;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 8pt;
                color: #2e7d32;
            }
        """)
        title_layout.addWidget(self.status_label)
        
        status_layout.addLayout(title_layout)
        
        # Log with scrollbars
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Activity log will appear here...")
        self.log.setMaximumHeight(120)
        
        # Enable scrollbars for log
        self.log.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.log.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        status_layout.addWidget(self.log)
        
        return status_window
    
    def _create_right_panel_with_exact_theme(self):
        """
        RIGHT PANEL WITH YOUR EXACT ORIGINAL THEME
        Using your exact colors from panel_controls.py and pastel_theme.json
        """
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(6)

        # IMG, COL Files Section - YOUR EXACT COLORS
        img_box = QGroupBox("IMG, COL Files")
        img_layout = QGridLayout()
        img_layout.setSpacing(2)
        img_buttons_data = [
            ("New", "new", "document-new", "#EEFAFA", "create_new_img"),
            ("Open", "open", "document-open", "#E3F2FD", "open_img_file"),
            ("Close", "close", "window-close", "#FFF3E0", "close_img_file"),
            ("Close All", "close_all", "edit-clear", "#FFF3E0", "close_all_img"),
            ("Rebuild", "rebuild", "view-refresh", "#E8F5E8", "rebuild_img"),
            ("Rebuild As", "rebuild_as", "document-save-as", "#E8F5E8", "rebuild_img_as"),
            ("Rebuild All", "rebuild_all", "document-save", "#E8F5E8", "rebuild_all_img"),
            ("Merge", "merge", "document-merge", "#F3E5F5", "merge_img"),
            ("Split", "split", "edit-cut", "#F3E5F5", "split_img"),
            ("Convert", "convert", "transform", "#FFF8E1", "convert_img_format"),
        ]
        
        # Create IMG buttons with YOUR EXACT COLORS
        for i, (label, action_type, icon, color, method_name) in enumerate(img_buttons_data):
            btn = create_pastel_button(self.main_window, label, action_type, icon, color, method_name)
            btn.full_text = label
            btn.short_text = get_short_text(label)
            self.img_buttons.append(btn)
            img_layout.addWidget(btn, i // 3, i % 3)
        
        img_box.setLayout(img_layout)
        right_layout.addWidget(img_box)

        # File Entries Section - YOUR EXACT COLORS + FIXED "Refresh"
        entries_box = QGroupBox("File Entries")
        entries_layout = QGridLayout()
        entries_layout.setSpacing(2)
        entry_buttons_data = [
            ("Import", "import", "document-import", "#E1F5FE", "import_files"),
            ("Import via", "import_via", "document-import", "#E1F5FE", "import_files_via"),
            ("🔄 Refresh", "update", "view-refresh", "#F9FBE7", "refresh_table"),  # FIXED: Was "Update list"
            ("Export", "export", "document-export", "#E0F2F1", "export_selected"),
            ("Export via", "export_via", "document-export", "#E0F2F1", "export_selected_via"),
            ("Quick Export", "quick_export", "document-export", "#E0F2F1", "quick_export_selected"),
            ("Remove", "remove", "edit-delete", "#FFEBEE", "remove_selected"),
            ("Remove via", "remove_via", "edit-delete", "#FFEBEE", "remove_via_entries"),  # FIXED: Add remove via functionality
            ("Dump", "dump", "document-export", "#E0F2F1", "dump_all_entries"),
            ("Pin selected", "pin", "view-pin", "#FCE4EC", "pin_selected_entries"),
            ("Rename", "rename", "edit", "#FFF8E1", "rename_selected_entry"),
            ("Replace", "replace", "edit-paste", "#FFF8E1", "replace_selected_entry"),
        ]
        
        # Create Entry buttons with YOUR EXACT COLORS
        for i, (label, action_type, icon, color, method_name) in enumerate(entry_buttons_data):
            btn = create_pastel_button(self.main_window, label, action_type, icon, color, method_name)
            btn.full_text = label
            btn.short_text = get_short_text(label)
            self.entry_buttons.append(btn)
            entries_layout.addWidget(btn, i // 3, i % 3)
        
        entries_box.setLayout(entries_layout)
        right_layout.addWidget(entries_box)

        # Editing Options Section - YOUR EXACT COLORS
        options_box = QGroupBox("Editing Options")
        options_layout = QGridLayout()
        options_layout.setSpacing(2)
        options_buttons_data = [
            ("Col Edit", "col_edit", "col-edit", "#E3F2FD", "edit_col_file"),
            ("Txd Edit", "txd_edit", "txd-edit", "#F8BBD9", "edit_txd_file"),
            ("Dff Edit", "dff_edit", "dff-edit", "#E1F5FE", "edit_dff_file"),
            ("Ipf Edit", "ipf_edit", "ipf-edit", "#FFF3E0", "edit_ipf_file"),
            ("IDE Edit", "ide_edit", "ide-edit", "#F8BBD9", "edit_ide_file"),
            ("IPL Edit", "ipl_edit", "ipl-edit", "#E1F5FE", "edit_ipl_file"),
            ("Dat Edit", "dat_edit", "dat-edit", "#E3F2FD", "edit_dat_file"),
            ("Zons Cull Ed", "zones_cull", "zones-cull", "#E8F5E8", "edit_zones_cull"),
            ("Weap Edit", "weap_edit", "weap-edit", "#E1F5FE", "edit_weap_file"),
            ("Vehi Edit", "vehi_edit", "vehi-edit", "#E3F2FD", "edit_vehi_file"),
            ("Peds Edit", "peds_edit", "peds-edit", "#F8BBD9", "edit_peds_file"),
            ("Radar Map", "radar_map", "radar-map", "#F8BBD9", "edit_radar_map"),
            ("Paths Map", "paths_map", "paths-map", "#E1F5FE", "edit_paths_map"),
            ("Waterpro", "timecyc", "timecyc", "#E3F2FD", "edit_waterpro"),
            ("Weather", "timecyc", "timecyc", "#E0F2F1", "edit_weather"),
            ("Handling", "handling", "handling", "#E4E3ED", "edit_handling"),
            ("Objects", "ojs_breakble", "ojs-breakble", "#FFE0B2", "edit_objects"),
        ]
        
        # Create Editing Options buttons with YOUR EXACT COLORS
        for i, (label, action_type, icon, color, method_name) in enumerate(options_buttons_data):
            btn = create_pastel_button(self.main_window, label, action_type, icon, color, method_name)
            btn.full_text = label
            btn.short_text = get_short_text(label)
            options_layout.addWidget(btn, i // 3, i % 3)
        
        options_box.setLayout(options_layout)
        right_layout.addWidget(options_box)

        # Filter & Search Section - YOUR EXACT LAYOUT
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
        
        # Add working search button
        search_advanced_btn = QPushButton("🔍 Advanced Search")
        search_advanced_btn.clicked.connect(self._show_advanced_search)
        filter_layout.addWidget(search_advanced_btn)
        
        filter_box.setLayout(filter_layout)
        right_layout.addWidget(filter_box)

        # Add stretch to push everything up - YOUR EXACT LAYOUT
        right_layout.addStretch()

        return right_panel
    

    # SEARCH FUNCTIONALITY - BUILT-IN AND WORKING

    def _setup_search_functionality(self):
        """Set up search functionality with keyboard shortcuts"""
        try:
            self.search_dialog = None
            self.current_search_matches = []
            self.current_search_index = -1
            
            # Create search shortcuts
            self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
            self.search_shortcut.activated.connect(self._show_advanced_search)
            
            self.find_next_shortcut = QShortcut(QKeySequence("F3"), self)
            self.find_next_shortcut.activated.connect(self._find_next)
            
            self.find_prev_shortcut = QShortcut(QKeySequence("Shift+F3"), self)
            self.find_prev_shortcut.activated.connect(self._find_previous)
            
        except Exception as e:
            self.main_window.log_message(f"❌ Search setup error: {str(e)}")
    
    def _quick_search(self, text: str):
        """Quick search functionality"""
        if not text.strip() or not self.table:
            self._clear_search_highlighting()
            return
        
        try:
            matches = []
            text = text.lower()
            
            for row in range(self.table.rowCount()):
                name_item = self.table.item(row, 0)
                if name_item and text in name_item.text().lower():
                    matches.append(row)
            
            # Highlight matches
            self._highlight_search_matches(matches)
            
            if matches:
                self.main_window.log_message(f"🔍 Found {len(matches)} matches")
            
        except Exception as e:
            self.main_window.log_message(f"❌ Quick search error: {str(e)}")
    
    def _show_advanced_search(self):
        """Show advanced search dialog"""
        try:
            if not self.search_dialog:
                self.search_dialog = SearchDialog(self)
                self.search_dialog.search_requested.connect(self._perform_advanced_search)
            
            self.search_dialog.show()
            self.search_dialog.raise_()
            
        except Exception as e:
            self.main_window.log_message(f"❌ Advanced search error: {str(e)}")
    
    def _perform_advanced_search(self, search_text: str, options: dict):
        """Perform advanced search with options"""
        try:
            if not self.table or not search_text.strip():
                return
            
            matches = []
            
            # Apply case sensitivity
            if not options.get('case_sensitive', False):
                search_text = search_text.lower()
            
            for row in range(self.table.rowCount()):
                name_item = self.table.item(row, 0)
                type_item = self.table.item(row, 1)
                
                if not name_item:
                    continue
                
                entry_name = name_item.text()
                entry_type = type_item.text() if type_item else ""
                
                # Apply case sensitivity
                if not options.get('case_sensitive', False):
                    entry_name = entry_name.lower()
                
                # File type filter
                file_type_filter = options.get('file_type', 'All Files')
                if file_type_filter != 'All Files':
                    type_mapping = {
                        'Models (DFF)': 'DFF',
                        'Textures (TXD)': 'TXD',
                        'Collision (COL)': 'COL',
                        'Animation (IFP)': 'IFP',
                        'Audio (WAV)': 'WAV',
                        'Scripts (SCM)': 'SCM'
                    }
                    if entry_type != type_mapping.get(file_type_filter, ''):
                        continue
                
                # Search logic
                found = False
                if options.get('regex', False):
                    import re
                    try:
                        if re.search(search_text, entry_name):
                            found = True
                    except re.error:
                        continue
                elif options.get('whole_word', False):
                    import re
                    pattern = r'\b' + re.escape(search_text) + r'\b'
                    if re.search(pattern, entry_name):
                        found = True
                else:
                    if search_text in entry_name:
                        found = True
                
                if found:
                    matches.append(row)
            
            # Store matches and highlight
            self.current_search_matches = matches
            self.current_search_index = -1
            self._highlight_search_matches(matches)
            
            # Update dialog
            if self.search_dialog:
                if matches:
                    self.search_dialog.results_label.setText(f"Found {len(matches)} matches")
                    if matches:
                        self._find_next()  # Jump to first match
                else:
                    self.search_dialog.results_label.setText("No matches found")
            
            self.main_window.log_message(f"🔍 Advanced search: {len(matches)} matches found")
            
        except Exception as e:
            self.main_window.log_message(f"❌ Advanced search error: {str(e)}")
    
    def _find_next(self):
        """Find next search match"""
        if not self.current_search_matches:
            return
        
        try:
            self.current_search_index = (self.current_search_index + 1) % len(self.current_search_matches)
            row = self.current_search_matches[self.current_search_index]
            
            # Select and scroll to row
            self.table.clearSelection()
            self.table.selectRow(row)
            self.table.scrollToItem(self.table.item(row, 0))
            
            self.main_window.log_message(f"🔍 Match {self.current_search_index + 1} of {len(self.current_search_matches)}")
            
        except Exception as e:
            self.main_window.log_message(f"❌ Find next error: {str(e)}")
    
    def _find_previous(self):
        """Find previous search match"""
        if not self.current_search_matches:
            return
        
        try:
            self.current_search_index = (self.current_search_index - 1) % len(self.current_search_matches)
            row = self.current_search_matches[self.current_search_index]
            
            # Select and scroll to row
            self.table.clearSelection()
            self.table.selectRow(row)
            self.table.scrollToItem(self.table.item(row, 0))
            
            self.main_window.log_message(f"🔍 Match {self.current_search_index + 1} of {len(self.current_search_matches)}")
            
        except Exception as e:
            self.main_window.log_message(f"❌ Find previous error: {str(e)}")
    
    def _highlight_search_matches(self, matches: List[int]):
        """Highlight search matches in table"""
        try:
            # Clear previous highlighting
            self._clear_search_highlighting()
            
            # Highlight matches
            for row in matches:
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.yellow)
            
        except Exception as e:
            self.main_window.log_message(f"❌ Highlighting error: {str(e)}")
    
    def _clear_search_highlighting(self):
        """Clear search highlighting"""
        try:
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.white)
            
        except Exception:
            pass
    
    # EVENT HANDLERS

    def _on_selection_changed(self):
        """Handle table selection changes"""
        try:
            selected_rows = set()
            for item in self.table.selectedItems():
                selected_rows.add(item.row())
            
            if selected_rows:
                self.entry_selected.emit(list(selected_rows)[0])
            
        except Exception as e:
            self.main_window.log_message(f"❌ Selection change error: {str(e)}")
    
    def _apply_theme_styling(self):
        """Apply theme styling - YOUR EXACT ORIGINAL THEME"""
        # Table styling - YOUR EXACT STYLING
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #e0e0e0;
                border: 1px solid #d0d0d0;
            }
            QTableWidget::item {
                padding: 4px;
                border: none;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                padding: 4px;
                font-weight: bold;
            }
        """)
        
        # Log styling - YOUR EXACT STYLING
        self.log.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 8pt;
            }
        """)

    def populate_table(self, entries):
        """Populate table with entries"""
        try:
            if not entries:
                self.table.setRowCount(0)
                return

            self.table.setRowCount(len(entries))

            for row, entry in enumerate(entries):
                # Name
                name = getattr(entry, 'name', f'Entry {row}')
                self.table.setItem(row, 0, QTableWidgetItem(name))

                # Type
                file_type = name.split('.')[-1].upper() if '.' in name else 'Unknown'
                self.table.setItem(row, 1, QTableWidgetItem(file_type))

                # Size
                size = getattr(entry, 'size', 0)
                size_text = self._format_size(size)
                self.table.setItem(row, 2, QTableWidgetItem(size_text))

                # Offset
                offset = getattr(entry, 'offset', 0)
                self.table.setItem(row, 3, QTableWidgetItem(str(offset)))

            self.main_window.log_message(f"📋 Table populated with {len(entries)} entries")

        except Exception as e:
            self.main_window.log_message(f"❌ Table population error: {str(e)}")
                
                
