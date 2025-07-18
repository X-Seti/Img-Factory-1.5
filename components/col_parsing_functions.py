#this belongs in components/col_parsing_functions.py - Version: 9
# X-Seti - July18 2025 - Img Factory 1.5 - Fixed COL Parser with IMG Debug

"""
COL Parser - Complete collision file parsing using IMG debug system
Handles all COL format versions (COL1/COL2/COL3/COL4) with working collision data parsing
PORTED FROM WORKING OLD FILES - Updated debug system only
"""

import struct
import os
from typing import Dict, List, Tuple, Optional

# Use IMG debug system instead of broken COL debug
try:
    from components.img_debug_functions import img_debugger
    debug_available = True
except ImportError:
    debug_available = False
    print("⚠️ IMG debug system not available")

##Methods list -
# _load_col_file
# _populate_col_table_enhanced
# _setup_col_tab
# setup_col_tab_integration
# _setup_col_table_structure
# _update_col_info_bar_enhanced
# _validate_col_file
# format_model_collision_types
# get_model_collision_stats
# load_col_file_safely
# parse_col_file_with_debug
# reset_table_styling

##class COLParser: -
#__init__
# _calculate_model_end_offset
# _is_multi_model_archive
# _parse_collision_data
# _parse_multi_model_archive
# clear_debug_log
# format_collision_types
# get_debug_log
# get_model_stats_by_index
# log
# parse_col_file_structure
# parse_single_model
# set_debug


# Quick fix for COL loading hang - Add this to your COL parser

def safe_parse_col_file_structure(self, file_path):
    """Parse COL file with hang prevention - FIXED VERSION"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

        # Limit file size to prevent memory issues
        if len(data) > 50 * 1024 * 1024:  # 50MB limit
            self.log(f"COL file too large: {len(data)} bytes")
            return []

        self.log(f"Parsing COL file: {os.path.basename(file_path)} ({len(data)} bytes)")

        models = []
        offset = 0
        model_index = 0
        max_iterations = 500  # Safety limit
        iteration_count = 0

        while offset < len(data) and iteration_count < max_iterations:
            iteration_count += 1

            # CRITICAL: Safety checks
            if offset + 32 > len(data):
                self.log(f"Not enough data remaining: {len(data) - offset} bytes")
                break

            # Parse this model with timeout protection
            initial_offset = offset
            model_info, new_offset = self.safe_parse_single_model(data, offset, model_index)

            # CRITICAL: Check for infinite loop conditions
            if new_offset <= initial_offset:
                self.log(f"HANG PREVENTION: Offset didn't advance (was {initial_offset}, now {new_offset})")
                break

            if model_info is None:
                self.log(f"Failed to parse model {model_index}, stopping")
                break

            models.append(model_info)
            offset = new_offset
            model_index += 1

            self.log(f"Model {model_index - 1} parsed, next offset: {offset}")

            # Additional safety checks
            if model_index > 200:
                self.log("Safety limit reached (200 models)")
                break

            if offset >= len(data):
                self.log("Reached end of data")
                break

        if iteration_count >= max_iterations:
            self.log("HANG PREVENTION: Maximum iterations reached")

        self.log(f"Parsing complete: {len(models)} models found")
        return models

    except Exception as e:
        self.log(f"Error parsing COL file: {str(e)}")
        return []

def safe_parse_single_model(self, data, offset, model_index):
    """Parse single model with hang prevention"""
    try:
        start_offset = offset

        # Read signature with bounds check
        if offset + 8 > len(data):
            return None, offset

        signature = data[offset:offset+4]

        # Validate signature
        valid_signatures = [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']
        if signature not in valid_signatures:
            self.log(f"Invalid signature: {signature}")
            return None, offset + 1  # Advance by 1 to prevent infinite loop

        # Read file size
        file_size = struct.unpack('<I', data[offset+4:offset+8])[0]

        # CRITICAL: Validate file size to prevent hang
        if file_size <= 0 or file_size > 10 * 1024 * 1024:  # 10MB limit per model
            self.log(f"Invalid model size: {file_size}")
            return None, offset + 8  # Skip header

        total_size = file_size + 8

        # Check bounds
        if offset + total_size > len(data):
            self.log(f"Model size exceeds data: need {total_size}, have {len(data) - offset}")
            return None, offset + 8  # Skip header

        # Create basic model info without deep parsing (to prevent hang)
        model_info = {
            'index': model_index,
            'version': 1 if signature == b'COLL' else 2,
            'size': file_size,
            'offset': offset,
            'signature': signature,
            'spheres': 0,    # Set to 0 for now
            'boxes': 0,      # Set to 0 for now
            'vertices': 0,   # Set to 0 for now
            'faces': 0,      # Set to 0 for now
            'collision_types': ['Basic COL (safe mode)']  # Simple fallback
        }

        self.log(f"Model {model_index} parsed safely (size: {file_size})")

        # Return with safe offset advancement
        return model_info, offset + total_size

    except Exception as e:
        self.log(f"Error parsing single model: {str(e)}")
        return None, offset + 8  # Safe advancement

# REPLACE the hanging method with this:
# Replace: self.parse_col_file_structure = safe_parse_col_file_structure
# Replace: self.parse_single_model = safe_parse_single_model

def reset_table_styling(main_window):
    """Completely reset table styling to default"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return

        table = main_window.gui_layout.table
        header = table.horizontalHeader()

        # Clear all styling
        table.setStyleSheet("")
        header.setStyleSheet("")
        table.setObjectName("")

        # Reset to basic alternating colors
        table.setAlternatingRowColors(True)

        main_window.log_message("🔧 Table styling completely reset")

    except Exception as e:
        main_window.log_message(f"⚠️ Error resetting table styling: {str(e)}")


