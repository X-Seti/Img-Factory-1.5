#!/usr/bin/env python3
"""
X-Seti - June05, 2023 - Light Pastel Button Theme Template for IMG Factory
Creates soft, modern button styling with action-type specific colors
"""

def get_pastel_button_stylesheet(app_settings):
    """
    Generate pastel button stylesheet based on current theme
    """
    theme = app_settings.get_theme()
    colors = theme["colors"]
    
    # Define light pastel colors for different action types
    pastel_colors = {
        # Import actions - Soft Blue
        "import": {
            "normal": "#E3F2FD",      # Light blue
            "hover": "#BBDEFB",       # Medium blue
            "pressed": "#90CAF9",     # Darker blue
            "border": "#2196F3",      # Blue border
            "text": "#1565C0"         # Dark blue text
        },
        
        # Export actions - Soft Green
        "export": {
            "normal": "#E8F5E8",      # Light green
            "hover": "#C8E6C9",       # Medium green
            "pressed": "#A5D6A7",     # Darker green
            "border": "#4CAF50",      # Green border
            "text": "#2E7D32"         # Dark green text
        },
        
        # Remove actions - Soft Red
        "remove": {
            "normal": "#FFEBEE",      # Light red
            "hover": "#FFCDD2",       # Medium red
            "pressed": "#EF9A9A",     # Darker red
            "border": "#F44336",      # Red border
            "text": "#C62828"         # Dark red text
        },
        
        # Update actions - Soft Orange
        "update": {
            "normal": "#FFF3E0",      # Light orange
            "hover": "#FFE0B2",       # Medium orange
            "pressed": "#FFCC02",     # Darker orange
            "border": "#FF9800",      # Orange border
            "text": "#E65100"         # Dark orange text
        },
        
        # Convert actions - Soft Purple
        "convert": {
            "normal": "#F3E5F5",      # Light purple
            "hover": "#E1BEE7",       # Medium purple
            "pressed": "#CE93D8",     # Darker purple
            "border": "#9C27B0",      # Purple border
            "text": "#6A1B9A"         # Dark purple text
        },
        
        # Default actions - Soft Gray
        "default": {
            "normal": "#F5F5F5",      # Light gray
            "hover": "#EEEEEE",       # Medium gray
            "pressed": "#E0E0E0",     # Darker gray
            "border": "#9E9E9E",      # Gray border
            "text": "#424242"         # Dark gray text
        }
    }
    
    # Build the comprehensive stylesheet
    stylesheet = """
    /* Base QPushButton styling */
    QPushButton {
        background-color: #F5F5F5;
        border: 2px solid #9E9E9E;
        border-radius: 8px;
        padding: 8px 16px;
        color: #424242;
        font-weight: bold;
        min-height: 24px;
        min-width: 80px;
        text-align: center;
    }
    
    QPushButton:hover {
        background-color: #EEEEEE;
        border-color: #757575;
        transform: translateY(-1px);
    }
    
    QPushButton:pressed {
        background-color: #E0E0E0;
        border-color: #616161;
        transform: translateY(1px);
    }
    
    QPushButton:disabled {
        background-color: #FAFAFA;
        border-color: #E0E0E0;
        color: #BDBDBD;
    }
    """
    
    # Add action-type specific styling
    for action_type, action_colors in pastel_colors.items():
        if action_type == "default":
            continue  # Already handled in base styling
            
        stylesheet += f"""
    /* {action_type.title()} Action Buttons */
    QPushButton[action-type="{action_type}"] {{
        background-color: {action_colors["normal"]};
        border-color: {action_colors["border"]};
        color: {action_colors["text"]};
    }}
    
    QPushButton[action-type="{action_type}"]:hover {{
        background-color: {action_colors["hover"]};
        border-color: {action_colors["border"]};
    }}
    
    QPushButton[action-type="{action_type}"]:pressed {{
        background-color: {action_colors["pressed"]};
        border-color: {action_colors["border"]};
    }}
    """
    
    # Add special styling for grouped buttons
    stylesheet += """
    /* Grouped button styling */
    QGroupBox QPushButton {
        margin: 2px;
        font-size: 9pt;
    }
    
    /* Large action buttons */
    QPushButton[bold="true"] {
        font-size: 10pt;
        font-weight: bold;
        min-height: 32px;
        padding: 10px 20px;
    }
    
    /* Icon buttons */
    QPushButton[icon-only="true"] {
        min-width: 40px;
        max-width: 40px;
        padding: 8px;
    }
    
    /* Toolbar buttons */
    QGroupBox[title="IMG Operations"] QPushButton,
    QGroupBox[title="Entry Operations"] QPushButton {
        border-radius: 6px;
        font-size: 9pt;
        padding: 6px 12px;
        min-height: 28px;
    }
    
    /* Filter section styling */
    QGroupBox[title="Filter & Search"] QPushButton {
        min-width: 32px;
        max-width: 40px;
        border-radius: 4px;
    }
    """
    
    return stylesheet


def apply_pastel_theme_to_buttons(app, app_settings):
    """
    Apply the pastel button theme to the entire application
    """
    # Get the button stylesheet
    button_style = get_pastel_button_stylesheet(app_settings)
    
    # Get the existing application stylesheet
    existing_style = app.styleSheet()
    
    # Combine with existing theme
    combined_style = existing_style + "\n\n" + button_style
    
    # Apply to application
    app.setStyleSheet(combined_style)


# Alternative: Apply only to specific widgets
def apply_pastel_theme_to_widget(widget, app_settings):
    """
    Apply pastel theme to a specific widget and its children
    """
    button_style = get_pastel_button_stylesheet(app_settings)
    
    # Apply to the widget
    existing_style = widget.styleSheet()
    combined_style = existing_style + "\n\n" + button_style
    widget.setStyleSheet(combined_style)


# Example usage in your ImgFactoryDemo class:
"""
# In your ImgFactoryDemo.__init__ method, after creating the UI:

# Apply pastel button theme
apply_pastel_theme_to_buttons(app, self.app_settings)

# Or apply to specific widget:
# apply_pastel_theme_to_widget(self, self.app_settings)
"""

# Color reference for manual button creation:
PASTEL_ACTION_COLORS = {
    "import": "#E3F2FD",    # Light Blue
    "export": "#E8F5E8",    # Light Green  
    "remove": "#FFEBEE",    # Light Red
    "update": "#FFF3E0",    # Light Orange
    "convert": "#F3E5F5",   # Light Purple
    "default": "#F5F5F5"    # Light Gray
}

# Usage example for individual button styling:
def style_action_button(button, action_type="default"):
    """
    Apply pastel styling to individual button
    """
    color = PASTEL_ACTION_COLORS.get(action_type, PASTEL_ACTION_COLORS["default"])
    
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            border: 2px solid #BDBDBD;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: {darken_color(color, 0.1)};
            border-color: #9E9E9E;
        }}
        QPushButton:pressed {{
            background-color: {darken_color(color, 0.2)};
        }}
    """)

def darken_color(hex_color, factor):
    """Helper function to darken a hex color"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))  
    b = max(0, int(b * (1 - factor)))
    
    return f"#{r:02x}{g:02x}{b:02x}"
