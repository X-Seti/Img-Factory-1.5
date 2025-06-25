#!/usr/bin/env python3
"""
IMG Factory Qt6 - Template Management System
Allows users to save, load, and manage custom IMG creation templates
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QTextEdit, QFormLayout, QLineEdit, QComboBox,
    QCheckBox, QSpinBox, QGroupBox, QMessageBox, QInputDialog,
    QSplitter, QFrame, QTabWidget, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont

from new_img_creator import GameType

@dataclass
class IMGTemplate:
    """Template data structure for saving user configurations"""
    name: str
    description: str
    game_type: str  # GameType enum value
    filename_pattern: str
    initial_size_mb: int
    platform: str
    compression_enabled: bool
    encryption_enabled: bool
    create_structure: bool
    created_date: str
    last_used: str
    use_count: int
    tags: List[str]
    custom_settings: Dict[str, Any]

class TemplateCategory(Enum):
    """Template categories for organization"""
    OFFICIAL = "official"
    USER = "user"
    SHARED = "shared"
    RECENT = "recent"

class IMGTemplateManager:
    """Manages IMG creation templates"""
    
    def __init__(self):
        self.templates_dir = self._get_templates_directory()
        self.templates: Dict[str, IMGTemplate] = {}
        self.categories: Dict[TemplateCategory, List[str]] = {
            category: [] for category in TemplateCategory
        }
        
        self._ensure_templates_directory()
        self._load_builtin_templates()
        self._load_user_templates()
    
    def _get_templates_directory(self) -> Path:
        """Get the templates directory path"""
        app_data = Path.home() / ".imgfactory"
        return app_data / "templates"
    
    def _ensure_templates_directory(self):
        """Ensure templates directory exists"""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        for category in TemplateCategory:
            (self.templates_dir / category.value).mkdir(exist_ok=True)
    
    def _load_builtin_templates(self):
        """Load built-in official templates"""
        builtin_templates = [
            IMGTemplate(
                name="GTA SA Vehicle Pack",
                description="Standard template for vehicle modifications in GTA San Andreas",
                game_type=GameType.GTA_SA.value,
                filename_pattern="vehicles_{name}",
                initial_size_mb=150,
                platform="PC",
                compression_enabled=True,
                encryption_enabled=False,
                create_structure=True,
                created_date=datetime.now().isoformat(),
                last_used="",
                use_count=0,
                tags=["vehicles", "gtasa", "standard"],
                custom_settings={
                    "suggested_files": ["*.dff", "*.txd", "*.col"],
                    "max_recommended_size": 500,
                    "target_audience": "modders"
                }
            ),
            IMGTemplate(
                name="GTA III Classic Mod",
                description="Classic template for GTA III modifications",
                game_type=GameType.GTA_III.value,
                filename_pattern="mod_{name}",
                initial_size_mb=50,
                platform="PC",
                compression_enabled=False,
                encryption_enabled=False,
                create_structure=True,
                created_date=datetime.now().isoformat(),
                last_used="",
                use_count=0,
                tags=["gta3", "classic", "basic"],
                custom_settings={
                    "suggested_files": ["*.dff", "*.txd"],
                    "compatibility_notes": "Compatible with original GTA III"
                }
            ),
            IMGTemplate(
                name="GTA IV Advanced",
                description="Advanced template for GTA IV with encryption support",
                game_type=GameType.GTA_IV.value,
                filename_pattern="custom_{name}",
                initial_size_mb=200,
                platform="PC",
                compression_enabled=True,
                encryption_enabled=True,
                create_structure=True,
                created_date=datetime.now().isoformat(),
                last_used="",
                use_count=0,
                tags=["gta4", "advanced", "encrypted"],
                custom_settings={
                    "suggested_files": ["*.wdr", "*.wtd"],
                    "security_level": "high"
                }
            )
        ]
        
        for template in builtin_templates:
            self.templates[template.name] = template
            self.categories[TemplateCategory.OFFICIAL].append(template.name)
    
    def _load_user_templates(self):
        """Load user-created templates"""
        user_dir = self.templates_dir / "user"
        
        for template_file in user_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                template = IMGTemplate(**data)
                self.templates[template.name] = template
                self.categories[TemplateCategory.USER].append(template.name)
                
            except Exception as e:
                print(f"Failed to load template {template_file}: {e}")
    
    def save_template(self, template: IMGTemplate, category: TemplateCategory = TemplateCategory.USER) -> bool:
        """Save a template to disk"""
        try:
            # Update metadata
            template.created_date = datetime.now().isoformat()
            
            # Save to memory
            self.templates[template.name] = template
            
            # Add to category if not already there
            if template.name not in self.categories[category]:
                self.categories[category].append(template.name)
            
            # Save to disk
            if category == TemplateCategory.USER:
                template_file = self.templates_dir / "user" / f"{template.name}.json"
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(template), f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Failed to save template: {e}")
            return False
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a user template"""
        if template_name not in self.templates:
            return False
        
        # Don't allow deletion of official templates
        if template_name in self.categories[TemplateCategory.OFFICIAL]:
            return False
        
        try:
            # Remove from memory
            del self.templates[template_name]
            
            # Remove from categories
            for category_list in self.categories.values():
                if template_name in category_list:
                    category_list.remove(template_name)
            
            # Remove from disk
            template_file = self.templates_dir / "user" / f"{template_name}.json"
            if template_file.exists():
                template_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"Failed to delete template: {e}")
            return False
    
    def get_template(self, template_name: str) -> Optional[IMGTemplate]:
        """Get a template by name"""
        return self.templates.get(template_name)
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[IMGTemplate]:
        """Get all templates in a category"""
        template_names = self.categories.get(category, [])
        return [self.templates[name] for name in template_names if name in self.templates]
    
    def get_templates_by_game(self, game_type: GameType) -> List[IMGTemplate]:
        """Get templates for a specific game"""
        return [
            template for template in self.templates.values()
            if template.game_type == game_type.value
        ]
    
    def search_templates(self, query: str) -> List[IMGTemplate]:
        """Search templates by name, description, or tags"""
        query = query.lower()
        results = []
        
        for template in self.templates.values():
            if (query in template.name.lower() or 
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results
    
    def update_template_usage(self, template_name: str):
        """Update template usage statistics"""
        if template_name in self.templates:
            template = self.templates[template_name]
            template.use_count += 1
            template.last_used = datetime.now().isoformat()
            
            # Save if it's a user template
            if template_name in self.categories[TemplateCategory.USER]:
                self.save_template(template, TemplateCategory.USER)
    
    def get_recent_templates(self, limit: int = 5) -> List[IMGTemplate]:
        """Get recently used templates"""
        templates_with_usage = [
            template for template in self.templates.values()
            if template.last_used
        ]
        
        # Sort by last used date
        templates_with_usage.sort(
            key=lambda t: t.last_used,
            reverse=True
        )
        
        return templates_with_usage[:limit]
    
    def export_template(self, template_name: str, export_path: str) -> bool:
        """Export a template to a file"""
        if template_name not in self.templates:
            return False
        
        try:
            template = self.templates[template_name]
            export_data = {
                "format_version": "1.0",
                "exported_date": datetime.now().isoformat(),
                "template": asdict(template)
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Failed to export template: {e}")
            return False
    
    def import_template(self, import_path: str) -> Optional[str]:
        """Import a template from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "template" not in data:
                return None
            
            template_data = data["template"]
            template = IMGTemplate(**template_data)
            
            # Ensure unique name
            original_name = template.name
            counter = 1
            while template.name in self.templates:
                template.name = f"{original_name} ({counter})"
                counter += 1
            
            # Save as user template
            if self.save_template(template, TemplateCategory.USER):
                return template.name
            
        except Exception as e:
            print(f"Failed to import template: {e}")
        
        return None

class TemplateManagerDialog(QDialog):
    """Dialog for managing IMG templates"""
    
    template_selected = pyqtSignal(object)  # Emits selected template
    
    def __init__(self, template_manager: IMGTemplateManager, parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.current_template = None
        
        self.setWindowTitle("Template Manager - IMG Factory")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        self._create_ui()
        self._connect_signals()
        self._refresh_template_list()
    
    def _create_ui(self):
        """Create the template manager UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("📄 Template Manager")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - template list
        left_panel = self._create_template_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - template details
        right_panel = self._create_template_details_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        # Buttons
        self._create_button_section(layout)
    
    def _create_template_list_panel(self) -> QWidget:
        """Create the template list panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Search and filter
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search templates...")
        self.search_input.textChanged.connect(self._filter_templates)
        search_layout.addWidget(self.search_input)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "All Categories",
            "📋 Official",
            "👤 User Created", 
            "🔄 Recent",
            "🎮 By Game Type"
        ])
        self.category_filter.currentTextChanged.connect(self._filter_templates)
        search_layout.addWidget(self.category_filter)
        
        layout.addLayout(search_layout)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self._on_template_selected)
        layout.addWidget(self.template_list)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        new_btn = QPushButton("➕ New")
        new_btn.clicked.connect(self._new_template)
        actions_layout.addWidget(new_btn)
        
        duplicate_btn = QPushButton("📋 Duplicate")
        duplicate_btn.clicked.connect(self._duplicate_template)
        actions_layout.addWidget(duplicate_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.clicked.connect(self._delete_template)
        actions_layout.addWidget(delete_btn)
        
        layout.addLayout(actions_layout)
        
        return panel
    
    def _create_template_details_panel(self) -> QWidget:
        """Create the template details panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget for different views
        self.details_tabs = QTabWidget()
        
        # Basic info tab
        self.basic_tab = self._create_basic_info_tab()
        self.details_tabs.addTab(self.basic_tab, "📋 Basic Info")
        
        # Settings tab
        self.settings_tab = self._create_settings_tab()
        self.details_tabs.addTab(self.settings_tab, "⚙️ Settings")
        
        # Statistics tab
        self.stats_tab = self._create_statistics_tab()
        self.details_tabs.addTab(self.stats_tab, "📊 Statistics")
        
        layout.addWidget(self.details_tabs)
        
        # Template actions
        actions_group = QGroupBox("Template Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self._export_template)
        actions_layout.addWidget(self.export_btn)
        
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.clicked.connect(self._import_template)
        actions_layout.addWidget(self.import_btn)
        
        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.clicked.connect(self._save_template_changes)
        self.save_btn.setEnabled(False)
        actions_layout.addWidget(self.save_btn)
        
        layout.addWidget(actions_group)
        
        return panel
    
    def _create_basic_info_tab(self) -> QWidget:
        """Create basic info tab"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.name_input = QLineEdit()
        self.name_input.textChanged.connect(self._on_template_modified)
        layout.addRow("Name:", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.textChanged.connect(self._on_template_modified)
        layout.addRow("Description:", self.description_input)
        
        self.game_type_combo = QComboBox()
        for game_type in GameType:
            self.game_type_combo.addItem(f"🎮 {game_type.value.upper()}", game_type.value)
        self.game_type_combo.currentTextChanged.connect(self._on_template_modified)
        layout.addRow("Game Type:", self.game_type_combo)
        
        self.filename_pattern_input = QLineEdit()
        self.filename_pattern_input.setPlaceholderText("e.g., custom_{name}")
        self.filename_pattern_input.textChanged.connect(self._on_template_modified)
        layout.addRow("Filename Pattern:", self.filename_pattern_input)
        
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("vehicles, textures, mod (comma-separated)")
        self.tags_input.textChanged.connect(self._on_template_modified)
        layout.addRow("Tags:", self.tags_input)
        
        return tab
    
    def _create_settings_tab(self) -> QWidget:
        """Create settings tab"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 2000)
        self.size_spin.setSuffix(" MB")
        self.size_spin.valueChanged.connect(self._on_template_modified)
        layout.addRow("Initial Size:", self.size_spin)
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["PC", "PlayStation 2", "Xbox", "Mobile"])
        self.platform_combo.currentTextChanged.connect(self._on_template_modified)
        layout.addRow("Platform:", self.platform_combo)
        
        self.compression_check = QCheckBox("Enable compression")
        self.compression_check.toggled.connect(self._on_template_modified)
        layout.addRow("Compression:", self.compression_check)
        
        self.encryption_check = QCheckBox("Enable encryption")
        self.encryption_check.toggled.connect(self._on_template_modified)
        layout.addRow("Encryption:", self.encryption_check)
        
        self.structure_check = QCheckBox("Create directory structure")
        self.structure_check.toggled.connect(self._on_template_modified)
        layout.addRow("Structure:", self.structure_check)
        
        return tab
    
    def _create_statistics_tab(self) -> QWidget:
        """Create statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        layout.addWidget(self.stats_display)
        
        return tab
    
    def _create_button_section(self, parent_layout):
        """Create dialog buttons"""
        button_layout = QHBoxLayout()
        
        help_btn = QPushButton("❓ Help")
        help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(help_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.use_btn = QPushButton("✅ Use Template")
        self.use_btn.clicked.connect(self._use_template)
        self.use_btn.setEnabled(False)
        button_layout.addWidget(self.use_btn)
        
        parent_layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect all signals"""
        pass
    
    def _refresh_template_list(self):
        """Refresh the template list"""
        self.template_list.clear()
        
        # Add templates by category
        for category in TemplateCategory:
            templates = self.template_manager.get_templates_by_category(category)
            
            if templates:
                # Add category header
                header_item = QListWidgetItem(f"── {category.value.title()} ──")
                header_item.setFlags(Qt.ItemFlag.NoItemFlags)
                header_font = QFont()
                header_font.setBold(True)
                header_item.setFont(header_font)
                self.template_list.addItem(header_item)
                
                # Add templates
                for template in templates:
                    item_text = f"{template.name}"
                    if template.use_count > 0:
                        item_text += f" (used {template.use_count}x)"
                    
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, template.name)
                    self.template_list.addItem(item)
    
    def _filter_templates(self):
        """Filter templates based on search and category"""
        # Implementation for filtering
        pass
    
    def _on_template_selected(self, current_item, previous_item):
        """Handle template selection"""
        if not current_item:
            self.current_template = None
            self.use_btn.setEnabled(False)
            return
        
        template_name = current_item.data(Qt.ItemDataRole.UserRole)
        if not template_name:
            return
        
        self.current_template = self.template_manager.get_template(template_name)
        if self.current_template:
            self._load_template_details(self.current_template)
            self.use_btn.setEnabled(True)
    
    def _load_template_details(self, template: IMGTemplate):
        """Load template details into UI"""
        # Basic info
        self.name_input.setText(template.name)
        self.description_input.setPlainText(template.description)
        
        # Find and set game type
        for i in range(self.game_type_combo.count()):
            if self.game_type_combo.itemData(i) == template.game_type:
                self.game_type_combo.setCurrentIndex(i)
                break
        
        self.filename_pattern_input.setText(template.filename_pattern)
        self.tags_input.setText(", ".join(template.tags))
        
        # Settings
        self.size_spin.setValue(template.initial_size_mb)
        self.platform_combo.setCurrentText(template.platform)
        self.compression_check.setChecked(template.compression_enabled)
        self.encryption_check.setChecked(template.encryption_enabled)
        self.structure_check.setChecked(template.create_structure)
        
        # Statistics
        self._update_statistics_display(template)
        
        self.save_btn.setEnabled(False)
    
    def _update_statistics_display(self, template: IMGTemplate):
        """Update statistics display"""
        stats_text = f"""
Template Statistics:

📅 Created: {template.created_date[:10] if template.created_date else 'Unknown'}
🔄 Last Used: {template.last_used[:10] if template.last_used else 'Never'}
📊 Use Count: {template.use_count}
🏷️ Tags: {', '.join(template.tags)}

Custom Settings:
{json.dumps(template.custom_settings, indent=2) if template.custom_settings else 'None'}
        """
        
        self.stats_display.setPlainText(stats_text.strip())
    
    def _on_template_modified(self):
        """Handle template modification"""
        self.save_btn.setEnabled(True)
    
    def _new_template(self):
        """Create new template"""
        name, ok = QInputDialog.getText(
            self,
            "New Template",
            "Enter template name:"
        )
        
        if ok and name:
            # Create new template with defaults
            new_template = IMGTemplate(
                name=name,
                description="",
                game_type=GameType.GTA_SA.value,
                filename_pattern="custom_{name}",
                initial_size_mb=100,
                platform="PC",
                compression_enabled=True,
                encryption_enabled=False,
                create_structure=True,
                created_date=datetime.now().isoformat(),
                last_used="",
                use_count=0,
                tags=[],
                custom_settings={}
            )
            
            if self.template_manager.save_template(new_template):
                self._refresh_template_list()
        else:
            QMessageBox.critical(self, "Error", "Failed to save template.")
    
    def _use_template(self):
        """Use the selected template"""
        if self.current_template:
            # Update usage statistics
            self.template_manager.update_template_usage(self.current_template.name)
            
            # Emit signal with template data
            self.template_selected.emit(self.current_template)
            self.accept()
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
        📄 Template Manager Help
        
        Templates allow you to save and reuse IMG creation settings.
        
        🔍 Features:
        • Save custom templates with your preferred settings
        • Organize templates by category
        • Search and filter templates
        • Export/import templates to share with others
        • Track usage statistics
        
        📋 Template Types:
        • Official: Built-in templates for common use cases
        • User Created: Your custom templates
        • Recent: Recently used templates
        
        💡 Tips:
        • Use descriptive names and tags for easy searching
        • Create templates for different mod types
        • Export templates to backup your settings
        • Import templates shared by other modders
        
        ⚙️ Custom Settings:
        Templates can store additional custom settings specific to your workflow.
        """
        
        QMessageBox.information(self, "Template Manager Help", help_text)list()
                QMessageBox.information(self, "Success", f"Template '{name}' created successfully!")
    
    def _duplicate_template(self):
        """Duplicate selected template"""
        if not self.current_template:
            QMessageBox.warning(self, "No Selection", "Please select a template to duplicate.")
            return
        
        name, ok = QInputDialog.getText(
            self,
            "Duplicate Template",
            "Enter name for duplicated template:",
            text=f"{self.current_template.name} (Copy)"
        )
        
        if ok and name:
            # Create duplicate
            duplicate = IMGTemplate(
                name=name,
                description=self.current_template.description,
                game_type=self.current_template.game_type,
                filename_pattern=self.current_template.filename_pattern,
                initial_size_mb=self.current_template.initial_size_mb,
                platform=self.current_template.platform,
                compression_enabled=self.current_template.compression_enabled,
                encryption_enabled=self.current_template.encryption_enabled,
                create_structure=self.current_template.create_structure,
                created_date=datetime.now().isoformat(),
                last_used="",
                use_count=0,
                tags=self.current_template.tags.copy(),
                custom_settings=self.current_template.custom_settings.copy()
            )
            
            if self.template_manager.save_template(duplicate):
                self._refresh_template_list()
                QMessageBox.information(self, "Success", f"Template duplicated as '{name}'!")
    
    def _delete_template(self):
        """Delete selected template"""
        if not self.current_template:
            QMessageBox.warning(self, "No Selection", "Please select a template to delete.")
            return
        
        # Check if it's an official template
        if self.current_template.name in self.template_manager.categories[TemplateCategory.OFFICIAL]:
            QMessageBox.warning(self, "Cannot Delete", "Official templates cannot be deleted.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete template '{self.current_template.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.template_manager.delete_template(self.current_template.name):
                self._refresh_template_list()
                QMessageBox.information(self, "Success", "Template deleted successfully!")
    
    def _export_template(self):
        """Export selected template"""
        if not self.current_template:
            QMessageBox.warning(self, "No Selection", "Please select a template to export.")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Template",
            f"{self.current_template.name}.imgtemplate",
            "IMG Templates (*.imgtemplate);;JSON Files (*.json)"
        )
        
        if filename:
            if self.template_manager.export_template(self.current_template.name, filename):
                QMessageBox.information(self, "Success", f"Template exported to:\n{filename}")
            else:
                QMessageBox.critical(self, "Error", "Failed to export template.")
    
    def _import_template(self):
        """Import template from file"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Template",
            "",
            "IMG Templates (*.imgtemplate);;JSON Files (*.json)"
        )
        
        if filename:
            template_name = self.template_manager.import_template(filename)
            if template_name:
                self._refresh_template_list()
                QMessageBox.information(self, "Success", f"Template imported as '{template_name}'!")
            else:
                QMessageBox.critical(self, "Error", "Failed to import template.")
    
    def _save_template_changes(self):
        """Save changes to current template"""
        if not self.current_template:
            return
        
        # Update template with UI values
        self.current_template.name = self.name_input.text()
        self.current_template.description = self.description_input.toPlainText()
        self.current_template.game_type = self.game_type_combo.currentData()
        self.current_template.filename_pattern = self.filename_pattern_input.text()
        self.current_template.tags = [tag.strip() for tag in self.tags_input.text().split(',') if tag.strip()]
        
        self.current_template.initial_size_mb = self.size_spin.value()
        self.current_template.platform = self.platform_combo.currentText()
        self.current_template.compression_enabled = self.compression_check.isChecked()
        self.current_template.encryption_enabled = self.encryption_check.isChecked()
        self.current_template.create_structure = self.structure_check.isChecked()
        
        if self.template_manager.save_template(self.current_template):
            self.save_btn.setEnabled(False)
            QMessageBox.information(self, "Success", "Template saved successfully!")
            self._refresh_template_