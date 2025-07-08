#this belongs in components/ col_display.py - Version: 1
# X-Seti - July08 2025 - COL Display Component for IMG Factory 1.5

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt
import os

class COLDisplayManager:
    """Manages COL data display in IMG Factory table"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.debug = True
    
    def populate_col_table(self, col_file):
        """Populate the main table with COL model data"""
        try:
            # Access the main table
            if not hasattr(self.main_window, 'gui_layout') or not hasattr(self.main_window.gui_layout, 'table'):
                self._log("⚠️ Main table not available")
                return False

            table = self.main_window.gui_layout.table
            
            # Configure table for COL data
            self._setup_col_table_headers(table)

            # Clear existing data
            table.setRowCount(0)
            
            if not hasattr(col_file, 'models') or not col_file.models:
                self._show_no_models_message(table)
                return True

            # Populate with COL models
            table.setRowCount(len(col_file.models))
            self._log(f"🔧 Populating table with {len(col_file.models)} COL models")

            for row, model in enumerate(col_file.models):
                self._populate_model_row(table, row, model)

            # Finalize table
            self._finalize_table_display(table)
            
            self._log(f"✅ COL table populated successfully")
            return True

        except Exception as e:
            self._log(f"❌ Error populating COL table: {str(e)}")
            return False
    
    def _setup_col_table_headers(self, table):
        """Setup table headers for COL display"""
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
        ])
    
    def _populate_model_row(self, table, row, model):
        """Populate a single model row in the table"""
        try:
            # Get model statistics
            stats = self._get_model_stats(model)
            
            # Debug log for first few models
            if row < 3 and self.debug:
                self._log(f"📊 Model {row+1} '{model.name}': {stats}")

            # Model name
            model_name = self._format_model_name(model, row)
            table.setItem(row, 0, QTableWidgetItem(model_name))
            
            # Model type (COL version)
            model_type = self._format_model_type(model)
            table.setItem(row, 1, QTableWidgetItem(model_type))
            
            # Model size
            model_size = self._calculate_model_size(model, stats)
            size_str = self._format_file_size(model_size)
            table.setItem(row, 2, QTableWidgetItem(size_str))
            
            # Surface count (total collision elements)
            surface_count = stats.get('total_elements', 0)
            table.setItem(row, 3, QTableWidgetItem(str(surface_count)))
            
            # Vertex count
            vertex_count = stats.get('vertices', 0)
            table.setItem(row, 4, QTableWidgetItem(str(vertex_count)))
            
            # Collision breakdown
            collision_info = self._format_collision_breakdown(stats)
            table.setItem(row, 5, QTableWidgetItem(collision_info))
            
            # Status
            table.setItem(row, 6, QTableWidgetItem("Loaded"))
            
            # Make all items read-only
            for col in range(7):
                item = table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        except Exception as e:
            self._log(f"⚠️ Error populating row {row}: {e}")
            # Set error row
            table.setItem(row, 0, QTableWidgetItem(f"Error_Model_{row+1}"))
            for col in range(1, 7):
                table.setItem(row, col, QTableWidgetItem("-"))
    
    def _get_model_stats(self, model):
        """Get model statistics (works with both original and enhanced models)"""
        if hasattr(model, 'get_stats') and callable(getattr(model, 'get_stats')):
            # Use existing get_stats method
            return model.get_stats()
        else:
            # Manual calculation for compatibility
            return {
                "spheres": len(getattr(model, 'spheres', [])),
                "boxes": len(getattr(model, 'boxes', [])), 
                "vertices": len(getattr(model, 'vertices', [])),
                "faces": len(getattr(model, 'faces', [])),
                "face_groups": len(getattr(model, 'face_groups', [])),
                "shadow_vertices": len(getattr(model, 'shadow_vertices', [])),
                "shadow_faces": len(getattr(model, 'shadow_faces', [])),
                "total_elements": (len(getattr(model, 'spheres', [])) + 
                                 len(getattr(model, 'boxes', [])) + 
                                 len(getattr(model, 'faces', [])))
            }
    
    def _format_model_name(self, model, row):
        """Format model name for display"""
        model_name = getattr(model, 'name', f"Model_{row+1}")
        if not model_name or model_name.strip() == "":
            model_name = f"Model_{row+1}"
        return str(model_name)
    
    def _format_model_type(self, model):
        """Format model type (COL version) for display"""
        version = getattr(model, 'version', None)
        if version and hasattr(version, 'name'):
            return f"COL {version.name.replace('COL_', '')}"
        elif version and hasattr(version, 'value'):
            return f"COL {version.value}"
        else:
            return "Collision"
    
    def _calculate_model_size(self, model, stats):
        """Calculate estimated model size in bytes"""
        try:
            size = 60  # Basic header
            
            # Accurate GTA COL format sizes
            size += stats.get('spheres', 0) * 20      # Spheres: center(12) + radius(4) + material(4)
            size += stats.get('boxes', 0) * 32        # Boxes: min(12) + max(12) + material(4) + flags(4)
            size += stats.get('vertices', 0) * 12     # Vertices: x,y,z coordinates (4 bytes each)
            size += stats.get('faces', 0) * 12        # Faces: 3 indices(6) + material(4) + flags(2)
            size += stats.get('face_groups', 0) * 8   # Face groups overhead
            size += stats.get('shadow_vertices', 0) * 12  # Shadow mesh (COL3)
            size += stats.get('shadow_faces', 0) * 12     # Shadow faces (COL3)
            
            return max(size, 60)  # Minimum header size
            
        except Exception as e:
            self._log(f"⚠️ Error calculating model size: {e}")
            return 60
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024*1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024*1024):.1f} MB"
    
    def _format_collision_breakdown(self, stats):
        """Format collision breakdown (S:spheres B:boxes F:faces)"""
        spheres = stats.get('spheres', 0)
        boxes = stats.get('boxes', 0)
        faces = stats.get('faces', 0)
        return f"S:{spheres} B:{boxes} F:{faces}"
    
    def _show_no_models_message(self, table):
        """Show message when no models are found"""
        table.setRowCount(1)
        table.setItem(0, 0, QTableWidgetItem("No models found"))
        for col in range(1, 7):
            table.setItem(0, col, QTableWidgetItem("-"))
    
    def _finalize_table_display(self, table):
        """Finalize table display settings"""
        # Resize columns to content
        table.resizeColumnsToContents()
        
        # Select first row
        if table.rowCount() > 0:
            table.selectRow(0)
    
    def update_col_info_bar(self, col_file, file_path):
        """Update the info bar with COL file information"""
        try:
            gui_layout = self.main_window.gui_layout
            
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
                size_str = self._format_file_size(file_size)
                gui_layout.file_size_label.setText(f"Size: {size_str}")
            
            # Update format version
            if hasattr(gui_layout, 'format_version_label'):
                # Determine predominant COL version
                versions = []
                if hasattr(col_file, 'models'):
                    for model in col_file.models:
                        version = getattr(model, 'version', None)
                        if version:
                            if hasattr(version, 'value'):
                                versions.append(version.value)
                            elif hasattr(version, 'name'):
                                versions.append(int(version.name.replace('COL_', '')))
                
                if versions:
                    most_common_version = max(set(versions), key=versions.count)
                    gui_layout.format_version_label.setText(f"Format: COL v{most_common_version}")
                else:
                    gui_layout.format_version_label.setText(f"Format: COL")
            
            self._log("✅ Updated info bar for COL file")
            return True

        except Exception as e:
            self._log(f"⚠️ Error updating info bar: {e}")
            return False
    
    def _log(self, message):
        """Log message to main window"""
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(message)
        elif self.debug:
            print(message)

class COLTableFormatter:
    """Utility class for formatting COL data for table display"""
    
    @staticmethod
    def format_collision_summary(model):
        """Create a summary string of collision data"""
        stats = COLDisplayManager._get_model_stats(None, model) if hasattr(COLDisplayManager, '_get_model_stats') else {}
        
        total = stats.get('total_elements', 0)
        if total == 0:
            return "No collision data"
        
        parts = []
        if stats.get('spheres', 0) > 0:
            parts.append(f"{stats['spheres']} spheres")
        if stats.get('boxes', 0) > 0:
            parts.append(f"{stats['boxes']} boxes")
        if stats.get('faces', 0) > 0:
            parts.append(f"{stats['faces']} faces")
        
        return ", ".join(parts) if parts else f"{total} elements"
    
    @staticmethod
    def get_collision_complexity_level(model):
        """Get collision complexity level (Simple/Medium/Complex)"""
        try:
            stats = COLDisplayManager._get_model_stats(None, model) if hasattr(COLDisplayManager, '_get_model_stats') else {}
            total = stats.get('total_elements', 0)
            
            if total == 0:
                return "None"
            elif total <= 10:
                return "Simple"
            elif total <= 50:
                return "Medium"
            else:
                return "Complex"
                
        except Exception:
            return "Unknown"
    
    @staticmethod
    def format_bounding_info(model):
        """Format bounding box information"""
        try:
            if hasattr(model, 'bounding_box') and model.bounding_box:
                center = model.bounding_box.center
                radius = model.bounding_box.radius
                return f"Center: ({center.x:.1f}, {center.y:.1f}, {center.z:.1f}), Radius: {radius:.1f}"
            else:
                return "No bounding data"
        except Exception:
            return "Invalid bounding data"

# Factory function for easy integration
def create_col_display_manager(main_window):
    """Create a COL display manager for the given main window"""
    return COLDisplayManager(main_window)

# Convenience functions for backward compatibility
def populate_col_table(main_window, col_file):
    """Convenience function to populate COL table"""
    display_manager = COLDisplayManager(main_window)
    return display_manager.populate_col_table(col_file)

def update_col_info_bar(main_window, col_file, file_path):
    """Convenience function to update COL info bar"""
    display_manager = COLDisplayManager(main_window)
    return display_manager.update_col_info_bar(col_file, file_path)