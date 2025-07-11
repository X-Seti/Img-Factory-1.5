#this belongs in components/img_import_export_integration.py - Version: 2
# X-Seti - July11 2025 - Img Factory 1.5
# Main integration module for import/export functionality

import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox, QApplication, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

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
        from components.img_import_export import get_selected_entries
        from utils.app_settings_system import AppSettings
        
        # Replace import_files method
        def new_import_files():
            """Import files with advanced dialog - uses project folder if set"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            # Check for project folder setting
            settings = AppSettings()
            project_folder = settings.get('project_folder', '')
            
            if project_folder and os.path.exists(project_folder):
                start_dir = project_folder
                main_window.log_message(f"📁 Using project folder: {project_folder}")
            else:
                start_dir = ""
            
            files, _ = QFileDialog.getOpenFileNames(
                main_window, "Import Files", start_dir,
                "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col)"
            )
            
            if files:
                options = {
                    'replace_existing': False,
                    'validate_files': True
                }
                from components.img_import_export import import_files_threaded
                import_files_threaded(main_window, files, options)
        
        # Replace import_via method  
        def new_import_via():
            """Import via IDE file or by folder"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            # Create choice dialog
            dialog = QDialog(main_window)
            dialog.setWindowTitle("Import Via Options")
            dialog.setModal(True)
            layout = QVBoxLayout(dialog)
            
            label = QLabel("Choose import method:")
            layout.addWidget(label)
            
            button_layout = QHBoxLayout()
            
            ide_btn = QPushButton("📄 Import from IDE File")
            ide_btn.clicked.connect(lambda: [dialog.accept(), import_from_ide_file()])
            
            folder_btn = QPushButton("📁 Import by Folder")
            folder_btn.clicked.connect(lambda: [dialog.accept(), import_by_folder()])
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(ide_btn)
            button_layout.addWidget(folder_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.exec()
            
            def import_from_ide_file():
                ide_file, _ = QFileDialog.getOpenFileName(
                    main_window, "Select IDE File", "", 
                    "IDE Files (*.ide);;Text Files (*.txt);;All Files (*)"
                )
                if ide_file:
                    options = {'replace_existing': True, 'validate_files': True}
                    from components.img_import_export import import_from_ide_file
                    import_from_ide_file(main_window, ide_file, options)
                    
            def import_by_folder():
                folder = QFileDialog.getExistingDirectory(main_window, "Select Folder to Import")
                if folder:
                    success, errors = main_window.current_img.import_directory(folder)
                    main_window.log_message(f"Folder import: {success} imported, {errors} errors")
                    if hasattr(main_window, '_update_ui_for_loaded_img'):
                        main_window._update_ui_for_loaded_img()
        
        # Replace export_selected method  
        def new_export_selected():
            """Export selected entries - uses export folder if set"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            selected_entries = get_selected_entries(main_window)
            if not selected_entries:
                QMessageBox.information(main_window, "No Selection", "Please select entries to export.")
                return
            
            # Check for export folder setting
            settings = AppSettings()
            export_folder = settings.get('export_folder', '')
            
            if export_folder and os.path.exists(export_folder):
                start_dir = export_folder
                main_window.log_message(f"📁 Using export folder: {export_folder}")
            else:
                start_dir = ""
            
            export_dir = QFileDialog.getExistingDirectory(main_window, "Export Selected Entries", start_dir)
            if export_dir:
                options = {
                    'preserve_structure': False,
                    'create_ide_file': False,
                    'overwrite_existing': True
                }
                from components.img_import_export import export_files_threaded
                export_files_threaded(main_window, selected_entries, export_dir, options)
        
        # Replace export_via method
        def new_export_via():
            """Export via existing IDE file - gather names and TXDs from IDE and export them"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            # Select IDE file to use as reference
            ide_file, _ = QFileDialog.getOpenFileName(
                main_window, "Select IDE File for Export Reference", "",
                "IDE Files (*.ide);;Text Files (*.txt);;All Files (*)"
            )
            
            if not ide_file:
                return
            
            try:
                # Parse IDE file to get list of models and their textures
                entries_to_export = []
                
                with open(ide_file, 'r') as f:
                    lines = f.readlines()
                
                model_names = set()
                txd_names = set()
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse IDE line - different formats possible
                        parts = line.split(',')
                        if len(parts) >= 2:
                            # Extract model name and TXD name
                            model_name = parts[1].strip()
                            if len(parts) >= 3:
                                txd_name = parts[2].strip()
                                txd_names.add(f"{txd_name}.txd")
                            model_names.add(f"{model_name}.dff")
                
                # Find matching entries in current IMG
                for entry in main_window.current_img.entries:
                    entry_name = getattr(entry, 'name', '')
                    if entry_name in model_names or entry_name in txd_names:
                        entries_to_export.append(entry)
                
                if entries_to_export:
                    export_dir = QFileDialog.getExistingDirectory(main_window, "Export IDE Referenced Files")
                    if export_dir:
                        options = {
                            'preserve_structure': True,
                            'create_ide_file': True,
                            'overwrite_existing': True
                        }
                        from components.img_import_export import export_files_threaded
                        export_files_threaded(main_window, entries_to_export, export_dir, options)
                        main_window.log_message(f"📄 Exported {len(entries_to_export)} entries referenced in IDE file")
                else:
                    QMessageBox.information(main_window, "No Matches", "No entries found matching the IDE file references.")
                    
            except Exception as e:
                QMessageBox.critical(main_window, "IDE Export Error", f"Failed to process IDE file: {str(e)}")
        
        # Replace quick_export method
        def new_quick_export():
            """Quick export selected to organized folders by type"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            selected_entries = get_selected_entries(main_window)
            if not selected_entries:
                QMessageBox.information(main_window, "No Selection", "Please select entries to export.")
                return
            
            # Get base export directory
            settings = AppSettings()
            base_export_dir = settings.get('quick_export_folder', 
                                         os.path.join(os.path.expanduser("~"), "Documents", "IMG_Exports"))
            
            os.makedirs(base_export_dir, exist_ok=True)
            
            # Export each file to its type-specific folder
            exported_count = 0
            for entry in selected_entries:
                entry_name = getattr(entry, 'name', f'entry_{exported_count}')
                file_ext = os.path.splitext(entry_name)[1].lower()
                
                # Determine subfolder by file type
                if file_ext == '.dff':
                    subfolder = 'models'
                elif file_ext == '.txd':
                    subfolder = 'textures'
                elif file_ext == '.col':
                    subfolder = 'collision'
                elif file_ext == '.ifp':
                    subfolder = 'animations'
                else:
                    subfolder = 'other'
                
                type_dir = os.path.join(base_export_dir, subfolder)
                os.makedirs(type_dir, exist_ok=True)
                
                output_path = os.path.join(type_dir, entry_name)
                if main_window.current_img.export_entry(entry, output_path):
                    exported_count += 1
                    main_window.log_message(f"⚡ Quick export: {entry_name} → {subfolder}/")
            
            main_window.log_message(f"⚡ Quick export complete: {exported_count} files to {base_export_dir}")
            QMessageBox.information(main_window, "Quick Export Complete", 
                                  f"Exported {exported_count} files to organized folders in:\n{base_export_dir}")
        
        # Replace export_all method
        def new_export_all():
            """Export all entries with advanced dialog"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            from components.img_import_export import show_export_dialog
            show_export_dialog(main_window, main_window.current_img.entries)
        
        # Replace dump method  
        def new_dump_all():
            """Dump all entries blindly to any folder"""
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            export_dir = QFileDialog.getExistingDirectory(main_window, "Dump All Entries to Folder")
            if not export_dir:
                return
            
            all_entries = main_window.current_img.entries
            
            # Simple dump - no organization, no IDE file, just extract everything
            exported_count = 0
            errors = 0
            
            for entry in all_entries:
                entry_name = getattr(entry, 'name', f'entry_{exported_count}')
                output_path = os.path.join(export_dir, entry_name)
                
                try:
                    if main_window.current_img.export_entry(entry, output_path):
                        exported_count += 1
                    else:
                        errors += 1
                except:
                    errors += 1
            
            main_window.log_message(f"🗂️ Dump complete: {exported_count} exported, {errors} errors")
            QMessageBox.information(main_window, "Dump Complete", 
                                  f"Dumped {exported_count} files to:\n{export_dir}\n{errors} files had errors.")
        
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
        main_window.remove_selected = new_remove_selected
        
        # Update button-specific method names
        main_window.import_files_via = new_import_via
        main_window.export_selected_via = new_export_via
        main_window.export_selected_entries = new_export_selected
        main_window.export_all_entries = new_export_all
        main_window.remove_selected_entries = new_remove_selected
        main_window.quick_export_selected = new_quick_export
        main_window.dump_entries = new_dump_all
        
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
            
            directory = QFileDialog.getExistingDirectory(main_window, "Select Directory to Import")
            if directory:
                success, errors = main_window.current_img.import_directory(directory)
                main_window.log_message(f"Directory import: {success} imported, {errors} errors")
                
                # Refresh the table
                if hasattr(main_window, '_update_ui_for_loaded_img'):
                    main_window._update_ui_for_loaded_img()
                
                QMessageBox.information(main_window, "Import Complete", 
                                      f"Imported {success} files from directory.\n{errors} files had errors.")
        
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
        main_window.rebuild_img = rebuild_img
        main_window.rebuild_img_as = rebuild_img_as
        
        main_window.log_message("✅ Convenience methods added")
        
    except Exception as e:
        main_window.log_message(f"❌ Error adding convenience methods: {str(e)}")

def setup_drag_drop_integration(main_window):
    """Setup drag and drop integration for importing files"""
    try:
        if not hasattr(main_window, 'setAcceptDrops'):
            return False
        
        # Enable drag and drop
        main_window.setAcceptDrops(True)
        
        # Store original drag/drop methods if they exist
        main_window._original_drag_enter = getattr(main_window, 'dragEnterEvent', None)
        main_window._original_drop = getattr(main_window, 'dropEvent', None)
        
        def enhanced_drag_enter_event(event):
            """Enhanced drag enter event for file imports"""
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
            elif main_window._original_drag_enter:
                main_window._original_drag_enter(event)
        
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
            elif main_window._original_drop:
                main_window._original_drop(event)
        
        # Replace drag/drop methods
        main_window.dragEnterEvent = enhanced_drag_enter_event
        main_window.dropEvent = enhanced_drop_event
        
        main_window.log_message("✅ Drag & Drop integration setup complete")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up drag & drop integration: {str(e)}")
        return False

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
        import_ide_action.triggered.connect(main_window.import_files_via)
        import_menu.addAction(import_ide_action)
        
        # Export submenu
        export_menu = file_menu.addMenu("Export")
        
        export_selected_action = QAction("Export Selected...", main_window)
        export_selected_action.setShortcut("Ctrl+E")
        export_selected_action.triggered.connect(main_window.export_selected)
        export_menu.addAction(export_selected_action)
        
        export_all_action = QAction("Export All...", main_window)
        export_all_action.triggered.connect(main_window.export_all_entries)
        export_menu.addAction(export_all_action)
        
        quick_export_action = QAction("Quick Export Selected", main_window)
        quick_export_action.setShortcut("Ctrl+Shift+E")
        quick_export_action.triggered.connect(main_window.quick_export_selected)
        export_menu.addAction(quick_export_action)
        
        export_menu.addSeparator()
        
        export_ide_action = QAction("Export via IDE File...", main_window)
        export_ide_action.triggered.connect(main_window.export_selected_via)
        export_menu.addAction(export_ide_action)
        
        dump_action = QAction("Dump All to Folder...", main_window)
        dump_action.triggered.connect(main_window.dump_entries)
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
        table._original_context_menu = getattr(table, 'contextMenuEvent', None)
        
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
        
        # Step 5: Update GUI layout buttons directly
        if update_gui_layout_buttons(main_window):
            success_count += 1
        
        main_window.log_message(f"✅ Import/Export integration complete: {success_count}/{total_steps} steps successful")
        
        return success_count == total_steps
        
    except Exception as e:
        main_window.log_message(f"❌ Error in complete import/export integration: {str(e)}")
        return False

def update_gui_layout_buttons(main_window):
    """Update GUI layout buttons directly instead of patching"""
    try:
        if not hasattr(main_window, 'gui_layout'):
            return False
        
        gui_layout = main_window.gui_layout
        
        # Update import buttons
        if hasattr(gui_layout, 'img_buttons'):
            for btn in gui_layout.img_buttons:
                if hasattr(btn, 'full_text'):
                    if 'Import' in btn.full_text and 'via' not in btn.full_text:
                        btn.clicked.connect(main_window.import_files)
                        btn.setToolTip("Import files (uses project folder if set)")
        
        if hasattr(gui_layout, 'entry_buttons'):
            for btn in gui_layout.entry_buttons:
                if hasattr(btn, 'full_text'):
                    btn_text = btn.full_text
                    
                    # Import buttons
                    if btn_text == "Import":
                        btn.clicked.connect(main_window.import_files)
                        btn.setToolTip("Import files from any folder (or project folder if set)")
                    elif btn_text == "Import via":
                        btn.clicked.connect(main_window.import_files_via)
                        btn.setToolTip("Import via IDE file or by folder")
                    
                    # Export buttons
                    elif btn_text == "Export":
                        btn.clicked.connect(main_window.export_selected)
                        btn.setToolTip("Export selected entries (uses export folder if set)")
                    elif btn_text == "Export via":
                        btn.clicked.connect(main_window.export_selected_via)
                        btn.setToolTip("Export entries referenced in existing IDE file")
                    elif btn_text == "Quick Export":
                        btn.clicked.connect(main_window.quick_export_selected)
                        btn.setToolTip("Quick export to organized folders by file type")
                    
                    # Management buttons
                    elif btn_text == "Dump":
                        btn.clicked.connect(main_window.dump_entries)
                        btn.setToolTip("Dump ALL entries to any folder")
                    elif btn_text == "Remove":
                        btn.clicked.connect(main_window.remove_selected)
                        btn.setToolTip("Remove selected entries")
        
        main_window.log_message("✅ GUI layout buttons updated with new functionality")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error updating GUI layout buttons: {str(e)}")
        return False

# Export main function
__all__ = [
    'integrate_import_export_to_main_window',
    'setup_complete_import_export_integration',
    'setup_import_export_menu',
    'setup_context_menu_integration', 
    'setup_drag_drop_integration',
    'update_gui_layout_buttons'
]