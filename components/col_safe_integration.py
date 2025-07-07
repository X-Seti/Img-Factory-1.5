# This goes in components/col_safe_integration.py
# X-Seti - July 07 2025 - Safe COL Integration with delayed initialization
# Version: 1 - Moved from main file to prevent init issues

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
    
    def get_col_tab_info():
        """Get information about all COL tabs"""
        col_tabs = []
        
        if not hasattr(main_window, 'open_files'):
            return col_tabs

        for tab_index, file_info in main_window.open_files.items():
            if file_info.get('type') == 'COL':
                tab_text = main_window.main_tab_widget.tabText(tab_index)
                file_path = file_info.get('file_path', 'Unknown')

                col_tabs.append({
                    'index': tab_index,
                    'name': tab_text,
                    'path': file_path,
                    'is_active': tab_index == main_window.main_tab_widget.currentIndex()
                })

        return col_tabs

    def change_col_tab_icon(icon_key='shield'):
        """Change the icon for all COL tabs"""
        try:
            icons = {
                'shield': '🛡️',      # Current - protection/collision
                'collision': '💥',    # Impact/collision
                'cube': '🧊',         # 3D collision box
                'diamond': '💎',      # Collision geometry
                'gear': '⚙️',         # Technical/mechanical
                'warning': '⚠️',      # Collision warning
                'target': '🎯',       # Collision detection
                'atom': '⚛️',         # Physics/collision
            }
            
            new_icon = icons.get(icon_key, '🛡️')
            changed_count = 0
            
            if not hasattr(main_window, 'open_files'):
                return

            for tab_index, file_info in main_window.open_files.items():
                if file_info.get('type') == 'COL':
                    current_text = main_window.main_tab_widget.tabText(tab_index)

                    # Replace any existing icon with new one
                    for old_icon in icons.values():
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

# Simple fix for imgfactory.py __init__ method
def init_col_integration_placeholder(main_window):
    """Placeholder for COL integration during init"""
    # Just set a flag that COL integration is needed
    main_window._col_integration_needed = True
    print("COL integration marked for later setup")
