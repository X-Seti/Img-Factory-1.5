#!/usr/bin/env python3

"""
 X-Seti - June03 - 2019-25 G-IMGTool v2 for ARM64/x86/x64
 Pure Bash Implementation, Handles RenderWare IMG format

 IMG File Structure:
- Header: 8 bytes
  - Signature: "VER2" (4 bytes)
  - Entry count: uint32 (4 bytes)
- Directory: 32 bytes per entry
  - Offset: uint32 (4 bytes) - in 2048-byte sectors
  - Size: uint32 (4 bytes) - in bytes
  - Filename: 24 bytes (null-terminated)
- Data: File contents, aligned to 2048-byte boundaries
"""

import os
import sys
import struct
import shutil
import tempfile
import argparse
import fnmatch
from pathlib import Path
from typing import List, Tuple, Optional
import time

VERSION = "2.0.0"
SECTOR_SIZE = 2048

class IMGTool:
    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='imgtool_')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def detect_img_format(self, img_file: str) -> str:
        """Detect IMG format version (VER1 or VER2)"""
        if not os.path.isfile(img_file):
            return "INVALID"

        try:
            with open(img_file, 'rb') as f:
                # Check for VER2 signature
                signature = f.read(4)
                if signature == b'VER2':
                    return "VER2"

                # For VER1, do heuristic checks
                file_size = os.path.getsize(img_file)
                if file_size < 32:
                    return "INVALID"

                # VER1 starts directly with directory entries
                f.seek(0)
                first_offset = struct.unpack('<I', f.read(4))[0]
                first_size = struct.unpack('<I', f.read(4))[0]

                # Basic sanity checks for VER1
                if first_offset > 0 and first_size > 0 and first_size < file_size:
                    return "VER1"

        except (IOError, struct.error):
            pass

        return "INVALID"

    def get_entry_count(self, img_file: str, format_type: str) -> int:
        """Get number of entries in IMG file"""
        with open(img_file, 'rb') as f:
            if format_type == "VER2":
                f.seek(4)
                return struct.unpack('<I', f.read(4))[0]
            elif format_type == "VER1":
                # Calculate entry count for VER1
                file_size = os.path.getsize(img_file)
                entry_count = 0
                offset = 0

                while offset < file_size:
                    f.seek(offset)
                    try:
                        file_offset = struct.unpack('<I', f.read(4))[0]
                        file_size_entry = struct.unpack('<I', f.read(4))[0]

                        if file_offset == 0 and file_size_entry == 0:
                            break

                        if file_offset > 0 and file_size_entry > 0:
                            entry_count += 1
                            offset += 32
                        else:
                            break

                        # Safety check
                        if entry_count > 10000:
                            break

                    except struct.error:
                        break

                return entry_count
        return 0

    def extract_img(self, img_file: str, output_dir: str) -> bool:
        """Extract all files from IMG archive"""
        if not os.path.isfile(img_file):
            print(f"Error: IMG file not found: {img_file}", file=sys.stderr)
            return False

        os.makedirs(output_dir, exist_ok=True)

        # Detect format
        format_type = self.detect_img_format(img_file)
        if format_type == "INVALID":
            print("Error: Invalid or unsupported IMG file format", file=sys.stderr)
            return False

        print(f"Detected format: {format_type}")

        entry_count = self.get_entry_count(img_file, format_type)
        dir_start = 8 if format_type == "VER2" else 0

        print(f"Extracting {entry_count} files from {img_file}")

        with open(img_file, 'rb') as f:
            for i in range(entry_count):
                dir_offset = dir_start + i * 32
                f.seek(dir_offset)

                try:
                    file_offset = struct.unpack('<I', f.read(4))[0]
                    file_size = struct.unpack('<I', f.read(4))[0]
                    #filename = f.read(24).rstrip(b'\x00').decode('ascii', errors='ignore')

                    filename_bytes = f.read(24)
                    # Take everything up to first null byte, strip whitespace
                    filename = filename_bytes.split(b'\x00')[0].strip().decode('ascii', errors='ignore')


                    # Skip empty entries
                    if not filename or file_size == 0:
                        continue

                    # Calculate byte offset
                    byte_offset = file_offset * SECTOR_SIZE

                    print(f"Extracting: {filename} (size: {file_size} bytes)")

                    # Extract file
                    f.seek(byte_offset)
                    file_data = f.read(file_size)

                    output_path = os.path.join(output_dir, filename)
                    with open(output_path, 'wb') as out_f:
                        out_f.write(file_data)

                except (struct.error, IOError) as e:
                    print(f"Error extracting file {i}: {e}", file=sys.stderr)
                    continue

        print("Extraction complete!")
        return True

    def create_img(self, format_type: str, img_file: str, input_dir: str) -> bool:
        """Create IMG file from directory"""
        if not os.path.isdir(input_dir):
            print(f"Error: Input directory not found: {input_dir}", file=sys.stderr)
            return False

        # Validate format
        format_type = format_type.upper()
        if format_type not in ["VER1", "VER2"]:
            print(f"Error: Invalid format '{format_type}'. Use 'ver1' or 'ver2'", file=sys.stderr)
            return False

        # Get list of files
        files = sorted([f for f in os.listdir(input_dir)
                       if os.path.isfile(os.path.join(input_dir, f))])

        if not files:
            print(f"Error: No files found in directory: {input_dir}", file=sys.stderr)
            return False

        print(f"Creating {format_type} IMG with {len(files)} files")

        # Calculate sizes
        header_size = 8 if format_type == "VER2" else 0
        dir_size = header_size + len(files) * 32
        data_start_sector = (dir_size + SECTOR_SIZE - 1) // SECTOR_SIZE

        with open(img_file, 'wb') as f:
            # Write header (VER2 only)
            if format_type == "VER2":
                f.write(b'VER2')
                f.write(struct.pack('<I', len(files)))

            # Pad to directory size
            f.write(b'\x00' * (dir_size - header_size))

            # Calculate file positions and write directory
            current_sector = data_start_sector
            file_info = []

            for i, filename in enumerate(files):
                filepath = os.path.join(input_dir, filename)
                filesize = os.path.getsize(filepath)

                # Check filename length
                if len(filename) > 24:
                    print(f"Warning: Filename '{filename}' exceeds 24 characters, truncating")
                    filename = filename[:24]

                sectors_needed = (filesize + SECTOR_SIZE - 1) // SECTOR_SIZE

                # Write directory entry
                dir_offset = (8 if format_type == "VER2" else 0) + i * 32
                f.seek(dir_offset)
                f.write(struct.pack('<I', current_sector))
                f.write(struct.pack('<I', filesize))
                f.write(filename.encode('ascii')[:24].ljust(24, b'\x00'))

                file_info.append((filepath, filesize, current_sector))
                print(f"Added: {filename} (sector: {current_sector}, size: {filesize})")
                current_sector += sectors_needed

            # Pad to data section
            data_start_byte = data_start_sector * SECTOR_SIZE
            f.seek(data_start_byte)

            # Write file data
            for filepath, filesize, sector in file_info:
                with open(filepath, 'rb') as src_f:
                    data = src_f.read()
                    f.write(data)

                    # Pad to sector boundary
                    padding = SECTOR_SIZE - (filesize % SECTOR_SIZE)
                    if padding != SECTOR_SIZE:
                        f.write(b'\x00' * padding)

        print(f"{format_type} IMG file created: {img_file}")
        return True

    def add_multiple_to_img(self, img_file: str, files_to_add: List[str]) -> bool:
        """Add multiple files to existing IMG"""
        if not files_to_add:
            print("Error: No files specified to add", file=sys.stderr)
            return False

        # Detect format
        format_type = self.detect_img_format(img_file)
        if format_type == "INVALID":
            print("Error: Invalid or unsupported IMG file format", file=sys.stderr)
            return False

        work_dir = os.path.join(self.temp_dir, 'img_work')

        # Extract existing IMG
        print("Extracting existing IMG...")
        if not self.extract_img(img_file, work_dir):
            return False

        # Add new files
        added_count = 0
        for file_path in files_to_add:
            if os.path.isfile(file_path):
                basename = os.path.basename(file_path)
                shutil.copy2(file_path, os.path.join(work_dir, basename))
                print(f"Added: {basename}")
                added_count += 1
            else:
                print(f"Warning: File not found: {file_path}")

        if added_count == 0:
            print("Error: No valid files were added", file=sys.stderr)
            return False

        # Rebuild IMG with same format
        print("Rebuilding IMG...")
        format_param = format_type.lower()
        if self.create_img(format_param, img_file, work_dir):
            print(f"Successfully added {added_count} file(s) to {img_file}")
            return True
        return False

    def remove_multiple_from_img(self, img_file: str, files_to_remove: List[str]) -> bool:
        """Remove multiple files from IMG"""
        if not files_to_remove:
            print("Error: No files specified to remove", file=sys.stderr)
            return False

        # Detect format
        format_type = self.detect_img_format(img_file)
        if format_type == "INVALID":
            print("Error: Invalid or unsupported IMG file format", file=sys.stderr)
            return False

        work_dir = os.path.join(self.temp_dir, 'img_work')

        # Extract existing IMG
        print("Extracting existing IMG...")
        if not self.extract_img(img_file, work_dir):
            return False

        # Remove files
        removed_count = 0
        for pattern in files_to_remove:
            # Handle wildcards
            matching_files = []
            for filename in os.listdir(work_dir):
                if fnmatch.fnmatch(filename, pattern):
                    matching_files.append(filename)

            if matching_files:
                for filename in matching_files:
                    filepath = os.path.join(work_dir, filename)
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                        print(f"Removed: {filename}")
                        removed_count += 1
            else:
                print(f"Warning: File not found: {pattern}")

        if removed_count == 0:
            print("Error: No files were removed", file=sys.stderr)
            return False

        # Rebuild IMG with same format
        print("Rebuilding IMG...")
        format_param = format_type.lower()
        if self.create_img(format_param, img_file, work_dir):
            print(f"Successfully removed {removed_count} file(s) from {img_file}")
            return True
        return False

    def rename_in_img(self, img_file: str, old_name: str, new_name: str) -> bool:
        """Rename file in IMG"""
        if not old_name or not new_name:
            print("Error: Both old and new filenames must be specified", file=sys.stderr)
            return False

        # Check new filename length
        if len(new_name) > 24:
            print("Error: New filename exceeds 24 character limit", file=sys.stderr)
            return False

        # Detect format
        format_type = self.detect_img_format(img_file)
        if format_type == "INVALID":
            print("Error: Invalid or unsupported IMG file format", file=sys.stderr)
            return False

        work_dir = os.path.join(self.temp_dir, 'img_work')

        # Extract existing IMG
        print("Extracting existing IMG...")
        if not self.extract_img(img_file, work_dir):
            return False

        old_path = os.path.join(work_dir, old_name)
        new_path = os.path.join(work_dir, new_name)

        # Check if old file exists
        if not os.path.isfile(old_path):
            print(f"Error: File '{old_name}' not found in archive", file=sys.stderr)
            return False

        # Check if new name already exists
        if os.path.isfile(new_path):
            print(f"Error: File '{new_name}' already exists in archive", file=sys.stderr)
            return False

        # Rename file
        os.rename(old_path, new_path)
        print(f"Renamed: {old_name} -> {new_name}")

        # Rebuild IMG with same format
        print("Rebuilding IMG...")
        format_param = format_type.lower()
        if self.create_img(format_param, img_file, work_dir):
            print(f"Successfully renamed file in {img_file}")
            return True
        return False

    def rebuild_img(self, img_file: str) -> bool:
        """Rebuild/optimize IMG file"""
        # Detect format
        format_type = self.detect_img_format(img_file)
        if format_type == "INVALID":
            print("Error: Invalid or unsupported IMG file format", file=sys.stderr)
            return False

        print(f"Rebuilding {img_file} (format: {format_type})...")

        work_dir = os.path.join(self.temp_dir, 'img_work')
        backup_file = f"{img_file}.backup.{int(time.time())}"

        # Create backup
        shutil.copy2(img_file, backup_file)
        print(f"Backup created: {backup_file}")

        # Extract existing IMG
        if not self.extract_img(img_file, work_dir):
            return False

        # Get original size
        old_size = os.path.getsize(backup_file)

        # Rebuild IMG with same format
        format_param = format_type.lower()
        if not self.create_img(format_param, img_file, work_dir):
            return False

        # Show size comparison
        new_size = os.path.getsize(img_file)
        saved_bytes = old_size - new_size

        print("Rebuild complete!")
        print(f"Original size: {old_size} bytes")
        print(f"New size: {new_size} bytes")
        if saved_bytes > 0:
            print(f"Space saved: {saved_bytes} bytes")
        elif saved_bytes < 0:
            print(f"Size increased: {-saved_bytes} bytes")
        else:
            print("Size unchanged")

        return True

    def list_img_filtered(self, img_file: str, filter_pattern: Optional[str] = None) -> bool:
        """List contents of IMG file with optional filtering"""
        if not os.path.isfile(img_file):
            print(f"Error: IMG file not found: {img_file}", file=sys.stderr)
            return False

        # Detect format
        format_type = self.detect_img_format(img_file)
        if format_type == "INVALID":
            print("Error: Invalid or unsupported IMG file format", file=sys.stderr)
            return False

        entry_count = self.get_entry_count(img_file, format_type)
        dir_start = 8 if format_type == "VER2" else 0

        print(f"IMG File: {img_file} (Format: {format_type})")
        print(f"Files: {entry_count}")
        if filter_pattern:
            print(f"Filter: {filter_pattern}")
        print("-" * 40)
        print(f"{'Filename':<24} {'Size':>10} {'Sector':>10}")
        print("-" * 40)

        displayed_count = 0

        with open(img_file, 'rb') as f:
            for i in range(entry_count):
                dir_offset = dir_start + i * 32
                f.seek(dir_offset)

                try:
                    file_offset = struct.unpack('<I', f.read(4))[0]
                    file_size = struct.unpack('<I', f.read(4))[0]
                    filename = f.read(24).rstrip(b'\x00').decode('ascii', errors='ignore')

                    # Skip empty entries
                    if not filename or file_size == 0:
                        continue

                    # Apply filter if specified
                    if filter_pattern and not fnmatch.fnmatch(filename, filter_pattern):
                        continue

                    print(f"{filename:<24} {file_size:>10} {file_offset:>10}")
                    displayed_count += 1

                except (struct.error, UnicodeDecodeError):
                    continue

        if filter_pattern:
            print("-" * 40)
            print(f"Displayed: {displayed_count} files (filtered)")

        return True

    def info_img(self, img_file: str) -> bool:
        """Show detailed information about IMG file"""
        if not os.path.isfile(img_file):
            print(f"Error: IMG file not found: {img_file}", file=sys.stderr)
            return False

        file_size = os.path.getsize(img_file)
        format_type = self.detect_img_format(img_file)

        print("IMG File Information")
        print("=" * 20)
        print(f"File: {img_file}")
        print(f"Size: {file_size} bytes ({file_size // 1024} KB)")
        print(f"Format: {format_type}")

        if format_type == "INVALID":
            print("Status: Invalid or unsupported format")
            return False

        entry_count = self.get_entry_count(img_file, format_type)
        header_size = 8 if format_type == "VER2" else 0

        dir_size = header_size + entry_count * 32
        data_start_sector = (dir_size + SECTOR_SIZE - 1) // SECTOR_SIZE
        data_start_byte = data_start_sector * SECTOR_SIZE

        print("Status: Valid")
        print(f"Entries: {entry_count}")
        print(f"Header size: {header_size} bytes")
        print(f"Directory size: {dir_size} bytes")
        print(f"Data starts at: sector {data_start_sector} (byte {data_start_byte})")

        # Calculate total data size
        total_data_size = 0
        dir_start = header_size

        with open(img_file, 'rb') as f:
            for i in range(entry_count):
                dir_offset = dir_start + i * 32 + 4  # Skip offset, read size
                f.seek(dir_offset)
                try:
                    file_size = struct.unpack('<I', f.read(4))[0]
                    total_data_size += file_size
                except struct.error:
                    continue

        print(f"Total data size: {total_data_size} bytes")
        print(f"Overhead: {file_size - total_data_size} bytes")
        if file_size > 0:
            print(f"Efficiency: {(total_data_size * 100) // file_size}%")

        return True


