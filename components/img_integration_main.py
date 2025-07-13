#this belongs in components/img_integration_main.py - Version: 1
# X-Seti - July11 2025 - Img Factory 1.5
# Main integration module for import/export functionality

import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import QTimer

def integrate_import_export_to_main_window(main_window):
    """Main function to integrate all import/export functionality"""
    try:
        # Step 1: Patch existing IMG classes with import/export methods
        from components.img_core_classes_addon import integrate_import_export_methods
        if not integrate_import_export_methods():
            main_window.log_message("❌ Failed to patch IMG classes with import/export methods")
            return False
        
        main_window.log_message("✅ IMG classes patched with import/export methods")
        
        # Step 2: Import the required modules
        from components.img_import_export import (
            integrate_import_export_system, 
            show_import_dialog, 
            show_export_dialog,
            dump_all_entries,
            get_selected_entries
        )
        
        # Step 3: Integrate the system
        if integrate_import_export_system(main_window):
            main_window.log_message("✅ Import/Export system integrated successfully")
            
            # Update the existing placeholder methods in imgfactory.py
            update_main_window_methods(main_window)
            
            # Add new convenience methods
            add_convenience_methods(main_window)
            
            return True
        else:
            main_window.log_message("❌ Failed to integrate import/export system")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Error integrating import/export: {str(e)}")
        return False

