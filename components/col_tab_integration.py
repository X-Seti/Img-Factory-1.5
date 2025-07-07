#this belongs in components/ col_tab_integration.py - version 1
# X-Seti - July07 2025 - COL Tab Integration for IMG Factory 1.5

import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView

def setup_col_integration_safe(main_window):
    """Setup COL integration safely after GUI is ready"""
    try:
        # Only setup after GUI is fully initialized
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window, 'log_message'):
            print("GUI not ready for COL integration - will retry later")
            return False
        
        # Setup COL tab styling
        setup_col_tab_styling_safe(main_window)
        
        # Add COL methods to main window
        add_col_methods_to_main_window(main_window)
        
        main_window.log_message("✅ COL integration setup complete")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL integration error: {str(e)}")
        else:
            print(f"COL integration error: {str(e)}")
        return False

def setup_col_tab_styling_safe(main_window):
    """Setup COL tab styling safely"""
    try:
        # Only proceed if we have main_tab_widget
        if not hasattr(main_window, 'main_tab_widget'):
            main_window.log_message("⚠️ main_tab_widget not available for COL styling")
            return

        # Apply base tab styling that supports COL themes
        update_tab_stylesheet_for_col(main_window)

        # Connect tab change to update styling
        if hasattr(main_window.main_tab_widget, 'currentChanged'):
            def enhanced_tab_changed(index):
                # Apply COL-specific styling if needed
                if hasattr(main_window, 'open_files') and index in main_window.open_files:
                    file_info = main_window.open_files[index]
                    if file_info.get('type') == 'COL':
                        apply_individual_col_tab_style(main_window, index)

            main_window.main_tab_widget.currentChanged.connect(enhanced_tab_changed)
            main_window.log_message("✅ COL tab styling system setup complete")

    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab styling: {str(e)}")

def update_tab_stylesheet_for_col(main_window):
    """Update tab stylesheet to support COL tab styling"""
    try:
        # Only proceed if we have main_tab_widget
        if not hasattr(main_window, 'main_tab_widget'):
            return

        # Enhanced stylesheet that differentiates COL tabs
        enhanced_style = """
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #ffffff;
                margin-top: 0px;
            }

            QTabBar {
                qproperty-drawBase: 0;
            }

            /* Default tab styling (IMG files) */
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                padding: 6px 12px;
                margin-right: 2px;
                border-radius: 3px 3px 0px 0px;
                min-width: 80px;
                max-height: 28px;
                font-size: 9pt;
                color: #333333;
            }

            /* Selected tab */
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 1px solid #ffffff;
                color: #000000;
                font-weight: bold;
            }

            /* Hover effect */
            QTabBar::tab:hover {
                background-color: #e8e8e8;
            }

            /* COL tab styling - light blue theme */
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """

        # Apply the enhanced stylesheet
        main_window.main_tab_widget.setStyleSheet(enhanced_style)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error updating tab stylesheet: {str(e)}")

def apply_individual_col_tab_style(main_window, tab_index):
    """Apply individual styling to a specific COL tab"""
    try:
        # This is a workaround since PyQt6 doesn't easily allow per-tab styling
        # We'll modify the tab text to include color coding
        tab_bar = main_window.main_tab_widget.tabBar()
        current_text = tab_bar.tabText(tab_index)

        # Ensure COL tabs have the shield icon and are visually distinct
        if not current_text.startswith("🛡️"):
            if current_text.startswith("🔧"):
                # Replace the wrench with shield
                new_text = current_text.replace("🔧", "🛡️")
            else:
                new_text = f"🛡️ {current_text}"

            tab_bar.setTabText(tab_index, new_text)

        # Set tooltip to indicate it's a COL file
        tab_bar.setTabToolTip(tab_index, "Collision File (COL) - Contains 3D collision data")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error applying individual COL tab style: {str(e)}")

