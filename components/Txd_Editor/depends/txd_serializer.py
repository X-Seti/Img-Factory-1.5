#!/usr/bin/env python3
#this belongs in components/Txd_Editor/ txd_serializer.py - Version: 1
# X-Seti - October04 2025 - Img Factory 1.5 - TXD Serializer

"""
RenderWare TXD Binary Serializer
Writes texture dictionary files in RenderWare binary format
Supports: DXT1/DXT3/DXT5, ARGB8888, RGB888, mipmaps
"""

import struct
from typing import List, Dict, Optional

class TXDSerializer:
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
    
    def __init__(self):
        self.output = bytearray()
    
    def serialize_txd(self, textures: List[Dict]) -> bytes:
        """Serialize texture list to TXD binary data"""
        if not textures:
            return b''
        
        # Build texture dictionary
        txd_data = self._build_texture_dictionary(textures)
        
        return bytes(txd_data)
    
    def _build_texture_dictionary(self, textures: List[Dict]) -> bytearray:
        """Build complete texture dictionary"""
        # Calculate total size first (for header)
        texture_sections = []
        for texture in textures:
            tex_data = self._build_texture_native(texture)
            texture_sections.append(tex_data)
        
        # Calculate struct size
        struct_size = 4  # texture count (u32)
        struct_data = struct.pack('<I', len(textures))
        
        # Build complete dictionary
        result = bytearray()
        
        # Texture Dictionary header
        total_size = 12 + struct_size + 12  # struct section header + data + extension
        for tex_section in texture_sections:
            total_size += len(tex_section)
        
        result.extend(self._write_section_header(
            self.SECTION_TEXTURE_DICTIONARY,
            total_size - 12,  # Don't include own header
            self.RW_VERSION
        ))
        
        # Struct section (texture count)
        result.extend(self._write_section_header(
            self.SECTION_STRUCT,
            struct_size,
            self.RW_VERSION
        ))
        result.extend(struct_data)
        
        # Texture sections
        for tex_section in texture_sections:
            result.extend(tex_section)
        
        # Extension section (empty)
        result.extend(self._write_section_header(
            self.SECTION_EXTENSION,
            0,
            self.RW_VERSION
        ))
        
        return result
    
    def _build_texture_native(self, texture: Dict) -> bytearray:
        """Build texture native section"""
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
        
        # Determine format code
        format_code = self._get_format_code(format_str, has_alpha)
        
        # Calculate mipmap count
        num_mipmaps = max(1, len(mipmap_levels))
        
        # Build struct data
        struct_data = bytearray()
        
        # Platform ID (4 bytes)
        struct_data.extend(struct.pack('<I', self.PLATFORM_D3D8))
        
        # Filter flags (4 bytes)
        filter_flags = 0x1102  # Linear filtering
        struct_data.extend(struct.pack('<I', filter_flags))
        
        # Texture name (32 bytes, null-terminated)
        name_bytes = name.encode('ascii')[:31] + b'\x00'
        name_bytes = name_bytes.ljust(32, b'\x00')
        struct_data.extend(name_bytes)
        
        # Alpha name (32 bytes, null-terminated)
        if has_alpha and alpha_name:
            alpha_bytes = alpha_name.encode('ascii')[:31] + b'\x00'
            alpha_bytes = alpha_bytes.ljust(32, b'\x00')
        else:
            alpha_bytes = b'\x00' * 32
        struct_data.extend(alpha_bytes)
        
        # Raster format (4 bytes)
        raster_format = format_code | 0x0400  # 0x0400 = has mipmaps flag if mipmaps > 1
        if num_mipmaps == 1:
            raster_format = format_code
        struct_data.extend(struct.pack('<I', raster_format))
        
        # D3D format (4 bytes) - only for D3D platform
        d3d_format = self._get_d3d_format(format_str)
        struct_data.extend(struct.pack('<I', d3d_format))
        
        # Width and Height (2 bytes each)
        struct_data.extend(struct.pack('<HH', width, height))
        
        # Depth (1 byte)
        struct_data.extend(struct.pack('<B', depth))
        
        # Mipmap count (1 byte)
        struct_data.extend(struct.pack('<B', num_mipmaps))
        
        # Raster type (1 byte)
        raster_type = 0x04  # Texture
        struct_data.extend(struct.pack('<B', raster_type))
        
        # Compression flags (1 byte)
        compression = 0x08 if 'DXT' in format_str else 0x00
        struct_data.extend(struct.pack('<B', compression))
        
        # Texture data size (4 bytes)
        if mipmap_levels:
            # Use actual mipmap data sizes
            total_data_size = sum(level.get('compressed_size', 0) for level in mipmap_levels)
        else:
            # Estimate based on format
            total_data_size = self._calculate_texture_size(width, height, format_str, num_mipmaps)
        
        struct_data.extend(struct.pack('<I', total_data_size))
        
        # Texture data (mipmap levels)
        texture_data = bytearray()
        
        if mipmap_levels:
            # Write each mipmap level
            for level in sorted(mipmap_levels, key=lambda x: x.get('level', 0)):
                level_data = level.get('compressed_data') or level.get('rgba_data', b'')
                if level_data:
                    texture_data.extend(level_data)
        else:
            # Use main rgba_data
            if 'DXT' in format_str:
                # Need to compress - for now use placeholder
                compressed = self._compress_to_dxt(rgba_data, width, height, format_str)
                texture_data.extend(compressed)
            else:
                texture_data.extend(rgba_data)
        
        # Pad struct_data to align
        while len(struct_data) % 4 != 0:
            struct_data.append(0)
        
        # Build section
        # Texture Native header
        section_size = 12 + len(struct_data) + len(texture_data) + 12  # +12 for extension
        result.extend(self._write_section_header(
            self.SECTION_TEXTURE_NATIVE,
            section_size - 12,
            self.RW_VERSION
        ))
        
        # Struct section
        result.extend(self._write_section_header(
            self.SECTION_STRUCT,
            len(struct_data) + len(texture_data),
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
    
    def _write_section_header(self, section_type: int, size: int, version: int) -> bytes:
        """Write RenderWare section header"""
        return struct.pack('<III', section_type, size, version)
    
    def _get_format_code(self, format_str: str, has_alpha: bool) -> int:
        """Get RenderWare format code"""
        format_map = {
            'DXT1': 0x31545844,  # 'DXT1' in hex
            'DXT3': 0x33545844,  # 'DXT3'
            'DXT5': 0x35545844,  # 'DXT5'
            'ARGB8888': 0x15,
            'RGB888': 0x14,
            'ARGB1555': 0x02,
            'RGB565': 0x01,
            'PAL8': 0x05,
        }
        return format_map.get(format_str, 0x31545844)
    
    def _get_d3d_format(self, format_str: str) -> int:
        """Get D3D format code"""
        d3d_map = {
            'DXT1': 0x31545844,  # D3DFMT_DXT1
            'DXT3': 0x33545844,  # D3DFMT_DXT3
            'DXT5': 0x35545844,  # D3DFMT_DXT5
            'ARGB8888': 21,      # D3DFMT_A8R8G8B8
            'RGB888': 20,        # D3DFMT_R8G8B8
            'ARGB1555': 25,      # D3DFMT_A1R5G5B5
            'RGB565': 23,        # D3DFMT_R5G6B5
            'PAL8': 0x14,        # D3DFMT_P8
        }
        return d3d_map.get(format_str, 0x31545844)
    
    def _calculate_texture_size(self, width: int, height: int, format_str: str, num_mipmaps: int) -> int:
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
    
    def _compress_to_dxt(self, rgba_data: bytes, width: int, height: int, format_str: str) -> bytes:
        """Compress RGBA data to DXT format (placeholder)"""
        # This is a simplified placeholder
        # Real DXT compression is complex and should use a library
        
        if not rgba_data:
            # Generate blank compressed data
            if 'DXT1' in format_str:
                size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * 8
            else:
                size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * 16
            return b'\x00' * size
        
        # Return placeholder - actual compression needed
        return rgba_data[:self._calculate_texture_size(width, height, format_str, 1)]


# Integration with TXD Workshop
def serialize_txd_file(textures: List[Dict]) -> Optional[bytes]:
    """Serialize texture list to TXD binary format"""
    try:
        serializer = TXDSerializer()
        return serializer.serialize_txd(textures)
    except Exception as e:
        print(f"Serialization error: {e}")
        return None
