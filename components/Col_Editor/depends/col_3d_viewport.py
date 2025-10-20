#this belongs in components/Col_Editor/depends/col_3d_viewport.py - Version: 1
# X-Seti - October20 2025 - IMG Factory 1.5 - COL 3D Viewport

"""
COL 3D Viewport - OpenGL-based 3D rendering widget for COL collision models
Renders vertices, faces, spheres, boxes, and shadow meshes with mouse navigation
Based on Steve M's COL Editor II approach using OpenGL
"""

import math
from typing import Optional, List, Tuple
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QTransform
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False

from PyQt6.QtGui import QSurfaceFormat

# Request OpenGL compatibility profile
fmt = QSurfaceFormat()
fmt.setVersion(2, 1)  # OpenGL 2.1 with compatibility
fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile)
QSurfaceFormat.setDefaultFormat(fmt)

##Methods list -
# draw_box
# draw_face_mesh
# draw_sphere
# initializeGL
# mouseMoveEvent
# mousePressEvent
# paintGL
# reset_view
# resizeGL
# set_current_model
# set_view_options
# update_display
# wheelEvent

##Classes -
# COL3DViewport

class COL3DViewport(QOpenGLWidget if OPENGL_AVAILABLE else QWidget):
    """OpenGL 3D viewport for COL collision models"""
    
    model_selected = pyqtSignal(int)
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        
        # View state
        self.rotation_x = 20.0
        self.rotation_y = 45.0
        self.zoom = 10.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        
        # Mouse tracking
        self.last_mouse_pos = QPoint()
        self.mouse_button = Qt.MouseButton.NoButton
        
        # Display options
        self.show_spheres = True
        self.show_boxes = True
        self.show_mesh = True
        self.show_wireframe = True
        self.show_bounds = True
        self.show_shadow_mesh = False
        
        # Current data
        self.current_model = None
        self.current_file = None
        self.selected_model_index = -1
        
        # Colors
        self.bg_color = QColor(30, 30, 30)
        self.mesh_color = QColor(0, 255, 0)
        self.wireframe_color = QColor(100, 255, 100)
        self.sphere_color = QColor(0, 200, 255)
        self.box_color = QColor(255, 200, 0)
        self.bounds_color = QColor(255, 0, 0)
        
        self.setMinimumSize(400, 300)
    
    def initializeGL(self): #vers 3
        """Initialize OpenGL settings - Modern OpenGL compatible"""
        if not OPENGL_AVAILABLE:
            return

        glClearColor(self.bg_color.redF(), self.bg_color.greenF(),
                    self.bg_color.blueF(), 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Legacy OpenGL features - wrap in try/except for compatibility
        try:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

            # Setup lighting (legacy)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

            # Light position
            glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        except Exception as e:
            # Modern OpenGL core profile - skip legacy features
            print(f"Note: Using modern OpenGL (legacy lighting disabled): {e}")
    
    def resizeGL(self, w, h): #vers 1
        """Handle viewport resize"""
        if not OPENGL_AVAILABLE:
            return
        
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = w / h if h > 0 else 1.0
        gluPerspective(45.0, aspect, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self): #vers 1
        """Render the 3D scene"""
        if not OPENGL_AVAILABLE:
            self._paint_fallback()
            return
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Apply camera transformations
        glTranslatef(self.pan_x, -self.pan_y, -self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        
        # Draw grid
        self._draw_grid()
        
        if not self.current_model:
            return
        
        # Draw collision elements
        if self.show_mesh and hasattr(self.current_model, 'faces'):
            self.draw_face_mesh()
        
        if self.show_spheres and hasattr(self.current_model, 'spheres'):
            for sphere in self.current_model.spheres:
                self.draw_sphere(sphere)
        
        if self.show_boxes and hasattr(self.current_model, 'boxes'):
            for box in self.current_model.boxes:
                self.draw_box(box)
        
        if self.show_bounds and hasattr(self.current_model, 'bounding_box'):
            self._draw_bounding_box(self.current_model.bounding_box)
        
        if self.show_shadow_mesh and hasattr(self.current_model, 'shadow_faces'):
            self._draw_shadow_mesh()
    
    def draw_face_mesh(self): #vers 1
        """Draw collision mesh faces"""
        if not hasattr(self.current_model, 'faces') or not hasattr(self.current_model, 'vertices'):
            return
        
        vertices = self.current_model.vertices
        faces = self.current_model.faces
        
        if self.show_wireframe:
            glDisable(GL_LIGHTING)
            glColor3f(self.wireframe_color.redF(), self.wireframe_color.greenF(), 
                     self.wireframe_color.blueF())
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glEnable(GL_LIGHTING)
            glColor3f(self.mesh_color.redF(), self.mesh_color.greenF(), 
                     self.mesh_color.blueF())
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        glBegin(GL_TRIANGLES)
        for face in faces:
            if hasattr(face, 'indices') and len(face.indices) >= 3:
                for idx in face.indices[:3]:
                    if idx < len(vertices):
                        v = vertices[idx]
                        if hasattr(v, 'x'):
                            glVertex3f(v.x, v.y, v.z)
        glEnd()
        
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    def draw_sphere(self, sphere): #vers 1
        """Draw collision sphere"""
        if not hasattr(sphere, 'center') or not hasattr(sphere, 'radius'):
            return
        
        glDisable(GL_LIGHTING)
        glColor4f(self.sphere_color.redF(), self.sphere_color.greenF(), 
                 self.sphere_color.blueF(), 0.4)
        
        glPushMatrix()
        glTranslatef(sphere.center.x, sphere.center.y, sphere.center.z)
        
        # Draw wireframe sphere
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_LINE)
        gluSphere(quadric, sphere.radius, 16, 16)
        gluDeleteQuadric(quadric)
        
        glPopMatrix()
    
    def draw_box(self, box): #vers 1
        """Draw collision box"""
        if not hasattr(box, 'min') or not hasattr(box, 'max'):
            return
        
        glDisable(GL_LIGHTING)
        glColor4f(self.box_color.redF(), self.box_color.greenF(), 
                 self.box_color.blueF(), 0.4)
        
        min_v = box.min
        max_v = box.max
        
        glBegin(GL_LINE_LOOP)
        glVertex3f(min_v.x, min_v.y, min_v.z)
        glVertex3f(max_v.x, min_v.y, min_v.z)
        glVertex3f(max_v.x, max_v.y, min_v.z)
        glVertex3f(min_v.x, max_v.y, min_v.z)
        glEnd()
        
        glBegin(GL_LINE_LOOP)
        glVertex3f(min_v.x, min_v.y, max_v.z)
        glVertex3f(max_v.x, min_v.y, max_v.z)
        glVertex3f(max_v.x, max_v.y, max_v.z)
        glVertex3f(min_v.x, max_v.y, max_v.z)
        glEnd()
        
        glBegin(GL_LINES)
        glVertex3f(min_v.x, min_v.y, min_v.z)
        glVertex3f(min_v.x, min_v.y, max_v.z)
        glVertex3f(max_v.x, min_v.y, min_v.z)
        glVertex3f(max_v.x, min_v.y, max_v.z)
        glVertex3f(max_v.x, max_v.y, min_v.z)
        glVertex3f(max_v.x, max_v.y, max_v.z)
        glVertex3f(min_v.x, max_v.y, min_v.z)
        glVertex3f(min_v.x, max_v.y, max_v.z)
        glEnd()
    
    def _draw_grid(self): #vers 1
        """Draw reference grid"""
        glDisable(GL_LIGHTING)
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        
        grid_size = 50.0
        grid_step = 5.0
        
        for i in range(-int(grid_size), int(grid_size) + 1):
            pos = i * grid_step
            glVertex3f(pos, 0, -grid_size * grid_step)
            glVertex3f(pos, 0, grid_size * grid_step)
            glVertex3f(-grid_size * grid_step, 0, pos)
            glVertex3f(grid_size * grid_step, 0, pos)
        
        glEnd()
        
        # Draw axes
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(10, 0, 0)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 10, 0)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 10)
        glEnd()
    
    def _draw_bounding_box(self, bbox): #vers 1
        """Draw bounding box"""
        if not bbox or not hasattr(bbox, 'min') or not hasattr(bbox, 'max'):
            return
        
        glDisable(GL_LIGHTING)
        glColor3f(self.bounds_color.redF(), self.bounds_color.greenF(), 
                 self.bounds_color.blueF())
        
        min_v = bbox.min
        max_v = bbox.max
        
        glBegin(GL_LINE_LOOP)
        glVertex3f(min_v.x, min_v.y, min_v.z)
        glVertex3f(max_v.x, min_v.y, min_v.z)
        glVertex3f(max_v.x, max_v.y, min_v.z)
        glVertex3f(min_v.x, max_v.y, min_v.z)
        glEnd()
        
        glBegin(GL_LINE_LOOP)
        glVertex3f(min_v.x, min_v.y, max_v.z)
        glVertex3f(max_v.x, min_v.y, max_v.z)
        glVertex3f(max_v.x, max_v.y, max_v.z)
        glVertex3f(min_v.x, max_v.y, max_v.z)
        glEnd()
        
        glBegin(GL_LINES)
        glVertex3f(min_v.x, min_v.y, min_v.z)
        glVertex3f(min_v.x, min_v.y, max_v.z)
        glVertex3f(max_v.x, min_v.y, min_v.z)
        glVertex3f(max_v.x, min_v.y, max_v.z)
        glVertex3f(max_v.x, max_v.y, min_v.z)
        glVertex3f(max_v.x, max_v.y, max_v.z)
        glVertex3f(min_v.x, max_v.y, min_v.z)
        glVertex3f(min_v.x, max_v.y, max_v.z)
        glEnd()
    
    def _draw_shadow_mesh(self): #vers 1
        """Draw shadow mesh if present"""
        if not hasattr(self.current_model, 'shadow_faces'):
            return
        
        glDisable(GL_LIGHTING)
        glColor4f(0.5, 0.5, 0.5, 0.3)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        # Draw shadow faces similar to regular mesh
        glBegin(GL_TRIANGLES)
        for face in self.current_model.shadow_faces:
            if hasattr(face, 'indices'):
                for idx in face.indices[:3]:
                    if idx < len(self.current_model.vertices):
                        v = self.current_model.vertices[idx]
                        glVertex3f(v.x, v.y, v.z)
        glEnd()
        
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    def mousePressEvent(self, event): #vers 1
        """Handle mouse press for rotation/zoom"""
        self.last_mouse_pos = event.pos()
        self.mouse_button = event.button()
    
    def mouseMoveEvent(self, event): #vers 1
        """Handle mouse movement for navigation"""
        dx = event.pos().x() - self.last_mouse_pos.x()
        dy = event.pos().y() - self.last_mouse_pos.y()
        
        if self.mouse_button == Qt.MouseButton.LeftButton:
            # Rotate view
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
            self.update()
        elif self.mouse_button == Qt.MouseButton.RightButton:
            # Pan view
            self.pan_x += dx * 0.05
            self.pan_y += dy * 0.05
            self.update()
        
        self.last_mouse_pos = event.pos()
    
    def wheelEvent(self, event): #vers 1
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y()
        self.zoom -= delta * 0.01
        self.zoom = max(1.0, min(100.0, self.zoom))
        self.update()
    
    def set_current_model(self, model, model_index=-1): #vers 1
        """Set current COL model to display"""
        self.current_model = model
        self.selected_model_index = model_index
        self.update()
    
    def set_view_options(self, show_spheres=None, show_boxes=None, show_mesh=None, 
                        show_wireframe=None, show_bounds=None, show_shadow=None): #vers 1
        """Update view display options"""
        if show_spheres is not None:
            self.show_spheres = show_spheres
        if show_boxes is not None:
            self.show_boxes = show_boxes
        if show_mesh is not None:
            self.show_mesh = show_mesh
        if show_wireframe is not None:
            self.show_wireframe = show_wireframe
        if show_bounds is not None:
            self.show_bounds = show_bounds
        if show_shadow is not None:
            self.show_shadow_mesh = show_shadow
        
        self.update()
    
    def reset_view(self): #vers 1
        """Reset camera to default position"""
        self.rotation_x = 20.0
        self.rotation_y = 45.0
        self.zoom = 10.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.update()
    
    def update_display(self): #vers 1
        """Force display update"""
        self.update()
    
    def _paint_fallback(self): #vers 1
        """Fallback rendering when OpenGL unavailable"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)
        
        painter.setPen(QPen(QColor(255, 255, 255)))
        text = "OpenGL not available\nInstall PyOpenGL:\npip install PyOpenGL PyOpenGL_accelerate"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)


# Export classes
__all__ = ['COL3DViewport']
