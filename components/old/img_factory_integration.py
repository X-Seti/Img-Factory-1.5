#!/usr/bin/env python3
"""
IMG Factory Integration - Adding New IMG Creation Functionality
Integration guide for adding the new IMG creation feature to your existing ImgFactoryDemo
"""

# ADD THIS TO YOUR imgfactory_demo.py imports section:
from new_img_creator import NewIMGDialog, IMGCreator, GameType, add_new_img_functionality

class ImgFactoryDemo(QMainWindow):
    def __init__(self, app_settings):
        super().__init__()
        # ... existing initialization code ...
        
        # ADD THIS LINE after your existing UI creation:
        self._add_new_img_functionality()
    
    def _add_new_img_functionality(self):
        """Add new IMG creation functionality to the interface"""
        # Method 1: Add to menu (existing _create_menu method)
        pass
    
    def _create_menu(self):
        """Modified version of your existing menu creation"""
        menubar = self.menuBar()

        # File Menu - MODIFIED
        file_menu = menubar.addMenu("File")
        
        show_menu_icons = self.app_settings.current_settings.get("show_menu_icons", True)
        
        # NEW: Add "New IMG" action first
        new_action = QAction("New IMG Archive...", self)
        if show_menu_icons:
            new_action.setIcon(QIcon.fromTheme("document-new"))
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.create_new_img)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()  # Separator after New
        
        # Existing Open action
        open_action = QAction("Open IMG...", self)
        if show_menu_icons:
            open_action.setIcon(QIcon.fromTheme("document-open"))
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_img_file)
        file_menu.addAction(open_action)
        
        # ... rest of existing file menu code ...
        
        # IMG Menu - MODIFIED to include New IMG
        img_menu = menubar.addMenu("IMG")
        
        # Add New IMG as first option
        new_img_action = QAction("New IMG Archive...", self)
        if show_menu_icons:
            new_img_action.setIcon(QIcon.fromTheme("document-new"))
        new_img_action.triggered.connect(self.create_new_img)
        img_menu.addAction(new_img_action)
        
        img_menu.addSeparator()
        
        # Existing IMG menu items
        rebuild_action = QAction("Rebuild", self)
        if show_menu_icons:
            rebuild_action.setIcon(QIcon.fromTheme("view-refresh"))
        rebuild_action.triggered.connect(self.rebuild_img)
        img_menu.addAction(rebuild_action)
        
        # ... rest of existing menu code ...
    
    def _create_right_panel(self):
        """Modified version to include New IMG button"""
        # ... existing right panel code ...
        
        # MODIFY your IMG Operations section:
        img_buttons = [
            ("🆕 New IMG", "import", "document-new", self.create_new_img),  # NEW
            ("📂 Open IMG", "import", "document-open", self.open_img_file),
            ("🔄 Refresh", "update", "view-refresh", self.refresh_table),
            ("❌ Close", None, "window-close", self.close_img_file),
            ("🔨 Rebuild", "update", "document-save", self.rebuild_img),
            ("💾 Rebuild As", None, "document-save-as", None),
            ("🔨 Rebuild All", None, "document-save", None),
            ("🔗 Merge", None, "document-merge", None),
            ("✂️ Split", None, "edit-cut", None),
            ("🔄 Convert", "convert", "transform", None),
        ]
        
        # ... rest of button creation code ...
    
    # NEW METHOD: Add this to your ImgFactoryDemo class
    def create_new_img(self):
        """Show new IMG creation dialog"""
        dialog = NewIMGDialog(self)
        
        # Connect success signal to load the new IMG
        dialog.img_created.connect(self.load_img_file)
        
        # Connect to update UI
        dialog.img_created.connect(lambda path: self.log_message(f"Created new IMG: {os.path.basename(path)}"))
        
        # Show dialog
        dialog.exec()
    
    # ENHANCED METHOD: Add advanced IMG creation with templates
    def create_new_img_with_template(self, game_type=None):
        """Create new IMG with specific game template"""
        dialog = NewIMGDialog(self)
        
        # Pre-select game type if specified
        if game_type:
            for button in dialog.game_button_group.buttons():
                if hasattr(button, 'game_type') and button.game_type == game_type:
                    button.setChecked(True)
                    dialog._on_game_type_changed(button)
                    break
        
        dialog.img_created.connect(self.load_img_file)
        dialog.exec()
    
    # NEW METHOD: Quick create functions for specific games
    def quick_create_gta3_img(self):
        """Quick create GTA III IMG"""
        self.create_new_img_with_template(GameType.GTA_III)
    
    def quick_create_gtavc_img(self):
        """Quick create GTA VC IMG"""
        self.create_new_img_with_template(GameType.GTA_VC)
    
    def quick_create_gtasa_img(self):
        """Quick create GTA SA IMG"""
        self.create_new_img_with_template(GameType.GTA_SA)
    
    def quick_create_bully_img(self):
        """Quick create Bully IMG"""
        self.create_new_img_with_template(GameType.BULLY)


