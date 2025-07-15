def remove_selected_function(main_window):
    """Remove selected entries from IMG"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        # Get selected entries using the utility function
        from core.utils import get_selected_entries
        selected_entries = get_selected_entries(main_window)
        
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to remove.")
            return
        
        main_window.log_message(f"📋 Found {len(selected_entries)} selected entries for removal")
        
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
        
        # Remove entries from IMG
        removed_count = 0
        for entry in selected_entries:
            try:
                entry_name = getattr(entry, 'name', 'unknown')
                
                # Method 1: Use IMG's remove_entry method
                if hasattr(main_window.current_img, 'remove_entry'):
                    try:
                        if main_window.current_img.remove_entry(entry):
                            removed_count += 1
                            main_window.log_message(f"🗑️ Removed: {entry_name}")
                            continue
                    except Exception as e:
                        main_window.log_message(f"⚠️ Method 1 failed for {entry_name}: {str(e)}")
                
                # Method 2: Remove from entries list directly
                if hasattr(main_window.current_img, 'entries'):
                    try:
                        if entry in main_window.current_img.entries:
                            main_window.current_img.entries.remove(entry)
                            removed_count += 1
                            main_window.log_message(f"🗑️ Removed: {entry_name}")
                            continue
                    except Exception as e:
                        main_window.log_message(f"⚠️ Method 2 failed for {entry_name}: {str(e)}")
                
                # Method 3: Remove by name match
                if hasattr(main_window.current_img, 'entries'):
                    try:
                        original_count = len(main_window.current_img.entries)
                        main_window.current_img.entries = [
                            e for e in main_window.current_img.entries 
                            if getattr(e, 'name', '').lower() != entry_name.lower()
                        ]
                        if len(main_window.current_img.entries) < original_count:
                            removed_count += 1
                            main_window.log_message(f"🗑️ Removed: {entry_name}")
                            continue
                    except Exception as e:
                        main_window.log_message(f"⚠️ Method 3 failed for {entry_name}: {str(e)}")
                
                # If we get here, removal failed
                main_window.log_message(f"❌ Failed to remove: {entry_name}")
                
            except Exception as e:
                entry_name = getattr(entry, 'name', 'unknown')
                main_window.log_message(f"❌ Error removing {entry_name}: {str(e)}")
        
        # Update table display
        try:
            if hasattr(main_window, 'populate_entries_table'):
                main_window.populate_entries_table()
            elif hasattr(main_window, '_update_ui_for_loaded_img'):
                main_window._update_ui_for_loaded_img()
            elif hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
        except Exception as e:
            main_window.log_message(f"⚠️ Table refresh failed: {str(e)}")
        
        # Show results
        main_window.log_message(f"✅ Removal complete: {removed_count}/{len(selected_entries)} entries removed")
        
        QMessageBox.information(
            main_window,
            "Removal Complete",
            f"Successfully removed {removed_count} out of {len(selected_entries)} entries."
        )
        
    except Exception as e:
        main_window.log_message(f"❌ Remove error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Error", f"Remove failed: {str(e)}")


def integrate_remove_functions(main_window):
    """Integrate remove functions into main window"""
    try:
        main_window.remove_selected_function = lambda: remove_selected_function(main_window)
        main_window.remove_via_entries_function = lambda: remove_via_entries_function(main_window)
        
        # Add aliases for different naming conventions
        main_window.remove_selected = main_window.remove_selected_function
        main_window.remove_via_entries = main_window.remove_via_entries_function
        
        main_window.log_message("✅ Remove functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate remove functions: {str(e)}")
        return False