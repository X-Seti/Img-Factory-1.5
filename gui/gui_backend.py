#this belongs in gui/gui_backend.py - Version: 1 
# X-Seti - July14 2025 - Img Factory 1.5
# GUI backend functionality separated from layout

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QProgressBar, QTextEdit, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon


class ButtonDisplayMode:
    """Button display mode constants"""
    TEXT_ONLY = "text_only"
    ICONS_ONLY = "icons_only" 
    ICONS_WITH_TEXT = "icons_with_text"


class GUIBackend:
    """Backend functionality for GUI layout"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.button_display_mode = ButtonDisplayMode.TEXT_ONLY  # Default: no icons
        
        # Button collections
        self.img_buttons = []
        self.entry_buttons = []
        self.options_buttons = []
        
        # UI References
        self.table = None
        self.log = None
        self.progress_bar = None
        self.status_label = None
        self.tab_widget = None
        
        # Theme colors cache
        self._theme_colors_cache = {}
    
    def set_button_display_mode(self, mode):
        """Set button display mode and update all buttons"""
        if mode not in [ButtonDisplayMode.TEXT_ONLY, ButtonDisplayMode.ICONS_ONLY, ButtonDisplayMode.ICONS_WITH_TEXT]:
            return False
        
        self.button_display_mode = mode
        self._update_all_button_displays()
        return True
    
    def _update_all_button_displays(self):
        """Update display for all buttons based on current mode"""
        all_buttons = self.img_buttons + self.entry_buttons + self.options_buttons
        
        for btn in all_buttons:
            self._update_button_display(btn)
    
    def _update_button_display(self, btn):
        """Update individual button display based on mode"""
        if not hasattr(btn, 'full_text') or not hasattr(btn, 'short_text'):
            return
        
        if self.button_display_mode == ButtonDisplayMode.TEXT_ONLY:
            btn.setText(btn.short_text)
            btn.setIcon(QIcon())  # Remove icon
            btn.setToolTip(btn.full_text)
            
        elif self.button_display_mode == ButtonDisplayMode.ICONS_ONLY:
            btn.setText("")
            if hasattr(btn, 'icon_name'):
                btn.setIcon(self._safe_load_icon(btn.icon_name))
            btn.setToolTip(btn.full_text)
            
        elif self.button_display_mode == ButtonDisplayMode.ICONS_WITH_TEXT:
            btn.setText(btn.short_text)
            if hasattr(btn, 'icon_name'):
                btn.setIcon(self._safe_load_icon(btn.icon_name))
            btn.setToolTip(btn.full_text)
    
    def _safe_load_icon(self, icon_name):
        """Safely load icon with fallback"""
        if not icon_name:
            return QIcon()
        
        try:
            # Try theme icon first
            theme_icon = QIcon.fromTheme(icon_name)
            if theme_icon and not theme_icon.isNull():
                return theme_icon
        except Exception:
            pass
        
        # Try local icon paths
        try:
            icon_paths = [
                f"icons/{icon_name}.png",
                f"gui/icons/{icon_name}.png",
                f"resources/icons/{icon_name}.png"
            ]
            
            for path in icon_paths:
                import os
                if os.path.exists(path):
                    local_icon = QIcon(path)
                    if local_icon and not local_icon.isNull():
                        return local_icon
        except Exception:
            pass
        
        # Return empty icon as fallback
        return QIcon()
    
    def create_pastel_button(self, label, action_type, icon_name, bg_color, method_name):
        """Create a button with pastel coloring and proper display mode handling"""
        btn = QPushButton()
        btn.setMaximumHeight(22)
        btn.setMinimumHeight(20)
        
        # Store button properties
        btn.full_text = label
        btn.short_text = self._get_short_text(label)
        btn.icon_name = icon_name
        btn.action_type = action_type
        btn.method_name = method_name
        
        # Apply initial display based on current mode
        self._update_button_display(btn)
        
        # Apply pastel styling
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 8pt;
                font-weight: bold;
                color: #333333;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(bg_color, 0.1)};
                border: 1px solid #aaaaaa;
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(bg_color, 0.1)};
                border: 1px solid #888888;
            }}
        """)
        
        # Connect to method if it exists
        if hasattr(self.main_window, method_name):
            btn.clicked.connect(getattr(self.main_window, method_name))
        else:
            # Log missing method and connect placeholder
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ Missing method: {method_name}")
            btn.clicked.connect(lambda: self._placeholder_function(method_name))
        
        return btn
    
    def _placeholder_function(self, method_name):
        """Placeholder for missing methods"""
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"⚠️ Method '{method_name}' not implemented")
    
    def _get_short_text(self, label):
        """Get short text for button"""
        short_text_map = {
            "New": "New",
            "Open": "Open", 
            "Close": "Close",
            "Close All": "Close All",
            "Rebuild": "Rebuild",
            "Rebuild As": "Rebuild As",
            "Rebuild All": "Rebuild All",
            "Merge": "Merge",
            "Split": "Split",
            "Convert": "Convert",
            "Import": "Import",
            "Import via": "Import>",
            "🔄 Refresh": "Refresh",
            "Export": "Export",
            "Export via": "Export>",
            "Quick Export": "Quick Export",
            "Remove": "Remove",
            "Remove via": "Remove>",
            "Dump": "Dump",
            "Pin selected": "Pin",
            "Rename": "Rename",
            "Replace": "Replace",
            "Select All": "Select All",
            "Sel Inverse": "Sel Inverse",
            "Sort": "Sort",
            # Editing Options
            "Col Edit": "Col Edit",
            "Txd Edit": "Txd Edit",
            "Dff Edit": "Dff Edit",
            "Ipf Edit": "Ipf Edit",
            "IDE Edit": "IDE Edit",
            "IPL Edit": "IPL Edit",
            "Dat Edit": "Dat Edit",
            "Zons Cull Ed": "Zons Cull",
            "Weap Edit": "Weap Edit",
            "Vehi Edit": "Vehi Edit",
            "Peds Edit": "Peds Edit",
            "Radar Map": "Radar Map",
            "Paths Map": "Paths Map",
            "Waterpro": "Waterpro",
            "Weather": "Weather",
            "Handling": "Handling",
            "Objects": "Objects",
        }
        
        return short_text_map.get(label, label)
    
    def _lighten_color(self, color, factor):
        """Lighten a hex color by factor (0.0 to 1.0)"""
        try:
            color = color.lstrip('#')
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color
    
    def _darken_color(self, color, factor):
        """Darken a hex color by factor (0.0 to 1.0)"""
        try:
            color = color.lstrip('#')
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color
    
    def get_theme_colors(self, theme_name="default"):
        """Get theme colors with caching"""
        if theme_name in self._theme_colors_cache:
            return self._theme_colors_cache[theme_name]
        
        # Default theme colors
        colors = {
            'background': 'f5f5f5',
            'text': '333333',
            'accent': '2196f3',
            'splitter_color_background': '777777',
            'splitter_color_shine': '787878',
            'splitter_color_shadow': '757575'
        }
        
        # Try to get colors from app settings
        try:
            if hasattr(self.main_window, 'app_settings'):
                settings_colors = self.main_window.app_settings.current_settings.get('theme_colors', {})
                colors.update(settings_colors)
        except Exception:
            pass
        
        self._theme_colors_cache[theme_name] = colors
        return colors
    
    def apply_settings_changes(self, settings):
        """Apply settings changes to the GUI backend"""
        try:
            # Handle button display mode changes
            if 'button_display_mode' in settings:
                self.set_button_display_mode(settings['button_display_mode'])
            
            # Handle theme changes
            if any(key.startswith('theme') for key in settings.keys()):
                self._theme_colors_cache.clear()  # Clear cache
            
            # Handle other settings
            if 'table_row_height' in settings and self.table:
                self.table.verticalHeader().setDefaultSectionSize(settings['table_row_height'])
            
            return True
            
        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error applying backend settings: {str(e)}")
            return False
    
    def update_button_states(self, img_loaded=False, entries_selected=False):
        """Update button states based on current state"""
        try:
            # Define which buttons depend on what
            img_dependent_buttons = {
                'import', 'import_via', 'refresh', 'export', 'export_via', 
                'quick_export', 'remove', 'remove_via', 'dump', 'select_all',
                'sel_inverse', 'sort', 'rebuild', 'rebuild_as', 'save'
            }
            
            selection_dependent_buttons = {
                'export', 'export_via', 'quick_export', 'remove', 'remove_via',
                'pin_selected', 'rename', 'replace'
            }
            
            # Update all buttons
            all_buttons = self.img_buttons + self.entry_buttons + self.options_buttons
            
            for btn in all_buttons:
                if hasattr(btn, 'action_type'):
                    action_type = btn.action_type
                    
                    if action_type in img_dependent_buttons:
                        btn.setEnabled(img_loaded)
                    elif action_type in selection_dependent_buttons:
                        btn.setEnabled(img_loaded and entries_selected)
                    else:
                        btn.setEnabled(True)  # Always enabled buttons
            
        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error updating button states: {str(e)}")


# Export classes
__all__ = [
    'GUIBackend',
    'ButtonDisplayMode'
]