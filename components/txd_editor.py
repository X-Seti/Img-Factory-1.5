#this belongs in components/ txd_editor.py - Version: 3
# X-Seti - August27 2025 - IMG Factory 1.5 - TXD Texture Editor
"""
TXD Texture Editor integrated with IMG Factory 1.5
Features:
- Theme integration with themer_settings.json
- Thumbnail view for texture preview
- DFF texture list comparison
- Missing texture detection
- Batch conversion support
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont
import struct
import os
import io
import json
import math
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import IntEnum

##Methods list -
# apply_theme_colors
# check_dff_texture_requirements
# create_thumbnail_grid
# export_batch_textures
# get_dff_texture_list
# load_theme_settings
# on_thumbnail_click
# setup_dff_comparison_panel
# setup_thumbnail_view
# update_missing_textures_display
# update_thumbnail_grid

VERSION = "1.5.0"

class RasterFormat(IntEnum): #vers 1
    """RenderWare raster format constants"""
    DEFAULT = 0x0000
    C1555 = 0x0100
    C565 = 0x0200  
    C4444 = 0x0300
    LUM8 = 0x0400
    C8888 = 0x0500
    C888 = 0x0600
    D16 = 0x0700
    D24 = 0x0800
    D32 = 0x0900
    C555 = 0x0A00
    AUTOMIPMAP = 0x1000
    PAL8 = 0x2000
    PAL4 = 0x4000
    MIPMAP = 0x8000

@dataclass
class MipLevel: #vers 1
    """Represents a mipmap level"""
    width: int
    height: int
    data: bytes
    size: int

@dataclass 
class TextureInfo: #vers 1
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

@dataclass
class DFFTextureRef: #vers 1
    """DFF texture reference"""
    texture_name: str
    material_name: str
    required: bool = True

class ThemeManager: #vers 1
    """Manages IMG Factory 1.5 theme integration"""
    
    def __init__(self):
        self.theme_data = None
        self.settings = None
        self.load_theme_settings() #vers 1
        
    def load_theme_settings(self): #vers 1
        """Load theme settings from themer_settings.json"""
        try:
            # Try to load themer_settings.json from root
            settings_file = "themer_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                # Fallback to default settings
                self.settings = self.get_default_settings()
                
            # Load theme file
            theme_name = self.settings.get('theme', 'img_factory_light')
            theme_file = f"themes/{theme_name}.json"
            
            if os.path.exists(theme_file):
                with open(theme_file, 'r') as f:
                    self.theme_data = json.load(f)
            else:
                self.theme_data = self.get_default_theme()
                
        except Exception as e:
            print(f"Error loading theme: {e}")
            self.settings = self.get_default_settings()
            self.theme_data = self.get_default_theme()
    
    def get_default_settings(self): #vers 1
        """Get default theme settings"""
        return {
            "theme": "img_factory_light",
            "font_family": "Segoe UI",
            "font_size": 9,
            "show_tooltips": True,
            "show_button_icons": True
        }
    
    def get_default_theme(self): #vers 1
        """Get default theme colors"""
        return {
            "colors": {
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa", 
                "panel_bg": "#f1f3f4",
                "accent_primary": "#1976d2",
                "text_primary": "#000000",
                "button_normal": "#e3f2fd",
                "button_hover": "#bbdefb",
                "border": "#dee2e6",
                "success": "#4caf50",
                "warning": "#ff9800", 
                "error": "#f44336"
            }
        }
    
    def get_color(self, color_key: str, fallback: str = "#ffffff"): #vers 1
        """Get color from theme"""
        if self.theme_data and "colors" in self.theme_data:
            return self.theme_data["colors"].get(color_key, fallback)
        return fallback
        
    def get_font(self): #vers 1
        """Get theme font settings"""
        if self.settings:
            family = self.settings.get('font_family', 'Segoe UI')
            size = self.settings.get('font_size', 9)
            return (family, size)
        return ('Segoe UI', 9)

class TXDFile: #vers 1
    """TXD file handler for GTA SA/VC"""

    def __init__(self):
        self.textures: List[TextureInfo] = []
        self.version = 0x1803FFFF  # GTA SA version
        self.filename = ""

    def load(self, filename: str) -> bool: #vers 1
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

    def _read_texture(self, f) -> Optional[TextureInfo]: #vers 1
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

    def save(self, filename: str) -> bool: #vers 1
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

    def _write_texture(self, f, texture: TextureInfo): #vers 1
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

    def _calculate_txd_size(self) -> int: #vers 1
        """Calculate total TXD file size"""
        size = 12  # Info chunk size
        for texture in self.textures:
            size += self._calculate_texture_size(texture)
        return size

    def _calculate_texture_size(self, texture: TextureInfo) -> int: #vers 1
        """Calculate single texture size"""
        size = 12 + 88  # Headers + struct
        if texture.palette:
            size += 4 + len(texture.palette)
        for mip_level in texture.mip_levels:
            size += 4 + mip_level.size
        return size

class ImageConverter: #vers 1
    """Handles conversion between TXD formats and PIL Images"""

    @staticmethod
    def txd_to_pil(texture: TextureInfo, mip_level: int = 0) -> Optional[Image.Image]: #vers 1
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
    def pil_to_txd(image: Image.Image, texture: TextureInfo, mip_level: int = 0) -> bool: #vers 1
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
    def _decode_rgba8888(data: bytes, width: int, height: int) -> Image.Image: #vers 1
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
    def _encode_rgba8888(image: Image.Image) -> bytes: #vers 1
        """Encode to RGBA8888 format"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        data = bytearray()
        for pixel in image.getdata():
            r, g, b, a = pixel
            data.extend([b, g, r, a])  # Convert RGBA to BGRA

        return bytes(data)

    @staticmethod
    def _decode_rgb888(data: bytes, width: int, height: int) -> Image.Image: #vers 1
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
    def _encode_rgb888(image: Image.Image) -> bytes: #vers 1
        """Encode to RGB888 format"""
        if image.mode != 'RGB':
            image = image.convert('RGB')

        data = bytearray()
        for pixel in image.getdata():
            r, g, b = pixel
            data.extend([b, g, r])  # Convert RGB to BGR

        return bytes(data)

    @staticmethod
    def _decode_rgb565(data: bytes, width: int, height: int) -> Image.Image: #vers 1
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
    def _encode_rgb565(image: Image.Image) -> bytes: #vers 1
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
    def _decode_rgba1555(data: bytes, width: int, height: int) -> Image.Image: #vers 1
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
    def _encode_rgba1555(image: Image.Image) -> bytes: #vers 1
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
    def _decode_pal8(data: bytes, width: int, height: int, palette: bytes) -> Image.Image: #vers 1
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
    def _decode_dxt1(data: bytes, width: int, height: int) -> Image.Image: #vers 1
        """Basic DXT1 decoder"""
        img = Image.new('RGBA', (width, height), (255, 0, 255, 255))
        return img

    @staticmethod
    def _decode_dxt3(data: bytes, width: int, height: int) -> Image.Image: #vers 1
        """Basic DXT3 decoder"""
        img = Image.new('RGBA', (width, height), (255, 0, 255, 255))
        return img

    @staticmethod
    def _decode_dxt5(data: bytes, width: int, height: int) -> Image.Image: #vers 1
        """Basic DXT5 decoder"""
        img = Image.new('RGBA', (width, height), (255, 0, 255, 255))
        return img

    @staticmethod
    def _encode_dxt1(image: Image.Image) -> bytes: #vers 1
        """Basic DXT1 encoder"""
        return ImageConverter._encode_rgb565(image)

    @staticmethod
    def _encode_dxt3(image: Image.Image) -> bytes: #vers 1
        """Basic DXT3 encoder"""
        return ImageConverter._encode_rgba8888(image)

    @staticmethod
    def _encode_dxt5(image: Image.Image) -> bytes: #vers 1
        """Basic DXT5 encoder"""
        return ImageConverter._encode_rgba8888(image)

