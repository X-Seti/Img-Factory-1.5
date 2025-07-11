#this belongs in components/ img_search_function.py - Version: 1
# X-Seti - July10 2025 - IMG Factory 1.5 - Search Box Fix

"""
IMG Factory Search Fix
Fixes the broken search functionality by properly connecting signals
"""

from PyQt6.QtWidgets import QLineEdit, QComboBox, QPushButton, QCheckBox
from PyQt6.QtCore import QTimer
from typing import Optional, Dict, Any, List
import re


class IMGSearchManager:
    """Manages search functionality for IMG entries"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        self.last_search_text = ""
        self.current_matches = []
        self.current_match_index = -1
        
    def setup_search_connections(self):
        """Setup search box connections - FIXED VERSION"""
        try:
            # Find search input in GUI layout
            search_input = None
            filter_combo = None
            
            # Try multiple possible locations for search input
            if hasattr(self.main_window, 'gui_layout'):
                if hasattr(self.main_window.gui_layout, 'search_input'):
                    search_input = self.main_window.gui_layout.search_input
                elif hasattr(self.main_window.gui_layout, 'filter_input'):
                    search_input = self.main_window.gui_layout.filter_input
                
                if hasattr(self.main_window.gui_layout, 'filter_combo'):
                    filter_combo = self.main_window.gui_layout.filter_combo
            
            # Also check direct attributes on main window
            if not search_input:
                if hasattr(self.main_window, 'filter_input'):
                    search_input = self.main_window.filter_input
                elif hasattr(self.main_window, 'search_input'):
                    search_input = self.main_window.search_input
            
            if not filter_combo and hasattr(self.main_window, 'filter_combo'):
                filter_combo = self.main_window.filter_combo
            
            # Connect signals if found
            if search_input:
                # Disconnect any existing connections
                try:
                    search_input.textChanged.disconnect()
                    search_input.returnPressed.disconnect()
                except:
                    pass
                
                # Connect to our search manager
                search_input.textChanged.connect(self._on_search_text_changed)
                search_input.returnPressed.connect(self._perform_immediate_search)
                
                self.main_window.log_message("✅ Search input connected")
                return True
            else:
                self.main_window.log_message("❌ Search input not found")
                return False
                
        except Exception as e:
            self.main_window.log_message(f"❌ Search connection error: {e}")
            return False
    
    def _on_search_text_changed(self, text: str):
        """Handle search text changes with debouncing"""
        self.search_timer.stop()
        if text.strip():
            self.search_timer.start(300)  # 300ms delay
        else:
            self._clear_search()
    
    def _perform_immediate_search(self):
        """Perform search immediately (Enter pressed)"""
        self.search_timer.stop()
        self._perform_search()
    
    def _perform_search(self):
        """Perform the actual search"""
        try:
            # Get search text
            search_text = ""
            if hasattr(self.main_window, 'filter_input'):
                search_text = self.main_window.filter_input.text().strip()
            elif hasattr(self.main_window.gui_layout, 'search_input'):
                search_text = self.main_window.gui_layout.search_input.text().strip()
            
            if not search_text:
                self._clear_search()
                return
            
            # Check if IMG is loaded
            if not self.main_window.current_img or not self.main_window.current_img.entries:
                self.main_window.log_message("No IMG file loaded for search")
                return
            
            # Perform search
            matches = self._find_matches(search_text)
            self.current_matches = matches
            self.current_match_index = -1
            
            # Update UI
            self._highlight_matches(matches)
            
            # Log results
            if matches:
                self.main_window.log_message(f"🔍 Found {len(matches)} matches for '{search_text}'")
                self._select_first_match()
            else:
                self.main_window.log_message(f"🔍 No matches found for '{search_text}'")
                
        except Exception as e:
            self.main_window.log_message(f"❌ Search error: {e}")
    
    def _find_matches(self, search_text: str) -> List[int]:
        """Find matching entries"""
        matches = []
        search_lower = search_text.lower()
        
        # Get filter type if available
        file_type_filter = "All Files"
        if hasattr(self.main_window, 'filter_combo'):
            file_type_filter = self.main_window.filter_combo.currentText()
        
        for i, entry in enumerate(self.main_window.current_img.entries):
            # Check file type filter first
            if file_type_filter != "All Files":
                entry_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else ''
                if file_type_filter == "Models (DFF)" and entry_ext != 'DFF':
                    continue
                elif file_type_filter == "Textures (TXD)" and entry_ext != 'TXD':
                    continue
                elif file_type_filter == "Collision (COL)" and entry_ext != 'COL':
                    continue
                elif file_type_filter == "Animation (IFP)" and entry_ext != 'IFP':
                    continue
                elif file_type_filter == "Audio (WAV)" and entry_ext != 'WAV':
                    continue
                elif file_type_filter == "Scripts (SCM)" and entry_ext != 'SCM':
                    continue
            
            # Check if name matches search
            if search_lower in entry.name.lower():
                matches.append(i)
        
        return matches
    
    def _highlight_matches(self, matches: List[int]):
        """Highlight matching entries in the table"""
        try:
            table = self.main_window.gui_layout.table
            
            # Clear previous selection
            table.clearSelection()
            
            # Select matching rows
            for row in matches:
                if row < table.rowCount():
                    table.selectRow(row)
                    
        except Exception as e:
            self.main_window.log_message(f"❌ Highlight error: {e}")
    
    def _select_first_match(self):
        """Select and scroll to first match"""
        if self.current_matches:
            try:
                table = self.main_window.gui_layout.table
                first_row = self.current_matches[0]
                
                # Clear selection and select first match
                table.clearSelection()
                table.selectRow(first_row)
                
                # Scroll to the row
                table.scrollToItem(table.item(first_row, 0))
                
                self.current_match_index = 0
                
            except Exception as e:
                self.main_window.log_message(f"❌ Select error: {e}")
    
    def _clear_search(self):
        """Clear search results"""
        try:
            self.current_matches = []
            self.current_match_index = -1
            
            # Clear table selection
            if hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'table'):
                self.main_window.gui_layout.table.clearSelection()
                
        except Exception as e:
            self.main_window.log_message(f"❌ Clear search error: {e}")
    
    def find_next(self):
        """Find next match"""
        if not self.current_matches:
            return
        
        try:
            self.current_match_index = (self.current_match_index + 1) % len(self.current_matches)
            row = self.current_matches[self.current_match_index]
            
            table = self.main_window.gui_layout.table
            table.clearSelection()
            table.selectRow(row)
            table.scrollToItem(table.item(row, 0))
            
            self.main_window.log_message(f"🔍 Match {self.current_match_index + 1} of {len(self.current_matches)}")
            
        except Exception as e:
            self.main_window.log_message(f"❌ Find next error: {e}")
    
    def find_previous(self):
        """Find previous match"""
        if not self.current_matches:
            return
        
        try:
            self.current_match_index = (self.current_match_index - 1) % len(self.current_matches)
            row = self.current_matches[self.current_match_index]
            
            table = self.main_window.gui_layout.table
            table.clearSelection()
            table.selectRow(row)
            table.scrollToItem(table.item(row, 0))
            
            self.main_window.log_message(f"🔍 Match {self.current_match_index + 1} of {len(self.current_matches)}")
            
        except Exception as e:
            self.main_window.log_message(f"❌ Find previous error: {e}")


def install_search_manager(main_window):
    """Install search manager in main window"""
    try:
        # Create search manager
        search_manager = IMGSearchManager(main_window)
        main_window.search_manager = search_manager
        
        # Setup connections
        if search_manager.setup_search_connections():
            main_window.log_message("✅ Search manager installed")
            
            # Add keyboard shortcuts for search navigation
            from PyQt6.QtGui import QShortcut, QKeySequence
            from PyQt6.QtCore import Qt
            
            # F3 for find next
            find_next_shortcut = QShortcut(QKeySequence("F3"), main_window)
            find_next_shortcut.activated.connect(search_manager.find_next)
            
            # Shift+F3 for find previous  
            find_prev_shortcut = QShortcut(QKeySequence("Shift+F3"), main_window)
            find_prev_shortcut.activated.connect(search_manager.find_previous)
            
            return True
        else:
            main_window.log_message("❌ Search manager connection failed")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Search manager installation error: {e}")
        return False


def fix_search_dialog(main_window):
    """Fix the search dialog functionality"""
    try:
        # Override the broken perform_search method
        def fixed_perform_search(search_text, options):
            """Fixed search implementation"""
            try:
                if not main_window.current_img or not main_window.current_img.entries:
                    main_window.log_message("No IMG file loaded or no entries to search")
                    return

                # Perform search with options
                matches = []
                total_entries = len(main_window.current_img.entries)

                for i, entry in enumerate(main_window.current_img.entries):
                    entry_name = entry.name

                    # Apply search options
                    if not options.get('case_sensitive', False):
                        entry_name = entry_name.lower()
                        search_text = search_text.lower()

                    # Check file type filter
                    file_type = options.get('file_type', 'All Files')
                    if file_type != 'All Files':
                        entry_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else ''
                        type_mapping = {
                            'Models (DFF)': 'DFF',
                            'Textures (TXD)': 'TXD', 
                            'Collision (COL)': 'COL',
                            'Animation (IFP)': 'IFP',
                            'Audio (WAV)': 'WAV',
                            'Scripts (SCM)': 'SCM'
                        }
                        if file_type in type_mapping and entry_ext != type_mapping[file_type]:
                            continue

                    # Check if matches
                    if options.get('whole_word', False):
                        import re
                        pattern = r'\b' + re.escape(search_text) + r'\b'
                        if re.search(pattern, entry_name):
                            matches.append(i)
                    elif options.get('regex', False):
                        import re
                        try:
                            if re.search(search_text, entry_name):
                                matches.append(i)
                        except re.error:
                            main_window.log_message("Invalid regular expression")
                            return
                    else:
                        # Simple text search
                        if search_text in entry_name:
                            matches.append(i)

                # Update search dialog results if it exists
                if hasattr(main_window, 'search_dialog') and main_window.search_dialog:
                    main_window.search_dialog.update_results(len(matches), total_entries)

                # Select matching entries in table
                if matches:
                    table = main_window.gui_layout.table
                    table.clearSelection()
                    for row in matches:
                        if row < table.rowCount():
                            table.selectRow(row)
                    
                    # Scroll to first match
                    if matches:
                        table.scrollToItem(table.item(matches[0], 0))
                    
                    main_window.log_message(f"🔍 Found {len(matches)} matches")
                else:
                    main_window.log_message(f"🔍 No matches found for '{search_text}'")

            except Exception as e:
                main_window.log_message(f"❌ Search error: {str(e)}")
        
        # Replace the broken method
        main_window.perform_search = fixed_perform_search
        
        main_window.log_message("✅ Search dialog fixed")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Search dialog fix error: {e}")
        return False
