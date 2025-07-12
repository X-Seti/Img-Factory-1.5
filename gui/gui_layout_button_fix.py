#this belongs in gui/ gui_layout.py - Version: Fix
# X-Seti - July12 2025 - Img Factory 1.5

"""
GUI Layout Button Fixes - Fix button naming conflicts and change "Update List" to "Refresh"
"""

def fix_gui_layout_buttons(main_window):
    """Fix button naming conflicts in GUI layout"""
    try:
        # Find and fix buttons in the GUI layout
        if not hasattr(main_window, 'gui_layout'):
            main_window.log_message("❌ No gui_layout found")
            return False
        
        # Check for entry_buttons (from gui_layout.py)
        if hasattr(main_window.gui_layout, 'entry_buttons'):
            for btn in main_window.gui_layout.entry_buttons:
                if hasattr(btn, 'full_text'):
                    btn_text = btn.full_text
                    
                    # Fix button connections to match our function names
                    if btn_text == "Import":
                        btn.clicked.disconnect()  # Remove old connections
                        btn.clicked.connect(main_window.import_files)
                        main_window.log_message(f"🔧 Fixed Import button")
                    
                    elif btn_text == "Import via":
                        btn.clicked.disconnect()
                        btn.clicked.connect(main_window.import_files_via)
                        main_window.log_message(f"🔧 Fixed Import via button")
                    
                    elif btn_text == "Export":
                        btn.clicked.disconnect()
                        btn.clicked.connect(main_window.export_selected)
                        main_window.log_message(f"🔧 Fixed Export button")
                    
                    elif btn_text == "Export via":
                        btn.clicked.disconnect()
                        btn.clicked.connect(main_window.export_selected_via)
                        main_window.log_message(f"🔧 Fixed Export via button")
                    
                    elif btn_text == "Quick Export":
                        btn.clicked.disconnect()
                        btn.clicked.connect(main_window.quick_export_selected)
                        main_window.log_message(f"🔧 Fixed Quick Export button")
                    
                    elif btn_text == "Remove":
                        btn.clicked.disconnect()
                        btn.clicked.connect(main_window.remove_selected)
                        main_window.log_message(f"🔧 Fixed Remove button")
                    
                    elif btn_text == "Dump":
                        btn.clicked.disconnect()
                        btn.clicked.connect(main_window.dump_all_entries)
                        main_window.log_message(f"🔧 Fixed Dump button")
        
        # Check for other button containers
        if hasattr(main_window, 'entry_buttons'):
            for btn in main_window.entry_buttons:
                btn_text = btn.text()
                
                # Change "Update List" to "Refresh"
                if "Update" in btn_text or "Update list" in btn_text:
                    btn.setText("🔄 Refresh")
                    btn.clicked.disconnect()
                    btn.clicked.connect(main_window.refresh_table)
                    main_window.log_message(f"🔧 Changed Update List to Refresh")
        
        # Find all buttons by scanning the GUI for common button texts
        all_widgets = main_window.findChildren(QPushButton)
        for btn in all_widgets:
            btn_text = btn.text()
            
            # Change "Update List" variants to "Refresh"
            if any(text in btn_text.lower() for text in ["update list", "update lst"]):
                btn.setText("🔄 Refresh")
                try:
                    btn.clicked.disconnect()
                except:
                    pass
                btn.clicked.connect(main_window.refresh_table)
                main_window.log_message(f"🔧 Changed '{btn_text}' to 'Refresh'")
            
            # Fix export buttons that may be calling wrong methods
            elif "Export via" in btn_text:
                try:
                    btn.clicked.disconnect()
                except:
                    pass
                btn.clicked.connect(main_window.export_selected_via)
                main_window.log_message(f"🔧 Fixed '{btn_text}' button")
            
            elif "Quick" in btn_text and "Export" in btn_text:
                try:
                    btn.clicked.disconnect()
                except:
                    pass
                btn.clicked.connect(main_window.quick_export_selected)
                main_window.log_message(f"🔧 Fixed '{btn_text}' button")
        
        main_window.log_message("✅ GUI layout button conflicts resolved")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error fixing GUI buttons: {str(e)}")
        import traceback
        main_window.log_message(f"❌ Traceback: {traceback.format_exc()}")
        return False

def fix_gui_button_conflicts(main_window):
    """Main function to fix all GUI button conflicts"""
    try:
        from PyQt6.QtWidgets import QPushButton
        
        # Import the functions we need
        from components.img_import_export_functions import (
            import_files_function, import_via_function, export_selected_function,
            export_via_function, quick_export_function, export_all_function, remove_via_entries_function, dump_all_function

            remove_selected_function, dump_all_function
        )
        
        # Step 1: Add all possible method names
        add_missing_button_methods(main_window)
        
        # Step 2: Fix button connections
        fix_gui_layout_buttons(main_window)
        
        # Step 3: Log current button state
        main_window.log_message("📋 Available import/export methods:")
        methods_to_check = [
            'import_files', 'import_files_via', 'export_selected', 'export_selected_via', 
            'quick_export_selected', 'export_all_entries', 'remove_selected', 'dump_entries'
        ]
        
        for method_name in methods_to_check:
            if hasattr(main_window, method_name):
                main_window.log_message(f"   ✅ {method_name}")
            else:
                main_window.log_message(f"   ❌ {method_name} MISSING")
        
        main_window.log_message("✅ GUI button conflicts fixed")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error fixing button conflicts: {str(e)}")
        import traceback
        main_window.log_message(f"❌ Traceback: {traceback.format_exc()}")
        return False


# Export main function
__all__ = [
    'fix_gui_button_conflicts',
    'fix_gui_layout_buttons', 
]
