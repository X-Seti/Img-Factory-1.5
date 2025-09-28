#this belongs in components/Txd_Editor/ txd_workshop.py - Version: 3
# X-Seti - September26 2025 - Img Factory 1.5 - TXD Workshop

"""
TXD Workshop - Main texture editing window for IMG Factory
Displays TXD files from IMG archives with texture preview and editing capabilities
"""

import os
import struct
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QListWidgetItem, QLabel, QPushButton, QFrame, QFileDialog,
    QMessageBox, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QInputDialog, QComboBox, QMenu
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
# _extract_txd_from_img
# _load_img_txd_list
# _load_txd_textures
# _on_texture_selected
# _on_txd_selected
# _parse_single_texture
# _update_texture_info
# export_selected_texture
# load_from_img_archive
# open_img_archive
# open_txd_file
# save_txd_file
# setup_ui

##class TXDWorkshop: -
# __init__
# closeEvent

# Helper constants for RenderWare chunk IDs
RW_TEXTURE_DICTIONARY = 0x16
RW_TEXTURE_NATIVE = 0x15
RW_STRUCT = 0x01
RW_STRING = 0x02

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

        self.open_img_btn = QPushButton("Open IMG")
        self.open_img_btn.clicked.connect(self.open_img_archive)
        layout.addWidget(self.open_img_btn)

        self.open_txd_btn = QPushButton("Open TXD")
        self.open_txd_btn.clicked.connect(self.open_txd_file)
        layout.addWidget(self.open_txd_btn)

        self.save_txd_btn = QPushButton("Save TXD")
        self.save_txd_btn.clicked.connect(self.save_txd_file)
        self.save_txd_btn.setEnabled(False)
        layout.addWidget(self.save_txd_btn)

        self.import_btn = QPushButton("Import")
        self.import_btn.clicked.connect(self.import_texture)
        self.import_btn.setEnabled(False)
        layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_selected_texture)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        self.export_all_btn = QPushButton("Export All")
        self.export_all_btn.clicked.connect(self.export_all_textures)
        self.export_all_btn.setEnabled(False)
        layout.addWidget(self.export_all_btn)


        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._edit_texture)
        self.edit_btn.setEnabled(False)
        layout.addWidget(self.edit_btn)

        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self._convert_texture)
        self.convert_btn.setEnabled(False)
        layout.addWidget(self.convert_btn)

        self.flip_btn = QPushButton("Flip!")
        self.flip_btn.clicked.connect(self.flip_texture)
        self.flip_btn.setEnabled(False)
        layout.addWidget(self.flip_btn)

        self.props_btn = QPushButton("Properties")
        self.props_btn.clicked.connect(self.show_properties)
        self.props_btn.setEnabled(False)
        layout.addWidget(self.props_btn)

        layout.addStretch()
        return toolbar

    def _create_left_panel(self): #vers 3
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

    def _create_middle_panel(self):
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

    def _create_right_panel(self):
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

        # Name clickable
        self.info_name = QPushButton("Name: -")
        self.info_name.clicked.connect(lambda: self._rename_texture(alpha=False))
        self.info_name.setFlat(True)
        info_layout.addWidget(self.info_name)

        # Alpha clickable
        self.info_alpha_name = QPushButton("Alpha: -")
        self.info_alpha_name.clicked.connect(lambda: self._rename_texture(alpha=True))
        self.info_alpha_name.setFlat(True)
        self.info_alpha_name.setStyleSheet("color: red;")
        info_layout.addWidget(self.info_alpha_name)

        # Size + resize options
        size_layout = QHBoxLayout()
        self.info_size = QLabel("Size: -")
        size_layout.addWidget(self.info_size)
        self.resize_btn = QPushButton("Resize")
        self.resize_btn.clicked.connect(self._resize_texture)
        size_layout.addWidget(self.resize_btn)
        self.upscale_btn = QPushButton("AI Upscale")
        self.upscale_btn.clicked.connect(self._upscale_texture)
        size_layout.addWidget(self.upscale_btn)
        info_layout.addLayout(size_layout)

        # Format dropdown
        fmt_layout = QHBoxLayout()
        fmt_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["DXT1", "DXT3", "DXT5", "ARGB8888", "ARGB1555", "ARGB4444"])
        self.format_combo.currentTextChanged.connect(self._change_format)
        fmt_layout.addWidget(fmt_label)
        fmt_layout.addWidget(self.format_combo)
        info_layout.addLayout(fmt_layout)

        # Compression info
        self.info_compression = QLabel("Compression: -")
        info_layout.addWidget(self.info_compression)

        layout.addWidget(info_group)
        return panel

    # --- Core helpers ---
    def _log(self, msg):
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(msg)


    def _qimage_to_rgba_bytes(self, image: QImage) -> bytes:
        """Convert QImage (RGBA8888) to raw bytes in RGBA order."""
        if image.format() != QImage.Format.Format_RGBA8888:
            image = image.convertToFormat(QImage.Format.Format_RGBA8888)
        width = image.width()
        height = image.height()
        ptr = image.bits()
        ptr.setsize(width * height * 4)
        return bytes(ptr)

    def _rgba_bytes_to_qimage(self, data: bytes, width: int, height: int) -> Optional[QImage]:
        try:
            image = QImage(data, width, height, width * 4, QImage.Format.Format_RGBA8888)
            return image.copy()
        except Exception:
            return None


    def _rename_texture(self): #vers 1
        """Rename selected texture"""
        from PyQt6.QtWidgets import QInputDialog

        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        old_name = self.selected_texture.get('name', 'texture')

        new_name, ok = QInputDialog.getText(
            self,
            "Rename Texture",
            "Enter new name:",
            text=old_name
        )

        if ok and new_name and new_name != old_name:
            self.selected_texture['name'] = new_name

            row = self.texture_table.currentRow()
            if row >= 0:
                details_item = self.texture_table.item(row, 1)
                if details_item:
                    text = details_item.text()
                    updated_text = text.replace(f"Name: {old_name}", f"Name: {new_name}")
                    details_item.setText(updated_text)

            self.info_name.setText(f"Name: {new_name}")

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Texture renamed: {old_name} -> {new_name}")

    def open_img_archive(self): #vers 1
        """Open IMG archive and load TXD file list"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open IMG Archive", "", "IMG Files (*.img);;All Files (*)")
            if file_path:
                self.load_from_img_archive(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open IMG: {str(e)}")

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

    # --- Texture load (augment to store QImage) ---
    """
    def _load_txd_textures(self, txd_data, txd_name):
        # Keep original parsing then create QImage if rgba_data exists
        try:
            # call previous implementation (we'll reuse parsing code from earlier file)
            # For brevity, use the existing load method previously defined in your file (assumed)
            # If you have multiple definitions, ensure this one is used.
            import_io = globals()
        except Exception as e:
            self._log(f"Error loading TXD textures: {e}")

        # For compatibility we will call the older method if present in the module
        try:
            # Attempt to locate the old implementation function in globals
            loader = getattr(self, '_original_load_txd_textures', None)
            if loader is None:
                # fallback: reuse earlier implemented parsing in this file if present
                loader = getattr(self, '_load_txd_textures_old', None)

            if loader:
                loader(txd_data, txd_name)
                # After loader runs, convert rgba_data -> qimage
                for tex in self.texture_list:
                    if tex.get('rgba_data') and tex.get('width') and tex.get('height'):
                        qimg = self._rgba_bytes_to_qimage(tex['rgba_data'], tex['width'], tex['height'])
                        tex['qimage'] = qimg
                self._log(f"Loaded textures and prepared QImage objects from {txd_name}")
                self.save_txd_btn.setEnabled(True)
                self.import_btn.setEnabled(True)
                self.export_all_btn.setEnabled(True)
                return
        except Exception as e:
            self._log(f"Error during texture post-processing: {e}")

        QMessageBox.critical(self, "Error", "Failed to parse TXD textures properly")
        """

    def _load_txd_textures(self, txd_data, txd_name): #vers 8
        """Load textures from TXD data with DXT decompression"""
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

            # Populate table with thumbnails
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

                details = f"Name: {tex['name']}\n"
                if tex['width'] > 0:
                    details += f"Size: {tex['width']}x{tex['height']}\n"
                details += f"Format: {tex['format']}\nAlpha: {'Yes' if tex['has_alpha'] else 'No'}"

                self.texture_table.setItem(row, 0, thumb_item)
                self.texture_table.setItem(row, 1, QTableWidgetItem(details))

            for row in range(self.texture_table.rowCount()):
                self.texture_table.setRowHeight(row, 80)
            self.texture_table.setColumnWidth(0, 80)

            self.save_txd_btn.setEnabled(True)
            self.import_btn.setEnabled(True)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Loaded {len(textures)} textures from {txd_name}")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Error: {str(e)}")

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
                        status = "J" if tex['rgba_data'] else "X"
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

    def _create_toolbar(self): #vers 2
        """Create toolbar with action buttons"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setMaximumHeight(50)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(5, 5, 5, 5)

        self.open_img_btn = QPushButton("Open IMG")
        self.open_img_btn.clicked.connect(self.open_img_archive)
        layout.addWidget(self.open_img_btn)

        self.open_txd_btn = QPushButton("Open")
        self.open_txd_btn.clicked.connect(self.open_txd_file)
        layout.addWidget(self.open_txd_btn)

        self.save_txd_btn = QPushButton("Save")
        self.save_txd_btn.clicked.connect(self.save_txd_file)
        self.save_txd_btn.setEnabled(False)
        layout.addWidget(self.save_txd_btn)

        self.import_btn = QPushButton("Import")
        self.import_btn.clicked.connect(self.import_texture)
        self.import_btn.setEnabled(False)
        layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_selected_texture)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        self.export_all_btn = QPushButton("Export All")
        self.export_all_btn.clicked.connect(self.export_all_textures)
        self.export_all_btn.setEnabled(False)
        layout.addWidget(self.export_all_btn)

        self.flip_btn = QPushButton("Flip!")
        self.flip_btn.clicked.connect(self.flip_texture)
        self.flip_btn.setEnabled(False)
        layout.addWidget(self.flip_btn)

        self.props_btn = QPushButton("Properties")
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

    # --- Context menu ---
    def _show_texture_context_menu(self, position):
        if not self.texture_table.selectedItems():
            return

        menu = QMenu(self)
        menu.addAction("Export Texture", self.export_selected_texture)
        menu.addAction("Export Alpha Channel", self._export_alpha_only)
        menu.addSeparator()
        menu.addAction("Import/Replace", self.import_texture)
        menu.addSeparator()
        menu.addAction("Compress", self._compress_texture)
        menu.addAction("Compress All", lambda: QMessageBox.information(self, "Compression", "Compress All: not implemented"))
        menu.addAction("Uncompress", self._uncompress_texture)
        menu.addSeparator()
        menu.addAction("View Alpha Channel", lambda: setattr(self, '_show_alpha', True) or self._update_texture_info(self.selected_texture))
        menu.addAction("View Normal", lambda: setattr(self, '_show_alpha', False) or self._update_texture_info(self.selected_texture))
        menu.addSeparator()
        menu.addAction("Properties", self.show_properties)
        menu.exec(self.texture_table.viewport().mapToGlobal(position))


    # --- Alpha export helper ---
    def _export_alpha_only(self):
        if not self.selected_texture:
            return

        name = self.selected_texture.get('name', 'texture')
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Alpha Channel", f"{name}_alpha.png",
                                                   "PNG Files (*.png)")
        if not file_path:
            return

        qimg = self.selected_texture.get('qimage')
        if qimg is None and self.selected_texture.get('rgba_data'):
            qimg = self._rgba_bytes_to_qimage(self.selected_texture['rgba_data'], self.selected_texture['width'], self.selected_texture['height'])

        if qimg is None or qimg.isNull():
            QMessageBox.critical(self, "Error", "No image to export")
            return

        # Create alpha grayscale image
        w = qimg.width()
        h = qimg.height()
        alpha_img = QImage(w, h, QImage.Format.Format_RGBA8888)
        src = qimg.convertToFormat(QImage.Format.Format_RGBA8888)
        for y in range(h):
            for x in range(w):
                px = src.pixelColor(x, y)
                a = px.alpha()
                alpha_img.setPixelColor(x, y, px.fromRgb(a, a, a, 255))

        if alpha_img.save(file_path):
            self._log(f"📤 Exported alpha to {file_path}")
            QMessageBox.information(self, "Export", "Alpha exported successfully")
        else:
            QMessageBox.critical(self, "Error", "Failed to save alpha image")


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
            self.main_window.log_message(f"👁️ Switched to {mode}")

    def _update_texture_info(self, texture): #vers 3
        """Update texture information display with preview and channel support"""
        try:
            name = texture.get('name', 'Unknown')
            width = texture.get('width', 0)
            height = texture.get('height', 0)
            has_alpha = texture.get('has_alpha', False)
            fmt = texture.get('format', 'Unknown')
            mipmaps = texture.get('mipmaps', 1)

            self.info_name.setText(f"Name: {name}")
            self.info_size.setText(f"Size: {width}x{height}" if width > 0 else "Size: Unknown")
            self.info_format.setText(f"Format: {fmt}")
            self.info_alpha.setText(f"Alpha: {'Yes' if has_alpha else 'No'}")

            comp = "Compressed DXT"
            if mipmaps > 1:
                comp += f" | Mipmaps: {mipmaps}"
            self.info_compression.setText(f"Compression: {comp}")

            # Show preview
            rgba_data = texture.get('rgba_data')
            if rgba_data and width > 0 and height > 0:
                # Check if we should show alpha channel
                if hasattr(self, '_show_alpha') and self._show_alpha:
                    # Extract alpha channel as grayscale
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

                    # Update button text
                    if hasattr(self, '_show_alpha') and self._show_alpha:
                        self.flip_btn.setText("🔄 Normal")
                    else:
                        self.flip_btn.setText("🔄 Alpha")
                    return

            self.preview_label.setText("Preview not available")
        except Exception as e:
            self.preview_label.setText(f"Preview error: {str(e)}")

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

    # --- Import / Export using QImage ---
    def import_texture(self):
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to replace")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Import Texture", "",
                                                   "Image Files (*.png *.jpg *.bmp *.tga *.dds);;All Files (*)")
        if not file_path:
            return

        qimg = QImage(file_path)
        if qimg.isNull():
            QMessageBox.critical(self, "Error", "Failed to load image")
            return

        qimg = qimg.convertToFormat(QImage.Format.Format_RGBA8888)
        self.selected_texture['qimage'] = qimg
        self.selected_texture['rgba_data'] = self._qimage_to_rgba_bytes(qimg)
        self.selected_texture['width'] = qimg.width()
        self.selected_texture['height'] = qimg.height()
        self._update_texture_info(self.selected_texture)
        self._log(f"Imported texture from {file_path}")


    def show_properties(self): #vers 1
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return
        tex = self.selected_texture
        QMessageBox.information(self, "Properties",
                                f"Name: {tex.get('name')}
Size: {tex.get('width')}x{tex.get('height')}
Format: {tex.get('format')}")


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

    def _resize_texture(self):
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        qimg = self.selected_texture.get('qimage')
        if qimg is None and self.selected_texture.get('rgba_data'):
            qimg = self._rgba_bytes_to_qimage(self.selected_texture['rgba_data'],
                                              self.selected_texture['width'],
                                              self.selected_texture['height'])
            self.selected_texture['qimage'] = qimg

        if qimg is None or qimg.isNull():
            QMessageBox.critical(self, "Error", "No image data to resize")
            return

        w, ok1 = QInputDialog.getInt(self, "Resize", "New width:", value=qimg.width(), min=1)
        if not ok1:
            return
        h, ok2 = QInputDialog.getInt(self, "Resize", "New height:", value=qimg.height(), min=1)
        if not ok2:
            return

        new_img = qimg.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        new_img = new_img.convertToFormat(QImage.Format.Format_RGBA8888)
        self.selected_texture['qimage'] = new_img
        self.selected_texture['rgba_data'] = self._qimage_to_rgba_bytes(new_img)
        self.selected_texture['width'] = w
        self.selected_texture['height'] = h
        self._update_texture_info(self.selected_texture)
        self._log(f"🔧 Resized texture to {w}x{h}")


    def _upscale_texture(self):
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        qimg = self.selected_texture.get('qimage')
        if qimg is None and self.selected_texture.get('rgba_data'):
            qimg = self._rgba_bytes_to_qimage(self.selected_texture['rgba_data'],
                                              self.selected_texture['width'],
                                              self.selected_texture['height'])
            self.selected_texture['qimage'] = qimg

        if qimg is None or qimg.isNull():
            QMessageBox.critical(self, "Error", "No image data to upscale")
            return

        factor, ok = QInputDialog.getInt(self, "AI Upscale", "Scale factor (integer, e.g. 2):", value=2, min=2, max=16)
        if not ok:
            return

        # Ask user if they want to try an external upscaler
        use_external = QMessageBox.question(self, "External upscaler",
                                            "Use external AI upscaler if available? (Otherwise fallback to high-quality resampling)",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        up_img = None
        if use_external == QMessageBox.StandardButton.Yes:
            # Ask for command path
            cmd_path, _ = QFileDialog.getOpenFileName(self, "Select upscaler executable (or Cancel)", "", "Executable Files (*)")
            if cmd_path:
                try:
                    up_qimg = _call_external_upscaler(qimg, factor, cmd_path)
                    if up_qimg is not None and not up_qimg.isNull():
                        up_img = up_qimg
                        self._log(f"🤖 External upscaler succeeded: {cmd_path}")
                    else:
                        self._log(f"🤖 External upscaler failed or produced no output: {cmd_path}")
                except Exception as e:
                    self._log(f"🤖 External upscaler error: {e}")

        if up_img is None:
            # Fallback to high-quality QImage scaling
            new_w = qimg.width() * factor
            new_h = qimg.height() * factor
            up_img = qimg.scaled(new_w, new_h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)

        up_img = up_img.convertToFormat(QImage.Format.Format_RGBA8888)
        new_w = up_img.width()
        new_h = up_img.height()
        self.selected_texture['qimage'] = up_img
        self.selected_texture['rgba_data'] = self._qimage_to_rgba_bytes(up_img)
        self.selected_texture['width'] = new_w
        self.selected_texture['height'] = new_h
        self._update_texture_info(self.selected_texture)
        self._log(f"🤖 Upscaled texture by {factor}x to {new_w}x{new_h}")


    # --- Selection updates ---
    def _on_texture_selected(self): #vars 1
        try:
            row = self.texture_table.currentRow()
            if row < 0 or row >= len(self.texture_list):
                return

            self.selected_texture = self.texture_list[row]
            self._update_texture_info(self.selected_texture)
            self.export_btn.setEnabled(True)
            self.edit_btn.setEnabled(True)
            self.convert_btn.setEnabled(True)
            self.import_btn.setEnabled(True)
        except Exception as e:
            self._log(f"❌ Selection error: {str(e)}")


    def _update_texture_info(self, texture): #vars 1
        try:
            name = texture.get('name', 'Unknown')
            width = texture.get('width', 0)
            height = texture.get('height', 0)
            has_alpha = texture.get('has_alpha', False)
            fmt = texture.get('format', 'Unknown')
            mipmaps = texture.get('mipmaps', 1)

            self.info_name.setText(f"Name: {name}")
            self.info_size.setText(f"Size: {width}x{height}" if width > 0 else "Size: Unknown")
            self.format_combo.setCurrentText(fmt if fmt else "ARGB8888")
            self.info_alpha_name.setText(f"Alpha: {texture.get('alpha_name', name + 'a') if has_alpha else 'None'}")
            self.info_alpha_name.setVisible(has_alpha)

            comp = "Compressed DXT" if 'DXT' in fmt else "Uncompressed"
            if mipmaps > 1:
                comp += f" | Mipmaps: {mipmaps}"
            self.info_compression.setText(f"Compression: {comp}")

            # Show preview
            qimg = texture.get('qimage')
            rgba_data = texture.get('rgba_data')
            if qimg is None and rgba_data and width > 0 and height > 0:
                qimg = self._rgba_bytes_to_qimage(rgba_data, width, height)
                texture['qimage'] = qimg

            if qimg and not qimg.isNull():
                pixmap = QPixmap.fromImage(qimg)
                label_size = self.preview_label.size()
                scaled_pixmap = pixmap.scaled(label_size.width()-20, label_size.height()-20,
                                              Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(scaled_pixmap)
                return

            self.preview_label.setText("Preview not available")
        except Exception as e:
            self.preview_label.setText(f"Preview error: {str(e)}")


    # --- TXD open helpers (standalone TXD or IMG) ---
    def open_txd_file(self, file_path=None): #var 2
        try:
            if not file_path:
                file_path, _ = QFileDialog.getOpenFileName(self, "Open TXD File", "", "TXD Files (*.txd);;All Files (*)")

            if file_path:
                with open(file_path, 'rb') as f:
                    txd_data = f.read()
                # We assume you have an existing parser in this module named _load_txd_textures_old
                # which will populate self.texture_list with dicts that include rgba_data/width/height
                if hasattr(self, '_load_txd_textures_old'):
                    self._load_txd_textures_old(txd_data, os.path.basename(file_path))
                    # Post-process into qimage objects
                    for tex in self.texture_list:
                        if tex.get('rgba_data') and tex.get('width') and tex.get('height'):
                            tex['qimage'] = self._rgba_bytes_to_qimage(tex['rgba_data'], tex['width'], tex['height'])
                    self._log(f"✅ Opened TXD {file_path}")
                    self.save_txd_btn.setEnabled(True)
                    self.import_btn.setEnabled(True)
                    self.export_all_btn.setEnabled(True)
                else:
                    QMessageBox.warning(self, "Parser Missing", "No TXD parser available in this module to read TXD files.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open TXD: {str(e)}")


    def save_txd_file(self):
        if not self.texture_list:
            QMessageBox.warning(self, "No TXD", "No textures available to save")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save TXD File", "", "TXD Files (*.txd);;All Files (*)")
        if not file_path:
            return

        try:
            with open(file_path, 'wb') as f:
                # We'll write a simple RenderWare chunked structure:
                # [Texture Dictionary Chunk] contains multiple [Texture Native] chunks
                # Each chunk: uint32 type, uint32 size, uint32 version, payload, (uint32 alignment padding)

                tw = bytearray()

                # Build inner data (texture natives)
                textures_data = bytearray()
                for tex in self.texture_list:
                    name = tex.get('name', 'unnamed')
                    qimg = tex.get('qimage')
                    if qimg is None and tex.get('rgba_data'):
                        qimg = self._rgba_bytes_to_qimage(tex['rgba_data'], tex['width'], tex['height'])

                    if qimg is None or qimg.isNull():
                        continue

                    w = qimg.width()
                    h = qimg.height()
                    rgba = self._qimage_to_rgba_bytes(qimg)

                    # Construct Texture Native chunk
                    tex_chunk = bytearray()

                    # Struct section: write a basic struct with header info and name
                    # We'll follow a simplified structure sufficient for many GTA tools
                    # Write platform ID (4), filter (1), addressing (1) + padding
                    platform_id = 9  # D3D9
                    filter_mode = 0
                    addressing = 0
                    tex_chunk.extend(struct.pack('<I2B', platform_id, filter_mode, addressing))
                    tex_chunk.extend(b'  ')

                    # Name (32 bytes)
                    name_bytes = name.encode('ascii', errors='ignore')[:31]
                    name_bytes += b' ' * (32 - len(name_bytes))
                    tex_chunk.extend(name_bytes)

                    # Mask name (32 bytes) - leave empty
                    tex_chunk.extend(b' ' * 32)

                    # raster_format_flags, d3d_format, width, height, depth, num_levels, raster_type
                    raster_format_flags = 0
                    d3d_format = 0  # we'll use 0 for ARGB
                    depth = 32
                    num_levels = 1
                    raster_type = 0
                    tex_chunk.extend(struct.pack('<IIHHBBB', raster_format_flags, d3d_format, w, h, depth, num_levels, raster_type))

                    # platform prop
                    platform_prop = 0
                    tex_chunk.extend(struct.pack('<B', platform_prop))

                    # Now write pixel data size + pixel data (ARGB32 expected by some RW parsers)
                    # Convert RGBA -> BGRA or ARGB ordering if needed. We'll write RGBA raw and set format accordingly.
                    pixels_len = len(rgba)
                    tex_chunk.extend(struct.pack('<I', pixels_len))
                    tex_chunk.extend(rgba)

                    # Wrap tex_chunk into a Texture Native parent (type 0x15)
                    parent_header = struct.pack('<III', RW_TEXTURE_NATIVE, len(tex_chunk), 0)
                    textures_data.extend(parent_header)
                    textures_data.extend(tex_chunk)

                    # Align to 4
                    if len(textures_data) % 4 != 0:
                        textures_data.extend(b' ' * (4 - (len(textures_data) % 4)))

                # Now wrap textures_data into a Texture Dictionary chunk
                dict_header = struct.pack('<III', RW_TEXTURE_DICTIONARY, len(textures_data), 0)
                tw.extend(dict_header)
                tw.extend(textures_data)

                f.write(tw)

            self._log(f"💾 Saved TXD to {file_path} (uncompressed ARGB textures)")
            QMessageBox.information(self, "Save TXD", "TXD saved (uncompressed ARGB). If you need DXT compression, use the compress tools later.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save TXD: {e}")


    # --- Compression stubs ---
    def _compress_texture(self):
        # Placeholder: real DXT compression is non-trivial. Keep stub for now.
        QMessageBox.information(self, "Compress", "DXT compression not implemented. Saved TXD uses uncompressed ARGB.")

    def _uncompress_texture(self):
        QMessageBox.information(self, "Uncompress", "Textures are handled in-memory as RGBA; uncompress is no-op for current implementation.")

    # --- Editor / Convert stubs ---
    def _edit_texture(self):
        QMessageBox.information(self, "Edit", "In-app editor not implemented; use Import to replace or export to edit externally.")

    def _convert_texture(self):
        QMessageBox.information(self, "Convert", "Use Export to save to desired format (PNG/BMP/JPG). IFF support requires additional parsers.")

    def closeEvent(self, event): #vers 1
        """Handle window close"""
        self.workshop_closed.emit()
        event.accept()


# --- DXT1 and DXT5 encoders (pure Python) ---

def _rgb_to_565(r, g, b):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def _565_to_rgb(c):
    r = ((c >> 11) & 0x1F) << 3
    g = ((c >> 5) & 0x3F) << 2
    b = (c & 0x1F) << 3
    return r, g, b


def _best_color_index(palette, r, g, b):
    best = 0
    best_dist = None
    for i, (pr, pg, pb) in enumerate(palette):
        dr = pr - r
        dg = pg - g
        db = pb - b
        dist = dr*dr + dg*dg + db*db
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best = i
    return best


def _encode_dxt1(rgba_bytes, width, height):
    """Encode raw RGBA bytes (RGBA8888) into DXT1 bytes.
    Simple block-wise encoder: select endpoints by luminance heuristic and assign indices.
    """
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    out = bytearray()

    for by in range(blocks_y):
        for bx in range(blocks_x):
            pixels = []
            for py in range(4):
                for px in range(4):
                    x = bx*4 + px
                    y = by*4 + py
                    if x < width and y < height:
                        idx = (y*width + x)*4
                        r = rgba_bytes[idx]
                        g = rgba_bytes[idx+1]
                        b = rgba_bytes[idx+2]
                    else:
                        r = g = b = 0
                    pixels.append((r,g,b))

            lum = [0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2] for p in pixels]
            max_i = lum.index(max(lum))
            min_i = lum.index(min(lum))
            c0_rgb = pixels[max_i]
            c1_rgb = pixels[min_i]

            c0_565 = _rgb_to_565(*c0_rgb)
            c1_565 = _rgb_to_565(*c1_rgb)

            pr0 = _565_to_rgb(c0_565)
            pr1 = _565_to_rgb(c1_565)
            palette = [pr0, pr1]
            if c0_565 > c1_565:
                palette.append(((2*pr0[0]+pr1[0])//3, (2*pr0[1]+pr1[1])//3, (2*pr0[2]+pr1[2])//3))
                palette.append(((pr0[0]+2*pr1[0])//3, (pr0[1]+2*pr1[1])//3, (pr0[2]+2*pr1[2])//3))
            else:
                palette.append(((pr0[0]+pr1[0])//2, (pr0[1]+pr1[1])//2, (pr0[2]+pr1[2])//2))
                palette.append((0,0,0))

            indices = 0
            bit_pos = 0
            for (r,g,b) in pixels:
                idx = _best_color_index(palette, r, g, b)
                indices |= (idx & 0x3) << bit_pos
                bit_pos += 2

            out.extend(struct.pack('<HHI', c0_565, c1_565, indices))

    return bytes(out)


def _encode_alpha_block(alpha_bytes):
    """Encode 4x4 alpha block for DXT5.
    alpha_bytes: list of 16 alpha values (0-255)
    Returns 8 bytes: a0, a1, and 48-bit index stream (little-endian packed 3 bits per pixel)
    """
    a0 = max(alpha_bytes)
    a1 = min(alpha_bytes)

    # Build alpha palette
    alpha_palette = [a0, a1]
    if a0 > a1:
        for i in range(1, 6):
            alpha_palette.append((( (6 - i) * a0 + i * a1 ) // 6))
    else:
        for i in range(1, 4):
            alpha_palette.append((( (4 - i) * a0 + i * a1 ) // 4))
        alpha_palette.extend([0, 255])

    # For each pixel, find best index (0..7)
    indices = 0
    bit_pos = 0
    for a in alpha_bytes:
        # find closest
        best_i = 0
        best_dist = None
        for i, av in enumerate(alpha_palette):
            dist = (av - a) * (av - a)
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_i = i
        indices |= (best_i & 0x7) << bit_pos
        bit_pos += 3

    # pack into 6 bytes little endian
    idx_bytes = indices.to_bytes(6, 'little')
    return bytes([a0, a1]) + idx_bytes


def _encode_dxt5(rgba_bytes, width, height):
    """Encode raw RGBA8888 bytes into DXT5 bytes.
    DXT5 block = 8 bytes alpha block + 8 bytes color block (same as DXT1 color block)
    """
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    out = bytearray()

    for by in range(blocks_y):
        for bx in range(blocks_x):
            alpha_vals = []
            pixels_rgb = []
            for py in range(4):
                for px in range(4):
                    x = bx*4 + px
                    y = by*4 + py
                    if x < width and y < height:
                        idx = (y*width + x)*4
                        r = rgba_bytes[idx]
                        g = rgba_bytes[idx+1]
                        b = rgba_bytes[idx+2]
                        a = rgba_bytes[idx+3]
                    else:
                        r = g = b = a = 0
                    pixels_rgb.append((r,g,b))
                    alpha_vals.append(a)

            # alpha block
            alpha_block = _encode_alpha_block(alpha_vals)

            # color block same as DXT1
            lum = [0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2] for p in pixels_rgb]
            max_i = lum.index(max(lum))
            min_i = lum.index(min(lum))
            c0_rgb = pixels_rgb[max_i]
            c1_rgb = pixels_rgb[min_i]
            c0_565 = _rgb_to_565(*c0_rgb)
            c1_565 = _rgb_to_565(*c1_rgb)
            pr0 = _565_to_rgb(c0_565)
            pr1 = _565_to_rgb(c1_565)
            palette = [pr0, pr1]
            if c0_565 > c1_565:
                palette.append(((2*pr0[0]+pr1[0])//3, (2*pr0[1]+pr1[1])//3, (2*pr0[2]+pr1[2])//3))
                palette.append(((pr0[0]+2*pr1[0])//3, (pr0[1]+2*pr1[1])//3, (pr0[2]+2*pr1[2])//3))
            else:
                palette.append(((pr0[0]+pr1[0])//2, (pr0[1]+pr1[1])//2, (pr0[2]+pr1[2])//2))
                palette.append((0,0,0))

            indices = 0
            bit_pos = 0
            for (r,g,b) in pixels_rgb:
                idx = _best_color_index(palette, r, g, b)
                indices |= (idx & 0x3) << bit_pos
                bit_pos += 2

            color_bytes = struct.pack('<HHI', c0_565, c1_565, indices)

            out.extend(alpha_block)
            out.extend(color_bytes)

    return bytes(out)


# --- External AI upscaler integration helper ---
import subprocess
import tempfile
import shutil
import sys


def _call_external_upscaler(qimage: QImage, factor: int, command: Optional[str] = None) -> Optional[QImage]:
    """Call an external upscaler executable. The executable is expected to accept input and output file paths.
    This helper writes the qimage to a temporary PNG, calls the command with arguments
    (we'll try common patterns), and reads back the result. If command is None, returns None.
    """❌ Error opening TXD Workshop: source code string cannot contain null bytes
    if not command:
        return None

    tmp_dir = tempfile.mkdtemp(prefix='txd_up_')
    in_path = os.path.join(tmp_dir, 'in.png')
    out_path = os.path.join(tmp_dir, 'out.png')
    try:
        qimage.save(in_path)

        patterns = [
            [command, '-i', in_path, '-o', out_path, '-s', str(factor)],
            [command, in_path, out_path],
            [command, in_path, out_path, str(factor)],
            [command, '--input', in_path, '--output', out_path, '--scale', str(factor)],
        ]

        for cmd in patterns:
            try:❌ Error opening TXD Workshop: source code string cannot contain null bytes
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if os.path.exists(out_path):
                    q2 = QImage(out_path)
                    if not q2.isNull():
                        return q2.convertToFormat(QImage.Format.Format_RGBA8888)
            except Exception:
                continue

        return None
    finally:
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass


# Expose an open function

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