def main():
    parser = argparse.ArgumentParser(
        description=' X-Seti - June03 - 2019-25 G-IMGTool v2 for ARM64/x86/x64 \n Pure Bash Implementation, Handles RenderWare IMG format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -e models.img ./extracted/
  %(prog)s -c ver2 custom.img ./my_models/
  %(prog)s -a models.img car1.dff car2.dff texture.txd
  %(prog)s -d models.img old_car.dff unused.txd
  %(prog)s -r models.img oldname.dff newname.dff
  %(prog)s -l textures.img "*.txd"
  %(prog)s -R models.img
        """
    )

    parser.add_argument('--version', '-v', action='version',
                       version=f'G-IMGTool version {VERSION}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Extract command
    extract_parser = subparsers.add_parser('extract', aliases=['e'],
                                         help='Extract files from IMG')
    extract_parser.add_argument('img_file', help='IMG file to extract from')
    extract_parser.add_argument('output_dir', help='Output directory')

    # Create command
    create_parser = subparsers.add_parser('create', aliases=['c'],
                                        help='Create IMG from directory')
    create_parser.add_argument('format', choices=['ver1', 'ver2'],
                             help='IMG format version')
    create_parser.add_argument('img_file', help='IMG file to create')
    create_parser.add_argument('input_dir', help='Input directory')

    # Add command
    add_parser = subparsers.add_parser('add', aliases=['a'],
                                     help='Add files to IMG')
    add_parser.add_argument('img_file', help='IMG file to modify')
    add_parser.add_argument('files', nargs='+', help='Files to add')

    # Delete command
    del_parser = subparsers.add_parser('del', aliases=['d'],
                                     help='Remove files from IMG')
    del_parser.add_argument('img_file', help='IMG file to modify')
    del_parser.add_argument('files', nargs='+', help='Files to remove')

    # Rename command
    rename_parser = subparsers.add_parser('rename', aliases=['r'],
                                        help='Rename file in IMG')
    rename_parser.add_argument('img_file', help='IMG file to modify')
    rename_parser.add_argument('old_name', help='Current filename')
    rename_parser.add_argument('new_name', help='New filename')

    # Rebuild command
    rebuild_parser = subparsers.add_parser('rebuild', aliases=['R'],
                                         help='Rebuild/optimize IMG')
    rebuild_parser.add_argument('img_file', help='IMG file to rebuild')

    # List command
    list_parser = subparsers.add_parser('list', aliases=['l'],
                                      help='List IMG contents')
    list_parser.add_argument('img_file', help='IMG file to list')
    list_parser.add_argument('filter', nargs='?', help='Filter pattern')

    # Info command
    info_parser = subparsers.add_parser('info', aliases=['i'],
                                      help='Show IMG information')
    info_parser.add_argument('img_file', help='IMG file to analyze')

    # Parse arguments
    args = parser.parse_args()

    # Validate arguments based on command
    if args.extract:
        if len(args.args) != 1:
            parser.error("--extract requires output directory")
        output_dir = args.args[0]
    elif args.create:
        if len(args.args) != 1:
            parser.error("--create requires input directory")
        input_dir = args.args[0]
        format_type = args.create
    elif args.add:
        if len(args.args) < 1:
            parser.error("--add requires at least one file")
        files = args.args
    elif args.delete:
        if len(args.args) < 1:
            parser.error("--del requires at least one file")
        files = args.args
    elif args.rename:
        if len(args.args) != 2:
            parser.error("--rename requires old_name and new_name")
        old_name, new_name = args.args
    elif args.list:
        filter_pattern = args.args[0] if args.args else None


    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    with IMGTool() as tool:
        try:
            if args.command in ['extract', 'e']:
                success = tool.extract_img(args.img_file, args.output_dir)
            elif args.command in ['create', 'c']:
                success = tool.create_img(args.format, args.img_file, args.input_dir)
            elif args.command in ['add', 'a']:
                success = tool.add_multiple_to_img(args.img_file, args.files)
            elif args.command in ['del', 'd']:
                success = tool.remove_multiple_from_img(args.img_file, args.files)
            elif args.command in ['rename', 'r']:
                success = tool.rename_in_img(args.img_file, args.old_name, args.new_name)
            elif args.command in ['rebuild', 'R']:
                success = tool.rebuild_img(args.img_file)
            elif args.command in ['list', 'l']:
                success = tool.list_img_filtered(args.img_file, getattr(args, 'filter', None))
            elif args.command in ['info', 'i']:
                success = tool.info_img(args.img_file)
            else:
                print(f"Unknown command: {args.command}", file=sys.stderr)
                return 2

            return 0 if success else 1

        except KeyboardInterrupt:
            print("\nOperation cancelled by user", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1


if __name__ == '__main__':
    sys.exit(main())
