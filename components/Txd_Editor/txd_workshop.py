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
    QHeaderView, QAbstractItemView
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

class TXDWorkshop(QWidget): #vers 3
    """TXD Workshop - Main texture editing window"""

    workshop_closed = pyqtSignal()

    def __init__(self, parent=None, main_window=None): #vers 3
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

    def _create_toolbar(self): #vers 1
        """Create toolbar with action buttons"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setMaximumHeight(50)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(5, 5, 5, 5)

        self.open_img_btn = QPushButton("📂 Open IMG")
        self.open_img_btn.clicked.connect(self.open_img_archive)
        layout.addWidget(self.open_img_btn)

        self.action_btn = QPushButton("⚙️ Action")
        self.action_btn.setEnabled(False)
        layout.addWidget(self.action_btn)

        self.open_txd_btn = QPushButton("📁 Open TXD")
        self.open_txd_btn.clicked.connect(self.open_txd_file)
        layout.addWidget(self.open_txd_btn)

        self.save_txd_btn = QPushButton("💾 Save TXD")
        self.save_txd_btn.clicked.connect(self.save_txd_file)
        self.save_txd_btn.setEnabled(False)
        layout.addWidget(self.save_txd_btn)

        self.import_btn = QPushButton("📥 Import")
        self.import_btn.setEnabled(False)
        layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_selected_texture)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        self.flip_btn = QPushButton("🔄 Flip!")
        self.flip_btn.setEnabled(False)
        layout.addWidget(self.flip_btn)

        self.props_btn = QPushButton("📋 Properties")
        self.props_btn.setEnabled(False)
        layout.addWidget(self.props_btn)

        layout.addStretch()
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

    def _create_middle_panel(self): #vers 2
        """Create middle panel - Texture list"""
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
        layout.addWidget(self.texture_table)

        return panel

    def _create_right_panel(self): #vers 1
        """Create right panel - Large texture preview"""
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

        self.info_name = QLabel("Name: -")
        self.info_size = QLabel("Size: -")
        self.info_format = QLabel("Format: -")
        self.info_alpha = QLabel("Alpha: -")
        self.info_compression = QLabel("Compression: -")

        info_layout.addWidget(self.info_name)
        info_layout.addWidget(self.info_size)
        info_layout.addWidget(self.info_format)
        info_layout.addWidget(self.info_alpha)
        info_layout.addWidget(self.info_compression)

        layout.addWidget(info_group)
        return panel

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
                self.main_window.log_message(f"✅ Loaded {len(textures)} textures from {txd_name}")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error: {str(e)}")

    def _parse_single_texture(self, txd_data, offset, index): #vers 2
        """Parse single texture with full format detection and DXT decompression"""
        import struct

        tex = {'name': f'texture_{index}', 'width': 0, 'height': 0, 'has_alpha': False, 'format': 'Unknown', 'mipmaps': 1, 'rgba_data': None, 'dxt_data': None, 'compression': 0}

        scan_start = offset + 12
        scan_end = min(scan_start + 200, len(txd_data) - 4)

        # Detect format
        for p in range(scan_start, scan_start + 50, 4):
            try:
                if p + 4 < len(txd_data):
                    platform_id = struct.unpack('<I', txd_data[p:p+4])[0]
                    if platform_id in [8, 9]:
                        if p + 12 < len(txd_data):
                            compression = struct.unpack('<I', txd_data[p+8:p+12])[0]
                            tex['compression'] = compression
                            if compression == 0x31545844: tex['format'] = 'DXT1'
                            elif compression == 0x33545844: tex['format'] = 'DXT3'; tex['has_alpha'] = True
                            elif compression == 0x35545844: tex['format'] = 'DXT5'; tex['has_alpha'] = True
                            elif compression == 0x15: tex['format'] = 'ARGB1555'; tex['has_alpha'] = True
                            elif compression == 0x16: tex['format'] = 'RGB565'
                            elif compression == 0x19: tex['format'] = 'ARGB4444'; tex['has_alpha'] = True
                            elif compression == 0x1A: tex['format'] = 'LUM8'
                        break
            except:
                pass

        # Get dimensions
        for p in range(scan_start, scan_end, 2):
            try:
                w, h = struct.unpack('<HH', txd_data[p:p+4])
                if w in [4,8,16,32,64,128,256,512,1024,2048,4096] and h in [4,8,16,32,64,128,256,512,1024,2048,4096]:
                    tex['width'] = w
                    tex['height'] = h
                    break
            except:
                pass

        # Get name
        for np in range(offset + 40, min(offset + 150, len(txd_data) - 12), 4):
            try:
                if struct.unpack('<I', txd_data[np:np+4])[0] == 0x02:
                    ns = struct.unpack('<I', txd_data[np+4:np+8])[0]
                    if 0 < ns < 64:
                        name = txd_data[np+12:np+12+ns].rstrip(b'\x00').decode('ascii', errors='ignore')
                        if name.isprintable():
                            tex['name'] = name
                        break
            except:
                pass

        # Decompress texture data
        if tex['width'] > 0 and tex['height'] > 0:
            raster_search = offset + 100
            for rp in range(raster_search, min(raster_search + 300, len(txd_data) - 12), 4):
                try:
                    rtype = struct.unpack('<I', txd_data[rp:rp+4])[0]
                    if rtype == 0x1E:
                        rsize = struct.unpack('<I', txd_data[rp+4:rp+8])[0]
                        raster_data_start = rp + 12

                        if 'DXT1' in tex['format']:
                            expected_size = ((tex['width'] + 3) // 4) * ((tex['height'] + 3) // 4) * 8
                        elif 'DXT3' in tex['format'] or 'DXT5' in tex['format']:
                            expected_size = ((tex['width'] + 3) // 4) * ((tex['height'] + 3) // 4) * 16
                        else:
                            expected_size = tex['width'] * tex['height'] * 4

                        dxt_offset = raster_data_start + 20
                        if dxt_offset + expected_size <= len(txd_data):
                            tex['dxt_data'] = txd_data[dxt_offset:dxt_offset + expected_size]

                            if 'DXT1' in tex['format']:
                                tex['rgba_data'] = self._decompress_dxt1(tex['dxt_data'], tex['width'], tex['height'])
                            elif 'DXT3' in tex['format']:
                                tex['rgba_data'] = self._decompress_dxt3(tex['dxt_data'], tex['width'], tex['height'])
                            elif 'DXT5' in tex['format']:
                                tex['rgba_data'] = self._decompress_dxt5(tex['dxt_data'], tex['width'], tex['height'])
                            elif 'ARGB' in tex['format'] or 'RGB' in tex['format']:
                                tex['rgba_data'] = self._decompress_uncompressed(tex['dxt_data'], tex['width'], tex['height'], tex['format'])
                        break
                except:
                    pass

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
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Selection error: {str(e)}")

    def _update_texture_info(self, texture): #vers 2
        """Update texture information display with preview"""
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

            # Show preview if we have RGBA data
            rgba_data = texture.get('rgba_data')
            if rgba_data and width > 0 and height > 0:
                image = QImage(rgba_data, width, height, width*4, QImage.Format.Format_RGBA8888)
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    label_size = self.preview_label.size()
                    scaled_pixmap = pixmap.scaled(label_size.width()-20, label_size.height()-20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.preview_label.setPixmap(scaled_pixmap)
                    return

            self.preview_label.setText("Preview not available")
        except Exception as e:
            self.preview_label.setText(f"Preview error: {str(e)}")

    def open_txd_file(self): #vers 1
        """Open standalone TXD file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open TXD File", "", "TXD Files (*.txd);;All Files (*)")
            if file_path:
                with open(file_path, 'rb') as f:
                    txd_data = f.read()
                self._load_txd_textures(txd_data, os.path.basename(file_path))
                self.setWindowTitle(f"TXD Workshop: {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open TXD: {str(e)}")

    def save_txd_file(self): #vers 1
        """Save current TXD file"""
        QMessageBox.information(self, "Save TXD", "Save functionality coming soon!")

    def export_selected_texture(self): #vers 1
        """Export selected texture"""
        QMessageBox.information(self, "Export", "Export functionality coming soon!")

    def closeEvent(self, event): #vers 1
        """Handle window close"""
        self.workshop_closed.emit()
        event.accept()


def open_txd_workshop(main_window, img_path=None): #vers 1
    """Open TXD Workshop from main window"""
    try:
        workshop = TXDWorkshop(main_window, main_window)

        if img_path:
            workshop.load_from_img_archive(img_path)
        elif main_window and hasattr(main_window, 'current_img') and main_window.current_img:
            workshop.load_from_img_archive(main_window.current_img.file_path)

        workshop.show()
        return workshop
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to open TXD Workshop: {str(e)}")
        return None
