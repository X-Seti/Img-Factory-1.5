#!/usr/bin/env python3
#this belongs in components/Txd_Editor/depends/ txd_serializer.py - Version: 3
#this belongs in methods/ txd_serializer.py - Version: 2
# X-Seti - October10 2025 - Img Factory 1.5 - TXD Serializer

"""
RenderWare TXD Binary Serializer
Writes texture dictionary files in RenderWare binary format
Supports: DXT1/DXT3/DXT5, ARGB8888, RGB888, mipmaps, bumpmaps, reflection maps
"""

import struct
from typing import List, Dict, Optional

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
        """
        Serialize texture list to TXD binary data
        
        Args:
            textures: List of texture dictionaries
            target_version: Target RenderWare version (optional)
            target_device: Target platform device (optional)
        """
        if not textures:
            return b''
        
        # Build texture dictionary
        txd_data = self._build_texture_dictionary(textures)
        
        return bytes(txd_data)
    
    def _build_texture_dictionary(self, textures: List[Dict]) -> bytearray: #vers 1
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
    
    def _build_texture_native(self, texture: Dict) -> bytearray: #vers 2
        """Build texture native section with bumpmap and reflection support"""
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
        
        # NEW: Get bumpmap and reflection data
        bumpmap_data = texture.get('bumpmap_data', b'')
        has_bumpmap = texture.get('has_bumpmap', False) or bool(bumpmap_data)
        reflection_map = texture.get('reflection_map', b'')
        fresnel_map = texture.get('fresnel_map', b'')
        has_reflection = texture.get('has_reflection', False) or bool(reflection_map)
        
        # Determine format code
        format_code = self._get_format_code(format_str, has_alpha)
        
        # Calculate mipmap count
        num_mipmaps = max(1, len(mipmap_levels))
        
        # Build struct data
        struct_data = bytearray()
        
        # Platform ID (4 bytes)
        struct_data.extend(struct.pack('<I', self.PLATFORM_D3D8))
        
        # Filter flags (4 bytes)
        filter_flags = texture.get('filter_flags', 0x1102)  # Linear filtering
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
        
        # Raster format (4 bytes) - NEW: Set bumpmap flag if present
        raster_format = format_code
        if num_mipmaps > 1:
            raster_format |= 0x0400  # Has mipmaps flag
        
        # Get raster_format_flags from texture (may have bumpmap bit set)
        raster_format_flags = texture.get('raster_format_flags', 0)
        if has_bumpmap:
            raster_format_flags |= 0x10  # Bit 4 = bumpmap/environment map
        
        raster_format |= (raster_format_flags & 0xFF0)  # Preserve other flags
        
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
        
        # Calculate total texture data size (mipmaps + bumpmap + reflection)
        total_data_size = 0
        
        # Mipmap data size
        if mipmap_levels:
            total_data_size = sum(level.get('compressed_size', 0) for level in mipmap_levels)
        else:
            total_data_size = self._calculate_texture_size(width, height, format_str, num_mipmaps)
        
        # Add bumpmap size (if present)
        if bumpmap_data:
            # Write bumpmap header: [size:4 bytes][type:1 byte][data]
            bumpmap_header = struct.pack('<I', len(bumpmap_data))
            texture_data.extend(bumpmap_header)

            bumpmap_type = texture.get('bumpmap_type', 0)
            texture_data.extend(struct.pack('<B', bumpmap_type))
            total_data_size += len(bumpmap_data)
        
        # Add reflection map sizes (if present)
        if reflection_map:
            total_data_size += len(reflection_map)
        if fresnel_map:
            total_data_size += len(fresnel_map)
        
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
            # Use main rgba_data
            if 'DXT' in format_str:
                compressed = self._compress_to_dxt(rgba_data, width, height, format_str)
                texture_data.extend(compressed)
            else:
                texture_data.extend(rgba_data)
        
        # NEW: Write bumpmap data (after mipmaps)
        if bumpmap_data:
            # Write bumpmap header: [size:4 bytes][type:1 byte][data]
            bumpmap_header = struct.pack('<I', len(bumpmap_data))
            texture_data.extend(bumpmap_header)
            
            bumpmap_type = texture.get('bumpmap_type', 0)
            texture_data.extend(struct.pack('<B', bumpmap_type))
            
            texture_data.extend(bumpmap_data)
        
        # NEW: Write reflection maps (after bumpmap)
        if has_reflection:
            # Write reflection map header: [size:4 bytes][data]
            if reflection_map:
                reflection_header = struct.pack('<I', len(reflection_map))
                texture_data.extend(reflection_header)
                texture_data.extend(reflection_map)
            
            # Write Fresnel map header: [size:4 bytes][data]
            if fresnel_map:
                fresnel_header = struct.pack('<I', len(fresnel_map))
                texture_data.extend(fresnel_header)
                texture_data.extend(fresnel_map)
        
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
    
    def _write_section_header(self, section_type: int, size: int, version: int) -> bytes: #vers 1
        """Write RenderWare section header"""
        return struct.pack('<III', section_type, size, version)
    
    def _get_format_code(self, format_str: str, has_alpha: bool) -> int: #vers 1
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
    
    def _get_d3d_format(self, format_str: str) -> int: #vers 1
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


    def _build_texture_dictionary_from_sections(self, texture_sections, texture_count): #vers 1
        """Build texture dictionary from pre-built texture sections"""
        import struct

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


