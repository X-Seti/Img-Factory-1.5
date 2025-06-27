#!/usr/bin/env python3
"""
#this belongs in gui/col_gui_components.py
X-Seti - June27 2025 - COL GUI Components for Img Factory 1.5
GUI buttons, menus, and styling for COL functionality integration
"""

from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QMenu, QAction, QMenuBar, QMessageBox, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont

class COLActionButton(QPushButton):
    """Specialized button for COL operations with proper theming"""
    
    def __init__(self, text: str, action_type: str = "update", parent=None):
        super().__init__(text, parent)
        
        # Set action type for theme styling
        self.setProperty("action-type", action_type)
        
        # Set COL-specific styling
        self.setMinimumHeight(32)
        self.setMinimumWidth(120)
        
        # Make it bold and prominent
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        
        # Add COL-specific tooltip
        self.setToolTip(f"COL Operation: {text}")

class COLEditorButton(COLActionButton):
    """Main COL Editor button"""
    
    col_editor_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("🔧 COL Editor", "update", parent)
        self.setToolTip("Open COL Editor\nEdit collision files with full 3D visualization")
        
        # Connect to signal
        self.clicked.connect(self.col_editor_requested.emit)
        
        # Make it extra prominent
        self.setMinimumHeight(40)
        self.setMinimumWidth(140)
        
        # Set font size larger
        font = self.font()
        font.setPointSize(font.pointSize() + 1)
        self.setFont(font)

class COLToolsButtonGroup(QWidget):
    """Group of COL tool buttons"""
    
    col_editor_requested = pyqtSignal()
    col_batch_requested = pyqtSignal()
    col_analyzer_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the button group UI"""
        layout = QVBoxLayout(self)
        
        # COL Tools group
        col_group = QGroupBox("🔧 COL Tools")
        col_layout = QVBoxLayout(col_group)
        
        # Main COL Editor button
        self.col_editor_btn = COLEditorButton()
        col_layout.addWidget(self.col_editor_btn)
        
        # Secondary tools in horizontal layout
        tools_layout = QHBoxLayout()
        
        self.batch_btn = COLActionButton("⚙️ Batch", "convert")
        self.batch_btn.setToolTip("COL Batch Processor\nProcess multiple COL files at once")
        tools_layout.addWidget(self.batch_btn)
        
        self.analyzer_btn = COLActionButton("📊 Analyze", "import")
        self.analyzer_btn.setToolTip("COL Analyzer\nAnalyze COL file structure and quality")
        tools_layout.addWidget(self.analyzer_btn)
        
        col_layout.addLayout(tools_layout)
        
        layout.addWidget(col_group)
    
    def connect_signals(self):
        """Connect button signals"""
        self.col_editor_btn.col_editor_requested.connect(self.col_editor_requested.emit)
        self.batch_btn.clicked.connect(self.col_batch_requested.emit)
        self.analyzer_btn.clicked.connect(self.col_analyzer_requested.emit)

class COLMenuBuilder:
    """Helper class to build COL menu items"""
    
    @staticmethod
    def add_col_menu_to_menubar(menubar: QMenuBar, parent_window) -> QMenu:
        """Add COL menu to existing menubar"""
        
        # Create COL menu
        col_menu = menubar.addMenu("🔧 &COL")
        
        # Main COL Editor
        editor_action = QAction("✏️ COL &Editor", parent_window)
        editor_action.setShortcut("Ctrl+Shift+C")
        editor_action.setStatusTip("Open COL Editor for collision file editing")
        editor_action.triggered.connect(lambda: COLMenuBuilder._open_col_editor(parent_window))
        col_menu.addAction(editor_action)
        
        col_menu.addSeparator()
        
        # File operations
        open_col_action = QAction("📂 &Open COL File", parent_window)
        open_col_action.setShortcut("Ctrl+Shift+O")
        open_col_action.setStatusTip("Open COL file directly")
        open_col_action.triggered.connect(lambda: COLMenuBuilder._open_col_file(parent_window))
        col_menu.addAction(open_col_action)
        
        new_col_action = QAction("🆕 &New COL File", parent_window)
        new_col_action.setStatusTip("Create new COL file")
        new_col_action.triggered.connect(lambda: COLMenuBuilder._new_col_file(parent_window))
        col_menu.addAction(new_col_action)
        
        col_menu.addSeparator()
        
        # Batch operations
        batch_action = QAction("⚙️ &Batch Processor", parent_window)
        batch_action.setShortcut("Ctrl+Shift+B")
        batch_action.setStatusTip("Process multiple COL files with batch operations")
        batch_action.triggered.connect(lambda: COLMenuBuilder._open_batch_processor(parent_window))
        col_menu.addAction(batch_action)
        
        analyze_action = QAction("📊 &Analyze COL", parent_window)
        analyze_action.setShortcut("Ctrl+Shift+A")
        analyze_action.setStatusTip("Analyze COL file structure and quality")
        analyze_action.triggered.connect(lambda: COLMenuBuilder._analyze_col(parent_window))
        col_menu.addAction(analyze_action)
        
        col_menu.addSeparator()
        
        # IMG integration
        import_submenu = col_menu.addMenu("📥 Import from IMG")
        
        extract_col_action = QAction("Extract COL from Current IMG", parent_window)
        extract_col_action.setStatusTip("Extract COL files from currently open IMG")
        extract_col_action.triggered.connect(lambda: COLMenuBuilder._extract_col_from_img(parent_window))
        import_submenu.addAction(extract_col_action)
        
        import_col_action = QAction("Import COL to Current IMG", parent_window)
        import_col_action.setStatusTip("Import COL file into currently open IMG")
        import_col_action.triggered.connect(lambda: COLMenuBuilder._import_col_to_img(parent_window))
        import_submenu.addAction(import_col_action)
        
        col_menu.addSeparator()
        
        # Help
        help_action = QAction("❓ COL &Help", parent_window)
        help_action.setStatusTip("Show help for COL functionality")
        help_action.triggered.connect(lambda: COLMenuBuilder._show_col_help(parent_window))
        col_menu.addAction(help_action)
        
        return col_menu
    
    @staticmethod
    def _open_col_editor(parent_window):
        """Open COL editor"""
        try:
            from components.col_editor import open_col_editor
            open_col_editor(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Editor", "COL Editor components not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to open COL Editor: {str(e)}")
    
    @staticmethod
    def _open_col_file(parent_window):
        """Open COL file dialog"""
        try:
            from imgfactory_col_integration import open_col_file_dialog
            open_col_file_dialog(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Tools", "COL integration components not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to open COL file: {str(e)}")
    
    @staticmethod
    def _new_col_file(parent_window):
        """Create new COL file"""
        try:
            from imgfactory_col_integration import create_new_col_file
            create_new_col_file(parent_window)
        except ImportError:
            QMessageBox.information(parent_window, "COL Tools", "New COL file creation coming soon!")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to create COL file: {str(e)}")
    
    @staticmethod
    def _open_batch_processor(parent_window):
        """Open batch processor"""
        try:
            from components.col_utilities import open_col_batch_processor
            open_col_batch_processor(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Tools", "COL batch processor not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to open batch processor: {str(e)}")
    
    @staticmethod
    def _analyze_col(parent_window):
        """Analyze COL file"""
        try:
            from components.col_utilities import analyze_col_file_dialog
            analyze_col_file_dialog(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Tools", "COL analyzer not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to analyze COL: {str(e)}")
    
    @staticmethod
    def _extract_col_from_img(parent_window):
        """Extract COL from IMG"""
        try:
            from imgfactory_col_integration import export_col_from_img
            export_col_from_img(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Tools", "COL integration not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to extract COL: {str(e)}")
    
    @staticmethod
    def _import_col_to_img(parent_window):
        """Import COL to IMG"""
        try:
            from imgfactory_col_integration import import_col_to_img
            import_col_to_img(parent_window)
        except ImportError:
            QMessageBox.warning(parent_window, "COL Tools", "COL integration not found")
        except Exception as e:
            QMessageBox.critical(parent_window, "Error", f"Failed to import COL: {str(e)}")
    
    @staticmethod
    def _show_col_help(parent_window):
        """Show COL help dialog"""
        help_text = """