def setup_col_tab_integration(main_window):
    """Setup COL tab integration with main window"""
    try:
        # Add COL loading method to main window
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)

        # Add styling reset method
        main_window._reset_table_styling = lambda: reset_table_styling(main_window)

        main_window.log_message("✅ COL tab integration ready")
        return True

    except Exception as e:
        main_window.log_message(f"❌ COL tab integration failed: {str(e)}")
        return False


def load_col_file_safely(main_window, file_path):
    """Load COL file safely with proper tab management"""
    try:
        # Validate file
        if not _validate_col_file(main_window, file_path):
            return False

        # Setup tab
        tab_index = _setup_col_tab(main_window, file_path)
        if tab_index is None:
            return False

        # Load COL file
        col_file = _load_col_file(main_window, file_path)
        if col_file is None:
            return False

        # Setup table structure for COL data
        _setup_col_table_structure(main_window)

        # Populate table with working COL data
        _populate_col_table_enhanced(main_window, col_file)

        # Update main window state
        main_window.current_col = col_file
        main_window.open_files[tab_index]['file_object'] = col_file

        # Update info bar with enhanced data
        _update_col_info_bar_enhanced(main_window, col_file, file_path)

        main_window.log_message(f"✅ COL file loaded: {os.path.basename(file_path)}")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return False


def _validate_col_file(main_window, file_path): #vers 1
    """Validate COL file before loading"""
    try:
        if not os.path.exists(file_path):
            main_window.log_message(f"❌ COL file not found: {file_path}")
            return False

        if not file_path.lower().endswith('.col'):
            main_window.log_message(f"❌ Not a COL file: {file_path}")
            return False

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size < 8:
            main_window.log_message(f"❌ COL file too small: {file_size} bytes")
            return False

        # Check COL signature
        with open(file_path, 'rb') as f:
            signature = f.read(4)
            if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                main_window.log_message(f"❌ Invalid COL signature: {signature}")
                return False

        return True

    except Exception as e:
        main_window.log_message(f"❌ COL validation error: {str(e)}")
        return False


def _setup_col_tab(main_window, file_path): #vers 1
    """Setup COL tab in main window"""
    try:
        filename = os.path.basename(file_path)
        
        # Check if file is already open
        for i, open_file in enumerate(main_window.open_files):
            if open_file['path'] == file_path:
                main_window.tab_widget.setCurrentIndex(i)
                return i

        # Create new tab
        tab_index = main_window.tab_widget.addTab(main_window.gui_layout.central_widget, filename)
        main_window.tab_widget.setCurrentIndex(tab_index)

        # Add to open files
        main_window.open_files.append({
            'path': file_path,
            'type': 'COL',
            'file_object': None
        })

        return tab_index

    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
        return None


