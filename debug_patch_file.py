#this belongs in debug_patch.py - Version: 1
# X-Seti - August01 2025 - IMG Factory 1.5 - DEBUG PATCH (ONE TIME ONLY)
# EMERGENCY DEBUG: Create new tab, loading IMG, and updating file window

"""
DEBUG PATCH - ONE TIME ONLY
Debugs and fixes:
1. Create new tab issues
2. IMG loading problems  
3. File window update failures
4. Blank window after loading

DO NOT INTEGRATE - APPLY AS PATCH ONLY
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout

##Methods list -
# debug_create_new_tab
# debug_img_loading_process
# debug_file_window_update
# debug_gui_visibility
# apply_debug_patches
# remove_debug_patches

def debug_create_new_tab(main_window): #vers 1
    """Debug create new tab functionality"""
    try:
        print("🔍 DEBUG: Starting create new tab analysis...")
        
        # Check if main_tab_widget exists
        if not hasattr(main_window, 'main_tab_widget'):
            print("❌ DEBUG: main_tab_widget does not exist!")
            return False
        
        tab_widget = main_window.main_tab_widget
        print(f"🔍 DEBUG: Tab widget found, current tabs: {tab_widget.count()}")
        
        # Check current files tracking
        if hasattr(main_window, 'open_files'):
            print(f"🔍 DEBUG: Open files tracking: {list(main_window.open_files.keys())}")
        else:
            print("❌ DEBUG: open_files tracking missing!")
        
        # Test tab creation
        current_index = tab_widget.currentIndex()
        print(f"🔍 DEBUG: Current tab index: {current_index}")
        
        # Check if current tab is empty
        if current_index not in main_window.open_files:
            print("✅ DEBUG: Current tab is empty, can use it")
            return True
        else:
            print("🔍 DEBUG: Current tab has file, need new tab")
            
            # Test new tab creation
            if hasattr(main_window, 'close_manager'):
                print("✅ DEBUG: close_manager exists")
                if hasattr(main_window.close_manager, 'create_new_tab'):
                    print("✅ DEBUG: create_new_tab method exists")
                    return True
                else:
                    print("❌ DEBUG: create_new_tab method missing!")
                    return False
            else:
                print("❌ DEBUG: close_manager missing!")
                return False
        
    except Exception as e:
        print(f"❌ DEBUG: Tab creation error: {str(e)}")
        return False

def debug_img_loading_process(main_window, img_file): #vers 1
    """Debug IMG loading process step by step"""
    try:
        print("🔍 DEBUG: Starting IMG loading analysis...")
        
        # Check IMG file object
        if not img_file:
            print("❌ DEBUG: IMG file object is None!")
            return False
        
        print(f"✅ DEBUG: IMG file object exists: {type(img_file)}")
        
        if hasattr(img_file, 'file_path'):
            print(f"✅ DEBUG: File path: {img_file.file_path}")
        else:
            print("❌ DEBUG: IMG file has no file_path!")
        
        if hasattr(img_file, 'entries'):
            print(f"✅ DEBUG: IMG entries: {len(img_file.entries) if img_file.entries else 0}")
        else:
            print("❌ DEBUG: IMG file has no entries!")
        
        # Check current IMG assignment
        if hasattr(main_window, 'current_img'):
            print(f"✅ DEBUG: main_window.current_img exists: {main_window.current_img is not None}")
        else:
            print("❌ DEBUG: main_window.current_img does not exist!")
        
        # Check open files tracking
        if hasattr(main_window, 'open_files'):
            current_index = main_window.main_tab_widget.currentIndex()
            if current_index in main_window.open_files:
                file_info = main_window.open_files[current_index]
                print(f"✅ DEBUG: Tab {current_index} file info: {file_info}")
            else:
                print(f"❌ DEBUG: Tab {current_index} not in open_files!")
        
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: IMG loading analysis error: {str(e)}")
        return False

def debug_file_window_update(main_window): #vers 1
    """Debug file window update process"""
    try:
        print("🔍 DEBUG: Starting file window analysis...")
        
        # Check GUI layout
        if not hasattr(main_window, 'gui_layout'):
            print("❌ DEBUG: gui_layout does not exist!")
            return False
        
        print("✅ DEBUG: gui_layout exists")
        
        # Check table widget
        if not hasattr(main_window.gui_layout, 'table'):
            print("❌ DEBUG: gui_layout.table does not exist!")
            return False
        
        table = main_window.gui_layout.table
        print(f"✅ DEBUG: Table exists: {type(table)}")
        print(f"🔍 DEBUG: Table visible: {table.isVisible()}")
        print(f"🔍 DEBUG: Table size: {table.size().width()}x{table.size().height()}")
        print(f"🔍 DEBUG: Table row count: {table.rowCount()}")
        print(f"🔍 DEBUG: Table column count: {table.columnCount()}")
        
        # Check table parent hierarchy
        parent = table.parent()
        level = 0
        while parent and level < 5:
            print(f"🔍 DEBUG: Table parent {level}: {type(parent)} visible: {parent.isVisible()}")
            parent = parent.parent()
            level += 1
        
        # Check main splitter
        if hasattr(main_window.gui_layout, 'main_splitter'):
            splitter = main_window.gui_layout.main_splitter
            print(f"✅ DEBUG: Main splitter exists, visible: {splitter.isVisible()}")
            print(f"🔍 DEBUG: Splitter sizes: {splitter.sizes()}")
            print(f"🔍 DEBUG: Splitter widget count: {splitter.count()}")
        else:
            print("❌ DEBUG: main_splitter does not exist!")
        
        # Check left vertical splitter
        if hasattr(main_window.gui_layout, 'left_vertical_splitter'):
            v_splitter = main_window.gui_layout.left_vertical_splitter
            print(f"✅ DEBUG: Left vertical splitter exists, visible: {v_splitter.isVisible()}")
            print(f"🔍 DEBUG: Vertical splitter sizes: {v_splitter.sizes()}")
        else:
            print("❌ DEBUG: left_vertical_splitter does not exist!")
        
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: File window analysis error: {str(e)}")
        return False

def debug_gui_visibility(main_window): #vers 1
    """Debug GUI component visibility issues"""
    try:
        print("🔍 DEBUG: Starting GUI visibility analysis...")
        
        # Check progress bar
        if hasattr(main_window.gui_layout, 'progress_bar'):
            progress = main_window.gui_layout.progress_bar
            print(f"🔍 DEBUG: Progress bar visible: {progress.isVisible()}")
            print(f"🔍 DEBUG: Progress bar value: {progress.value()}")
        else:
            print("❌ DEBUG: progress_bar does not exist!")
        
        # Check tab widget
        if hasattr(main_window.gui_layout, 'tab_widget'):
            tab_widget = main_window.gui_layout.tab_widget
            print(f"🔍 DEBUG: Tab widget visible: {tab_widget.isVisible()}")
            print(f"🔍 DEBUG: Tab widget size: {tab_widget.size().width()}x{tab_widget.size().height()}")
            print(f"🔍 DEBUG: Tab widget tab count: {tab_widget.count()}")
        else:
            print("❌ DEBUG: tab_widget does not exist!")
        
        # Check log widget
        if hasattr(main_window.gui_layout, 'log'):
            log = main_window.gui_layout.log
            print(f"🔍 DEBUG: Log widget visible: {log.isVisible()}")
        else:
            print("❌ DEBUG: log widget does not exist!")
        
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: GUI visibility analysis error: {str(e)}")
        return False

def debug_populate_img_table_method(main_window): #vers 1
    """Debug the populate_img_table method"""
    try:
        print("🔍 DEBUG: Testing populate_img_table method...")
        
        # Check if method exists
        try:
            from methods.populate_img_table import populate_img_table
            print("✅ DEBUG: populate_img_table import successful")
        except ImportError as e:
            print(f"❌ DEBUG: populate_img_table import failed: {e}")
            return False
        
        # Check if current_img exists and has entries
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            print("❌ DEBUG: No current_img to test with")
            return False
        
        if not hasattr(main_window.current_img, 'entries') or not main_window.current_img.entries:
            print("❌ DEBUG: current_img has no entries to populate")
            return False
        
        print(f"✅ DEBUG: current_img has {len(main_window.current_img.entries)} entries")
        
        # Test table population
        table = main_window.gui_layout.table
        original_row_count = table.rowCount()
        print(f"🔍 DEBUG: Table original row count: {original_row_count}")
        
        # Test the actual population
        try:
            populate_img_table(table, main_window.current_img)
            new_row_count = table.rowCount()
            print(f"✅ DEBUG: Table population successful, new row count: {new_row_count}")
            return True
        except Exception as e:
            print(f"❌ DEBUG: Table population failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ DEBUG: populate_img_table test error: {str(e)}")
        return False

def patch_on_img_loaded_with_debug(main_window): #vers 1
    """Patch the _on_img_loaded method with debug output"""
    try:
        # Store original method if it exists
        if hasattr(main_window, '_on_img_loaded_original'):
            print("🔍 DEBUG: Patch already applied")
            return True
        
        if hasattr(main_window, '_on_img_loaded'):
            main_window._on_img_loaded_original = main_window._on_img_loaded
        else:
            print("❌ DEBUG: _on_img_loaded method does not exist!")
            return False
        
        def debug_on_img_loaded(img_file):
            """Debug version of _on_img_loaded"""
            print("🔍 DEBUG: === _on_img_loaded called ===")
            
            # Debug the IMG loading process
            debug_img_loading_process(main_window, img_file)
            
            try:
                # Store the loaded IMG file in tab system
                current_index = main_window.main_tab_widget.currentIndex()
                print(f"🔍 DEBUG: Current tab index: {current_index}")
                
                if current_index in main_window.open_files:
                    main_window.open_files[current_index]['file_object'] = img_file
                    print("✅ DEBUG: IMG file stored in tab system")
                else:
                    print("❌ DEBUG: Current tab index not in open_files!")
                
                # Set current IMG reference
                main_window.current_img = img_file
                print("✅ DEBUG: current_img set")
                
                # Debug file window before update
                print("🔍 DEBUG: === BEFORE file window update ===")
                debug_file_window_update(main_window)
                
                # Test table clearing
                if hasattr(main_window.gui_layout, 'table'):
                    table = main_window.gui_layout.table
                    original_rows = table.rowCount()
                    table.setRowCount(0)
                    print(f"🔍 DEBUG: Table cleared from {original_rows} to {table.rowCount()} rows")
                
                # Update UI using original method or fallback
                if hasattr(main_window, '_update_ui_for_loaded_img'):
                    print("🔍 DEBUG: Calling _update_ui_for_loaded_img...")
                    main_window._update_ui_for_loaded_img()
                    print("✅ DEBUG: _update_ui_for_loaded_img completed")
                else:
                    print("❌ DEBUG: _update_ui_for_loaded_img method missing!")
                
                # Debug file window after update
                print("🔍 DEBUG: === AFTER file window update ===")
                debug_file_window_update(main_window)
                
                # Debug GUI visibility
                debug_gui_visibility(main_window)
                
                # Test table population directly
                debug_populate_img_table_method(main_window)
                
                # Hide progress - with debug
                if hasattr(main_window.gui_layout, 'hide_progress'):
                    print("🔍 DEBUG: Calling hide_progress...")
                    main_window.gui_layout.hide_progress()
                else:
                    print("❌ DEBUG: hide_progress method not available")
                
                # Force GUI visibility
                print("🔍 DEBUG: Forcing GUI component visibility...")
                if hasattr(main_window.gui_layout, 'table'):
                    main_window.gui_layout.table.setVisible(True)
                    main_window.gui_layout.table.show()
                    print("✅ DEBUG: Table forced visible")
                
                if hasattr(main_window.gui_layout, 'main_splitter'):
                    main_window.gui_layout.main_splitter.setVisible(True)
                    main_window.gui_layout.main_splitter.show()
                    print("✅ DEBUG: Main splitter forced visible")
                
                # Log success
                main_window.log_message(f"✅ DEBUG: Loaded: {os.path.basename(img_file.file_path)} ({len(img_file.entries)} entries)")
                print(f"✅ DEBUG: === _on_img_loaded completed successfully ===")
                
            except Exception as e:
                error_msg = f"Error in debug _on_img_loaded: {str(e)}"
                print(f"❌ DEBUG: {error_msg}")
                main_window.log_message(f"❌ DEBUG: {error_msg}")
        
        # Replace the method
        main_window._on_img_loaded = debug_on_img_loaded
        print("✅ DEBUG: _on_img_loaded method patched with debug version")
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Failed to patch _on_img_loaded: {str(e)}")
        return False

def apply_debug_patches(main_window): #vers 1
    """Apply all debug patches to main window"""
    try:
        print("🔍 DEBUG: === APPLYING DEBUG PATCHES ===")
        
        # Run initial diagnostics
        print("🔍 DEBUG: Running initial diagnostics...")
        debug_create_new_tab(main_window)
        debug_file_window_update(main_window)
        debug_gui_visibility(main_window)
        
        # Apply patches
        patch_on_img_loaded_with_debug(main_window)
        
        # Add debug methods to main window
        main_window.debug_create_new_tab = lambda: debug_create_new_tab(main_window)
        main_window.debug_img_loading = lambda img: debug_img_loading_process(main_window, img)
        main_window.debug_file_window = lambda: debug_file_window_update(main_window)
        main_window.debug_gui_visibility = lambda: debug_gui_visibility(main_window)
        
        print("✅ DEBUG: All debug patches applied successfully")
        main_window.log_message("🔍 DEBUG: Debug patches applied - use debug_* methods for analysis")
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Failed to apply debug patches: {str(e)}")
        return False

def remove_debug_patches(main_window): #vers 1
    """Remove debug patches and restore original methods"""
    try:
        print("🔍 DEBUG: === REMOVING DEBUG PATCHES ===")
        
        # Restore original _on_img_loaded method
        if hasattr(main_window, '_on_img_loaded_original'):
            main_window._on_img_loaded = main_window._on_img_loaded_original
            delattr(main_window, '_on_img_loaded_original')
            print("✅ DEBUG: Original _on_img_loaded method restored")
        
        # Remove debug methods
        debug_methods = ['debug_create_new_tab', 'debug_img_loading', 'debug_file_window', 'debug_gui_visibility']
        for method_name in debug_methods:
            if hasattr(main_window, method_name):
                delattr(main_window, method_name)
                print(f"✅ DEBUG: Removed {method_name}")
        
        print("✅ DEBUG: All debug patches removed")
        main_window.log_message("🔍 DEBUG: Debug patches removed, original functionality restored")
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Failed to remove debug patches: {str(e)}")
        return False

# Integration functions
def integrate_debug_patch(main_window): #vers 1
    """Integrate debug patch into main window - CALL THIS ONCE"""
    return apply_debug_patches(main_window)

def remove_debug_patch(main_window): #vers 1
    """Remove debug patch from main window - CALL THIS TO CLEAN UP"""
    return remove_debug_patches(main_window)

__all__ = [
    'integrate_debug_patch',
    'remove_debug_patch',
    'apply_debug_patches',
    'remove_debug_patches'
]