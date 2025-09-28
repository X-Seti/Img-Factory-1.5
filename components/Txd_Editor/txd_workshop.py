#this belongs in components/Txd_Editor/ txd_workshop.py - Version: 3
# X-Seti - September26 2025 - Img Factory 1.5 - TXD Workshop

"""
TXD Workshop - Main texture editing window for IMG Factory
Displays TXD files from IMG archives with texture preview and editing capabilities
"""

import os
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QListWidgetItem, QLabel, QPushButton, QFrame, QFileDialog,
    QMessageBox, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMenu, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage

##Methods list -
# _create_left_panel
# _create_middle_panel
# _create_right_panel
# _create_thumbnail
# _create_toolbar
# _decompress_dxt1
# _decompress_dxt3
# _decompress_dxt5
# _decompress_uncompressed
# _extract_alpha_channel
# _extract_txd_from_img
# _export_alpha_only
# _load_img_txd_list
# _load_txd_textures
# _on_texture_selected
# _on_txd_selected
# _parse_single_texture
# _save_texture_png
# _show_texture_context_menu
# _update_texture_info
# export_all_textures
# export_selected_texture
# flip_texture
# import_texture
# load_from_img_archive
# open_img_archive
# open_txd_file
# save_txd_file
# setup_ui
# show_properties

##class TXDWorkshop: -
# __init__
# closeEvent

