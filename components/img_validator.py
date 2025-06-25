#this belongs in components/ img_validator.py

#!/usr/bin/env python3
"""
X-Seti - June25 2025 - IMG Factory 1.5
IMG Validator - Simple validation without complex dependencies
"""

import os
import struct
from typing import List, Dict, Optional, Any
from enum import Enum


class ValidationLevel(Enum):
    """Validation issue levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationResult:
    """Results from IMG validation"""
    
    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def add_error(self, message: str):
        """Add error message"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add warning message"""
        self.warnings.append(message)
    
    def add_info(self, message: str):
        """Add info message"""
        self.info.append(message)
    
    def get_summary(self) -> str:
        """Get validation summary"""
        if not self.is_valid:
            return f"Invalid - {len(self.errors)} errors, {len(self.warnings)} warnings"
        elif self.warnings:
            return f"Valid with {len(self.warnings)} warnings"
        else:
            return "Valid"
    
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
        
        return "\n".join(details) if details else "No issues found"


class IMGValidator:
    """Simple IMG file validator"""
    
    # Known file signatures for validation
    KNOWN_SIGNATURES = {
        'DFF': [b'\x10\x00\x00\x00', b'\x0E\x00\x00\x00'],
        'TXD': [b'\x16\x00\x00\x00'],
        'COL': [b'COL\x01', b'COL\x02', b'COL\x03', b'COL\x04', b'COLL'],
        'IFP': [b'ANPK'],
        'SCM': [b'\x03\x00', b'\x04\x00'],
    }
    
    @staticmethod
    def validate_img_file(img_file) -> ValidationResult:
        """Validate an IMG file object"""
        result = ValidationResult()
        
        if not img_file:
            result.add_error("IMG file object is None")
            return result
        
        # Check if file exists
        if not hasattr(img_file, 'file_path') or not img_file.file_path:
            result.add_error("IMG file path not set")
            return result
        
        if not os.path.exists(img_file.file_path):
            result.add_error(f"IMG file does not exist: {img_file.file_path}")
            return result
        
        # Check file size
        try:
            file_size = os.path.getsize(img_file.file_path)
            if file_size == 0:
                result.add_error("IMG file is empty")
                return result
            
            if file_size > 2 * 1024 * 1024 * 1024:  # 2GB
                result.add_warning("IMG file is very large (>2GB)")
            
            result.add_info(f"File size: {IMGValidator._format_size(file_size)}")
            
        except Exception as e:
            result.add_error(f"Cannot read file size: {str(e)}")
            return result
        
        # Check entries if available
        if hasattr(img_file, 'entries') and img_file.entries:
            IMGValidator._validate_entries(img_file.entries, result)
        else:
            result.add_warning("No entries found in IMG file")
        
        # Check version if available
        if hasattr(img_file, 'version'):
            version_name = getattr(img_file.version, 'name', str(img_file.version))
            result.add_info(f"IMG version: {version_name}")
        
        return result
    
    @staticmethod
    def validate_file_for_import(file_path: str) -> ValidationResult:
        """Validate a file for import into IMG"""
        result = ValidationResult()
        
        if not file_path:
            result.add_error("File path is empty")
            return result
        
        if not os.path.exists(file_path):
            result.add_error(f"File does not exist: {file_path}")
            return result
        
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                result.add_error("File is empty")
                return result
            
            if file_size > 100 * 1024 * 1024:  # 100MB
                result.add_warning("Large file (>100MB) - import may take time")
            
            # Check file extension and validate format
            ext = os.path.splitext(file_path)[1].upper().lstrip('.')
            if ext in IMGValidator.KNOWN_SIGNATURES:
                if IMGValidator._validate_file_signature(file_path, ext):
                    result.add_info(f"Valid {ext} file format")
                else:
                    result.add_warning(f"Invalid {ext} file signature")
            else:
                result.add_info(f"Unknown file type: {ext}")
            
            result.add_info(f"File size: {IMGValidator._format_size(file_size)}")
            
        except Exception as e:
            result.add_error(f"Validation failed: {str(e)}")
        
        return result
    
    @staticmethod
    def _validate_entries(entries: List, result: ValidationResult):
        """Validate IMG entries"""
        if not entries:
            return
        
        result.add_info(f"Found {len(entries)} entries")
        
        # Check for duplicate names
        names = []
        for entry in entries:
            if hasattr(entry, 'name') and entry.name:
                if entry.name.lower() in [n.lower() for n in names]:
                    result.add_warning(f"Duplicate entry name: {entry.name}")
                names.append(entry.name)
        
        # Check for suspicious entries
        suspicious_count = 0
        for entry in entries:
            if hasattr(entry, 'size') and entry.size == 0:
                suspicious_count += 1
        
        if suspicious_count > 0:
            result.add_warning(f"{suspicious_count} entries have zero size")
        
        # Statistics
        total_size = sum(getattr(entry, 'size', 0) for entry in entries)
        if total_size > 0:
            result.add_info(f"Total entries size: {IMGValidator._format_size(total_size)}")
    
    @staticmethod
    def _validate_file_signature(file_path: str, expected_type: str) -> bool:
        """Validate file signature"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
                
                if expected_type in IMGValidator.KNOWN_SIGNATURES:
                    signatures = IMGValidator.KNOWN_SIGNATURES[expected_type]
                    for signature in signatures:
                        if header.startswith(signature):
                            return True
                
                return False
                
        except Exception:
            return False
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    @staticmethod
    def quick_validate_img(file_path: str) -> ValidationResult:
        """Quick validation without loading full file"""
        result = ValidationResult()
        
        if not os.path.exists(file_path):
            result.add_error(f"File does not exist: {file_path}")
            return result
        
        try:
            # Check basic file properties
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                result.add_error("File is empty")
                return result
            
            # Try to detect IMG version by header
            with open(file_path, 'rb') as f:
                header = f.read(8)
                
                if len(header) >= 4:
                    if header[:4] == b'VER2':
                        result.add_info("Detected IMG Version 2 (GTA SA)")
                    elif header[:4] in [b'VER3', b'VER4']:
                        result.add_info("Detected IMG Version 3+ (GTA IV)")
                    elif header[:8] == b'38MAFVER':
                        result.add_info("Detected Fastman92 IMG format")
                    else:
                        # Check for Version 1 (look for DIR file)
                        dir_path = file_path.replace('.img', '.dir')
                        if os.path.exists(dir_path):
                            result.add_info("Detected IMG Version 1 (GTA III/VC)")
                        else:
                            result.add_warning("Unknown IMG format")
                else:
                    result.add_error("File too small to be valid IMG")
            
            result.add_info(f"File size: {IMGValidator._format_size(file_size)}")
            
        except Exception as e:
            result.add_error(f"Failed to analyze file: {str(e)}")
        
        return result


# Utility functions
def validate_before_import(file_paths: List[str]) -> Dict[str, ValidationResult]:
    """Validate multiple files before import"""
    results = {}
    
    for file_path in file_paths:
        results[file_path] = IMGValidator.validate_file_for_import(file_path)
    
    return results


def get_file_type_stats(entries: List) -> Dict[str, int]:
    """Get statistics about file types in entries"""
    stats = {}
    
    for entry in entries:
        if hasattr(entry, 'name') and entry.name:
            ext = os.path.splitext(entry.name)[1].upper().lstrip('.')
            if not ext:
                ext = 'Unknown'
            stats[ext] = stats.get(ext, 0) + 1
    
    return stats


# Example usage and testing
if __name__ == "__main__":
    print("IMG Validator Test")
    
    # Test file validation
    test_files = ["test.img", "nonexistent.img"]
    
    for test_file in test_files:
        print(f"\nValidating: {test_file}")
        result = IMGValidator.quick_validate_img(test_file)
        print(f"Result: {result.get_summary()}")
        if result.warnings or result.errors:
            print(result.get_details())
    
    print("\nValidation tests completed!")