# ENHANCED INTEGRATION: Add quick access toolbar
def create_enhanced_img_toolbar(main_window):
    """Create enhanced toolbar with new IMG options"""
    from PyQt6.QtWidgets import QToolBar, QAction, QMenu
    
    # Create toolbar
    toolbar = main_window.addToolBar("IMG Operations")
    toolbar.setMovable(False)
    
    # New IMG with dropdown menu
    new_img_action = QAction("🆕 New", main_window)
    new_img_action.setToolTip("Create new IMG archive")
    
    # Create dropdown menu for New IMG
    new_menu = QMenu(main_window)
    
    # Quick create actions
    quick_actions = [
        ("🏙️ GTA III Archive", main_window.quick_create_gta3_img),
        ("🌴 GTA VC Archive", main_window.quick_create_gtavc_img), 
        ("🏜️ GTA SA Archive", main_window.quick_create_gtasa_img),
        ("🏙️📱 LC Stories Archive", lambda: main_window.create_new_img_with_template(GameType.GTA_LC_STORIES)),
        ("🌴📱 VC Stories Archive", lambda: main_window.create_new_img_with_template(GameType.GTA_VC_STORIES)),
        ("🏫 Bully Archive", main_window.quick_create_bully_img),
        None,  # Separator
        ("⚙️ Custom Archive...", main_window.create_new_img)
    ]
    
    for action_data in quick_actions:
        if action_data is None:
            new_menu.addSeparator()
        else:
            text, callback = action_data
            action = new_menu.addAction(text)
            action.triggered.connect(callback)
    
    # Set menu on action (this creates a dropdown button)
    new_img_action.setMenu(new_menu)
    toolbar.addAction(new_img_action)
    
    # Add other toolbar actions
    toolbar.addSeparator()
    
    open_action = QAction("📂 Open", main_window)
    open_action.triggered.connect(main_window.open_img_file)
    toolbar.addAction(open_action)
    
    save_action = QAction("💾 Save", main_window) 
    save_action.triggered.connect(main_window.rebuild_img)
    toolbar.addAction(save_action)


# ADDITIONAL FEATURE: Recent templates and favorites
class IMGTemplateManager:
    """Manage user-defined IMG templates and recent settings"""
    
    def __init__(self, settings_path="img_templates.json"):
        self.settings_path = settings_path
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """Load user templates from file"""
        try:
            import json
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"user_templates": [], "recent_settings": []}
    
    def save_template(self, name, game_type, settings):
        """Save a user-defined template"""
        template = {
            "name": name,
            "game_type": game_type.value,
            "settings": settings,
            "created": time.time()
        }
        
        self.templates["user_templates"].append(template)
        self._save_templates()
    
    def get_user_templates(self):
        """Get list of user-defined templates"""
        return self.templates.get("user_templates", [])
    
    def _save_templates(self):
        """Save templates to file"""
        try:
            import json
            with open(self.settings_path, 'w') as f:
                json.dump(self.templates, f, indent=2)
        except Exception as e:
            print(f"Failed to save templates: {e}")