def update_main_window_methods(main_window):
    """Update existing methods in main window to use new system"""
    try:
        from components.img_import_export import (
            show_import_dialog, 
            show_export_dialog,
            get_selected_entries
        )
        
        # Replace import_files method
        def new_import_files():
            """Import files with advanced dialog"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            show_import_dialog(main_window)
        
        # Replace export_selected method  
        def new_export_selected():
            """Export selected entries with advanced dialog"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            selected_entries = get_selected_entries(main_window)
            if selected_entries:
                show_export_dialog(main_window, selected_entries)
            else:
                QMessageBox.information(main_window, "No Selection", "Please select entries to export.")
        
        # Replace export_all method
        def new_export_all():
            """Export all entries with advanced dialog"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            show_export_dialog(main_window, main_window.current_img.entries)
        
        # Replace remove_selected method
        def new_remove_selected():
            """Remove selected entries with confirmation"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            selected_entries = get_selected_entries(main_window)
            if not selected_entries:
                QMessageBox.information(main_window, "No Selection", "Please select entries to remove.")
                return
            
            # Confirm removal
            reply = QMessageBox.question(
                main_window, "Confirm Removal", 
                f"Remove {len(selected_entries)} selected entries?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                removed_count = 0
                for entry in selected_entries:
                    if main_window.current_img.remove_entry(entry):
                        removed_count += 1
                        main_window.log_message(f"🗑️ Removed: {entry.name}")
                
                main_window.log_message(f"Removal complete: {removed_count} entries removed")
                
                # Refresh the table
                if hasattr(main_window, '_update_ui_for_loaded_img'):
                    main_window._update_ui_for_loaded_img()
                
                QMessageBox.information(main_window, "Removal Complete", 
                                      f"Removed {removed_count} entries successfully.")
        
        # Update the methods in main window
        main_window.import_files = new_import_files
        main_window.export_selected = new_export_selected  
        main_window.export_all = new_export_all
        main_window.remove_selected = new_remove_selected
        
        main_window.log_message("✅ Main window methods updated")
        
    except Exception as e:
        main_window.log_message(f"❌ Error updating main window methods: {str(e)}")

def add_convenience_methods(main_window):
    """Add new convenience methods to main window"""
    try:
        from components.img_import_export import dump_all_entries
        
        # Quick import from directory
        def quick_import_directory():
            """Quick import all files from a directory"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            from PyQt6.QtWidgets import QFileDialog
            directory = QFileDialog.getExistingDirectory(main_window, "Select Directory to Import")
            if directory:
                success, errors = main_window.current_img.import_directory(directory)
                main_window.log_message(f"Directory import: {success} imported, {errors} errors")
                
                # Refresh the table
                if hasattr(main_window, '_update_ui_for_loaded_img'):
                    main_window._update_ui_for_loaded_img()
                
                QMessageBox.information(main_window, "Import Complete", 
                                      f"Imported {success} files from directory.\n{errors} files had errors.")
        
        # Quick export to default location
        def quick_export_selected():
            """Quick export selected files to Documents/IMG_Exports"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            from components.img_import_export import get_selected_entries
            selected_entries = get_selected_entries(main_window)
            if not selected_entries:
                QMessageBox.information(main_window, "No Selection", "Please select entries to export.")
                return
            
            # Use Documents/IMG_Exports as default
            export_dir = os.path.join(os.path.expanduser("~"), "Documents", "IMG_Exports")
            os.makedirs(export_dir, exist_ok=True)
            
            success = 0
            errors = 0
            for entry in selected_entries:
                if main_window.current_img.export_entry(entry, os.path.join(export_dir, entry.name)):
                    success += 1
                else:
                    errors += 1
            
            main_window.log_message(f"Quick export: {success} exported, {errors} errors")
            QMessageBox.information(main_window, "Export Complete", 
                                  f"Exported {success} files to {export_dir}\n{errors} files had errors.")
        
        # Import via IDE file
        def import_via_ide():
            """Import files using an IDE file as guide"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            from PyQt6.QtWidgets import QFileDialog
            from components.img_import_export import import_from_ide_file
            
            ide_file, _ = QFileDialog.getOpenFileName(
                main_window, "Select IDE File", "", 
                "IDE Files (*.ide);;Text Files (*.txt);;All Files (*)"
            )
            
            if ide_file:
                options = {
                    'replace_existing': True,
                    'validate_files': True
                }
                import_from_ide_file(main_window, ide_file, options)
        
        # Export with IDE file creation
        def export_with_ide():
            """Export all files and create IDE listing"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            from PyQt6.QtWidgets import QFileDialog
            export_dir = QFileDialog.getExistingDirectory(main_window, "Select Export Directory")
            if export_dir:
                options = {
                    'preserve_structure': True,
                    'create_ide_file': True,
                    'overwrite_existing': True
                }
                
                from components.img_import_export import export_files_threaded
                export_files_threaded(main_window, main_window.current_img.entries, export_dir, options)
        
        # Rebuild IMG file
        def rebuild_img():
            """Rebuild the current IMG file"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            reply = QMessageBox.question(
                main_window, "Rebuild IMG", 
                "Rebuild the IMG file with current changes?\nThis will modify the original file.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if main_window.current_img.rebuild():
                    main_window.log_message("✅ IMG file rebuilt successfully")
                    QMessageBox.information(main_window, "Rebuild Complete", "IMG file rebuilt successfully.")
                else:
                    main_window.log_message("❌ Failed to rebuild IMG file")
                    QMessageBox.critical(main_window, "Rebuild Error", "Failed to rebuild IMG file.")
        
        # Rebuild as new file
        def rebuild_img_as():
            """Rebuild IMG file with new name"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            from PyQt6.QtWidgets import QFileDialog
            new_path, _ = QFileDialog.getSaveFileName(
                main_window, "Save IMG As", "", 
                "IMG Files (*.img);;All Files (*)"
            )
            
            if new_path:
                # Save original path
                original_path = main_window.current_img.file_path
                
                # Set new path and rebuild
                main_window.current_img.file_path = new_path
                if main_window.current_img.rebuild():
                    main_window.log_message(f"✅ IMG file saved as: {new_path}")
                    QMessageBox.information(main_window, "Save Complete", f"IMG file saved as: {os.path.basename(new_path)}")
                else:
                    # Restore original path on failure
                    main_window.current_img.file_path = original_path
                    main_window.log_message("❌ Failed to save IMG file")
                    QMessageBox.critical(main_window, "Save Error", "Failed to save IMG file.")
        
        # Add methods to main window
        main_window.quick_import_directory = quick_import_directory
        main_window.quick_export_selected = quick_export_selected
        main_window.import_via_ide = import_via_ide
        main_window.export_with_ide = export_with_ide
        main_window.rebuild_img = rebuild_img
        main_window.rebuild_img_as = rebuild_img_as
        main_window.dump_all_entries = lambda: dump_all_entries(main_window)
        
        main_window.log_message("✅ Convenience methods added")
        
    except Exception as e:
        main_window.log_message(f"❌ Error adding convenience methods: {str(e)}")

def setup_import_export_menu(main_window):
    """Setup import/export menu items"""
    try:
        if not hasattr(main_window, 'menubar'):
            return False
        
        # Create File menu if it doesn't exist
        file_menu = None
        for action in main_window.menubar.actions():
            if action.text() == "File":
                file_menu = action.menu()
                break
        
        if not file_menu:
            file_menu = main_window.menubar.addMenu("File")
        
        # Add separator
        file_menu.addSeparator()
        
        # Import submenu
        import_menu = file_menu.addMenu("Import")
        
        from PyQt6.QtGui import QAction
        
        import_files_action = QAction("Import Files...", main_window)
        import_files_action.setShortcut("Ctrl+I")
        import_files_action.triggered.connect(main_window.import_files)
        import_menu.addAction(import_files_action)
        
        import_dir_action = QAction("Import Directory...", main_window)
        import_dir_action.triggered.connect(main_window.quick_import_directory)
        import_menu.addAction(import_dir_action)
        
        import_ide_action = QAction("Import via IDE File...", main_window)
        import_ide_action.triggered.connect(main_window.import_via_ide)
        import_menu.addAction(import_ide_action)
        
        # Export submenu
        export_menu = file_menu.addMenu("Export")
        
        export_selected_action = QAction("Export Selected...", main_window)
        export_selected_action.setShortcut("Ctrl+E")
        export_selected_action.triggered.connect(main_window.export_selected)
        export_menu.addAction(export_selected_action)
        
        export_all_action = QAction("Export All...", main_window)
        export_all_action.triggered.connect(main_window.export_all)
        export_menu.addAction(export_all_action)
        
        quick_export_action = QAction("Quick Export Selected", main_window)
        quick_export_action.setShortcut("Ctrl+Shift+E")
        quick_export_action.triggered.connect(main_window.quick_export_selected)
        export_menu.addAction(quick_export_action)
        
        export_menu.addSeparator()
        
        export_ide_action = QAction("Export with IDE File...", main_window)
        export_ide_action.triggered.connect(main_window.export_with_ide)
        export_menu.addAction(export_ide_action)
        
        dump_action = QAction("Dump All to Folder...", main_window)
        dump_action.triggered.connect(main_window.dump_all_entries)
        export_menu.addAction(dump_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Rebuild actions
        rebuild_action = QAction("Rebuild IMG", main_window)
        rebuild_action.setShortcut("Ctrl+R")
        rebuild_action.triggered.connect(main_window.rebuild_img)
        file_menu.addAction(rebuild_action)
        
        rebuild_as_action = QAction("Rebuild IMG As...", main_window)
        rebuild_as_action.setShortcut("Ctrl+Shift+S")
        rebuild_as_action.triggered.connect(main_window.rebuild_img_as)
        file_menu.addAction(rebuild_as_action)
        
        main_window.log_message("✅ Import/Export menu setup complete")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up import/export menu: {str(e)}")
        return False

def setup_context_menu_integration(main_window):
    """Setup context menu integration for table entries"""
    try:
        if not hasattr(main_window.gui_layout, 'table'):
            return False
        
        table = main_window.gui_layout.table
        
        # Store original context menu method
        if hasattr(table, 'contextMenuEvent'):
            original_context_menu = table.contextMenuEvent
        else:
            original_context_menu = None
        
        def enhanced_context_menu(event):
            """Enhanced context menu with import/export options"""
            from PyQt6.QtWidgets import QMenu
            from PyQt6.QtGui import QAction
            from components.img_import_export import get_selected_entries
            
            menu = QMenu(table)
            
            # Get selected entries
            selected_entries = get_selected_entries(main_window)
            
            if selected_entries:
                # Export options
                export_action = QAction("Export Selected...", menu)
                export_action.triggered.connect(lambda: main_window.export_selected())
                menu.addAction(export_action)
                
                quick_export_action = QAction("Quick Export", menu)
                quick_export_action.triggered.connect(lambda: main_window.quick_export_selected())
                menu.addAction(quick_export_action)
                
                menu.addSeparator()
                
                # Remove option
                remove_action = QAction("Remove Selected", menu)
                remove_action.triggered.connect(lambda: main_window.remove_selected())
                menu.addAction(remove_action)
                
                menu.addSeparator()
            
            # Import options (always available)
            import_action = QAction("Import Files...", menu)
            import_action.triggered.connect(lambda: main_window.import_files())
            menu.addAction(import_action)
            
            import_dir_action = QAction("Import Directory...", menu)
            import_dir_action.triggered.connect(lambda: main_window.quick_import_directory())
            menu.addAction(import_dir_action)
            
            # Show menu
            if not menu.isEmpty():
                menu.exec(event.globalPos())
        
        # Replace context menu method
        table.contextMenuEvent = enhanced_context_menu
        
        main_window.log_message("✅ Context menu integration setup complete")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up context menu integration: {str(e)}")
        return False

def setup_drag_drop_integration(main_window):
    """Setup drag and drop integration for importing files"""
    try:
        if not hasattr(main_window, 'setAcceptDrops'):
            return False
        
        # Enable drag and drop
        main_window.setAcceptDrops(True)
        
        # Store original drag/drop methods
        original_drag_enter = getattr(main_window, 'dragEnterEvent', None)
        original_drop = getattr(main_window, 'dropEvent', None)
        
        def enhanced_drag_enter_event(event):
            """Enhanced drag enter event for file imports"""
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
            elif original_drag_enter:
                original_drag_enter(event)
        
        def enhanced_drop_event(event):
            """Enhanced drop event for file imports"""
            if event.mimeData().hasUrls():
                if not hasattr(main_window, 'current_img') or not main_window.current_img:
                    QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                    return
                
                # Get dropped files
                files = []
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if os.path.isfile(file_path):
                            files.append(file_path)
                        elif os.path.isdir(file_path):
                            # Add all files from directory
                            for root, dirs, filenames in os.walk(file_path):
                                for filename in filenames:
                                    files.append(os.path.join(root, filename))
                
                if files:
                    # Import files using background thread
                    options = {
                        'replace_existing': False,
                        'validate_files': True
                    }
                    
                    from components.img_import_export import import_files_threaded
                    import_files_threaded(main_window, files, options)
                    
                    main_window.log_message(f"📥 Drag & Drop: importing {len(files)} files")
                
                event.acceptProposedAction()
            elif original_drop:
                original_drop(event)
        
        # Replace drag/drop methods
        main_window.dragEnterEvent = enhanced_drag_enter_event
        main_window.dropEvent = enhanced_drop_event
        
        main_window.log_message("✅ Drag & Drop integration setup complete")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up drag & drop integration: {str(e)}")
        return False

# Main integration function
def setup_complete_import_export_integration(main_window):
    """Setup complete import/export integration"""
    try:
        success_count = 0
        total_steps = 5
        
        # Step 1: Integrate core system
        if integrate_import_export_to_main_window(main_window):
            success_count += 1
        
        # Step 2: Setup menu integration
        if setup_import_export_menu(main_window):
            success_count += 1
        
        # Step 3: Setup context menu integration
        if setup_context_menu_integration(main_window):
            success_count += 1
        
        # Step 4: Setup drag & drop integration
        if setup_drag_drop_integration(main_window):
            success_count += 1
        
        # Step 5: Final validation
        if hasattr(main_window, 'import_files') and hasattr(main_window, 'export_selected'):
            success_count += 1
            main_window.log_message("✅ Import/Export validation passed")
        
        main_window.log_message(f"✅ Import/Export integration complete: {success_count}/{total_steps} steps successful")
        
        return success_count == total_steps
        
    except Exception as e:
        main_window.log_message(f"❌ Error in complete import/export integration: {str(e)}")
        return False

# Export main function
__all__ = [
    'integrate_import_export_to_main_window',
    'setup_complete_import_export_integration',
    'setup_import_export_menu',
    'setup_context_menu_integration', 
    'setup_drag_drop_integration'
]
        