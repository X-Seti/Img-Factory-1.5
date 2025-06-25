#!/usr/bin/env python3
"""
IMG Template Manager - System for managing IMG creation templates
Allows users to save, load, and manage reusable IMG creation settings
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QTextEdit, QLabel, QMessageBox, QGroupBox,
    QFormLayout, QComboBox, QCheckBox, QSpinBox, QFileDialog, QInputDialog,
    QSplitter, QWidget, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QIcon


class IMGTemplateManager:
    """Manages user-defined IMG templates and recent settings"""
    
    def __init__(self, settings_path: Optional[str] = None):
        if settings_path is None:
            # Store templates in the app's data directory
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
            "export_presets": [],
            "version": "1.0",
            "last_modified": time.time()
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
    
    def save_template(self, name: str, game_type: str, settings: Dict, description: str = "") -> bool:
        """Save a user-defined template"""
        try:
            template = {
                "name": name,
                "game_type": game_type,
                "settings": settings,
                "description": description,
                "created": time.time(),
                "created_readable": time.strftime('%Y-%m-%d %H:%M:%S'),
                "modified": time.time(),
                "modified_readable": time.strftime('%Y-%m-%d %H:%M:%S'),
                "id": f"template_{int(time.time())}_{hash(name) % 10000}",
                "usage_count": 0,
                "tags": self._extract_tags(game_type, settings)
            }
            
            # Check if template with this name already exists
            existing_templates = self.templates.get("user_templates", [])
            for i, existing in enumerate(existing_templates):
                if existing.get("name") == name:
                    # Update existing template
                    template["created"] = existing.get("created", template["created"])
                    template["created_readable"] = existing.get("created_readable", template["created_readable"])
                    template["usage_count"] = existing.get("usage_count", 0)
                    existing_templates[i] = template
                    break
            else:
                # Add new template
                existing_templates.append(template)
            
            self.templates["user_templates"] = existing_templates
            self.templates["last_modified"] = time.time()
            self._save_templates()
            return True
            
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
    
    def get_user_templates(self) -> List[Dict]:
        """Get list of user-defined templates"""
        return self.templates.get("user_templates", [])
    
    def get_template_by_name(self, name: str) -> Optional[Dict]:
        """Get specific template by name"""
        for template in self.get_user_templates():
            if template.get("name") == name:
                return template
        return None
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a user template"""
        try:
            templates = self.templates.get("user_templates", [])
            self.templates["user_templates"] = [
                t for t in templates if t.get("name") != template_name
            ]
            self.templates["last_modified"] = time.time()
            self._save_templates()
            return True
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False
    
    def update_template_usage(self, template_name: str):
        """Update template usage count"""
        try:
            templates = self.templates.get("user_templates", [])
            for template in templates:
                if template.get("name") == template_name:
                    template["usage_count"] = template.get("usage_count", 0) + 1
                    template["last_used"] = time.time()
                    template["last_used_readable"] = time.strftime('%Y-%m-%d %H:%M:%S')
                    break
            self._save_templates()
        except Exception as e:
            print(f"Error updating template usage: {e}")
    
    def save_recent_settings(self, settings: Dict):
        """Save recent settings for quick access"""
        try:
            recent = self.templates.get("recent_settings", [])
            
            # Add timestamp and metadata
            settings_with_time = {
                **settings,
                "timestamp": time.time(),
                "readable_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                "session_id": f"session_{int(time.time())}",
                "tags": self._extract_tags(settings.get('game_type', ''), settings)
            }
            
            # Remove duplicates by checking similar settings
            recent = [r for r in recent if not self._are_settings_similar(r, settings_with_time)]
            
            # Add to front of list
            recent.insert(0, settings_with_time)
            
            # Keep only last 15 recent settings
            self.templates["recent_settings"] = recent[:15]
            self.templates["last_modified"] = time.time()
            self._save_templates()
            
        except Exception as e:
            print(f"Error saving recent settings: {e}")
    
    def get_recent_settings(self) -> List[Dict]:
        """Get recent settings"""
        return self.templates.get("recent_settings", [])
    
    def get_templates_by_game_type(self, game_type: str) -> List[Dict]:
        """Get templates filtered by game type"""
        templates = self.get_user_templates()
        return [t for t in templates if t.get("game_type") == game_type]
    
    def get_popular_templates(self, limit: int = 5) -> List[Dict]:
        """Get most used templates"""
        templates = self.get_user_templates()
        sorted_templates = sorted(templates, key=lambda t: t.get("usage_count", 0), reverse=True)
        return sorted_templates[:limit]
    
    def export_templates(self, file_path: str, template_names: Optional[List[str]] = None) -> bool:
        """Export templates to file"""
        try:
            if template_names is None:
                # Export all templates
                export_data = {
                    "user_templates": self.get_user_templates(),
                    "exported_on": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "exported_by": "IMG Factory",
                    "version": self.templates.get("version", "1.0")
                }
            else:
                # Export specific templates
                templates_to_export = [
                    t for t in self.get_user_templates() 
                    if t.get("name") in template_names
                ]
                export_data = {
                    "user_templates": templates_to_export,
                    "exported_on": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "exported_by": "IMG Factory",
                    "version": self.templates.get("version", "1.0")
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting templates: {e}")
            return False
    
    def import_templates(self, file_path: str, overwrite_existing: bool = False) -> Dict:
        """Import templates from file"""
        result = {"imported": 0, "skipped": 0, "errors": []}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_templates = import_data.get("user_templates", [])
            existing_names = {t.get("name") for t in self.get_user_templates()}
            
            for template in imported_templates:
                template_name = template.get("name", "")
                
                if not template_name:
                    result["errors"].append("Template missing name")
                    continue
                
                if template_name in existing_names and not overwrite_existing:
                    result["skipped"] += 1
                    continue
                
                # Add import metadata
                template["imported"] = True
                template["import_date"] = time.time()
                template["import_date_readable"] = time.strftime('%Y-%m-%d %H:%M:%S')
                
                if self.save_template(
                    template_name,
                    template.get("game_type", "custom"),
                    template.get("settings", {}),
                    template.get("description", "")
                ):
                    result["imported"] += 1
                else:
                    result["errors"].append(f"Failed to save template: {template_name}")
            
        except Exception as e:
            result["errors"].append(f"Import error: {str(e)}")
        
        return result
    
    def _extract_tags(self, game_type: str, settings: Dict) -> List[str]:
        """Extract relevant tags from settings"""
        tags = []
        
        if game_type:
            tags.append(game_type)
        
        if settings.get("compression_enabled"):
            tags.append("compressed")
        
        if settings.get("encryption_enabled"):
            tags.append("encrypted")
        
        if settings.get("create_structure"):
            tags.append("structured")
        
        platform = settings.get("platform")
        if platform and platform != "PC":
            tags.append(platform.lower())
        
        # Size categories
        size_mb = settings.get("initial_size_mb", 0)
        if size_mb < 50:
            tags.append("small")
        elif size_mb < 200:
            tags.append("medium")
        else:
            tags.append("large")
        
        return tags
    
    def _are_settings_similar(self, settings1: Dict, settings2: Dict) -> bool:
        """Check if two settings are similar enough to be considered duplicates"""
        key_fields = ['game_type', 'initial_size_mb', 'compression_enabled', 'encryption_enabled']
        
        for field in key_fields:
            if settings1.get(field) != settings2.get(field):
                return False
        
        return True
    
    def _save_templates(self):
        """Save templates to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            
            # Create backup of existing file
            if os.path.exists(self.settings_path):
                backup_path = self.settings_path + '.backup'
                try:
                    os.rename(self.settings_path, backup_path)
                except:
                    pass  # Backup failed, continue anyway
            
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving templates: {e}")


class TemplateManagerDialog(QDialog):
    """Dialog for managing IMG creation templates"""
    
    template_selected = pyqtSignal(dict)  # Emits selected template data
    
    def __init__(self, template_manager: IMGTemplateManager, parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.setWindowTitle("IMG Template Manager")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        self._create_ui()
        self._load_templates()
    
    def _create_ui(self):
        """Create the template manager UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📋 IMG Template Manager")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #2E7D32; margin: 10px;")
        layout.addWidget(header)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Template list
        left_panel = self._create_template_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Template details and actions
        right_panel = self._create_details_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        # Bottom buttons
        self._create_bottom_buttons(layout)
    
    def _create_template_list_panel(self) -> QWidget:
        """Create template list panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Search and filter
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search templates...")
        self.search_input.textChanged.connect(self._filter_templates)
        search_layout.addWidget(self.search_input)
        
        self.game_filter = QComboBox()
        self.game_filter.addItems(["All Games", "GTA III", "GTA VC", "GTA SA", "GTA IV", "Bully", "Custom"])
        self.game_filter.currentTextChanged.connect(self._filter_templates)
        search_layout.addWidget(self.game_filter)
        
        layout.addLayout(search_layout)
        
        # Template list
        list_group = QGroupBox("User Templates")
        list_layout = QVBoxLayout(list_group)
        
        self.template_list = QListWidget()
        self.template_list.itemSelectionChanged.connect(self._on_template_selected)
        self.template_list.itemDoubleClicked.connect(self._use_template)
        list_layout.addWidget(self.template_list)
        
        # List buttons
        list_btn_layout = QHBoxLayout()
        
        self.use_btn = QPushButton("✅ Use Template")
        self.use_btn.clicked.connect(self._use_template)
        self.use_btn.setEnabled(False)
        list_btn_layout.addWidget(self.use_btn)
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self._edit_template)
        self.edit_btn.setEnabled(False)
        list_btn_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self._delete_template)
        self.delete_btn.setEnabled(False)
        list_btn_layout.addWidget(self.delete_btn)
        
        list_layout.addLayout(list_btn_layout)
        layout.addWidget(list_group)
        
        # Recent settings
        recent_group = QGroupBox("🕒 Recent Settings")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(120)
        self.recent_list.itemDoubleClicked.connect(self._use_recent)
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_group)
        
        return panel
    
    def _create_details_panel(self) -> QWidget:
        """Create template details panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Template details
        details_group = QGroupBox("📄 Template Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Select a template to see details...")
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        # Statistics
        stats_group = QGroupBox("📊 Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(100)
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        # Actions
        actions_group = QGroupBox("⚙️ Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Create new template
        new_template_btn = QPushButton("➕ Create New Template")
        new_template_btn.clicked.connect(self._create_new_template)
        actions_layout.addWidget(new_template_btn)
        
        # Import/Export
        io_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 Import Templates")
        import_btn.clicked.connect(self._import_templates)
        io_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 Export Templates")
        export_btn.clicked.connect(self._export_templates)
        io_layout.addWidget(export_btn)
        
        actions_layout.addLayout(io_layout)
        
        # Backup/Restore
        backup_layout = QHBoxLayout()
        
        backup_btn = QPushButton("💾 Create Backup")
        backup_btn.clicked.connect(self._create_backup)
        backup_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("🔄 Restore Backup")
        restore_btn.clicked.connect(self._restore_backup)
        backup_layout.addWidget(restore_btn)
        
        actions_layout.addLayout(backup_layout)
        
        layout.addWidget(actions_group)
        
        return panel
    
    def _create_bottom_buttons(self, parent_layout):
        """Create bottom dialog buttons"""
        button_layout = QHBoxLayout()
        
        # Statistics summary
        self.summary_label = QLabel("")
        button_layout.addWidget(self.summary_label)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        parent_layout.addLayout(button_layout)
    
    def _load_templates(self):
        """Load templates into the lists"""
        self.template_list.clear()
        self.recent_list.clear()
        
        # Load user templates
        templates = self.template_manager.get_user_templates()
        for template in templates:
            item_text = f"{template['name']} ({template.get('game_type', 'Unknown').upper()})"
            if template.get('usage_count', 0) > 0:
                item_text += f" [{template['usage_count']} uses]"
            
            item = QListWidgetItem(item_text)
            item.template_data = template
            self.template_list.addItem(item)
        
        # Load recent settings
        recent = self.template_manager.get_recent_settings()
        for settings in recent[:8]:  # Show only last 8
            time_str = settings.get('readable_time', 'Unknown time')
            game_type = settings.get('game_type', 'Unknown').upper()
            item_text = f"{game_type} - {time_str}"
            item = QListWidgetItem(item_text)
            item.settings_data = settings
            self.recent_list.addItem(item)
        
        # Update statistics
        self._update_statistics()
        self._filter_templates()  # Apply any existing filters
    
    def _update_statistics(self):
        """Update template statistics display"""
        templates = self.template_manager.get_user_templates()
        recent = self.template_manager.get_recent_settings()
        
        total_templates = len(templates)
        total_usage = sum(t.get('usage_count', 0) for t in templates)
        
        summary = f"Templates: {total_templates} | Recent: {len(recent)} | Total Usage: {total_usage}"
        self.summary_label.setText(summary)
        
        # Popular templates
        popular = self.template_manager.get_popular_templates(3)
        stats_text = "📈 Most Used Templates:\n"
        for i, template in enumerate(popular, 1):
            usage = template.get('usage_count', 0)
            stats_text += f"{i}. {template['name']} ({usage} uses)\n"
        
        if not popular:
            stats_text += "No usage statistics available yet."
        
        self.stats_text.setPlainText(stats_text)
    
    def _filter_templates(self):
        """Filter templates based on search and game type"""
        search_text = self.search_input.text().lower()
        game_filter = self.game_filter.currentText()
        
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            template = item.template_data
            
            # Apply text search
            visible = True
            if search_text:
                searchable_text = f"{template['name']} {template.get('description', '')} {template.get('game_type', '')}".lower()
                visible = search_text in searchable_text
            
            # Apply game type filter
            if visible and game_filter != "All Games":
                game_type_map = {
                    "GTA III": "gta3",
                    "GTA VC": "gtavc", 
                    "GTA SA": "gtasa",
                    "GTA IV": "gtaiv",
                    "Bully": "bully",
                    "Custom": "custom"
                }
                expected_type = game_type_map.get(game_filter, "")
                visible = template.get('game_type', '') == expected_type
            
            item.setHidden(not visible)
    
    def _on_template_selected(self):
        """Handle template selection"""
        current = self.template_list.currentItem()
        has_selection = current is not None and not current.isHidden()
        
        self.use_btn.setEnabled(has_selection)
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        
        if has_selection and hasattr(current, 'template_data'):
            template = current.template_data
            self._display_template_details(template)
        else:
            self.details_text.clear()
    
    def _display_template_details(self, template: Dict):
        """Display detailed template information"""
        settings = template.get('settings', {})
        
        details = f"""
<h3>{template['name']}</h3>
<p><strong>Game Type:</strong> {template.get('game_type', 'Unknown').upper()}</p>
<p><strong>Description:</strong> {template.get('description', 'No description provided')}</p>

<h4>Settings:</h4>
<ul>
<li><strong>Initial Size:</strong> {settings.get('initial_size_mb', 100)} MB</li>
<li><strong>Platform:</strong> {settings.get('platform', 'PC')}</li>
<li><strong>Create Structure:</strong> {'Yes' if settings.get('create_structure', False) else 'No'}</li>
<li><strong>Compression:</strong> {'Enabled' if settings.get('compression_enabled', False) else 'Disabled'}</li>
<li><strong>Encryption:</strong> {'Enabled' if settings.get('encryption_enabled', False) else 'Disabled'}</li>
</ul>

<h4>Metadata:</h4>
<ul>
<li><strong>Created:</strong> {template.get('created_readable', 'Unknown')}</li>
<li><strong>Last Modified:</strong> {template.get('modified_readable', template.get('created_readable', 'Unknown'))}</li>
<li><strong>Usage Count:</strong> {template.get('usage_count', 0)}</li>
<li><strong>Last Used:</strong> {template.get('last_used_readable', 'Never')}</li>
</ul>

<h4>Tags:</h4>
<p>{', '.join(template.get('tags', []))}</p>
        """.strip()
        
        self.details_text.setHtml(details)
    
    def _use_template(self):
        """Use the selected template"""
        current = self.template_list.currentItem()
        if current and hasattr(current, 'template_data'):
            template_data = current.template_data
            self.template_manager.update_template_usage(template_data['name'])
            self.template_selected.emit(template_data)
            self.accept()
    
    def _use_recent(self, item):
        """Use recent settings"""
        if hasattr(item, 'settings_data'):
            # Convert recent settings to template format
            template_data = {
                'name': 'Recent Settings',
                'game_type': item.settings_data.get('game_type', 'Unknown'),
                'settings': item.settings_data,
                'description': f"Recent settings from {item.settings_data.get('readable_time', 'unknown time')}"
            }
            self.template_selected.emit(template_data)
            self.accept()
    
    def _edit_template(self):
        """Edit the selected template"""
        current = self.template_list.currentItem()
        if current and hasattr(current, 'template_data'):
            template = current.template_data
            dialog = TemplateEditDialog(template, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_template = dialog.get_template_data()
                if self.template_manager.save_template(
                    updated_template['name'],
                    updated_template['game_type'],
                    updated_template['settings'],
                    updated_template['description']
                ):
                    self._load_templates()
                    QMessageBox.information(self, "Success", "Template updated successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update template.")
    
    def _delete_template(self):
        """Delete the selected template"""
        current = self.template_list.currentItem()
        if current and hasattr(current, 'template_data'):
            template_name = current.template_data['name']
            
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Delete template '{template_name}'?\n\nThis action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.template_manager.delete_template(template_name):
                    self._load_templates()
                    QMessageBox.information(self, "Success", "Template deleted successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete template.")
    
    def _create_new_template(self):
        """Create a new template"""
        dialog = TemplateEditDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template_data = dialog.get_template_data()
            if self.template_manager.save_template(
                template_data['name'],
                template_data['game_type'],
                template_data['settings'],
                template_data['description']
            ):
                self._load_templates()
                QMessageBox.information(self, "Success", "Template created successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to create template.")
    
    def _import_templates(self):
        """Import templates from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Templates", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            # Ask about overwrite policy
            reply = QMessageBox.question(
                self, "Import Policy",
                "Overwrite existing templates with same names?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            overwrite = reply == QMessageBox.StandardButton.Yes
            result = self.template_manager.import_templates(file_path, overwrite)
            
            message = f"Import completed!\n\nImported: {result['imported']}\nSkipped: {result['skipped']}"
            if result['errors']:
                message += f"\nErrors: {len(result['errors'])}"
                for error in result['errors'][:3]:  # Show first 3 errors
                    message += f"\n- {error}"
            
            self._load_templates()
            QMessageBox.information(self, "Import Complete", message)
    
    def _export_templates(self):
        """Export templates to file"""
        if not self.template_manager.get_user_templates():
            QMessageBox.information(self, "Export", "No templates to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Templates", "img_templates_export.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            if self.template_manager.export_templates(file_path):
                QMessageBox.information(
                    self, "Export Complete",
                    f"Templates exported successfully to:\n{file_path}"
                )
            else:
                QMessageBox.critical(self, "Export Error", "Failed to export templates.")
    
    def _create_backup(self):
        """Create backup of templates"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        backup_name = f"img_templates_backup_{timestamp}.json"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Create Backup", backup_name,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            if self.template_manager.export_templates(file_path):
                QMessageBox.information(
                    self, "Backup Created",
                    f"Backup created successfully:\n{file_path}"
                )
            else:
                QMessageBox.critical(self, "Backup Error", "Failed to create backup.")
    
    def _restore_backup(self):
        """Restore templates from backup"""
        reply = QMessageBox.warning(
            self, "Restore Backup",
            "This will replace all current templates with the backup.\n\nAre you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Backup File", "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Clear existing templates
                self.template_manager.templates["user_templates"] = []
                
                # Import from backup
                result = self.template_manager.import_templates(file_path, True)
                
                message = f"Restore completed!\n\nRestored: {result['imported']} templates"
                if result['errors']:
                    message += f"\nErrors: {len(result['errors'])}"
                
                self._load_templates()
                QMessageBox.information(self, "Restore Complete", message)


class TemplateEditDialog(QDialog):
    """Dialog for editing template details"""
    
    def __init__(self, template_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.template_data = template_data or {}
        self.is_editing = template_data is not None
        
        title = "Edit Template" if self.is_editing else "Create New Template"
        self.setWindowTitle(title)
        self.setMinimumSize(500, 600)
        self.setModal(True)
        
        self._create_ui()
        self._load_template_data()
    
    def _create_ui(self):
        """Create the edit dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_text = "✏️ Edit Template" if self.is_editing else "➕ Create New Template"
        header = QLabel(header_text)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Basic info
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter template name...")
        basic_layout.addRow("Template Name:", self.name_input)
        
        self.game_type_combo = QComboBox()
        self.game_type_combo.addItems(["gta3", "gtavc", "gtasa", "gtaiv", "bully", "custom"])
        basic_layout.addRow("Game Type:", self.game_type_combo)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Optional description...")
        basic_layout.addRow("Description:", self.description_input)
        
        layout.addWidget(basic_group)
        
        # Settings
        settings_group = QGroupBox("Template Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 2048)
        self.size_spin.setValue(100)
        self.size_spin.setSuffix(" MB")
        settings_layout.addRow("Initial Size:", self.size_spin)
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["PC", "XBOX", "PS2", "PSP", "Mobile"])
        settings_layout.addRow("Platform:", self.platform_combo)
        
        self.structure_check = QCheckBox("Create basic folder structure")
        settings_layout.addRow("Options:", self.structure_check)
        
        self.compression_check = QCheckBox("Enable compression")
        settings_layout.addRow("", self.compression_check)
        
        self.encryption_check = QCheckBox("Enable encryption")
        settings_layout.addRow("", self.encryption_check)
        
        layout.addWidget(settings_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        save_text = "💾 Update Template" if self.is_editing else "✨ Create Template"
        save_btn = QPushButton(save_text)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_template)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _load_template_data(self):
        """Load existing template data into form"""
        if not self.is_editing:
            return
        
        self.name_input.setText(self.template_data.get('name', ''))
        self.game_type_combo.setCurrentText(self.template_data.get('game_type', 'custom'))
        self.description_input.setPlainText(self.template_data.get('description', ''))
        
        settings = self.template_data.get('settings', {})
        self.size_spin.setValue(settings.get('initial_size_mb', 100))
        self.platform_combo.setCurrentText(settings.get('platform', 'PC'))
        self.structure_check.setChecked(settings.get('create_structure', False))
        self.compression_check.setChecked(settings.get('compression_enabled', False))
        self.encryption_check.setChecked(settings.get('encryption_enabled', False))
    
    def _save_template(self):
        """Save template data"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Template name is required.")
            return
        
        self.accept()
    
    def get_template_data(self) -> Dict:
        """Get template data from form"""
        return {
            'name': self.name_input.text().strip(),
            'game_type': self.game_type_combo.currentText(),
            'description': self.description_input.toPlainText().strip(),
            'settings': {
                'initial_size_mb': self.size_spin.value(),
                'platform': self.platform_combo.currentText(),
                'create_structure': self.structure_check.isChecked(),
                'compression_enabled': self.compression_check.isChecked(),
                'encryption_enabled': self.encryption_check.isChecked()
            }
        }


class QuickTemplateSelector(QDialog):
    """Quick template selection dialog for common workflows"""
    
    template_selected = pyqtSignal(dict)
    
    def __init__(self, template_manager: IMGTemplateManager, game_type: str = "", parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.game_type = game_type
        
        self.setWindowTitle("Quick Template Selection")
        self.setMinimumSize(400, 300)
        self.setModal(True)
        
        self._create_ui()
        self._load_quick_templates()
    
    def _create_ui(self):
        """Create quick selector UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("⚡ Quick Template Selection")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        if self.game_type:
            game_label = QLabel(f"Game Type: {self.game_type.upper()}")
            game_label.setStyleSheet("color: #666; font-style: italic;")
            game_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(game_label)
        
        # Quick templates list
        self.quick_list = QListWidget()
        self.quick_list.itemDoubleClicked.connect(self._select_template)
        layout.addWidget(self.quick_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        manage_btn = QPushButton("⚙️ Manage All Templates")
        manage_btn.clicked.connect(self._open_manager)
        button_layout.addWidget(manage_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        select_btn = QPushButton("✅ Use Selected")
        select_btn.clicked.connect(self._select_template)
        select_btn.setDefault(True)
        button_layout.addWidget(select_btn)
        
        layout.addLayout(button_layout)
    
    def _load_quick_templates(self):
        """Load quick access templates"""
        self.quick_list.clear()
        
        # Get templates for specific game type
        if self.game_type:
            templates = self.template_manager.get_templates_by_game_type(self.game_type)
        else:
            templates = self.template_manager.get_popular_templates(10)
        
        if not templates:
            # Show recent settings instead
            recent = self.template_manager.get_recent_settings()[:5]
            for settings in recent:
                item_text = f"Recent: {settings.get('game_type', 'Unknown').upper()} ({settings.get('readable_time', '')})"
                item = QListWidgetItem(item_text)
                item.template_data = {
                    'name': 'Recent Settings',
                    'game_type': settings.get('game_type', 'custom'),
                    'settings': settings,
                    'description': 'Recent settings'
                }
                self.quick_list.addItem(item)
        else:
            for template in templates:
                usage_info = f" [{template.get('usage_count', 0)} uses]" if template.get('usage_count', 0) > 0 else ""
                item_text = f"{template['name']}{usage_info}"
                item = QListWidgetItem(item_text)
                item.template_data = template
                self.quick_list.addItem(item)
        
        # Add "No Template" option
        item = QListWidgetItem("🆕 Create without template")
        item.template_data = None
        self.quick_list.addItem(item)
    
    def _select_template(self):
        """Select and use template"""
        current = self.quick_list.currentItem()
        if current:
            if current.template_data is None:
                # No template selected
                self.reject()
            else:
                self.template_selected.emit(current.template_data)
                self.accept()
    
    def _open_manager(self):
        """Open full template manager"""
        dialog = TemplateManagerDialog(self.template_manager, self)
        dialog.template_selected.connect(self.template_selected)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.accept()


# Utility functions for integration
def show_template_manager(template_manager: IMGTemplateManager, parent=None):
    """Show template manager dialog"""
    dialog = TemplateManagerDialog(template_manager, parent)
    return dialog.exec()


def show_quick_template_selector(template_manager: IMGTemplateManager, game_type: str = "", parent=None):
    """Show quick template selector"""
    dialog = QuickTemplateSelector(template_manager, game_type, parent)
    return dialog.exec()


# Example usage and testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test template manager
    manager = IMGTemplateManager()
    
    # Add some test templates
    test_settings = {
        'initial_size_mb': 150,
        'platform': 'PC',
        'compression_enabled': False,
        'encryption_enabled': False,
        'create_structure': True
    }
    
    manager.save_template("GTA SA Standard", "gtasa", test_settings, "Standard GTA SA IMG template")
    
    # Show template manager
    dialog = TemplateManagerDialog(manager)
    dialog.show()
    
    sys.exit(app.exec())