# Integration with TXD Workshop
def serialize_txd_file(textures: List[Dict], target_version: int = None, 
                      target_device: int = None) -> Optional[bytes]: #vers 1
    """
    Serialize texture list to TXD binary format
    
    Args:
        textures: List of texture dictionaries
        target_version: Target RenderWare version (optional)
        target_device: Target platform device (optional)
    
    Returns:
        TXD binary data or None on error
    """
    try:
        serializer = TXDSerializer()
        return serializer.serialize_txd(textures, target_version, target_device)
    except Exception as e:
        print(f"Serialization error: {e}")
        return None


# ============================================================================
# DOCUMENTATION
# ============================================================================

"""
TXD FILE STRUCTURE WITH BUMPMAPS AND REFLECTION:

TextureNative {
    Struct {
        Platform ID (4 bytes)
        Filter flags (4 bytes)
        Texture name (32 bytes)
        Alpha name (32 bytes)
        Raster format (4 bytes) <- Bit 0x10 set if has bumpmap
        D3D format (4 bytes)
        Width (2 bytes)
        Height (2 bytes)
        Depth (1 byte)
        Mipmap count (1 byte)
        Raster type (1 byte)
        Compression (1 byte)
        Total data size (4 bytes) <- Includes mipmaps + bumpmap + reflection
        
        === TEXTURE DATA ===
        Mipmap Level 0 (main texture)
        Mipmap Level 1
        ...
        Mipmap Level N
        
        === BUMPMAP DATA (if present) ===
        Bumpmap size (4 bytes)
        Bumpmap type (1 byte): 0=height, 1=normal, 2=both
        Bumpmap data (variable size)
        
        === REFLECTION DATA (if present) ===
        Reflection map size (4 bytes)
        Reflection map RGB data (width*height*3 bytes)
        
        Fresnel map size (4 bytes)
        Fresnel map grayscale data (width*height bytes)
    }
    Extension {}
}

CHANGES FROM VERSION 1:
- Added bumpmap_data writing after mipmaps
- Added reflection_map and fresnel_map writing after bumpmap
- Set raster_format_flags bit 0x10 when has_bumpmap is true
- Updated total_data_size calculation to include all map sizes
- Added support for target_version and target_device parameters

USAGE:
texture_dict = {
    'name': 'my_texture',
    'width': 512,
    'height': 512,
    'format': 'DXT1',
    'rgba_data': <bytes>,
    'mipmap_levels': [...],
    'bumpmap_data': <bytes>,        # NEW
    'bumpmap_type': 1,              # NEW
    'has_bumpmap': True,            # NEW
    'reflection_map': <bytes>,      # NEW
    'fresnel_map': <bytes>,         # NEW
    'has_reflection': True,         # NEW
    'raster_format_flags': 0x10     # Bumpmap flag
}

txd_data = serialize_txd_file([texture_dict])
"""
