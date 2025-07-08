#this belongs in components/ col_tab_integration.py - Version: 4
# X-Seti - July08 2025 - COL Tab Integration for IMG Factory 1.5 (DEBUG VERSION)

import os
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt

def setup_col_integration_safe(main_window):
    """Setup COL integration safely after GUI is ready"""
    try:
        # Only setup after GUI is fully initialized
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window, 'log_message'):
            print("GUI not ready for COL integration - will retry later")
            return False
        
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
        main_window.log_message(f"❌ Error adding COL methods: {str(e)}")

def get_model_stats_with_estimates(model):
    """Get model statistics including estimates if available"""
    if hasattr(model, '_has_estimates') and model._has_estimates:
        return {
            "spheres": getattr(model, '_estimated_spheres', 0),
            "boxes": getattr(model, '_estimated_boxes', 0),
            "vertices": getattr(model, '_estimated_vertices', 0), 
            "faces": getattr(model, '_estimated_faces', 0),
            "face_groups": 0,  # Not estimated
            "shadow_vertices": 0,  # COL1 doesn't have shadow mesh
            "shadow_faces": 0,  # COL1 doesn't have shadow mesh
            "total_elements": (getattr(model, '_estimated_spheres', 0) + 
                             getattr(model, '_estimated_boxes', 0) + 
                             getattr(model, '_estimated_faces', 0))
        }
    else:
        # Use original method
        return model.get_stats() if hasattr(model, 'get_stats') else {}

def load_col_file_safely(main_window, file_path):
    """Load COL file safely - DEBUG VERSION with detailed logging"""
    try:
        main_window.log_message(f"🔧 Setting up COL tab for: {os.path.basename(file_path)}")
        
        # Check if current tab is empty (no file loaded) 
        current_index = main_window.main_tab_widget.currentIndex()
        
        if current_index not in main_window.open_files:
            # Current tab is empty, use it
            main_window.log_message(f"Using current empty tab for COL file")
        else:
            # Current tab has a file, create new tab
            main_window.log_message(f"Creating new tab for COL file")
            main_window.close_manager.create_new_tab()
            current_index = main_window.main_tab_widget.currentIndex()
        
        # Store file info BEFORE loading
        file_name = os.path.basename(file_path)
        # Remove .col extension for cleaner tab names
        if file_name.lower().endswith('.col'):
            file_name_clean = file_name[:-4]  # Remove .col extension
        else:
            file_name_clean = file_name

        # Use shield icon for COL files
        tab_name = f"🛡️ {file_name_clean}"

        main_window.open_files[current_index] = {
            'type': 'COL',
            'file_path': file_path,
            'file_object': None,  # Will be set when loaded
            'tab_name': tab_name
        }

        # Update tab name with icon
        main_window.main_tab_widget.setTabText(current_index, tab_name)

        # Start loading COL file
        load_col_file_content_debug(main_window, file_path)

    except Exception as e:
        error_msg = f"Error setting up COL tab: {str(e)}"
        main_window.log_message(f"❌ {error_msg}")
        QMessageBox.critical(main_window, "COL Setup Error", error_msg)

