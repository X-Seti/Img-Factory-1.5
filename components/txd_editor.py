#this belongs in components/ txd_editor.py - Version: 1
# X-Seti - August26 2025 - IMG Factory 1.5 -
#!/usr/bin/env python3
"""
TXD Texture Editor for GTA San Andreas, Liberty City and Vice City
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps
import struct
import os
import io
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum

VERSION = "1.0.0"

class RasterFormat(IntEnum):
    """RenderWare raster format constants"""
    DEFAULT = 0x0000
    C1555 = 0x0100    # 16-bit 1555
    C565 = 0x0200     # 16-bit 565
    C4444 = 0x0300    # 16-bit 4444
    LUM8 = 0x0400     # 8-bit luminance
    C8888 = 0x0500    # 32-bit 8888
    C888 = 0x0600     # 24-bit 888
    D16 = 0x0700      # 16-bit depth
    D24 = 0x0800      # 24-bit depth
    D32 = 0x0900      # 32-bit depth
    C555 = 0x0A00     # 16-bit 555
    AUTOMIPMAP = 0x1000
    PAL8 = 0x2000     # 8-bit palettized
    PAL4 = 0x4000     # 4-bit palettized
    MIPMAP = 0x8000

@dataclass
class MipLevel:
    """Represents a mipmap level"""
    width: int
    height: int
    data: bytes
    size: int

@dataclass
class TextureInfo:
    """Texture information structure"""
    name: str
    mask_name: str
    format: int
    width: int
    height: int
    depth: int
    mipmap_count: int
    raster_type: int
    compression: int
    has_alpha: bool
    mip_levels: List[MipLevel]
    palette: Optional[bytes] = None

class TXDFile:
    """TXD file handler for GTA SA/VC"""

    def __init__(self):
        self.textures: List[TextureInfo] = []
        self.version = 0x1803FFFF  # GTA SA version
        self.filename = ""

    def load(self, filename: str) -> bool:
        """Load TXD file"""
        try:
            with open(filename, 'rb') as f:
                self.filename = filename
                self.textures.clear()

                # Read TXD header
                chunk_type = struct.unpack('<I', f.read(4))[0]
                if chunk_type != 0x16:  # RW_TEXDICTIONARY
                    raise ValueError("Not a valid TXD file")

                chunk_size = struct.unpack('<I', f.read(4))[0]
                self.version = struct.unpack('<I', f.read(4))[0]

                # Read texture count
                info_chunk = struct.unpack('<I', f.read(4))[0]
                if info_chunk != 0x01:  # RW_STRUCT
                    raise ValueError("Invalid TXD structure")

                info_size = struct.unpack('<I', f.read(4))[0]
                info_version = struct.unpack('<I', f.read(4))[0]

                texture_count = struct.unpack('<H', f.read(2))[0]
                device_id = struct.unpack('<H', f.read(2))[0]

                # Read textures
                for i in range(texture_count):
                    texture = self._read_texture(f)
                    if texture:
                        self.textures.append(texture)

                return True

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load TXD: {e}")
            return False

    def _read_texture(self, f) -> Optional[TextureInfo]:
        """Read a single texture from TXD"""
        try:
            # Read texture chunk header
            chunk_type = struct.unpack('<I', f.read(4))[0]
            if chunk_type != 0x15:  # RW_TEXTURENATIVE
                return None

            chunk_size = struct.unpack('<I', f.read(4))[0]
            version = struct.unpack('<I', f.read(4))[0]

            chunk_start = f.tell()

            # Read struct chunk
            struct_type = struct.unpack('<I', f.read(4))[0]
            struct_size = struct.unpack('<I', f.read(4))[0]
            struct_version = struct.unpack('<I', f.read(4))[0]

            # Read texture info
            platform = struct.unpack('<I', f.read(4))[0]
            filter_flags = struct.unpack('<I', f.read(4))[0]

            # Read texture name (32 bytes)
            name_data = f.read(32)
            name = name_data.rstrip(b'\x00').decode('ascii', errors='ignore')

            # Read mask name (32 bytes)
            mask_data = f.read(32)
            mask_name = mask_data.rstrip(b'\x00').decode('ascii', errors='ignore')

            # Read raster format info
            raster_format = struct.unpack('<I', f.read(4))[0]
            has_alpha = struct.unpack('<I', f.read(4))[0]
            width = struct.unpack('<H', f.read(2))[0]
            height = struct.unpack('<H', f.read(2))[0]
            depth = struct.unpack('<B', f.read(1))[0]
            mipmap_count = struct.unpack('<B', f.read(1))[0]
            raster_type = struct.unpack('<B', f.read(1))[0]
            compression = struct.unpack('<B', f.read(1))[0]

            # Create texture info
            texture = TextureInfo(
                name=name,
                mask_name=mask_name,
                format=raster_format,
                width=width,
                height=height,
                depth=depth,
                mipmap_count=mipmap_count,
                raster_type=raster_type,
                compression=compression,
                has_alpha=bool(has_alpha),
                mip_levels=[]
            )

            # Read palette if present
            if raster_format & RasterFormat.PAL8 or raster_format & RasterFormat.PAL4:
                palette_size = struct.unpack('<I', f.read(4))[0]
                texture.palette = f.read(palette_size)

            # Read mipmap levels
            for level in range(mipmap_count):
                mip_size = struct.unpack('<I', f.read(4))[0]
                mip_data = f.read(mip_size)

                mip_width = width >> level
                mip_height = height >> level
                if mip_width < 1: mip_width = 1
                if mip_height < 1: mip_height = 1

                mip_level = MipLevel(
                    width=mip_width,
                    height=mip_height,
                    data=mip_data,
                    size=mip_size
                )
                texture.mip_levels.append(mip_level)

            return texture

        except Exception as e:
            print(f"Error reading texture: {e}")
            return None

    def save(self, filename: str) -> bool:
        """Save TXD file"""
        try:
            with open(filename, 'wb') as f:
                # Calculate total size
                total_size = self._calculate_txd_size()

                # Write TXD header
                f.write(struct.pack('<I', 0x16))  # RW_TEXDICTIONARY
                f.write(struct.pack('<I', total_size))
                f.write(struct.pack('<I', self.version))

                # Write info chunk
                f.write(struct.pack('<I', 0x01))  # RW_STRUCT
                f.write(struct.pack('<I', 4))     # Size
                f.write(struct.pack('<I', self.version))
                f.write(struct.pack('<H', len(self.textures)))
                f.write(struct.pack('<H', 0x0325))  # Device ID

                # Write textures
                for texture in self.textures:
                    self._write_texture(f, texture)

                return True

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save TXD: {e}")
            return False

    def _write_texture(self, f, texture: TextureInfo):
        """Write a single texture to TXD"""
        # Calculate texture size
        texture_size = self._calculate_texture_size(texture)

        # Write texture header
        f.write(struct.pack('<I', 0x15))  # RW_TEXTURENATIVE
        f.write(struct.pack('<I', texture_size))
        f.write(struct.pack('<I', self.version))

        # Write struct header
        struct_size = 88  # Base struct size
        if texture.palette:
            struct_size += 4 + len(texture.palette)

        f.write(struct.pack('<I', 0x01))  # RW_STRUCT
        f.write(struct.pack('<I', struct_size))
        f.write(struct.pack('<I', self.version))

        # Write texture data
        f.write(struct.pack('<I', 0x0325))  # Platform
        f.write(struct.pack('<I', 0x1106))  # Filter flags

        # Write names (32 bytes each)
        name_bytes = texture.name.encode('ascii')[:31] + b'\x00'
        f.write(name_bytes.ljust(32, b'\x00'))

        mask_bytes = texture.mask_name.encode('ascii')[:31] + b'\x00'
        f.write(mask_bytes.ljust(32, b'\x00'))

        # Write format info
        f.write(struct.pack('<I', texture.format))
        f.write(struct.pack('<I', 1 if texture.has_alpha else 0))
        f.write(struct.pack('<H', texture.width))
        f.write(struct.pack('<H', texture.height))
        f.write(struct.pack('<B', texture.depth))
        f.write(struct.pack('<B', texture.mipmap_count))
        f.write(struct.pack('<B', texture.raster_type))
        f.write(struct.pack('<B', texture.compression))

        # Write palette if present
        if texture.palette:
            f.write(struct.pack('<I', len(texture.palette)))
            f.write(texture.palette)

        # Write mipmap data
        for mip_level in texture.mip_levels:
            f.write(struct.pack('<I', mip_level.size))
            f.write(mip_level.data)

    def _calculate_txd_size(self) -> int:
        """Calculate total TXD file size"""
        size = 12  # Info chunk size
        for texture in self.textures:
            size += self._calculate_texture_size(texture)
        return size

    def _calculate_texture_size(self, texture: TextureInfo) -> int:
        """Calculate single texture size"""
        size = 12 + 88  # Headers + struct
        if texture.palette:
            size += 4 + len(texture.palette)
        for mip_level in texture.mip_levels:
            size += 4 + mip_level.size
        return size

class ImageConverter:
    """Handles conversion between TXD formats and PIL Images"""

    @staticmethod
    def txd_to_pil(texture: TextureInfo, mip_level: int = 0) -> Optional[Image.Image]:
        """Convert TXD texture data to PIL Image"""
        if mip_level >= len(texture.mip_levels):
            return None

        mip = texture.mip_levels[mip_level]
        width, height = mip.width, mip.height
        data = mip.data

        try:
            if texture.compression == 1:  # DXT1
                return ImageConverter._decode_dxt1(data, width, height)
            elif texture.compression == 3:  # DXT3
                return ImageConverter._decode_dxt3(data, width, height)
            elif texture.compression == 5:  # DXT5
                return ImageConverter._decode_dxt5(data, width, height)
            elif texture.format & RasterFormat.C8888:
                return ImageConverter._decode_rgba8888(data, width, height)
            elif texture.format & RasterFormat.C888:
                return ImageConverter._decode_rgb888(data, width, height)
            elif texture.format & RasterFormat.C565:
                return ImageConverter._decode_rgb565(data, width, height)
            elif texture.format & RasterFormat.C1555:
                return ImageConverter._decode_rgba1555(data, width, height)
            elif texture.format & RasterFormat.PAL8:
                return ImageConverter._decode_pal8(data, width, height, texture.palette)
            else:
                # Try as RGBA8888 by default
                return ImageConverter._decode_rgba8888(data, width, height)

        except Exception as e:
            print(f"Error converting texture {texture.name}: {e}")
            return None

    @staticmethod
    def pil_to_txd(image: Image.Image, texture: TextureInfo, mip_level: int = 0) -> bool:
        """Convert PIL Image to TXD texture data"""
        if mip_level >= len(texture.mip_levels):
            return False

        mip = texture.mip_levels[mip_level]

        # Resize image to match mip level
        if image.size != (mip.width, mip.height):
            image = image.resize((mip.width, mip.height), Image.Resampling.LANCZOS)

        try:
            if texture.compression == 1:  # DXT1
                data = ImageConverter._encode_dxt1(image)
            elif texture.compression == 3:  # DXT3
                data = ImageConverter._encode_dxt3(image)
            elif texture.compression == 5:  # DXT5
                data = ImageConverter._encode_dxt5(image)
            elif texture.format & RasterFormat.C8888:
                data = ImageConverter._encode_rgba8888(image)
            elif texture.format & RasterFormat.C888:
                data = ImageConverter._encode_rgb888(image)
            elif texture.format & RasterFormat.C565:
                data = ImageConverter._encode_rgb565(image)
            elif texture.format & RasterFormat.C1555:
                data = ImageConverter._encode_rgba1555(image)
            else:
                data = ImageConverter._encode_rgba8888(image)

            # Update mip level
            mip.data = data
            mip.size = len(data)
            return True

        except Exception as e:
            print(f"Error encoding texture: {e}")
            return False

    @staticmethod
    def _decode_rgba8888(data: bytes, width: int, height: int) -> Image.Image:
        """Decode RGBA8888 format"""
        if len(data) < width * height * 4:
            # Pad with zeros if data is too short
            data += b'\x00' * (width * height * 4 - len(data))

        # Convert BGRA to RGBA
        pixels = []
        for i in range(0, len(data), 4):
            if i + 3 < len(data):
                b, g, r, a = data[i:i+4]
                pixels.extend([r, g, b, a])
            else:
                pixels.extend([0, 0, 0, 255])

        img = Image.new('RGBA', (width, height))
        img.putdata([tuple(pixels[i:i+4]) for i in range(0, len(pixels), 4)])
        return img

    @staticmethod
    def _encode_rgba8888(image: Image.Image) -> bytes:
        """Encode to RGBA8888 format"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        data = bytearray()
        for pixel in image.getdata():
            r, g, b, a = pixel
            data.extend([b, g, r, a])  # Convert RGBA to BGRA

        return bytes(data)

    @staticmethod
    def _decode_rgb888(data: bytes, width: int, height: int) -> Image.Image:
        """Decode RGB888 format"""
        if len(data) < width * height * 3:
            data += b'\x00' * (width * height * 3 - len(data))

        pixels = []
        for i in range(0, len(data), 3):
            if i + 2 < len(data):
                b, g, r = data[i:i+3]
                pixels.append((r, g, b))
            else:
                pixels.append((0, 0, 0))

        img = Image.new('RGB', (width, height))
        img.putdata(pixels)
        return img

    @staticmethod
    def _encode_rgb888(image: Image.Image) -> bytes:
        """Encode to RGB888 format"""
        if image.mode != 'RGB':
            image = image.convert('RGB')

        data = bytearray()
        for pixel in image.getdata():
            r, g, b = pixel
            data.extend([b, g, r])  # Convert RGB to BGR

        return bytes(data)

    @staticmethod
    def _decode_rgb565(data: bytes, width: int, height: int) -> Image.Image:
        """Decode RGB565 format"""
        pixels = []
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                val = struct.unpack('<H', data[i:i+2])[0]
                r = ((val >> 11) & 0x1F) << 3
                g = ((val >> 5) & 0x3F) << 2
                b = (val & 0x1F) << 3
                pixels.append((r, g, b))
            else:
                pixels.append((0, 0, 0))

        img = Image.new('RGB', (width, height))
        img.putdata(pixels)
        return img

    @staticmethod
    def _encode_rgb565(image: Image.Image) -> bytes:
        """Encode to RGB565 format"""
        if image.mode != 'RGB':
            image = image.convert('RGB')

        data = bytearray()
        for pixel in image.getdata():
            r, g, b = pixel
            r565 = (r >> 3) & 0x1F
            g565 = (g >> 2) & 0x3F
            b565 = (b >> 3) & 0x1F
            val = (r565 << 11) | (g565 << 5) | b565
            data.extend(struct.pack('<H', val))

        return bytes(data)

    @staticmethod
    def _decode_rgba1555(data: bytes, width: int, height: int) -> Image.Image:
        """Decode RGBA1555 format"""
        pixels = []
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                val = struct.unpack('<H', data[i:i+2])[0]
                a = 255 if (val >> 15) & 1 else 0
                r = ((val >> 10) & 0x1F) << 3
                g = ((val >> 5) & 0x1F) << 3
                b = (val & 0x1F) << 3
                pixels.append((r, g, b, a))
            else:
                pixels.append((0, 0, 0, 255))

        img = Image.new('RGBA', (width, height))
        img.putdata(pixels)
        return img

    @staticmethod
    def _encode_rgba1555(image: Image.Image) -> bytes:
        """Encode to RGBA1555 format"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        data = bytearray()
        for pixel in image.getdata():
            r, g, b, a = pixel
            a1 = 1 if a > 127 else 0
            r5 = (r >> 3) & 0x1F
            g5 = (g >> 3) & 0x1F
            b5 = (b >> 3) & 0x1F
            val = (a1 << 15) | (r5 << 10) | (g5 << 5) | b5
            data.extend(struct.pack('<H', val))

        return bytes(data)

    @staticmethod
    def _decode_pal8(data: bytes, width: int, height: int, palette: bytes) -> Image.Image:
        """Decode 8-bit palettized format"""
        if not palette or len(palette) < 1024:  # 256 * 4 bytes
            # Create grayscale palette
            palette_data = []
            for i in range(256):
                palette_data.extend([i, i, i, 255])
        else:
            palette_data = list(palette[:1024])

        # Create palette image
        img = Image.new('P', (width, height))

        # Set palette (PIL expects RGB format)
        pal = []
        for i in range(0, len(palette_data), 4):
            if i + 2 < len(palette_data):
                b, g, r = palette_data[i:i+3]
                pal.extend([r, g, b])
            else:
                pal.extend([0, 0, 0])

        img.putpalette(pal)

        # Set pixel data
        pixel_data = list(data[:width * height])
        if len(pixel_data) < width * height:
            pixel_data.extend([0] * (width * height - len(pixel_data)))

        img.putdata(pixel_data)
        return img.convert('RGBA')

    # Simplified DXT decoders (basic implementation)
    @staticmethod
    def _decode_dxt1(data: bytes, width: int, height: int) -> Image.Image:
        """Basic DXT1 decoder"""
        # This is a simplified implementation
        # For production use, consider using a proper DXT library
        img = Image.new('RGBA', (width, height), (255, 0, 255, 255))
        return img

    @staticmethod
    def _decode_dxt3(data: bytes, width: int, height: int) -> Image.Image:
        """Basic DXT3 decoder"""
        img = Image.new('RGBA', (width, height), (255, 0, 255, 255))
        return img

    @staticmethod
    def _decode_dxt5(data: bytes, width: int, height: int) -> Image.Image:
        """Basic DXT5 decoder"""
        img = Image.new('RGBA', (width, height), (255, 0, 255, 255))
        return img

    @staticmethod
    def _encode_dxt1(image: Image.Image) -> bytes:
        """Basic DXT1 encoder"""
        # Simplified - just convert to RGB565 blocks
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return ImageConverter._encode_rgb565(image)

    @staticmethod
    def _encode_dxt3(image: Image.Image) -> bytes:
        """Basic DXT3 encoder"""
        return ImageConverter._encode_rgba8888(image)

    @staticmethod
    def _encode_dxt5(image: Image.Image) -> bytes:
        """Basic DXT5 encoder"""
        return ImageConverter._encode_rgba8888(image)

class TXDEditor:
    """Main TXD Editor application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"TXD Texture Editor v{VERSION}")
        self.root.geometry("1200x800")

        self.txd_file = TXDFile()
        self.current_texture = None
        self.current_mip_level = 0
        self.current_image = None
        self.display_mode = "normal"  # "normal", "alpha", "both"

        self.setup_ui()
        self.setup_menu()

    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open TXD...", command=self.open_txd, accelerator="Ctrl+O")
        file_menu.add_command(label="Save TXD", command=self.save_txd, accelerator="Ctrl+S")
        file_menu.add_command(label="Save TXD As...", command=self.save_txd_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Replace Texture...", command=self.replace_texture)
        edit_menu.add_command(label="Export Texture...", command=self.export_texture)
        edit_menu.add_command(label="Add Texture...", command=self.add_texture)
        edit_menu.add_command(label="Remove Texture", command=self.remove_texture)
        edit_menu.add_separator()
        edit_menu.add_command(label="Generate Mipmaps", command=self.generate_mipmaps)
        edit_menu.add_command(label="Change Bit Depth...", command=self.change_bit_depth)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Normal", command=lambda: self.set_display_mode("normal"))
        view_menu.add_command(label="Alpha Channel", command=lambda: self.set_display_mode("alpha"))
        view_menu.add_command(label="Both", command=lambda: self.set_display_mode("both"))

        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_txd())
        self.root.bind('<Control-s>', lambda e: self.save_txd())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_txd_as())

    def setup_ui(self):
        """Setup user interface"""
        # Main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - texture list and properties
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Texture list
        list_frame = ttk.LabelFrame(left_frame, text="Textures")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Texture listbox with scrollbar
        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.texture_listbox = tk.Listbox(list_scroll_frame)
        texture_scrollbar = ttk.Scrollbar(list_scroll_frame, orient=tk.VERTICAL, command=self.texture_listbox.yview)
        self.texture_listbox.config(yscrollcommand=texture_scrollbar.set)

        self.texture_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        texture_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.texture_listbox.bind('<<ListboxSelect>>', self.on_texture_select)

        # Properties frame
        props_frame = ttk.LabelFrame(left_frame, text="Properties")
        props_frame.pack(fill=tk.X, pady=(0, 5))

        # Properties grid
        props_grid = ttk.Frame(props_frame)
        props_grid.pack(fill=tk.X, padx=5, pady=5)

        # Property labels and values
        self.prop_labels = {}
        self.prop_values = {}

        properties = [
            ("Name:", "name"),
            ("Size:", "size"),
            ("Format:", "format"),
            ("Bit Depth:", "depth"),
            ("Alpha:", "alpha"),
            ("Mipmaps:", "mipmaps"),
            ("Compression:", "compression")
        ]

        for i, (label, key) in enumerate(properties):
            ttk.Label(props_grid, text=label).grid(row=i, column=0, sticky=tk.W, padx=(0, 5))
            value_label = ttk.Label(props_grid, text="-")
            value_label.grid(row=i, column=1, sticky=tk.W)
            self.prop_values[key] = value_label

        # Mipmap conxseti
        mip_frame = ttk.LabelFrame(left_frame, text="Mipmap Level")
        mip_frame.pack(fill=tk.X)

        mip_controls = ttk.Frame(mip_frame)
        mip_controls.pack(fill=tk.X, padx=5, pady=5)

        self.mip_var = tk.IntVar()
        self.mip_scale = ttk.Scale(mip_controls, from_=0, to=0, orient=tk.HORIZONTAL,
                                  variable=self.mip_var, command=self.on_mip_change)
        self.mip_scale.pack(fill=tk.X, pady=(0, 5))

        self.mip_label = ttk.Label(mip_controls, text="Level 0 (0x0)")
        self.mip_label.pack()

        # Right panel - image display
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        # Display controls
        display_frame = ttk.Frame(right_frame)
        display_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Label(display_frame, text="Display Mode:").pack(side=tk.LEFT)

        self.display_var = tk.StringVar(value="normal")
        display_combo = ttk.Combobox(display_frame, textvariable=self.display_var,
                                   values=["normal", "alpha", "both"], state="readonly", width=10)
        display_combo.pack(side=tk.LEFT, padx=(5, 0))
        display_combo.bind('<<ComboboxSelected>>', self.on_display_mode_change)

        # Zoom controls
        ttk.Label(display_frame, text="Zoom:").pack(side=tk.LEFT, padx=(20, 5))
        self.zoom_var = tk.StringVar(value="100%")
        zoom_combo = ttk.Combobox(display_frame, textvariable=self.zoom_var,
                                values=["25%", "50%", "75%", "100%", "150%", "200%", "400%"],
                                state="readonly", width=8)
        zoom_combo.pack(side=tk.LEFT)
        zoom_combo.bind('<<ComboboxSelected>>', self.on_zoom_change)

        # Image display area
        image_frame = ttk.LabelFrame(right_frame, text="Preview")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        # Scrollable canvas for image
        canvas_frame = ttk.Frame(image_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg='gray50')
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        h_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        v_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize display
        self.update_texture_list()
        self.update_properties()
        self.update_image_display()

    def open_txd(self):
        """Open TXD file"""
        filename = filedialog.askopenfilename(
            title="Open TXD File",
            filetypes=[("TXD Files", "*.txd"), ("All Files", "*.*")]
        )

        if filename:
            self.status_var.set("Loading TXD file...")
            self.root.update()

            if self.txd_file.load(filename):
                self.status_var.set(f"Loaded: {os.path.basename(filename)} ({len(self.txd_file.textures)} textures)")
                self.update_texture_list()
                self.update_properties()
                self.update_image_display()
            else:
                self.status_var.set("Failed to load TXD file")

    def save_txd(self):
        """Save current TXD file"""
        if not self.txd_file.filename:
            self.save_txd_as()
            return

        self.status_var.set("Saving TXD file...")
        self.root.update()

        if self.txd_file.save(self.txd_file.filename):
            self.status_var.set(f"Saved: {os.path.basename(self.txd_file.filename)}")
        else:
            self.status_var.set("Failed to save TXD file")

    def save_txd_as(self):
        """Save TXD file with new name"""
        filename = filedialog.asksaveasfilename(
            title="Save TXD File",
            defaultextension=".txd",
            filetypes=[("TXD Files", "*.txd"), ("All Files", "*.*")]
        )

        if filename:
            self.status_var.set("Saving TXD file...")
            self.root.update()

            if self.txd_file.save(filename):
                self.txd_file.filename = filename
                self.status_var.set(f"Saved: {os.path.basename(filename)}")
            else:
                self.status_var.set("Failed to save TXD file")

    def replace_texture(self):
        """Replace current texture with image file"""
        if not self.current_texture:
            messagebox.showwarning("Warning", "No texture selected")
            return

        filename = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tga *.tiff"),
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg *.jpeg"),
                ("Bitmap Files", "*.bmp"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            try:
                # Load image
                new_image = Image.open(filename)

                # Ask if user wants to resize to match texture
                if new_image.size != (self.current_texture.width, self.current_texture.height):
                    result = messagebox.askyesnocancel(
                        "Size Mismatch",
                        f"Image size {new_image.size} doesn't match texture size "
                        f"({self.current_texture.width}x{self.current_texture.height}).\n\n"
                        f"Resize image to match texture?"
                    )

                    if result is None:  # Cancel
                        return
                    elif result:  # Yes, resize
                        new_image = new_image.resize(
                            (self.current_texture.width, self.current_texture.height),
                            Image.Resampling.LANCZOS
                        )
                    else:  # No, update texture size
                        self.current_texture.width = new_image.size[0]
                        self.current_texture.height = new_image.size[1]
                        # Regenerate mipmaps with new size
                        self.generate_mipmaps_for_texture(self.current_texture, new_image)

                # Convert image to texture format
                if ImageConverter.pil_to_txd(new_image, self.current_texture, self.current_mip_level):
                    self.status_var.set(f"Replaced texture: {self.current_texture.name}")
                    self.update_properties()
                    self.update_image_display()
                else:
                    messagebox.showerror("Error", "Failed to convert image to texture format")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def export_texture(self):
        """Export current texture to image file"""
        if not self.current_texture:
            messagebox.showwarning("Warning", "No texture selected")
            return

        filename = filedialog.asksaveasfilename(
            title="Export Texture",
            defaultextension=".png",
            initialvalue=f"{self.current_texture.name}.png",
            filetypes=[
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg"),
                ("Bitmap Files", "*.bmp"),
                ("TIFF Files", "*.tiff"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            try:
                image = ImageConverter.txd_to_pil(self.current_texture, self.current_mip_level)
                if image:
                    image.save(filename)
                    self.status_var.set(f"Exported: {os.path.basename(filename)}")
                else:
                    messagebox.showerror("Error", "Failed to convert texture to image")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export texture: {e}")

    def add_texture(self):
        """Add new texture from image file"""
        filename = filedialog.askopenfilename(
            title="Add Texture",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tga *.tiff"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            try:
                # Load image
                image = Image.open(filename)

                # Get texture name
                base_name = os.path.splitext(os.path.basename(filename))[0]
                texture_name = simpledialog.askstring("Texture Name", "Enter texture name:", initialvalue=base_name)

                if not texture_name:
                    return

                # Check if name already exists
                if any(tex.name.lower() == texture_name.lower() for tex in self.txd_file.textures):
                    messagebox.showerror("Error", "Texture name already exists")
                    return

                # Create new texture
                width, height = image.size
                has_alpha = image.mode in ('RGBA', 'LA') or 'transparency' in image.info

                # Determine format based on image
                if has_alpha:
                    format_val = RasterFormat.C8888 | RasterFormat.MIPMAP
                    depth = 32
                else:
                    format_val = RasterFormat.C888 | RasterFormat.MIPMAP
                    depth = 24

                # Create texture info
                texture = TextureInfo(
                    name=texture_name,
                    mask_name="",
                    format=format_val,
                    width=width,
                    height=height,
                    depth=depth,
                    mipmap_count=1,
                    raster_type=4,  # Texture
                    compression=0,  # No compression
                    has_alpha=has_alpha,
                    mip_levels=[]
                )

                # Generate mipmaps
                self.generate_mipmaps_for_texture(texture, image)

                # Add to TXD
                self.txd_file.textures.append(texture)

                # Update UI
                self.update_texture_list()
                self.texture_listbox.selection_set(len(self.txd_file.textures) - 1)
                self.on_texture_select(None)

                self.status_var.set(f"Added texture: {texture_name}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to add texture: {e}")

    def remove_texture(self):
        """Remove current texture"""
        if not self.current_texture:
            messagebox.showwarning("Warning", "No texture selected")
            return

        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to remove texture '{self.current_texture.name}'?"
        )

        if result:
            # Find and remove texture
            for i, texture in enumerate(self.txd_file.textures):
                if texture == self.current_texture:
                    del self.txd_file.textures[i]
                    break

            # Update UI
            self.current_texture = None
            self.update_texture_list()
            self.update_properties()
            self.update_image_display()

            self.status_var.set("Texture removed")

    def generate_mipmaps(self):
        """Generate mipmaps for current texture"""
        if not self.current_texture:
            messagebox.showwarning("Warning", "No texture selected")
            return

        try:
            # Get base image
            base_image = ImageConverter.txd_to_pil(self.current_texture, 0)
            if not base_image:
                messagebox.showerror("Error", "Failed to get base texture image")
                return

            self.generate_mipmaps_for_texture(self.current_texture, base_image)

            # Update UI
            self.update_mipmap_controls()
            self.update_properties()
            self.update_image_display()

            self.status_var.set(f"Generated {self.current_texture.mipmap_count} mipmap levels")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate mipmaps: {e}")

    def generate_mipmaps_for_texture(self, texture: TextureInfo, base_image: Image.Image):
        """Generate mipmaps for a texture"""
        texture.mip_levels.clear()

        width, height = base_image.size
        mip_count = 1

        # Calculate maximum mipmap levels
        max_levels = int(math.log2(max(width, height))) + 1

        current_image = base_image.copy()

        for level in range(max_levels):
            mip_width = max(1, width >> level)
            mip_height = max(1, height >> level)

            if level > 0:
                current_image = base_image.resize((mip_width, mip_height), Image.Resampling.LANCZOS)

            # Convert to texture format
            if level == 0:
                # Use original image for level 0
                ImageConverter.pil_to_txd(current_image, texture, 0)
            else:
                # Create temporary mip level
                temp_mip = MipLevel(mip_width, mip_height, b'', 0)
                texture.mip_levels.append(temp_mip)
                ImageConverter.pil_to_txd(current_image, texture, level)

            mip_count += 1

            # Stop if we've reached 1x1
            if mip_width == 1 and mip_height == 1:
                break

        texture.mipmap_count = len(texture.mip_levels)
        texture.format |= RasterFormat.MIPMAP

    def change_bit_depth(self):
        """Change bit depth of current texture"""
        if not self.current_texture:
            messagebox.showwarning("Warning", "No texture selected")
            return

        # Show bit depth selection dialog
        depth_dialog = BitDepthDialog(self.root, self.current_texture)
        if depth_dialog.result:
            new_format, new_depth = depth_dialog.result

            try:
                # Get current image
                image = ImageConverter.txd_to_pil(self.current_texture, 0)
                if not image:
                    messagebox.showerror("Error", "Failed to get texture image")
                    return

                # Update texture format
                old_format = self.current_texture.format
                self.current_texture.format = new_format | (old_format & RasterFormat.MIPMAP)
                self.current_texture.depth = new_depth

                # Regenerate all mipmap levels with new format
                self.generate_mipmaps_for_texture(self.current_texture, image)

                # Update UI
                self.update_properties()
                self.update_image_display()

                self.status_var.set(f"Changed bit depth to {new_depth}-bit")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to change bit depth: {e}")

    def set_display_mode(self, mode: str):
        """Set image display mode"""
        self.display_mode = mode
        self.display_var.set(mode)
        self.update_image_display()

    def on_texture_select(self, event):
        """Handle texture selection"""
        selection = self.texture_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_texture = self.txd_file.textures[index]
            self.current_mip_level = 0
            self.mip_var.set(0)

            self.update_mipmap_controls()
            self.update_properties()
            self.update_image_display()

    def on_mip_change(self, value):
        """Handle mipmap level change"""
        self.current_mip_level = int(float(value))
        self.update_mipmap_label()
        self.update_image_display()

    def on_display_mode_change(self, event):
        """Handle display mode change"""
        self.display_mode = self.display_var.get()
        self.update_image_display()

    def on_zoom_change(self, event):
        """Handle zoom change"""
        self.update_image_display()

    def update_texture_list(self):
        """Update texture list"""
        self.texture_listbox.delete(0, tk.END)
        for texture in self.txd_file.textures:
            self.texture_listbox.insert(tk.END, texture.name)

    def update_mipmap_controls(self):
        """Update mipmap controls"""
        if self.current_texture and self.current_texture.mip_levels:
            max_level = len(self.current_texture.mip_levels) - 1
            self.mip_scale.config(to=max_level)
            self.mip_scale.config(state=tk.NORMAL if max_level > 0 else tk.DISABLED)
        else:
            self.mip_scale.config(to=0, state=tk.DISABLED)

        self.update_mipmap_label()

    def update_mipmap_label(self):
        """Update mipmap level label"""
        if self.current_texture and self.current_mip_level < len(self.current_texture.mip_levels):
            mip = self.current_texture.mip_levels[self.current_mip_level]
            self.mip_label.config(text=f"Level {self.current_mip_level} ({mip.width}x{mip.height})")
        else:
            self.mip_label.config(text="Level 0 (0x0)")

    def update_properties(self):
        """Update texture properties display"""
        if self.current_texture:
            self.prop_values["name"].config(text=self.current_texture.name)
            self.prop_values["size"].config(text=f"{self.current_texture.width}x{self.current_texture.height}")

            # Format description
            format_desc = self.get_format_description(self.current_texture.format)
            self.prop_values["format"].config(text=format_desc)

            self.prop_values["depth"].config(text=f"{self.current_texture.depth}-bit")
            self.prop_values["alpha"].config(text="Yes" if self.current_texture.has_alpha else "No")
            self.prop_values["mipmaps"].config(text=str(self.current_texture.mipmap_count))

            # Compression description
            comp_desc = {0: "None", 1: "DXT1", 3: "DXT3", 5: "DXT5"}.get(self.current_texture.compression, "Unknown")
            self.prop_values["compression"].config(text=comp_desc)
        else:
            for key in self.prop_values:
                self.prop_values[key].config(text="-")

    def get_format_description(self, format_val: int) -> str:
        """Get human-readable format description"""
        base_format = format_val & 0xFF00

        format_map = {
            RasterFormat.C1555: "RGBA1555",
            RasterFormat.C565: "RGB565",
            RasterFormat.C4444: "RGBA4444",
            RasterFormat.LUM8: "Luminance8",
            RasterFormat.C8888: "RGBA8888",
            RasterFormat.C888: "RGB888",
            RasterFormat.C555: "RGB555",
            RasterFormat.PAL8: "Palette8",
            RasterFormat.PAL4: "Palette4"
        }

        desc = format_map.get(base_format, "Unknown")

        if format_val & RasterFormat.MIPMAP:
            desc += " + Mipmaps"

        return desc

    def update_image_display(self):
        """Update image display"""
        self.canvas.delete("all")

        if not self.current_texture or self.current_mip_level >= len(self.current_texture.mip_levels):
            return

        try:
            # Get image from texture
            image = ImageConverter.txd_to_pil(self.current_texture, self.current_mip_level)
            if not image:
                return

            # Apply display mode
            display_image = self.apply_display_mode(image)

            # Apply zoom
            zoom_str = self.zoom_var.get().rstrip('%')
            zoom_factor = float(zoom_str) / 100.0

            if zoom_factor != 1.0:
                new_size = (int(display_image.width * zoom_factor), int(display_image.height * zoom_factor))
                display_image = display_image.resize(new_size, Image.Resampling.NEAREST)

            # Convert to PhotoImage
            self.current_image = ImageTk.PhotoImage(display_image)

            # Display on canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_image)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

        except Exception as e:
            print(f"Error updating image display: {e}")

    def apply_display_mode(self, image: Image.Image) -> Image.Image:
        """Apply display mode to image"""
        if self.display_mode == "alpha":
            if image.mode in ('RGBA', 'LA'):
                # Show alpha channel as grayscale
                alpha = image.split()[-1]
                return alpha.convert('RGB')
            else:
                # No alpha channel, show white
                return Image.new('RGB', image.size, (255, 255, 255))

        elif self.display_mode == "both":
            if image.mode in ('RGBA', 'LA'):
                # Show image and alpha side by side
                alpha = image.split()[-1].convert('RGB')
                rgb_image = image.convert('RGB')

                combined = Image.new('RGB', (image.width * 2, image.height))
                combined.paste(rgb_image, (0, 0))
                combined.paste(alpha, (image.width, 0))
                return combined
            else:
                return image.convert('RGB')

        else:  # normal mode
            return image.convert('RGB')

    def run(self):
        """Run the application"""
        self.root.mainloop()

class BitDepthDialog:
    """Dialog for changing texture bit depth"""

    def __init__(self, parent, texture: TextureInfo):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Change Bit Depth")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        # Current format info
        info_frame = ttk.LabelFrame(self.dialog, text="Current Format")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(info_frame, text=f"Format: {self.get_format_name(texture.format)}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Bit Depth: {texture.depth}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Alpha: {'Yes' if texture.has_alpha else 'No'}").pack(anchor=tk.W, padx=5, pady=2)

        # New format selection
        format_frame = ttk.LabelFrame(self.dialog, text="New Format")
        format_frame.pack(fill=tk.X, padx=10, pady=5)

        self.format_var = tk.StringVar()

        formats = [
            ("RGB565 (16-bit)", RasterFormat.C565, 16),
            ("RGBA1555 (16-bit)", RasterFormat.C1555, 16),
            ("RGB888 (24-bit)", RasterFormat.C888, 24),
            ("RGBA8888 (32-bit)", RasterFormat.C8888, 32),
        ]

        for name, format_val, depth in formats:
            ttk.Radiobutton(format_frame, text=name, variable=self.format_var,
                          value=f"{format_val}:{depth}").pack(anchor=tk.W, padx=5, pady=2)

        # Set current format as default
        current_base = texture.format & 0xFF00
        for name, format_val, depth in formats:
            if format_val == current_base:
                self.format_var.set(f"{format_val}:{depth}")
                break

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT)

        # Wait for dialog
        self.dialog.wait_window()

    def get_format_name(self, format_val: int) -> str:
        """Get format name"""
        base_format = format_val & 0xFF00
        format_map = {
            RasterFormat.C565: "RGB565",
            RasterFormat.C1555: "RGBA1555",
            RasterFormat.C888: "RGB888",
            RasterFormat.C8888: "RGBA8888",
        }
        return format_map.get(base_format, "Unknown")

    def ok_clicked(self):
        """Handle OK button"""
        selection = self.format_var.get()
        if selection:
            format_val, depth = selection.split(':')
            self.result = (int(format_val), int(depth))
        self.dialog.destroy()

    def cancel_clicked(self):
        """Handle Cancel button"""
        self.dialog.destroy()

def main():
    """Main entry point"""
    try:
        app = TXDEditor()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
