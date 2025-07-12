#this belongs in components/ img_import_export_functions.py - Version: 4
# X-Seti - July12 2025 - Img Factory 1.5

"""
Clean Import/Export Functions - Fixed AppSettings usage and COL export issues
Fixes: AppSettings.get() -> AppSettings.current_settings.get()
"""

import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox, QFileDialog


def get_selected_entries(main_window):
    """Get currently selected entries from the table - FIXED"""
    try:
        selected_entries = []
        
        # Try multiple ways to get the table
        table = None
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
        elif hasattr(main_window, 'table'):
            table = main_window.table
        elif hasattr(main_window, 'entries_table'):
            table = main_window.entries_table
        
        if not table:
            main_window.log_message("❌ Could not find table widget")
            return []
        
        # Debug: Log table info
        main_window.log_message(f"🔍 Table found: {type(table).__name__}")
        
        # Get selected rows using selection model
        selection_model = table.selectionModel()
        if selection_model:
            selected_indexes = selection_model.selectedRows()
            selected_rows = [index.row() for index in selected_indexes]
        else:
            # Fallback: Use selectedItems
            selected_rows = set()
            for item in table.selectedItems():
                selected_rows.add(item.row())
            selected_rows = list(selected_rows)
        
        main_window.log_message(f"🔍 Selected rows detected: {len(selected_rows)}")
        
        # Get entries from IMG file
        if hasattr(main_window, 'current_img') and main_window.current_img and hasattr(main_window.current_img, 'entries'):
            for row in selected_rows:
                if 0 <= row < len(main_window.current_img.entries):
                    selected_entries.append(main_window.current_img.entries[row])
        
        main_window.log_message(f"✅ Found {len(selected_entries)} selected entries")
        return selected_entries
        
    except Exception as e:
        main_window.log_message(f"❌ Error getting selected entries: {str(e)}")
        import traceback
        main_window.log_message(f"❌ Traceback: {traceback.format_exc()}")
        return []


def import_files_function(main_window):
    """Import files into current IMG - Clean version"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        # Get project folder setting - FIXED: Use current_settings.get()
        try:
            from utils.app_settings_system import AppSettings
            settings = AppSettings()
            project_folder = settings.current_settings.get('project_folder', '')
        except:
            project_folder = ''
        
        # Set start directory
        if project_folder and os.path.exists(project_folder):
            start_dir = project_folder
            main_window.log_message(f"📁 Using project folder: {project_folder}")
        else:
            start_dir = os.path.expanduser("~")
        
        # File selection dialog
        files, _ = QFileDialog.getOpenFileNames(
            main_window, 
            "Import Files", 
            start_dir,
            "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col);;IFP Animations (*.ifp)"
        )
        
        if not files:
            return
        
        # Import each file
        imported_count = 0
        failed_count = 0
        
        for file_path in files:
            try:
                filename = os.path.basename(file_path)
                
                # Read file data
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # Add to IMG
                if main_window.current_img.add_entry(filename, file_data):
                    imported_count += 1
                    main_window.log_message(f"📥 Imported: {filename}")
                else:
                    failed_count += 1
                    main_window.log_message(f"❌ Failed to import: {filename}")
                    
            except Exception as e:
                failed_count += 1
                main_window.log_message(f"❌ Error importing {os.path.basename(file_path)}: {str(e)}")
        
        # Update table
        if hasattr(main_window, 'populate_entries_table'):
            main_window.populate_entries_table()
        
        # Show results
        QMessageBox.information(
            main_window, 
            "Import Complete", 
            f"Imported {imported_count} files successfully.\n{failed_count} files failed."
        )
        
    except Exception as e:
        main_window.log_message(f"❌ Import error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Import failed: {str(e)}")


def export_selected_function(main_window):
    """Export selected entries - Clean version"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to export.")
            return
        
        # Get export folder setting - FIXED: Use current_settings.get()
        try:
            from utils.app_settings_system import AppSettings
            settings = AppSettings()
            export_folder = settings.current_settings.get('export_folder', '')
        except:
            export_folder = ''
        
        # Set start directory
        if export_folder and os.path.exists(export_folder):
            start_dir = export_folder
            main_window.log_message(f"📁 Using export folder: {export_folder}")
        else:
            start_dir = os.path.expanduser("~")
        
        # Directory selection
        export_dir = QFileDialog.getExistingDirectory(main_window, "Export Selected Entries", start_dir)
        if not export_dir:
            return
        
        # Export each selected entry
        exported_count = 0
        failed_count = 0
        
        for entry in selected_entries:
            try:
                entry_name = getattr(entry, 'name', f'entry_{exported_count}')
                output_path = os.path.join(export_dir, entry_name)
                
                # Get entry data
                if hasattr(entry, 'get_data'):
                    entry_data = entry.get_data()
                elif hasattr(main_window.current_img, 'export_entry'):
                    if main_window.current_img.export_entry(entry, output_path):
                        exported_count += 1
                        main_window.log_message(f"📤 Exported: {entry_name}")
                        continue
                    else:
                        failed_count += 1
                        continue
                else:
                    main_window.log_message(f"❌ Cannot export {entry_name}: No export method")
                    failed_count += 1
                    continue
                
                # Write data to file
                with open(output_path, 'wb') as f:
                    f.write(entry_data)
                
                exported_count += 1
                main_window.log_message(f"📤 Exported: {entry_name}")
                
            except Exception as e:
                failed_count += 1
                entry_name = getattr(entry, 'name', 'unknown')
                main_window.log_message(f"❌ Export failed for {entry_name}: {str(e)}")
        
        # Show results
        QMessageBox.information(
            main_window, 
            "Export Complete", 
            f"Exported {exported_count} files successfully.\n{failed_count} files failed.\n\nFiles saved to: {export_dir}"
        )
        
    except Exception as e:
        main_window.log_message(f"❌ Export error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export failed: {str(e)}")


