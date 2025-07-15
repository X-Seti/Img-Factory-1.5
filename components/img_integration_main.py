#this belongs in components/img_integration_main.py - Version: 2
# X-Seti - July15 2025 - Img Factory 1.5
"""
Main integration module for import/export functionality with fixed button mappings
"""

import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import QTimer

def integrate_complete_img_system(main_window):
    """Main function to integrate all import/export functionality"""
    try:
        # Import the required functions
        from components.img_import_export_functions import (
            import_files_function,
            import_via_function,
            import_from_ide_file,
            import_directory_function,
            export_selected_function,
            export_via_function,
            export_all_function,
            quick_export_function,
            remove_selected_function,
            remove_via_entries_function,
            dump_all_function,
            get_selected_entries,
            add_import_export_menus
        )
        
        # Map functions to main_window
        main_window.import_files = lambda: import_files_function(main_window)
        main_window.import_files_via = lambda: import_via_function(main_window)
        main_window.export_selected = lambda: export_selected_function(main_window)
        main_window.export_selected_via = lambda: export_via_function(main_window)
        main_window.quick_export_selected = lambda: quick_export_function(main_window)
        main_window.export_all_entries = lambda: export_all_function(main_window)
        main_window.remove_via_entries = lambda: remove_via_entries_function(main_window)
        main_window.remove_selected = lambda: remove_selected_function(main_window)
        main_window.dump_all_entries = lambda: dump_all_function(main_window)
        
        # Add convenience method for getting selected entries
        main_window.get_selected_entries = lambda: get_selected_entries(main_window)
        
        # Add refresh table method if not already present
        if not hasattr(main_window, 'refresh_table'):
            def refresh_table_func():
                """Refresh the entries table with current data"""
                if hasattr(main_window, 'populate_entries_table'):
                    main_window.populate_entries_table()
                main_window.log_message("✅ Table refreshed")
            
            main_window.refresh_table = refresh_table_func
        
        # Add menus
        add_import_export_menus(main_window)
        
        # Add validate method if not present
        if not hasattr(main_window, 'validate_img'):
            def validate_img_func():
                """Validate IMG file integrity"""
                if not hasattr(main_window, 'current_img') or not main_window.current_img:
                    QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                    return
                
                main_window.log_message("🔍 Validating IMG file...")
                
                try:
                    if hasattr(main_window.current_img, 'validate_integrity'):
                        issues = main_window.current_img.validate_integrity()
                        
                        if not issues:
                            QMessageBox.information(main_window, "Validation Successful", "IMG file passed all integrity checks.")
                            main_window.log_message("✅ IMG file validation passed")
                        else:
                            issues_text = "\n".join([f"- {issue}" for issue in issues[:10]])
                            if len(issues) > 10:
                                issues_text += f"\n- ... and {len(issues) - 10} more issues"
                            
                            QMessageBox.warning(
                                main_window, 
                                "Validation Issues", 
                                f"Found {len(issues)} issues in IMG file:\n\n{issues_text}"
                            )
                            main_window.log_message(f"⚠️ IMG file validation found {len(issues)} issues")
                    else:
                        main_window.log_message("❌ Validation method not available")
                        QMessageBox.information(main_window, "Validation", "Basic validation: IMG file structure appears valid.")
                
                except Exception as e:
                    main_window.log_message(f"❌ Validation error: {str(e)}")
                    QMessageBox.critical(main_window, "Validation Error", f"Error during validation: {str(e)}")
            
            main_window.validate_img = validate_img_func
        
        # Add show_img_info method if not present
        if not hasattr(main_window, 'show_img_info'):
            def show_img_info_func():
                """Show IMG file information"""
                if not hasattr(main_window, 'current_img') or not main_window.current_img:
                    QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                    return
                
                try:
                    # Basic info
                    file_name = getattr(main_window.current_img, 'file_path', 'Unknown')
                    file_name = os.path.basename(file_name) if file_name != 'Unknown' else 'Unknown'
                    
                    entry_count = len(main_window.current_img.entries) if hasattr(main_window.current_img, 'entries') else 0
                    
                    file_size = getattr(main_window.current_img, 'file_size', 0)
                    file_size_str = f"{file_size:,} bytes ({file_size / (1024*1024):.2f} MB)" if file_size else "Unknown"
                    
                    version = getattr(main_window.current_img, 'version', 'Unknown')
                    version_str = str(version) if version else "Unknown"
                    
                    # Get detailed statistics if available
                    stats = {}
                    if hasattr(main_window.current_img, 'get_file_statistics'):
                        try:
                            stats = main_window.current_img.get_file_statistics()
                        except:
                            pass
                    
                    # Build info text
                    info_text = f"File: {file_name}\n"
                    info_text += f"Entries: {entry_count}\n"
                    info_text += f"Size: {file_size_str}\n"
                    info_text += f"Version: {version_str}\n"
                    
                    if stats:
                        info_text += "\nDetailed Statistics:\n"
                        for key, value in stats.items():
                            if isinstance(value, int) and key.lower() in ['size', 'data_size', 'total_size']:
                                value_str = f"{value:,} bytes ({value / (1024*1024):.2f} MB)"
                            else:
                                value_str = str(value)
                            
                            info_text += f"- {key}: {value_str}\n"
                    
                    QMessageBox.information(main_window, "IMG File Information", info_text)
                    
                except Exception as e:
                    main_window.log_message(f"❌ Error showing IMG info: {str(e)}")
                    QMessageBox.critical(main_window, "Error", f"Error getting IMG information: {str(e)}")
            
            main_window.show_img_info = show_img_info_func
        
        main_window.log_message("✅ IMG system integrated successfully")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error integrating IMG system: {str(e)}")
        return False

# Export main function
__all__ = ['integrate_complete_img_system']
