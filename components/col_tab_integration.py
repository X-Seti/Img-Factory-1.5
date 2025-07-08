#this belongs in components/ col_tab_integration.py - Version: 8
# X-Seti - July08 2025 - COL Tab Integration for IMG Factory 1.5

import os
import struct
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt, QTimer

def setup_col_integration_safe(main_window):
    """Setup COL integration safely after GUI is ready"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window, 'log_message'):
            print("GUI not ready for COL integration - will retry later")
            return False
        
        main_window.log_message("🔧 Starting COL integration setup...")
        
        # Apply COL parsing improvements
        main_window.log_message("🔧 Applying COL parsing patch...")
        patch_success = apply_col_parsing_patch()
        if patch_success:
            main_window.log_message("✅ COL parsing patch applied successfully")
        else:
            main_window.log_message("❌ COL parsing patch FAILED")
        
        # Add COL methods to main window
        add_col_methods_to_main_window(main_window)
        
        main_window.log_message("✅ COL integration setup complete")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL integration error: {str(e)}")
        else:
            print(f"COL integration error: {str(e)}")
        return False

def apply_col_parsing_patch():
    """Apply improved COL parsing"""
    try:
        print("🔧 Attempting to import col_core_classes...")
        from components import col_core_classes
        print("✅ col_core_classes imported successfully")
        
        print("🔧 Checking COLFile class...")
        if hasattr(col_core_classes, 'COLFile'):
            print("✅ COLFile class found")
        else:
            print("❌ COLFile class NOT found")
            return False
            
        print("🔧 Checking _parse_col1_model method...")
        if hasattr(col_core_classes.COLFile, '_parse_col1_model'):
            print("✅ _parse_col1_model method found")
        else:
            print("❌ _parse_col1_model method NOT found")
            return False
        
        # Store original method to check if patch is applied
        original_parse_col1 = col_core_classes.COLFile._parse_col1_model
        
        def improved_parse_col1_model(self, model, data):
            """Improved COL1 parsing that actually reads collision data"""
            try:
                print(f"🔧 PATCH ACTIVE: Parsing model with {len(data)} bytes")
                offset = 0
                
                # Read name (22 bytes)
                if len(data) < 22:
                    print("❌ Data too short for name")
                    return
                
                name_bytes = data[offset:offset+22]
                model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
                offset += 22
                print(f"🔧 PATCH: Model name: '{model.name}'")
                
                # Read model ID (4 bytes)
                if offset + 4 > len(data):
                    print("❌ Data too short for model ID")
                    return
                
                model.model_id = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                print(f"🔧 PATCH: Model ID: {model.model_id}")
                
                # Calculate remaining collision data
                remaining_size = len(data) - offset
                print(f"🔧 PATCH: {remaining_size} bytes of collision data to parse")
                
                # Initialize collision data lists - FORCE CLEAR FIRST
                model.spheres = []
                model.boxes = []
                model.vertices = []
                model.faces = []
                print(f"🔧 PATCH: Cleared collision lists")
                
                if remaining_size >= 16:
                    # Read bounding sphere
                    center_x, center_y, center_z, radius = struct.unpack('<ffff', data[offset:offset+16])
                    offset += 16
                    print(f"🔧 PATCH: Bounding sphere: center=({center_x:.2f}, {center_y:.2f}, {center_z:.2f}) radius={radius:.2f}")
                    
                    if remaining_size >= 32:
                        # Read counts
                        num_spheres, num_boxes, num_vertices, num_faces = struct.unpack('<IIII', data[offset:offset+16])
                        offset += 16
                        print(f"🔧 PATCH: Declared counts: S:{num_spheres} B:{num_boxes} V:{num_vertices} F:{num_faces}")
                        
                        # Safety limits
                        num_spheres = min(num_spheres, 50)
                        num_boxes = min(num_boxes, 50)
                        num_vertices = min(num_vertices, 500)
                        num_faces = min(num_faces, 500)
                        print(f"🔧 PATCH: Safe counts: S:{num_spheres} B:{num_boxes} V:{num_vertices} F:{num_faces}")
                        
                        # Parse spheres (20 bytes each)
                        spheres_parsed = 0
                        for i in range(num_spheres):
                            if offset + 20 <= len(data):
                                sx, sy, sz, sr, material = struct.unpack('<ffffI', data[offset:offset+20])
                            try:
                                # Safe material creation
                                safe_material = col_core_classes.COLMaterial.DEFAULT
                                try:
                                    safe_material = col_core_classes.COLMaterial(material & 0xFF)
                                except (ValueError, TypeError):
                                    safe_material = col_core_classes.COLMaterial.DEFAULT
                                
                                sphere = col_core_classes.COLSphere(
                                    col_core_classes.Vector3(sx, sy, sz),
                                    sr,
                                    safe_material
                                )
                                model.spheres.append(sphere)
                                spheres_parsed += 1
                                offset += 20
                                if i == 0:  # Log first sphere
                                    print(f"🔧 PATCH: First sphere: center=({sx:.2f}, {sy:.2f}, {sz:.2f}) radius={sr:.2f} material={material}")
                            except Exception as sphere_error:
                                print(f"⚠️ PATCH: Error creating sphere {i}: {sphere_error}")
                                offset += 20  # Skip this sphere but continue
                        
                        print(f"🔧 PATCH: Parsed {spheres_parsed} spheres, model.spheres now has {len(model.spheres)} items")
                        
                        # Parse boxes (32 bytes each)
                        boxes_parsed = 0
                        for i in range(num_boxes):
                            if offset + 32 <= len(data):
                                try:
                                    min_x, min_y, min_z, max_x, max_y, max_z, material, flags = struct.unpack('<ffffffII', data[offset:offset+32])
                                    
                                    safe_material = col_core_classes.COLMaterial.DEFAULT
                                    try:
                                        safe_material = col_core_classes.COLMaterial(material & 0xFF)
                                    except (ValueError, TypeError):
                                        safe_material = col_core_classes.COLMaterial.DEFAULT
                                    
                                    box = col_core_classes.COLBox(
                                        col_core_classes.Vector3(min_x, min_y, min_z),
                                        col_core_classes.Vector3(max_x, max_y, max_z),
                                        safe_material
                                    )
                                    model.boxes.append(box)
                                    boxes_parsed += 1
                                    offset += 32
                                except Exception as box_error:
                                    print(f"⚠️ PATCH: Error creating box {i}: {box_error}")
                                    offset += 32
                        
                        print(f"🔧 PATCH: Parsed {boxes_parsed} boxes, model.boxes now has {len(model.boxes)} items")
                        
                        # Parse vertices (12 bytes each)
                        vertices_parsed = 0
                        for i in range(num_vertices):
                            if offset + 12 <= len(data):
                                vx, vy, vz = struct.unpack('<fff', data[offset:offset+12])
                                vertex = col_core_classes.COLVertex(
                                    col_core_classes.Vector3(vx, vy, vz)
                                )
                                model.vertices.append(vertex)
                                vertices_parsed += 1
                                offset += 12
                        
                        print(f"🔧 PATCH: Parsed {vertices_parsed} vertices, model.vertices now has {len(model.vertices)} items")
                        
                        # Parse faces (12 bytes each)
                        faces_parsed = 0
                        for i in range(num_faces):
                            if offset + 12 <= len(data):
                                va, vb, vc, material = struct.unpack('<HHHHI', data[offset:offset+12])
                                face = col_core_classes.COLFace(
                                    va, vb, vc,
                                    col_core_classes.COLMaterial(material & 0xFF),
                                    0
                                )
                                model.faces.append(face)
                                faces_parsed += 1
                                offset += 12
                        
                        print(f"🔧 PATCH: Parsed {faces_parsed} faces, model.faces now has {len(model.faces)} items")
                
                # Set bounding box
                if 'center_x' in locals():
                    center = col_core_classes.Vector3(center_x, center_y, center_z)
                    model.bounding_box = col_core_classes.BoundingBox(center, center, center, radius)
                else:
                    model.calculate_bounding_box()
                
                model.update_flags()
                
                # VERIFY collision data is still there right after parsing
                final_spheres = len(model.spheres)
                final_boxes = len(model.boxes) 
                final_vertices = len(model.vertices)
                final_faces = len(model.faces)
                
                print(f"✅ PATCH COMPLETE: '{model.name}' S:{final_spheres} B:{final_boxes} V:{final_vertices} F:{final_faces}")
                
                # Double-check the lists aren't getting cleared
                if final_spheres > 0:
                    print(f"🔧 VERIFICATION: model.spheres list still has {len(model.spheres)} items")
                    print(f"🔧 VERIFICATION: First sphere object: {model.spheres[0]}")
                else:
                    print(f"⚠️ VERIFICATION: model.spheres is empty after parsing!")
                
            except Exception as e:
                print(f"❌ PATCH ERROR parsing COL1 model: {e}")
                print(f"❌ Exception details: {type(e).__name__}: {str(e)}")
                # Don't clear on error - keep whatever we managed to parse
                if not hasattr(model, 'spheres'):
                    model.spheres = []
                if not hasattr(model, 'boxes'): 
                    model.boxes = []
                if not hasattr(model, 'vertices'):
                    model.vertices = []
                if not hasattr(model, 'faces'):
                    model.faces = []
        
        # Apply the patch
        col_core_classes.COLFile._parse_col1_model = improved_parse_col1_model
        print("✅ COL parsing patch applied successfully")
        
        # Verify patch was applied
        if col_core_classes.COLFile._parse_col1_model == improved_parse_col1_model:
            print("✅ PATCH VERIFICATION: Method replacement confirmed")
        else:
            print("❌ PATCH VERIFICATION: Method replacement FAILED")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying COL parsing patch: {e}")
        return False

def load_col_file_safely(main_window, file_path):
    """Load COL file safely"""
    try:
        main_window.log_message(f"🔧 Setting up COL tab for: {os.path.basename(file_path)}")
        
        # Check if current tab is empty
        current_index = main_window.main_tab_widget.currentIndex()
        
        if current_index not in main_window.open_files:
            main_window.log_message(f"Using current empty tab for COL file")
        else:
            main_window.log_message(f"Creating new tab for COL file")
            main_window.close_manager.create_new_tab()
            current_index = main_window.main_tab_widget.currentIndex()
        
        # Setup tab info
        file_name = os.path.basename(file_path)
        file_name_clean = file_name[:-4] if file_name.lower().endswith('.col') else file_name
        tab_name = f"🛡️ {file_name_clean}"

        main_window.open_files[current_index] = {
            'type': 'COL',
            'file_path': file_path,
            'file_object': None,
            'tab_name': tab_name
        }

        # Update tab name
        main_window.main_tab_widget.setTabText(current_index, tab_name)

        # Load COL file
        success = load_col_file_content(main_window, file_path)
        
        if not success:
            # Clean up on failure
            if current_index in main_window.open_files:
                del main_window.open_files[current_index]
            main_window.main_tab_widget.setTabText(current_index, "New Tab")
        
        return success

    except Exception as e:
        error_msg = f"Error setting up COL tab: {str(e)}"
        main_window.log_message(f"❌ {error_msg}")
        QMessageBox.critical(main_window, "COL Setup Error", error_msg)
        return False

def load_col_file_content(main_window, file_path):
    """Load COL file content"""
    try:
        main_window.log_message(f"📖 Loading COL file: {os.path.basename(file_path)}")
        
        # Show progress
        if hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(0, "Loading COL file...")

        # Validate file
        if not os.path.exists(file_path):
            raise Exception(f"COL file not found: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise Exception(f"Cannot read COL file: {file_path}")

        # DEBUG: Check what COL classes we have
        main_window.log_message("🔍 Importing COL classes...")
        from components.col_core_classes import COLFile
        main_window.log_message("✅ COL classes imported")
        
        # DEBUG: Check the method before loading
        main_window.log_message(f"🔍 COLFile._parse_col1_model method: {COLFile._parse_col1_model}")
        
        # Load COL file
        main_window.log_message("🔍 Creating COLFile instance...")
        col_file = COLFile(file_path)
        main_window.log_message("🔍 Calling col_file.load()...")
        
        if not col_file.load():
            error_details = getattr(col_file, 'load_error', 'Unknown loading error')
            raise Exception(f"Failed to load COL file: {error_details}")

        main_window.log_message("🔍 COL file load() completed")

        # Verify we have models
        if not hasattr(col_file, 'models'):
            col_file.models = []
        
        model_count = len(col_file.models)
        main_window.log_message(f"✅ COL loaded with {model_count} models")
        
        # DEBUG: Check first model AFTER loading
        if model_count > 0:
            first_model = col_file.models[0]
            main_window.log_message(f"🔍 AFTER LOADING - First model name: '{first_model.name}'")
            main_window.log_message(f"🔍 AFTER LOADING - First model spheres: {len(getattr(first_model, 'spheres', []))}")
            main_window.log_message(f"🔍 AFTER LOADING - First model boxes: {len(getattr(first_model, 'boxes', []))}")
            main_window.log_message(f"🔍 AFTER LOADING - First model vertices: {len(getattr(first_model, 'vertices', []))}")
            main_window.log_message(f"🔍 AFTER LOADING - First model faces: {len(getattr(first_model, 'faces', []))}")
            
            # Also check if spheres list has actual objects
            if hasattr(first_model, 'spheres') and len(first_model.spheres) > 0:
                main_window.log_message(f"🔍 AFTER LOADING - First sphere type: {type(first_model.spheres[0])}")
                main_window.log_message(f"🔍 AFTER LOADING - Spheres list: {first_model.spheres}")
            else:
                main_window.log_message(f"🔍 AFTER LOADING - NO SPHERES FOUND!")

        # Update main window state
        main_window.current_col = col_file
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index in main_window.open_files:
            main_window.open_files[current_index]['file_object'] = col_file

        # DEBUG: Check models one more time before display
        main_window.log_message("🔍 BEFORE DISPLAY - Checking models again...")
        if model_count > 0:
            first_model = col_file.models[0]
            main_window.log_message(f"🔍 BEFORE DISPLAY - Model spheres: {len(getattr(first_model, 'spheres', []))}")

        # Export collision data to log file for analysis
        export_col_data_to_log(main_window, col_file, file_path)

        # Display COL data
        main_window.log_message("🔍 Starting table population...")
        populate_col_table(main_window, col_file)
        update_col_info_bar(main_window, col_file, file_path)

        # Update window title
        file_name = os.path.basename(file_path)
        main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        # Hide progress
        if hasattr(main_window.gui_layout, 'hide_progress'):
            main_window.gui_layout.hide_progress()

        main_window.log_message(f"✅ COL file loaded: {file_name} ({model_count} models)")
        return True

    except Exception as e:
        if hasattr(main_window.gui_layout, 'hide_progress'):
            main_window.gui_layout.hide_progress()
        
        error_msg = f"Error loading COL file: {str(e)}"
        main_window.log_message(f"❌ {error_msg}")
        QMessageBox.critical(main_window, "COL Load Error", error_msg)
        return False

def populate_col_table(main_window, col_file):
    """Populate table with COL data"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return False

        table = main_window.gui_layout.table
        
        # Setup table headers
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
        ])

        # Clear existing data
        table.setRowCount(0)

        if not hasattr(col_file, 'models') or not col_file.models:
            table.setRowCount(1)
            table.setItem(0, 0, QTableWidgetItem("No models found"))
            for col in range(1, 7):
                table.setItem(0, col, QTableWidgetItem("-"))
            return True

        # Populate with models
        table.setRowCount(len(col_file.models))
        main_window.log_message(f"🔧 Populating table with {len(col_file.models)} COL models")

        for row, model in enumerate(col_file.models):
            # Get statistics - FORCE MANUAL COUNT to bypass broken get_stats()
            # The parsing worked but get_stats() is broken, so count directly
            spheres = len(getattr(model, 'spheres', []))
            boxes = len(getattr(model, 'boxes', []))
            vertices = len(getattr(model, 'vertices', []))
            faces = len(getattr(model, 'faces', []))
            
            stats = {
                "spheres": spheres,
                "boxes": boxes,
                "vertices": vertices,
                "faces": faces,
                "total_elements": spheres + boxes + faces
            }
            
            # Debug log for first few models
            if row < 3:
                main_window.log_message(f"📊 Model {row+1} DIRECT COUNT: S:{spheres} B:{boxes} V:{vertices} F:{faces}")
                main_window.log_message(f"📊 Model {row+1} spheres attr exists: {hasattr(model, 'spheres')}")
                if hasattr(model, 'spheres'):
                    main_window.log_message(f"📊 Model {row+1} spheres type: {type(model.spheres)} len: {len(model.spheres)}")
                    if len(model.spheres) > 0:
                        main_window.log_message(f"📊 Model {row+1} first sphere: {model.spheres[0]}")
                if hasattr(model, 'boxes') and len(model.boxes) > 0:
                    main_window.log_message(f"📊 Model {row+1} first box: {model.boxes[0]}")
                if hasattr(model, 'vertices') and len(model.vertices) > 0:
                    main_window.log_message(f"📊 Model {row+1} first vertex: {model.vertices[0]}")
                if hasattr(model, 'faces') and len(model.faces) > 0:
                    main_window.log_message(f"📊 Model {row+1} first face: {model.faces[0]}")

            # Model name
            model_name = getattr(model, 'name', f"Model_{row+1}")
            if not model_name or model_name.strip() == "":
                model_name = f"Model_{row+1}"
            table.setItem(row, 0, QTableWidgetItem(str(model_name)))
            
            # Model type
            version = getattr(model, 'version', None)
            if version and hasattr(version, 'name'):
                model_type = f"COL {version.name.replace('COL_', '')}"
            else:
                model_type = "Collision"
            table.setItem(row, 1, QTableWidgetItem(model_type))
            
            # Size calculation
            size = 60  # Header
            size += stats.get('spheres', 0) * 20
            size += stats.get('boxes', 0) * 32
            size += stats.get('vertices', 0) * 12
            size += stats.get('faces', 0) * 12
            
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024*1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            table.setItem(row, 2, QTableWidgetItem(size_str))
            
            # Surface count
            table.setItem(row, 3, QTableWidgetItem(str(stats.get('total_elements', 0))))
            
            # Vertex count
            table.setItem(row, 4, QTableWidgetItem(str(stats.get('vertices', 0))))
            
            # Collision breakdown
            spheres = stats.get('spheres', 0)
            boxes = stats.get('boxes', 0)
            faces = stats.get('faces', 0)
            collision_info = f"S:{spheres} B:{boxes} F:{faces}"
            table.setItem(row, 5, QTableWidgetItem(collision_info))
            
            # Status
            status = "Loaded"
            table.setItem(row, 6, QTableWidgetItem(status))
            
            # Make read-only
            for col in range(7):
                item = table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        # Finalize table
        table.resizeColumnsToContents()
        if table.rowCount() > 0:
            table.selectRow(0)
        
        main_window.log_message(f"✅ COL table populated")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Error populating COL table: {str(e)}")
        return False

