#this belongs in components/ col_integration_manager.py - Version: 1
# X-Seti - July08 2025 - COL Integration Manager for IMG Factory 1.5

import os
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer

class COLIntegrationManager:
    """Main coordinator for COL integration with IMG Factory"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.display_manager = None
        self.is_initialized = False
        self.debug = True
    
    def setup_col_integration(self):
        """Main setup entry point for COL integration"""
        try:
            self._log("🔧 Setting up COL integration...")
            
            # Check if GUI is ready
            if not self._is_gui_ready():
                self._log("⚠️ GUI not ready, scheduling delayed setup")
                self._schedule_delayed_setup()
                return False
            
            # Apply COL parser patches
            self._apply_parser_patches()
            
            # Initialize display manager
            self._initialize_display_manager()
            
            # Add COL methods to main window
            self._add_col_methods()
            
            # Mark as initialized
            self.is_initialized = True
            self._log("✅ COL integration setup complete")
            return True
            
        except Exception as e:
            self._log(f"❌ COL integration setup failed: {str(e)}")
            return False
    
    def load_col_file_for_display(self, file_path):
        """Load COL file and display in IMG Factory"""
        try:
            self._log(f"📂 Loading COL file: {os.path.basename(file_path)}")
            
            # Validate file
            if not self._validate_col_file(file_path):
                return False
            
            # Setup or reuse tab
            tab_index = self._setup_col_tab(file_path)
            if tab_index is None:
                return False
            
            # Load COL file
            col_file = self._load_col_file(file_path)
            if col_file is None:
                return False
            
            # Update main window state
            self._update_main_window_state(tab_index, col_file, file_path)
            
            # Display COL data
            self._display_col_data(col_file, file_path)
            
            # Update window title
            self._update_window_title(file_path)
            
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            self._log(f"✅ COL file loaded successfully: {model_count} models")
            return True
            
        except Exception as e:
            self._log(f"❌ Error loading COL file: {str(e)}")
            self._show_error_dialog("COL Load Error", f"Failed to load COL file:\n{str(e)}")
            return False
    
    def cleanup_col_resources(self, tab_index=None):
        """Cleanup COL resources when closing files"""
        try:
            if tab_index is not None:
                # Clean up specific tab
                if hasattr(self.main_window, 'open_files') and tab_index in self.main_window.open_files:
                    file_info = self.main_window.open_files[tab_index]
                    if file_info.get('type') == 'COL':
                        # Clear COL reference
                        if hasattr(self.main_window, 'current_col'):
                            self.main_window.current_col = None
                        self._log(f"🧹 Cleaned up COL resources for tab {tab_index}")
            else:
                # General cleanup
                if hasattr(self.main_window, 'current_col'):
                    self.main_window.current_col = None
                self._log("🧹 General COL resource cleanup")
            
            return True
            
        except Exception as e:
            self._log(f"⚠️ Error during COL cleanup: {str(e)}")
            return False
    
    def _is_gui_ready(self):
        """Check if GUI is ready for COL integration"""
        return (hasattr(self.main_window, 'gui_layout') and 
                hasattr(self.main_window, 'log_message') and
                hasattr(self.main_window, 'main_tab_widget'))
    
    def _schedule_delayed_setup(self):
        """Schedule delayed setup when GUI is ready"""
        def try_setup():
            if self._is_gui_ready():
                self.setup_col_integration()
            else:
                # Retry in 100ms
                QTimer.singleShot(100, try_setup)
        
        QTimer.singleShot(100, try_setup)
    
    def _apply_parser_patches(self):
        """Apply enhanced COL parser patches"""
        try:
            from components.col_parser import patch_col_core_classes
            if patch_col_core_classes():
                self._log("✅ COL parser patches applied")
            else:
                self._log("⚠️ COL parser patches failed")
        except ImportError:
            self._log("⚠️ COL parser not available")
        except Exception as e:
            self._log(f"⚠️ Error applying parser patches: {e}")
    
    def _initialize_display_manager(self):
        """Initialize the COL display manager"""
        try:
            from components.col_display import COLDisplayManager
            self.display_manager = COLDisplayManager(self.main_window)
            self._log("✅ COL display manager initialized")
        except ImportError:
            self._log("⚠️ COL display manager not available")
        except Exception as e:
            self._log(f"⚠️ Error initializing display manager: {e}")
    
    def _add_col_methods(self):
        """Add COL-specific methods to main window"""
        try:
            # Add COL loading method
            self.main_window.load_col_file_safely = lambda file_path: self.load_col_file_for_display(file_path)
            
            # Add utility methods
            self.main_window.get_col_text_color = lambda: "#1565c0"
            self.main_window.get_col_background_color = lambda: "#e3f2fd"
            
            # Add tab info method
            def get_col_tab_info(tab_index):
                if hasattr(self.main_window, 'open_files') and tab_index in self.main_window.open_files:
                    file_info = self.main_window.open_files[tab_index]
                    if file_info.get('type') == 'COL':
                        return {
                            'is_col': True,
                            'file_path': file_info.get('file_path'),
                            'tab_name': file_info.get('tab_name')
                        }
                return {'is_col': False}
            
            self.main_window.get_col_tab_info = get_col_tab_info
            
            self._log("✅ COL methods added to main window")
            
        except Exception as e:
            self._log(f"❌ Error adding COL methods: {e}")
    
    def _validate_col_file(self, file_path):
        """Validate COL file before loading"""
        if not os.path.exists(file_path):
            self._show_error_dialog("File Not Found", f"COL file not found:\n{file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            self._show_error_dialog("Access Denied", f"Cannot read COL file:\n{file_path}")
            return False
        
        file_size = os.path.getsize(file_path)
        if file_size < 32:  # Minimum viable COL file size
            self._show_error_dialog("Invalid File", f"COL file too small ({file_size} bytes):\n{file_path}")
            return False
        
        return True
    
    def _setup_col_tab(self, file_path):
        """Setup or reuse tab for COL file"""
        try:
            current_index = self.main_window.main_tab_widget.currentIndex()
            
            # Check if current tab is empty
            if not hasattr(self.main_window, 'open_files') or current_index not in self.main_window.open_files:
                # Use current empty tab
                self._log("Using current empty tab for COL file")
            else:
                # Create new tab
                self._log("Creating new tab for COL file")
                if hasattr(self.main_window, 'close_manager'):
                    self.main_window.close_manager.create_new_tab()
                    current_index = self.main_window.main_tab_widget.currentIndex()
                else:
                    self._log("⚠️ Close manager not available")
                    return None
            
            # Setup tab info
            file_name = os.path.basename(file_path)
            file_name_clean = file_name[:-4] if file_name.lower().endswith('.col') else file_name
            tab_name = f"🛡️ {file_name_clean}"
            
            # Store tab info
            if not hasattr(self.main_window, 'open_files'):
                self.main_window.open_files = {}
            
            self.main_window.open_files[current_index] = {
                'type': 'COL',
                'file_path': file_path,
                'file_object': None,  # Will be set when loaded
                'tab_name': tab_name
            }
            
            # Update tab name
            self.main_window.main_tab_widget.setTabText(current_index, tab_name)
            
            return current_index
            
        except Exception as e:
            self._log(f"❌ Error setting up COL tab: {e}")
            return None
    
    def _load_col_file(self, file_path):
        """Load COL file using enhanced parser"""
        try:
            # Show progress
            if hasattr(self.main_window.gui_layout, 'show_progress'):
                self.main_window.gui_layout.show_progress(0, "Loading COL file...")
            
            # Import COL classes
            from components.col_core_classes import COLFile
            
            # Create and load COL file
            col_file = COLFile(file_path)
            if not col_file.load():
                error_details = getattr(col_file, 'load_error', 'Unknown loading error')
                raise Exception(f"Failed to load COL file: {error_details}")
            
            # Hide progress
            if hasattr(self.main_window.gui_layout, 'hide_progress'):
                self.main_window.gui_layout.hide_progress()
            
            return col_file
            
        except Exception as e:
            # Hide progress on error
            if hasattr(self.main_window.gui_layout, 'hide_progress'):
                self.main_window.gui_layout.hide_progress()
            raise e
    
    def _update_main_window_state(self, tab_index, col_file, file_path):
        """Update main window state with loaded COL file"""
        try:
            # Set current COL reference
            self.main_window.current_col = col_file
            
            # Update tab info
            if tab_index in self.main_window.open_files:
                self.main_window.open_files[tab_index]['file_object'] = col_file
                self._log(f"✅ Updated tab {tab_index} with COL object")
            
        except Exception as e:
            self._log(f"⚠️ Error updating main window state: {e}")
    
    def _display_col_data(self, col_file, file_path):
        """Display COL data in table and info bar"""
        try:
            if self.display_manager:
                # Populate table
                self.display_manager.populate_col_table(col_file)
                
                # Update info bar
                self.display_manager.update_col_info_bar(col_file, file_path)
            else:
                self._log("⚠️ Display manager not available")
                
        except Exception as e:
            self._log(f"❌ Error displaying COL data: {e}")
    
    def _update_window_title(self, file_path):
        """Update main window title"""
        try:
            file_name = os.path.basename(file_path)
            self.main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")
        except Exception as e:
            self._log(f"⚠️ Error updating window title: {e}")
    
    def _show_error_dialog(self, title, message):
        """Show error dialog to user"""
        try:
            QMessageBox.critical(self.main_window, title, message)
        except Exception as e:
            self._log(f"⚠️ Error showing dialog: {e}")
    
    def _log(self, message):
        """Log message to main window"""
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(message)
        elif self.debug:
            print(message)

# Global integration manager instance
_integration_manager = None

def setup_col_integration(main_window):
    """Setup COL integration for main window"""
    global _integration_manager
    try:
        _integration_manager = COLIntegrationManager(main_window)
        return _integration_manager.setup_col_integration()
    except Exception as e:
        print(f"❌ Error setting up COL integration: {e}")
        return False

def load_col_file_safely(main_window, file_path):
    """Load COL file safely using integration manager"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = COLIntegrationManager(main_window)
        _integration_manager.setup_col_integration()
    
    return _integration_manager.load_col_file_for_display(file_path)

def cleanup_col_resources(main_window, tab_index=None):
    """Cleanup COL resources"""
    global _integration_manager
    if _integration_manager:
        return _integration_manager.cleanup_col_resources(tab_index)
    return True

# Backward compatibility functions
def setup_complete_col_integration(main_window):
    """Backward compatibility wrapper"""
    return setup_col_integration(main_window)

def setup_delayed_col_integration(main_window):
    """Backward compatibility wrapper"""
    # Integration manager handles delayed setup automatically
    return setup_col_integration(main_window)