<h2>🔧 COL Functionality Help</h2>

<h3>What are COL files?</h3>
<p>COL files contain collision data for GTA games. They define the physical boundaries 
that players, vehicles, and objects interact with in the game world.</p>

<h3>COL Editor Features:</h3>
<ul>
<li><b>3D Visualization</b> - View collision geometry in 3D</li>
<li><b>Edit Collision Elements</b> - Modify spheres, boxes, and meshes</li>
<li><b>Material Assignment</b> - Set surface materials for different effects</li>
<li><b>Version Conversion</b> - Convert between COL formats</li>
<li><b>Optimization Tools</b> - Remove duplicates and optimize geometry</li>
</ul>

<h3>Batch Processor:</h3>
<ul>
<li><b>Process Multiple Files</b> - Handle many COL files at once</li>
<li><b>Automatic Optimization</b> - Clean up and optimize collision data</li>
<li><b>Version Conversion</b> - Convert entire batches between formats</li>
<li><b>Quality Analysis</b> - Check for issues and problems</li>
</ul>

<h3>Supported Games:</h3>
<ul>
<li>GTA III (COL Version 1)</li>
<li>GTA Vice City (COL Version 1)</li>
<li>GTA San Andreas (COL Version 2 & 3)</li>
<li>GTA Stories series</li>
<li>Bully</li>
</ul>

<h3>Keyboard Shortcuts:</h3>
<ul>
<li><b>Ctrl+Shift+C</b> - Open COL Editor</li>
<li><b>Ctrl+Shift+B</b> - Open Batch Processor</li>
<li><b>Ctrl+Shift+A</b> - Analyze COL File</li>
<li><b>Ctrl+Shift+O</b> - Open COL File</li>
</ul>

