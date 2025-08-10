#!/bin/bash
# X-Seti - June03 - 2019-25 G-IMGTool v2 for ARM64/x86/x64
# Pure Bash Implementation, Handles RenderWare IMG format
#
# IMG File Structure:
#- Header: 8 bytes
#  - Signature: "VER2" (4 bytes)
#  - Entry count: uint32 (4 bytes)
#- Directory: 32 bytes per entry
#  - Offset: uint32 (4 bytes) - in 2048-byte sectors
#  - Size: uint32 (4 bytes) - in bytes
#  - Filename: 24 bytes (null-terminated)
#- Data: File contents, aligned to 2048-byte boundaries

#!/bin/bash

# IMG Tool for ARM64 - Pure Bash Implementation
# Handles RenderWare IMG format versions 1 and 2

set -e

SECTOR_SIZE=2048
TEMP_DIR="/tmp/img_$$"
VERSION="2.0.0"

# Global variables for current working IMG
CURRENT_IMG=""
CURRENT_FORMAT=""

# Helper functions
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

show_help() {
    cat << 'EOF'
 X-Seti - June03 - 2019-25 G-IMGTool v2 for ARM64/x86/x64
 Pure Bash Implementation, Handles RenderWare IMG format

SYNOPSIS
    imgtool.sh [COMMAND] [OPTIONS] [ARGUMENTS]
    imgtool.sh --help | -h
    imgtool.sh --info | -i <imgfile>
    imgtool.sh --version | -v
    imgtool.sh --add | -a <img_file> file1 [file2] [file3] ...
    imgtool.sh --del | -d <img_file> file1 [file2] [file3] ...
    imgtool.sh --rename | -r <img_file> <old_filename> <new_filename>
    imgtool.sh --rebuild | -R <img_file>
    imgtool.sh --list | -l <img_file> [directory_list]
    imgtool.sh --create | -c <ver1|ver2> <new_archive.img> [source_directory]
    imgtool.sh --extract | -e <imgfile> <dest folder>

OPTIONS
    -h, --help      Show this help message and exit
    -v, --version   Show version information and exit
    -q, --quiet     Suppress non-error output
    -V, --verbose   Show verbose output


DESCRIPTION
    A pure bash implementation for working with RenderWare IMG archive files,
    supporting both version 1 and version 2 formats commonly used in
    Grand Theft Auto games.

SUPPORTED FORMATS
    VER1 (IMG Format 1):
        - Used in GTA III, Vice City
        - Simple directory structure
        - 32-byte entries (offset, size, filename)

    VER2 (IMG Format 2):
        - Used in GTA San Andreas and later
        - Enhanced format with signature
        - Header + directory + data structure

FILE TYPES
    Commonly supported file extensions:
    - .dff (3D models)
    - .txd (texture dictionaries)
    - .col (collision data)
    - .ipl (item placement)
    - .dat (data files)
    - .ifp (animation files)

EXAMPLES
    # Create a new VER2 IMG from directory
    imgtool.sh -c ver2 my_mod.img ./mod_files/

    # Add multiple models to existing IMG
    imgtool.sh -a models.img car1.dff car2.dff car1.txd car2.txd

    # Remove unwanted files
    imgtool.sh -d models.img old_car.dff temp*.txd

    # Rename a file in the archive
    imgtool.sh -r models.img oldname.dff newname.dff

    # List only texture files
    imgtool.sh -l textures.img "*.txd"

    # Rebuild/optimize an IMG file
    imgtool.sh -R models.img

    # Extract everything
    imgtool.sh extract gta3.img ./extracted_files/

NOTES
    - Always backup your original IMG files before modifying them
    - Filenames are limited to 24 characters (including extension)
    - VER1 format has no signature, VER2 starts with "VER2"
    - Files are stored in 2048-byte aligned sectors
    - Rebuild operation optimizes file layout and removes fragmentation

EXIT STATUS
    0    Success
    1    General error (file not found, invalid format, etc.)
    2    Invalid command line arguments

AUTHOR
    X-Seti - keithvc1972@hotmail.com

EOF
}

show_version() {
    echo "G-IMGTool version $VERSION"
}

# Utility functions
hex_to_dec() {
    printf "%d" "0x$1"
}

dec_to_hex() {
    printf "%08x" "$1"
}

