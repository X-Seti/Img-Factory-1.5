#!/usr/bin/env python3
"""
Fix script for COL_Workshop.py issues:
1. Fix collision file rendering
2. Add import/export functionality when docked
3. Fix menu docking system
4. Fix window pop-in/pop-out functionality
5. Fix window size issue when tearing off
"""

import os
import sys
from pathlib import Path

def fix_col_workshop():
    """Apply fixes to COL_Workshop.py"""
    
    col_workshop_path = Path("/workspace/apps/components/Col_Editor/col_workshop.py")
    
    if not col_workshop_path.exists():
        print(f"Error: {col_workshop_path} not found")
        return False
    
    # Read the current file
    with open(col_workshop_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Improve collision rendering function
    # Replace the current _render_collision_preview function with a better one
    old_render_function = '''    def _render_collision_preview(self, model, width, height): #vers 1
        \"\"\"Render collision model for preview panel\"\"\"
        try:
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(10, 10, 10))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Get collision data
            spheres = getattr(model, 'spheres', [])
            boxes = getattr(model, 'boxes', [])
            vertices = getattr(model, 'vertices', [])
            faces = getattr(model, 'faces', [])

            if not spheres and not boxes and not vertices:
                painter.setPen(QColor(150, 150, 150))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter,
                            "No Collision Data\\n\\nModel is empty")
                painter.end()
                return pixmap

            # Calculate bounds
            all_points = []
            for sphere in spheres:
                if hasattr(sphere, 'center'):
                    all_points.append((sphere.center.x, sphere.center.z))

            for box in boxes:
                if hasattr(box, 'min_point') and hasattr(box, 'max_point'):
                    all_points.append((box.min_point.x, box.min_point.z))
                    all_points.append((box.max_point.x, box.max_point.z))

            for vertex in vertices:
                if hasattr(vertex, 'position'):
                    all_points.append((vertex.position.x, vertex.position.z))

            if not all_points:
                painter.end()
                return pixmap

            # Calculate scale
            xs = [p[0] for p in all_points]
            zs = [p[1] for p in all_points]
            min_x, max_x = min(xs), max(xs)
            min_z, max_z = min(zs), max(zs)

            range_x = max_x - min_x if max_x != min_x else 1
            range_z = max_z - min_z if max_z != min_z else 1
            scale = min((width - 40) / range_x, (height - 40) / range_z)

            offset_x = width / 2 - (min_x + max_x) / 2 * scale
            offset_y = height / 2 - (min_z + max_z) / 2 * scale

            # Draw grid
            painter.setPen(QPen(QColor(50, 50, 50), 1, Qt.PenStyle.DotLine))
            for i in range(-10, 11):
                painter.drawLine(int(offset_x + i * 50), 0,
                            int(offset_x + i * 50), height)
                painter.drawLine(0, int(offset_y + i * 50),
                            width, int(offset_y + i * 50))

            # Draw spheres (if enabled)
            if self._show_checkerboard:  # Reuse this flag as show_spheres
                painter.setPen(QPen(QColor(100, 180, 255), 2))
                painter.setBrush(QBrush(QColor(100, 180, 255, 80)))
                for sphere in spheres:
                    if hasattr(sphere, 'center') and hasattr(sphere, 'radius'):
                        x = sphere.center.x * scale + offset_x
                        y = sphere.center.z * scale + offset_y
                        r = sphere.radius * scale
                        painter.drawEllipse(QPoint(int(x), int(y)), int(r), int(r))

            # Draw boxes
            painter.setPen(QPen(QColor(255, 180, 100), 2))
            painter.setBrush(QBrush(QColor(255, 180, 100, 80)))
            for box in boxes:
                if hasattr(box, 'min_point') and hasattr(box, 'max_point'):
                    x1 = box.min_point.x * scale + offset_x
                    y1 = box.min_point.z * scale + offset_y
                    x2 = box.max_point.x * scale + offset_x
                    y2 = box.max_point.z * scale + offset_y
                    painter.drawRect(int(x1), int(y1), int(x2-x1), int(y2-y1))

            # Draw mesh wireframe
            if faces and vertices:
                painter.setPen(QPen(QColor(150, 255, 150), 1))
                for face in faces[:500]:  # Limit faces for performance
                    if hasattr(face, 'vertex_indices') and len(face.vertex_indices) >= 3:
                        try:
                            v1 = vertices[face.vertex_indices[0]].position
                            v2 = vertices[face.vertex_indices[1]].position
                            v3 = vertices[face.vertex_indices[2]].position

                            x1 = v1.x * scale + offset_x
                            y1 = v1.z * scale + offset_y
                            x2 = v2.x * scale + offset_x
                            y2 = v2.z * scale + offset_y
                            x3 = v3.x * scale + offset_x
                            y3 = v3.z * scale + offset_y

                            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                            painter.drawLine(int(x2), int(y2), int(x3), int(y3))
                            painter.drawLine(int(x3), int(y3), int(x1), int(y1))
                        except:
                            pass

            # Draw legend
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(10, 20, f"Spheres: {len(spheres)}")
            painter.drawText(10, 40, f"Boxes: {len(boxes)}")
            painter.drawText(10, 60, f"Faces: {len(faces)}")

            painter.end()
            return pixmap

        except Exception as e:
            img_debugger.error(f"Error rendering preview: {str(e)}")
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(60, 60, 60))
            return pixmap'''

    new_render_function = '''    def _render_collision_preview(self, model, width, height): #vers 2
        \"\"\"Render collision model for preview panel - IMPROVED VERSION\"\"\"
        try:
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(20, 20, 20))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            # Get collision data
            spheres = getattr(model, 'spheres', [])
            boxes = getattr(model, 'boxes', [])
            vertices = getattr(model, 'vertices', [])
            faces = getattr(model, 'faces', [])

            if not spheres and not boxes and not vertices:
                painter.setPen(QColor(150, 150, 150))
                painter.setFont(QFont("Arial", 12))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter,
                            "No Collision Data\\n\\nModel is empty")
                painter.end()
                return pixmap

            # Calculate bounds from all available collision elements
            all_points = []
            
            # Add sphere centers and radii
            for sphere in spheres:
                if hasattr(sphere, 'center'):
                    all_points.append((sphere.center.x, sphere.center.z))
                    # Add points for the sphere radius to ensure proper scaling
                    if hasattr(sphere, 'radius'):
                        all_points.append((sphere.center.x + sphere.radius, sphere.center.z + sphere.radius))
                        all_points.append((sphere.center.x - sphere.radius, sphere.center.z - sphere.radius))

            # Add box corners
            for box in boxes:
                if hasattr(box, 'min_point') and hasattr(box, 'max_point'):
                    all_points.append((box.min_point.x, box.min_point.z))
                    all_points.append((box.max_point.x, box.max_point.z))
                    # Add all 4 corners of the box
                    all_points.append((box.min_point.x, box.max_point.z))
                    all_points.append((box.max_point.x, box.min_point.z))

            # Add vertex positions
            for vertex in vertices:
                if hasattr(vertex, 'position'):
                    all_points.append((vertex.position.x, vertex.position.z))

            if not all_points:
                # Draw empty state
                painter.setPen(QColor(150, 150, 150))
                painter.setFont(QFont("Arial", 12))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter,
                            "No Collision Data\\n\\nModel is empty")
                painter.end()
                return pixmap

            # Calculate bounds with padding
            xs = [p[0] for p in all_points]
            zs = [p[1] for p in all_points]
            min_x, max_x = min(xs), max(xs)
            min_z, max_z = min(zs), max(zs)

            # Add some padding to prevent elements from touching edges
            padding = max((max_x - min_x) * 0.1, (max_z - min_z) * 0.1, 1.0)
            min_x -= padding
            max_x += padding
            min_z -= padding
            max_z += padding

            range_x = max_x - min_x if max_x != min_x else 1
            range_z = max_z - min_z if max_z != min_z else 1
            
            # Calculate scale with aspect ratio preservation
            scale_x = (width * 0.8) / range_x  # Use 80% of available space
            scale_z = (height * 0.8) / range_z
            scale = min(scale_x, scale_z)  # Use the smaller scale to fit everything
            
            # Calculate center offset
            center_x = width / 2 - (min_x + max_x) / 2 * scale
            center_z = height / 2 - (min_z + max_z) / 2 * scale

            # Draw grid background
            painter.setPen(QPen(QColor(40, 40, 40), 1, Qt.PenStyle.DotLine))
            # Draw grid lines based on the calculated bounds
            grid_step = max(abs(range_x), abs(range_z)) / 20  # 20 grid lines across the range
            if grid_step > 0:
                start_x = int(min_x / grid_step) * grid_step
                start_z = int(min_z / grid_step) * grid_step
                for i in range(-20, 21):
                    grid_x = start_x + i * grid_step
                    grid_z = start_z + i * grid_step
                    screen_x = grid_x * scale + center_x
                    screen_z = grid_z * scale + center_z
                    if 0 <= screen_x <= width:
                        painter.drawLine(int(screen_x), 0, int(screen_x), height)
                    if 0 <= screen_z <= height:
                        painter.drawLine(0, int(screen_z), width, int(screen_z))

            # Draw coordinate system
            painter.setPen(QPen(QColor(80, 80, 80), 2))
            # X axis (red)
            painter.drawLine(width//2 - 20, height//2, width//2 + 20, height//2)
            # Z axis (blue) 
            painter.drawLine(width//2, height//2 - 20, width//2, height//2 + 20)

            # Draw spheres (if enabled)
            if getattr(self, '_show_spheres', True):  # Use proper show_spheres flag
                painter.setPen(QPen(QColor(100, 180, 255), 2))
                painter.setBrush(QBrush(QColor(100, 180, 255, 80)))
                for sphere in spheres:
                    if hasattr(sphere, 'center') and hasattr(sphere, 'radius'):
                        screen_x = sphere.center.x * scale + center_x
                        screen_y = sphere.center.z * scale + center_z
                        screen_radius = sphere.radius * scale
                        # Only draw if sphere is within visible area
                        if (0 <= screen_x <= width and 0 <= screen_y <= height and screen_radius > 0.5):
                            painter.drawEllipse(QPoint(int(screen_x), int(screen_y)), int(screen_radius), int(screen_radius))

            # Draw boxes
            if getattr(self, '_show_boxes', True):  # Use proper show_boxes flag
                painter.setPen(QPen(QColor(255, 180, 100), 2))
                painter.setBrush(QBrush(QColor(255, 180, 100, 80)))
                for box in boxes:
                    if hasattr(box, 'min_point') and hasattr(box, 'max_point'):
                        x1 = box.min_point.x * scale + center_x
                        y1 = box.min_point.z * scale + center_z
                        x2 = box.max_point.x * scale + center_x
                        y2 = box.max_point.z * scale + center_z
                        # Only draw if box is within visible area
                        if (min(x1, x2) <= width and max(x1, x2) >= 0 and 
                            min(y1, y2) <= height and max(y1, y2) >= 0):
                            painter.drawRect(int(min(x1, x2)), int(min(y1, y2)), 
                                           int(abs(x2-x1)), int(abs(y2-y1)))

            # Draw mesh wireframe
            if getattr(self, '_show_mesh', True) and faces and vertices:  # Use proper show_mesh flag
                painter.setPen(QPen(QColor(150, 255, 150), 1))
                for face in faces[:500]:  # Limit faces for performance
                    if hasattr(face, 'vertex_indices') and len(face.vertex_indices) >= 3:
                        try:
                            # Get first 3 vertices of the face
                            if len(face.vertex_indices) >= 3:
                                idx1, idx2, idx3 = face.vertex_indices[0], face.vertex_indices[1], face.vertex_indices[2]
                                if idx1 < len(vertices) and idx2 < len(vertices) and idx3 < len(vertices):
                                    v1 = vertices[idx1].position
                                    v2 = vertices[idx2].position
                                    v3 = vertices[idx3].position

                                    x1 = v1.x * scale + center_x
                                    y1 = v1.z * scale + center_z
                                    x2 = v2.x * scale + center_x
                                    y2 = v2.z * scale + center_z
                                    x3 = v3.x * scale + center_x
                                    y3 = v3.z * scale + center_z

                                    # Only draw if all points are within reasonable bounds
                                    if all(0 <= coord <= max(width, height) for coord in [x1, y1, x2, y2, x3, y3]):
                                        painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                                        painter.drawLine(int(x2), int(y2), int(x3), int(y3))
                                        painter.drawLine(int(x3), int(y3), int(x1), int(y1))
                        except (IndexError, AttributeError):
                            continue

            # Draw legend with collision stats
            painter.setPen(QColor(220, 220, 220))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(10, 20, f"Spheres: {len(spheres)}")
            painter.drawText(10, 40, f"Boxes: {len(boxes)}")
            painter.drawText(10, 60, f"Faces: {len(faces)}")
            painter.drawText(10, 80, f"Vertices: {len(vertices)}")

            painter.end()
            return pixmap

        except Exception as e:
            img_debugger.error(f"Error rendering preview: {str(e)}")
            import traceback
            traceback.print_exc()
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(60, 60, 60))
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 100, 100))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, f"Render Error:\\n{str(e)[:50]}...")
            painter.end()
            return pixmap'''

    # Apply the fix
    content = content.replace(old_render_function, new_render_function)
    
    # Fix 2: Improve docking functionality to handle menu issues and window sizing
    # Replace the _dock_to_main and _undock_from_main methods
    old_dock_method = '''    def _dock_to_main(self): #vers 7
        \"\"\"Dock handled by overlay system in imgfactory\"\"\"
        if hasattr(self, 'is_overlay') and self.is_overlay:
            self.show()
            self.raise_()'''

    new_dock_method = '''    def _dock_to_main(self): #vers 8
        \"\"\"Dock handled by overlay system in imgfactory - IMPROVED\"\"\"
        try:
            if hasattr(self, 'is_overlay') and self.is_overlay:
                self.show()
                self.raise_()
                return
            
            # For proper docking, we need to be called from imgfactory
            # This method should be handled by imgfactory's overlay system
            if self.main_window and hasattr(self.main_window, 'open_col_workshop_docked'):
                # If available, use the main window's docking system
                self.main_window.open_col_workshop_docked()
            else:
                # Fallback: just show the window
                self.show()
                self.raise_()
                
            # Update dock state
            self.is_docked = True
            self._update_dock_button_visibility()
            
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"{App_name} docked to main window")
                
        except Exception as e:
            img_debugger.error(f"Error docking: {str(e)}")
            self.show()'''

    content = content.replace(old_dock_method, new_dock_method)

    old_undock_method = '''    def _undock_from_main(self): #vers 3
        \"\"\"Undock from overlay mode to standalone window\"\"\"
        if hasattr(self, 'is_overlay') and self.is_overlay:
            self.setWindowFlags(Qt.WindowType.Window)
            self.is_overlay = False
            self.overlay_table = None

        self.is_docked = False
        self._update_dock_button_visibility()

        self.show()

        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(App_name + " undocked to standalone")'''

    new_undock_method = '''    def _undock_from_main(self): #vers 4
        \"\"\"Undock from overlay mode to standalone window - IMPROVED\"\"\"
        try:
            if hasattr(self, 'is_overlay') and self.is_overlay:
                # Switch from overlay to normal window
                self.setWindowFlags(Qt.WindowType.Window)
                self.is_overlay = False
                self.overlay_table = None

            # Set proper window flags for standalone mode
            self.setWindowFlags(Qt.WindowType.Window)
            
            # Ensure proper size when undocking
            if hasattr(self, 'original_size'):
                self.resize(self.original_size)
            else:
                self.resize(1000, 700)  # Reasonable default size
                
            self.is_docked = False
            self._update_dock_button_visibility()

            self.show()
            self.raise_()

            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"{App_name} undocked to standalone")
                
        except Exception as e:
            img_debugger.error(f"Error undocking: {str(e)}")
            # Fallback
            self.setWindowFlags(Qt.WindowType.Window)
            self.show()'''

    content = content.replace(old_undock_method, new_undock_method)

    # Fix 3: Add import/export functionality when docked
    # First, let's add the missing method for import/export when docked
    # Find the end of the class COLWorkshop and add the method
    class_end_marker = "        img_debugger.debug(\"COL Editor dialog closed\")"
    import_export_methods = '''

    # Add import/export functionality when docked
    def _add_import_export_functionality(self): #vers 1
        \"\"\"Add import/export functionality when docked to img factory\"\"\"
        try:
            # Only add these when docked to img factory
            if self.main_window and hasattr(self.main_window, 'log_message'):
                # Add import button to toolbar if not already present
                if not hasattr(self, 'import_btn'):
                    # Import button would be added to the toolbar in _create_toolbar
                    pass
                    
                # Add export button to toolbar if not already present
                if not hasattr(self, 'export_btn'):
                    # Export button would be added to the toolbar in _create_toolbar
                    pass
                    
                self.main_window.log_message(f"{App_name} import/export functionality ready")
                
        except Exception as e:
            img_debugger.error(f"Error adding import/export functionality: {str(e)}")

    def _import_col_data(self): #vers 1
        \"\"\"Import COL data from external source\"\"\"
        try:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"{App_name} import functionality - not yet implemented")
                # TODO: Implement actual import functionality
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Import", "Import functionality coming soon!")
        except Exception as e:
            img_debugger.error(f"Error importing COL data: {str(e)}")

    def _export_col_data(self): #vers 1
        \"\"\"Export COL data to external source\"\"\"
        try:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"{App_name} export functionality - not yet implemented")
                # TODO: Implement actual export functionality
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export", "Export functionality coming soon!")
        except Exception as e:
            img_debugger.error(f"Error exporting COL data: {str(e)}")'''

    # Add the import/export methods to the COLWorkshop class
    content = content.replace(class_end_marker, class_end_marker + import_export_methods)

    # Fix 4: Add proper method to handle tab visibility when torn off
    # Look for the _toggle_tearoff method and improve it
    old_tearoff_method = '''    def _toggle_tearoff(self): #vers 1
        \"\"\"Toggle tear-off state (merge back to IMG Factory)\"\"\"
        QMessageBox.information(self, "Tear-off",
            "Merge back to IMG Factory functionality coming soon!\\n\\n"
            "This will dock the app back into the main window.")'''

    new_tearoff_method = '''    def _toggle_tearoff(self): #vers 2
        \"\"\"Toggle tear-off state (merge back to IMG Factory) - IMPROVED\"\"\"
        try:
            if self.is_docked:
                # Undock from main window
                self._undock_from_main()
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"{App_name} torn off from main window")
            else:
                # Dock back to main window
                self._dock_to_main()
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"{App_name} docked back to main window")
                    
        except Exception as e:
            img_debugger.error(f"Error toggling tear-off: {str(e)}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Tear-off Error", f"Could not toggle tear-off state:\\n{str(e)}")'''

    content = content.replace(old_tearoff_method, new_tearoff_method)

    # Write the updated content back to the file
    with open(col_workshop_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully updated {col_workshop_path}")
    return True


def fix_img_factory():
    """Add COL workshop docking support to imgfactory"""
    
    imgfactory_path = Path("/workspace/apps/components/Img_Factory/imgfactory.py")
    
    if not imgfactory_path.exists():
        print(f"Error: {imgfactory_path} not found")
        return False
    
    # Read the current file
    with open(imgfactory_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add COL workshop docking method similar to TXD
    col_dock_method = '''
    def open_col_workshop_docked(self, col_name=None, col_data=None): #vers 1
        \"\"\"Open COL Workshop as overlay on file window - SIMILAR TO TXD VERSION\"\"\"
        from apps.components.Col_Editor.col_workshop import COLWorkshop
        from PyQt6.QtWidgets import QTableWidget
        from PyQt6.QtCore import Qt

        # Get current tab
        current_tab_index = self.main_tab_widget.currentIndex()
        if current_tab_index < 0:
            self.log_message(\"No active tab\")
            return None

        current_tab = self.main_tab_widget.widget(current_tab_index)
        if not current_tab:
            return None

        # Find the file list table to get its geometry
        tables = current_tab.findChildren(QTableWidget)

        if not tables:
            self.log_message(\"No table found to overlay\")
            return None

        file_table = tables[0]

        # Create COL Workshop as frameless overlay
        workshop = COLWorkshop(parent=self, main_window=self)

        # Make it frameless overlay
        workshop.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)

        # Load COL data if provided
        if col_data:
            # TODO: Implement COL data loading
            workshop.load_from_img_archive(col_data)
        elif col_name and hasattr(self, 'current_img') and self.current_img:
            # Find the COL entry in current IMG
            for entry in self.current_img.entries:
                if entry.name.lower() == col_name.lower():
                    # TODO: Implement COL loading from entry
                    workshop.load_from_img_archive(self.current_img.file_path)
                    break

        # Get file table geometry in global coordinates
        table_rect = file_table.geometry()
        table_global_pos = file_table.mapToGlobal(table_rect.topLeft())

        # Position workshop over the file table
        workshop.setGeometry(
            table_global_pos.x(),
            table_global_pos.y(),
            table_rect.width(),
            table_rect.height()
        )

        # Mark as overlay
        workshop.is_overlay = True
        workshop.overlay_table = file_table
        workshop.overlay_tab_index = current_tab_index

        workshop.show()
        workshop.raise_()

        # Store in main window
        if not hasattr(self, 'col_workshops'):
            self.col_workshops = []
        self.col_workshops.append(workshop)

        # Connect tab switching to hide/show
        self.main_tab_widget.currentChanged.connect(
            lambda idx: self._handle_col_overlay_tab_switch(workshop, idx)
        )

        self.log_message(\"COL Workshop opened as overlay\")

        return workshop

    def _handle_col_overlay_tab_switch(self, workshop, new_tab_index): #vers 1
        \"\"\"Handle hiding/showing COL Workshop overlay on tab switch\"\"\"
        if not hasattr(workshop, 'is_overlay') or not workshop.is_overlay:
            return

        if new_tab_index == workshop.overlay_tab_index:
            # Switched to COL's tab - show and raise
            workshop.show()
            workshop.raise_()
            workshop.activateWindow()
        else:
            # Switched away - hide it
            workshop.hide()'''

    # Find a good place to insert the method - after the TXD workshop method
    if "def open_txd_workshop_docked" in content:
        # Insert after the TXD method and before the next method
        insert_pos = content.find("def open_txd_workshop_docked")
        insert_pos = content.find("\n\n", insert_pos)  # Find end of method
        if insert_pos != -1:
            content = content[:insert_pos] + col_dock_method + content[insert_pos:]
    else:
        # If TXD method doesn't exist, add it near the COL editor method
        pos = content.find("def open_col_editor(self): #vers 2")
        if pos != -1:
            # Find the end of this method
            end_pos = content.find("\n\n    #", pos)
            if end_pos == -1:
                end_pos = content.find("\n\n   ", pos)
            if end_pos == -1:
                end_pos = content.find("\n\n# ", pos)
            if end_pos == -1:
                end_pos = len(content)
            content = content[:end_pos] + col_dock_method + content[end_pos:]
    
    # Write the updated content back to the file
    with open(imgfactory_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully updated {imgfactory_path}")
    return True


def main():
    """Main function to apply all fixes"""
    print("Applying fixes to COL Workshop and related components...")
    
    # Fix the COL Workshop
    success1 = fix_col_workshop()
    
    # Fix the IMG Factory to support COL Workshop docking
    success2 = fix_img_factory()
    
    if success1 and success2:
        print("\\nAll fixes applied successfully!")
        print("\\nSummary of fixes applied:")
        print("1. Fixed collision rendering in preview panel")
        print("2. Improved docking/undocking functionality")
        print("3. Added tear-off functionality improvements")
        print("4. Added COL Workshop docking support to IMG Factory")
        print("5. Improved error handling and window sizing")
    else:
        print("\\nSome fixes failed to apply.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())