<p><i>COL functionality is based on Steve's COL Editor II with modern improvements.</i></p>
        """
        
        QMessageBox.about(parent_window, "COL Help", help_text)

class COLStatusIndicator(QWidget):
    """Status indicator for COL operations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.reset_status()
    
    def setup_ui(self):
        """Setup status indicator UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Status label
        self.status_label = QPushButton("COL: Ready")
        self.status_label.setFlat(True)
        self.status_label.setMaximumHeight(20)
        self.status_label.setStyleSheet("""
            QPushButton {
                background-color: #e8f5e8;
                border: 1px solid #4caf50;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 8pt;
                color: #2e7d32;
            }
            QPushButton:hover {
                background-color: #c8e6c9;
            }
        """)
        
        layout.addWidget(self.status_label)
    
    def set_status(self, status: str, status_type: str = "ready"):
        """Set status with type-based styling"""
        colors = {
            "ready": {"bg": "#e8f5e8", "border": "#4caf50", "text": "#2e7d32"},
            "working": {"bg": "#fff3e0", "border": "#ff9800", "text": "#e65100"},
            "error": {"bg": "#ffebee", "border": "#f44336", "text": "#c62828"},
            "success": {"bg": "#e3f2fd", "border": "#2196f3", "text": "#1565c0"}
        }
        
        color = colors.get(status_type, colors["ready"])
        
        self.status_label.setText(f"COL: {status}")
        self.status_label.setStyleSheet(f"""
            QPushButton {{
                background-color: {color["bg"]};
                border: 1px solid {color["border"]};
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 8pt;
                color: {color["text"]};
            }}
            QPushButton:hover {{
                background-color: {color["bg"]};
                opacity: 0.8;
            }}
        """)
    
    def reset_status(self):
        """Reset to ready status"""
        self.set_status("Ready", "ready")
    
    def set_working(self, operation: str):
        """Set working status"""
        self.set_status(f"Working: {operation}", "working")
    
    def set_error(self, error: str):
        """Set error status"""
        self.set_status(f"Error: {error}", "error")
    
    def set_success(self, message: str):
        """Set success status"""
        self.set_status(f"✓ {message}", "success")

def integrate_col_gui_into_imgfactory(img_factory_window):
    """
    Integrate COL GUI components into the main IMG Factory window
    """
    try:
        # Add COL menu to menubar
        if hasattr(img_factory_window, 'menuBar'):
            col_menu = COLMenuBuilder.add_col_menu_to_menubar(
                img_factory_window.menuBar(), 
                img_factory_window
            )
            
            # Store reference
            img_factory_window.col_menu = col_menu
        
        # Add COL tools to right panel if it exists
        if hasattr(img_factory_window, '_create_right_panel') or hasattr(img_factory_window, 'right_panel'):
            # Try to add COL tools group to existing right panel
            try:
                # Find the right panel widget
                right_panel = None
                if hasattr(img_factory_window, 'right_panel'):
                    right_panel = img_factory_window.right_panel
                elif hasattr(img_factory_window, 'main_splitter'):
                    # Look for right panel in splitter
                    for i in range(img_factory_window.main_splitter.count()):
                        widget = img_factory_window.main_splitter.widget(i)
                        if widget and i == img_factory_window.main_splitter.count() - 1:  # Last widget
                            right_panel = widget
                            break
                
                if right_panel and hasattr(right_panel, 'layout'):
                    # Create COL tools group
                    col_tools = COLToolsButtonGroup()
                    
                    # Connect signals to main window methods
                    col_tools.col_editor_requested.connect(lambda: COLMenuBuilder._open_col_editor(img_factory_window))
                    col_tools.col_batch_requested.connect(lambda: COLMenuBuilder._open_batch_processor(img_factory_window))
                    col_tools.col_analyzer_requested.connect(lambda: COLMenuBuilder._analyze_col(img_factory_window))
                    
                    # Insert before the stretch (usually last item)
                    layout = right_panel.layout()
                    if layout:
                        # Find stretch item and insert before it
                        count = layout.count()
                        if count > 0:
                            last_item = layout.itemAt(count - 1)
                            if hasattr(last_item, 'spacerItem') and last_item.spacerItem():
                                # Insert before stretch
                                layout.insertWidget(count - 1, col_tools)
                            else:
                                # Just add at the end
                                layout.addWidget(col_tools)
                        else:
                            layout.addWidget(col_tools)
                    
                    # Store reference
                    img_factory_window.col_tools = col_tools
                    
            except Exception as e:
                print(f"Failed to add COL tools to right panel: {e}")
        
        # Add COL status indicator to status bar
        if hasattr(img_factory_window, 'statusBar'):
            col_status = COLStatusIndicator()
            img_factory_window.statusBar().addPermanentWidget(col_status)
            img_factory_window.col_status = col_status
        
        # Log success
        if hasattr(img_factory_window, 'log_message'):
            img_factory_window.log_message("COL GUI components integrated successfully")
        
        return True
        
    except Exception as e:
        print(f"Error integrating COL GUI: {e}")
        if hasattr(img_factory_window, 'log_message'):
            img_factory_window.log_message(f"COL GUI integration error: {str(e)}")
        return False

# Convenience function for easy integration
def setup_col_gui(img_factory_window):
    """
    Easy setup function for COL GUI integration
    Call this from your main IMG Factory window after UI creation
    """
    return integrate_col_gui_into_imgfactory(img_factory_window)