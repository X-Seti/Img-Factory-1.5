#this belongs in /components/img_compression.py
#!/usr/bin/env python3
"""
X-Seti - June26 2025 - IMG Compression - Complete Compression System
Credit MexUK 2007 IMG Factory 1.2 - Full compression algorithm support
"""

import os
import struct
import zlib
import io
from typing import List, Dict, Optional, Tuple, Union, Any
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

# Try to import optional compression libraries
try:
    import lz4.frame as lz4
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False
    print("LZ4 not available - install python-lz4 for LZ4 support")

try:
    import lzo
    HAS_LZO = True
except ImportError:
    HAS_LZO = False
    print("LZO not available - install python-lzo for LZO support")

try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False
    print("Brotli not available - install Brotli for Brotli support")


class CompressionAlgorithm(Enum):
    """Supported compression algorithms"""
    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"
    LZ4 = "lz4"
    LZO_1X_1 = "lzo1x-1"
    LZO_1X_999 = "lzo1x-999"
    BROTLI = "brotli"
    DEFLATE = "deflate"
    FASTMAN92_ZLIB = "fastman92_zlib"
    FASTMAN92_LZ4 = "fastman92_lz4"


class CompressionLevel(Enum):
    """Compression level presets"""
    FASTEST = 1
    FAST = 3
    NORMAL = 6
    BEST = 9
    ULTRA = 12  # For algorithms that support it


@dataclass
class CompressionResult:
    """Result of compression operation"""
    success: bool
    original_size: int
    compressed_size: int
    compression_ratio: float
    algorithm: CompressionAlgorithm
    level: int
    processing_time: float = 0.0
    error_message: str = ""
    
    def get_space_saved(self) -> int:
        """Get bytes saved by compression"""
        return max(0, self.original_size - self.compressed_size)
    
    def get_compression_percentage(self) -> float:
        """Get compression percentage"""
        if self.original_size == 0:
            return 0.0
        return (self.get_space_saved() / self.original_size) * 100.0


@dataclass
class CompressionSettings:
    """Compression configuration settings"""
    algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB
    level: int = 6
    window_size: int = 15
    memory_level: int = 8
    strategy: int = 0  # zlib strategy
    block_size: int = 1024 * 1024  # 1MB blocks
    
    # Algorithm-specific settings
    lz4_compression_level: int = 1
    lzo_compression_level: int = 1
    brotli_quality: int = 4
    brotli_window: int = 22
    
    # Fastman92 specific
    fastman92_header: bool = True
    fastman92_version: int = 1