def update_col_info_bar(main_window, col_file, file_path):
    """Update info bar with COL information"""
    try:
        gui_layout = main_window.gui_layout
        
        # Update file name
        if hasattr(gui_layout, 'file_name_label'):
            file_name = os.path.basename(file_path)
            gui_layout.file_name_label.setText(f"File: {file_name}")
        
        # Update model count
        if hasattr(gui_layout, 'entry_count_label'):
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            gui_layout.entry_count_label.setText(f"Models: {model_count}")
        
        # Update file size
        if hasattr(gui_layout, 'file_size_label'):
            file_size = os.path.getsize(file_path)
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024*1024:
                size_str = f"{file_size/1024:.1f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.1f} MB"
            gui_layout.file_size_label.setText(f"Size: {size_str}")
        
        # Update format version
        if hasattr(gui_layout, 'format_version_label'):
            gui_layout.format_version_label.setText(f"Format: COL")
        
        main_window.log_message("✅ Updated info bar for COL file")
        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Error updating info bar: {e}")
        return False

def export_col_data_to_log(main_window, col_file, file_path):
    """Export all COL model data to a log file"""
    try:
        import datetime
        
        # Create log filename
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"col_analysis_{base_name}_{timestamp}.txt"
        log_path = os.path.join(os.path.dirname(file_path), log_filename)
        
        main_window.log_message(f"📄 Exporting COL data to: {log_filename}")
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"COL FILE ANALYSIS REPORT\n")
            f.write(f"========================\n")
            f.write(f"File: {file_path}\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Models: {len(col_file.models)}\n")
            f.write(f"\n")
            
            f.write(f"MODEL DETAILS:\n")
            f.write(f"{'#':<4} {'Model Name':<30} {'S':<3} {'B':<3} {'V':<4} {'F':<4} {'Total':<6} {'Status'}\n")
            f.write(f"{'-'*70}\n")
            
            models_with_collision = 0
            total_spheres = 0
            total_boxes = 0
            total_vertices = 0
            total_faces = 0
            
            for i, model in enumerate(col_file.models, 1):
                # Get collision counts
                spheres = len(getattr(model, 'spheres', []))
                boxes = len(getattr(model, 'boxes', []))
                vertices = len(getattr(model, 'vertices', []))
                faces = len(getattr(model, 'faces', []))
                total_elements = spheres + boxes + faces
                
                # Accumulate totals
                total_spheres += spheres
                total_boxes += boxes
                total_vertices += vertices
                total_faces += faces
                
                if total_elements > 0:
                    models_with_collision += 1
                    status = "HAS_COLLISION"
                else:
                    status = "NO_COLLISION"
                
                # Truncate long model names
                model_name = getattr(model, 'name', f'Model_{i}')
                if len(model_name) > 29:
                    model_name = model_name[:26] + "..."
                
                f.write(f"{i:<4} {model_name:<30} {spheres:<3} {boxes:<3} {vertices:<4} {faces:<4} {total_elements:<6} {status}\n")
            
            f.write(f"{'-'*70}\n")
            f.write(f"SUMMARY:\n")
            f.write(f"Models with collision: {models_with_collision}/{len(col_file.models)} ({models_with_collision/len(col_file.models)*100:.1f}%)\n")
            f.write(f"Total spheres: {total_spheres}\n")
            f.write(f"Total boxes: {total_boxes}\n")
            f.write(f"Total vertices: {total_vertices}\n")
            f.write(f"Total faces: {total_faces}\n")
            f.write(f"Total collision elements: {total_spheres + total_boxes + total_faces}\n")
            
            # Add top collision models
            f.write(f"\nTOP 20 MODELS BY COLLISION COMPLEXITY:\n")
            f.write(f"{'Model Name':<30} {'Total Elements':<15} {'Details'}\n")
            f.write(f"{'-'*70}\n")
            
            # Sort models by collision complexity
            models_by_complexity = []
            for i, model in enumerate(col_file.models):
                spheres = len(getattr(model, 'spheres', []))
                boxes = len(getattr(model, 'boxes', []))
                vertices = len(getattr(model, 'vertices', []))
                faces = len(getattr(model, 'faces', []))
                total_elements = spheres + boxes + faces
                
                if total_elements > 0:
                    models_by_complexity.append((
                        getattr(model, 'name', f'Model_{i+1}'),
                        total_elements,
                        f"S:{spheres} B:{boxes} V:{vertices} F:{faces}"
                    ))
            
            # Sort by total elements (descending)
            models_by_complexity.sort(key=lambda x: x[1], reverse=True)
            
            # Write top 20
            for name, total, details in models_by_complexity[:20]:
                if len(name) > 29:
                    name = name[:26] + "..."
                f.write(f"{name:<30} {total:<15} {details}\n")
        
        main_window.log_message(f"✅ COL analysis exported to: {log_path}")
        return log_path
        
    except Exception as e:
        main_window.log_message(f"❌ Error exporting COL data: {e}")
        return None