def _load_col_file(main_window, file_path): #vers 1
    """Load COL file using working COL core classes"""
    try:
        # Import COL core classes
        from components.col_core_classes import COLFile
        
        # Create COL file object
        col_file = COLFile(file_path)
        
        # Load the file
        if col_file.load():
            main_window.log_message(f"✅ COL file loaded successfully: {len(col_file.models)} models")
            return col_file
        else:
            main_window.log_message(f"❌ Failed to load COL file: {col_file.load_error}")
            return None

    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return None


def _setup_col_table_structure(main_window): #vers 1
    """Setup table structure for COL data with scoped styling"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return

        table = main_window.gui_layout.table
        
        # Configure table for COL data (7 columns)
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
        ])

        # Set column widths
        table.setColumnWidth(0, 60)   # Model
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 100)  # Size
        table.setColumnWidth(3, 80)   # Surfaces
        table.setColumnWidth(4, 80)   # Vertices
        table.setColumnWidth(5, 120)  # Collision
        table.setColumnWidth(6, 80)   # Status

        # Apply scoped COL table styling
        table.setObjectName("col_table")
        col_table_style = """
            QTableWidget#col_table {
                background-color: #F8F9FA;
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget#col_table::item {
                padding: 6px;
                border: none;
            }
            QTableWidget#col_table::item:alternate {
                background-color: #F5F5F5;
            }
            QTableWidget#col_table::item:hover {
                background-color: #E3F2FD;
            }
            QTableWidget#col_table::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """

        # Apply header styling separately
        header_style = """
            background-color: #BBDEFB;
            color: #1976D2;
            font-weight: bold;
            border: 1px solid #90CAF9;
            padding: 6px;
        """

        # Apply table styling
        table.setStyleSheet(col_table_style)

        # Apply header styling directly to the header widget
        header = table.horizontalHeader()
        header.setStyleSheet(f"""
            QHeaderView::section {{
                {header_style}
            }}
            QHeaderView::section:hover {{
                background-color: #90CAF9;
            }}
        """)

        # Clear existing data
        table.setRowCount(0)

        main_window.log_message("🔧 Table structure configured for COL data")

    except Exception as e:
        main_window.log_message(f"⚠️ Error setting up table structure: {str(e)}")


def _populate_col_table_enhanced(main_window, col_file): #vers 1
    """Populate table with COL data using working parser"""
    try:
        if debug_available:
            img_debugger.debug("Starting COL table population")
        
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return
        
        table = main_window.gui_layout.table
        
        # Import QTableWidgetItem
        try:
            from PyQt6.QtWidgets import QTableWidgetItem
        except ImportError:
            try:
                from PyQt5.QtWidgets import QTableWidgetItem
            except ImportError:
                main_window.log_message("❌ QTableWidgetItem not available")
                return
        
        if not hasattr(col_file, 'models') or not col_file.models:
            main_window.log_message("⚠️ No models found in COL file")
            return
        
        table.setRowCount(len(col_file.models))
        main_window.log_message(f"🔧 Populating table with {len(col_file.models)} COL models")
        
        # Use working collision parser for real data
        parser = COLParser(debug=debug_available)
        parsed_models = parser.parse_col_file_structure(col_file.file_path)
        
        for row, model in enumerate(col_file.models):
            try:
                # Get collision stats from working parser
                collision_stats = ""
                if parsed_models and row < len(parsed_models):
                    parsed_model = parsed_models[row]
                    if isinstance(parsed_model, dict):
                        collision_stats = format_model_collision_types(parsed_model)
                
                # Model index
                table.setItem(row, 0, QTableWidgetItem(str(row)))
                
                # Type (COL version)
                version_str = f"COL{model.version.value}" if hasattr(model, 'version') else "COL1"
                table.setItem(row, 1, QTableWidgetItem(version_str))
                
                # Size
                size_str = f"{len(model.spheres + model.boxes + model.vertices)} objects"
                table.setItem(row, 2, QTableWidgetItem(size_str))
                
                # Surfaces
                surfaces = len(model.face_groups) if hasattr(model, 'face_groups') else 0
                table.setItem(row, 3, QTableWidgetItem(str(surfaces)))
                
                # Vertices
                vertices = len(model.vertices) if hasattr(model, 'vertices') else 0
                table.setItem(row, 4, QTableWidgetItem(str(vertices)))
                
                # Collision types
                table.setItem(row, 5, QTableWidgetItem(collision_stats))
                
                # Status
                status = "✅ Loaded" if model.is_loaded else "❌ Error"
                table.setItem(row, 6, QTableWidgetItem(status))
                
            except Exception as e:
                main_window.log_message(f"⚠️ Error populating row {row}: {str(e)}")
                # Fill with error data
                table.setItem(row, 0, QTableWidgetItem(str(row)))
                table.setItem(row, 1, QTableWidgetItem("ERROR"))
                table.setItem(row, 2, QTableWidgetItem("N/A"))
                table.setItem(row, 3, QTableWidgetItem("N/A"))
                table.setItem(row, 4, QTableWidgetItem("N/A"))
                table.setItem(row, 5, QTableWidgetItem("Parse Error"))
                table.setItem(row, 6, QTableWidgetItem("❌ Error"))

        main_window.log_message("✅ COL table population complete")

    except Exception as e:
        main_window.log_message(f"❌ Error populating COL table: {str(e)}")


