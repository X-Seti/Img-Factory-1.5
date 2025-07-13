#this belongs in components/ img_integration_main.py - Version: 2
# X-Seti - July13 2025 - Img Factory 1.5
# Main integration module - Consolidated and cleaned

#!/usr/bin/env python3
"""
IMG Integration Main - Single point integration for all IMG functionality
Removes duplicates and provides clean integration path
"""

import os
from typing import Optional
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer


def integrate_complete_img_system(main_window):
    """Complete IMG system integration - single function does everything"""
    try:
        main_window.log_message("🔧 Starting complete IMG system integration...")
        
        # Step 1: Integrate core class methods (utilities, validation)
        from components.img_core_classes_addon import integrate_core_class_methods
        if not integrate_core_class_methods():
            main_window.log_message("⚠️ Core class methods integration had issues, continuing...")
        else:
            main_window.log_message("✅ Core class methods integrated")
        
        # Step 2: Integrate main import/export functionality
        from components.img_import_export_functions import integrate_clean_import_export
        if not integrate_clean_import_export(main_window):
            main_window.log_message("❌ Failed to integrate import/export system")
            return False
        
        main_window.log_message("✅ Import/Export system integrated")
        
        # Step 3: Add any missing convenience methods
        add_convenience_methods(main_window)
        
        # Step 4: Initialize settings integration
        initialize_settings_integration(main_window)
        
        main_window.log_message("✅ Complete IMG system integration finished")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ IMG system integration error: {str(e)}")
        return False


def add_convenience_methods(main_window):
    """Add convenience methods that bridge different systems"""
    try:
        # Refresh table method (if not already present)
        if not hasattr(main_window, 'refresh_table'):
            def refresh_table():
                """Refresh the entries table"""
                try:
                    if hasattr(main_window, 'populate_entries_table'):
                        main_window.populate_entries_table()
                    elif hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'update_table'):
                        main_window.gui_layout.update_table()
                    main_window.log_message("🔄 Table refreshed")
                except Exception as e:
                    main_window.log_message(f"❌ Table refresh error: {str(e)}")
            
            main_window.refresh_table = refresh_table
        
        # Validate IMG method
        if not hasattr(main_window, 'validate_img'):
            def validate_img():
                """Validate current IMG file"""
                try:
                    if not hasattr(main_window, 'current_img') or not main_window.current_img:
                        QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                        return
                    
                    if hasattr(main_window.current_img, 'validate_integrity'):
                        is_valid, message = main_window.current_img.validate_integrity()
                        if is_valid:
                            QMessageBox.information(main_window, "Validation Result", f"✅ {message}")
                            main_window.log_message(f"✅ Validation: {message}")
                        else:
                            QMessageBox.warning(main_window, "Validation Issues", f"⚠️ {message}")
                            main_window.log_message(f"⚠️ Validation: {message}")
                    else:
                        QMessageBox.information(main_window, "Validation", "Basic validation: IMG file appears to be loaded correctly.")
                        main_window.log_message("ℹ️ Basic validation completed")
                        
                except Exception as e:
                    main_window.log_message(f"❌ Validation error: {str(e)}")
            
            main_window.validate_img = validate_img
        
        # Show IMG info method
        if not hasattr(main_window, 'show_img_info'):
            def show_img_info():
                """Show IMG file information"""
                try:
                    if not hasattr(main_window, 'current_img') or not main_window.current_img:
                        QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                        return
                    
                    if hasattr(main_window.current_img, 'get_file_statistics'):
                        stats = main_window.current_img.get_file_statistics()
                        
                        info_text = f"IMG File Information:\n\n"
                        info_text += f"Total Entries: {stats.get('total_entries', 0)}\n"
                        info_text += f"Total Size: {_format_size(stats.get('total_size', 0))}\n\n"
                        
                        info_text += "File Types:\n"
                        for file_type, count in stats.get('file_types', {}).items():
                            info_text += f"  {file_type}: {count}\n"
                        
                        if stats.get('largest_entry'):
                            largest = stats['largest_entry']
                            info_text += f"\nLargest Entry: {largest['name']} ({_format_size(largest['size'])})"
                        
                        if stats.get('smallest_entry'):
                            smallest = stats['smallest_entry']
                            info_text += f"\nSmallest Entry: {smallest['name']} ({_format_size(smallest['size'])})"
                        
                        QMessageBox.information(main_window, "IMG File Information", info_text)
                    else:
                        # Basic info
                        entry_count = len(main_window.current_img.entries) if hasattr(main_window.current_img, 'entries') else 0
                        QMessageBox.information(main_window, "IMG File Information", f"Entries: {entry_count}")
                        
                except Exception as e:
                    main_window.log_message(f"❌ Show info error: {str(e)}")
            
            main_window.show_img_info = show_img_info
        
        main_window.log_message("✅ Convenience methods added")
        
    except Exception as e:
        main_window.log_message(f"❌ Convenience methods error: {str(e)}")


def initialize_settings_integration(main_window):
    """Initialize settings integration for import/export paths"""
    try:
        # Set up project folder integration if available
        if hasattr(main_window, 'app_settings'):
            settings = main_window.app_settings.current_settings
            
            # Check for project folder setting
            project_folder = settings.get('project_folder', '')
            if project_folder and os.path.exists(project_folder):
                main_window.log_message(f"📁 Project folder: {project_folder}")
            
            # Check for export folder setting
            export_folder = settings.get('export_folder', '')
            if export_folder and os.path.exists(export_folder):
                main_window.log_message(f"📤 Export folder: {export_folder}")
            
            # Check for auto-backup setting
            auto_backup = settings.get('auto_backup', False)
            if auto_backup:
                main_window.log_message("💾 Auto-backup enabled")
        
        main_window.log_message("✅ Settings integration initialized")
        
    except Exception as e:
        main_window.log_message(f"❌ Settings integration error: {str(e)}")


def _format_size(size: int) -> str:
    """Format file size for display"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


# ============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# ============================================================================

def integrate_import_export_to_main_window(main_window):
    """Legacy function - redirects to new consolidated integration"""
    try:
        main_window.log_message("⚠️ Using legacy integration function - redirecting to new system")
        return integrate_complete_img_system(main_window)
    except Exception as e:
        main_window.log_message(f"❌ Legacy integration error: {str(e)}")
        return False


def update_main_window_methods(main_window):
    """Legacy function - now handled by main integration"""
    try:
        main_window.log_message("ℹ️ update_main_window_methods is now handled by integrate_complete_img_system")
        return True
    except Exception as e:
        main_window.log_message(f"❌ Legacy method update error: {str(e)}")
        return False


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Main integration function
    'integrate_complete_img_system',
    
    # Helper functions
    'add_convenience_methods',
    'initialize_settings_integration',
    
    # Legacy compatibility
    'integrate_import_export_to_main_window',
    'update_main_window_methods'
]