class TXDWorkshop(QWidget): #vers 3
    """TXD Workshop - Main texture editing window"""

    workshop_closed = pyqtSignal()

    def __init__(self, parent=None, main_window=None): #vers 4
        super().__init__(parent)
        self.main_window = main_window
        self.current_img = None
        self.current_txd_data = None
        self.current_txd_name = None
        self.txd_list = []
        self.texture_list = []
        self.selected_texture = None

        self.setWindowTitle("TXD Workshop: No File")
        self.resize(1200, 700)

        # Position window below menu bar
        if parent:
            parent_pos = parent.pos()
            self.move(parent_pos.x() + 50, parent_pos.y() + 80)

        self.setup_ui()
        self._apply_theme()

    def setup_ui(self): #vers 3
        """Setup the main UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)

        middle_panel = self._create_middle_panel()
        main_splitter.addWidget(middle_panel)

        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)

        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setStretchFactor(2, 5)

        main_layout.addWidget(main_splitter)

    def _apply_theme(self): #vers 1
        """Apply theme from main window"""
        try:
            if self.main_window and hasattr(self.main_window, 'app_settings'):
                from components.Txd_Editor.txd_workshop_theme import apply_theme_to_workshop, connect_workshop_to_theme_system
                apply_theme_to_workshop(self, self.main_window)
                connect_workshop_to_theme_system(self, self.main_window)
        except:
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #e0e0e0; }
                QListWidget { background-color: #1e1e1e; border: 1px solid #3a3a3a; }
                QListWidget::item:selected { background-color: #0d47a1; }
                QPushButton { background-color: #3a3a3a; border: 1px solid #4a4a4a; padding: 5px 15px; border-radius: 3px; }
                QPushButton:hover { background-color: #4a4a4a; }
            """)

    def _create_toolbar(self): #vers 2
        """Create toolbar with action buttons"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setMaximumHeight(50)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(5, 5, 5, 5)

        self.open_img_btn = QPushButton("📂 Open IMG")
        self.open_img_btn.clicked.connect(self.open_img_archive)
        layout.addWidget(self.open_img_btn)

        self.open_txd_btn = QPushButton("📄 Open TXD")
        self.open_txd_btn.clicked.connect(self.open_txd_file)
        layout.addWidget(self.open_txd_btn)

        self.save_txd_btn = QPushButton("💾 Save TXD")
        self.save_txd_btn.clicked.connect(self.save_txd_file)
        self.save_txd_btn.setEnabled(False)
        layout.addWidget(self.save_txd_btn)

        self.import_btn = QPushButton("📥 Import")
        self.import_btn.clicked.connect(self.import_texture)
        self.import_btn.setEnabled(False)
        layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_selected_texture)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        self.export_all_btn = QPushButton("📤 Export All")
        self.export_all_btn.clicked.connect(self.export_all_textures)
        self.export_all_btn.setEnabled(False)
        layout.addWidget(self.export_all_btn)

        self.flip_btn = QPushButton("🔄 Flip!")
        self.flip_btn.clicked.connect(self.flip_texture)
        self.flip_btn.setEnabled(False)
        layout.addWidget(self.flip_btn)

        self.props_btn = QPushButton("📋 Properties")
        self.props_btn.clicked.connect(self.show_properties)
        self.props_btn.setEnabled(False)
        layout.addWidget(self.props_btn)

        layout.addStretch()

        # Window controls on the right
        self.minimize_btn = QPushButton("_")
        self.minimize_btn.setMaximumWidth(30)
        self.minimize_btn.clicked.connect(self.showMinimized)
        layout.addWidget(self.minimize_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setMaximumWidth(30)
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        return toolbar

    def _create_left_panel(self): #vers 2
        """Create left panel - TXD file list from IMG"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(200)
        panel.setMaximumWidth(300)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        header = QLabel("TXD Files")
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(header)

        self.txd_list_widget = QListWidget()
        self.txd_list_widget.setAlternatingRowColors(True)
        self.txd_list_widget.itemClicked.connect(self._on_txd_selected)
        layout.addWidget(self.txd_list_widget)

        return panel

    def _create_middle_panel(self): #vers 3
        """Create middle panel - Texture list with context menu"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(250)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        header = QLabel("Textures")
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(header)

        self.texture_table = QTableWidget()
        self.texture_table.setColumnCount(2)
        self.texture_table.setHorizontalHeaderLabels(["Preview", "Details"])
        self.texture_table.horizontalHeader().setStretchLastSection(True)
        self.texture_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.texture_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.texture_table.setAlternatingRowColors(True)
        self.texture_table.itemSelectionChanged.connect(self._on_texture_selected)
        self.texture_table.setIconSize(QSize(64, 64))
        self.texture_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.texture_table.customContextMenuRequested.connect(self._show_texture_context_menu)
        layout.addWidget(self.texture_table)

        return panel


    def _show_texture_context_menu(self, position): #vers 1
        """Show right-click context menu for textures"""
        if not self.texture_table.selectedItems():
            return

        menu = QMenu(self)

        export_action = menu.addAction("📤 Export Texture")
        export_action.triggered.connect(self.export_selected_texture)

        export_alpha_action = menu.addAction("📤 Export Alpha Channel")
        export_alpha_action.triggered.connect(lambda: self._export_alpha_only())

        menu.addSeparator()

        import_action = menu.addAction("📥 Import/Replace")
        import_action.triggered.connect(self.import_texture)

        menu.addSeparator()

        view_alpha_action = menu.addAction("👁️ View Alpha Channel")
        view_alpha_action.triggered.connect(lambda: setattr(self, '_show_alpha', True) or self._update_texture_info(self.selected_texture))

        view_normal_action = menu.addAction("👁️ View Normal")
        view_normal_action.triggered.connect(lambda: setattr(self, '_show_alpha', False) or self._update_texture_info(self.selected_texture))

        menu.addSeparator()

        props_action = menu.addAction("📋 Properties")
        props_action.triggered.connect(self.show_properties)

        menu.exec(self.texture_table.viewport().mapToGlobal(position))

    def load_from_img_archive(self, img_path): #vers 1
        """Load TXD list from IMG archive"""
        try:
            if self.main_window and hasattr(self.main_window, 'current_img'):
                self.current_img = self.main_window.current_img
            else:
                from methods.img_core_classes import IMGFile
                self.current_img = IMGFile(img_path)
                self.current_img.open()

            img_name = os.path.basename(img_path)
            self.setWindowTitle(f"TXD Workshop: {img_name}")
            self._load_img_txd_list()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ TXD Workshop loaded: {img_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load IMG: {str(e)}")

    def _load_img_txd_list(self): #vers 1
        """Load TXD files from IMG archive"""
        try:
            self.txd_list_widget.clear()
            self.txd_list = []

            if not self.current_img:
                return

            for entry in self.current_img.entries:
                if entry.name.lower().endswith('.txd'):
                    self.txd_list.append(entry)
                    item = QListWidgetItem(entry.name)
                    item.setData(Qt.ItemDataRole.UserRole, entry)
                    size_kb = entry.size / 1024
                    item.setToolTip(f"{entry.name}\nSize: {size_kb:.1f} KB")
                    self.txd_list_widget.addItem(item)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"📋 Found {len(self.txd_list)} TXD files")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error loading TXD list: {str(e)}")

    def _on_txd_selected(self, item): #vers 1
        """Handle TXD file selection"""
        try:
            entry = item.data(Qt.ItemDataRole.UserRole)
            if entry:
                txd_data = self._extract_txd_from_img(entry)
                if txd_data:
                    self.current_txd_data = txd_data
                    self.current_txd_name = entry.name
                    self._load_txd_textures(txd_data, entry.name)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error selecting TXD: {str(e)}")

    def _extract_txd_from_img(self, entry): #vers 2
        """Extract TXD data from IMG entry"""
        try:
            if not self.current_img:
                return None
            return self.current_img.read_entry_data(entry)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Extract error: {str(e)}")
            return None

    def _load_txd_textures(self, txd_data, txd_name): #vers 10
        """Load textures from TXD data - display only in middle panel"""
        try:
            import struct

            self.texture_table.setRowCount(0)
            self.texture_list = []
            textures = []
            offset = 12

            # Get texture count
            texture_count = 0
            if offset + 12 < len(txd_data):
                try:
                    st, ss, sv = struct.unpack('<III', txd_data[offset:offset+12])
                    offset += 12
                    if ss >= 4:
                        texture_count = struct.unpack('<I', txd_data[offset:offset+4])[0]
                        offset += ss
                except:
                    pass

            # Parse each texture
            if 0 < texture_count < 500:
                for i in range(texture_count):
                    if offset + 12 > len(txd_data):
                        break
                    try:
                        stype, ssize, sver = struct.unpack('<III', txd_data[offset:offset+12])
                        if stype == 0x15:  # Texture Native
                            tex = self._parse_single_texture(txd_data, offset, i)
                            if tex:
                                textures.append(tex)
                        offset += 12 + ssize
                    except:
                        offset += 1000
                        continue

            if not textures:
                textures = [{'name': 'No textures', 'width': 0, 'height': 0, 'has_alpha': False, 'format': 'Unknown', 'mipmaps': 0, 'rgba_data': None}]

            # Populate table - DISPLAY ONLY
            for tex in textures:
                self.texture_list.append(tex)
                row = self.texture_table.rowCount()
                self.texture_table.insertRow(row)

                thumb_item = QTableWidgetItem()
                if tex.get('rgba_data') and tex['width'] > 0:
                    pixmap = self._create_thumbnail(tex['rgba_data'], tex['width'], tex['height'])
                    if pixmap:
                        thumb_item.setData(Qt.ItemDataRole.DecorationRole, pixmap)
                    else:
                        thumb_item.setText("🖼️")
                else:
                    thumb_item.setText("🖼️")

                # Build details text - DISPLAY ONLY
                details = f"Name: {tex['name']}\n"

                # Add alpha name if texture has alpha
                if tex.get('has_alpha', False):
                    alpha_name = tex.get('alpha_name', tex['name'] + 'a')
                    details += f"Alpha: {alpha_name}\n"

                if tex['width'] > 0:
                    details += f"Size: {tex['width']}x{tex['height']}\n"
                details += f"Format: {tex['format']}\n"
                details += f"Alpha: {'Yes' if tex.get('has_alpha', False) else 'No'}"

                # Make items non-editable
                thumb_item.setFlags(thumb_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                details_item = QTableWidgetItem(details)
                details_item.setFlags(details_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self.texture_table.setItem(row, 0, thumb_item)
                self.texture_table.setItem(row, 1, details_item)

            for row in range(self.texture_table.rowCount()):
                self.texture_table.setRowHeight(row, 80)
            self.texture_table.setColumnWidth(0, 80)

            self.save_txd_btn.setEnabled(True)
            self.import_btn.setEnabled(True)
            self.export_all_btn.setEnabled(True)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Loaded {len(textures)} textures from {txd_name}")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error: {str(e)}")

    def _rename_texture(self, alpha=False): #vers 1
        """Rename texture or alpha name"""
        from PyQt6.QtWidgets import QInputDialog

        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        current_name = self.selected_texture.get('name', 'texture')

        if alpha:
            # Only allow alpha renaming if texture has alpha
            if not self.selected_texture.get('has_alpha', False):
                QMessageBox.information(self, "No Alpha", "This texture does not have an alpha channel")
                return

            alpha_name = self.selected_texture.get('alpha_name', current_name + 'a')
            new_name, ok = QInputDialog.getText(self, "Rename Alpha", "Enter alpha name:", text=alpha_name)
            if ok and new_name:
                self.selected_texture['alpha_name'] = new_name
                self.info_alpha_name.setText(f"Alpha: {new_name}")
                self._update_table_display()
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Alpha renamed to: {new_name}")
        else:
            new_name, ok = QInputDialog.getText(self, "Rename Texture", "Enter texture name:", text=current_name)
            if ok and new_name and new_name != current_name:
                self.selected_texture['name'] = new_name
                self.info_name.setText(f"Name: {new_name}")
                self._update_table_display()
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Texture renamed: {current_name} -> {new_name}")

def _resize_texture(self): #vers 2
    """Resize selected texture with large size handling"""
    from PyQt6.QtWidgets import QInputDialog

    if not self.selected_texture:
        QMessageBox.warning(self, "No Selection", "Please select a texture first")
        return

    current_width = self.selected_texture.get('width', 256)
    current_height = self.selected_texture.get('height', 256)

    # Get new dimensions
    w, ok1 = QInputDialog.getInt(self, "Resize Texture", "New width:", value=current_width, min=1, max=4096)
    if not ok1:
        return
    h, ok2 = QInputDialog.getInt(self, "Resize Texture", "New height:", value=current_height, min=1, max=4096)
    if not ok2:
        return

    # Calculate size impact
    old_pixels = current_width * current_height
    new_pixels = w * h
    size_multiplier = new_pixels / old_pixels if old_pixels > 0 else 1

    if size_multiplier > 4:  # More than 4x pixel increase
        reply = QMessageBox.question(self, "Large Resize",
                                   f"Resizing to {w}x{h} will increase texture size by {size_multiplier:.1f}x. "
                                   f"This may require IMG rebuilding. Continue?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

    # Update texture data and mark as modified
    self.selected_texture['width'] = w
    self.selected_texture['height'] = h

    # If we had actual image data, we'd resize it here
    if self.selected_texture.get('rgba_data'):
        # This would need actual image resizing implementation
        self._resize_texture_data(w, h)

    self._update_texture_info(self.selected_texture)
    self._update_table_display()
    self._mark_as_modified()

    if self.main_window and hasattr(self.main_window, 'log_message'):
        self.main_window.log_message(f"Resized texture to {w}x{h} (size impact: {size_multiplier:.1f}x)")

    def _upscale_texture(self): #vers 2
        """AI upscale selected texture with size management"""
        from PyQt6.QtWidgets import QInputDialog

        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Get scale factor
        factor, ok = QInputDialog.getInt(self, "AI Upscale", "Scale factor:", value=2, min=2, max=8)
        if not ok:
            return

        current_width = self.selected_texture.get('width', 256)
        current_height = self.selected_texture.get('height', 256)

        new_width = current_width * factor
        new_height = current_height * factor

        # Calculate memory and file size impact
        old_size_mb = (current_width * current_height * 4) / (1024 * 1024)
        new_size_mb = (new_width * new_height * 4) / (1024 * 1024)

        if new_size_mb > 16:  # Warn for textures over 16MB uncompressed
            reply = QMessageBox.question(self, "Large Upscale",
                                    f"Upscaling {factor}x will create a {new_width}x{new_height} texture "
                                    f"(~{new_size_mb:.1f}MB uncompressed). "
                                    f"This will significantly increase TXD size. Continue?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Perform the upscale
        if self._perform_ai_upscale(factor):
            self.selected_texture['width'] = new_width
            self.selected_texture['height'] = new_height

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"AI upscaled texture {factor}x to {new_width}x{new_height}")
        else:
            QMessageBox.critical(self, "Error", "AI upscale failed")

    def _upscale_texture(self): #vers 2
        """AI upscale selected texture with size management"""
        from PyQt6.QtWidgets import QInputDialog

        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Get scale factor
        factor, ok = QInputDialog.getInt(self, "AI Upscale", "Scale factor:", value=2, min=2, max=8)
        if not ok:
            return

        current_width = self.selected_texture.get('width', 256)
        current_height = self.selected_texture.get('height', 256)

        new_width = current_width * factor
        new_height = current_height * factor

        # Calculate memory and file size impact
        old_size_mb = (current_width * current_height * 4) / (1024 * 1024)
        new_size_mb = (new_width * new_height * 4) / (1024 * 1024)

        if new_size_mb > 16:  # Warn for textures over 16MB uncompressed
            reply = QMessageBox.question(self, "Large Upscale",
                                    f"Upscaling {factor}x will create a {new_width}x{new_height} texture "
                                    f"(~{new_size_mb:.1f}MB uncompressed). "
                                    f"This will significantly increase TXD size. Continue?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Perform the upscale
        if self._perform_ai_upscale(factor):
            self.selected_texture['width'] = new_width
            self.selected_texture['height'] = new_height

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"AI upscaled texture {factor}x to {new_width}x{new_height}")
        else:
            QMessageBox.critical(self, "Error", "AI upscale failed")

    def _resize_texture_data(self, new_width, new_height): #vers 1
        """Resize the actual texture image data"""
        try:
            if not self.selected_texture.get('rgba_data'):
                return False

            # Convert current RGBA data to QImage
            rgba_data = self.selected_texture['rgba_data']
            old_width = self.selected_texture['width']
            old_height = self.selected_texture['height']

            qimg = QImage(rgba_data, old_width, old_height, old_width * 4, QImage.Format.Format_RGBA8888)

            # Resize image
            resized_img = qimg.scaled(new_width, new_height,
                                    Qt.AspectRatioMode.IgnoreAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)

            # Convert back to RGBA data
            resized_img = resized_img.convertToFormat(QImage.Format.Format_RGBA8888)
            new_rgba_data = resized_img.constBits().asstring(resized_img.sizeInBytes())

            self.selected_texture['rgba_data'] = new_rgba_data
            return True

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Resize data error: {str(e)}")
            return False

    def _perform_ai_upscale(self, factor): #vers 1
        """Perform AI upscaling on texture data"""
        try:
            if not self.selected_texture.get('rgba_data'):
                return False

            # For now, use basic upscaling (could be enhanced with actual AI upscaling libraries)
            return self._resize_texture_data(
                self.selected_texture['width'] * factor,
                self.selected_texture['height'] * factor
            )

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"AI upscale error: {str(e)}")
            return False

    def _calculate_new_txd_size(self): #vers 2
        """Enhanced size calculation including actual texture data"""
        estimated_size = 1024  # Header overhead

        for texture in self.texture_list:
            width = texture.get('width', 0)
            height = texture.get('height', 0)
            fmt = texture.get('format', 'DXT1')
            has_data = texture.get('rgba_data') is not None

            if has_data:
                # Use actual data size if available
                rgba_size = len(texture['rgba_data'])

                # Estimate compressed size based on format
                if 'DXT1' in fmt:
                    estimated_size += rgba_size // 8  # DXT1 compression
                elif 'DXT5' in fmt:
                    estimated_size += rgba_size // 4  # DXT5 compression
                else:
                    estimated_size += rgba_size  # Uncompressed
            else:
                # Fallback to dimension-based estimation
                if 'DXT1' in fmt:
                    estimated_size += (width * height) // 2
                elif 'DXT5' in fmt:
                    estimated_size += width * height
                else:
                    estimated_size += width * height * 4

            estimated_size += 200  # Header per texture

        return estimated_size

    def _change_format(self, format_name): #vers 1
        """Change texture format"""
        if not self.selected_texture:
            return

        old_format = self.selected_texture.get('format', 'Unknown')
        self.selected_texture['format'] = format_name

        # Update alpha flag based on format
        if format_name in ['DXT3', 'DXT5', 'ARGB8888', 'ARGB1555', 'ARGB4444']:
            self.selected_texture['has_alpha'] = True
        elif format_name in ['DXT1', 'RGB888', 'RGB565']:
            self.selected_texture['has_alpha'] = False

        self._update_texture_info(self.selected_texture)
        self._update_table_display()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Format changed: {old_format} -> {format_name}")

    def _compress_texture(self): #vers 1
        """Compress selected texture"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        current_format = self.selected_texture.get('format', 'ARGB8888')

        if 'DXT' in current_format:
            QMessageBox.information(self, "Already Compressed", "Texture is already compressed")
            return

        # Choose compression format based on alpha
        has_alpha = self.selected_texture.get('has_alpha', False)
        new_format = 'DXT5' if has_alpha else 'DXT1'

        self.selected_texture['format'] = new_format
        self._update_texture_info(self.selected_texture)
        self._update_table_display()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Compressed texture to {new_format}")

    def _uncompress_texture(self): #vers 1
        """Uncompress selected texture"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        current_format = self.selected_texture.get('format', 'ARGB8888')

        if 'DXT' not in current_format:
            QMessageBox.information(self, "Not Compressed", "Texture is not compressed")
            return

        # Uncompress to ARGB8888
        self.selected_texture['format'] = 'ARGB8888'
        self.selected_texture['has_alpha'] = True

        self._update_texture_info(self.selected_texture)
        self._update_table_display()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Uncompressed texture to ARGB8888")

    def _update_table_display(self): #vers 1
        """Update the middle panel table display after edits"""
        if not self.selected_texture:
            return

        row = self.texture_table.currentRow()
        if row < 0 or row >= len(self.texture_list):
            return

        tex = self.selected_texture

        # Rebuild details text
        details = f"Name: {tex['name']}\n"

        # Add alpha name if texture has alpha
        if tex.get('has_alpha', False):
            alpha_name = tex.get('alpha_name', tex['name'] + 'a')
            details += f"Alpha: {alpha_name}\n"

        if tex['width'] > 0:
            details += f"Size: {tex['width']}x{tex['height']}\n"
        details += f"Format: {tex['format']}\n"
        details += f"Alpha: {'Yes' if tex.get('has_alpha', False) else 'No'}"

        # Update the table item
        details_item = self.texture_table.item(row, 1)
        if details_item:
            details_item.setText(details)

    def _on_texture_selected(self): #vers 3
        """Handle texture selection and enable editing controls"""
        try:
            row = self.texture_table.currentRow()
            if row < 0 or row >= len(self.texture_list):
                # Disable all controls
                self.info_name.setEnabled(False)
                self.info_alpha_name.setEnabled(False)
                self.resize_btn.setEnabled(False)
                self.upscale_btn.setEnabled(False)
                self.format_combo.setEnabled(False)
                self.compress_btn.setEnabled(False)
                self.uncompress_btn.setEnabled(False)
                return

            self.selected_texture = self.texture_list[row]
            self._update_texture_info(self.selected_texture)

            # Enable editing controls
            self.export_btn.setEnabled(True)
            self.flip_btn.setEnabled(True)
            self.props_btn.setEnabled(True)
            self.info_name.setEnabled(True)
            self.resize_btn.setEnabled(True)
            self.upscale_btn.setEnabled(True)
            self.format_combo.setEnabled(True)
            self.compress_btn.setEnabled(False)
            self.uncompress_btn.setEnabled(False)

            # Enable alpha editing only if texture has alpha
            if self.selected_texture.get('has_alpha', False):
                self.info_alpha_name.setEnabled(True)
            else:
                self.info_alpha_name.setEnabled(False)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Selection error: {str(e)}")

    def _parse_single_texture(self, txd_data, offset, index): #vers 14
        """Parse single texture - Following working txd.py structure exactly"""
        import struct

        tex = {'name': f'texture_{index}', 'width': 0, 'height': 0, 'has_alpha': False, 'format': 'Unknown', 'mipmaps': 1, 'rgba_data': None}

        try:
            # TextureNative structure (from txd.py line 515):
            # Struct section contains: header(88 bytes) + palette(optional) + pixel data(size-prefixed)

            parent_type, parent_size, parent_version = struct.unpack('<III', txd_data[offset:offset+12])

            if parent_type != 0x15:
                return tex

            # Struct section
            struct_offset = offset + 12
            struct_type, struct_size, struct_version = struct.unpack('<III', txd_data[struct_offset:struct_offset+12])

            if struct_type != 0x01:
                return tex

            pos = struct_offset + 12

            # Read 88-byte header
            platform_id, filter_mode, uv_addressing = struct.unpack('<I2B', txd_data[pos:pos+6])[:3]
            pos += 8  # Skip padding

            name_bytes = txd_data[pos:pos+32]
            tex['name'] = name_bytes.rstrip(b'\x00').decode('ascii', errors='ignore') or f'texture_{index}'
            pos += 32

            mask_bytes = txd_data[pos:pos+32]
            pos += 32

            raster_format_flags, d3d_format, width, height, depth, num_levels, raster_type = struct.unpack('<IIHHBBB', txd_data[pos:pos+15])
            tex['width'] = width
            tex['height'] = height
            tex['mipmaps'] = num_levels
            pos += 15

            platform_prop = struct.unpack('<B', txd_data[pos:pos+1])[0]
            pos += 1

            # Format detection
            if platform_id == 8:  # D3D8
                if platform_prop == 1: tex['format'] = 'DXT1'
                elif platform_prop == 3: tex['format'] = 'DXT3'; tex['has_alpha'] = True
                elif platform_prop == 5: tex['format'] = 'DXT5'; tex['has_alpha'] = True
            elif platform_id == 9:  # D3D9
                if d3d_format == 827611204: tex['format'] = 'DXT1'
                elif d3d_format == 861165636: tex['format'] = 'DXT3'; tex['has_alpha'] = True
                elif d3d_format == 894720068: tex['format'] = 'DXT5'; tex['has_alpha'] = True

            # Now pos points to palette (if any) then pixel data
            # Check for palette (from raster_format_flags bits 13-14)
            palette_type = (raster_format_flags >> 13) & 0b11

            if palette_type == 1:  # 8-bit palette
                pos += 1024
            elif palette_type > 1:  # 4-bit palette
                if depth == 4:
                    pos += 64
                else:
                    pos += 128

            # Now read size-prefixed pixel data for FIRST mipmap level
            if pos + 4 < len(txd_data):
                pixels_len = struct.unpack('<I', txd_data[pos:pos+4])[0]
                pos += 4

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"{tex['name']}: {pixels_len} bytes at {pos}")

                if pos + pixels_len <= len(txd_data):
                    dxt_data = txd_data[pos:pos + pixels_len]

                    # Decompress
                    if 'DXT1' in tex['format']:
                        tex['rgba_data'] = self._decompress_dxt1(dxt_data, width, height)
                    elif 'DXT3' in tex['format']:
                        tex['rgba_data'] = self._decompress_dxt3(dxt_data, width, height)
                    elif 'DXT5' in tex['format']:
                        tex['rgba_data'] = self._decompress_dxt5(dxt_data, width, height)

                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        status = "✅" if tex['rgba_data'] else "❌"
                        self.main_window.log_message(f"{status} Decompress {tex['format']}")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"ERROR: {str(e)}")

        return tex

    def _decompress_dxt1(self, dxt_data, width, height): #vers 1
        """DXT1 decompression"""
        try:
            import struct
            rgba = bytearray(width * height * 4)
            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    block_offset = (by * blocks_x + bx) * 8
                    if block_offset + 8 > len(dxt_data):
                        break

                    c0, c1 = struct.unpack('<HH', dxt_data[block_offset:block_offset+4])
                    indices = struct.unpack('<I', dxt_data[block_offset+4:block_offset+8])[0]

                    colors = []
                    for c in [c0, c1]:
                        r = ((c >> 11) & 0x1F) << 3
                        g = ((c >> 5) & 0x3F) << 2
                        b = (c & 0x1F) << 3
                        colors.append((r, g, b, 255))

                    if c0 > c1:
                        colors.append(((2*colors[0][0]+colors[1][0])//3, (2*colors[0][1]+colors[1][1])//3, (2*colors[0][2]+colors[1][2])//3, 255))
                        colors.append(((colors[0][0]+2*colors[1][0])//3, (colors[0][1]+2*colors[1][1])//3, (colors[0][2]+2*colors[1][2])//3, 255))
                    else:
                        colors.append(((colors[0][0]+colors[1][0])//2, (colors[0][1]+colors[1][1])//2, (colors[0][2]+colors[1][2])//2, 255))
                        colors.append((0, 0, 0, 0))

                    for py in range(4):
                        for px in range(4):
                            if (bx*4+px < width) and (by*4+py < height):
                                index = (indices >> ((py*4+px)*2)) & 0x03
                                pixel_offset = ((by*4+py)*width+(bx*4+px))*4
                                rgba[pixel_offset:pixel_offset+4] = colors[index]
            return bytes(rgba)
        except:
            return None

    def _decompress_dxt3(self, dxt_data, width, height): #vers 1
        """DXT3 decompression"""
        try:
            import struct
            rgba = bytearray(width * height * 4)
            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    block_offset = (by * blocks_x + bx) * 16
                    if block_offset + 16 > len(dxt_data):
                        break

                    alpha_data = struct.unpack('<Q', dxt_data[block_offset:block_offset+8])[0]
                    c0, c1 = struct.unpack('<HH', dxt_data[block_offset+8:block_offset+12])
                    indices = struct.unpack('<I', dxt_data[block_offset+12:block_offset+16])[0]

                    colors = []
                    for c in [c0, c1]:
                        r = ((c >> 11) & 0x1F) << 3
                        g = ((c >> 5) & 0x3F) << 2
                        b = (c & 0x1F) << 3
                        colors.append((r, g, b))

                    colors.append(((2*colors[0][0]+colors[1][0])//3, (2*colors[0][1]+colors[1][1])//3, (2*colors[0][2]+colors[1][2])//3))
                    colors.append(((colors[0][0]+2*colors[1][0])//3, (colors[0][1]+2*colors[1][1])//3, (colors[0][2]+2*colors[1][2])//3))

                    for py in range(4):
                        for px in range(4):
                            if (bx*4+px < width) and (by*4+py < height):
                                color_index = (indices >> ((py*4+px)*2)) & 0x03
                                alpha_index = py*4 + px
                                alpha = ((alpha_data >> (alpha_index*4)) & 0x0F) * 17
                                pixel_offset = ((by*4+py)*width+(bx*4+px))*4
                                rgba[pixel_offset:pixel_offset+3] = colors[color_index]
                                rgba[pixel_offset+3] = alpha
            return bytes(rgba)
        except:
            return None

    def _decompress_dxt5(self, dxt_data, width, height): #vers 1
        """DXT5 decompression"""
        try:
            import struct
            rgba = bytearray(width * height * 4)
            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    block_offset = (by * blocks_x + bx) * 16
                    if block_offset + 16 > len(dxt_data):
                        break

                    a0 = dxt_data[block_offset]
                    a1 = dxt_data[block_offset + 1]
                    alpha_indices = struct.unpack('<Q', dxt_data[block_offset:block_offset+8])[0] >> 16
                    alpha_palette = [a0, a1]
                    if a0 > a1:
                        for i in range(1, 7):
                            alpha_palette.append(((7-i)*a0+i*a1)//7)
                    else:
                        for i in range(1, 5):
                            alpha_palette.append(((5-i)*a0+i*a1)//5)
                        alpha_palette.extend([0, 255])

                    c0, c1 = struct.unpack('<HH', dxt_data[block_offset+8:block_offset+12])
                    indices = struct.unpack('<I', dxt_data[block_offset+12:block_offset+16])[0]

                    colors = []
                    for c in [c0, c1]:
                        r = ((c >> 11) & 0x1F) << 3
                        g = ((c >> 5) & 0x3F) << 2
                        b = (c & 0x1F) << 3
                        colors.append((r, g, b))

                    colors.append(((2*colors[0][0]+colors[1][0])//3, (2*colors[0][1]+colors[1][1])//3, (2*colors[0][2]+colors[1][2])//3))
                    colors.append(((colors[0][0]+2*colors[1][0])//3, (colors[0][1]+2*colors[1][1])//3, (colors[0][2]+2*colors[1][2])//3))

                    for py in range(4):
                        for px in range(4):
                            if (bx*4+px < width) and (by*4+py < height):
                                color_index = (indices >> ((py*4+px)*2)) & 0x03
                                alpha_index = (alpha_indices >> ((py*4+px)*3)) & 0x07
                                pixel_offset = ((by*4+py)*width+(bx*4+px))*4
                                rgba[pixel_offset:pixel_offset+3] = colors[color_index]
                                rgba[pixel_offset+3] = alpha_palette[alpha_index]
            return bytes(rgba)
        except:
            return None

    def _decompress_uncompressed(self, data, width, height, format_type): #vers 1
        """Decompress uncompressed formats"""
        try:
            import struct
            rgba = bytearray(width * height * 4)

            if 'ARGB8888' in format_type or 'ARGB32' in format_type:
                for i in range(width * height):
                    if i*4+4 <= len(data):
                        b,g,r,a = struct.unpack('BBBB', data[i*4:i*4+4])
                        rgba[i*4:i*4+4] = [r,g,b,a]

            elif 'RGB565' in format_type:
                for i in range(width * height):
                    if i*2+2 <= len(data):
                        pixel = struct.unpack('<H', data[i*2:i*2+2])[0]
                        r = ((pixel >> 11) & 0x1F) << 3
                        g = ((pixel >> 5) & 0x3F) << 2
                        b = (pixel & 0x1F) << 3
                        rgba[i*4:i*4+4] = [r,g,b,255]

            elif 'ARGB1555' in format_type:
                for i in range(width * height):
                    if i*2+2 <= len(data):
                        pixel = struct.unpack('<H', data[i*2:i*2+2])[0]
                        a = 255 if (pixel & 0x8000) else 0
                        r = ((pixel >> 10) & 0x1F) << 3
                        g = ((pixel >> 5) & 0x1F) << 3
                        b = (pixel & 0x1F) << 3
                        rgba[i*4:i*4+4] = [r,g,b,a]

            elif 'ARGB4444' in format_type:
                for i in range(width * height):
                    if i*2+2 <= len(data):
                        pixel = struct.unpack('<H', data[i*2:i*2+2])[0]
                        a = ((pixel >> 12) & 0x0F) * 17
                        r = ((pixel >> 8) & 0x0F) * 17
                        g = ((pixel >> 4) & 0x0F) * 17
                        b = (pixel & 0x0F) * 17
                        rgba[i*4:i*4+4] = [r,g,b,a]

            elif 'LUM8' in format_type or 'L8' in format_type:
                for i in range(width * height):
                    if i < len(data):
                        lum = data[i]
                        rgba[i*4:i*4+4] = [lum,lum,lum,255]

            return bytes(rgba)
        except:
            return None

    def _create_thumbnail(self, rgba_data, width, height): #vers 1
        """Create thumbnail from RGBA data"""
        try:
            if not rgba_data or width <= 0 or height <= 0:
                return None

            image = QImage(rgba_data, width, height, width*4, QImage.Format.Format_RGBA8888)
            if image.isNull():
                return None

            pixmap = QPixmap.fromImage(image)
            return pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        except:
            return None

    def _on_texture_selected(self): #vers 1
        """Handle texture selection"""
        try:
            row = self.texture_table.currentRow()
            if row < 0 or row >= len(self.texture_list):
                return

            self.selected_texture = self.texture_list[row]
            self._update_texture_info(self.selected_texture)
            self.export_btn.setEnabled(True)
            self.flip_btn.setEnabled(True)
            self.props_btn.setEnabled(True)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Selection error: {str(e)}")

    def _create_right_panel(self): #vers 6
        """Create clean right panel with right-click rename context menu"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(400)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        self.preview_label = QLabel("No texture selected")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(400)
        self.preview_label.setStyleSheet("border: 1px solid #3a3a3a; background-color: #1e1e1e;")
        layout.addWidget(self.preview_label)

        info_group = QGroupBox("Texture Information")
        info_layout = QVBoxLayout(info_group)

        # Texture name with right-click context menu
        self.info_name = QLabel("Name: -")
        self.info_name.setStyleSheet("font-weight: bold; padding: 5px;")
        self.info_name.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.info_name.customContextMenuRequested.connect(lambda pos: self._show_name_context_menu(pos, alpha=False))
        info_layout.addWidget(self.info_name)

        # Alpha name with right-click context menu
        self.info_alpha_name = QLabel("")
        self.info_alpha_name.setStyleSheet("color: red; font-weight: bold; padding: 5px;")
        self.info_alpha_name.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.info_alpha_name.customContextMenuRequested.connect(lambda pos: self._show_name_context_menu(pos, alpha=True))
        info_layout.addWidget(self.info_alpha_name)

        # Size with resize controls
        size_layout = QHBoxLayout()
        self.info_size = QLabel("Size: -")
        size_layout.addWidget(self.info_size)

        self.resize_btn = QPushButton("Resize")
        self.resize_btn.setEnabled(False)
        size_layout.addWidget(self.resize_btn)

        self.upscale_btn = QPushButton("AI Upscale")
        self.upscale_btn.setEnabled(False)
        size_layout.addWidget(self.upscale_btn)

        info_layout.addLayout(size_layout)

        # Format dropdown with compression status
        format_layout = QHBoxLayout()
        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["DXT1", "DXT3", "DXT5", "ARGB8888", "ARGB1555", "ARGB4444", "RGB888", "RGB565"])
        self.format_combo.setEnabled(False)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)

        self.compress_btn = QPushButton("Compress")
        self.compress_btn.setEnabled(False)
        format_layout.addWidget(self.compress_btn)

        self.uncompress_btn = QPushButton("Uncompress")
        self.uncompress_btn.setEnabled(False)
        format_layout.addWidget(self.uncompress_btn)

        info_layout.addLayout(format_layout)

        layout.addWidget(info_group)
        return panel

    def _show_name_context_menu(self, position, alpha=False): #vers 1
        """Show context menu for renaming texture or alpha name"""
        if not self.selected_texture:
            return

        # Don't show alpha context menu if no alpha channel
        if alpha and not self.selected_texture.get('has_alpha', False):
            return

        menu = QMenu(self)

        if alpha:
            rename_action = menu.addAction("Rename Alpha")
            rename_action.triggered.connect(lambda: self._rename_texture(alpha=True))
        else:
            rename_action = menu.addAction("Rename Texture")
            rename_action.triggered.connect(lambda: self._rename_texture(alpha=False))

        # Show menu at the cursor position
        if alpha:
            menu.exec(self.info_alpha_name.mapToGlobal(position))
        else:
            menu.exec(self.info_name.mapToGlobal(position))

    def _update_texture_info(self, texture): #vers 5
        """Update texture information display - clean version with consistent spacing"""
        try:
            name = texture.get('name', 'Unknown')
            width = texture.get('width', 0)
            height = texture.get('height', 0)
            has_alpha = texture.get('has_alpha', False)
            fmt = texture.get('format', 'Unknown')

            # Update clickable name
            self.info_name.setText(f"Name: {name}")

            # Update alpha name space (always present for consistent spacing)
            if has_alpha:
                alpha_name = texture.get('alpha_name', name + 'a')
                self.info_alpha_name.setText(f"Alpha: {alpha_name}")
                self.info_alpha_name.setStyleSheet("text-align: left; color: red; font-weight: bold;")
            else:
                # Keep the space but make it empty
                self.info_alpha_name.setText("")
                self.info_alpha_name.setStyleSheet("text-align: left;")

            # Update size
            self.info_size.setText(f"Size: {width}x{height}" if width > 0 else "Size: Unknown")

            # Update format combo to match current format
            if hasattr(self, 'format_combo'):
                index = self.format_combo.findText(fmt)
                if index >= 0:
                    self.format_combo.setCurrentIndex(index)

            # Show preview (existing preview code...)
            rgba_data = texture.get('rgba_data')
            if rgba_data and width > 0 and height > 0:
                if hasattr(self, '_show_alpha') and self._show_alpha:
                    alpha_data = bytearray()
                    for i in range(0, len(rgba_data), 4):
                        a = rgba_data[i+3]
                        alpha_data.extend([a, a, a, 255])
                    display_data = bytes(alpha_data)
                else:
                    display_data = rgba_data

                image = QImage(display_data, width, height, width*4, QImage.Format.Format_RGBA8888)

                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    label_size = self.preview_label.size()
                    scaled_pixmap = pixmap.scaled(label_size.width()-20, label_size.height()-20,
                                                Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation)
                    self.preview_label.setPixmap(scaled_pixmap)

                    if hasattr(self, 'flip_btn'):
                        if hasattr(self, '_show_alpha') and self._show_alpha:
                            self.flip_btn.setText("Normal")
                        else:
                            self.flip_btn.setText("Alpha")
                    return

            self.preview_label.setText("Preview not available")
        except Exception as e:
            self.preview_label.setText(f"Preview error: {str(e)}")

    def flip_texture(self): #vers 1
        """Flip between normal and alpha channel view"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Toggle alpha view flag
        if not hasattr(self, '_show_alpha'):
            self._show_alpha = False

        self._show_alpha = not self._show_alpha
        self._update_texture_info(self.selected_texture)

        mode = "Alpha Channel" if self._show_alpha else "Normal View"
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Switched to {mode}")

    def export_selected_texture(self): #vers 2
        """Export selected texture with channel options"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            name = self.selected_texture.get('name', 'texture')

            # Ask user what to export
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Export Options")
            dialog.setText(f"Export {name} as:")

            normal_btn = dialog.addButton("Normal (RGBA)", QMessageBox.ButtonRole.AcceptRole)
            alpha_btn = dialog.addButton("Alpha Channel Only", QMessageBox.ButtonRole.AcceptRole)
            both_btn = dialog.addButton("Both Separately", QMessageBox.ButtonRole.AcceptRole)
            cancel_btn = dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

            dialog.exec()
            clicked = dialog.clickedButton()

            if clicked == cancel_btn:
                return

            # Get save location
            default_name = f"{name}.png"
            file_path, _ = QFileDialog.getSaveFileName(self, "Export Texture", default_name,
                                                    "PNG Files (*.png);;All Files (*)")

            if not file_path:
                return

            rgba_data = self.selected_texture.get('rgba_data')
            width = self.selected_texture.get('width', 0)
            height = self.selected_texture.get('height', 0)

            if not rgba_data or width <= 0:
                QMessageBox.critical(self, "Error", "Cannot export this texture")
                return

            if clicked == normal_btn:
                self._save_texture_png(rgba_data, width, height, file_path)
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Exported: {file_path}")

            elif clicked == alpha_btn:
                alpha_data = self._extract_alpha_channel(rgba_data)
                self._save_texture_png(alpha_data, width, height, file_path)
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Exported alpha: {file_path}")

            elif clicked == both_btn:
                # Save normal
                self._save_texture_png(rgba_data, width, height, file_path)
                # Save alpha
                alpha_path = file_path.replace('.png', '_alpha.png')
                alpha_data = self._extract_alpha_channel(rgba_data)
                self._save_texture_png(alpha_data, width, height, alpha_path)
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Exported both: {file_path} and {alpha_path}")

            QMessageBox.information(self, "Success", "Texture exported successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def export_all_textures(self): #vers 1
        """Export all textures in current TXD"""
        if not self.texture_list:
            QMessageBox.warning(self, "No Textures", "No textures to export")
            return

        # Ask for output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not output_dir:
            return

        try:
            exported = 0
            for texture in self.texture_list:
                name = texture.get('name', f'texture_{exported}')
                rgba_data = texture.get('rgba_data')
                width = texture.get('width', 0)
                height = texture.get('height', 0)

                if rgba_data and width > 0:
                    file_path = os.path.join(output_dir, f"{name}.png")
                    self._save_texture_png(rgba_data, width, height, file_path)
                    exported += 1

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Exported {exported} textures to {output_dir}")

            QMessageBox.information(self, "Success", f"Exported {exported} textures successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def _extract_alpha_channel(self, rgba_data): #vers 1
        """Extract alpha channel as grayscale RGBA"""
        alpha_data = bytearray()
        for i in range(0, len(rgba_data), 4):
            a = rgba_data[i+3]
            alpha_data.extend([a, a, a, 255])
        return bytes(alpha_data)

    def _save_texture_png(self, rgba_data, width, height, file_path): #vers 1
        """Save RGBA data as PNG"""
        image = QImage(rgba_data, width, height, width*4, QImage.Format.Format_RGBA8888)
        if not image.save(file_path):
            raise Exception("Failed to save PNG")

    def _export_alpha_only(self): #vers 1
        """Export only alpha channel"""
        if not self.selected_texture:
            return

        name = self.selected_texture.get('name', 'texture')
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Alpha Channel", f"{name}_alpha.png",
                                                "PNG Files (*.png)")
        if file_path:
            rgba_data = self.selected_texture.get('rgba_data')
            width = self.selected_texture.get('width', 0)
            height = self.selected_texture.get('height', 0)

            if rgba_data:
                alpha_data = self._extract_alpha_channel(rgba_data)
                self._save_texture_png(alpha_data, width, height, file_path)
                QMessageBox.information(self, "Success", "Alpha channel exported!")

    def import_texture(self): #vers 1
        """Import texture to replace selected"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to replace")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Import Texture", "",
                                                "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)")
        if file_path:
            QMessageBox.information(self, "Coming Soon", "Import functionality will be added soon!")

    def save_txd_file(self): #vers 4
        """Enhanced save for modding with large texture support"""
        if not self.texture_list or not self.current_txd_name:
            QMessageBox.warning(self, "No TXD", "No TXD file loaded to save")
            return

        try:
            # Use enhanced rebuilding for large textures
            modified_txd_data = self._rebuild_txd_with_size_management()

            if modified_txd_data:
                # Use enhanced IMG updating
                if self._update_img_with_large_txd(modified_txd_data):
                    self._post_save_cleanup()
                    QMessageBox.information(self, "Success",
                                        "TXD saved successfully! Large textures may have triggered IMG rebuild.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to save TXD with large textures")
            else:
                QMessageBox.critical(self, "Error", "Failed to rebuild TXD data")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save TXD: {str(e)}")

    def _rebuild_txd_data(self): #vers 1
        """Rebuild TXD data with modified texture names"""
        try:
            import struct

            if not self.current_txd_data or not self.texture_list:
                return None

            # Start with original TXD data
            original_data = bytearray(self.current_txd_data)

            # Parse and update texture names
            offset = 12

            # Skip to texture count
            if offset + 12 < len(original_data):
                st, ss, sv = struct.unpack('<III', original_data[offset:offset+12])
                offset += 12
                if ss >= 4:
                    texture_count = struct.unpack('<I', original_data[offset:offset+4])[0]
                    offset += ss

                    # Update each texture's name in the binary data
                    texture_index = 0
                    for i in range(texture_count):
                        if offset + 12 > len(original_data) or texture_index >= len(self.texture_list):
                            break

                        stype, ssize, sver = struct.unpack('<III', original_data[offset:offset+12])
                        if stype == 0x15:  # Texture Native
                            # Update texture name in binary data
                            self._update_texture_name_in_data(original_data, offset, self.texture_list[texture_index])
                            texture_index += 1

                        offset += 12 + ssize

            return bytes(original_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Rebuild error: {str(e)}")
            return None

    def _update_img_with_txd(self, modified_txd_data): #vers 3
        """Update the IMG archive with the modified TXD data and force save"""
        try:
            if not self.current_img or not self.current_txd_name:
                return False

            # Find the TXD entry in the IMG
            txd_entry = None
            for entry in self.current_img.entries:
                if entry.name == self.current_txd_name:
                    txd_entry = entry
                    break

            if not txd_entry:
                raise Exception(f"TXD entry {self.current_txd_name} not found in IMG")

            # Update the entry's data directly
            old_size = txd_entry.size
            txd_entry.data = modified_txd_data
            txd_entry.size = len(modified_txd_data)

            # Mark IMG as modified (important for save detection)
            if hasattr(self.current_img, 'modified'):
                self.current_img.modified = True
            if hasattr(self.current_img, 'is_modified'):
                self.current_img.is_modified = True
            if hasattr(self.current_img, '_modified'):
                self.current_img._modified = True

            # Force save the IMG file
            if hasattr(self.current_img, 'save'):
                result = self.current_img.save()
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"IMG save result: {result}")
            elif hasattr(self.current_img, 'write'):
                self.current_img.write()
            else:
                # Use main window save function
                if self.main_window and hasattr(self.main_window, 'save_current_img'):
                    self.main_window.save_current_img()
                else:
                    # Try to find and call the save function from core
                    try:
                        from core.save_entry import save_img_file
                        save_img_file(self.main_window, self.current_img)
                    except ImportError:
                        if self.main_window and hasattr(self.main_window, 'log_message'):
                            self.main_window.log_message("Warning: Could not find save function - changes in memory only")

            # Log the change details
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"TXD {self.current_txd_name} updated: {old_size} -> {len(modified_txd_data)} bytes")

            return True

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"IMG update error: {str(e)}")
            return False

    def _refresh_main_window(self): #vers 1
        """Refresh the main window to show changes"""
        try:
            if self.main_window:
                # Try to refresh the main table
                if hasattr(self.main_window, 'refresh_table'):
                    self.main_window.refresh_table()
                elif hasattr(self.main_window, 'reload_current_file'):
                    self.main_window.reload_current_file()
                elif hasattr(self.main_window, 'update_display'):
                    self.main_window.update_display()

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Refresh error: {str(e)}")

    def _mark_as_modified(self): #vers 1
        """Mark the TXD as modified and enable save button"""
        self.save_txd_btn.setEnabled(True)
        self.save_txd_btn.setStyleSheet("background-color: #ff6b35; font-weight: bold;")  # Orange highlight

        # Update window title to show unsaved changes
        current_title = self.windowTitle()
        if not current_title.endswith("*"):
            self.setWindowTitle(current_title + "*")

    def _rename_texture(self, alpha=False): #vers 2
        """Rename texture or alpha name and mark as modified"""
        from PyQt6.QtWidgets import QInputDialog

        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        current_name = self.selected_texture.get('name', 'texture')

        if alpha:
            if not self.selected_texture.get('has_alpha', False):
                QMessageBox.information(self, "No Alpha", "This texture does not have an alpha channel")
                return

            alpha_name = self.selected_texture.get('alpha_name', current_name + 'a')
            new_name, ok = QInputDialog.getText(self, "Rename Alpha", "Enter alpha name:", text=alpha_name)
            if ok and new_name and new_name != alpha_name:
                self.selected_texture['alpha_name'] = new_name
                self.info_alpha_name.setText(f"Alpha: {new_name}")
                self._update_table_display()
                self._mark_as_modified()  # Mark as modified
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Alpha renamed to: {new_name}")
        else:
            new_name, ok = QInputDialog.getText(self, "Rename Texture", "Enter texture name:", text=current_name)
            if ok and new_name and new_name != current_name:
                self.selected_texture['name'] = new_name
                self.info_name.setText(f"Name: {new_name}")
                self._update_table_display()
                self._mark_as_modified()  # Mark as modified
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Texture renamed: {current_name} -> {new_name}")

    def _mark_as_modified(self): #vers 1
        """Mark the TXD as modified and enable save button"""
        self.save_txd_btn.setEnabled(True)
        self.save_txd_btn.setStyleSheet("background-color: #ff6b35; font-weight: bold;")  # Orange highlight

    def _update_texture_name_in_data(self, data, offset, texture_info): #vers 1
        """Update texture name in the binary TXD data"""
        try:
            import struct

            # Navigate to the texture name location (offset + 12 for section header + 8 for platform info + name at pos 32)
            struct_offset = offset + 12
            struct_type, struct_size, struct_version = struct.unpack('<III', data[struct_offset:struct_offset+12])

            if struct_type == 0x01:  # Struct section
                name_pos = struct_offset + 12 + 8  # Skip header and platform info

                # Update texture name (32 bytes)
                new_name = texture_info.get('name', 'texture')[:31]  # Max 31 chars + null terminator
                name_bytes = new_name.encode('ascii')[:31].ljust(32, b'\x00')
                data[name_pos:name_pos+32] = name_bytes

                # Update alpha/mask name if it exists (next 32 bytes)
                if texture_info.get('has_alpha', False) and texture_info.get('alpha_name'):
                    alpha_name = texture_info.get('alpha_name', '')[:31]
                    alpha_bytes = alpha_name.encode('ascii')[:31].ljust(32, b'\x00')
                    data[name_pos+32:name_pos+64] = alpha_bytes

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Name update error: {str(e)}")

        # Update window title to show unsaved changes
        current_title = self.windowTitle()
        if not current_title.endswith("*"):
            self.setWindowTitle(current_title + "*")

    def _rebuild_txd_with_size_management(self): #vers 1
        """Rebuild TXD data with support for large texture replacements"""
        try:
            import struct

            if not self.current_txd_data or not self.texture_list:
                return None

            # Calculate new TXD size requirements
            estimated_size = self._calculate_new_txd_size()
            original_size = len(self.current_txd_data)

            if estimated_size > original_size * 3:  # More than 3x size increase
                reply = QMessageBox.question(self, "Large Texture Replacement",
                                        f"New TXD will be ~{estimated_size/1024/1024:.1f}MB "
                                        f"(was {original_size/1024/1024:.1f}MB). "
                                        f"This may require IMG rebuilding. Continue?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply != QMessageBox.StandardButton.Yes:
                    return None

            # Build new TXD from scratch rather than modifying existing
            return self._build_new_txd_structure()

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"TXD rebuild error: {str(e)}")
            return None

    def _requires_img_rebuild(self, new_txd_data): #vers 1
        """Check if IMG needs full rebuild due to size changes"""
        if not self.current_txd_data:
            return True

        size_ratio = len(new_txd_data) / len(self.current_txd_data)
        return size_ratio > 2.0  # Rebuild if more than 2x size increase

    def _update_img_with_large_txd(self, modified_txd_data): #vers 1
        """Handle IMG update with potentially large TXD replacements"""
        try:
            if self._requires_img_rebuild(modified_txd_data):
                return self._rebuild_img_with_new_txd(modified_txd_data)
            else:
                return self._update_img_in_place(modified_txd_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"IMG update error: {str(e)}")
            return False

    def _rebuild_img_with_new_txd(self, new_txd_data): #vers 1
        """Rebuild entire IMG file to accommodate large TXD"""
        try:
            # This would require integration with your IMG rebuilding system
            if self.main_window and hasattr(self.main_window, 'rebuild_current_img'):
                # Update TXD data first
                for entry in self.current_img.entries:
                    if entry.name == self.current_txd_name:
                        entry.data = new_txd_data
                        entry.size = len(new_txd_data)
                        break

                # Trigger full IMG rebuild
                result = self.main_window.rebuild_current_img()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"IMG rebuilt due to large TXD size change")

                return result
            else:
                # Fallback: save to new file
                return self._save_as_new_img(new_txd_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"IMG rebuild error: {str(e)}")
            return False

    def _save_as_new_img(self, new_txd_data): #vers 1
        """Save as new IMG file when rebuild is needed"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save IMG with Large Textures",
                self.current_img.file_path.replace('.img', '_hd.img'),
                "IMG Files (*.img);;All Files (*)"
            )

            if file_path:
                # Update TXD data
                for entry in self.current_img.entries:
                    if entry.name == self.current_txd_name:
                        entry.data = new_txd_data
                        entry.size = len(new_txd_data)
                        break

                # Save as new file
                self.current_img.save_as(file_path)

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Saved as new IMG: {file_path}")

                return True

            return False

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Save as new error: {str(e)}")
            return False

    def open_img_archive(self): #vers 1
        """Open IMG archive and load TXD file list"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open IMG Archive", "", "IMG Files (*.img);;All Files (*)")
            if file_path:
                self.load_from_img_archive(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open IMG: {str(e)}")


    def open_txd_file(self, file_path=None): #vers 2
        """Open standalone TXD file"""
        try:
            if not file_path:
                file_path, _ = QFileDialog.getOpenFileName(self, "Open TXD File", "", "TXD Files (*.txd);;All Files (*)")

            if file_path:
                with open(file_path, 'rb') as f:
                    txd_data = f.read()
                self._load_txd_textures(txd_data, os.path.basename(file_path))
                self.setWindowTitle(f"TXD Workshop: {os.path.basename(file_path)}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open TXD: {str(e)}")

    def import_texture(self): #vers 1
        """Import texture to replace selected"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to replace")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Import Texture", "",
                                                "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)")
        if file_path:
            QMessageBox.information(self, "Coming Soon", "Import functionality will be added soon!")

    def show_properties(self): #vers 1
        """Show detailed texture properties"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        QMessageBox.information(self, "Coming Soon", "Properties dialog will be added soon!")

    def closeEvent(self, event): #vers 1
        """Handle window close"""
        self.workshop_closed.emit()
        event.accept()


def open_txd_workshop(main_window, img_path=None): #vers 2
    """Open TXD Workshop from main window"""
    try:
        workshop = TXDWorkshop(main_window, main_window)

        if img_path:
            # Check if it's a TXD file or IMG file
            if img_path.lower().endswith('.txd'):
                # Load standalone TXD file
                workshop.open_txd_file(img_path)
            else:
                # Load from IMG archive
                workshop.load_from_img_archive(img_path)
        elif main_window and hasattr(main_window, 'current_img') and main_window.current_img:
            workshop.load_from_img_archive(main_window.current_img.file_path)

        workshop.show()
        return workshop
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to open TXD Workshop: {str(e)}")
        return None
