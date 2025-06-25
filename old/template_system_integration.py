#!/usr/bin/env python3
"""
Template System Integration - Complete Implementation
Shows exactly where to add the template system in your existing code
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QTextEdit, QLabel, QMessageBox, QGroupBox,
    QFormLayout, QComboBox, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# 1. FIRST: Add this class to a new file called `img_template_system.py`
class IMGTemplateManager:
    """Manages user-defined IMG templates and recent settings"""
    
    def __init__(self, settings_path=None):
        if settings_path is None:
            # Store templates in the same directory as your app
            app_dir = os.path.dirname(os.path.abspath(__file__))
            self.settings_path = os.path.join(app_dir, "img_templates.json")
        else:
            self.settings_path = settings_path
            
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load templates from file"""
        default_structure = {
            "user_templates": [],
            "recent_settings": [],
            "favorites": [],
            "version": "1.0"
        }
        
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure all required keys exist
                    for key in default_structure:
                        if key not in data:
                            data[key] = default_structure[key]
                    return data
        except Exception as e:
            print(f"Error loading templates: {e}")
        
        return default_structure
    
    def save_template(self, name: str, game_type: str, settings: Dict) -> bool:
        """Save a user-defined template"""
        try:
            template = {
                "name": name,
                "game_type": game_type,
                "settings": settings,
                "created": time.time(),
                "created_readable": time.strftime('%Y-%m-%d %H:%M:%S'),
                "id": f"template_{int(time.time())}"
            }
            
            # Check if template with this name already exists
            existing_templates = self.templates.get("user_templates", [])
            for i, existing in enumerate(existing_templates):
                if existing.get("name") == name:
                    # Update existing template
                    existing_templates[i] = template
                    break
            else:
                # Add new template
                existing_templates.append(template)
            
            self.templates["user_templates"] = existing_templates
            self._save_templates()
            return True
            
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
    
    def get_user_templates(self) -> List[Dict]:
        """Get list of user-defined templates"""
        return self.templates.get("user_templates", [])
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a user template"""
        try:
            templates = self.templates.get("user_templates", [])
            self.templates["user_templates"] = [
                t for t in templates if t.get("name") != template_name
            ]
            self._save_templates()
            return True
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False
    
    def save_recent_settings(self, settings: Dict):
        """Save recent settings for quick access"""
        try:
            recent = self.templates.get("recent_settings", [])
            
            # Add timestamp
            settings_with_time = {
                **settings,
                "timestamp": time.time(),
                "readable_time": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Add to front of list
            recent.insert(0, settings_with_time)
            
            # Keep only last 10 recent settings
            self.templates["recent_settings"] = recent[:10]
            self._save_templates()
            
        except Exception as e:
            print(f"Error saving recent settings: {e}")
    
    def get_recent_settings(self) -> List[Dict]:
        """Get recent settings"""
        return self.templates.get("recent_settings", [])
    
    def _save_templates(self):
        """Save templates to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving templates: {e}")