# Read little-endian 32-bit integer from file
read_uint32() {
    local file="$1"
    local offset="$2"

    local bytes=$(dd if="$file" bs=1 skip="$offset" count=4 2>/dev/null | xxd -p)
    # Convert little-endian to big-endian
    local le_bytes="${bytes:6:2}${bytes:4:2}${bytes:2:2}${bytes:0:2}"
    hex_to_dec "$le_bytes"
}

# Write little-endian 32-bit integer to file
write_uint32() {
    local file="$1"
    local offset="$2"
    local value="$3"

    local hex=$(printf "%08x" "$value")
    local le_hex="${hex:6:2}${hex:4:2}${hex:2:2}${hex:0:2}"

    echo -n -e "\\x${le_hex:0:2}\\x${le_hex:2:2}\\x${le_hex:4:2}\\x${le_hex:6:2}" | \
        dd of="$file" bs=1 seek="$offset" count=4 conv=notrunc 2>/dev/null
}

# Detect IMG format version
detect_img_format() {
    local img_file="$1"

    if [ ! -f "$img_file" ]; then
        echo "INVALID"
        return 1
    fi

    # Check if file starts with VER2
    local signature=$(dd if="$img_file" bs=4 count=1 2>/dev/null)
    if [ "$signature" = "VER2" ]; then
        echo "VER2"
        return 0
    fi

    # For VER1, we need to do some heuristic checks
    local file_size=$(stat -c%s "$img_file")
    if [ $file_size -lt 32 ]; then
        echo "INVALID"
        return 1
    fi

    # VER1 starts directly with directory entries
    # Try to read first entry and see if it makes sense
    local first_offset=$(read_uint32 "$img_file" 0)
    local first_size=$(read_uint32 "$img_file" 4)

    # Basic sanity checks for VER1
    if [ $first_offset -gt 0 ] && [ $first_size -gt 0 ] && [ $first_size -lt $file_size ]; then
        echo "VER1"
        return 0
    fi

    echo "INVALID"
    return 1
}

# Get entry count for different formats
get_entry_count() {
    local img_file="$1"
    local format="$2"

    case "$format" in
        "VER2")
            read_uint32 "$img_file" 4
            ;;
        "VER1")
            # For VER1, we need to calculate based on file structure
            # Find where data starts by looking at first valid offset
            local file_size=$(stat -c%s "$img_file")
            local entry_count=0
            local offset=0

            while [ $offset -lt $file_size ]; do
                local file_offset=$(read_uint32 "$img_file" $offset)
                local file_size_entry=$(read_uint32 "$img_file" $((offset + 4)))

                # Check if this looks like a valid entry
                if [ $file_offset -eq 0 ] && [ $file_size_entry -eq 0 ]; then
                    break
                fi

                if [ $file_offset -gt 0 ] && [ $file_size_entry -gt 0 ]; then
                    entry_count=$((entry_count + 1))
                    offset=$((offset + 32))
                else
                    break
                fi

                # Safety check to prevent infinite loop
                if [ $entry_count -gt 10000 ]; then
                    break
                fi
            done

            echo $entry_count
            ;;
    esac
}

# Extract IMG file (supports both formats)
extract_img() {
    local img_file="$1"
    local output_dir="$2"

    if [ ! -f "$img_file" ]; then
        echo "Error: IMG file not found: $img_file" >&2
        return 1
    fi

    mkdir -p "$output_dir"

    # Detect format
    local format=$(detect_img_format "$img_file")
    if [ "$format" = "INVALID" ]; then
        echo "Error: Invalid or unsupported IMG file format" >&2
        return 1
    fi

    echo "Detected format: $format"

    local entry_count=$(get_entry_count "$img_file" "$format")
    local dir_start=0

    case "$format" in
        "VER2")
            dir_start=8
            ;;
        "VER1")
            dir_start=0
            ;;
    esac

    echo "Extracting $entry_count files from $img_file"

    # Read directory entries
    for ((i=0; i<entry_count; i++)); do
        local dir_offset=$((dir_start + i * 32))

        local file_offset=$(read_uint32 "$img_file" $dir_offset)
        local file_size=$(read_uint32 "$img_file" $((dir_offset + 4)))

        # Read filename (24 bytes)
        local filename=$(dd if="$img_file" bs=1 skip=$((dir_offset + 8)) count=24 2>/dev/null | tr -d '\0')

        # Skip empty entries
        if [ -z "$filename" ] || [ $file_size -eq 0 ]; then
            continue
        fi

        # Calculate actual byte offset
        local byte_offset=$((file_offset * SECTOR_SIZE))

        echo "Extracting: $filename (size: $file_size bytes)"

        # Extract file
        dd if="$img_file" bs=1 skip="$byte_offset" count="$file_size" of="$output_dir/$filename" 2>/dev/null
    done

    echo "Extraction complete!"
}

