#this belongs in components/ col_parsing_functions.py - Version: 2
# X-Seti - July11 2025 - Img Factory 1.5

"""
COL Parser - Complete collision file parsing with debug control
Handles all COL format versions (COL1/COL2/COL3/COL4) with detailed logging
"""

import struct
import os
from typing import Dict, List, Tuple, Optional
from components.col_core_classes import is_col_debug_enabled

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

        # Populate table with enhanced COL data
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

def _populate_col_table_enhanced(main_window, col_file):
    """Populate table using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager

        display_manager = COLDisplayManager(main_window)
        display_manager.populate_col_table(col_file)
        main_window.log_message("✅ Enhanced COL table populated")

    except Exception as e:
        main_window.log_message(f"❌ Enhanced table population failed: {str(e)}")
        raise

def _update_col_info_bar_enhanced(main_window, col_file, file_path):
    """Update info bar using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager

        display_manager = COLDisplayManager(main_window)
        display_manager.update_col_info_bar(col_file, file_path)
        main_window.log_message("✅ Enhanced info bar updated")

    except Exception as e:
        main_window.log_message(f"❌ Enhanced info bar update failed: {str(e)}")
        raise

def _validate_col_file(main_window, file_path):
    """Validate COL file before loading"""
    if not os.path.exists(file_path):
        main_window.log_message(f"❌ COL file not found: {file_path}")
        return False

    if not os.access(file_path, os.R_OK):
        main_window.log_message(f"❌ Cannot read COL file: {file_path}")
        return False

    file_size = os.path.getsize(file_path)
    if file_size < 32:
        main_window.log_message(f"❌ COL file too small ({file_size} bytes)")
        return False

    return True

def _setup_col_tab(main_window, file_path):
    """Setup or reuse tab for COL file"""
    try:
        current_index = main_window.main_tab_widget.currentIndex()

        # Check if current tab is empty
        if not hasattr(main_window, 'open_files') or current_index not in main_window.open_files:
            main_window.log_message("Using current tab for COL file")
        else:
            main_window.log_message("Creating new tab for COL file")
            if hasattr(main_window, 'close_manager'):
                main_window.close_manager.create_new_tab()
                current_index = main_window.main_tab_widget.currentIndex()
            else:
                main_window.log_message("⚠️ Close manager not available")
                return None

        # Setup tab info
        file_name = os.path.basename(file_path)
        file_name_clean = file_name[:-4] if file_name.lower().endswith('.col') else file_name
        tab_name = f"🛡️ {file_name_clean}"

        # Store tab info
        if not hasattr(main_window, 'open_files'):
            main_window.open_files = {}

        main_window.open_files[current_index] = {
            'type': 'COL',
            'file_path': file_path,
            'file_object': None,
            'tab_name': tab_name
        }

        # Update tab name
        main_window.main_tab_widget.setTabText(current_index, tab_name)

        return current_index

    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
        return None

def _load_col_file(main_window, file_path):
    """Load COL file object"""
    try:
        from components.col_core_classes import COLFile

        main_window.log_message("📖 Loading COL file data...")
        col_file = COLFile(file_path)

        if not col_file.load():
            error_details = getattr(col_file, 'load_error', 'Unknown loading error')
            main_window.log_message(f"❌ Failed to load COL file: {error_details}")
            return None

        return col_file

    except ImportError as e:
        main_window.log_message(f"❌ COL core classes not available: {str(e)}")
        return None
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return None

def _setup_col_table_structure(main_window):
    """Setup table structure for COL data display with enhanced usability"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return

        table = main_window.gui_layout.table

        # Configure table for COL data (7 columns)
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
        ])

        # Enable column dragging and resizing
        from PyQt6.QtWidgets import QHeaderView
        header = table.horizontalHeader()
        header.setSectionsMovable(True)  # Allow dragging columns
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # Allow resizing
        header.setDefaultSectionSize(120)  # Default column width

        # Set specific column widths for better visibility
        table.setColumnWidth(0, 150)  # Model name - wider for readability
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 100)  # Size
        table.setColumnWidth(3, 80)   # Surfaces
        table.setColumnWidth(4, 80)   # Vertices
        table.setColumnWidth(5, 200)  # Collision - wider for collision types
        table.setColumnWidth(6, 80)   # Status

        # Enable alternating row colors with light blue theme
        table.setAlternatingRowColors(True)

        # Set object name for specific styling
        table.setObjectName("col_table")

        # Apply COL-specific styling ONLY to this table
        col_table_style = """
            QTableWidget#col_table {
                alternate-background-color: #E3F2FD;
                background-color: #F5F5F5;
                gridline-color: #CCCCCC;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            QTableWidget#col_table::item {
                padding: 4px;
                border-bottom: 1px solid #E0E0E0;
                background-color: transparent;
            }
            QTableWidget#col_table::item:alternate {
                background-color: #E3F2FD;
            }
            QTableWidget#col_table::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """

        # Apply header styling separately to avoid affecting other headers
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

        main_window.log_message("🔧 Table structure configured for COL data with scoped styling")

    except Exception as e:
        main_window.log_message(f"⚠️ Error setting up table structure: {str(e)}")