# INTEGRATION EXAMPLE: Complete integration in main function
def integrate_new_img_functionality():
    """
    Complete example of how to integrate the new IMG functionality
    Add this to your main imgfactory_demo.py file
    """
    
    # 1. Add imports at top of file:
    """
    from new_img_creator import (
        NewIMGDialog, IMGCreator, GameType, IMGTemplate,
        add_new_img_functionality
    )
    """
    
    # 2. Modify your ImgFactoryDemo.__init__ method:
    """
    def __init__(self, app_settings):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5 [Enhanced with New IMG Creation]")
        self.setGeometry(100, 100, 1100, 700)
        self.app_settings = app_settings
        
        # Current IMG file
        self.current_img: IMGFile = None
        self.load_thread: IMGLoadThread = None
        
        # NEW: Template manager
        self.template_manager = IMGTemplateManager()
        
        self._create_menu()
        self._create_status_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        self._create_main_ui_with_splitters(main_layout)
        
        # NEW: Add enhanced toolbar
        create_enhanced_img_toolbar(self)
    """
    
    # 3. Update your button creation in _create_right_panel:
    """
    img_buttons = [
        ("🆕 New IMG", "import", "document-new", self.create_new_img),
        ("📂 Open IMG", "import", "document-open", self.open_img_file),
        ("🔄 Refresh", "update", "view-refresh", self.refresh_table),
        # ... rest of your buttons
    ]
    """
    
    # 4. Add the new methods to your class:
    """
    # Add all the methods from the integration code above
    """


# BONUS: Advanced IMG creation with validation
class AdvancedIMGCreator(IMGCreator):
    """Enhanced IMG creator with validation and optimization"""
    
    def __init__(self, game_type: GameType):
        super().__init__(game_type)
        self.validation_errors = []
    
    def validate_creation_params(self, **params) -> bool:
        """Validate parameters before creation"""
        self.validation_errors = []
        
        # Check filename
        filename = params.get('filename', '')
        if not filename:
            self.validation_errors.append("Filename is required")
        elif len(filename) > 100:
            self.validation_errors.append("Filename too long (max 100 characters)")
        elif any(char in filename for char in r'<>:"/\|?*'):
            self.validation_errors.append("Filename contains invalid characters")
        
        # Check output directory
        output_dir = params.get('output_dir', '')
        if not output_dir:
            self.validation_errors.append("Output directory is required")
        elif not os.path.exists(output_dir):
            self.validation_errors.append("Output directory does not exist")
        elif not os.access(output_dir, os.W_OK):
            self.validation_errors.append("No write permission to output directory")
        
        # Check initial size
        initial_size = params.get('initial_size_mb', 0)
        if initial_size < 0:
            self.validation_errors.append("Initial size cannot be negative")
        elif initial_size > 4000:  # 4GB limit for most systems
            self.validation_errors.append("Initial size too large (max 4000 MB)")
        
        # Check available disk space
        try:
            import shutil
            free_space = shutil.disk_usage(output_dir).free
            required_space = initial_size * 1024 * 1024
            if required_space > free_space * 0.9:  # Leave 10% free
                self.validation_errors.append("Insufficient disk space")
        except Exception:
            pass  # Skip if we can't check disk space
        
        return len(self.validation_errors) == 0
    
    def create_img_with_validation(self, **params) -> str:
        """Create IMG with full validation"""
        if not self.validate_creation_params(**params):
            raise ValueError("Validation failed:\n" + "\n".join(self.validation_errors))
        
        return self.create_img(**params)


# USAGE EXAMPLE: How to use in your main application
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from App_settings_system import AppSettings, apply_theme_to_app
    
    app = QApplication(sys.argv)
    settings = AppSettings()
    
    # Apply theme
    apply_theme_to_app(app, settings)
    
    # Create enhanced IMG Factory with new IMG functionality
    window = ImgFactoryDemo(settings)
    
    # Show welcome message about new functionality
    window.log_message("IMG Factory Enhanced - New IMG creation functionality added!")
    window.log_message("Use File > New IMG Archive or the toolbar button to create new archives")
    window.log_message("Supports: GTA III, Vice City, San Andreas, Stories, and Bully formats")
    
    window.show()
    sys.exit(app.exec())