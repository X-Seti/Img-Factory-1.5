#this belongs in components/ col_simple_patch.py - Version: 1
# X-Seti - July08 2025 - Simple patch to fix existing COL integration

"""
Simple patch to fix COL parsing issues in existing system.
This patches the existing col_tab_integration.py functions to work properly.
"""

def patch_existing_col_system():
    """Apply simple fixes to existing COL system"""
    try:
        from components.col_core_classes import COLFile
        
        # Get the original load method
        original_load = COLFile.load
        
        def enhanced_load(self) -> bool:
            """Enhanced load method that ensures models are properly initialized"""
            try:
                # Try original load first
                result = original_load(self)
                
                # If successful, ensure models have proper attributes
                if result and hasattr(self, 'models'):
                    for model in self.models:
                        # Ensure all collision lists exist
                        if not hasattr(model, 'spheres') or model.spheres is None:
                            model.spheres = []
                        if not hasattr(model, 'boxes') or model.boxes is None:
                            model.boxes = []
                        if not hasattr(model, 'vertices') or model.vertices is None:
                            model.vertices = []
                        if not hasattr(model, 'faces') or model.faces is None:
                            model.faces = []
                        if not hasattr(model, 'face_groups') or model.face_groups is None:
                            model.face_groups = []
                        if not hasattr(model, 'shadow_vertices') or model.shadow_vertices is None:
                            model.shadow_vertices = []
                        if not hasattr(model, 'shadow_faces') or model.shadow_faces is None:
                            model.shadow_faces = []
                
                return result
                
            except Exception as e:
                print(f"❌ Enhanced COL load error: {e}")
                return False
        
        # Apply the patch
        COLFile.load = enhanced_load
        
        print("✅ COL system patched successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error patching COL system: {e}")
        return False

def fix_col_tab_integration():
    """Fix the col_tab_integration module"""
    try:
        # Check if col_tab_integration exists
        import components.col_tab_integration as col_tab
        
        # If load_col_file_safely is missing or broken, provide a working version
        if not hasattr(col_tab, 'load_col_file_safely') or col_tab.load_col_file_safely is None:
            
            def load_col_file_safely(main_window, file_path):
                """Working COL file loader"""
                try:
                    from components.col_core_classes import COLFile
                    
                    # Setup tab
                    current_index = main_window.main_tab_widget.currentIndex()
                    
                    if current_index not in main_window.open_files:
                        main_window.log_message("Using current tab for COL file")
                    else:
                        main_window.log_message("Creating new tab for COL file")
                        if hasattr(main_window, 'close_manager'):
                            main_window.close_manager.create_new_tab()
                            current_index = main_window.main_tab_widget.currentIndex()
                    
                    # Setup tab info
                    file_name = os.path.basename(file_path)
                    file_name_clean = file_name[:-4] if file_name.lower().endswith('.col') else file_name
                    tab_name = f"🛡️ {file_name_clean}"
                    
                    if not hasattr(main_window, 'open_files'):
                        main_window.open_files = {}
                    
                    main_window.open_files[current_index] = {
                        'type': 'COL',
                        'file_path': file_path,
                        'file_object': None,
                        'tab_name': tab_name
                    }
                    
                    main_window.main_tab_widget.setTabText(current_index, tab_name)
                    
                    # Load COL file
                    col_file = COLFile(file_path)
                    if col_file.load():
                        main_window.open_files[current_index]['file_object'] = col_file
                        main_window.current_col = col_file
                        
                        # Simple table population
                        if hasattr(main_window, 'main_table'):
                            populate_simple_col_table(main_window, col_file)
                        
                        main_window.log_message(f"✅ COL file loaded: {len(col_file.models)} models")
                        return True
                    else:
                        main_window.log_message("❌ Failed to load COL file")
                        return False
                        
                except Exception as e:
                    main_window.log_message(f"❌ Error loading COL file: {e}")
                    return False
            
            # Add the fixed function
            col_tab.load_col_file_safely = load_col_file_safely
            print("✅ Fixed load_col_file_safely function")
        
        return True
        
    except ImportError:
        print("⚠️ col_tab_integration module not found")
        return False
    except Exception as e:
        print(f"❌ Error fixing col_tab_integration: {e}")
        return False

def populate_simple_col_table(main_window, col_file):
    """Simple table population for COL files"""
    try:
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        
        table = main_window.main_table
        table.setRowCount(0)
        
        if not col_file.models:
            return
        
        # Set headers
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Model Name", "Type", "Elements", "Version"])
        
        # Add rows
        table.setRowCount(len(col_file.models))
        
        for row, model in enumerate(col_file.models):
            # Model name
            name_item = QTableWidgetItem(model.name or f"Model_{row+1}")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem("COL Model")
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 1, type_item)
            
            # Elements count
            spheres = len(model.spheres) if hasattr(model, 'spheres') and model.spheres else 0
            boxes = len(model.boxes) if hasattr(model, 'boxes') and model.boxes else 0
            faces = len(model.faces) if hasattr(model, 'faces') and model.faces else 0
            elements_text = f"S:{spheres} B:{boxes} F:{faces}"
            
            elements_item = QTableWidgetItem(elements_text)
            elements_item.setFlags(elements_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 2, elements_item)
            
            # Version
            version_text = f"COL{model.version.value}" if hasattr(model, 'version') else "COL1"
            version_item = QTableWidgetItem(version_text)
            version_item.setFlags(version_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 3, version_item)
        
        table.resizeColumnsToContents()
        if table.rowCount() > 0:
            table.selectRow(0)
        
        main_window.log_message(f"✅ COL table populated with {len(col_file.models)} models")
        
    except Exception as e:
        main_window.log_message(f"❌ Error populating COL table: {e}")

# Auto-apply patches when imported
print("🔧 Applying COL system patches...")
if patch_existing_col_system():
    print("✅ COL core system patched")
else:
    print("❌ COL core system patch failed")

if fix_col_tab_integration():
    print("✅ COL tab integration fixed")
else:
    print("❌ COL tab integration fix failed")

print("🎯 COL patches applied")