class DFFTextureAnalyzer: #vers 1
    """Analyzes DFF files to extract texture requirements"""
    
    def __init__(self):
        self.texture_refs = []
    
    def get_dff_texture_list(self, dff_filename: str) -> List[DFFTextureRef]: #vers 1
        """Extract texture list from DFF file"""
        texture_refs = []
        
        try:
            with open(dff_filename, 'rb') as f:
                # This is a simplified DFF parser
                # A full implementation would need proper RenderWare parsing
                
                # Read file and search for texture names
                file_data = f.read()
                
                # Look for texture dictionary references
                # This is a basic string search - real implementation needs proper chunk parsing
                pos = 0
                while pos < len(file_data) - 32:
                    # Look for potential texture names (null-terminated strings)
                    if file_data[pos:pos+4] == b'\x15\x00\x00\x00':  # Texture native chunk
                        # Skip ahead to potential name area
                        name_pos = pos + 88  # Approximate offset to texture name
                        if name_pos + 32 < len(file_data):
                            # Extract potential texture name
                            name_data = file_data[name_pos:name_pos+32]
                            name = name_data.rstrip(b'\x00').decode('ascii', errors='ignore')
                            
                            if name and len(name) > 2 and name.replace('_', '').isalnum():
                                texture_refs.append(DFFTextureRef(
                                    texture_name=name,
                                    material_name=f"Material_{len(texture_refs)}",
                                    required=True
                                ))
                    pos += 1
                    
        except Exception as e:
            print(f"Error reading DFF file: {e}")
            
        return texture_refs
    
    def check_dff_texture_requirements(self, dff_file: str, txd_file: TXDFile) -> Dict[str, Any]: #vers 1
        """Check which textures from DFF are missing in TXD"""
        dff_textures = self.get_dff_texture_list(dff_file)
        txd_texture_names = [tex.name.lower() for tex in txd_file.textures]
        
        missing_textures = []
        found_textures = []
        
        for dff_tex in dff_textures:
            if dff_tex.texture_name.lower() in txd_texture_names:
                found_textures.append(dff_tex)
            else:
                missing_textures.append(dff_tex)
        
        return {
            'dff_textures': dff_textures,
            'missing_textures': missing_textures,
            'found_textures': found_textures,
            'missing_count': len(missing_textures),
            'found_count': len(found_textures),
            'total_required': len(dff_textures)
        }