# 2. SECOND: Add this dialog class to your `new_img_creator.py` file
class TemplateManagerDialog(QDialog):
    """Dialog for managing IMG creation templates"""
    
    template_selected = pyqtSignal(dict)  # Emits selected template data
    
    def __init__(self, template_manager: IMGTemplateManager, parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.setWindowTitle("Manage IMG Templates")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        self._create_ui()
        self._load_templates()
    
    def _create_ui(self):
        """Create the template manager UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("IMG Creation Templates")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Template list
        list_group = QGroupBox("📋 Saved Templates")
        list_layout = QVBoxLayout(list_group)
        
        self.template_list = QListWidget()
        self.template_list.itemSelectionChanged.connect(self._on_template_selected)
        list_layout.addWidget(self.template_list)
        
        # Template list buttons
        list_btn_layout = QHBoxLayout()
        
        self.use_btn = QPushButton("✅ Use Template")
        self.use_btn.clicked.connect(self._use_template)
        self.use_btn.setEnabled(False)
        list_btn_layout.addWidget(self.use_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self._delete_template)
        self.delete_btn.setEnabled(False)
        list_btn_layout.addWidget(self.delete_btn)
        
        list_btn_layout.addStretch()
        list_layout.addLayout(list_btn_layout)
        
        layout.addWidget(list_group)
        
        # Template details
        details_group = QGroupBox("📄 Template Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(120)
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Select a template to see details...")
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        # Recent settings
        recent_group = QGroupBox("🕒 Recent Settings")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(100)
        self.recent_list.itemDoubleClicked.connect(self._use_recent)
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_group)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 Import Templates")
        import_btn.clicked.connect(self._import_templates)
        button_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 Export Templates")
        export_btn.clicked.connect(self._export_templates)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _load_templates(self):
        """Load templates into the list"""
        self.template_list.clear()
        self.recent_list.clear()
        
        # Load user templates
        templates = self.template_manager.get_user_templates()
        for template in templates:
            item_text = f"🎮 {template['name']} ({template.get('game_type', 'Unknown')})"
            item = QListWidgetItem(item_text)
            item.template_data = template
            self.template_list.addItem(item)
        
        # Load recent settings
        recent = self.template_manager.get_recent_settings()
        for i, settings in enumerate(recent[:5]):  # Show only last 5
            time_str = settings.get('readable_time', 'Unknown time')
            game_type = settings.get('game_type', 'Unknown')
            item_text = f"🕒 {game_type} - {time_str}"
            item = QListWidgetItem(item_text)
            item.settings_data = settings
            self.recent_list.addItem(item)
    
    def _on_template_selected(self):
        """Handle template selection"""
        current = self.template_list.currentItem()
        has_selection = current is not None
        
        self.use_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        
        if has_selection and hasattr(current, 'template_data'):
            template = current.template_data
            details = f"""
Name: {template['name']}
Game Type: {template.get('game_type', 'Unknown')}
Created: {template.get('created_readable', 'Unknown')}

Settings:
• Initial Size: {template['settings'].get('initial_size_mb', 10)} MB
• Create Structure: {template['settings'].get('create_structure', False)}
• Platform: {template['settings'].get('platform', 'PC')}
• Compression: {template['settings'].get('compression_enabled', False)}
            """.strip()
            self.details_text.setPlainText(details)
        else:
            self.details_text.clear()
    
    def _use_template(self):
        """Use the selected template"""
        current = self.template_list.currentItem()
        if current and hasattr(current, 'template_data'):
            self.template_selected.emit(current.template_data)
            self.accept()
    
    def _use_recent(self, item):
        """Use recent settings"""
        if hasattr(item, 'settings_data'):
            # Convert recent settings to template format
            template_data = {
                'name': 'Recent Settings',
                'game_type': item.settings_data.get('game_type', 'Unknown'),
                'settings': item.settings_data
            }
            self.template_selected.emit(template_data)
            self.accept()
    
    def _delete_template(self):
        """Delete the selected template"""
        current = self.template_list.currentItem()
        if current and hasattr(current, 'template_data'):
            template_name = current.template_data['name']
            
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Delete template '{template_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.template_manager.delete_template(template_name):
                    self._load_templates()
                    QMessageBox.information(self, "Success", "Template deleted successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete template.")
    
    def _import_templates(self):
        """Import templates from file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Templates", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                imported_count = 0
                if 'user_templates' in data:
                    for template in data['user_templates']:
                        if self.template_manager.save_template(
                            template['name'], 
                            template['game_type'], 
                            template['settings']
                        ):
                            imported_count += 1
                
                self._load_templates()
                QMessageBox.information(
                    self, "Import Complete", 
                    f"Successfully imported {imported_count} templates!"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import templates:\n{str(e)}")
    
    def _export_templates(self):
        """Export templates to file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Templates", "img_templates_export.json", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.template_manager.templates, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(
                    self, "Export Complete", 
                    f"Templates exported successfully to:\n{file_path}"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export templates:\n{str(e)}")


# 3. THIRD: Add this to your ImgFactoryDemo class in imgfactory_demo.py
class ImgFactoryDemo(QMainWindow):
    def __init__(self, app_settings):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5 [Enhanced with Templates]")
        self.setGeometry(100, 100, 1100, 700)
        self.app_settings = app_settings
        
        # Current IMG file
        self.current_img: IMGFile = None
        self.load_thread: IMGLoadThread = None
        
        # ADD THIS: Initialize template manager
        self.template_manager = IMGTemplateManager()
        
        self._create_menu()
        self._create_status_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self._create_main_ui_with_splitters(main_layout)
        
        # ADD THIS: Add new IMG functionality with templates
        self._add_new_img_support()
    
    def _add_new_img_support(self):
        """Add new IMG creation support with templates"""
        # This method was already added in your __init__
        pass
    
    # ADD THESE METHODS to your ImgFactoryDemo class:
    
    def create_new_img(self):
        """Show new IMG creation dialog"""
        from new_img_creator import GameSpecificIMGDialog
        
        dialog = GameSpecificIMGDialog(self)
        dialog.template_manager = self.template_manager  # Pass template manager
        dialog.img_created.connect(self.load_img_file)
        dialog.img_created.connect(lambda path: self.log_message(f"Created: {os.path.basename(path)}"))
        dialog.exec()
    
    def manage_templates(self):
        """Show template manager dialog"""
        dialog = TemplateManagerDialog(self.template_manager, self)
        dialog.template_selected.connect(self._apply_template)
        dialog.exec()
    
    def _apply_template(self, template_data):
        """Apply a template to create new IMG"""
        from new_img_creator import GameSpecificIMGDialog, GameType
        
        dialog = GameSpecificIMGDialog(self)
        dialog.template_manager = self.template_manager
        
        # Apply template settings
        game_type_str = template_data.get('game_type', 'gtasa')
        settings = template_data.get('settings', {})
        
        # Set game type
        try:
            game_type = GameType(game_type_str)
            for button in dialog.game_button_group.buttons():
                if hasattr(button, 'game_type') and button.game_type == game_type:
                    button.setChecked(True)
                    dialog._on_game_type_changed(button)
                    break
        except ValueError:
            pass  # Invalid game type, use default
        
        # Apply settings
        if 'initial_size_mb' in settings:
            dialog.initial_size_spin.setValue(settings['initial_size_mb'])
        
        if 'create_structure' in settings:
            dialog.auto_structure_check.setChecked(settings['create_structure'])
        
        if 'platform' in settings:
            dialog.platform_combo.setCurrentText(settings['platform'])
        
        if 'compression_enabled' in settings:
            dialog.compression_check.setChecked(settings['compression_enabled'])
        
        # Pre-fill filename if available
        if 'filename' in settings:
            dialog.filename_input.setText(settings['filename'])
        
        dialog.img_created.connect(self.load_img_file)
        dialog.exec()


# 4. FOURTH: Update your NewIMGDialog class in new_img_creator.py
# Add this to the NewIMGDialog class:

def _create_button_section(self, parent_layout):
    """Create dialog buttons with template support"""
    button_layout = QHBoxLayout()
    
    # Template buttons
    load_template_btn = QPushButton("📁 Load Template")
    load_template_btn.setToolTip("Load a saved template")
    load_template_btn.clicked.connect(self._load_template)
    button_layout.addWidget(load_template_btn)
    
    save_template_btn = QPushButton("💾 Save as Template")
    save_template_btn.setToolTip("Save current settings as a reusable template")
    save_template_btn.clicked.connect(self._save_template)
    button_layout.addWidget(save_template_btn)
    
    button_layout.addStretch()
    
    # Standard buttons
    cancel_btn = QPushButton("❌ Cancel")
    cancel_btn.clicked.connect(self.reject)
    button_layout.addWidget(cancel_btn)
    
    self.create_btn = QPushButton("✨ Create IMG Archive")
    self.create_btn.setDefault(True)
    self.create_btn.clicked.connect(self._create_img_file)
    button_layout.addWidget(self.create_btn)
    
    parent_layout.addLayout(button_layout)

def _load_template(self):
    """Load template from template manager"""
    if hasattr(self, 'template_manager'):
        dialog = TemplateManagerDialog(self.template_manager, self)
        dialog.template_selected.connect(self._apply_template_to_dialog)
        dialog.exec()

def _apply_template_to_dialog(self, template_data):
    """Apply template data to current dialog"""
    settings = template_data.get('settings', {})
    
    # Apply all settings to the dialog
    if 'filename' in settings:
        self.filename_input.setText(settings['filename'])
    
    if 'initial_size_mb' in settings:
        self.initial_size_spin.setValue(settings['initial_size_mb'])
    
    if 'platform' in settings:
        self.platform_combo.setCurrentText(settings['platform'])
    
    if 'compression_enabled' in settings:
        self.compression_check.setChecked(settings['compression_enabled'])
    
    if 'create_structure' in settings:
        self.auto_structure_check.setChecked(settings['create_structure'])
    
    # Set game type
    game_type_str = template_data.get('game_type', '')
    try:
        game_type = GameType(game_type_str)
        for button in self.game_button_group.buttons():
            if hasattr(button, 'game_type') and button.game_type == game_type:
                button.setChecked(True)
                self._on_game_type_changed(button)
                break
    except ValueError:
        pass

def _save_template(self):
    """Save current settings as template"""
    if not hasattr(self, 'template_manager'):
        QMessageBox.warning(self, "Template Error", "Template manager not available")
        return
    
    # Get template name from user
    from PyQt6.QtWidgets import QInputDialog
    
    name, ok = QInputDialog.getText(
        self, "Save Template", 
        "Enter template name:",
        text=f"{self.selected_game_type.value.replace('_', ' ').title()} Template"
    )
    
    if ok and name:
        # Collect current settings
        settings = {
            'filename': self.filename_input.text(),
            'initial_size_mb': self.initial_size_spin.value(),
            'platform': self.platform_combo.currentText(),
            'compression_enabled': self.compression_check.isChecked(),
            'encryption_enabled': self.encryption_check.isChecked(),
            'create_structure': self.auto_structure_check.isChecked()
        }
        
        # Save template
        if self.template_manager.save_template(name, self.selected_game_type.value, settings):
            QMessageBox.information(self, "Success", f"Template '{name}' saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to save template")

def _create_img_file(self):
    """Enhanced IMG creation with template history"""
    # ... existing creation code ...
    
    # After successful creation, save to recent settings
    if hasattr(self, 'template_manager'):
        recent_settings = {
            'game_type': self.selected_game_type.value,
            'filename': self.filename_input.text(),
            'initial_size_mb': self.initial_size_spin.value(),
            'platform': self.platform_combo.currentText(),
            'compression_enabled': self.compression_check.isChecked(),
            'create_structure': self.auto_structure_check.isChecked()
        }
        self.template_manager.save_recent_settings(recent_settings)


# 5. FIFTH: Add menu item for template management
# Add this to your _create_menu method in ImgFactoryDemo:

def _create_menu(self):
    """Enhanced menu with template support"""
    # ... existing menu code ...
    
    # Add to Settings menu
    settings_menu = None
    for action in self.menuBar().actions():
        if action.text() == "Settings":
            settings_menu = action.menu()
            break
    
    if settings_menu:
        settings_menu.addSeparator()
        template_action = settings_menu.addAction("📋 Manage Templates")
        template_action.triggered.connect(self.manage_templates)


# 6. SIXTH: File structure should look like this:
"""
your_project/
├── imgfactory_demo.py              (your main file - add template integration here)
├── img_core_classes.py             (existing)
├── new_img_creator.py              (add template dialog methods here)
├── enhanced_img_formats.py         (existing)
├── img_template_system.py          (NEW - create this file with IMGTemplateManager)
├── App_settings_system.py          (existing)
└── img_templates.json              (AUTO-CREATED - stores user templates)
"""

# 7. SEVENTH: Quick test to verify template system works
def test_template_system():
    """Test the template system"""
    manager = IMGTemplateManager()
    
    # Save a test template
    test_settings = {
        'initial_size_mb': 100,
        'platform': 'PC',
        'compression_enabled': True,
        'create_structure': True
    }
    
    success = manager.save_template("Test GTA SA", "gtasa", test_settings)
    print(f"Template saved: {success}")
    
    # Load templates
    templates = manager.get_user_templates()
    print(f"Found {len(templates)} templates")
    
    return manager

if __name__ == "__main__":
    # Test the template system
    test_template_system()
