#!/usr/bin/env python3
#this belongs in methods/ txd_serializer.py - Version: 4
# X-Seti - October11 2025 - Img Factory 1.5 - TXD Serializer

"""
RenderWare TXD Binary Serializer
Writes texture dictionary files in RenderWare binary format
Supports: DXT1/DXT3/DXT5, ARGB8888, RGB888, mipmaps, bumpmaps, reflection maps
REVERTED: Names go INSIDE struct (88-byte header format), not separate STRING sections
"""

import struct
from typing import List, Dict, Optional

##Methods list -
# __init__
# _build_texture_dictionary
# _build_texture_dictionary_from_sections
# _build_texture_native
# _calculate_texture_size
# _compress_to_dxt
# _get_d3d_format
# _get_format_code
# _write_section_header
# serialize_txd
# serialize_txd_file

class TXDSerializer: #vers 1
    """Serialize texture data to RenderWare TXD binary format"""
    
    # RenderWare section types
    SECTION_STRUCT = 0x01
    SECTION_STRING = 0x02
    SECTION_EXTENSION = 0x03
    SECTION_TEXTURE_DICTIONARY = 0x16
    SECTION_TEXTURE_NATIVE = 0x15
    
    # Platform identifiers
    PLATFORM_D3D8 = 0x08  # PC/DirectX 8
    PLATFORM_D3D9 = 0x09  # PC/DirectX 9
    
    # RenderWare version
    RW_VERSION = 0x1803FFFF  # 3.6.0.3
    
    def __init__(self): #vers 1
        self.output = bytearray()
    
    def serialize_txd(self, textures: List[Dict], target_version: int = None, 
                     target_device: int = None) -> bytes: #vers 1
        """Serialize texture list to TXD binary data"""
        if not textures:
            return b''
        
        txd_data = self._build_texture_dictionary(textures)
        return bytes(txd_data)
    
    def _build_texture_dictionary(self, textures: List[Dict]) -> bytearray: #vers 1
        """Build complete texture dictionary"""
        texture_sections = []
        for texture in textures:
            tex_data = self._build_texture_native(texture)
            texture_sections.append(tex_data)
        
        struct_size = 4
        struct_data = struct.pack('<I', len(textures))
        
        result = bytearray()
        
        total_size = 12 + struct_size + 12
        for tex_section in texture_sections:
            total_size += len(tex_section)
        
        result.extend(self._write_section_header(
            self.SECTION_TEXTURE_DICTIONARY,
            total_size - 12,
            self.RW_VERSION
        ))
        
        result.extend(self._write_section_header(
            self.SECTION_STRUCT,
            struct_size,
            self.RW_VERSION
        ))
        result.extend(struct_data)
        
        for tex_section in texture_sections:
            result.extend(tex_section)
        
        result.extend(self._write_section_header(
            self.SECTION_EXTENSION,
            0,
            self.RW_VERSION
        ))
        
        return result
    
    def _build_texture_native(self, texture: Dict) -> bytearray: #vers 4
        """Build texture native - REVERTED: Names inside struct (88-byte header)"""
        result = bytearray()
        
        # Get texture properties
        width = texture.get('width', 256)
        height = texture.get('height', 256)
        depth = texture.get('depth', 32)
        format_str = texture.get('format', 'DXT1')
        has_alpha = texture.get('has_alpha', False)
        rgba_data = texture.get('rgba_data', b'')
        mipmap_levels = texture.get('mipmap_levels', [])
        name = texture.get('name', 'texture')
        alpha_name = texture.get('alpha_name', name + 'a') if has_alpha else ''
        
        bumpmap_data = texture.get('bumpmap_data', b'')
        has_bumpmap = texture.get('has_bumpmap', False) or bool(bumpmap_data)
        reflection_map = texture.get('reflection_map', b'')
        fresnel_map = texture.get('fresnel_map', b'')
        has_reflection = texture.get('has_reflection', False) or bool(reflection_map)
        
        format_code = self._get_format_code(format_str, has_alpha)
        num_mipmaps = max(1, len(mipmap_levels))
        
        # Build struct data WITH names (88-byte header)
        struct_data = bytearray()
        
        # Platform ID (4 bytes)
        struct_data.extend(struct.pack('<I', self.PLATFORM_D3D8))
        
        # Filter flags (4 bytes)
        filter_flags = texture.get('filter_flags', 0x1102)
        struct_data.extend(struct.pack('<I', filter_flags))
        
        # REVERTED: Texture name INSIDE struct (32 bytes, null-terminated)
        name_bytes = name.encode('ascii')[:31] + b'\x00'
        name_bytes = name_bytes.ljust(32, b'\x00')
        struct_data.extend(name_bytes)
        
        # REVERTED: Alpha name INSIDE struct (32 bytes, null-terminated)
        if has_alpha and alpha_name:
            alpha_bytes = alpha_name.encode('ascii')[:31] + b'\x00'
            alpha_bytes = alpha_bytes.ljust(32, b'\x00')
        else:
            alpha_bytes = b'\x00' * 32
        struct_data.extend(alpha_bytes)
        
        # Raster format (4 bytes)
        raster_format = format_code
        if num_mipmaps > 1:
            raster_format |= 0x0400
        
        raster_format_flags = texture.get('raster_format_flags', 0)
        if has_bumpmap:
            raster_format_flags |= 0x10
        
        raster_format |= (raster_format_flags & 0xFF0)
        struct_data.extend(struct.pack('<I', raster_format))
        
        # D3D format (4 bytes)
        d3d_format = self._get_d3d_format(format_str)
        struct_data.extend(struct.pack('<I', d3d_format))
        
        # Width and Height (2 bytes each)
        struct_data.extend(struct.pack('<HH', width, height))
        
        # Depth (1 byte)
        struct_data.extend(struct.pack('<B', depth))
        
        # Mipmap count (1 byte)
        struct_data.extend(struct.pack('<B', num_mipmaps))
        
        # Raster type (1 byte)
        raster_type = 0x04
        struct_data.extend(struct.pack('<B', raster_type))
        
        # Compression flags (1 byte)
        compression = 0x08 if 'DXT' in format_str else 0x00
        struct_data.extend(struct.pack('<B', compression))
        
        # Calculate total data size
        total_data_size = 0
        
        if mipmap_levels:
            total_data_size = sum(level.get('compressed_size', 0) for level in mipmap_levels)
        else:
            total_data_size = self._calculate_texture_size(width, height, format_str, num_mipmaps)
        
        if bumpmap_data:
            total_data_size += 4 + 1 + len(bumpmap_data)
        
        if reflection_map:
            total_data_size += 4 + len(reflection_map)
        if fresnel_map:
            total_data_size += 4 + len(fresnel_map)
        
        struct_data.extend(struct.pack('<I', total_data_size))
        
        # Build texture data section
        texture_data = bytearray()
        
        # Write mipmap levels
        if mipmap_levels:
            for level in sorted(mipmap_levels, key=lambda x: x.get('level', 0)):
                level_data = level.get('compressed_data') or level.get('rgba_data', b'')
                if level_data:
                    texture_data.extend(level_data)
        else:
            if 'DXT' in format_str:
                compressed = texture.get('compressed_data', b'')
                if compressed:
                    texture_data.extend(compressed)
                else:
                    compressed = self._compress_to_dxt(rgba_data, width, height, format_str)
                    texture_data.extend(compressed)
            else:
                if rgba_data:
                    texture_data.extend(rgba_data)
                else:
                    size = width * height * 4
                    texture_data.extend(b'\x00' * size)
        
        # Write bumpmap data
        if bumpmap_data:
            bumpmap_header = struct.pack('<I', len(bumpmap_data))
            texture_data.extend(bumpmap_header)
            bumpmap_type = texture.get('bumpmap_type', 0)
            texture_data.extend(struct.pack('<B', bumpmap_type))
            texture_data.extend(bumpmap_data)
        
        # Write reflection data
        if reflection_map:
            reflection_header = struct.pack('<I', len(reflection_map))
            texture_data.extend(reflection_header)
            texture_data.extend(reflection_map)
        
        if fresnel_map:
            fresnel_header = struct.pack('<I', len(fresnel_map))
            texture_data.extend(fresnel_header)
            texture_data.extend(fresnel_map)
        
        # Pad struct_data to align
        while len(struct_data) % 4 != 0:
            struct_data.append(0)
        
        # Calculate section sizes
        struct_section_size = len(struct_data) + len(texture_data)
        
        # Total: TextureNative + Struct + Extension
        total_size = 12 + struct_section_size + 12
        
        # Write TextureNative header
        result.extend(self._write_section_header(
            self.SECTION_TEXTURE_NATIVE,
            total_size - 12,
            self.RW_VERSION
        ))
        
        # Write Struct section
        result.extend(self._write_section_header(
            self.SECTION_STRUCT,
            struct_section_size,
            self.RW_VERSION
        ))
        result.extend(struct_data)
        result.extend(texture_data)
        
        # Extension (empty)
        result.extend(self._write_section_header(
            self.SECTION_EXTENSION,
            0,
            self.RW_VERSION
        ))
        
        return result
    
    def _write_section_header(self, section_type: int, size: int, version: int) -> bytes: #vers 1
        """Write RenderWare section header"""
        return struct.pack('<III', section_type, size, version)
    
    def _get_format_code(self, format_str: str, has_alpha: bool) -> int: #vers 1
        """Get RenderWare format code"""
        format_map = {
            'DXT1': 0x31545844,
            'DXT3': 0x33545844,
            'DXT5': 0x35545844,
            'ARGB8888': 0x15,
            'RGB888': 0x14,
            'ARGB1555': 0x02,
            'RGB565': 0x01,
            'PAL8': 0x05,
        }
        return format_map.get(format_str, 0x31545844)
    
    def _get_d3d_format(self, format_str: str) -> int: #vers 1
        """Get D3D format code"""
        d3d_map = {
            'DXT1': 0x31545844,
            'DXT3': 0x33545844,
            'DXT5': 0x35545844,
            'ARGB8888': 21,
            'RGB888': 20,
            'ARGB1555': 25,
            'RGB565': 23,
            'PAL8': 0x14,
        }
        return d3d_map.get(format_str, 0x31545844)
    
    def _calculate_texture_size(self, width: int, height: int, format_str: str, num_mipmaps: int) -> int: #vers 1
        """Calculate texture data size"""
        total = 0
        w, h = width, height
        
        for i in range(num_mipmaps):
            if 'DXT1' in format_str:
                size = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * 8
            elif 'DXT' in format_str:
                size = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * 16
            elif 'ARGB8888' in format_str:
                size = w * h * 4
            elif 'RGB888' in format_str:
                size = w * h * 3
            elif 'PAL8' in format_str:
                size = w * h
            else:
                size = w * h * 2
            
            total += size
            w = max(1, w // 2)
            h = max(1, h // 2)
        
        return total
    
    def _compress_to_dxt(self, rgba_data: bytes, width: int, height: int, format_str: str) -> bytes: #vers 1
        """Compress RGBA data to DXT format (placeholder)"""
        if not rgba_data:
            if 'DXT1' in format_str:
                size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * 8
            else:
                size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * 16
            return b'\x00' * size
        
        return rgba_data[:self._calculate_texture_size(width, height, format_str, 1)]

    def _build_texture_dictionary_from_sections(self, texture_sections, texture_count): #vers 1
        """Build texture dictionary from pre-built texture sections"""
        struct_size = 4
        struct_data = struct.pack('<I', texture_count)

        result = bytearray()

        total_size = 12 + struct_size + 12
        for tex_section in texture_sections:
            total_size += len(tex_section)

        result.extend(self._write_section_header(
            self.SECTION_TEXTURE_DICTIONARY,
            total_size - 12,
            self.RW_VERSION
        ))

        result.extend(self._write_section_header(
            self.SECTION_STRUCT,
            struct_size,
            self.RW_VERSION
        ))
        result.extend(struct_data)

        for tex_section in texture_sections:
            result.extend(tex_section)

        result.extend(self._write_section_header(
            self.SECTION_EXTENSION,
            0,
            self.RW_VERSION
        ))

        return result


def serialize_txd_file(textures: List[Dict], target_version: int = None, 
                      target_device: int = None) -> Optional[bytes]: #vers 1
    """
    Serialize texture list to TXD binary format
    
    Args:
        textures: List of texture dictionaries
        target_version: Target RenderWare version (optional)
        target_device: Target platform device (optional)
    
    Returns:
        bytes: Serialized TXD data or None on error
    """
    try:
        serializer = TXDSerializer()
        return serializer.serialize_txd(textures, target_version, target_device)
    except Exception as e:
        print(f"TXD serialization error: {e}")
        return None


# DOCUMENTATION
"""
TXD FILE STRUCTURE - VERSION 4 (REVERTED TO WORKING FORMAT):

TextureNative {
    Struct {
        Platform ID (4 bytes)
        Filter flags (4 bytes)
        Texture name (32 bytes)         <- INSIDE struct
        Alpha name (32 bytes)            <- INSIDE struct
        Raster format (4 bytes)
        D3D format (4 bytes)
        Width (2 bytes)
        Height (2 bytes)
        Depth (1 byte)
        Mipmap count (1 byte)
        Raster type (1 byte)
        Compression (1 byte)
        Total data size (4 bytes)
        
        === TEXTURE DATA ===
        Mipmap levels...
        Bumpmap data (if present)
        Reflection data (if present)
    }
    Extension {}
}

CHANGES FROM VERSION 3:
- REVERTED: Names back INSIDE struct as 32-byte fields
- This matches the parser's expectations (_parse_single_texture)
- v3's separate STRING sections caused corruption
- This is the 88-byte header format that IMG Factory uses
"""