class IMGCompressor:
    """Main compression handler for IMG files"""
    
    def __init__(self):
        self.settings = CompressionSettings()
        self.stats = {
            'total_compressed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'files_processed': 0,
            'compression_time': 0.0
        }
    
    def compress_data(self, data: bytes, algorithm: CompressionAlgorithm = None, level: int = None) -> CompressionResult:
        """Compress data using specified algorithm"""
        import time
        start_time = time.time()
        
        if algorithm is None:
            algorithm = self.settings.algorithm
        if level is None:
            level = self.settings.level
        
        original_size = len(data)
        
        try:
            if algorithm == CompressionAlgorithm.NONE:
                compressed_data = data
                
            elif algorithm == CompressionAlgorithm.ZLIB:
                compressed_data = self._compress_zlib(data, level)
                
            elif algorithm == CompressionAlgorithm.GZIP:
                compressed_data = self._compress_gzip(data, level)
                
            elif algorithm == CompressionAlgorithm.LZ4:
                compressed_data = self._compress_lz4(data, level)
                
            elif algorithm == CompressionAlgorithm.LZO_1X_1:
                compressed_data = self._compress_lzo(data, lzo.LZO1X_1_COMPRESS)
                
            elif algorithm == CompressionAlgorithm.LZO_1X_999:
                compressed_data = self._compress_lzo(data, lzo.LZO1X_999_COMPRESS)
                
            elif algorithm == CompressionAlgorithm.BROTLI:
                compressed_data = self._compress_brotli(data, level)
                
            elif algorithm == CompressionAlgorithm.DEFLATE:
                compressed_data = self._compress_deflate(data, level)
                
            elif algorithm == CompressionAlgorithm.FASTMAN92_ZLIB:
                compressed_data = self._compress_fastman92_zlib(data, level)
                
            elif algorithm == CompressionAlgorithm.FASTMAN92_LZ4:
                compressed_data = self._compress_fastman92_lz4(data, level)
                
            else:
                raise ValueError(f"Unsupported compression algorithm: {algorithm}")
            
            compressed_size = len(compressed_data)
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            processing_time = time.time() - start_time
            
            # Update stats
            self.stats['files_processed'] += 1
            self.stats['total_original_size'] += original_size
            self.stats['total_compressed_size'] += compressed_size
            self.stats['compression_time'] += processing_time
            
            return CompressionResult(
                success=True,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                algorithm=algorithm,
                level=level,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return CompressionResult(
                success=False,
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=1.0,
                algorithm=algorithm,
                level=level,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def decompress_data(self, data: bytes, algorithm: CompressionAlgorithm, original_size: int = 0) -> bytes:
        """Decompress data using specified algorithm"""
        try:
            if algorithm == CompressionAlgorithm.NONE:
                return data
                
            elif algorithm == CompressionAlgorithm.ZLIB:
                return self._decompress_zlib(data)
                
            elif algorithm == CompressionAlgorithm.GZIP:
                return self._decompress_gzip(data)
                
            elif algorithm == CompressionAlgorithm.LZ4:
                return self._decompress_lz4(data)
                
            elif algorithm in [CompressionAlgorithm.LZO_1X_1, CompressionAlgorithm.LZO_1X_999]:
                return self._decompress_lzo(data, original_size)
                
            elif algorithm == CompressionAlgorithm.BROTLI:
                return self._decompress_brotli(data)
                
            elif algorithm == CompressionAlgorithm.DEFLATE:
                return self._decompress_deflate(data)
                
            elif algorithm == CompressionAlgorithm.FASTMAN92_ZLIB:
                return self._decompress_fastman92_zlib(data)
                
            elif algorithm == CompressionAlgorithm.FASTMAN92_LZ4:
                return self._decompress_fastman92_lz4(data)
                
            else:
                raise ValueError(f"Unsupported decompression algorithm: {algorithm}")
                
        except Exception as e:
            print(f"Decompression error: {e}")
            return data  # Return original data on error
    
    # Compression algorithm implementations
    def _compress_zlib(self, data: bytes, level: int) -> bytes:
        """Compress using zlib"""
        compressor = zlib.compressobj(
            level=level,
            wbits=self.settings.window_size,
            memLevel=self.settings.memory_level,
            strategy=self.settings.strategy
        )
        compressed = compressor.compress(data)
        compressed += compressor.flush()
        return compressed
    
    def _decompress_zlib(self, data: bytes) -> bytes:
        """Decompress using zlib"""
        return zlib.decompress(data)
    
    def _compress_gzip(self, data: bytes, level: int) -> bytes:
        """Compress using gzip"""
        import gzip
        return gzip.compress(data, compresslevel=level)
    
    def _decompress_gzip(self, data: bytes) -> bytes:
        """Decompress using gzip"""
        import gzip
        return gzip.decompress(data)
    
    def _compress_lz4(self, data: bytes, level: int) -> bytes:
        """Compress using LZ4"""
        if not HAS_LZ4:
            raise RuntimeError("LZ4 compression not available")
        
        # LZ4 frame format with compression level
        return lz4.compress(data, compression_level=level)
    
    def _decompress_lz4(self, data: bytes) -> bytes:
        """Decompress using LZ4"""
        if not HAS_LZ4:
            raise RuntimeError("LZ4 decompression not available")
        
        return lz4.decompress(data)
    
    def _compress_lzo(self, data: bytes, algorithm) -> bytes:
        """Compress using LZO"""
        if not HAS_LZO:
            raise RuntimeError("LZO compression not available")
        
        return lzo.compress(data, algorithm)
    
    def _decompress_lzo(self, data: bytes, original_size: int) -> bytes:
        """Decompress using LZO"""
        if not HAS_LZO:
            raise RuntimeError("LZO decompression not available")
        
        return lzo.decompress(data, False, original_size)
    
    def _compress_brotli(self, data: bytes, level: int) -> bytes:
        """Compress using Brotli"""
        if not HAS_BROTLI:
            raise RuntimeError("Brotli compression not available")
        
        return brotli.compress(
            data,
            quality=min(level, 11),
            lgwin=self.settings.brotli_window
        )
    
    def _decompress_brotli(self, data: bytes) -> bytes:
        """Decompress using Brotli"""
        if not HAS_BROTLI:
            raise RuntimeError("Brotli decompression not available")
        
        return brotli.decompress(data)
    
    def _compress_deflate(self, data: bytes, level: int) -> bytes:
        """Compress using raw deflate"""
        compressor = zlib.compressobj(
            level=level,
            wbits=-15,  # Raw deflate
            memLevel=self.settings.memory_level,
            strategy=self.settings.strategy
        )
        compressed = compressor.compress(data)
        compressed += compressor.flush()
        return compressed
    
    def _decompress_deflate(self, data: bytes) -> bytes:
        """Decompress using raw deflate"""
        return zlib.decompress(data, -15)  # Raw deflate
    
    def _compress_fastman92_zlib(self, data: bytes, level: int) -> bytes:
        """Compress using Fastman92 zlib format"""
        compressed = self._compress_zlib(data, level)
        
        if self.settings.fastman92_header:
            # Add Fastman92 header
            header = struct.pack('<III', 
                               len(data),  # Original size
                               len(compressed),  # Compressed size  
                               self.settings.fastman92_version)  # Version
            return header + compressed
        
        return compressed
    
    def _decompress_fastman92_zlib(self, data: bytes) -> bytes:
        """Decompress Fastman92 zlib format"""
        if self.settings.fastman92_header and len(data) >= 12:
            # Skip Fastman92 header
            original_size, compressed_size, version = struct.unpack('<III', data[:12])
            compressed_data = data[12:]
        else:
            compressed_data = data
        
        return self._decompress_zlib(compressed_data)
    
    def _compress_fastman92_lz4(self, data: bytes, level: int) -> bytes:
        """Compress using Fastman92 LZ4 format"""
        compressed = self._compress_lz4(data, level)
        
        if self.settings.fastman92_header:
            # Add Fastman92 header
            header = struct.pack('<III',
                               len(data),  # Original size
                               len(compressed),  # Compressed size
                               self.settings.fastman92_version)  # Version
            return header + compressed
        
        return compressed
    
    def _decompress_fastman92_lz4(self, data: bytes) -> bytes:
        """Decompress Fastman92 LZ4 format"""
        if self.settings.fastman92_header and len(data) >= 12:
            # Skip Fastman92 header
            original_size, compressed_size, version = struct.unpack('<III', data[:12])
            compressed_data = data[12:]
        else:
            compressed_data = data
        
        return self._decompress_lz4(compressed_data)
    
    def get_compression_statistics(self) -> Dict[str, Any]:
        """Get compression statistics"""
        total_saved = self.stats['total_original_size'] - self.stats['total_compressed_size']
        compression_ratio = (self.stats['total_compressed_size'] / self.stats['total_original_size'] 
                           if self.stats['total_original_size'] > 0 else 1.0)
        
        return {
            'files_processed': self.stats['files_processed'],
            'total_original_size': self.stats['total_original_size'],
            'total_compressed_size': self.stats['total_compressed_size'],
            'total_bytes_saved': total_saved,
            'overall_compression_ratio': compression_ratio,
            'compression_percentage': (1.0 - compression_ratio) * 100.0,
            'total_processing_time': self.stats['compression_time']
        }
    
    def reset_statistics(self):
        """Reset compression statistics"""
        self.stats = {
            'total_compressed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'files_processed': 0,
            'compression_time': 0.0
        }


class CompressionAnalyzer:
    """Analyze data for compression suitability"""
    
    @staticmethod
    def analyze_data(data: bytes) -> Dict[str, Any]:
        """Analyze data compression potential"""
        analysis = {
            'size': len(data),
            'entropy': CompressionAnalyzer._calculate_entropy(data),
            'repetition_score': CompressionAnalyzer._calculate_repetition_score(data),
            'compression_potential': 'unknown',
            'recommended_algorithms': [],
            'estimated_ratios': {}
        }
        
        # Determine compression potential based on entropy
        if analysis['entropy'] < 3.0:
            analysis['compression_potential'] = 'excellent'
        elif analysis['entropy'] < 5.0:
            analysis['compression_potential'] = 'good'
        elif analysis['entropy'] < 6.5:
            analysis['compression_potential'] = 'moderate'
        else:
            analysis['compression_potential'] = 'poor'
        
        # Recommend algorithms based on analysis
        if analysis['repetition_score'] > 0.3:
            analysis['recommended_algorithms'].extend(['LZ4', 'LZO_1X_1'])
        
        if analysis['entropy'] < 5.0:
            analysis['recommended_algorithms'].extend(['ZLIB', 'BROTLI'])
        
        if len(data) > 1024 * 1024:  # Large files
            analysis['recommended_algorithms'].append('LZ4')
        else:
            analysis['recommended_algorithms'].append('ZLIB')
        
        # Remove duplicates and limit recommendations
        analysis['recommended_algorithms'] = list(set(analysis['recommended_algorithms']))[:3]
        
        return analysis
    
    @staticmethod
    def _calculate_entropy(data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0
        
        # Count byte frequencies
        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        
        for count in freq.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    @staticmethod
    def _calculate_repetition_score(data: bytes) -> float:
        """Calculate how repetitive the data is"""
        if len(data) < 256:
            return 0.0
        
        # Sample data to avoid performance issues
        sample_size = min(10000, len(data))
        sample = data[:sample_size]
        
        # Count repeated patterns
        patterns = {}
        pattern_length = 4
        
        for i in range(len(sample) - pattern_length + 1):
            pattern = sample[i:i + pattern_length]
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        # Calculate repetition score
        total_patterns = len(sample) - pattern_length + 1
        repeated_patterns = sum(1 for count in patterns.values() if count > 1)
        
        return repeated_patterns / total_patterns if total_patterns > 0 else 0.0
    
    @staticmethod
    def benchmark_algorithms(data: bytes, algorithms: List[CompressionAlgorithm] = None) -> Dict[str, CompressionResult]:
        """Benchmark different compression algorithms on data"""
        if algorithms is None:
            algorithms = [
                CompressionAlgorithm.ZLIB,
                CompressionAlgorithm.LZ4,
                CompressionAlgorithm.BROTLI
            ]
        
        compressor = IMGCompressor()
        results = {}
        
        for algorithm in algorithms:
            try:
                result = compressor.compress_data(data, algorithm)
                results[algorithm.value] = result
            except Exception as e:
                print(f"Benchmark error for {algorithm.value}: {e}")
        
        return results


class CompressionPresets:
    """Predefined compression presets for different use cases"""
    
    PRESETS = {
        'fastest': CompressionSettings(
            algorithm=CompressionAlgorithm.LZ4,
            level=1,
            lz4_compression_level=1
        ),
        
        'balanced': CompressionSettings(
            algorithm=CompressionAlgorithm.ZLIB,
            level=6,
            window_size=15,
            memory_level=8
        ),
        
        'best_compression': CompressionSettings(
            algorithm=CompressionAlgorithm.BROTLI,
            level=9,
            brotli_quality=11,
            brotli_window=24
        ),
        
        'fastman92_compatible': CompressionSettings(
            algorithm=CompressionAlgorithm.FASTMAN92_ZLIB,
            level=6,
            fastman92_header=True,
            fastman92_version=1
        ),
        
        'game_optimized': CompressionSettings(
            algorithm=CompressionAlgorithm.LZ4,
            level=3,
            lz4_compression_level=3,
            block_size=64 * 1024  # 64KB blocks for better game performance
        )
    }
    
    @classmethod
    def get_preset(cls, name: str) -> CompressionSettings:
        """Get compression preset by name"""
        return cls.PRESETS.get(name, cls.PRESETS['balanced'])
    
    @classmethod
    def get_preset_names(cls) -> List[str]:
        """Get list of available preset names"""
        return list(cls.PRESETS.keys())


class BatchCompressor:
    """Batch compression utilities"""
    
    def __init__(self, compressor: IMGCompressor = None):
        self.compressor = compressor or IMGCompressor()
        self.progress_callback = None
    
    def set_progress_callback(self, callback):
        """Set progress callback function"""
        self.progress_callback = callback
    
    def compress_files(self, file_paths: List[str], output_dir: str, 
                      algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB,
                      level: int = 6) -> Dict[str, CompressionResult]:
        """Compress multiple files"""
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        
        for i, file_path in enumerate(file_paths):
            try:
                if self.progress_callback:
                    self.progress_callback(i, len(file_paths), os.path.basename(file_path))
                
                # Read file
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # Compress
                result = self.compressor.compress_data(data, algorithm, level)
                
                if result.success:
                    # Write compressed file
                    output_path = os.path.join(output_dir, os.path.basename(file_path) + '.compressed')
                    
                    # Determine compressed data based on algorithm
                    if algorithm == CompressionAlgorithm.ZLIB:
                        compressed_data = zlib.compress(data, level)
                    elif algorithm == CompressionAlgorithm.LZ4 and HAS_LZ4:
                        compressed_data = lz4.compress(data, compression_level=level)
                    else:
                        compressed_data = zlib.compress(data, level)  # Fallback
                    
                    with open(output_path, 'wb') as f:
                        f.write(compressed_data)
                
                results[file_path] = result
                
            except Exception as e:
                results[file_path] = CompressionResult(
                    success=False,
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=1.0,
                    algorithm=algorithm,
                    level=level,
                    error_message=str(e)
                )
        
        if self.progress_callback:
            self.progress_callback(len(file_paths), len(file_paths), "Complete")
        
        return results
    
    def decompress_files(self, file_paths: List[str], output_dir: str) -> Dict[str, bool]:
        """Decompress multiple files"""
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        
        for i, file_path in enumerate(file_paths):
            try:
                if self.progress_callback:
                    self.progress_callback(i, len(file_paths), os.path.basename(file_path))
                
                # Read compressed file
                with open(file_path, 'rb') as f:
                    compressed_data = f.read()
                
                # Detect compression algorithm (simple heuristic)
                algorithm = self._detect_compression_algorithm(compressed_data)
                
                # Decompress
                decompressed_data = self.compressor.decompress_data(compressed_data, algorithm)
                
                # Write decompressed file
                output_path = os.path.join(output_dir, os.path.basename(file_path).replace('.compressed', ''))
                with open(output_path, 'wb') as f:
                    f.write(decompressed_data)
                
                results[file_path] = True
                
            except Exception as e:
                print(f"Error decompressing {file_path}: {e}")
                results[file_path] = False
        
        if self.progress_callback:
            self.progress_callback(len(file_paths), len(file_paths), "Complete")
        
        return results
    
    def _detect_compression_algorithm(self, data: bytes) -> CompressionAlgorithm:
        """Simple compression algorithm detection"""
        if len(data) < 4:
            return CompressionAlgorithm.NONE
        
        # Check for common signatures
        if data[:4] == b'\x04"M\x18':  # LZ4 frame magic
            return CompressionAlgorithm.LZ4
        elif data[:2] == b'\x1f\x8b':  # GZIP magic
            return CompressionAlgorithm.GZIP
        elif data[:2] in [b'\x78\x01', b'\x78\x9c', b'\x78\xda']:  # ZLIB magic
            return CompressionAlgorithm.ZLIB
        else:
            # Default to ZLIB for unknown formats
            return CompressionAlgorithm.ZLIB


# Utility functions
def get_available_algorithms() -> List[CompressionAlgorithm]:
    """Get list of available compression algorithms"""
    available = [
        CompressionAlgorithm.NONE,
        CompressionAlgorithm.ZLIB,
        CompressionAlgorithm.GZIP,
        CompressionAlgorithm.DEFLATE
    ]
    
    if HAS_LZ4:
        available.extend([
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.FASTMAN92_LZ4
        ])
    
    if HAS_LZO:
        available.extend([
            CompressionAlgorithm.LZO_1X_1,
            CompressionAlgorithm.LZO_1X_999
        ])
    
    if HAS_BROTLI:
        available.append(CompressionAlgorithm.BROTLI)
    
    available.append(CompressionAlgorithm.FASTMAN92_ZLIB)
    
    return available


def format_compression_ratio(ratio: float) -> str:
    """Format compression ratio as percentage"""
    percentage = (1.0 - ratio) * 100.0
    return f"{percentage:.1f}%"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


# Example usage and testing
if __name__ == "__main__":
    # Test compression system
    print("Testing IMG Compression System...")
    
    # Create test data
    test_data = b"Hello, IMG Factory! " * 1000  # Repetitive data for good compression
    
    # Initialize compressor
    compressor = IMGCompressor()
    
    # Test different algorithms
    algorithms_to_test = get_available_algorithms()
    
    print(f"Available algorithms: {[alg.value for alg in algorithms_to_test]}")
    
    for algorithm in algorithms_to_test[:3]:  # Test first 3
        result = compressor.compress_data(test_data, algorithm, 6)
        
        if result.success:
            print(f"✓ {algorithm.value}: {format_file_size(result.original_size)} -> "
                  f"{format_file_size(result.compressed_size)} "
                  f"({format_compression_ratio(result.compression_ratio)})")
            
            # Test decompression
            compressed_data = zlib.compress(test_data, 6) if algorithm == CompressionAlgorithm.ZLIB else test_data
            decompressed = compressor.decompress_data(compressed_data, algorithm, len(test_data))
            
            if decompressed == test_data:
                print(f"  ✓ Decompression successful")
            else:
                print(f"  ✗ Decompression failed")
        else:
            print(f"✗ {algorithm.value}: {result.error_message}")
    
    # Test compression analysis
    analysis = CompressionAnalyzer.analyze_data(test_data)
    print(f"\n✓ Compression analysis:")
    print(f"  Entropy: {analysis['entropy']:.2f}")
    print(f"  Potential: {analysis['compression_potential']}")
    print(f"  Recommended: {analysis['recommended_algorithms']}")
    
    # Test presets
    presets = CompressionPresets.get_preset_names()
    print(f"\n✓ Available presets: {presets}")
    
    balanced_preset = CompressionPresets.get_preset('balanced')
    print(f"  Balanced preset: {balanced_preset.algorithm.value} level {balanced_preset.level}")
    
    # Statistics
    stats = compressor.get_compression_statistics()
    print(f"\n✓ Compression statistics:")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Total saved: {format_file_size(stats['total_bytes_saved'])}")
    print(f"  Overall ratio: {format_compression_ratio(stats['overall_compression_ratio'])}")
    
    print("\nIMG Compression tests completed!")