def add_col_methods_to_main_window(main_window):
    """Add COL-specific methods to main window"""
    
    def get_col_text_color():
        """Get text color for COL tabs"""
        try:
            from PyQt6.QtGui import QColor
            return QColor(25, 118, 210)  # Nice blue color
        except ImportError:
            return None

    def get_col_background_color():
        """Get background color for COL tabs"""
        try:
            from PyQt6.QtGui import QColor
            return QColor(227, 242, 253)  # Light blue background
        except ImportError:
            return None

    def get_col_tab_info(tab_index):
        """Get COL tab information"""
        try:
            if tab_index in main_window.open_files:
                file_info = main_window.open_files[tab_index]
                if file_info.get('type') == 'COL':
                    return {
                        'type': 'COL',
                        'path': file_info.get('file_path', ''),
                        'name': file_info.get('tab_name', ''),
                        'object': file_info.get('file_object', None)
                    }
            return None
        except Exception as e:
            main_window.log_message(f"❌ Error getting COL tab info: {str(e)}")
            return None

    def change_col_tab_icon(new_icon="🛡️"):
        """Change icon for all COL tabs"""
        try:
            changed_count = 0
            icon_map = {"🔧": "wrench", "🛡️": "shield", "⚔️": "sword"}

            for tab_index in range(main_window.main_tab_widget.count()):
                if tab_index in main_window.open_files:
                    file_info = main_window.open_files[tab_index]
                    if file_info.get('type') == 'COL':
                        current_text = main_window.main_tab_widget.tabText(tab_index)

                        # Remove existing icon
                        for old_icon in icon_map.keys():
                            if current_text.startswith(old_icon):
                                current_text = current_text[2:]  # Remove icon and space
                                break

                        new_text = f"{new_icon} {current_text}"
                        main_window.main_tab_widget.setTabText(tab_index, new_text)
                        changed_count += 1

            if changed_count > 0:
                main_window.log_message(f"✅ Changed icon for {changed_count} COL tabs to {new_icon}")

        except Exception as e:
            main_window.log_message(f"❌ Error changing COL tab icons: {str(e)}")

    # Add methods to main window
    main_window.get_col_text_color = get_col_text_color
    main_window.get_col_background_color = get_col_background_color
    main_window.get_col_tab_info = get_col_tab_info
    main_window.change_col_tab_icon = change_col_tab_icon

# NEW COL TAB CREATION FUNCTIONS

def load_col_file_safely(main_window, file_path):
    """Load COL file safely - FIXED method name and logic"""
    try:
        main_window.log_message(f"🔧 Setting up COL tab for: {os.path.basename(file_path)}")
        
        # Check if current tab is empty (no file loaded) 
        current_index = main_window.main_tab_widget.currentIndex()
        
        if current_index not in main_window.open_files:
            # Current tab is empty, use it
            main_window.log_message(f"Using current empty tab for COL file")
        else:
            # Current tab has a file, create new tab
            main_window.log_message(f"Creating new tab for COL file")
            main_window.close_manager.create_new_tab()
            current_index = main_window.main_tab_widget.currentIndex()
        
        # Store file info BEFORE loading
        file_name = os.path.basename(file_path)
        # Remove .col extension for cleaner tab names
        if file_name.lower().endswith('.col'):
            file_name_clean = file_name[:-4]  # Remove .col extension
        else:
            file_name_clean = file_name

        # Use shield icon for COL files
        tab_name = f"🛡️ {file_name_clean}"

        main_window.open_files[current_index] = {
            'type': 'COL',
            'file_path': file_path,
            'file_object': None,  # Will be set when loaded
            'tab_name': tab_name
        }

        # Update tab name with icon
        main_window.main_tab_widget.setTabText(current_index, tab_name)

        # Apply COL tab styling
        apply_col_tab_styling(main_window, current_index)

        # Start loading COL file
        load_col_file_content(main_window, file_path)

    except Exception as e:
        error_msg = f"Error setting up COL tab: {str(e)}"
        main_window.log_message(f"❌ {error_msg}")
        QMessageBox.critical(main_window, "COL Setup Error", error_msg)