def load_col_file_content_debug(main_window, file_path):
    """Load COL file content - DEBUG VERSION with inline estimation"""
    try:
        main_window.log_message(f"🔍 Loading COL file: {os.path.basename(file_path)}")
        
        # Show progress
        if hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(0, "Loading COL file...")

        # Verify file exists and is readable
        if not os.path.exists(file_path):
            raise Exception(f"COL file not found: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise Exception(f"Cannot read COL file: {file_path}")

        # File size info
        file_size = os.path.getsize(file_path)
        main_window.log_message(f"📊 File size: {file_size:,} bytes")

        # Try to import COL classes with fallback
        try:
            from components.col_core_classes import COLFile, diagnose_col_file
            main_window.log_message("✅ COL core classes imported successfully")
        except ImportError as e:
            raise Exception(f"COL core classes not available: {str(e)}")

        # Diagnose file first - DETAILED
        try:
            diagnosis = diagnose_col_file(file_path)
            main_window.log_message(f"🔬 COL Diagnosis:")
            main_window.log_message(f"   Signature: {diagnosis.get('header_ascii', 'Unknown')}")
            main_window.log_message(f"   Version: {diagnosis.get('detected_version', 'Unknown')}")
            main_window.log_message(f"   Valid: {diagnosis.get('signature_valid', False)}")
            main_window.log_message(f"   Declared size: {diagnosis.get('declared_size', 'Unknown')}")
            
            if diagnosis.get('error'):
                main_window.log_message(f"⚠️ Diagnosis error: {diagnosis.get('error')}")
                
        except Exception as e:
            main_window.log_message(f"⚠️ Could not diagnose COL file: {str(e)}")

        # Create and load COL file object
        main_window.log_message("🔧 Creating COL file object...")
        col_file = COLFile(file_path)
        
        main_window.log_message("📖 Loading COL file data...")
        if not col_file.load():
            # Try to get more specific error info
            error_details = "Unknown loading error"
            if hasattr(col_file, 'load_error'):
                error_details = col_file.load_error
            raise Exception(f"Failed to load COL file: {error_details}")

        # INLINE ESTIMATION: Add estimates to models after loading
        main_window.log_message("🔧 Adding collision estimates to models...")
        
        # Read raw file data to calculate remaining bytes for each model
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        offset = 0
        import struct
        for i, model in enumerate(col_file.models):
            try:
                # Find this model's position and calculate remaining data
                if offset < len(raw_data) - 8:
                    # Read model size
                    model_size = struct.unpack('<I', raw_data[offset+4:offset+8])[0]
                    header_size = 26  # COLL(4) + size(4) + name(22) = 30, but we start after 4
                    remaining_bytes = model_size - 22  # Subtract name(22) + ID(4)
                    
                    if remaining_bytes > 0:
                        # Estimate collision data from remaining bytes
                        # Rough estimates based on typical GTA COL structure
                        estimated_spheres = max(0, min(remaining_bytes // 40, 20))  # Conservative estimate
                        estimated_boxes = max(0, min(remaining_bytes // 60, 15))   # Conservative estimate
                        
                        # Estimate mesh data from remaining space
                        mesh_bytes = remaining_bytes - (estimated_spheres * 20) - (estimated_boxes * 32)
                        if mesh_bytes > 50:  # Need minimum space for vertices/faces
                            estimated_vertices = max(0, min(mesh_bytes // 20, 100))  # Conservative
                            estimated_faces = max(0, min(estimated_vertices // 3, estimated_vertices))
                        else:
                            estimated_vertices = 0
                            estimated_faces = 0
                        
                        # Store estimates in model
                        model._estimated_spheres = estimated_spheres
                        model._estimated_boxes = estimated_boxes
                        model._estimated_vertices = estimated_vertices
                        model._estimated_faces = estimated_faces
                        model._remaining_bytes = remaining_bytes
                        model._has_estimates = True
                        
                        main_window.log_message(f"   Model '{model.name}': {remaining_bytes}B -> S:{estimated_spheres} B:{estimated_boxes} V:{estimated_vertices} F:{estimated_faces}")
                    else:
                        model._estimated_spheres = 0
                        model._estimated_boxes = 0
                        model._estimated_vertices = 0
                        model._estimated_faces = 0
                        model._remaining_bytes = 0
                        model._has_estimates = True
                    
                    # Move to next model
                    offset += model_size + 8
                
            except Exception as e:
                main_window.log_message(f"⚠️ Error estimating model {i}: {e}")
                # Set minimal estimates
                model._estimated_spheres = 0
                model._estimated_boxes = 0 
                model._estimated_vertices = 0
                model._estimated_faces = 0
                model._remaining_bytes = 0
                model._has_estimates = True

        # Verify loaded data - DETAILED DEBUG
        if not hasattr(col_file, 'models'):
            main_window.log_message("⚠️ COL file has no models attribute")
            col_file.models = []  # Create empty models list
        
        model_count = len(col_file.models) if col_file.models else 0
        main_window.log_message(f"✅ COL loaded with {model_count} models")

        # DEBUG: Analyze each model in detail
        if col_file.models:
            main_window.log_message(f"🔍 Analyzing {model_count} models:")
            for i, model in enumerate(col_file.models[:5]):  # Show first 5 models
                # Use custom get_stats that includes estimates
                stats = get_model_stats_with_estimates(model)
                model_name = getattr(model, 'name', f"Model_{i+1}")
                has_estimates = getattr(model, '_has_estimates', False)
                remaining = getattr(model, '_remaining_bytes', 0)
                main_window.log_message(f"   Model {i+1}: '{model_name}' (Est: {has_estimates}, {remaining}B)")
                main_window.log_message(f"      Spheres: {stats.get('spheres', 0)}")
                main_window.log_message(f"      Boxes: {stats.get('boxes', 0)}")
                main_window.log_message(f"      Vertices: {stats.get('vertices', 0)}")
                main_window.log_message(f"      Faces: {stats.get('faces', 0)}")
                main_window.log_message(f"      Total Elements: {stats.get('total_elements', 0)}")
            
            if model_count > 5:
                main_window.log_message(f"   ... and {model_count - 5} more models")

        # Update current COL reference
        main_window.current_col = col_file

        # Update file info in open_files
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index in main_window.open_files:
            main_window.open_files[current_index]['file_object'] = col_file
            main_window.log_message(f"✅ Updated tab {current_index} with COL object")

        # CORRECT: Populate the main table with COL data (like IMG files do)
        populate_table_with_col_data_debug(main_window, col_file)

        # Update info bar with COL information
        update_info_bar_for_col(main_window, col_file, file_path)

        # Hide progress
        if hasattr(main_window.gui_layout, 'hide_progress'):
            main_window.gui_layout.hide_progress()

        # Update window title
        file_name = os.path.basename(file_path)
        main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        main_window.log_message(f"✅ COL Load Complete: {file_name} ({model_count} models)")

    except Exception as e:
        if hasattr(main_window.gui_layout, 'hide_progress'):
            main_window.gui_layout.hide_progress()
        error_msg = f"Error loading COL file: {str(e)}"
        main_window.log_message(f"❌ {error_msg}")
        
        # More detailed error logging
        main_window.log_message(f"📁 File path: {file_path}")
        main_window.log_message(f"📊 File exists: {os.path.exists(file_path)}")
        if os.path.exists(file_path):
            main_window.log_message(f"📊 File size: {os.path.getsize(file_path)} bytes")
        
        QMessageBox.critical(main_window, "COL Load Error", error_msg)

def calculate_model_size(model, stats):
    """Calculate estimated size of a COL model in bytes"""
    try:
        # Check if we have better estimation available
        try:
            from components.col_estimation_patch import estimate_col_size_from_stats
            return estimate_col_size_from_stats(stats)
        except ImportError:
            pass
        
        # Fallback calculation
        size = 60  # Basic model header
        
        # Spheres: each sphere is typically 16-20 bytes (center + radius + material)
        size += stats.get('spheres', 0) * 20
        
        # Boxes: each box is typically 24-32 bytes (min + max + material)  
        size += stats.get('boxes', 0) * 32
        
        # Vertices: each vertex is typically 12-16 bytes (x, y, z coordinates)
        size += stats.get('vertices', 0) * 16
        
        # Faces: each face is typically 8-12 bytes (3 vertex indices + material)
        size += stats.get('faces', 0) * 12
        
        # Face groups: if present, add extra overhead
        size += stats.get('face_groups', 0) * 8
        
        # Shadow mesh (COL3 only)
        size += stats.get('shadow_vertices', 0) * 16
        size += stats.get('shadow_faces', 0) * 12
        
        return max(size, 60)  # Minimum 60 bytes (header)
        
    except Exception as e:
        return 60  # Fallback to header size

def populate_table_with_col_data_debug(main_window, col_file):
    """Populate the main table with COL model data - DEBUG VERSION"""
    try:
        # Access the main table (same as IMG files use)
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return

        table = main_window.gui_layout.table
        
        # Configure table for COL data (7 columns to include size)
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
        ])

        # Clear existing table data
        table.setRowCount(0)
        main_window.log_message(f"🔧 Configuring table for {len(col_file.models)} COL models")

        # Populate with COL models
        if hasattr(col_file, 'models') and col_file.models:
            table.setRowCount(len(col_file.models))
            
            for row, model in enumerate(col_file.models):
                # Get model statistics using estimates if available
                stats = get_model_stats_with_estimates(model)
                
                # DEBUG: Log stats for first few models
                if row < 3:
                    main_window.log_message(f"📊 Model {row+1} stats: {stats}")
                
                # Model name/index
                model_name = getattr(model, 'name', f"Model_{row+1}")
                if not model_name or model_name.strip() == "":
                    model_name = f"Model_{row+1}"
                table.setItem(row, 0, QTableWidgetItem(str(model_name)))
                
                # Model type - show COL version
                version = getattr(model, 'version', None)
                if version and hasattr(version, 'name'):
                    model_type = f"COL {version.name.replace('COL_', '')}"
                else:
                    model_type = "Collision"
                table.setItem(row, 1, QTableWidgetItem(model_type))
                
                # Calculate estimated model size in bytes
                model_size = calculate_model_size(model, stats)
                if model_size < 1024:
                    size_str = f"{model_size} B"
                elif model_size < 1024*1024:
                    size_str = f"{model_size/1024:.1f} KB"
                else:
                    size_str = f"{model_size/(1024*1024):.1f} MB"
                table.setItem(row, 2, QTableWidgetItem(size_str))
                
                # Surface count (total collision elements)
                surface_count = stats.get('total_elements', 0)
                table.setItem(row, 3, QTableWidgetItem(str(surface_count)))
                
                # Vertex count
                vertex_count = stats.get('vertices', 0)
                table.setItem(row, 4, QTableWidgetItem(str(vertex_count)))
                
                # Collision breakdown (S:spheres B:boxes F:faces)
                spheres = stats.get('spheres', 0)
                boxes = stats.get('boxes', 0) 
                faces = stats.get('faces', 0)
                collision_info = f"S:{spheres} B:{boxes} F:{faces}"
                table.setItem(row, 5, QTableWidgetItem(collision_info))
                
                # Status
                status = "Loaded"
                table.setItem(row, 6, QTableWidgetItem(status))
                
                # Make all items read-only
                for col in range(7):
                    item = table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        else:
            # No models found
            table.setRowCount(1)
            table.setItem(0, 0, QTableWidgetItem("No models found"))
            for col in range(1, 7):
                table.setItem(0, col, QTableWidgetItem("-"))

        # Resize columns to content
        table.resizeColumnsToContents()
        
        # Update table selection behavior
        table.selectRow(0)  # Select first row
        
        main_window.log_message(f"✅ Populated table with {table.rowCount()} COL models")

    except Exception as e:
        main_window.log_message(f"❌ Error populating table with COL data: {str(e)}")

def update_info_bar_for_col(main_window, col_file, file_path):
    """Update the info bar with COL file information - LIKE IMG FILES DO"""
    try:
        # Access the info bar labels (same as IMG files use)
        gui_layout = main_window.gui_layout
        
        # Update file name
        if hasattr(gui_layout, 'file_name_label'):
            file_name = os.path.basename(file_path)
            gui_layout.file_name_label.setText(f"File: {file_name}")
        
        # Update entry count (models for COL)
        if hasattr(gui_layout, 'entry_count_label'):
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            gui_layout.entry_count_label.setText(f"Models: {model_count}")
        
        # Update file size
        if hasattr(gui_layout, 'file_size_label'):
            file_size = os.path.getsize(file_path)
            # Simple file size formatting
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024*1024:
                size_str = f"{file_size/1024:.1f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.1f} MB"
            gui_layout.file_size_label.setText(f"Size: {size_str}")
        
        # Update format version
        if hasattr(gui_layout, 'format_version_label'):
            version = getattr(col_file, 'version', 'Unknown')
            gui_layout.format_version_label.setText(f"Format: COL v{version}")
        
        main_window.log_message("✅ Updated info bar for COL file")

    except Exception as e:
        main_window.log_message(f"⚠️ Error updating info bar: {str(e)}")

# SETUP FUNCTION TO REPLACE init_col_integration_placeholder
def setup_complete_col_integration(main_window):
    """Complete COL integration setup - REPLACES placeholder"""
    try:
        # Mark integration as ready
        main_window._col_integration_ready = True
        
        # Add COL loading method to main window
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)
        
        # Setup delayed integration
        setup_delayed_col_integration(main_window)
        
        main_window.log_message("✅ Complete COL integration setup finished")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ COL integration setup failed: {str(e)}")
        return False

# Function to call from main imgfactory.py after GUI is ready
def setup_delayed_col_integration(main_window):
    """Setup COL integration after GUI is fully ready"""
    try:
        # Use a timer to delay until GUI is ready
        from PyQt6.QtCore import QTimer
        
        def try_setup():
            if setup_col_integration_safe(main_window):
                # Success - stop trying
                return
            else:
                # Retry in 100ms
                QTimer.singleShot(100, try_setup)
        
        # Start the retry process
        QTimer.singleShot(100, try_setup)
        
    except Exception as e:
        print(f"Error setting up delayed COL integration: {str(e)}")

# DEPRECATED - keeping for compatibility but should not be used
def init_col_integration_placeholder(main_window):
    """Placeholder for COL integration during init - DEPRECATED"""
    # Just set a flag that COL integration is needed
    main_window._col_integration_needed = True
    print("COL integration marked for later setup - use setup_complete_col_integration instead")