def _update_col_info_bar_enhanced(main_window, col_file, file_path): #vers 1
    """Update info bar with COL file information"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'info_bar'):
            return

        info_bar = main_window.gui_layout.info_bar
        
        # Calculate statistics
        total_models = len(col_file.models)
        total_vertices = sum(len(model.vertices) for model in col_file.models if hasattr(model, 'vertices'))
        total_surfaces = sum(len(model.face_groups) for model in col_file.models if hasattr(model, 'face_groups'))
        
        # File info
        file_size = os.path.getsize(file_path)
        file_size_str = f"{file_size:,} bytes"
        
        # Update info bar
        info_text = f"COL File: {os.path.basename(file_path)} | Models: {total_models} | Vertices: {total_vertices} | Surfaces: {total_surfaces} | Size: {file_size_str}"
        info_bar.setText(info_text)
        
        if debug_available:
            img_debugger.debug(f"Updated info bar: {info_text}")

    except Exception as e:
        main_window.log_message(f"⚠️ Error updating info bar: {str(e)}")


# COL Parser Class - WORKING VERSION FROM OLD FILES
class COLParser:
    """Complete COL file parser with working collision data extraction - Updated to use IMG debug"""
    
    def __init__(self, debug=None): #vers 1
        """Initialize COL parser with IMG debug control"""
        self.debug = debug if debug is not None else debug_available
        self.log_messages = []
    
    def log(self, message): #vers 1
        """Log debug message using IMG debug system"""
        if self.debug and debug_available:
            img_debugger.debug(f"COLParser: {message}")
        self.log_messages.append(message)
    
    def set_debug(self, enabled): #vers 1
        """Update debug setting"""
        self.debug = enabled
    
    def parse_col_file_structure(self, file_path): #vers 1
        """Parse complete COL file and return structure info for all models - WORKING VERSION"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            self.log(f"Parsing COL file: {os.path.basename(file_path)} ({len(data)} bytes)")
            
            # CRITICAL FIX: First check if this is a multi-model COL archive
            if self._is_multi_model_archive(data):
                return self._parse_multi_model_archive(data)
            
            # Single model parsing (original working approach)
            models = []
            offset = 0
            model_index = 0
            
            while offset < len(data):
                self.log(f"--- Model {model_index} at offset {offset} ---")
                
                # Check if we have enough data for a model
                if offset + 32 > len(data):
                    self.log(f"Not enough data for model header (need 32, have {len(data) - offset})")
                    break
                
                # Parse this model
                model_info, new_offset = self.parse_single_model(data, offset, model_index)
                
                if model_info is None:
                    self.log(f"Failed to parse model {model_index}, stopping")
                    break
                
                models.append(model_info)
                
                # Check if we advanced
                if new_offset <= offset:
                    self.log(f"Offset didn't advance (was {offset}, now {new_offset}), stopping")
                    break
                
                offset = new_offset
                model_index += 1
                
                self.log(f"Model {model_index - 1} parsed successfully, next offset: {offset}")
                
                # Safety check - don't parse more than 200 models
                if model_index > 200:
                    self.log("Safety limit reached (200 models), stopping")
                    break
            
            self.log(f"Parsing complete: {len(models)} models found")
            return models
            
        except Exception as e:
            self.log(f"Error parsing COL file: {str(e)}")
            return []
    
    def parse_single_model(self, data, offset, model_index): #vers 1
        """Parse single COL model - WORKING VERSION"""
        try:
            # Check for valid COL signature
            if offset + 8 > len(data):
                return None, offset
            
            signature = data[offset:offset+4]
            if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                self.log(f"Invalid signature at offset {offset}: {signature}")
                return None, offset
            
            # Read model size
            model_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            total_model_size = model_size + 8
            
            if offset + total_model_size > len(data):
                self.log(f"Model size exceeds data bounds: need {total_model_size}, have {len(data) - offset}")
                return None, offset
            
            # Determine COL version
            if signature == b'COLL':
                version = 1
            elif signature == b'COL\x02':
                version = 2
            elif signature == b'COL\x03':
                version = 3
            elif signature == b'COL\x04':
                version = 4
            else:
                version = 1
            
            # Parse model data
            model_data = data[offset+8:offset+total_model_size]
            model_info = {
                'index': model_index,
                'version': version,
                'size': model_size,
                'offset': offset,
                'signature': signature,
                'spheres': 0,
                'boxes': 0,
                'vertices': 0,
                'faces': 0,
                'collision_types': []
            }
            
            # Parse collision data based on version
            if version == 1:
                self._parse_col1_collision_data(model_data, model_info)
            else:
                self._parse_col23_collision_data(model_data, model_info)
            
            return model_info, offset + total_model_size
            
        except Exception as e:
            self.log(f"Error parsing single model: {str(e)}")
            return None, offset
    
    def _is_multi_model_archive(self, data): #vers 1
        """Check if this is a multi-model COL archive"""
        try:
            if len(data) < 16:
                return False
            
            # Check for multiple COL signatures
            signatures_found = 0
            offset = 0
            
            while offset < len(data) - 8:
                chunk = data[offset:offset+4]
                if chunk in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                    signatures_found += 1
                    if signatures_found > 1:
                        return True
                    
                    # Skip past this model
                    try:
                        size = struct.unpack('<I', data[offset+4:offset+8])[0]
                        offset += size + 8
                    except:
                        break
                else:
                    offset += 1
            
            return False
            
        except Exception as e:
            self.log(f"Error checking multi-model archive: {str(e)}")
            return False
    
    def _parse_multi_model_archive(self, data): #vers 1
        """Parse multi-model COL archive"""
        models = []
        offset = 0
        model_index = 0
        
        while offset < len(data) - 8:
            chunk = data[offset:offset+4]
            if chunk in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                model_info, new_offset = self.parse_single_model(data, offset, model_index)
                if model_info:
                    models.append(model_info)
                    model_index += 1
                
                if new_offset <= offset:
                    break
                offset = new_offset
            else:
                offset += 1
        
        return models
    
    def _parse_col1_collision_data(self, data, model_info): #vers 1
        """Parse COL1 collision data"""
        try:
            if len(data) < 40:
                return
            
            # COL1 structure parsing
            offset = 0
            
            # Skip bounding info (40 bytes)
            offset += 40
            
            # Read sphere count
            if offset + 4 <= len(data):
                sphere_count = struct.unpack('<I', data[offset:offset+4])[0]
                model_info['spheres'] = sphere_count
                offset += 4 + (sphere_count * 20)  # Each sphere is 20 bytes
            
            # Read box count
            if offset + 4 <= len(data):
                box_count = struct.unpack('<I', data[offset:offset+4])[0]
                model_info['boxes'] = box_count
                offset += 4 + (box_count * 72)  # Each box is 72 bytes
            
            # Read vertex count
            if offset + 4 <= len(data):
                vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
                model_info['vertices'] = vertex_count
                offset += 4 + (vertex_count * 12)  # Each vertex is 12 bytes
            
            # Read face count
            if offset + 4 <= len(data):
                face_count = struct.unpack('<I', data[offset:offset+4])[0]
                model_info['faces'] = face_count
            
            # Determine collision types
            collision_types = []
            if model_info['spheres'] > 0:
                collision_types.append(f"Spheres ({model_info['spheres']})")
            if model_info['boxes'] > 0:
                collision_types.append(f"Boxes ({model_info['boxes']})")
            if model_info['vertices'] > 0:
                collision_types.append(f"Mesh ({model_info['vertices']} verts)")
            
            model_info['collision_types'] = collision_types
            
        except Exception as e:
            self.log(f"Error parsing COL1 collision data: {str(e)}")
    
    def _parse_col23_collision_data(self, data, model_info): #vers 1
        """Parse COL2/COL3 collision data"""
        try:
            if len(data) < 40:
                return
            
            # COL2/3 structure parsing
            offset = 0
            
            # Skip bounding info (40 bytes)
            offset += 40
            
            # Read sphere count
            if offset + 4 <= len(data):
                sphere_count = struct.unpack('<I', data[offset:offset+4])[0]
                model_info['spheres'] = sphere_count
                offset += 4 + (sphere_count * 20)
            
            # Read box count  
            if offset + 4 <= len(data):
                box_count = struct.unpack('<I', data[offset:offset+4])[0]
                model_info['boxes'] = box_count
                offset += 4 + (box_count * 72)
            
            # Read vertex count
            if offset + 4 <= len(data):
                vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
                model_info['vertices'] = vertex_count
                offset += 4 + (vertex_count * 12)
            
            # Read face count
            if offset + 4 <= len(data):
                face_count = struct.unpack('<I', data[offset:offset+4])[0]
                model_info['faces'] = face_count
            
            # Determine collision types
            collision_types = []
            if model_info['spheres'] > 0:
                collision_types.append(f"Spheres ({model_info['spheres']})")
            if model_info['boxes'] > 0:
                collision_types.append(f"Boxes ({model_info['boxes']})")
            if model_info['vertices'] > 0:
                collision_types.append(f"Mesh ({model_info['vertices']} verts)")
            
            model_info['collision_types'] = collision_types
            
        except Exception as e:
            self.log(f"Error parsing COL2/3 collision data: {str(e)}")
    
    def clear_debug_log(self): #vers 1
        """Clear debug log messages"""
        self.log_messages = []
    
    def get_debug_log(self): #vers 1
        """Get debug log messages"""
        return self.log_messages
    
    def format_collision_types(self, model_info): #vers 1
        """Format collision types for display"""
        if not model_info.get('collision_types'):
            return "No collision"
        return ", ".join(model_info['collision_types'])
    
    def get_model_stats_by_index(self, models, index): #vers 1
        """Get model statistics by index"""
        if not models or index >= len(models):
            return None
        return models[index]