class TXDEditor: #vers 1
    """Main TXD Editor application with IMG Factory 1.5 integration"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"TXD Texture Editor v{VERSION} - IMG Factory 1.5")
        self.root.geometry("1400x900")

        # Initialize components
        self.theme_manager = ThemeManager()
        self.txd_file = TXDFile()
        self.dff_analyzer = DFFTextureAnalyzer()
        
        # Editor state
        self.current_texture = None
        self.current_mip_level = 0
        self.current_image = None
        self.display_mode = "normal"  # "normal", "alpha", "both"
        self.view_mode = "thumbnail"  # "thumbnail", "list"
        self.thumbnail_size = 64
        
        # DFF comparison data
        self.loaded_dff_file = None
        self.dff_analysis = None
        self.missing_textures = []
        
        # Thumbnail grid
        self.thumbnail_widgets = []
        self.selected_thumbnail = None

        self.setup_ui()
        self.setup_menu()
        self.apply_theme_colors()

    def setup_menu(self): #vers 1
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open TXD...", command=self.open_txd, accelerator="Ctrl+O")
        file_menu.add_command(label="Save TXD", command=self.save_txd, accelerator="Ctrl+S")
        file_menu.add_command(label="Save TXD As...", command=self.save_txd_as)
        file_menu.add_separator()
        file_menu.add_command(label="Load DFF for Comparison...", command=self.load_dff_file)
        file_menu.add_separator()
        file_menu.add_command(label="Batch Export Textures...", command=self.export_batch_textures)
        file_menu.add_command(label="Batch Convert TXDs...", command=self.batch_convert_txds)
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

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Thumbnail View", command=lambda: self.set_view_mode("thumbnail"))
        view_menu.add_command(label="List View", command=lambda: self.set_view_mode("list"))
        view_menu.add_separator()
        view_menu.add_command(label="Small Thumbnails (32px)", command=lambda: self.set_thumbnail_size(32))
        view_menu.add_command(label="Medium Thumbnails (64px)", command=lambda: self.set_thumbnail_size(64))
        view_menu.add_command(label="Large Thumbnails (128px)", command=lambda: self.set_thumbnail_size(128))
        view_menu.add_separator()
        view_menu.add_command(label="Normal", command=lambda: self.set_display_mode("normal"))
        view_menu.add_command(label="Alpha Channel", command=lambda: self.set_display_mode("alpha"))
        view_menu.add_command(label="Both", command=lambda: self.set_display_mode("both"))

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Show Missing Textures", command=self.show_missing_textures)
        tools_menu.add_command(label="Texture Requirements Report", command=self.show_texture_report)
        tools_menu.add_separator()
        tools_menu.add_command(label="Reload Theme", command=self.reload_theme)

        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_txd())
        self.root.bind('<Control-s>', lambda e: self.save_txd())

    def setup_ui(self): #vers 1
        """Setup user interface"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Main paned window
        main_paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # Left panel
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Setup texture view (thumbnail grid)
        self.setup_thumbnail_view(left_frame)

        # DFF comparison panel
        self.setup_dff_comparison_panel(left_frame)

        # Right panel - image display and properties
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        self.setup_properties_panel(right_frame)
        self.setup_image_display(right_frame)

        # Status bar
        self.status_var = tk.StringVar(value="Ready - IMG Factory 1.5 TXD Editor")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_thumbnail_view(self, parent): #vers 1
        """Setup thumbnail view for textures"""
        # Texture view frame
        view_frame = ttk.LabelFrame(parent, text="Textures")
        view_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # View controls
        controls_frame = ttk.Frame(view_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        # View mode buttons
        self.view_mode_var = tk.StringVar(value="thumbnail")
        ttk.Radiobutton(controls_frame, text="Thumbnails", variable=self.view_mode_var,
                       value="thumbnail", command=self.update_texture_view).pack(side=tk.LEFT)
        ttk.Radiobutton(controls_frame, text="List", variable=self.view_mode_var,
                       value="list", command=self.update_texture_view).pack(side=tk.LEFT, padx=(10, 0))

        # Thumbnail size control
        ttk.Label(controls_frame, text="Size:").pack(side=tk.LEFT, padx=(20, 5))
        size_var = tk.IntVar(value=64)
        size_combo = ttk.Combobox(controls_frame, textvariable=size_var, 
                                 values=[32, 48, 64, 96, 128], width=8, state="readonly")
        size_combo.pack(side=tk.LEFT)
        size_combo.bind('<<ComboboxSelected>>', lambda e: self.set_thumbnail_size(size_var.get()))

        # Scrollable frame for thumbnails
        canvas_frame = ttk.Frame(view_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.texture_canvas = tk.Canvas(canvas_frame)
        texture_scrollbar_v = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.texture_canvas.yview)
        texture_scrollbar_h = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.texture_canvas.xview)
        
        self.texture_canvas.config(yscrollcommand=texture_scrollbar_v.set, 
                                  xscrollcommand=texture_scrollbar_h.set)

        # Scrollable frame inside canvas
        self.texture_scroll_frame = ttk.Frame(self.texture_canvas)
        self.texture_canvas.create_window((0, 0), window=self.texture_scroll_frame, anchor=tk.NW)

        self.texture_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        texture_scrollbar_v.grid(row=0, column=1, sticky=tk.NS)
        texture_scrollbar_h.grid(row=1, column=0, sticky=tk.EW)

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Bind canvas scroll events
        self.texture_canvas.bind('<Configure>', self.on_canvas_configure)
        self.texture_canvas.bind_all('<MouseWheel>', self.on_mousewheel)

        # Legacy list view (hidden initially)
        self.texture_listbox = tk.Listbox(view_frame, height=8)
        self.texture_listbox.bind('<<ListboxSelect>>', self.on_texture_select)

    def setup_dff_comparison_panel(self, parent): #vers 1
        """Setup DFF comparison panel"""
        dff_frame = ttk.LabelFrame(parent, text="DFF Texture Comparison")
        dff_frame.pack(fill=tk.X, pady=(0, 5))

        # DFF file info
        info_frame = ttk.Frame(dff_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(info_frame, text="Load DFF File...", command=self.load_dff_file).pack(side=tk.LEFT)
        self.dff_file_label = ttk.Label(info_frame, text="No DFF loaded")
        self.dff_file_label.pack(side=tk.LEFT, padx=(10, 0))

        # Status labels
        status_frame = ttk.Frame(dff_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.missing_count_label = ttk.Label(status_frame, text="Missing: 0", foreground="red")
        self.missing_count_label.pack(side=tk.LEFT)

        self.found_count_label = ttk.Label(status_frame, text="Found: 0", foreground="green")
        self.found_count_label.pack(side=tk.LEFT, padx=(20, 0))

        ttk.Button(status_frame, text="Show Report", command=self.show_texture_report).pack(side=tk.RIGHT)

    def setup_properties_panel(self, parent): #vers 1
        """Setup properties panel"""
        props_frame = ttk.LabelFrame(parent, text="Texture Properties")
        props_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Properties grid
        props_grid = ttk.Frame(props_frame)
        props_grid.pack(fill=tk.X, padx=5, pady=5)

        # Property labels and values
        self.prop_values = {}
        properties = [
            ("Name:", "name"),
            ("Size:", "size"),
            ("Format:", "format"),
            ("Bit Depth:", "depth"),
            ("Alpha:", "alpha"),
            ("Mipmaps:", "mipmaps"),
            ("Status:", "status")
        ]

        for i, (label, key) in enumerate(properties):
            ttk.Label(props_grid, text=label).grid(row=i, column=0, sticky=tk.W, padx=(0, 5))
            value_label = ttk.Label(props_grid, text="-")
            value_label.grid(row=i, column=1, sticky=tk.W)
            self.prop_values[key] = value_label

        # Mipmap level control
        mip_frame = ttk.Frame(props_frame)
        mip_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        ttk.Label(mip_frame, text="Mipmap Level:").pack(side=tk.LEFT)
        self.mip_var = tk.IntVar()
        self.mip_scale = ttk.Scale(mip_frame, from_=0, to=0, orient=tk.HORIZONTAL,
                                  variable=self.mip_var, command=self.on_mip_change)
        self.mip_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

    def setup_image_display(self, parent): #vers 1
        """Setup image display area"""
        # Display controls
        display_frame = ttk.Frame(parent)
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
        image_frame = ttk.LabelFrame(parent, text="Texture Preview")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        # Scrollable canvas for image
        canvas_container = ttk.Frame(image_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_container)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        h_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        v_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)

    def apply_theme_colors(self): #vers 1
        """Apply IMG Factory 1.5 theme colors"""
        try:
            # Get theme colors
            bg_primary = self.theme_manager.get_color('bg_primary', '#ffffff')
            bg_secondary = self.theme_manager.get_color('bg_secondary', '#f8f9fa')
            panel_bg = self.theme_manager.get_color('panel_bg', '#f1f3f4')
            text_primary = self.theme_manager.get_color('text_primary', '#000000')
            accent_primary = self.theme_manager.get_color('accent_primary', '#1976d2')

            # Configure root window
            self.root.configure(bg=bg_primary)

            # Configure canvas backgrounds
            if hasattr(self, 'texture_canvas'):
                self.texture_canvas.configure(bg=bg_secondary)
            
            if hasattr(self, 'canvas'):
                self.canvas.configure(bg=panel_bg)

        except Exception as e:
            print(f"Error applying theme colors: {e}")

    def create_thumbnail_grid(self): #vers 1
        """Create thumbnail grid for texture display"""
        # Clear existing thumbnails
        for widget in self.thumbnail_widgets:
            widget.destroy()
        self.thumbnail_widgets.clear()

        if not self.txd_file.textures:
            return

        # Calculate grid dimensions
        canvas_width = self.texture_canvas.winfo_width()
        if canvas_width <= 1:  # Not yet rendered
            canvas_width = 400
        
        thumb_total = self.thumbnail_size + 10  # thumbnail + padding
        cols = max(1, canvas_width // thumb_total)

        # Create thumbnail widgets
        for i, texture in enumerate(self.txd_file.textures):
            row = i // cols
            col = i % cols

            # Create thumbnail frame
            thumb_frame = ttk.Frame(self.texture_scroll_frame)
            thumb_frame.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NW)

            # Create thumbnail image
            try:
                pil_image = ImageConverter.txd_to_pil(texture, 0)
                if pil_image:
                    # Resize to thumbnail size
                    pil_image.thumbnail((self.thumbnail_size, self.thumbnail_size), Image.Resampling.LANCZOS)
                    
                    # Create thumbnail with border
                    thumb_img = Image.new('RGB', (self.thumbnail_size, self.thumbnail_size), (200, 200, 200))
                    
                    # Center the image
                    x = (self.thumbnail_size - pil_image.width) // 2
                    y = (self.thumbnail_size - pil_image.height) // 2
                    thumb_img.paste(pil_image, (x, y))
                    
                    # Check if texture is missing from DFF
                    border_color = "green"
                    if self.dff_analysis and texture.name.lower() in [t.texture_name.lower() for t in self.dff_analysis['missing_textures']]:
                        border_color = "red"
                    elif self.dff_analysis and texture.name.lower() in [t.texture_name.lower() for t in self.dff_analysis['found_textures']]:
                        border_color = "green"
                    else:
                        border_color = "gray"

                    photo = ImageTk.PhotoImage(thumb_img)
                else:
                    # Create placeholder thumbnail
                    placeholder = Image.new('RGB', (self.thumbnail_size, self.thumbnail_size), (128, 128, 128))
                    draw = ImageDraw.Draw(placeholder)
                    draw.text((5, 5), "NO\nIMG", fill=(255, 255, 255))
                    photo = ImageTk.PhotoImage(placeholder)
                    border_color = "red"

                # Create thumbnail label
                thumb_label = tk.Label(thumb_frame, image=photo, cursor="hand2", 
                                     relief=tk.RAISED, bd=2, bg=border_color)
                thumb_label.image = photo  # Keep reference
                thumb_label.pack()

                # Bind click event
                thumb_label.bind("<Button-1>", lambda e, idx=i: self.on_thumbnail_click(idx))
                thumb_label.bind("<Double-Button-1>", lambda e, idx=i: self.on_thumbnail_double_click(idx))

                # Add texture name label
                name_label = ttk.Label(thumb_frame, text=texture.name[:12] + "..." if len(texture.name) > 12 else texture.name,
                                     font=('Arial', 8))
                name_label.pack()

                # Add size info
                size_label = ttk.Label(thumb_frame, text=f"{texture.width}×{texture.height}",
                                     font=('Arial', 7), foreground='gray')
                size_label.pack()

                self.thumbnail_widgets.extend([thumb_frame, thumb_label, name_label, size_label])

            except Exception as e:
                print(f"Error creating thumbnail for {texture.name}: {e}")

        # Update scroll region
        self.texture_scroll_frame.update_idletasks()
        self.texture_canvas.configure(scrollregion=self.texture_canvas.bbox("all"))

    def on_thumbnail_click(self, texture_index: int): #vers 1
        """Handle thumbnail click"""
        if texture_index < len(self.txd_file.textures):
            self.current_texture = self.txd_file.textures[texture_index]
            self.current_mip_level = 0
            self.mip_var.set(0)
            
            # Highlight selected thumbnail
            if self.selected_thumbnail is not None and self.selected_thumbnail < len(self.thumbnail_widgets):
                # Reset previous selection
                try:
                    prev_thumb = self.thumbnail_widgets[self.selected_thumbnail * 4 + 1]  # Label is second widget
                    prev_thumb.configure(relief=tk.RAISED, bd=2)
                except:
                    pass
            
            # Highlight current selection
            try:
                current_thumb = self.thumbnail_widgets[texture_index * 4 + 1]
                current_thumb.configure(relief=tk.SUNKEN, bd=3)
                self.selected_thumbnail = texture_index
            except:
                pass

            self.update_mipmap_controls()
            self.update_properties()
            self.update_image_display()

    def on_thumbnail_double_click(self, texture_index: int): #vers 1
        """Handle thumbnail double-click (open texture editor)"""
        self.on_thumbnail_click(texture_index)
        # Could open advanced texture editor here

    def load_dff_file(self): #vers 1
        """Load DFF file for texture comparison"""
        filename = filedialog.askopenfilename(
            title="Load DFF File",
            filetypes=[("DFF Files", "*.dff"), ("All Files", "*.*")]
        )

        if filename:
            self.loaded_dff_file = filename
            self.dff_file_label.config(text=f"DFF: {os.path.basename(filename)}")
            
            # Analyze DFF textures
            if self.txd_file.textures:
                self.dff_analysis = self.dff_analyzer.check_dff_texture_requirements(filename, self.txd_file)
                self.update_missing_textures_display()
                self.create_thumbnail_grid()  # Refresh thumbnails with color coding
                
                self.status_var.set(f"DFF loaded: {self.dff_analysis['missing_count']} missing textures found")
            else:
                self.status_var.set("Load a TXD file first to compare textures")

    def update_missing_textures_display(self): #vers 1
        """Update missing textures display"""
        if self.dff_analysis:
            missing_count = self.dff_analysis['missing_count']
            found_count = self.dff_analysis['found_count']
            
            self.missing_count_label.config(text=f"Missing: {missing_count}")
            self.found_count_label.config(text=f"Found: {found_count}")

    def show_missing_textures(self): #vers 1
        """Show dialog with missing textures"""
        if not self.dff_analysis or not self.dff_analysis['missing_textures']:
            messagebox.showinfo("Missing Textures", "No missing textures found!")
            return

        missing_dialog = tk.Toplevel(self.root)
        missing_dialog.title("Missing Textures Report")
        missing_dialog.geometry("400x300")
        missing_dialog.transient(self.root)

        # Missing textures list
        list_frame = ttk.Frame(missing_dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(list_frame, text=f"Missing Textures ({len(self.dff_analysis['missing_textures'])}):").pack(anchor=tk.W)

        missing_listbox = tk.Listbox(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=missing_listbox.yview)
        missing_listbox.config(yscrollcommand=scrollbar.set)

        for missing_tex in self.dff_analysis['missing_textures']:
            missing_listbox.insert(tk.END, missing_tex.texture_name)

        missing_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = ttk.Frame(missing_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(button_frame, text="Create Template Textures", 
                  command=lambda: self.create_missing_texture_templates(missing_dialog)).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", command=missing_dialog.destroy).pack(side=tk.RIGHT)

    def create_missing_texture_templates(self, dialog): #vers 1
        """Create placeholder textures for missing ones"""
        if not self.dff_analysis:
            return

        created_count = 0
        for missing_tex in self.dff_analysis['missing_textures']:
            # Create a simple colored placeholder texture
            placeholder_img = Image.new('RGB', (64, 64), (255, 0, 255))  # Magenta placeholder
            draw = ImageDraw.Draw(placeholder_img)
            
            # Try to load font for text
            try:
                font = ImageFont.load_default()
                draw.text((5, 25), missing_tex.texture_name[:8], fill=(255, 255, 255), font=font)
            except:
                draw.text((5, 25), missing_tex.texture_name[:8], fill=(255, 255, 255))

            # Create texture info
            texture = TextureInfo(
                name=missing_tex.texture_name,
                mask_name="",
                format=RasterFormat.C888,
                width=64,
                height=64,
                depth=24,
                mipmap_count=1,
                raster_type=4,
                compression=0,
                has_alpha=False,
                mip_levels=[]
            )

            # Add mipmap
            mip_data = ImageConverter._encode_rgb888(placeholder_img)
            mip_level = MipLevel(width=64, height=64, data=mip_data, size=len(mip_data))
            texture.mip_levels.append(mip_level)

            # Add to TXD
            self.txd_file.textures.append(texture)
            created_count += 1

        if created_count > 0:
            self.update_texture_view()
            self.status_var.set(f"Created {created_count} placeholder textures")
            messagebox.showinfo("Success", f"Created {created_count} placeholder textures")
            dialog.destroy()


    def show_texture_report(self):  # vers 1
        """Show detailed texture requirements report."""

        if not self.dff_analysis:
            messagebox.showwarning(
                "No Analysis", "Load a DFF file first to generate a report"
            )
            return

        report_dialog = tk.Toplevel(self.root)
        report_dialog.title("Texture Requirements Report")
        report_dialog.geometry("600x500")
        report_dialog.transient(self.root)

        # Text area for report
        text_frame = ttk.Frame(report_dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        report_text = tk.Text(text_frame, wrap=tk.WORD)
        report_scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=report_text.yview
        )
        report_text.config(yscrollcommand=report_scrollbar.set)

        # Generate report content
        report_content = f"""TEXTURE REQUIREMENTS REPORT
    {'='*50}

    DFF File: {os.path.basename(self.loaded_dff_file) if self.loaded_dff_file else 'Unknown'}
    TXD File: {os.path.basename(self.txd_file.filename) if self.txd_file.filename else 'Unsaved'}

    SUMMARY:
    - Total Required Textures: {self.dff_analysis['total_required']}
    - Found in TXD: {self.dff_analysis['found_count']}
    - Missing from TXD: {self.dff_analysis['missing_count']}
    - Completion: {(self.dff_analysis['found_count'] / self.dff_analysis['total_required'] * 100):.1f}%

    FOUND TEXTURES ({self.dff_analysis['found_count']}):
    {'-'*30}
    """

        for found_tex in self.dff_analysis['found_textures']:
            txd_tex = next(
                (t for t in self.txd_file.textures
                if t.name.lower() == found_tex.texture_name.lower()),
                None
            )
            if txd_tex:
                report_content += (
                    f"✓ {found_tex.texture_name} "
                    f"({txd_tex.width}x{txd_tex.height}, {txd_tex.depth}-bit)\n"
                )

        report_content += (
            f"\nMISSING TEXTURES ({self.dff_analysis['missing_count']}):\n{'-'*30}\n"
        )

        for missing_tex in self.dff_analysis['missing_textures']:
            report_content += (
                f"✗ {missing_tex.texture_name} "
                f"(Required by: {missing_tex.material_name})\n"
            )

        if self.dff_analysis['missing_count'] > 0:
            report_content += f"\nRECOMMENDATIONS:\n{'-'*15}\n"
            report_content += "- Create placeholder textures for missing ones\n"
            report_content += "- Check if textures exist in other TXD files\n"
            report_content += "- Verify DFF file is correct version\n"

        report_text.insert(tk.END, report_content)
        report_text.config(state=tk.DISABLED)

        report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Close button
        ttk.Button(report_dialog, text="Close", command=report_dialog.destroy).pack(pady=10)


    def export_batch_textures(self):  # vers 1
        """Export all textures to individual image files."""

        if not self.txd_file.textures:
            messagebox.showwarning("No Textures", "No textures to export")
            return

        export_dir = filedialog.askdirectory(title="Select Export Directory")
        if not export_dir:
            return

        exported_count = 0
        failed_count = 0

        for texture in self.txd_file.textures:
            try:
                image = ImageConverter.txd_to_pil(texture, 0)
                if image:
                    filename = os.path.join(export_dir, f"{texture.name}.png")
                    image.save(filename)
                    exported_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                print(f"Failed to export {texture.name}: {e}")
                failed_count += 1

        messagebox.showinfo(
            "Export Complete",
            f"Exported {exported_count} textures\n{failed_count} failed"
        )
        self.status_var.set(
            f"Batch export complete: {exported_count} textures exported"
        )



    def batch_convert_txds(self): #vers 1
        """Convert multiple TXD files between GTA versions"""
        source_dir = filedialog.askdirectory(title="Select Source Directory with TXD files")
        if not source_dir:
            return

        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return

        # Get conversion options
        conversion_dialog = BatchConversionDialog(self.root)
        if not conversion_dialog.result:
            return

        target_version, target_format = conversion_dialog.result

        # Find all TXD files
        txd_files = [f for f in os.listdir(source_dir) if f.lower().endswith('.txd')]

        if not txd_files:
            messagebox.showwarning("No Files", "No TXD files found in source directory")
            return

        converted_count = 0
        failed_count = 0

        for txd_filename in txd_files:
            try:
                # Load TXD
                temp_txd = TXDFile()
                source_path = os.path.join(source_dir, txd_filename)

                if temp_txd.load(source_path):
                    # Update version and format if needed
                    temp_txd.version = target_version

                    # Convert texture formats if needed
                    for texture in temp_txd.textures:
                        if target_format != "keep":
                            # Update texture format based on target
                            if target_format == "dxt1":
                                texture.compression = 1
                            elif target_format == "dxt3":
                                texture.compression = 3
                            elif target_format == "dxt5":
                                texture.compression = 5
                            elif target_format == "rgba8888":
                                texture.format = RasterFormat.C8888
                                texture.compression = 0

                    # Save converted TXD
                    output_path = os.path.join(output_dir, txd_filename)
                    if temp_txd.save(output_path):
                        converted_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                print(f"Failed to convert {txd_filename}: {e}")
                failed_count += 1

        messagebox.showinfo("Batch Conversion Complete",
                          f"Converted {converted_count} TXD files\n{failed_count} failed")
        self.status_var.set(f"Batch conversion complete: {converted_count} files converted")

    def run(self): #vers 1
        """Run the application"""
        self.root.mainloop()

class BatchConversionDialog: #vers 1
    """Dialog for batch TXD conversion options"""

    def __init__(self, parent):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Batch TXD Conversion")
        self.dialog.geometry("350x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Target version
        version_frame = ttk.LabelFrame(self.dialog, text="Target GTA Version")
        version_frame.pack(fill=tk.X, padx=10, pady=5)

        self.version_var = tk.IntVar(value=0x1803FFFF)
        ttk.Radiobutton(version_frame, text="GTA San Andreas", variable=self.version_var,
                       value=0x1803FFFF).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(version_frame, text="GTA Vice City", variable=self.version_var,
                       value=0x0800FFFF).pack(anchor=tk.W, padx=5, pady=2)

        # Target format
        format_frame = ttk.LabelFrame(self.dialog, text="Texture Format")
        format_frame.pack(fill=tk.X, padx=10, pady=5)

        self.format_var = tk.StringVar(value="keep")
        ttk.Radiobutton(format_frame, text="Keep Original", variable=self.format_var,
                       value="keep").pack(anchor=tk.W, padx=5, pady=1)
        ttk.Radiobutton(format_frame, text="DXT1 (No Alpha)", variable=self.format_var,
                       value="dxt1").pack(anchor=tk.W, padx=5, pady=1)
        ttk.Radiobutton(format_frame, text="DXT5 (With Alpha)", variable=self.format_var,
                       value="dxt5").pack(anchor=tk.W, padx=5, pady=1)
        ttk.Radiobutton(format_frame, text="RGBA8888", variable=self.format_var,
                       value="rgba8888").pack(anchor=tk.W, padx=5, pady=1)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Convert", command=self.ok_clicked).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT, padx=(0, 5))

        self.dialog.wait_window()

    def ok_clicked(self): #vers 1
        """Handle OK button"""
        self.result = (self.version_var.get(), self.format_var.get())
        self.dialog.destroy()

    def cancel_clicked(self): #vers 1
        """Handle Cancel button"""
        self.dialog.destroy()

def main(): #vers 1
    """Main entry point"""
    try:
        app = TXDEditor()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
