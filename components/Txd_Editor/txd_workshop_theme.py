#this belongs in components/Txd_Workshop/ txd_workshop_theme.py - Version: 1
# X-Seti - September26 2025 - Img Factory 1.5 - TXD Workshop Theme Support

"""
TXD Workshop Theme Integration - Applies IMG Factory themes to TXD Workshop
"""

##Methods list -
# apply_theme_to_workshop
# get_workshop_stylesheet
# update_workshop_theme

def apply_theme_to_workshop(workshop, main_window=None): #vers 1
    """Apply current theme from main window to TXD Workshop"""
    try:
        # Get app_settings from main window
        if main_window and hasattr(main_window, 'app_settings'):
            app_settings = main_window.app_settings

            # Get current theme name
            theme_name = app_settings.current_settings.get("theme", "IMG_Factory")

            # Get theme colors
            theme_colors = app_settings.get_theme_colors(theme_name)

            # Generate stylesheet
            stylesheet = get_workshop_stylesheet(theme_colors)

            # Apply to workshop window
            workshop.setStyleSheet(stylesheet)

            # Store theme info for updates
            workshop._current_theme = theme_name
            workshop._theme_colors = theme_colors

            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"🎨 TXD Workshop theme applied: {theme_name}")

            return True
        else:
            # Use default dark theme if no main window
            default_colors = {
                'bg_primary': '#2b2b2b',
                'bg_secondary': '#1e1e1e',
                'bg_tertiary': '#3a3a3a',
                'text_primary': '#e0e0e0',
                'text_secondary': '#b0b0b0',
                'accent_primary': '#0d47a1',
                'border': '#3a3a3a',
                'button_normal': '#3a3a3a',
                'button_hover': '#4a4a4a',
                'button_pressed': '#2a2a2a'
            }
            stylesheet = get_workshop_stylesheet(default_colors)
            workshop.setStyleSheet(stylesheet)
            return True

    except Exception as e:
        print(f"❌ TXD Workshop theme error: {str(e)}")
        return False

def get_workshop_stylesheet(theme_colors): #vers 1
    """Generate TXD Workshop stylesheet from theme colors"""

    # Extract colors with fallbacks
    bg_primary = theme_colors.get('bg_primary', '#2b2b2b')
    bg_secondary = theme_colors.get('bg_secondary', '#1e1e1e')
    bg_tertiary = theme_colors.get('bg_tertiary', '#3a3a3a')
    text_primary = theme_colors.get('text_primary', '#e0e0e0')
    text_secondary = theme_colors.get('text_secondary', '#b0b0b0')
    accent_primary = theme_colors.get('accent_primary', '#0d47a1')
    border = theme_colors.get('border', '#3a3a3a')
    button_normal = theme_colors.get('button_normal', '#3a3a3a')
    button_hover = theme_colors.get('button_hover', '#4a4a4a')
    button_pressed = theme_colors.get('button_pressed', '#2a2a2a')

    stylesheet = f"""
    /* Main Window */
    QWidget {{
        background-color: {bg_primary};
        color: {text_primary};
        font-family: Arial, sans-serif;
    }}

    /* Frames and Panels */
    QFrame {{
        background-color: {bg_secondary};
        border: 1px solid {border};
    }}

    /* List Widgets */
    QListWidget {{
        background-color: {bg_secondary};
        border: 1px solid {border};
        padding: 5px;
        color: {text_primary};
    }}

    QListWidget::item {{
        padding: 5px;
        border-radius: 2px;
    }}

    QListWidget::item:selected {{
        background-color: {accent_primary};
        color: white;
    }}

    QListWidget::item:hover {{
        background-color: {bg_tertiary};
    }}

    /* Table Widget */
    QTableWidget {{
        background-color: {bg_secondary};
        border: 1px solid {border};
        gridline-color: {border};
        color: {text_primary};
    }}

    QTableWidget::item {{
        padding: 5px;
    }}

    QTableWidget::item:selected {{
        background-color: {accent_primary};
        color: white;
    }}

    QHeaderView::section {{
        background-color: {bg_tertiary};
        color: {text_primary};
        padding: 5px;
        border: 1px solid {border};
        font-weight: bold;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {button_normal};
        border: 1px solid {border};
        padding: 5px 15px;
        border-radius: 3px;
        color: {text_primary};
        font-weight: normal;
    }}

    QPushButton:hover {{
        background-color: {button_hover};
    }}

    QPushButton:pressed {{
        background-color: {button_pressed};
    }}

    QPushButton:disabled {{
        background-color: {bg_tertiary};
        color: {text_secondary};
    }}

    /* Labels */
    QLabel {{
        color: {text_primary};
        padding: 2px;
    }}

    /* Group Boxes */
    QGroupBox {{
        border: 1px solid {border};
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
        color: {text_primary};
        font-weight: bold;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        color: {text_primary};
    }}

    /* Preview Label */
    QLabel#preview_label {{
        border: 1px solid {border};
        background-color: {bg_secondary};
    }}

    /* Toolbar */
    QFrame#toolbar {{
        background-color: {bg_tertiary};
        border-bottom: 1px solid {border};
    }}

    /* Splitter */
    QSplitter::handle {{
        background-color: {border};
        width: 3px;
        height: 3px;
    }}

    QSplitter::handle:hover {{
        background-color: {accent_primary};
    }}
    """

    return stylesheet

def update_workshop_theme(workshop, theme_name, main_window=None): #vers 1
    """Update TXD Workshop theme when theme changes"""
    try:
        if main_window and hasattr(main_window, 'app_settings'):
            app_settings = main_window.app_settings

            # Get new theme colors
            theme_colors = app_settings.get_theme_colors(theme_name)

            # Generate and apply new stylesheet
            stylesheet = get_workshop_stylesheet(theme_colors)
            workshop.setStyleSheet(stylesheet)

            # Update stored theme info
            workshop._current_theme = theme_name
            workshop._theme_colors = theme_colors

            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"🎨 TXD Workshop theme updated: {theme_name}")

            return True

        return False

    except Exception as e:
        print(f"❌ TXD Workshop theme update error: {str(e)}")
        return False

def connect_workshop_to_theme_system(workshop, main_window): #vers 1
    """Connect TXD Workshop to main window's theme change signal"""
    try:
        if main_window and hasattr(main_window, 'app_settings'):
            # Connect to theme change signal if available
            if hasattr(main_window.app_settings, 'themeChanged'):
                main_window.app_settings.themeChanged.connect(
                    lambda theme_name: update_workshop_theme(workshop, theme_name, main_window)
                )

                if hasattr(main_window, 'log_message'):
                    main_window.log_message("🔗 TXD Workshop connected to theme system")

                return True

        return False

    except Exception as e:
        print(f"❌ TXD Workshop theme connection error: {str(e)}")
        return False