# Helper functions for table population
def format_model_collision_types(model_info): #vers 1
    """Format model collision types for display"""
    if not isinstance(model_info, dict):
        return "Unknown"
    
    collision_types = model_info.get('collision_types', [])
    if not collision_types:
        return "No collision"
    
    return ", ".join(collision_types)


def get_model_collision_stats(model_info): #vers 1
    """Get collision statistics from model info"""
    if not isinstance(model_info, dict):
        return "N/A"
    
    stats = []
    if model_info.get('spheres', 0) > 0:
        stats.append(f"S:{model_info['spheres']}")
    if model_info.get('boxes', 0) > 0:
        stats.append(f"B:{model_info['boxes']}")
    if model_info.get('vertices', 0) > 0:
        stats.append(f"V:{model_info['vertices']}")
    if model_info.get('faces', 0) > 0:
        stats.append(f"F:{model_info['faces']}")
    
    return " | ".join(stats) if stats else "No data"


def parse_col_file_with_debug(file_path, debug=False): #vers 1
    """Parse COL file with debug output"""
    parser = COLParser(debug=debug)
    models = parser.parse_col_file_structure(file_path)
    
    if debug and debug_available:
        img_debugger.debug(f"Parsed {len(models)} models from {file_path}")
        for i, model in enumerate(models):
            img_debugger.debug(f"Model {i}: {format_model_collision_types(model)}")
    
    return models, parser.get_debug_log()


# Export main functions
__all__ = [
    'COLParser',
    'load_col_file_safely',
    'setup_col_tab_integration',
    'reset_table_styling',
    'format_model_collision_types',
    'get_model_collision_stats',
    'parse_col_file_with_debug'
]