def quick_export_function(main_window):
    """Quick export selected to organized folders by type - Clean version with COL support"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to export.")
            return
        
        # Get base export directory - FIXED: Use current_settings.get()
        try:
            from utils.app_settings_system import AppSettings
            settings = AppSettings()
            base_export_dir = settings.current_settings.get('quick_export_folder', 
                                         os.path.join(os.path.expanduser("~"), "Documents", "IMG_Exports"))
        except:
            base_export_dir = os.path.join(os.path.expanduser("~"), "Documents", "IMG_Exports")
        
        # Create base directory
        os.makedirs(base_export_dir, exist_ok=True)
        
        # Export each file to its type-specific folder
        exported_count = 0
        failed_count = 0
        
        for entry in selected_entries:
            try:
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
                elif file_ext == '.ide':
                    subfolder = 'definitions'
                elif file_ext == '.ipl':
                    subfolder = 'placement'
                elif file_ext in ['.wav', '.mp3']:
                    subfolder = 'audio'
                else:
                    subfolder = 'other'
                
                # Create type directory
                type_dir = os.path.join(base_export_dir, subfolder)
                os.makedirs(type_dir, exist_ok=True)
                
                # Export file
                output_path = os.path.join(type_dir, entry_name)
                
                # Try multiple export methods
                exported = False
                
                # Method 1: Use IMG export_entry if available
                if hasattr(main_window.current_img, 'export_entry'):
                    try:
                        if main_window.current_img.export_entry(entry, output_path):
                            exported = True
                    except:
                        pass
                
                # Method 2: Use entry get_data if available
                if not exported and hasattr(entry, 'get_data'):
                    try:
                        entry_data = entry.get_data()
                        with open(output_path, 'wb') as f:
                            f.write(entry_data)
                        exported = True
                    except:
                        pass
                
                # Method 3: Direct data access
                if not exported and hasattr(entry, 'data'):
                    try:
                        with open(output_path, 'wb') as f:
                            f.write(entry.data)
                        exported = True
                    except:
                        pass
                
                if exported:
                    exported_count += 1
                    main_window.log_message(f"⚡ Quick export: {entry_name} → {subfolder}/")
                else:
                    failed_count += 1
                    main_window.log_message(f"❌ Failed to export: {entry_name}")
                
            except Exception as e:
                failed_count += 1
                entry_name = getattr(entry, 'name', 'unknown')
                main_window.log_message(f"❌ Quick export error for {entry_name}: {str(e)}")
        
        # Show results
        main_window.log_message(f"⚡ Quick export complete: {exported_count} files, {failed_count} failed")
        QMessageBox.information(
            main_window, 
            "Quick Export Complete", 
            f"Exported {exported_count} files to organized folders.\n{failed_count} files failed.\n\nLocation: {base_export_dir}"
        )
        
    except Exception as e:
        main_window.log_message(f"❌ Quick export error: {str(e)}")
        QMessageBox.critical(main_window, "Quick Export Error", f"Quick export failed: {str(e)}")


def remove_selected_function(main_window):
    """Remove selected entries from IMG - Clean version"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to remove.")
            return
        
        # Confirm removal
        entry_names = [getattr(entry, 'name', 'unknown') for entry in selected_entries]
        reply = QMessageBox.question(
            main_window,
            "Confirm Removal",
            f"Are you sure you want to remove {len(selected_entries)} entries?\n\n" + 
            "\n".join(entry_names[:5]) + 
            ("..." if len(entry_names) > 5 else ""),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Remove entries
        removed_count = 0
        for entry in selected_entries:
            try:
                if hasattr(main_window.current_img, 'remove_entry'):
                    if main_window.current_img.remove_entry(entry):
                        removed_count += 1
                        entry_name = getattr(entry, 'name', 'unknown')
                        main_window.log_message(f"🗑️ Removed: {entry_name}")
                
            except Exception as e:
                entry_name = getattr(entry, 'name', 'unknown')
                main_window.log_message(f"❌ Failed to remove {entry_name}: {str(e)}")
        
        # Update table
        if hasattr(main_window, 'populate_entries_table'):
            main_window.populate_entries_table()
        
        # Show results
        QMessageBox.information(
            main_window,
            "Removal Complete",
            f"Removed {removed_count} entries successfully."
        )
        
    except Exception as e:
        main_window.log_message(f"❌ Remove error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Error", f"Remove failed: {str(e)}")

def remove_via_entries_function(main_window):
    """Remove entries using IDE file reference"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        # Get IDE file for removal reference
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE file for removal reference",
            "",
            "IDE Files (*.ide);;All Files (*)"
        )

        if not ide_file:
            return

        main_window.log_message(f"🚮 Remove Via IDE: {ide_file}")

        QMessageBox.information(
            main_window,
            "Remove Via",
            f"Remove Via function called with IDE file:\n{ide_file}\n\nImplementation pending."
        )

    except Exception as e:
        main_window.log_message(f"❌ Remove Via error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Via Error", f"Remove Via failed: {str(e)}")

def dump_all_function(main_window):
    """Dump all entries from IMG - Clean version"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        # Get dump directory
        dump_dir = QFileDialog.getExistingDirectory(main_window, "Dump All Entries To")
        if not dump_dir:
            return
        
        # Confirm dump
        total_entries = len(main_window.current_img.entries) if hasattr(main_window.current_img, 'entries') else 0
        reply = QMessageBox.question(
            main_window,
            "Confirm Dump",
            f"Dump all {total_entries} entries to:\n{dump_dir}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Dump all entries
        dumped_count = 0
        failed_count = 0
        
        for i, entry in enumerate(main_window.current_img.entries):
            try:
                entry_name = getattr(entry, 'name', f'entry_{i}')
                output_path = os.path.join(dump_dir, entry_name)
                
                # Try multiple dump methods
                dumped = False
                
                if hasattr(main_window.current_img, 'export_entry'):
                    try:
                        if main_window.current_img.export_entry(entry, output_path):
                            dumped = True
                    except:
                        pass
                
                if not dumped and hasattr(entry, 'get_data'):
                    try:
                        entry_data = entry.get_data()
                        with open(output_path, 'wb') as f:
                            f.write(entry_data)
                        dumped = True
                    except:
                        pass
                
                if dumped:
                    dumped_count += 1
                    main_window.log_message(f"💾 Dumped: {entry_name}")
                else:
                    failed_count += 1
                    main_window.log_message(f"❌ Failed to dump: {entry_name}")
                
            except Exception as e:
                failed_count += 1
                entry_name = getattr(entry, 'name', f'entry_{i}')
                main_window.log_message(f"❌ Dump error for {entry_name}: {str(e)}")
        
        # Show results
        QMessageBox.information(
            main_window,
            "Dump Complete",
            f"Dumped {dumped_count} files successfully.\n{failed_count} files failed.\n\nLocation: {dump_dir}"
        )
        
    except Exception as e:
        main_window.log_message(f"❌ Dump error: {str(e)}")
        QMessageBox.critical(main_window, "Dump Error", f"Dump failed: {str(e)}")


def import_via_function(main_window):
    """Import via IDE file or folder - Clean version"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        # Choice dialog
        reply = QMessageBox.question(
            main_window,
            "Import Method",
            "Choose import method:\n\nYes = Import via IDE file\nNo = Import entire folder",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            return
        elif reply == QMessageBox.StandardButton.Yes:
            # Import via IDE file
            ide_file, _ = QFileDialog.getOpenFileName(
                main_window, 
                "Select IDE File", 
                "",
                "IDE Files (*.ide);;All Files (*)"
            )
            if ide_file:
                import_from_ide_file(main_window, ide_file)
        else:
            # Import entire folder
            folder = QFileDialog.getExistingDirectory(main_window, "Select Folder to Import")
            if folder:
                import_directory_function(main_window, folder)
                
    except Exception as e:
        main_window.log_message(f"❌ Import via error: {str(e)}")


def import_from_ide_file(main_window, ide_file_path):
    """Import files listed in IDE file"""
    try:
        base_dir = os.path.dirname(ide_file_path)
        imported_count = 0
        failed_count = 0
        
        with open(ide_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse IDE line (name, path, size)
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        file_name = parts[0]
                        file_path = os.path.join(base_dir, parts[1])
                        
                        if os.path.exists(file_path):
                            try:
                                with open(file_path, 'rb') as file_f:
                                    file_data = file_f.read()
                                
                                if main_window.current_img.add_entry(file_name, file_data):
                                    imported_count += 1
                                    main_window.log_message(f"📥 IDE Import: {file_name}")
                                else:
                                    failed_count += 1
                            except:
                                failed_count += 1
                        else:
                            failed_count += 1
                            main_window.log_message(f"❌ File not found: {file_path}")
        
        # Update table
        if hasattr(main_window, 'populate_entries_table'):
            main_window.populate_entries_table()
        
        QMessageBox.information(
            main_window,
            "IDE Import Complete",
            f"Imported {imported_count} files from IDE.\n{failed_count} files failed."
        )
        
    except Exception as e:
        main_window.log_message(f"❌ IDE import error: {str(e)}")


def import_directory_function(main_window, directory):
    """Import all files from directory"""
    try:
        imported_count = 0
        failed_count = 0
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    if main_window.current_img.add_entry(filename, file_data):
                        imported_count += 1
                        main_window.log_message(f"📁 Dir Import: {filename}")
                    else:
                        failed_count += 1
                except:
                    failed_count += 1
        
        # Update table
        if hasattr(main_window, 'populate_entries_table'):
            main_window.populate_entries_table()
        
        QMessageBox.information(
            main_window,
            "Directory Import Complete",
            f"Imported {imported_count} files from directory.\n{failed_count} files failed."
        )
        
    except Exception as e:
        main_window.log_message(f"❌ Directory import error: {str(e)}")


def export_via_function(main_window):
    """Export via existing IDE file"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        # Select IDE file
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE File for Export Matching",
            "",
            "IDE Files (*.ide);;All Files (*)"
        )
        
        if not ide_file:
            return
        
        # Select export directory
        export_dir = QFileDialog.getExistingDirectory(main_window, "Export Matching Files To")
        if not export_dir:
            return
        
        # Parse IDE and export matching files
        exported_count = 0
        failed_count = 0
        
        with open(ide_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('\t')
                    if len(parts) >= 1:
                        file_name = parts[0]
                        
                        # Find matching entry in IMG
                        for entry in main_window.current_img.entries:
                            if getattr(entry, 'name', '') == file_name:
                                try:
                                    output_path = os.path.join(export_dir, file_name)
                                    
                                    if hasattr(entry, 'get_data'):
                                        entry_data = entry.get_data()
                                        with open(output_path, 'wb') as out_f:
                                            out_f.write(entry_data)
                                        exported_count += 1
                                        main_window.log_message(f"📋 IDE Export: {file_name}")
                                    elif hasattr(main_window.current_img, 'export_entry'):
                                        if main_window.current_img.export_entry(entry, output_path):
                                            exported_count += 1
                                            main_window.log_message(f"📋 IDE Export: {file_name}")
                                    else:
                                        failed_count += 1
                                except:
                                    failed_count += 1
                                break
                        else:
                            failed_count += 1
                            main_window.log_message(f"❌ Not found in IMG: {file_name}")
        
        QMessageBox.information(
            main_window,
            "IDE Export Complete",
            f"Exported {exported_count} files matching IDE.\n{failed_count} files failed/not found."
        )
        
    except Exception as e:
        main_window.log_message(f"❌ IDE export error: {str(e)}")


def export_all_function(main_window):
    """Export all entries with dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        # Get export directory
        export_dir = QFileDialog.getExistingDirectory(main_window, "Export All Entries To")
        if not export_dir:
            return
        
        # Confirm export
        total_entries = len(main_window.current_img.entries)
        reply = QMessageBox.question(
            main_window,
            "Confirm Export All",
            f"Export all {total_entries} entries to:\n{export_dir}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Export all entries
        exported_count = 0
        failed_count = 0
        
        for i, entry in enumerate(main_window.current_img.entries):
            try:
                entry_name = getattr(entry, 'name', f'entry_{i}')
                output_path = os.path.join(export_dir, entry_name)
                
                # Try multiple export methods
                exported = False
                
                if hasattr(main_window.current_img, 'export_entry'):
                    try:
                        if main_window.current_img.export_entry(entry, output_path):
                            exported = True
                    except:
                        pass
                
                if not exported and hasattr(entry, 'get_data'):
                    try:
                        entry_data = entry.get_data()
                        with open(output_path, 'wb') as f:
                            f.write(entry_data)
                        exported = True
                    except:
                        pass
                
                if exported:
                    exported_count += 1
                    if exported_count % 50 == 0:  # Progress update every 50 files
                        main_window.log_message(f"📤 Exported {exported_count}/{total_entries} files...")
                else:
                    failed_count += 1
                
            except Exception as e:
                failed_count += 1
                entry_name = getattr(entry, 'name', f'entry_{i}')
                main_window.log_message(f"❌ Export all error for {entry_name}: {str(e)}")
        
        QMessageBox.information(
            main_window,
            "Export All Complete",
            f"Exported {exported_count} files successfully.\n{failed_count} files failed.\n\nLocation: {export_dir}"
        )
        
    except Exception as e:
        main_window.log_message(f"❌ Export all error: {str(e)}")


def add_import_export_menus(main_window):
    """Add import/export menus to main window"""
    try:
        # Find or create File menu
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
        import_files_action.triggered.connect(lambda: import_files_function(main_window))
        import_menu.addAction(import_files_action)
        
        import_via_action = QAction("Import Via...", main_window)
        import_via_action.triggered.connect(lambda: import_via_function(main_window))
        import_menu.addAction(import_via_action)
        
        # Export submenu
        export_menu = file_menu.addMenu("Export")
        
        export_selected_action = QAction("Export Selected...", main_window)
        export_selected_action.setShortcut("Ctrl+E")
        export_selected_action.triggered.connect(lambda: export_selected_function(main_window))
        export_menu.addAction(export_selected_action)
        
        export_via_action = QAction("Export Via IDE...", main_window)
        export_via_action.triggered.connect(lambda: export_via_function(main_window))
        export_menu.addAction(export_via_action)
        
        quick_export_action = QAction("Quick Export", main_window)
        quick_export_action.setShortcut("Ctrl+Shift+E")
        quick_export_action.triggered.connect(lambda: quick_export_function(main_window))
        export_menu.addAction(quick_export_action)
        
        export_all_action = QAction("Export All...", main_window)
        export_all_action.triggered.connect(lambda: export_all_function(main_window))
        export_menu.addAction(export_all_action)
        
        export_menu.addSeparator()
        
        dump_all_action = QAction("Dump All Entries", main_window)
        dump_all_action.triggered.connect(lambda: dump_all_function(main_window))
        export_menu.addAction(dump_all_action)
        
        main_window.log_message("✅ Import/Export menus added")
        
    except Exception as e:
        main_window.log_message(f"❌ Menu creation error: {str(e)}")


def integrate_clean_import_export(main_window):
    """Integrate clean import/export functions to main window"""
    try:
        # Replace existing methods with clean versions
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

        # Add menus
        add_import_export_menus(main_window)

        main_window.log_message("✅ Clean import/export functions integrated")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Integration error: {str(e)}")
        return False

# Export functions for external use
__all__ = [
    'import_files_function',
    'import_via_function',
    'import_from_ide_file',
    'import_directory_function',
    'export_selected_function',
    'export_via_function',
    'export_all_function',
    'quick_export_function',
    'remove_selected_function',
    'remove_via_entries_function',
    'dump_all_function',
    'get_selected_entries',
    'add_import_export_menus',
    'integrate_clean_import_export'
]