# Create IMG file from directory (supports both formats)
create_img() {
    local format="$1"
    local img_file="$2"
    local input_dir="$3"

    if [ ! -d "$input_dir" ]; then
        echo "Error: Input directory not found: $input_dir" >&2
        return 1
    fi

    # Validate format
    if [ "$format" != "ver1" ] && [ "$format" != "ver2" ] && [ "$format" != "VER1" ] && [ "$format" != "VER2" ]; then
        echo "Error: Invalid format '$format'. Use 'ver1' or 'ver2'" >&2
        return 1
    fi

    # Normalize format
    format=$(echo "$format" | tr '[:lower:]' '[:upper:]')

    # Get list of files
    local files=($(find "$input_dir" -maxdepth 1 -type f -printf "%f\n" | sort))
    local file_count=${#files[@]}

    if [ $file_count -eq 0 ]; then
        echo "Error: No files found in directory: $input_dir" >&2
        return 1
    fi

    echo "Creating $format IMG with $file_count files"

    # Calculate directory size
    local header_size=0
    local dir_start=0

    case "$format" in
        "VER2")
            header_size=8
            dir_start=8
            ;;
        "VER1")
            header_size=0
            dir_start=0
            ;;
    esac

    local dir_size=$((header_size + file_count * 32))
    local data_start_sector=$(( (dir_size + SECTOR_SIZE - 1) / SECTOR_SIZE ))

    # Create temporary file
    local temp_img="$TEMP_DIR/temp.img"
    mkdir -p "$TEMP_DIR"

    # Write header (VER2 only)
    if [ "$format" = "VER2" ]; then
        echo -n "VER2" > "$temp_img"
        write_uint32 "$temp_img" 4 "$file_count"
    else
        > "$temp_img"  # Create empty file for VER1
    fi

    # Pad to directory start if needed
    if [ $header_size -gt 0 ]; then
        dd if=/dev/zero bs=1 count=$((dir_size - header_size)) >> "$temp_img" 2>/dev/null
    fi

    # Write directory entries
    local current_sector=$data_start_sector

    for ((i=0; i<file_count; i++)); do
        local filename="${files[i]}"
        local filepath="$input_dir/$filename"
        local filesize=$(stat -c%s "$filepath")

        # Check filename length
        if [ ${#filename} -gt 24 ]; then
            echo "Warning: Filename '$filename' exceeds 24 characters, truncating"
            filename="${filename:0:24}"
        fi

        # Calculate sectors needed
        local sectors_needed=$(( (filesize + SECTOR_SIZE - 1) / SECTOR_SIZE ))

        # Write directory entry
        local dir_offset=$((dir_start + i * 32))

        # Ensure file is large enough
        local current_size=$(stat -c%s "$temp_img")
        local needed_size=$((dir_offset + 32))
        if [ $current_size -lt $needed_size ]; then
            dd if=/dev/zero bs=1 count=$((needed_size - current_size)) >> "$temp_img" 2>/dev/null
        fi

        write_uint32 "$temp_img" $dir_offset "$current_sector"
        write_uint32 "$temp_img" $((dir_offset + 4)) "$filesize"

        # Write filename (pad to 24 bytes)
        local padded_name=$(printf "%-24s" "$filename" | cut -c1-24)
        echo -n "$padded_name" | dd of="$temp_img" bs=1 seek=$((dir_offset + 8)) count=24 conv=notrunc 2>/dev/null

        echo "Added: $filename (sector: $current_sector, size: $filesize)"
        current_sector=$((current_sector + sectors_needed))
    done

    # Pad to data section
    local current_size=$(stat -c%s "$temp_img")
    local data_start_byte=$((data_start_sector * SECTOR_SIZE))
    local padding_needed=$((data_start_byte - current_size))

    if [ $padding_needed -gt 0 ]; then
        dd if=/dev/zero bs=1 count=$padding_needed >> "$temp_img" 2>/dev/null
    fi

    # Append file data
    for filename in "${files[@]}"; do
        local filepath="$input_dir/$filename"
        local filesize=$(stat -c%s "$filepath")

        # Add file data
        cat "$filepath" >> "$temp_img"

        # Pad to sector boundary
        local padding=$(( SECTOR_SIZE - (filesize % SECTOR_SIZE) ))
        if [ $padding -ne $SECTOR_SIZE ]; then
            dd if=/dev/zero bs=1 count=$padding >> "$temp_img" 2>/dev/null
        fi
    done

    # Move to final location
    mv "$temp_img" "$img_file"
    echo "$format IMG file created: $img_file"
}

# Add multiple files to existing IMG
add_multiple_to_img() {
    local img_file="$1"
    shift
    local files_to_add=("$@")

    if [ ${#files_to_add[@]} -eq 0 ]; then
        echo "Error: No files specified to add" >&2
        return 1
    fi

    # Detect format
    local format=$(detect_img_format "$img_file")
    if [ "$format" = "INVALID" ]; then
        echo "Error: Invalid or unsupported IMG file format" >&2
        return 1
    fi

    local work_dir="$TEMP_DIR/img_work"

    # Extract existing IMG
    echo "Extracting existing IMG..."
    extract_img "$img_file" "$work_dir"

    # Add new files
    local added_count=0
    for file_path in "${files_to_add[@]}"; do
        if [ -f "$file_path" ]; then
            local basename=$(basename "$file_path")
            cp "$file_path" "$work_dir/$basename"
            echo "Added: $basename"
            added_count=$((added_count + 1))
        else
            echo "Warning: File not found: $file_path"
        fi
    done

    if [ $added_count -eq 0 ]; then
        echo "Error: No valid files were added" >&2
        return 1
    fi

    # Rebuild IMG with same format
    echo "Rebuilding IMG..."
    local format_param=$(echo "$format" | tr '[:upper:]' '[:lower:]')
    create_img "$format_param" "$img_file" "$work_dir"

    echo "Successfully added $added_count file(s) to $img_file"
}

# Remove multiple files from IMG
remove_multiple_from_img() {
    local img_file="$1"
    shift
    local files_to_remove=("$@")

    if [ ${#files_to_remove[@]} -eq 0 ]; then
        echo "Error: No files specified to remove" >&2
        return 1
    fi

    # Detect format
    local format=$(detect_img_format "$img_file")
    if [ "$format" = "INVALID" ]; then
        echo "Error: Invalid or unsupported IMG file format" >&2
        return 1
    fi

    local work_dir="$TEMP_DIR/img_work"

    # Extract existing IMG
    echo "Extracting existing IMG..."
    extract_img "$img_file" "$work_dir"

    # Remove files
    local removed_count=0
    for filename in "${files_to_remove[@]}"; do
        # Handle wildcards
        local matching_files=($(find "$work_dir" -maxdepth 1 -name "$filename" -type f -printf "%f\n" 2>/dev/null))

        if [ ${#matching_files[@]} -gt 0 ]; then
            for match in "${matching_files[@]}"; do
                if [ -f "$work_dir/$match" ]; then
                    rm "$work_dir/$match"
                    echo "Removed: $match"
                    removed_count=$((removed_count + 1))
                fi
            done
        else
            echo "Warning: File not found: $filename"
        fi
    done

    if [ $removed_count -eq 0 ]; then
        echo "Error: No files were removed" >&2
        return 1
    fi

    # Rebuild IMG with same format
    echo "Rebuilding IMG..."
    local format_param=$(echo "$format" | tr '[:upper:]' '[:lower:]')
    create_img "$format_param" "$img_file" "$work_dir"

    echo "Successfully removed $removed_count file(s) from $img_file"
}

# Rename file in IMG
rename_in_img() {
    local img_file="$1"
    local old_name="$2"
    local new_name="$3"

    if [ -z "$old_name" ] || [ -z "$new_name" ]; then
        echo "Error: Both old and new filenames must be specified" >&2
        return 1
    fi

    # Check new filename length
    if [ ${#new_name} -gt 24 ]; then
        echo "Error: New filename exceeds 24 character limit" >&2
        return 1
    fi

    # Detect format
    local format=$(detect_img_format "$img_file")
    if [ "$format" = "INVALID" ]; then
        echo "Error: Invalid or unsupported IMG file format" >&2
        return 1
    fi

    local work_dir="$TEMP_DIR/img_work"

    # Extract existing IMG
    echo "Extracting existing IMG..."
    extract_img "$img_file" "$work_dir"

    # Check if old file exists
    if [ ! -f "$work_dir/$old_name" ]; then
        echo "Error: File '$old_name' not found in archive" >&2
        return 1
    fi

    # Check if new name already exists
    if [ -f "$work_dir/$new_name" ]; then
        echo "Error: File '$new_name' already exists in archive" >&2
        return 1
    fi

    # Rename file
    mv "$work_dir/$old_name" "$work_dir/$new_name"
    echo "Renamed: $old_name -> $new_name"

    # Rebuild IMG with same format
    echo "Rebuilding IMG..."
    local format_param=$(echo "$format" | tr '[:upper:]' '[:lower:]')
    create_img "$format_param" "$img_file" "$work_dir"

    echo "Successfully renamed file in $img_file"
}

# Rebuild IMG (optimize/defragment)
rebuild_img() {
    local img_file="$1"

    # Detect format
    local format=$(detect_img_format "$img_file")
    if [ "$format" = "INVALID" ]; then
        echo "Error: Invalid or unsupported IMG file format" >&2
        return 1
    fi

    echo "Rebuilding $img_file (format: $format)..."

    local work_dir="$TEMP_DIR/img_work"
    local backup_file="${img_file}.backup.$(date +%s)"

    # Create backup
    cp "$img_file" "$backup_file"
    echo "Backup created: $backup_file"

    # Extract existing IMG
    extract_img "$img_file" "$work_dir"

    # Rebuild IMG with same format
    local format_param=$(echo "$format" | tr '[:upper:]' '[:lower:]')
    create_img "$format_param" "$img_file" "$work_dir"

    # Show size comparison
    local old_size=$(stat -c%s "$backup_file")
    local new_size=$(stat -c%s "$img_file")
    local saved_bytes=$((old_size - new_size))

    echo "Rebuild complete!"
    echo "Original size: $old_size bytes"
    echo "New size: $new_size bytes"
    if [ $saved_bytes -gt 0 ]; then
        echo "Space saved: $saved_bytes bytes"
    elif [ $saved_bytes -lt 0 ]; then
        echo "Size increased: $((-saved_bytes)) bytes"
    else
        echo "Size unchanged"
    fi
}

# List contents with optional filtering
list_img_filtered() {
    local img_file="$1"
    local filter_pattern="$2"

    if [ ! -f "$img_file" ]; then
        echo "Error: IMG file not found: $img_file" >&2
        return 1
    fi

    # Detect format
    local format=$(detect_img_format "$img_file")
    if [ "$format" = "INVALID" ]; then
        echo "Error: Invalid or unsupported IMG file format" >&2
        return 1
    fi

    local entry_count=$(get_entry_count "$img_file" "$format")
    local dir_start=0

    case "$format" in
        "VER2")
            dir_start=8
            ;;
        "VER1")
            dir_start=0
            ;;
    esac

    echo "IMG File: $img_file (Format: $format)"
    echo "Files: $entry_count"
    if [ -n "$filter_pattern" ]; then
        echo "Filter: $filter_pattern"
    fi
    echo "----------------------------------------"
    printf "%-24s %10s %10s\n" "Filename" "Size" "Sector"
    echo "----------------------------------------"

    local displayed_count=0

    # Read directory entries
    for ((i=0; i<entry_count; i++)); do
        local dir_offset=$((dir_start + i * 32))

        local file_offset=$(read_uint32 "$img_file" $dir_offset)
        local file_size=$(read_uint32 "$img_file" $((dir_offset + 4)))
        local filename=$(dd if="$img_file" bs=1 skip=$((dir_offset + 8)) count=24 2>/dev/null | tr -d '\0')

        # Skip empty entries
        if [ -z "$filename" ] || [ $file_size -eq 0 ]; then
            continue
        fi

        # Apply filter if specified
        if [ -n "$filter_pattern" ]; then
            if [[ ! "$filename" == $filter_pattern ]]; then
                continue
            fi
        fi

        printf "%-24s %10d %10d\n" "$filename" "$file_size" "$file_offset"
        displayed_count=$((displayed_count + 1))
    done

    if [ -n "$filter_pattern" ]; then
        echo "----------------------------------------"
        echo "Displayed: $displayed_count files (filtered)"
    fi
}

info_img() {
    local img_file="$1"

    if [ ! -f "$img_file" ]; then
        echo "Error: IMG file not found: $img_file" >&2
        return 1
    fi

    local file_size=$(stat -c%s "$img_file")
    local signature=$(dd if="$img_file" bs=4 count=1 2>/dev/null)

    echo "IMG File Information"
    echo "===================="
    echo "File: $img_file"
    echo "Size: $file_size bytes ($(( file_size / 1024 )) KB)"
    echo "Format: $signature"

    if [ "$signature" != "VER2" ]; then
        echo "Status: Invalid or unsupported format"
        return 1
    fi

    local entry_count=$(read_uint32 "$img_file" 4)
    local dir_size=$((8 + entry_count * 32))
    local data_start_sector=$(( (dir_size + SECTOR_SIZE - 1) / SECTOR_SIZE ))
    local data_start_byte=$((data_start_sector * SECTOR_SIZE))

    echo "Status: Valid"
    echo "Entries: $entry_count"
    echo "Directory size: $dir_size bytes"
    echo "Data starts at: sector $data_start_sector (byte $data_start_byte)"
    echo "Estimated compression: $(( (file_size * 100) / (entry_count * 1024 + file_size) ))% efficiency"
}

# Main function
main() {
    # Handle help and version flags first
    case "$1" in
        "--help"|"-h"|"help")
            show_help
            exit 0
            ;;
        "--version"|"-v"|"version")
            show_version
            exit 0
            ;;
    esac

    # Handle commands
    case "$1" in
        "extract"|"x")
            if [ $# -ne 3 ]; then
                echo "Error: Invalid arguments for extract command" >&2
                echo "Usage: $0 extract <img_file> <output_dir>" >&2
                echo "Use '$0 --help' for more information." >&2
                exit 2
            fi
            extract_img "$2" "$3"
            ;;
        "create"|"c")
            if [ $# -ne 3 ]; then
                echo "Error: Invalid arguments for create command" >&2
                echo "Usage: $0 create <input_dir> <img_file>" >&2
                echo "Use '$0 --help' for more information." >&2
                exit 2
            fi
            create_img "$2" "$3"
            ;;
        "add"|"a")
            if [ $# -ne 3 ]; then
                echo "Error: Invalid arguments for add command" >&2
                echo "Usage: $0 add <img_file> <file_to_add>" >&2
                echo "Use '$0 --help' for more information." >&2
                exit 2
            fi
            add_to_img "$2" "$3"
            ;;
        "remove"|"rm"|"r")
            if [ $# -ne 3 ]; then
                echo "Error: Invalid arguments for remove command" >&2
                echo "Usage: $0 remove <img_file> <filename>" >&2
                echo "Use '$0 --help' for more information." >&2
                exit 2
            fi
            remove_from_img "$2" "$3"
            ;;
        "list"|"l")
            if [ $# -ne 2 ]; then
                echo "Error: Invalid arguments for list command" >&2
                echo "Usage: $0 list <img_file>" >&2
                echo "Use '$0 --help' for more information." >&2
                exit 2
            fi
            list_img "$2"
            ;;
        "info"|"i")
            if [ $# -ne 2 ]; then
                echo "Error: Invalid arguments for info command" >&2
                echo "Usage: $0 info <img_file>" >&2
                echo "Use '$0 --help' for more information." >&2
                exit 2
            fi
            info_img "$2"
            ;;
        "")
            echo "Error: No command specified" >&2
            echo "Use '$0 --help' for usage information." >&2
            exit 2
            ;;
        *)
            echo "Error: Unknown command '$1'" >&2
            echo "Use '$0 --help' for available commands." >&2
            exit 2
            ;;
    esac
}

main "$@"



