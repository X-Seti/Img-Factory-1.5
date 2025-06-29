#!/usr/bin/env python3

"""
X-Seti - June29 2025 - IMG Manager - High-Level Operations
Credit MexUK 2007 IMG Factory 1.2 - High-level management operations only
"""

#this belongs in /components/img_manager.py - version 33

import os
import zlib
import hashlib
from typing import List, Dict
from components.img_core_classes import (
    IMGFile, IMGEntry, IMGVersion, Platform,
    CompressionType, FileType, IMGValidationResult,
    format_file_size, detect_img_version
)


def create_img_from_directory(directory_path: str, output_path: str, version: IMGVersion = IMGVersion.VERSION_2, **kwargs) -> bool:
    """Create IMG file from directory contents"""
    try:
        img = IMGFile()
        if not img.create_new(output_path, version, **kwargs):
            return False

        success_count, error_count = img.import_directory(directory_path)

        if success_count > 0:
            return img.rebuild()

        return error_count == 0

    except Exception as e:
        print(f"Error creating IMG from directory: {e}")
        return False


def merge_img_files(img_paths: List[str], output_path: str, version: IMGVersion = IMGVersion.VERSION_2) -> bool:
    """Merge multiple IMG files into one"""
    try:
        merged_img = IMGFile()
        if not merged_img.create_new(output_path, version):
            return False

        for img_path in img_paths:
            source_img = IMGFile(img_path)
            if source_img.open():
                for entry in source_img.entries:
                    # Check for duplicates
                    if not merged_img.find_entry(entry.name):
                        data = entry.get_data()
                        merged_img.add_entry(entry.name, data)
                source_img.close()

        return merged_img.rebuild()

    except Exception as e:
        print(f"Error merging IMG files: {e}")
        return False


class IMGAnalyzer:
    """Advanced IMG file analysis tools"""
    
    @staticmethod
    def analyze_corruption(img_file: IMGFile) -> Dict:
        """Analyze IMG file for corruption"""
        analysis = {
            'corrupt_entries': [],
            'suspicious_entries': [],
            'missing_data': [],
            'size_mismatches': [],
            'offset_errors': []
        }
        
        for entry in img_file.entries:
            try:
                # Check if data can be read
                data = entry.get_data()
                
                # Check size consistency
                if len(data) != entry.size:
                    analysis['size_mismatches'].append({
                        'name': entry.name,
                        'expected': entry.size,
                        'actual': len(data)
                    })
                
                # Check for suspicious patterns
                if len(set(data[:min(1024, len(data))])) == 1:  # All same byte
                    analysis['suspicious_entries'].append({
                        'name': entry.name,
                        'reason': 'Uniform data pattern'
                    })
                
            except Exception as e:
                analysis['corrupt_entries'].append({
                    'name': entry.name,
                    'error': str(e)
                })
        
        return analysis
    
    @staticmethod
    def find_duplicates(img_file: IMGFile) -> Dict[str, List[str]]:
        """Find duplicate files by content hash"""
        hash_map = {}
        duplicates = {}
        
        for entry in img_file.entries:
            try:
                data = entry.get_data()
                file_hash = hashlib.md5(data).hexdigest()
                
                if file_hash in hash_map:
                    if file_hash not in duplicates:
                        duplicates[file_hash] = [hash_map[file_hash]]
                    duplicates[file_hash].append(entry.name)
                else:
                    hash_map[file_hash] = entry.name
                    
            except Exception:
                continue
        
        return duplicates
    
    @staticmethod
    def get_compression_ratio_analysis(img_file: IMGFile) -> Dict:
        """Analyze compression ratios for entries"""
        analysis = {
            'compressible_entries': [],
            'already_compressed': [],
            'potential_savings': 0
        }
        
        for entry in img_file.entries:
            try:
                if entry.is_compressed:
                    ratio = (entry.uncompressed_size - entry.size) / entry.uncompressed_size * 100
                    analysis['already_compressed'].append({
                        'name': entry.name,
                        'ratio': ratio,
                        'savings': entry.uncompressed_size - entry.size
                    })
                else:
                    # Test compression
                    data = entry.get_data()
                    compressed = zlib.compress(data, 6)
                    if len(compressed) < len(data):
                        savings = len(data) - len(compressed)
                        ratio = savings / len(data) * 100
                        analysis['compressible_entries'].append({
                            'name': entry.name,
                            'ratio': ratio,
                            'savings': savings
                        })
                        analysis['potential_savings'] += savings
                        
            except Exception:
                continue
        
        return analysis


# Example usage and testing
if __name__ == "__main__":
    # Test basic functionality
    print("Testing IMG Manager...")
    
    # Test version detection
    test_files = ["test_v1.img", "test_v2.img", "test_v3.img"]
    for test_file in test_files:
        if os.path.exists(test_file):
            version = detect_img_version(test_file)
            print(f"{test_file}: {version.name}")
    
    # Test creating new IMG
    img = IMGFile()
    if img.create_new("test_new.img", IMGVersion.VERSION_2, initial_size_mb=5):
        print("✓ Created new IMG file")
        
        # Add test entry
        test_data = b"Hello, IMG Factory! This is test data for the new IMG system."
        entry = img.add_entry("test.txt", test_data)
        print(f"✓ Added entry: {entry.name} ({entry.size} bytes)")
        
        # Test rebuild
        if img.rebuild():
            print("✓ Rebuilt IMG file")
        
        # Test validation
        validation = img.validate()
        print(f"✓ Validation: {validation.get_summary()}")
        
        # Test statistics
        stats = img.get_statistics()
        print(f"✓ Statistics: {stats['total_entries']} entries, {stats['total_size_formatted']}")
        
        img.close()
        
        # Clean up
        if os.path.exists("test_new.img"):
            os.remove("test_new.img")
    
    print("IMG Manager tests completed!")
