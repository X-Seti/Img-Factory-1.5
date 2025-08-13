#this belongs in visibility_fix.py - Version: 1
# X-Seti - August01 2025 - IMG Factory 1.5 - VISIBILITY FIX PATCH

"""
VISIBILITY FIX - Based on debug analysis
Fixes the specific GUI visibility issue where all components exist but are hidden
"""

def fix_gui_visibility_issue(main_window): #vers 1
    """Fix the specific GUI visibility issue identified by debug"""
    try:
        print("🔧 FIXING: GUI visibility issue...")
        
        # Force main splitter visibility
        if hasattr(main_window.gui_layout, 'main_splitter'):
            splitter = main_window.gui_layout.main_splitter
            splitter.setVisible(True)
            splitter.show()
            print("✅ FIXED: Main splitter visible")
        
        # Force left vertical splitter visibility  
        if hasattr(main_window.gui_layout, 'left_vertical_splitter'):
            v_splitter = main_window.gui_layout.left_vertical_splitter
            v_splitter.setVisible(True)
            v_splitter.show()
            print("✅ FIXED: Left vertical splitter visible")
        
        # Force tab widget visibility (CRITICAL - this was hidden)
        if hasattr(main_window.gui_layout, 'tab_widget'):
            tab_widget = main_window.gui_layout.tab_widget
            tab_widget.setVisible(True)
            tab_widget.show()
            
            # Make sure current tab is visible
            current_tab = tab_widget.currentWidget()
            if current_tab:
                current_tab.setVisible(True)
                current_tab.show()
            
            print("✅ FIXED: Tab widget and current tab visible")
        
        # Force table visibility
        if hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            table.setVisible(True)
            table.show()
            
            # Force all table parents to be visible
            parent = table.parent()
            level = 0
            while parent and level < 5:
                parent.setVisible(True)
                parent.show()
                parent = parent.parent()
                level += 1
            
            print("✅ FIXED: Table and all parents visible")
        
        # Force log widget visibility
        if hasattr(main_window.gui_layout, 'log'):
            log = main_window.gui_layout.log
            log.setVisible(True)
            log.show()
            print("✅ FIXED: Log widget visible")
        
        # Force central widget visibility
        central_widget = main_window.centralWidget()
        if central_widget:
            central_widget.setVisible(True)
            central_widget.show()
            print("✅ FIXED: Central widget visible")
        
        # Force main window visibility
        main_window.setVisible(True)
        main_window.show()
        
        # Force repaint everything
        main_window.repaint()
        if hasattr(main_window.gui_layout, 'main_splitter'):
            main_window.gui_layout.main_splitter.repaint()
        
        print("✅ FIXED: All GUI components forced visible")
        return True
        
    except Exception as e:
        print(f"❌ VISIBILITY FIX ERROR: {str(e)}")
        return False

def patch_update_ui_for_loaded_img(main_window): #vers 1
    """Patch _update_ui_for_loaded_img to include visibility fix"""
    try:
        # Store original method
        if hasattr(main_window, '_update_ui_for_loaded_img_original'):
            return True  # Already patched
        
        if hasattr(main_window, '_update_ui_for_loaded_img'):
            main_window._update_ui_for_loaded_img_original = main_window._update_ui_for_loaded_img
        else:
            print("❌ _update_ui_for_loaded_img method not found!")
            return False
        
        def fixed_update_ui_for_loaded_img():
            """Fixed version with visibility enforcement"""
            try:
                # Call original method
                result = main_window._update_ui_for_loaded_img_original()
                
                # Force GUI visibility after UI update
                fix_gui_visibility_issue(main_window)
                
                return result
            except Exception as e:
                print(f"❌ Error in fixed _update_ui_for_loaded_img: {e}")
                # Still try to fix visibility even if original method fails
                fix_gui_visibility_issue(main_window)
        
        # Replace method
        main_window._update_ui_for_loaded_img = fixed_update_ui_for_loaded_img
        print("✅ PATCHED: _update_ui_for_loaded_img with visibility fix")
        return True
        
    except Exception as e:
        print(f"❌ Failed to patch _update_ui_for_loaded_img: {e}")
        return False

def patch_on_img_loaded_with_visibility_fix(main_window): #vers 1
    """Patch _on_img_loaded to include visibility fix"""
    try:
        # Store original method
        if hasattr(main_window, '_on_img_loaded_visibility_original'):
            return True  # Already patched
        
        if hasattr(main_window, '_on_img_loaded'):
            main_window._on_img_loaded_visibility_original = main_window._on_img_loaded
        else:
            print("❌ _on_img_loaded method not found!")
            return False
        
        def fixed_on_img_loaded(img_file):
            """Fixed version with visibility enforcement"""
            try:
                # Call original method
                main_window._on_img_loaded_visibility_original(img_file)
                
                # CRITICAL: Force GUI visibility after loading
                fix_gui_visibility_issue(main_window)
                
            except Exception as e:
                print(f"❌ Error in fixed _on_img_loaded: {e}")
                # Still try to fix visibility even if original method fails
                fix_gui_visibility_issue(main_window)
        
        # Replace method
        main_window._on_img_loaded = fixed_on_img_loaded
        print("✅ PATCHED: _on_img_loaded with visibility fix")
        return True
        
    except Exception as e:
        print(f"❌ Failed to patch _on_img_loaded: {e}")
        return False

def apply_visibility_fix(main_window): #vers 1
    """Apply all visibility fixes"""
    try:
        print("🔧 APPLYING: Visibility fixes...")
        
        # Apply patches
        patch_update_ui_for_loaded_img(main_window)
        patch_on_img_loaded_with_visibility_fix(main_window)
        
        # Add manual fix method
        main_window.fix_gui_visibility = lambda: fix_gui_visibility_issue(main_window)
        
        # Fix visibility immediately if something is already loaded
        if hasattr(main_window, 'current_img') and main_window.current_img:
            fix_gui_visibility_issue(main_window)
        
        print("✅ APPLIED: All visibility fixes")
        main_window.log_message("🔧 Visibility fixes applied - GUI should now be visible")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply visibility fixes: {e}")
        return False

def remove_visibility_fix(main_window): #vers 1
    """Remove visibility fix patches"""
    try:
        print("🔧 REMOVING: Visibility fixes...")
        
        # Restore original methods
        if hasattr(main_window, '_update_ui_for_loaded_img_original'):
            main_window._update_ui_for_loaded_img = main_window._update_ui_for_loaded_img_original
            delattr(main_window, '_update_ui_for_loaded_img_original')
        
        if hasattr(main_window, '_on_img_loaded_visibility_original'):
            main_window._on_img_loaded = main_window._on_img_loaded_visibility_original
            delattr(main_window, '_on_img_loaded_visibility_original')
        
        # Remove manual fix method
        if hasattr(main_window, 'fix_gui_visibility'):
            delattr(main_window, 'fix_gui_visibility')
        
        print("✅ REMOVED: All visibility fixes")
        return True
        
    except Exception as e:
        print(f"❌ Failed to remove visibility fixes: {e}")
        return False

__all__ = [
    'apply_visibility_fix',
    'remove_visibility_fix',
    'fix_gui_visibility_issue'
]