def add_col_methods_to_main_window(main_window):
    """Add COL-specific methods to main window"""
    try:
        # Color methods
        main_window.get_col_text_color = lambda: "#1565c0"
        main_window.get_col_background_color = lambda: "#e3f2fd"
        
        # Tab info method
        def get_col_tab_info(tab_index):
            if tab_index in main_window.open_files:
                file_info = main_window.open_files[tab_index]
                if file_info.get('type') == 'COL':
                    return {
                        'is_col': True,
                        'file_path': file_info.get('file_path'),
                        'tab_name': file_info.get('tab_name')
                    }
            return {'is_col': False}
        
        main_window.get_col_tab_info = get_col_tab_info

    except Exception as e:
        main_window.log_message(f"❌ Error adding COL methods: {e}")

# MAIN SETUP FUNCTIONS
def setup_complete_col_integration(main_window):
    """Complete COL integration setup"""
    try:
        # Mark integration as ready
        main_window._col_integration_ready = True
        
        # Add COL loading method
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)
        
        # Setup delayed integration
        setup_delayed_col_integration(main_window)
        
        main_window.log_message("✅ Complete COL integration setup finished")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ COL integration setup failed: {str(e)}")
        return False

def setup_delayed_col_integration(main_window):
    """Setup COL integration after GUI is ready"""
    try:
        def try_setup():
            if setup_col_integration_safe(main_window):
                return
            else:
                QTimer.singleShot(100, try_setup)
        
        QTimer.singleShot(100, try_setup)
        
    except Exception as e:
        print(f"Error setting up delayed COL integration: {str(e)}")

# Legacy compatibility
def init_col_integration_placeholder(main_window):
    """Placeholder for COL integration during init - DEPRECATED"""
    main_window._col_integration_needed = True
    print("COL integration marked for later setup - use setup_complete_col_integration instead")