def load_col_file_content(main_window, file_path):
    """Load COL file content - ROBUST version with error handling"""
    try:
        main_window.log_message(f"Loading COL file: {os.path.basename(file_path)}")
        
        # Show progress
        if hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(0, "Loading COL file...")

        # Verify file exists and is readable
        if not os.path.exists(file_path):
            raise Exception(f"COL file not found: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise Exception(f"Cannot read COL file: {file_path}")

        # Try to import COL classes with fallback
        try:
            from components.col_core_classes import COLFile
            main_window.log_message("✅ COL core classes imported successfully")
        except ImportError as e:
            raise Exception(f"COL core classes not available: {str(e)}")

        # Diagnose file first
        try:
            from components.col_core_classes import diagnose_col_file
            diagnosis = diagnose_col_file(file_path)
            
            if not diagnosis.get('signature_valid', False):
                main_window.log_message(f"⚠️ COL file warning: {diagnosis.get('error', 'Unknown format')}")
                # Continue anyway - might still be loadable
            else:
                main_window.log_message(f"✅ COL file format: {diagnosis.get('detected_version', 'Unknown')}")
                
        except Exception as e:
            main_window.log_message(f"⚠️ Could not diagnose COL file: {str(e)}")

        # Create and load COL file object
        main_window.log_message("Creating COL file object...")
        col_file = COLFile(file_path)
        
        main_window.log_message("Loading COL file data...")
        if not col_file.load():
            # Try to get more specific error info
            error_details = "Unknown loading error"
            if hasattr(col_file, 'load_error'):
                error_details = col_file.load_error
            raise Exception(f"Failed to load COL file: {error_details}")

        # Verify loaded data
        if not hasattr(col_file, 'models'):
            main_window.log_message("⚠️ COL file has no models attribute")
            col_file.models = []  # Create empty models list
        
        model_count = len(col_file.models) if col_file.models else 0
        main_window.log_message(f"✅ COL loaded with {model_count} models")

        # Update current COL reference
        main_window.current_col = col_file

        # Update file info in open_files
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index in main_window.open_files:
            main_window.open_files[current_index]['file_object'] = col_file
            main_window.log_message(f"✅ Updated tab {current_index} with COL object")

        # Update UI for loaded COL
        update_ui_for_loaded_col(main_window)

        # Hide progress
        if hasattr(main_window.gui_layout, 'hide_progress'):
            main_window.gui_layout.hide_progress()

        # Update window title
        file_name = os.path.basename(file_path)
        main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        main_window.log_message(f"✅ Loaded COL: {file_name} ({model_count} models)")

    except Exception as e:
        if hasattr(main_window.gui_layout, 'hide_progress'):
            main_window.gui_layout.hide_progress()
        error_msg = f"Error loading COL file: {str(e)}"
        main_window.log_message(f"❌ {error_msg}")
        
        # More detailed error logging
        main_window.log_message(f"📁 File path: {file_path}")
        main_window.log_message(f"📊 File exists: {os.path.exists(file_path)}")
        if os.path.exists(file_path):
            main_window.log_message(f"📊 File size: {os.path.getsize(file_path)} bytes")
        
        QMessageBox.critical(main_window, "COL Load Error", error_msg)

def apply_col_tab_styling(main_window, tab_index):
    """Apply styling to COL tab - NEW method"""
    try:
        # Set tab tooltip
        tab_bar = main_window.main_tab_widget.tabBar()
        tab_bar.setTabToolTip(tab_index, "Collision File (COL) - Contains 3D collision data")
        
        # Apply COL-specific styling through safe integration
        if hasattr(main_window, '_col_integration_ready'):
            apply_individual_col_tab_style(main_window, tab_index)
        
        main_window.log_message(f"✅ Applied COL styling to tab {tab_index}")

    except Exception as e:
        main_window.log_message(f"⚠️ Error applying COL tab styling: {str(e)}")

def update_ui_for_loaded_col(main_window):
    """Update UI when COL file is loaded - FIXED method"""
    try:
        if not hasattr(main_window, 'current_col') or not main_window.current_col:
            main_window.log_message("⚠️ No COL file to display")
            return

        # Clear current display
        clear_current_display(main_window)

        # Create COL-specific UI elements
        create_col_display_ui(main_window)

        main_window.log_message(f"✅ Updated UI for COL file")

    except Exception as e:
        main_window.log_message(f"❌ Error updating UI for COL: {str(e)}")

def create_col_display_ui(main_window):
    """Create UI elements for displaying COL file - NEW method"""
    try:
        if not hasattr(main_window, 'current_col') or not main_window.current_col:
            return

        # Get current tab content widget
        current_index = main_window.main_tab_widget.currentIndex()
        current_widget = main_window.main_tab_widget.widget(current_index)
        
        if not current_widget:
            main_window.log_message("⚠️ No current widget for COL display")
            return

        # Clear existing layout
        if current_widget.layout():
            clear_layout(current_widget.layout())

        # Create new layout for COL display
        col_layout = QVBoxLayout(current_widget)
        col_layout.setContentsMargins(5, 5, 5, 5)

        # Add COL file info panel
        add_col_info_panel(main_window, col_layout)

        # Add COL models table
        add_col_models_table(main_window, col_layout)

        main_window.log_message(f"✅ Created COL display UI")

    except Exception as e:
        main_window.log_message(f"❌ Error creating COL display UI: {str(e)}")

def update_ui_for_loaded_col(main_window):
    """Update UI when COL file is loaded - FIXED method"""
    try:
        if not hasattr(main_window, 'current_col') or not main_window.current_col:
            main_window.log_message("⚠️ No COL file to display")
            return

        # Clear current display
        clear_current_display(main_window)

        # Create COL-specific UI elements
        create_col_display_ui(main_window)

        main_window.log_message(f"✅ Updated UI for COL file")

    except Exception as e:
        main_window.log_message(f"❌ Error updating UI for COL: {str(e)}")

def create_col_display_ui(main_window):
    """Create UI elements for displaying COL file - NEW method"""
    try:
        if not hasattr(main_window, 'current_col') or not main_window.current_col:
            return

        # Get current tab content widget
        current_index = main_window.main_tab_widget.currentIndex()
        current_widget = main_window.main_tab_widget.widget(current_index)
        
        if not current_widget:
            main_window.log_message("⚠️ No current widget for COL display")
            return

        # Clear existing layout
        if current_widget.layout():
            clear_layout(current_widget.layout())

        # Create new layout for COL display
        col_layout = QVBoxLayout(current_widget)
        col_layout.setContentsMargins(5, 5, 5, 5)

        # Add COL file info panel
        add_col_info_panel(main_window, col_layout)

        # Add COL models table
        add_col_models_table(main_window, col_layout)

        main_window.log_message(f"✅ Created COL display UI")

    except Exception as e:
        main_window.log_message(f"❌ Error creating COL display UI: {str(e)}")

def add_col_info_panel(main_window, layout):
    """Add COL file information panel - NEW method"""
    try:
        info_group = QGroupBox("COL File Information")
        info_layout = QFormLayout(info_group)
        
        col_file = main_window.current_col
        
        # File name
        info_layout.addRow("File:", QLabel(os.path.basename(col_file.file_path)))
        
        # File size
        file_size = os.path.getsize(col_file.file_path)
        from components.img_core_classes import format_file_size
        info_layout.addRow("Size:", QLabel(format_file_size(file_size)))
        
        # Model count
        model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
        info_layout.addRow("Models:", QLabel(str(model_count)))
        
        # Version info
        if hasattr(col_file, 'version'):
            info_layout.addRow("Version:", QLabel(str(col_file.version)))
        
        layout.addWidget(info_group)

    except Exception as e:
        main_window.log_message(f"⚠️ Error adding COL info panel: {str(e)}")

def add_col_models_table(main_window, layout):
    """Add COL models table - NEW method"""
    try:
        models_group = QGroupBox("Collision Models")
        models_layout = QVBoxLayout(models_group)
        
        # Create table
        models_table = QTableWidget()
        models_table.setColumnCount(4)
        models_table.setHorizontalHeaderLabels(["Model Name", "Faces", "Vertices", "Material"])
        
        # Populate table
        col_file = main_window.current_col
        if hasattr(col_file, 'models') and col_file.models:
            models_table.setRowCount(len(col_file.models))
            
            for row, model in enumerate(col_file.models):
                # Model name/identifier
                name_item = QTableWidgetItem(getattr(model, 'name', f"Model {row+1}"))
                models_table.setItem(row, 0, name_item)
                
                # Face count
                face_count = getattr(model, 'face_count', 0)
                models_table.setItem(row, 1, QTableWidgetItem(str(face_count)))
                
                # Vertex count  
                vertex_count = getattr(model, 'vertex_count', 0)
                models_table.setItem(row, 2, QTableWidgetItem(str(vertex_count)))
                
                # Material info
                material = getattr(model, 'material', 'Default')
                models_table.setItem(row, 3, QTableWidgetItem(str(material)))
        
        # Configure table
        models_table.setAlternatingRowColors(True)
        models_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        models_table.horizontalHeader().setStretchLastSection(True)
        models_table.resizeColumnsToContents()
        
        models_layout.addWidget(models_table)
        layout.addWidget(models_group)
        
        # Store reference for later use
        main_window.col_models_table = models_table

    except Exception as e:
        main_window.log_message(f"⚠️ Error adding COL models table: {str(e)}")

def clear_current_display(main_window):
    """Clear current tab display - HELPER method"""
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        current_widget = main_window.main_tab_widget.widget(current_index)
        
        if current_widget and current_widget.layout():
            clear_layout(current_widget.layout())

    except Exception as e:
        main_window.log_message(f"⚠️ Error clearing display: {str(e)}")

def clear_layout(layout):
    """Clear all widgets from layout - HELPER method"""
    try:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    except Exception as e:
        print(f"⚠️ Error clearing layout: {str(e)}")

# SETUP FUNCTION TO REPLACE init_col_integration_placeholder
def setup_complete_col_integration(main_window):
    """Complete COL integration setup - REPLACES placeholder"""
    try:
        # Mark integration as ready
        main_window._col_integration_ready = True
        
        # Add COL loading method to main window
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)
        
        # Setup delayed integration
        setup_delayed_col_integration(main_window)
        
        main_window.log_message("✅ Complete COL integration setup finished")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ COL integration setup failed: {str(e)}")
        return False

# Function to call from main imgfactory.py after GUI is ready
def setup_delayed_col_integration(main_window):
    """Setup COL integration after GUI is fully ready"""
    try:
        # Use a timer to delay until GUI is ready
        from PyQt6.QtCore import QTimer
        
        def try_setup():
            if setup_col_integration_safe(main_window):
                # Success - stop trying
                return
            else:
                # Retry in 100ms
                QTimer.singleShot(100, try_setup)
        
        # Start the retry process
        QTimer.singleShot(100, try_setup)
        
    except Exception as e:
        print(f"Error setting up delayed COL integration: {str(e)}")

# DEPRECATED - keeping for compatibility but should not be used
def init_col_integration_placeholder(main_window):
    """Placeholder for COL integration during init - DEPRECATED"""
    # Just set a flag that COL integration is needed
    main_window._col_integration_needed = True
    print("COL integration marked for later setup - use setup_complete_col_integration instead")