class COLParser:
    """Complete COL file parser with debugging support"""
    
    def __init__(self, debug=None):
        """Initialize COL parser with debug control"""
        # Check global debug setting if not specified
        if debug is None:
            self.debug = is_col_debug_enabled()
        else:
            self.debug = debug
        
        self.log_messages = []
    
    def log(self, message):
        """Log debug message only if global debug is enabled"""
        # Always check global debug setting
        if is_col_debug_enabled():
            print(f"🔍 COLParser: {message}")
        self.log_messages.append(message)
    
    def set_debug(self, enabled):
        """Update debug setting - now syncs with global setting"""
        self.debug = enabled
        # Also update global setting to keep them in sync
        from components.col_core_classes import set_col_debug_enabled
        set_col_debug_enabled(enabled)
    
    def parse_col_file_structure(self, file_path):
        """Parse complete COL file and return structure info for all models"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            self.log(f"Parsing COL file: {os.path.basename(file_path)} ({len(data)} bytes)")

            # CRITICAL FIX: First check if this is a multi-model COL archive
            if self._is_multi_model_archive(data):
                return self._parse_multi_model_archive(data)

            # Single model parsing (original approach)
            models = []
            offset = 0
            model_index = 0

            while offset < len(data):
                self.log(f"\n--- Model {model_index} at offset {offset} ---")

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

            self.log(f"\nParsing complete: {len(models)} models found")
            return models

        except Exception as e:
            self.log(f"Error parsing COL file: {str(e)}")
            return []
    
    def _parse_col23_info(self, data, model_index, signature):
        """Parse COL version 2/3 model info"""
        try:
            if len(data) < 60:
                return None

            offset = 0

            # Skip bounding sphere (16 bytes)
            offset += 16

            # Skip bounding box (24 bytes)
            offset += 24

            # Read counts
            if offset + 16 <= len(data):
                num_spheres, num_boxes, num_vertices, num_faces = struct.unpack('<IIII', data[offset:offset+16])
                offset += 16
            else:
                num_spheres = num_boxes = num_vertices = num_faces = 0

            # Try to find name in the data
            name = f"COL_{signature.decode('ascii', errors='ignore')}_Model_{model_index}"

            total_elements = num_spheres + num_boxes + num_faces

            return {
                'name': name,
                'model_id': model_index,
                'type': signature.decode('ascii', errors='ignore'),
                'sphere_count': num_spheres,
                'box_count': num_boxes,
                'vertex_count': num_vertices,
                'face_count': num_faces,
                'total_elements': total_elements,
                'estimated_size': len(data)
            }

        except Exception as e:
            self.log(f"Error parsing COL2/3 info: {str(e)}")
            return None

    def parse_single_model(self, data, offset, model_index):
        """Parse single COL model at given offset"""
        try:
            if offset + 8 > len(data):
                self.log(f"Not enough data for signature at offset {offset}")
                return None, offset

            # Read signature
            signature = data[offset:offset+4]

            self.log(f"Found {signature} at offset {offset}")

            if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                self.log(f"Invalid signature: {signature}")
                # Try to find next valid signature
                next_offset = self._find_next_signature(data, offset + 1)
                if next_offset > 0:
                    return None, next_offset
                else:
                    return None, len(data)  # End of data

            # Read file size
            try:
                file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
                self.log(f"Model size: {file_size} bytes")
            except struct.error:
                self.log("Failed to read file size")
                return None, offset + 8

            # Validate size
            total_size = file_size + 8
            if offset + total_size > len(data):
                self.log(f"Model extends beyond file (needs {total_size}, available {len(data) - offset})")
                return None, len(data)  # Skip to end

            # Extract model data
            model_data = data[offset + 8:offset + total_size]

            # Parse based on version
            if signature == b'COLL':
                model_info = self._parse_col1_info(model_data, model_index)
            else:
                model_info = self._parse_col23_info(model_data, model_index, signature)

            if model_info:
                model_info['file_offset'] = offset
                model_info['file_size'] = file_size
                model_info['total_size'] = total_size
                model_info['version'] = signature.decode('ascii', errors='ignore')

            return model_info, offset + total_size

        except Exception as e:
            self.log(f"Error parsing model at offset {offset}: {str(e)}")
            return None, offset + 64  # Skip ahead to try next model

    def _find_next_signature(self, data, start_offset):
        """Find next valid COL signature in data"""
        signatures = [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']

        for i in range(start_offset, len(data) - 4):
            for sig in signatures:
                if data[i:i+4] == sig:
                    self.log(f"Found next signature {sig} at offset {i}")
                    return i

        return -1  # No signature found

    def _is_multi_model_archive(self, data):
        """Check if this is a multi-model COL archive"""
        if len(data) < 32:
            return False

        # Look for multiple signatures
        signature_count = 0
        offset = 0

        while offset < len(data) - 8:
            signature = data[offset:offset+4]
            if signature in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                signature_count += 1
                if signature_count > 1:
                    self.log("Detected multi-model COL archive")
                    return True

                # Skip past this model
                try:
                    file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
                    offset += file_size + 8
                except:
                    break
            else:
                offset += 1

        return False

   def _parse_col1_info(self, data, model_index):
        """Parse COL version 1 model info"""
        try:
            if len(data) < 40:
                return None

            offset = 0

            # Name (22 bytes)
            name_bytes = data[offset:offset+22]
            name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22

            # Model ID (4 bytes)
            model_id = struct.unpack('<I', data[offset:offset+4])[0] if len(data) >= offset + 4 else 0
            offset += 4

            if not name:
                name = f"COL1_Model_{model_id or model_index}"

            return {
                'name': name,
                'model_id': model_id,
                'type': 'COL1',
                'sphere_count': 0,  # COL1 doesn't have detailed counts
                'box_count': 0,
                'vertex_count': 0,
                'face_count': 0,
                'total_elements': 1,
                'estimated_size': len(data)
            }

        except Exception as e:
            self.log(f"Error parsing COL1 info: {str(e)}")
            return None

    def _parse_multi_model_archive(self, data):
        """Parse multi-model COL archive"""
        self.log("Parsing as multi-model archive")
        models = []
        offset = 0
        model_index = 0

        while offset < len(data) - 8:
            signature = data[offset:offset+4]

            if signature in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
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


    def parse_single_model(self, data, offset, model_index):
        """Parse a single COL model and return info + new offset"""
        try:
            start_offset = offset
            
            # Read signature
            if offset + 4 > len(data):
                return None, offset
            
            signature = data[offset:offset+4]
            self.log(f"Signature: {signature}")
            
            # Validate signature
            if signature not in [b'COLL', b'COL2', b'COL3', b'COL4']:
                self.log(f"Invalid signature: {signature}")
                return None, offset
            
            offset += 4
            
            # Read file size
            if offset + 4 > len(data):
                return None, offset
            
            file_size = struct.unpack('<I', data[offset:offset+4])[0]
            self.log(f"Declared size: {file_size}")
            offset += 4
            
            # Read model name (22 bytes)
            if offset + 22 > len(data):
                return None, offset
            
            name_bytes = data[offset:offset+22]
            model_name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            self.log(f"Model name: '{model_name}'")
            offset += 22
            
            # Read model ID (2 bytes)
            if offset + 2 > len(data):
                return None, offset
            
            model_id = struct.unpack('<H', data[offset:offset+2])[0]
            self.log(f"Model ID: {model_id}")
            offset += 2
            
            # Determine version from signature
            if signature == b'COLL':
                version = 'COL1'
            elif signature == b'COL2':
                version = 'COL2'
            elif signature == b'COL3':
                version = 'COL3'
            elif signature == b'COL4':
                version = 'COL4'
            else:
                version = 'UNKNOWN'
            
            # Parse collision data based on version
            collision_stats = self._parse_collision_data(data, offset, file_size - 28, version)
            
            # Calculate end offset
            end_offset = self._calculate_model_end_offset(data, start_offset, file_size)
            
            # Build model info dictionary
            model_info = {
                'name': model_name or f'Model_{model_index}',
                'model_id': model_id,
                'version': version,
                'size': file_size + 8,  # Include header
                'sphere_count': collision_stats.get('sphere_count', 0),
                'box_count': collision_stats.get('box_count', 0),
                'vertex_count': collision_stats.get('vertex_count', 0),
                'face_count': collision_stats.get('face_count', 0),
                'total_elements': collision_stats.get('total_elements', 0),
                'estimated_size': file_size + 8
            }
            
            self.log(f"Model parsed: {model_info['name']} (v{version}, {file_size + 8} bytes)")
            
            return model_info, end_offset
            
        except Exception as e:
            self.log(f"Error parsing model at offset {offset}: {str(e)}")
            return None, offset + 32  # Skip ahead to try next model
    
    def _parse_collision_data(self, data, offset, data_size, version):
        """Parse collision data and return statistics"""
        stats = {
            'sphere_count': 0,
            'box_count': 0,
            'vertex_count': 0,
            'face_count': 0,
            'total_elements': 0
        }
        
        try:
            if version == 'COL1':
                # COL1 has simpler structure
                # For now, estimate based on data size
                if data_size > 100:
                    stats['sphere_count'] = max(1, data_size // 200)
                    stats['total_elements'] = stats['sphere_count']
            else:
                # COL2/3/4 have more complex structure
                # For now, estimate based on data size
                if data_size > 200:
                    stats['vertex_count'] = max(10, data_size // 50)
                    stats['face_count'] = max(5, data_size // 100)
                    stats['total_elements'] = stats['vertex_count'] + stats['face_count']
            
            self.log(f"Collision stats: {stats}")
            
        except Exception as e:
            self.log(f"Error parsing collision data: {e}")
        
        return stats
    
    def _calculate_model_end_offset(self, data, start_offset, declared_size):
        """Calculate where this model ends"""
        try:
            return start_offset + declared_size + 8
        except Exception as e:
            self.log(f"Error calculating model end: {str(e)}")
            return start_offset + 800  # Safe fallback
    
    def get_model_stats_by_index(self, file_path, model_index):
        """Get statistics for a specific model by index"""
        models = self.parse_col_file_structure(file_path)

        if model_index < len(models):
            return models[model_index]
        else:
            self.log(f"Model index {model_index} not found (only {len(models)} models)")
            return {
                'sphere_count': 0,
                'box_count': 0,
                'vertex_count': 0,
                'face_count': 0,
                'total_elements': 0,
                'estimated_size': 64
            }

    def format_collision_types(self, stats):
        """Format collision types string from stats"""
        types = []
        if stats.get('sphere_count', 0) > 0:
            types.append(f"Spheres({stats['sphere_count']})")
        if stats.get('box_count', 0) > 0:
            types.append(f"Boxes({stats['box_count']})")
        if stats.get('face_count', 0) > 0:
            types.append(f"Mesh({stats['face_count']})")

        return ", ".join(types) if types else "None"

    def get_debug_log(self):
        """Get debug log messages"""
        return self.log_messages

    def clear_debug_log(self):
        """Clear debug log"""
        self.log_messages = []

# Convenience functions that respect global debug setting
def parse_col_file_with_debug(file_path, debug=None):
    """Parse COL file and return model statistics with optional debug output"""
    if debug is None:
        debug = is_col_debug_enabled()

    parser = COLParser(debug=debug)
    models = parser.parse_col_file_structure(file_path)

    # Only show debug log if global debug is enabled
    if is_col_debug_enabled() and debug:
        print("\n=== COL Parser Debug Log ===")
        for msg in parser.get_debug_log():
            print(msg)
        print("=== End Debug Log ===\n")

    return models

def get_model_collision_stats(file_path, model_index, debug=None):
    """Get collision statistics for a specific model"""
    if debug is None:
        debug = is_col_debug_enabled()

    parser = COLParser(debug=debug)
    return parser.get_model_stats_by_index(file_path, model_index)

def format_model_collision_types(stats):
    """Format collision types string"""
    parser = COLParser(debug=False)  # Never debug for formatting
    return parser.format_collision_types(stats)

# Export main classes and functions
__all__ = [
    'COLParser',
    'parse_col_file_with_debug',
    'get_model_collision_stats', 
    'format_model_collision_types'
]
