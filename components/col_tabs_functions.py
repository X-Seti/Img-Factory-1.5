#this belongs in components/ col_tabs_function.py - Version: 5
# X-Seti - July08 2025 - COL Tabs Integration for IMG Factory 1.5

"""
COL Tabs Integration
"""

import os
from PyQt6.QtWidgets import QTableWidgetItem

# Methods list -
# add_col_tab
# _setup_col_tab
# setup_col_tab_integration


def add_col_tab(img_factory_instance): #vers 4
    """Add COL tab to the main interface"""

    # Check if main interface has a tab widget
    if not hasattr(img_factory_instance, 'main_tab_widget'):
        # Create tab widget if it doesn't exist
        central_widget = img_factory_instance.centralWidget()
        if central_widget:
            # Replace central widget with tab widget
            old_layout = central_widget.layout()

            img_factory_instance.main_tab_widget = QTabWidget()

            # Move existing content to first tab
            if old_layout:
                img_tab = QWidget()
                img_tab.setLayout(old_layout)
                img_factory_instance.main_tab_widget.addTab(img_tab, "📁 IMG Files")

            # Set new layout
            new_layout = QVBoxLayout(central_widget)
            new_layout.addWidget(img_factory_instance.main_tab_widget)

    # Create COL tab
    col_tab = QWidget()
    col_layout = QVBoxLayout(col_tab)

    # Create COL interface
    col_splitter = QSplitter(Qt.Orientation.Horizontal)

    # Left panel - COL file list
    col_list_widget = COLListWidget()
    col_splitter.addWidget(col_list_widget)

    # Right panel - COL model details
    col_details_widget = COLModelDetailsWidget()
    col_splitter.addWidget(col_details_widget)

    # Connect signals
    col_list_widget.col_selected.connect(col_details_widget.set_col_file)
    col_list_widget.col_double_clicked.connect(lambda col_file: open_col_editor_with_file(img_factory_instance, col_file))

    # Set splitter sizes
    col_splitter.setSizes([400, 300])

    col_layout.addWidget(col_splitter)

    # Add COL tab
    img_factory_instance.main_tab_widget.addTab(col_tab, "🔧 COL Files")

    # Store references
    img_factory_instance.col_list_widget = col_list_widget
    img_factory_instance.col_details_widget = col_details_widget


def _setup_col_tab(main_window, file_path): #vers 8
    """Setup or reuse tab for COL file"""
    try:
        current_index = main_window.main_tab_widget.currentIndex()

        # Check if current tab is empty
        if not hasattr(main_window, 'open_files') or current_index not in main_window.open_files:
            main_window.log_message("Using current tab for COL file")
        else:
            main_window.log_message("Creating new tab for COL file")
            if hasattr(main_window, 'close_manager'):
                main_window.close_manager.create_new_tab()
                current_index = main_window.main_tab_widget.currentIndex()
            else:
                main_window.log_message("⚠️ Close manager not available")
                return None

        # Setup tab info
        file_name = os.path.basename(file_path)
        file_name_clean = file_name[:-4] if file_name.lower().endswith('.col') else file_name
        tab_name = f"🛡️ {file_name_clean}"

        # Store tab info
        if not hasattr(main_window, 'open_files'):
            main_window.open_files = {}

        main_window.open_files[current_index] = {
            'type': 'COL',
            'file_path': file_path,
            'file_object': None,
            'tab_name': tab_name
        }

        # Update tab name
        main_window.main_tab_widget.setTabText(current_index, tab_name)

        return current_index

    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
        return None


def setup_col_tab_integration(main_window): #vers 1
    """Setup COL tab integration with main window"""
    try:
        # Add COL loading method to main window
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)
        
        # Add styling reset method
        main_window._reset_table_styling = lambda: reset_table_styling(main_window)
        
        main_window.log_message("✅ COL tab integration ready")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ COL tab integration failed: {str(e)}")
        return False



