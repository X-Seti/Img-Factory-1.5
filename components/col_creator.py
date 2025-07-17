#this belongs in components/ col_creator.py - Version: 1
# X-Seti - July16 2025 - IMG Factory 1.5 - COL Creation Functions

"""
COL Creation Functions
Handles creating new COL files from scratch
"""

import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox


def create_new_col_file(main_window):
    """Create new COL file"""
    try:
        file_path, _ = QFileDialog.getSaveFileName(
            main_window,
            "Create New COL File",
            "",
            "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            # Create basic COL file
            try:
                from components.col_core_classes import COLFile
                col_file = COLFile()
                if col_file.save_to_file(file_path):
                    main_window.log_message(f"✅ Created new COL file: {os.path.basename(file_path)}")
                else:
                    QMessageBox.critical(main_window, "Error", "Failed to create COL file")
            except ImportError:
                # Fallback - create empty COL file
                create_empty_col_file(file_path)
                main_window.log_message(f"✅ Created basic COL file: {os.path.basename(file_path)}")
                
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to create COL file: {str(e)}")


def create_empty_col_file(file_path):
    """Create a basic empty COL file structure"""
    try:
        # COL1 basic header structure
        col_header = bytearray(44)  # Basic COL header size
        
        # COL identifier
        col_header[0:4] = b'COLL'
        
        # File size (will be updated)
        file_size = 44
        col_header[4:8] = file_size.to_bytes(4, 'little')
        
        # Model name (empty)
        col_header[8:32] = b'\x00' * 24
        
        # Model ID
        col_header[32:36] = (1).to_bytes(4, 'little')
        
        # Bounding sphere (empty)
        col_header[36:44] = b'\x00' * 8
        
        # Write to file
        with open(file_path, 'wb') as f:
            f.write(col_header)
        
        return True
        
    except Exception as e:
        print(f"Error creating empty COL file: {e}")
        return False


def create_col_from_template(main_window, template_type="basic"):
    """Create COL file from template"""
    try:
        file_path, _ = QFileDialog.getSaveFileName(
            main_window,
            f"Create COL File from {template_type.title()} Template",
            "",
            "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            if template_type == "basic":
                success = create_empty_col_file(file_path)
            elif template_type == "vehicle":
                success = create_vehicle_col_template(file_path)
            elif template_type == "building":
                success = create_building_col_template(file_path)
            else:
                success = create_empty_col_file(file_path)
            
            if success:
                main_window.log_message(f"✅ Created {template_type} COL template: {os.path.basename(file_path)}")
            else:
                QMessageBox.critical(main_window, "Error", f"Failed to create {template_type} COL template")
                
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to create COL template: {str(e)}")


def create_vehicle_col_template(file_path):
    """Create COL template for vehicles with basic bounding box"""
    try:
        # More complex COL structure for vehicles
        col_data = bytearray(100)  # Larger for vehicle template
        
        # COL identifier
        col_data[0:4] = b'COLL'
        
        # File size
        file_size = 100
        col_data[4:8] = file_size.to_bytes(4, 'little')
        
        # Model name
        model_name = b'vehicle_template\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        col_data[8:32] = model_name
        
        # Model ID
        col_data[32:36] = (100).to_bytes(4, 'little')
        
        # Bounding sphere (centered at origin, radius 5.0)
        import struct
        center_x = struct.pack('<f', 0.0)
        center_y = struct.pack('<f', 0.0) 
        center_z = struct.pack('<f', 0.0)
        radius = struct.pack('<f', 5.0)
        
        col_data[36:40] = center_x
        col_data[40:44] = center_y
        col_data[44:48] = center_z
        col_data[48:52] = radius
        
        # Basic collision box data
        col_data[52:56] = (1).to_bytes(4, 'little')  # Number of boxes
        col_data[56:100] = b'\x00' * 44  # Box data placeholder
        
        # Write to file
        with open(file_path, 'wb') as f:
            f.write(col_data)
        
        return True
        
    except Exception as e:
        print(f"Error creating vehicle COL template: {e}")
        return False


def create_building_col_template(file_path):
    """Create COL template for buildings"""
    try:
        # Building-specific COL structure
        col_data = bytearray(80)
        
        # COL identifier
        col_data[0:4] = b'COLL'
        
        # File size
        file_size = 80
        col_data[4:8] = file_size.to_bytes(4, 'little')
        
        # Model name
        model_name = b'building_template\x00\x00\x00\x00\x00\x00\x00\x00'
        col_data[8:32] = model_name
        
        # Model ID
        col_data[32:36] = (200).to_bytes(4, 'little')
        
        # Bounding sphere (larger for buildings)
        import struct
        center_x = struct.pack('<f', 0.0)
        center_y = struct.pack('<f', 0.0)
        center_z = struct.pack('<f', 2.0)  # Slightly elevated
        radius = struct.pack('<f', 10.0)  # Larger radius
        
        col_data[36:40] = center_x
        col_data[40:44] = center_y
        col_data[44:48] = center_z
        col_data[48:52] = radius
        
        # Building-specific data
        col_data[52:80] = b'\x00' * 28
        
        # Write to file
        with open(file_path, 'wb') as f:
            f.write(col_data)
        
        return True
        
    except Exception as e:
        print(f"Error creating building COL template: {e}")
        return False


def import_col_to_current_img(main_window):
    """Import COL file to current IMG"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "Warning", "No IMG file is currently open")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Import COL File to IMG",
            "",
            "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            # Implementation for importing COL to IMG
            main_window.log_message(f"🔗 COL import functionality will be implemented")
            
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to import COL: {str(e)}")


def export_all_col_from_img(main_window):
    """Export all COL files from current IMG"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "Warning", "No IMG file is currently open")
            return
        
        output_dir = QFileDialog.getExistingDirectory(
            main_window,
            "Export COL Files to Directory"
        )
        
        if output_dir:
            # Implementation for exporting all COL files
            main_window.log_message(f"📤 COL export functionality will be implemented")
            
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to export COL files: {str(e)}")


# Export functions
__all__ = [
    'create_new_col_file',
    'create_empty_col_file',
    'create_col_from_template',
    'create_vehicle_col_template',
    'create_building_col_template',
    'import_col_to_current_img',
    'export_all_col_from_img'
]