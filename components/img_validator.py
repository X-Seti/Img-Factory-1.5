#!/usr/bin/env python3
"""
IMG Validator - Validation and verification utilities for IMG files
Provides comprehensive validation for IMG files, entries, and operations
"""

import os
import struct
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
from img_manager import IMGFile, IMGEntry, IMGVersion


class ValidationResult:
    """Container for validation results"""
    
    def __init__(self, is_valid: bool = True, warnings: List[str] = None, errors: List[str] = None):
        self.is_valid = is_valid
        self.warnings = warnings or []
        self.errors = errors or []
        self.info = []
    
    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)
    
    def add_error(self, message: str):
        """Add an error message"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_info(self, message: str):
        """Add an info message"""
        self.info.append(message)
    
    def get_summary(self) -> str:
        """Get validation summary"""
        if self.is_valid:
            if self.warnings:
                return f"Valid with {len(self.warnings)} warnings"
            else:
                return "Valid"
        else:
            return f"Invalid - {len(self.errors)} errors, {len(self.warnings)} warnings"
    
    def get_details(self) -> str:
        """Get detailed validation report"""
        details = []
        
        if self.errors:
            details.append("ERRORS:")
            for error in self.errors:
                details.append(f"  • {error}")
        
        if self.warnings:
            details.append("WARNINGS:")
            for warning in self.warnings:
                details.append(f"  • {warning}")
        
        if self.info:
            details.append("INFO:")
            for info in self.info:
                details.append(f"  • {info}")
        
        return "\n".join(details) if details else "No issues found."


class IMGValidator:
    """Comprehensive IMG file validator"""
    
    # Known file signatures for validation
    KNOWN_SIGNATURES = {
        'DFF': [b'\x10\x00\x00\x00', b'\x0E\x00\x00\x00'],  # RenderWare DFF
        'TXD': [b'\x16\x00\x00\x00'],  # RenderWare TXD
        'COL': [b'COL\x01', b'COL\x02', b'COL\x03', b'COL\x04', b'COLL'],  # Collision
        'IFP': [b'ANPK'],  # Animation package
        'SCM': [b'\x03\x00', b'\x04\x00'],  # Script
    }
    
    # Maximum reasonable file sizes (in MB)
    MAX_FILE_SIZES = {
        'DFF': 50,   # Model files
        'TXD': 100,  # Texture files
        'COL': 10,   # Collision files
        'IFP': 20,   # Animation files
        'SCM': 5,    # Script files
        'IPL': 1,    # Item placement
        'IDE': 1,    # Item definition
        'DAT': 1,    # Data files
    }
    
    @staticmethod
    def validate_img_file(img_file: IMGFile) -> ValidationResult:
        """Validate an entire IMG file"""
        result = ValidationResult()
        
        if not img_file:
            result.add_error("IMG file object is None")
            return result
        
        # Basic file validation
        if not os.path.exists(img_file.file_path):
            result.add_error(f"IMG file does not exist: {img_file.file_path}")
            return result
        
        # File size validation
        file_size = os.path.getsize(img_file.file_path)
        if file_size == 0:
            result.add_error("IMG file is empty")
            return result
        
        if file_size > 2 * 1024 * 1024 * 1024:  # 2GB
            result.add_warning("IMG file is very large (>2GB)")
        
        # Version-specific validation
        IMGValidator._validate_img_version(img_file, result)
        
        # Entry validation
        IMGValidator._validate_img_entries(img_file, result)
        
        # Structure validation
        IMGValidator._validate_img_structure(img_file, result)
        
        return result
    
    @staticmethod
    def _validate_img_version(img_file: IMGFile, result: ValidationResult):
        """Validate IMG version-specific aspects"""
        version = img_file.version
        
        if version == IMGVersion.UNKNOWN:
            result.add_error("Unknown IMG version")
            return
        
        # Version 1 specific validation
        if version == IMGVersion.VERSION_1:
            dir_path = img_file.file_path.replace('.img', '.dir')
            if not os.path.exists(dir_path):
                result.add_error(f"DIR file missing for IMG Version 1: {dir_path}")
            else:
                # Validate DIR file size
                dir_size = os.path.getsize(dir_path)
                expected_size = len(img_file.entries) * 32
                if dir_size != expected_size:
                    result.add_warning(f"DIR file size mismatch. Expected: {expected_size}, Actual: {dir_size}")
        
        # Version 3 specific validation
        elif version == IMGVersion.VERSION_3:
            if img_file.is_encrypted and img_file.encryption_type == 0:
                result.add_warning("IMG Version 3 marked as encrypted but encryption type is unknown")
        
        # Fastman92 specific validation
        elif version == IMGVersion.FASTMAN92:
            if img_file.is_encrypted:
                result.add_warning("Fastman92 format encryption is not fully supported")
            
            if img_file.game_type != 0:
                result.add_warning(f"Fastman92 format with non-standard game type: {img_file.game_type}")
    
    @staticmethod
    def _validate_img_entries(img_file: IMGFile, result: ValidationResult):
        """Validate all entries in the IMG file"""
        entries = img_file.entries
        
        if not entries:
            result.add_warning("IMG file contains no entries")
            return
        
        # Check for duplicate names
        names = [entry.name.upper() for entry in entries]
        duplicates = set([name for name in names if names.count(name) > 1])
        if duplicates:
            result.add_error(f"Duplicate entry names found: {', '.join(duplicates)}")
        
        # Validate individual entries
        total_size = 0
        offset_ranges = []
        
        for i, entry in enumerate(entries):
            entry_result = IMGValidator.validate_img_entry(entry, img_file)
            
            # Merge entry validation results
            result.warnings.extend([f"Entry '{entry.name}': {w}" for w in entry_result.warnings])
            result.errors.extend([f"Entry '{entry.name}': {e}" for e in entry_result.errors])
            if not entry_result.is_valid:
                result.is_valid = False
            
            # Track size and offsets
            total_size += entry.size
            offset_ranges.append((entry.offset, entry.offset + entry.size))
        
        # Check for overlapping entries
        sorted_ranges = sorted(offset_ranges)
        for i in range(len(sorted_ranges) - 1):
            current_end = sorted_ranges[i][1]
            next_start = sorted_ranges[i + 1][0]
            if current_end > next_start:
                result.add_error(f"Overlapping entries detected at offset {next_start}")
        
        # File size validation
        file_size = os.path.getsize(img_file.file_path)
        if total_size > file_size:
            result.add_error(f"Total entry size ({total_size}) exceeds file size ({file_size})")
        
        result.add_info(f"Validated {len(entries)} entries")
    
    @staticmethod
    def _validate_img_structure(img_file: IMGFile, result: ValidationResult):
        """Validate IMG file structure and layout"""
        version = img_file.version
        
        # Check sector alignment for appropriate versions
        if version in [IMGVersion.VERSION_2, IMGVersion.VERSION_3, IMGVersion.FASTMAN92]:
            for entry in img_file.entries:
                if entry.offset % 2048 != 0:
                    result.add_warning(f"Entry '{entry.name}' not sector-aligned (offset: {entry.offset})")
        
        # Check for reasonable entry distribution
        if img_file.entries:
            max_offset = max(entry.offset + entry.size for entry in img_file.entries)
            file_size = os.path.getsize(img_file.file_path)
            
            if max_offset < file_size * 0.5:
                result.add_info("IMG file has significant unused space at the end")
            elif max_offset > file_size:
                result.add_error("Entry data extends beyond file size")
    
    @staticmethod
    def validate_img_entry(entry: IMGEntry, img_file: Optional[IMGFile] = None) -> ValidationResult:
        """Validate a single IMG entry"""
        result = ValidationResult()
        
        if not entry:
            result.add_error("Entry is None")
            return result
        
        # Name validation
        if not entry.name:
            result.add_error("Entry name is empty")
        elif len(entry.name) > 24:  # Standard IMG name limit
            result.add_warning(f"Entry name is long ({len(entry.name)} chars): {entry.name}")
        
        # Check for invalid characters in name
        invalid_chars = '<>:"|?*'
        if any(char in entry.name for char in invalid_chars):
            result.add_error(f"Entry name contains invalid characters: {entry.name}")
        
        # Size validation
        if entry.size == 0:
            result.add_warning("Entry has zero size")
        elif entry.size < 0:
            result.add_error("Entry has negative size")
        
        # Extension-specific validation
        if entry.extension:
            max_size_mb = IMGValidator.MAX_FILE_SIZES.get(entry.extension, 200)  # Default 200MB
            if entry.size > max_size_mb * 1024 * 1024:
                result.add_warning(f"Entry size ({entry.size / (1024*1024):.1f}MB) is unusually large for {entry.extension} file")
        
        # Offset validation
        if entry.offset < 0:
            result.add_error("Entry has negative offset")
        
        # Compression validation
        if entry.is_compressed:
            if entry.uncompressed_size > 0 and entry.uncompressed_size < entry.size:
                result.add_warning("Compressed entry has uncompressed size smaller than compressed size")
        
        # File format validation (if data is accessible)
        if img_file and entry.can_be_read():
            try:
                data = entry.get_data()
                format_result = IMGValidator._validate_entry_format(entry, data)
                result.warnings.extend(format_result.warnings)
                result.errors.extend(format_result.errors)
                if not format_result.is_valid:
                    result.is_valid = False
            except Exception as e:
                result.add_warning(f"Could not read entry data for format validation: {str(e)}")
        
        return result
    
    @staticmethod
    def _validate_entry_format(entry: IMGEntry, data: bytes) -> ValidationResult:
        """Validate entry data format"""
        result = ValidationResult()
        
        if not data:
            result.add_warning("Entry data is empty")
            return result
        
        extension = entry.extension
        if not extension:
            return result  # Can't validate unknown formats
        
        # Check file signatures
        signatures = IMGValidator.KNOWN_SIGNATURES.get(extension, [])
        if signatures:
            header = data[:16] if len(data) >= 16 else data
            signature_match = any(header.startswith(sig) for sig in signatures)
            
            if not signature_match:
                result.add_warning(f"File signature doesn't match expected {extension} format")
        
        # Extension-specific validation
        if extension == 'DFF':
            IMGValidator._validate_dff_format(data, result)
        elif extension == 'TXD':
            IMGValidator._validate_txd_format(data, result)
        elif extension == 'COL':
            IMGValidator._validate_col_format(data, result)
        elif extension == 'IFP':
            IMGValidator._validate_ifp_format(data, result)
        
        return result
    
    @staticmethod
    def _validate_dff_format(data: bytes, result: ValidationResult):
        """Validate DFF (model) file format"""
        if len(data) < 12:
            result.add_error("DFF file too small to contain valid header")
            return
        
        try:
            # Read RenderWare chunk header
            chunk_type, chunk_size, version = struct.unpack('<III', data[:12])
            
            # Validate chunk type (should be clump for DFF)
            if chunk_type not in [0x10, 0x0E]:  # Clump or atomic
                result.add_warning(f"Unexpected DFF chunk type: 0x{chunk_type:X}")
            
            # Validate version
            if version == 0:
                result.add_warning("DFF has unknown/zero RenderWare version")
            
            # Check if file size matches chunk size
            if chunk_size + 12 != len(data):
                result.add_warning("DFF chunk size doesn't match file size")
                
        except struct.error:
            result.add_error("Invalid DFF header structure")
    
    @staticmethod
    def _validate_txd_format(data: bytes, result: ValidationResult):
        """Validate TXD (texture) file format"""
        if len(data) < 12:
            result.add_error("TXD file too small to contain valid header")
            return
        
        try:
            # Read RenderWare chunk header
            chunk_type, chunk_size, version = struct.unpack('<III', data[:12])
            
            # Validate chunk type (should be texture dictionary)
            if chunk_type != 0x16:
                result.add_warning(f"Unexpected TXD chunk type: 0x{chunk_type:X}")
            
            # Validate version
            if version == 0:
                result.add_warning("TXD has unknown/zero RenderWare version")
                
        except struct.error:
            result.add_error("Invalid TXD header structure")
    
    @staticmethod
    def _validate_col_format(data: bytes, result: ValidationResult):
        """Validate COL (collision) file format"""
        if len(data) < 4:
            result.add_error("COL file too small to contain valid header")
            return
        
        # Check COL signature
        signature = data[:4]
        if signature not in [b'COL\x01', b'COL\x02', b'COL\x03', b'COL\x04', b'COLL']:
            result.add_warning("COL file doesn't have recognized signature")
        
        # Version-specific validation
        if signature.startswith(b'COL'):
            version = signature[3]
            if version < 1 or version > 4:
                result.add_warning(f"Unusual COL version: {version}")
    
    @staticmethod
    def _validate_ifp_format(data: bytes, result: ValidationResult):
        """Validate IFP (animation) file format"""
        if len(data) < 4:
            result.add_error("IFP file too small to contain valid header")
            return
        
        # Check IFP signature
        if not data.startswith(b'ANPK'):
            result.add_warning("IFP file doesn't start with ANPK signature")
    
    @staticmethod
    def validate_file_for_import(file_path: str) -> ValidationResult:
        """Validate a file before importing into IMG"""
        result = ValidationResult()
        
        if not os.path.exists(file_path):
            result.add_error(f"File does not exist: {file_path}")
            return result
        
        # Basic file checks
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            result.add_error("File is empty")
            return result
        
        if file_size > 500 * 1024 * 1024:  # 500MB
            result.add_warning("File is very large (>500MB)")
        
        # Name validation
        filename = os.path.basename(file_path)
        if len(filename) > 24:
            result.add_warning(f"Filename is long ({len(filename)} chars) and may be truncated")
        
        # Extension validation
        extension = Path(file_path).suffix.upper().lstrip('.')
        if extension:
            # Create dummy entry for format validation
            dummy_entry = IMGEntry(filename, 0, file_size)
            dummy_entry.extension = extension
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read(min(1024, file_size))  # Read first 1KB for validation
                
                format_result = IMGValidator._validate_entry_format(dummy_entry, data)
                result.warnings.extend(format_result.warnings)
                result.errors.extend(format_result.errors)
                if not format_result.is_valid:
                    result.is_valid = False
                    
            except Exception as e:
                result.add_warning(f"Could not read file for format validation: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_img_creation_settings(settings: Dict) -> ValidationResult:
        """Validate settings for IMG creation"""
        result = ValidationResult()
        
        # Required fields
        required_fields = ['output_path', 'img_version', 'initial_size_mb']
        for field in required_fields:
            if field not in settings:
                result.add_error(f"Missing required setting: {field}")
        
        if not result.is_valid:
            return result
        
        # Validate output path
        output_path = settings['output_path']
        output_dir = os.path.dirname(output_path)
        
        if not os.path.exists(output_dir):
            result.add_error(f"Output directory does not exist: {output_dir}")
        
        if os.path.exists(output_path):
            result.add_warning("Output file already exists and will be overwritten")
        
        # Validate filename
        filename = os.path.basename(output_path)
        if not filename.lower().endswith('.img'):
            result.add_warning("Output filename should have .img extension")
        
        # Validate size
        initial_size = settings.get('initial_size_mb', 0)
        if initial_size < 1:
            result.add_error("Initial size must be at least 1 MB")
        elif initial_size > 2048:
            result.add_warning("Initial size is very large (>2GB)")
        
        # Validate version compatibility
        img_version = settings.get('img_version')
        compression_enabled = settings.get('compression_enabled', False)
        encryption_enabled = settings.get('encryption_enabled', False)
        
        if compression_enabled and img_version not in [IMGVersion.VERSION_3, IMGVersion.FASTMAN92]:
            result.add_error(f"Compression not supported for IMG version {img_version}")
        
        if encryption_enabled and img_version != IMGVersion.VERSION_3:
            result.add_error(f"Encryption not supported for IMG version {img_version}")
        
        return result
    
    @staticmethod
    def get_img_health_report(img_file: IMGFile) -> Dict:
        """Generate comprehensive health report for IMG file"""
        validation = IMGValidator.validate_img_file(img_file)
        
        # Collect statistics
        stats = {
            'total_entries': len(img_file.entries),
            'total_size': sum(entry.size for entry in img_file.entries),
            'file_types': {},
            'compression_stats': {
                'compressed_count': 0,
                'uncompressed_count': 0,
                'compression_ratio': 0.0
            },
            'version_info': {
                'version': img_file.version.name,
                'platform': img_file.platform.value,
                'encrypted': img_file.is_encrypted
            }
        }
        
        # Analyze file types
        for entry in img_file.entries:
            ext = entry.extension or 'Unknown'
            stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
            
            if entry.is_compressed:
                stats['compression_stats']['compressed_count'] += 1
            else:
                stats['compression_stats']['uncompressed_count'] += 1
        
        # Calculate compression ratio
        if stats['compression_stats']['compressed_count'] > 0:
            total_compressed_size = sum(
                entry.size for entry in img_file.entries if entry.is_compressed
            )
            total_uncompressed_size = sum(
                entry.uncompressed_size for entry in img_file.entries 
                if entry.is_compressed and entry.uncompressed_size > 0
            )
            
            if total_uncompressed_size > 0:
                stats['compression_stats']['compression_ratio'] = total_compressed_size / total_uncompressed_size
        
        return {
            'validation': validation,
            'statistics': stats,
            'recommendations': IMGValidator._generate_recommendations(img_file, validation, stats)
        }
    
    @staticmethod
    def _generate_recommendations(img_file: IMGFile, validation: ValidationResult, stats: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Size-based recommendations
        if stats['total_size'] > 1024 * 1024 * 1024:  # >1GB
            recommendations.append("Consider splitting large IMG into multiple smaller files")
        
        # Compression recommendations
        compression_stats = stats['compression_stats']
        if compression_stats['uncompressed_count'] > compression_stats['compressed_count'] * 2:
            if img_file.version in [IMGVersion.VERSION_3, IMGVersion.FASTMAN92]:
                recommendations.append("Many uncompressed files detected - consider enabling compression")
        
        # Error-based recommendations
        if validation.errors:
            recommendations.append("Fix validation errors before using this IMG file")
        
        if validation.warnings:
            recommendations.append("Review validation warnings for potential issues")
        
        # File type recommendations
        file_types = stats['file_types']
        if 'Unknown' in file_types and file_types['Unknown'] > 5:
            recommendations.append("Many files with unknown extensions - verify file types")
        
        return recommendations


# Utility functions for integration
def quick_validate_img(file_path: str) -> ValidationResult:
    """Quick validation of IMG file without full loading"""
    result = ValidationResult()
    
    if not os.path.exists(file_path):
        result.add_error(f"File does not exist: {file_path}")
        return result
    
    try:
        # Try to detect version
        version = detect_img_version(file_path)
        if version == IMGVersion.UNKNOWN:
            result.add_error("Unknown or invalid IMG file format")
        else:
            result.add_info(f"Detected IMG version: {version.name}")
    
    except Exception as e:
        result.add_error(f"Failed to analyze file: {str(e)}")
    
    return result


def validate_before_import(file_paths: List[str]) -> Dict[str, ValidationResult]:
    """Validate multiple files before import"""
    results = {}
    
    for file_path in file_paths:
        results[file_path] = IMGValidator.validate_file_for_import(file_path)
    
    return results


# Example usage
if __name__ == "__main__":
    # Test validation system
    print("IMG Validator Test")
    
    # Test file validation
    test_files = ["test.dff", "test.txd", "nonexistent.img"]
    
    for test_file in test_files:
        print(f"\nValidating: {test_file}")
        result = IMGValidator.validate_file_for_import(test_file)
        print(f"Result: {result.get_summary()}")
        if result.warnings or result.errors:
            print(result.get_details())
    
    print("\nValidation tests completed!")
