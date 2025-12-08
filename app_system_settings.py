#!/usr/bin/env python3
# $vers" X-Seti - December08, 2025 - IMG Factory - System Settings with Amiga MUI Support
"""
IMG Factory - App System Settings - Enhanced Version with Amiga MUI Support
System settings management with theme detection, Amiga MUI tab support, and image backgrounds
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from PyQt6.QtCore import Qt, pyqtSignal, QDateTime, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QButtonGroup, QRadioButton, QLabel, QPushButton,
    QComboBox, QCheckBox, QSpinBox, QMenu, QSlider, QSplitter,
    QTabWidget, QDialog, QMessageBox, QFileDialog, QColorDialog,
    QGroupBox, QTextEdit, QScrollArea, QFrame, QLineEdit, QListWidget,
    QStyleFactory
)

# Check for screen capture libraries (for system theme detection)
try:
    import mss
    MSS_AVAILABLE = True
    print("MSS library available for system theme detection")
except ImportError:
    MSS_AVAILABLE = False
    try:
        from PIL import ImageGrab
        PIL_AVAILABLE = True
        print("MSS not available, using PIL fallback for system theme detection")
    except ImportError:
        PIL_AVAILABLE = False
        print("Neither MSS nor PIL available - using Qt fallback for system theme detection")


@dataclass
class ThemeImageSettings:
    """Settings for image backgrounds in Amiga MUI style tabs"""
    bg_primary_image: Optional[str] = None
    bg_secondary_image: Optional[str] = None
    panel_bg_image: Optional[str] = None
    bg_primary_mode: str = "stretch"  # "stretch", "tile", "center", "fit"
    bg_secondary_mode: str = "stretch"
    panel_bg_mode: str = "stretch"
    bg_primary_opacity: int = 100
    bg_secondary_opacity: int = 100
    panel_bg_opacity: int = 100


class SystemThemeDetector:
    """Class to detect and capture system theme information"""
    
    @staticmethod
    def detect_system_theme() -> Dict[str, Any]:
        """Detect system theme (Windows, macOS, Linux) and return compatible theme data"""
        system_theme = {}
        
        # Detect OS
        if sys.platform.startswith('win'):
            system_theme.update(SystemThemeDetector._detect_windows_theme())
        elif sys.platform.startswith('darwin'):
            system_theme.update(SystemThemeDetector._detect_macos_theme())
        else:  # Linux
            system_theme.update(SystemThemeDetector._detect_linux_theme())
        
        return system_theme
    
    @staticmethod
    def _detect_windows_theme() -> Dict[str, Any]:
        """Detect Windows theme settings"""
        theme_data = {
            "system_theme": "windows",
            "is_dark_mode": False,
            "accent_color": "#0078D7",  # Windows blue
            "window_color": "#F3F3F3",
            "text_color": "#000000",
            "highlight_color": "#3399FF"
        }
        
        # Try to read Windows registry for dark mode (simplified)
        try:
            import winreg
            # Check Windows 10/11 dark mode setting
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                apps_use_dark_mode, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                theme_data["is_dark_mode"] = apps_use_dark_mode == 0
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass  # Registry key doesn't exist on older Windows versions
        except ImportError:
            pass  # Not on Windows or winreg not available
        
        return theme_data
    
    @staticmethod
    def _detect_macos_theme() -> Dict[str, Any]:
        """Detect macOS theme settings"""
        theme_data = {
            "system_theme": "macos",
            "is_dark_mode": False,
            "accent_color": "#007AFF",  # iOS blue
            "window_color": "#F5F5F7",
            "text_color": "#000000",
            "highlight_color": "#0A84FF"
        }
        
        # Try to detect macOS dark mode
        try:
            import subprocess
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True
            )
            theme_data["is_dark_mode"] = "Dark" in result.stdout
        except:
            pass  # Could not detect, default to light
        
        return theme_data
    
    @staticmethod
    def _detect_linux_theme() -> Dict[str, Any]:
        """Detect Linux theme settings"""
        theme_data = {
            "system_theme": "linux",
            "is_dark_mode": False,
            "accent_color": "#4A90D9",  # GNOME blue
            "window_color": "#F5F5F5",
            "text_color": "#2D2D2D",
            "highlight_color": "#3584E4"
        }
        
        # Try to detect desktop environment and theme
        try:
            desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
            if "kde" in desktop_env:
                theme_data["system_theme"] = "kde"
                # KDE-specific theme detection would go here
            elif "gnome" in desktop_env:
                theme_data["system_theme"] = "gnome"
                # GNOME-specific theme detection would go here
        except:
            pass
        
        return theme_data
    
    @staticmethod
    def capture_screen_color(x: int, y: int) -> str:
        """Capture color at specific screen coordinates"""
        try:
            if MSS_AVAILABLE:
                with mss.mss() as sct:
                    monitor = {"top": y, "left": x, "width": 1, "height": 1}
                    screenshot = sct.grab(monitor)
                    pixel = screenshot.pixel(0, 0)
                    return f"#{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"
            elif PIL_AVAILABLE:
                from PIL import ImageGrab
                bbox = (x, y, x + 1, y + 1)
                screenshot = ImageGrab.grab(bbox)
                pixel = screenshot.getpixel((0, 0))
                if isinstance(pixel, tuple) and len(pixel) >= 3:
                    return f"#{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"
            else:
                # Qt fallback
                screen = QApplication.primaryScreen()
                if screen:
                    pixmap = screen.grabWindow(0, x, y, 1, 1)
                    if not pixmap.isNull():
                        image = pixmap.toImage()
                        if not image.isNull():
                            color = QColor(image.pixel(0, 0))
                            return color.name()
        except Exception as e:
            print(f"Screen capture error: {e}")
        
        return "#ffffff"  # Default fallback


class AmigaMUITabWidget(QTabWidget):
    """Amiga MUI style tab widget with image background support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_settings = ThemeImageSettings()
        self._setup_mui_style()
        
        # Initialize advanced gadgets
        self.advanced_gadgets = {}
        self._init_advanced_gadgets()
        
        # Initialize transparency support
        self.transparency_enabled = True
        self.titlebar_transparency = 0.9
        self.panel_transparency = 0.95
        
        # Initialize shadow effects
        self.shadow_enabled = True
        self.button_shadow_depth = 2
        self.panel_shadow_depth = 3
    
    def _setup_mui_style(self):
        """Setup Amiga MUI style properties"""
        # Set tab position and style
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.setDocumentMode(True)
        self.setTabsClosable(False)
        self.setMovable(True)
    
    def _init_advanced_gadgets(self):
        """Initialize advanced Amiga MUI style gadgets"""
        # String gadget (text input)
        self.advanced_gadgets['string'] = QLineEdit
        
        # Gauge gadget (progress indicator)
        from PyQt6.QtWidgets import QProgressBar
        self.advanced_gadgets['gauge'] = QProgressBar
        
        # Scale gadget (slider)
        self.advanced_gadgets['scale'] = QSlider
        
        # Colorfield gadget (color selection)
        from PyQt6.QtWidgets import QPushButton
        self.advanced_gadgets['colorfield'] = QPushButton
        
        # List gadget
        from PyQt6.QtWidgets import QListWidget
        self.advanced_gadgets['list'] = QListWidget
        
        # Numeric gadget
        from PyQt6.QtWidgets import QSpinBox
        self.advanced_gadgets['numeric'] = QSpinBox
        
        # Knob gadget (circular control)
        # We'll implement a custom knob-like control
        self.advanced_gadgets['knob'] = QDial
        
        # Levelmeter gadget (audio level indicator)
        self.advanced_gadgets['levelmeter'] = QProgressBar
        
        # Slider gadget (horizontal/vertical)
        self.advanced_gadgets['slider'] = QSlider
        
        # Radio gadget (radio buttons)
        from PyQt6.QtWidgets import QRadioButton
        self.advanced_gadgets['radio'] = QRadioButton
        
        # Cycle gadget (cycle through options)
        from PyQt6.QtWidgets import QComboBox
        self.advanced_gadgets['cycle'] = QComboBox
        
        # Palette gadget (color palette)
        self.advanced_gadgets['palette'] = QWidget
        
        # Popstring gadget (popup string input)
        self.advanced_gadgets['popstring'] = QLineEdit
    
    def create_mui_gadget(self, gadget_type: str, **kwargs):
        """Create an Amiga MUI style gadget"""
        if gadget_type in self.advanced_gadgets:
            gadget_class = self.advanced_gadgets[gadget_type]
            
            # Special handling for certain gadgets
            if gadget_type == 'colorfield':
                gadget = gadget_class()
                gadget.setText("Select Color")
                def color_dialog():
                    color = QColorDialog.getColor()
                    if color.isValid():
                        gadget.setStyleSheet(f"background-color: {color.name()};")
                        gadget.color = color
                gadget.clicked.connect(color_dialog)
                return gadget
            elif gadget_type == 'palette':
                # Create a color palette widget
                palette_widget = QWidget()
                layout = QGridLayout(palette_widget)
                
                colors = [
                    "#FF0000", "#00FF00", "#0000FF", "#FFFF00", 
                    "#FF00FF", "#00FFFF", "#FFA500", "#800080",
                    "#FFC0CB", "#A52A2A", "#808080", "#000000"
                ]
                
                for i, color in enumerate(colors):
                    btn = QPushButton()
                    btn.setStyleSheet(f"background-color: {color}; min-width: 20px; min-height: 20px;")
                    btn.setProperty('color', color)
                    btn.clicked.connect(lambda _, c=color: self._palette_color_selected(c))
                    row = i // 4
                    col = i % 4
                    layout.addWidget(btn, row, col)
                
                return palette_widget
            else:
                gadget = gadget_class()
                
                # Apply common properties
                if 'minimum' in kwargs:
                    if hasattr(gadget, 'setMinimum'):
                        gadget.setMinimum(kwargs['minimum'])
                if 'maximum' in kwargs:
                    if hasattr(gadget, 'setMaximum'):
                        gadget.setMaximum(kwargs['maximum'])
                if 'value' in kwargs:
                    if hasattr(gadget, 'setValue'):
                        gadget.setValue(kwargs['value'])
                if 'text' in kwargs:
                    if hasattr(gadget, 'setText'):
                        gadget.setText(kwargs['text'])
                
                return gadget
        
        return None
    
    def _palette_color_selected(self, color):
        """Handle palette color selection"""
        print(f"Palette color selected: {color}")
    
    def set_transparency(self, titlebar_transparency: float = 0.9, panel_transparency: float = 0.95):
        """Set transparency levels for UI elements"""
        self.titlebar_transparency = max(0.0, min(1.0, titlebar_transparency))
        self.panel_transparency = max(0.0, min(1.0, panel_transparency))
        
        # Apply transparency to the widget
        if hasattr(self, 'parent') and self.parent():
            self.parent().setWindowOpacity(self.titlebar_transparency)
    
    def enable_shadow_effects(self, enable: bool = True, button_depth: int = 2, panel_depth: int = 3):
        """Enable or disable shadow effects"""
        self.shadow_enabled = enable
        self.button_shadow_depth = button_depth
        self.panel_shadow_depth = panel_depth
        
        if enable:
            self._apply_shadow_effects()
    
    def _apply_shadow_effects(self):
        """Apply shadow effects to UI elements"""
        # This would apply shadow effects to buttons, panels, etc.
        # In a real implementation, we would use QGraphicsEffect
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtCore import Qt
        
        # Apply shadow to tabs
        for i in range(self.count()):
            widget = self.widget(i)
            if self.shadow_enabled:
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(self.panel_shadow_depth * 2)
                shadow.setXOffset(0)
                shadow.setYOffset(self.panel_shadow_depth)
                shadow.setColor(QColor(0, 0, 0, 100))
                widget.setGraphicsEffect(shadow)
    
    def create_mui_group(self, title: str = ""):
        """Create an Amiga MUI style group"""
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        return group, layout
    
    def create_mui_scrollbar(self, orientation=Qt.Orientation.Vertical):
        """Create an Amiga MUI style scrollbar"""
        scrollbar = QSlider()
        scrollbar.setOrientation(orientation)
        return scrollbar
    
    def create_mui_listview(self):
        """Create an Amiga MUI style listview"""
        listview = QListWidget()
        return listview
    
    def create_mui_register(self, titles: List[str]):
        """Create an Amiga MUI style register (tabbed interface)"""
        register = QTabWidget()
        for title in titles:
            tab = QWidget()
            layout = QVBoxLayout(tab)
            register.addTab(tab, title)
        return register
    
    def create_mui_virtgroup(self):
        """Create an Amiga MUI style virtual group (scrollable container)"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        return scroll_area, content_widget
    
    def create_mui_scrollgroup(self):
        """Create an Amiga MUI style scrollgroup"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        
        return widget, layout, scroll_area, scroll_content
    
    def create_mui_popobject(self, content_widget):
        """Create an Amiga MUI style popup object"""
        # This would create a popup window or dropdown
        popup = QDialog(self)
        popup.setLayout(QVBoxLayout())
        popup.layout().addWidget(content_widget)
        return popup
    
    def set_image_backgrounds(self, settings: ThemeImageSettings):
        """Set image backgrounds for different areas"""
        self.image_settings = settings
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event to handle image backgrounds"""
        painter = QPainter(self)
        
        # Paint background images if configured
        if self.image_settings.bg_primary_image:
            self._paint_background_image(
                painter, 
                self.image_settings.bg_primary_image,
                self.image_settings.bg_primary_mode,
                self.image_settings.bg_primary_opacity
            )
        
        # Call parent paint event for tabs
        super().paintEvent(event)
    
    def _paint_background_image(self, painter, image_path, mode, opacity):
        """Paint background image with specified mode and opacity"""
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                painter.setOpacity(opacity / 100.0)
                
                if mode == "stretch":
                    painter.drawPixmap(self.rect(), pixmap)
                elif mode == "tile":
                    # Tile the image
                    painter.drawTiledPixmap(self.rect(), pixmap)
                elif mode == "center":
                    # Center the image
                    x = (self.width() - pixmap.width()) // 2
                    y = (self.height() - pixmap.height()) // 2
                    painter.drawPixmap(x, y, pixmap)
                elif mode == "fit":
                    # Fit the image while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        self.size(), 
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    x = (self.width() - scaled_pixmap.width()) // 2
                    y = (self.height() - scaled_pixmap.height()) // 2
                    painter.drawPixmap(x, y, scaled_pixmap)
                
                painter.setOpacity(1.0)
        except Exception as e:
            print(f"Error painting background image: {e}")


class AppSystemSettings:
    """Main system settings class with Amiga MUI support"""
    
    def __init__(self, settings_file="appfactory.settings.json"):
        """Initialize system settings"""
        self.settings_file = Path(settings_file)
        self.current_settings = self._load_settings()
        
        # Initialize theme detection
        self.system_theme_detector = SystemThemeDetector()
        
        # Initialize image background settings
        self.image_settings = ThemeImageSettings()
        
        # Initialize Amiga MUI support
        self.mui_tabs_enabled = True
        self.mui_theme_data = self._load_mui_themes()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        default_settings = {
            'theme': 'App_Factory',
            'system_theme_detection': True,
            'mui_tabs_enabled': True,
            'bg_primary_image': '',
            'bg_secondary_image': '',
            'panel_bg_image': '',
            'bg_primary_mode': 'stretch',
            'bg_secondary_mode': 'stretch',
            'panel_bg_mode': 'stretch',
            'bg_primary_opacity': 100,
            'bg_secondary_opacity': 100,
            'panel_bg_opacity': 100,
        }
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                settings = default_settings.copy()
                settings.update(loaded_settings)
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2, ensure_ascii=False)
            print(f"Settings saved to: {self.settings_file}")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def detect_and_save_system_theme(self) -> Dict[str, Any]:
        """Detect system theme and save as compatible theme"""
        system_theme = self.system_theme_detector.detect_system_theme()
        
        # Create a compatible theme structure
        theme_data = {
            "name": f"System Theme ({system_theme.get('system_theme', 'unknown')})",
            "description": "System theme detected automatically",
            "category": "System",
            "author": "System",
            "version": "1.0",
            "colors": {
                "bg_primary": system_theme.get("window_color", "#F0F0F0"),
                "bg_secondary": system_theme.get("window_color", "#F0F0F0"),
                "bg_tertiary": "#E0E0E0",
                "panel_bg": system_theme.get("window_color", "#F0F0F0"),
                "accent_primary": system_theme.get("accent_color", "#0078D4"),
                "accent_secondary": system_theme.get("highlight_color", "#005A9E"),
                "text_primary": system_theme.get("text_color", "#000000"),
                "text_secondary": "#666666",
                "text_accent": system_theme.get("highlight_color", "#0078D4"),
                "button_normal": "#E0E0E0",
                "button_hover": "#D0D0D0",
                "button_pressed": "#C0C0C0",
                "border": "#CCCCCC",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "error": "#F44336",
                "grid": "#E0E0E0",
                "pin_default": "#757575",
                "pin_highlight": system_theme.get("highlight_color", "#0078D4"),
                "action_import": system_theme.get("accent_color", "#2196F3"),
                "action_export": "#4CAF50",
                "action_remove": "#F44336",
                "action_update": "#FF9800",
                "action_convert": "#9C27B0"
            },
            "mui_settings": {
                "system_detected": True,
                "is_dark_mode": system_theme.get("is_dark_mode", False),
                "original_system_theme": system_theme.get("system_theme", "unknown")
            }
        }
        
        # Save as a theme file
        theme_name = f"system_{system_theme.get('system_theme', 'unknown')}"
        success = self.save_theme(theme_name, theme_data)
        
        if success:
            print(f"System theme saved as: {theme_name}")
            return theme_data
        else:
            print(f"Failed to save system theme as: {theme_name}")
            return {}
    
    def save_theme(self, theme_name: str, theme_data: Dict[str, Any]) -> bool:
        """Save theme data to JSON file in themes directory"""
        try:
            # Determine themes directory
            themes_dir = Path("apps/themes")
            themes_dir.mkdir(parents=True, exist_ok=True)
            
            # Create safe filename
            safe_name = theme_name.lower().replace(' ', '_').replace('/', '_')
            theme_file = themes_dir / f"{safe_name}.json"
            
            # Write theme to file
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            print(f"Theme saved: {theme_file}")
            return True
        except Exception as e:
            print(f"Failed to save theme: {e}")
            return False
    
    def _load_mui_themes(self) -> Dict[str, Any]:
        """Load existing Amiga MUI themes"""
        mui_themes = {}
        themes_dir = Path("apps/themes")
        
        if themes_dir.exists():
            for theme_file in themes_dir.glob("*mui*.json"):
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                        theme_name = theme_file.stem
                        mui_themes[theme_name] = theme_data
                except Exception as e:
                    print(f"Error loading MUI theme {theme_file.name}: {e}")
        
        return mui_themes
    
    def get_mui_theme_features(self) -> List[str]:
        """Get list of features supported by Amiga MUI"""
        return [
            "Intuitive interface design",
            "Screen modes and display handling",
            "Intuition menus and gadgets",
            "Image and brush handling",
            "Font management",
            "Window and screen management",
            "GadTools for standard gadgets",
            "EasyRequest for dialogs",
            "Color management and pens",
            "Virtual screen handling",
            "Drag and drop support",
            "Multiple screen support",
            "Intuitive file selection",
            "Configurable user interface",
            "Image mapping and masking",
            "Pattern and brush support",
            "Font and text rendering",
            "Window layering and management"
        ]
    
    def create_mui_tab_widget(self) -> AmigaMUITabWidget:
        """Create an Amiga MUI style tab widget"""
        tab_widget = AmigaMUITabWidget()
        
        # Apply current image settings
        tab_widget.set_image_backgrounds(self.image_settings)
        
        # Apply transparency settings
        tab_widget.set_transparency(
            self.current_settings.get('titlebar_transparency', 0.9),
            self.current_settings.get('panel_transparency', 0.95)
        )
        
        # Apply shadow effects settings
        tab_widget.enable_shadow_effects(
            self.current_settings.get('shadow_effects_enabled', True),
            self.current_settings.get('button_shadow_depth', 2),
            self.current_settings.get('panel_shadow_depth', 3)
        )
        
        return tab_widget
    
    def set_transparency_settings(self, titlebar_transparency: float = 0.9, panel_transparency: float = 0.95):
        """Set transparency settings"""
        self.current_settings['titlebar_transparency'] = titlebar_transparency
        self.current_settings['panel_transparency'] = panel_transparency
    
    def set_shadow_settings(self, shadow_enabled: bool = True, button_depth: int = 2, panel_depth: int = 3):
        """Set shadow effect settings"""
        self.current_settings['shadow_effects_enabled'] = shadow_enabled
        self.current_settings['button_shadow_depth'] = button_depth
        self.current_settings['panel_shadow_depth'] = panel_depth
    
    def create_mui_gadget(self, gadget_type: str, **kwargs):
        """Create an Amiga MUI style gadget using the tab widget"""
        tab_widget = self.create_mui_tab_widget()
        return tab_widget.create_mui_gadget(gadget_type, **kwargs)
    
    def create_mui_components(self):
        """Create various Amiga MUI components"""
        components = {}
        
        # Create a tab widget
        components['tab_widget'] = self.create_mui_tab_widget()
        
        # Create a group
        group, layout = components['tab_widget'].create_mui_group("Example Group")
        components['group'] = group
        components['group_layout'] = layout
        
        # Create various gadgets
        components['string_input'] = components['tab_widget'].create_mui_gadget('string', text="Example text")
        components['slider'] = components['tab_widget'].create_mui_gadget('slider')
        components['list'] = components['tab_widget'].create_mui_gadget('list')
        components['colorfield'] = components['tab_widget'].create_mui_gadget('colorfield')
        components['palette'] = components['tab_widget'].create_mui_gadget('palette')
        
        # Create other UI elements
        components['scrollbar'] = components['tab_widget'].create_mui_scrollbar()
        components['listview'] = components['tab_widget'].create_mui_listview()
        components['register'] = components['tab_widget'].create_mui_register(["Tab 1", "Tab 2", "Tab 3"])
        components['scrollgroup'] = components['tab_widget'].create_mui_scrollgroup()
        components['virtgroup'] = components['tab_widget'].create_mui_virtgroup()
        
        return components


def main():
    """Example usage of the system settings"""
    app = QApplication(sys.argv)
    
    # Create system settings instance
    system_settings = AppSystemSettings()
    
    # Detect and save system theme
    print("Detecting system theme...")
    system_theme_data = system_settings.detect_and_save_system_theme()
    
    if system_theme_data:
        print("System theme detected and saved successfully!")
        print(f"Theme name: {system_theme_data['name']}")
        print(f"Is dark mode: {system_theme_data['mui_settings'].get('is_dark_mode', False)}")
    else:
        print("Failed to detect system theme")
    
    # Show available MUI features
    print("\nAmiga MUI supported features:")
    for feature in system_settings.get_mui_theme_features():
        print(f"  - {feature}")
    
    # Create and show a simple window with MUI tab
    window = QMainWindow()
    window.setWindowTitle("IMG Factory - Amiga MUI Style")
    window.setGeometry(100, 100, 1000, 700)
    
    # Create MUI components
    components = system_settings.create_mui_components()
    main_tab_widget = components['tab_widget']
    
    # Add some example tabs with various gadgets
    tab1 = QWidget()
    tab1_layout = QVBoxLayout(tab1)
    
    # Add a group with various gadgets
    group, group_layout = components['group'], components['group_layout']
    
    # Add different types of gadgets to the group
    group_layout.addWidget(QLabel("String Input:"))
    group_layout.addWidget(components['string_input'])
    
    group_layout.addWidget(QLabel("Slider:"))
    group_layout.addWidget(components['slider'])
    
    group_layout.addWidget(QLabel("List:"))
    group_layout.addWidget(components['list'])
    for i in range(5):
        components['list'].addItem(f"Item {i+1}")
    
    group_layout.addWidget(QLabel("Color Field:"))
    group_layout.addWidget(components['colorfield'])
    
    group_layout.addWidget(QLabel("Color Palette:"))
    group_layout.addWidget(components['palette'])
    
    tab1_layout.addWidget(group)
    
    # Add a separator
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    tab1_layout.addWidget(separator)
    
    # Add more controls
    tab1_layout.addWidget(QLabel("Additional MUI Components:"))
    
    # Add a register (tabbed interface)
    tab1_layout.addWidget(QLabel("Register (Tabbed Interface):"))
    tab1_layout.addWidget(components['register'])
    
    # Add listview
    tab1_layout.addWidget(QLabel("Listview:"))
    tab1_layout.addWidget(components['listview'])
    for i in range(3):
        components['listview'].addItem(f"ListView Item {i+1}")
    
    # Add scrollgroup
    scrollgroup_widget, scrollgroup_layout, scroll_area, scroll_content = components['scrollgroup']
    tab1_layout.addWidget(QLabel("Scrollgroup:"))
    tab1_layout.addWidget(scrollgroup_widget)
    
    # Add content to scroll area
    for i in range(10):
        label = QLabel(f"Scrollable content item {i+1}")
        scroll_content.layout().addWidget(label)
    
    main_tab_widget.addTab(tab1, "Advanced Gadgets")
    
    # Create second tab with more traditional controls
    tab2 = QWidget()
    tab2_layout = QVBoxLayout(tab2)
    
    # Create various gadgets directly
    string_gadget = main_tab_widget.create_mui_gadget('string', text="Direct gadget creation")
    tab2_layout.addWidget(QLabel("String Gadget:"))
    tab2_layout.addWidget(string_gadget)
    
    numeric_gadget = main_tab_widget.create_mui_gadget('numeric', minimum=0, maximum=100, value=50)
    tab2_layout.addWidget(QLabel("Numeric Gadget:"))
    tab2_layout.addWidget(numeric_gadget)
    
    gauge_gadget = main_tab_widget.create_mui_gadget('gauge')
    gauge_gadget.setValue(75)
    tab2_layout.addWidget(QLabel("Gauge Gadget:"))
    tab2_layout.addWidget(gauge_gadget)
    
    cycle_gadget = main_tab_widget.create_mui_gadget('cycle')
    cycle_gadget.addItems(["Option 1", "Option 2", "Option 3"])
    tab2_layout.addWidget(QLabel("Cycle Gadget:"))
    tab2_layout.addWidget(cycle_gadget)
    
    knob_gadget = main_tab_widget.create_mui_gadget('knob', minimum=0, maximum=100, value=30)
    tab2_layout.addWidget(QLabel("Knob Gadget:"))
    tab2_layout.addWidget(knob_gadget)
    
    # Add radio buttons
    radio_layout = QHBoxLayout()
    for i in range(3):
        radio = main_tab_widget.create_mui_gadget('radio', text=f"Radio {i+1}")
        radio_layout.addWidget(radio)
    tab2_layout.addWidget(QLabel("Radio Gadgets:"))
    tab2_layout.addLayout(radio_layout)
    
    main_tab_widget.addTab(tab2, "Basic Gadgets")
    
    # Set the main tab widget as central widget
    window.setCentralWidget(main_tab_widget)
    
    # Add a menu for testing new features
    menu_bar = window.menuBar()
    settings_menu = menu_bar.addMenu("Settings")
    gadgets_menu = menu_bar.addMenu("Gadgets")
    
    def toggle_transparency():
        current_transparency = system_settings.current_settings.get('panel_transparency', 0.95)
        new_transparency = 0.5 if current_transparency > 0.7 else 0.95
        system_settings.set_transparency_settings(panel_transparency=new_transparency)
        main_tab_widget.set_transparency(
            system_settings.current_settings.get('titlebar_transparency', 0.9),
            new_transparency
        )
        print(f"Transparency set to {new_transparency}")
    
    def toggle_shadows():
        current_shadows = system_settings.current_settings.get('shadow_effects_enabled', True)
        system_settings.set_shadow_settings(shadow_enabled=not current_shadows)
        main_tab_widget.enable_shadow_effects(not current_shadows)
        print(f"Shadows {'enabled' if not current_shadows else 'disabled'}")
    
    def add_new_gadget():
        # Create a new tab with a random gadget
        gadget_types = ['string', 'gauge', 'scale', 'colorfield', 'list', 'numeric', 'knob', 'levelmeter', 'slider', 'radio', 'cycle', 'palette']
        import random
        selected_type = random.choice(gadget_types)
        
        new_tab = QWidget()
        new_layout = QVBoxLayout(new_tab)
        new_layout.addWidget(QLabel(f"Random Gadget: {selected_type}"))
        
        gadget = main_tab_widget.create_mui_gadget(selected_type)
        if gadget:
            new_layout.addWidget(gadget)
        else:
            new_layout.addWidget(QLabel("Gadget creation failed"))
        
        main_tab_widget.addTab(new_tab, f"Random {selected_type}")
        print(f"Added new gadget: {selected_type}")
    
    transparency_action = settings_menu.addAction("Toggle Transparency")
    transparency_action.triggered.connect(toggle_transparency)
    
    shadow_action = settings_menu.addAction("Toggle Shadows")
    shadow_action.triggered.connect(toggle_shadows)
    
    gadget_action = gadgets_menu.addAction("Add Random Gadget")
    gadget_action.triggered.connect(add_new_gadget)
    
    # Add a status bar
    status_bar = window.statusBar()
    status_bar.showMessage("Amiga MUI System Ready")
    
    window.show()
    
    # Save settings
    system_settings.save_settings()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()