#!/bin/bash
#this belongs in root /findwithin.sh - Version: 1
# X-Seti - JULY01 2025 - IMG Factory 1.5 Search Script
# Recursively search for words/functions within files

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print usage
usage() {
    echo -e "${CYAN}IMG Factory 1.5 - File Content Search Tool${NC}"
    echo -e "${YELLOW}Usage: $0 [options] \"search_term\"${NC}"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -i, --ignore-case   Case insensitive search"
    echo "  -w, --word-only     Match whole words only"
    echo "  -n, --line-numbers  Show line numbers"
    echo "  -c, --count         Show only count of matches per file"
    echo "  -l, --files-only    Show only filenames with matches"
    echo "  -e, --exclude       Exclude pattern (can be used multiple times)"
    echo "  -t, --type          File type filter (py, json, md, sh, etc.)"
    echo ""
    echo "Examples:"
    echo "  $0 \"imgfactory_main\"                    # Find references to imgfactory_main"
    echo "  $0 \"ImgFactoryDemo\"                     # Find references to ImgFactoryDemo class"
    echo "  $0 -i \"imgfactory_demo\"                # Case insensitive search"
    echo "  $0 -w \"main\"                           # Match whole word 'main' only"
    echo "  $0 -t py \"def create_new_img\"          # Search only Python files"
    echo "  $0 -e \"__pycache__\" -e \"*.pyc\" \"import\"  # Exclude cache files"
    echo ""
    echo -e "${GREEN}Project Cleanup Commands:${NC}"
    echo "  $0 \"imgfactory_main\"     # Find all references to remove"
    echo "  $0 \"ImgFactoryDemo\"      # Find demo class references"
    echo "  $0 \"imgfactory_demo\"     # Find demo file references"
}

# Default options
IGNORE_CASE=""
WORD_ONLY=""
LINE_NUMBERS="-n"
COUNT_ONLY=""
FILES_ONLY=""
EXCLUDES=()
FILE_TYPE=""
SEARCH_TERM=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -i|--ignore-case)
            IGNORE_CASE="-i"
            shift
            ;;
        -w|--word-only)
            WORD_ONLY="-w"
            shift
            ;;
        -n|--line-numbers)
            LINE_NUMBERS="-n"
            shift
            ;;
        -c|--count)
            COUNT_ONLY="-c"
            LINE_NUMBERS=""
            shift
            ;;
        -l|--files-only)
            FILES_ONLY="-l"
            LINE_NUMBERS=""
            shift
            ;;
        -e|--exclude)
            EXCLUDES+=("$2")
            shift 2
            ;;
        -t|--type)
            FILE_TYPE="$2"
            shift 2
            ;;
        -*)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            exit 1
            ;;
        *)
            if [[ -z "$SEARCH_TERM" ]]; then
                SEARCH_TERM="$1"
            else
                echo -e "${RED}Error: Multiple search terms not supported${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if search term is provided
if [[ -z "$SEARCH_TERM" ]]; then
    echo -e "${RED}Error: Search term is required${NC}"
    usage
    exit 1
fi

# Build grep command
GREP_CMD="grep"
GREP_OPTIONS=""

# Add options
if [[ -n "$IGNORE_CASE" ]]; then
    GREP_OPTIONS="$GREP_OPTIONS $IGNORE_CASE"
fi

if [[ -n "$WORD_ONLY" ]]; then
    GREP_OPTIONS="$GREP_OPTIONS $WORD_ONLY"
fi

if [[ -n "$LINE_NUMBERS" ]]; then
    GREP_OPTIONS="$GREP_OPTIONS $LINE_NUMBERS"
fi

if [[ -n "$COUNT_ONLY" ]]; then
    GREP_OPTIONS="$GREP_OPTIONS $COUNT_ONLY"
fi

if [[ -n "$FILES_ONLY" ]]; then
    GREP_OPTIONS="$GREP_OPTIONS $FILES_ONLY"
fi

# Add recursive and color options
GREP_OPTIONS="$GREP_OPTIONS -r --color=always"

# Build find command for file filtering
FIND_CMD="find . -type f"

# Add file type filter
if [[ -n "$FILE_TYPE" ]]; then
    case "$FILE_TYPE" in
        py)
            FIND_CMD="$FIND_CMD -name '*.py'"
            ;;
        json)
            FIND_CMD="$FIND_CMD -name '*.json'"
            ;;
        md)
            FIND_CMD="$FIND_CMD -name '*.md'"
            ;;
        sh)
            FIND_CMD="$FIND_CMD -name '*.sh'"
            ;;
        txt)
            FIND_CMD="$FIND_CMD -name '*.txt'"
            ;;
        *)
            FIND_CMD="$FIND_CMD -name '*.$FILE_TYPE'"
            ;;
    esac
fi

# Add default excludes
DEFAULT_EXCLUDES=("__pycache__" "*.pyc" "*.pyo" ".git" ".vscode" "*.log" "node_modules")

# Combine default and user excludes
ALL_EXCLUDES=("${DEFAULT_EXCLUDES[@]}" "${EXCLUDES[@]}")

# Build exclude options for find
for exclude in "${ALL_EXCLUDES[@]}"; do
    if [[ "$exclude" == *"*"* ]]; then
        FIND_CMD="$FIND_CMD ! -name '$exclude'"
    else
        FIND_CMD="$FIND_CMD ! -path '*/$exclude/*' ! -name '$exclude'"
    fi
done

# Function to colorize output
colorize_output() {
    if [[ -n "$COUNT_ONLY" ]]; then
        # For count mode, colorize numbers
        sed -E "s/^([^:]+):([0-9]+)$/$(printf "${BLUE}")\\1$(printf "${NC}"):$(printf "${GREEN}")\\2$(printf "${NC}")/"
    elif [[ -n "$FILES_ONLY" ]]; then
        # For files-only mode, colorize filenames
        sed -E "s/^(.+)$/$(printf "${GREEN}")\\1$(printf "${NC}")/"
    else
        # For regular mode, colorize filename and line numbers
        sed -E "s/^([^:]+):([0-9]+):(.*)$/$(printf "${BLUE}")\\1$(printf "${NC}"):$(printf "${YELLOW}")\\2$(printf "${NC}"):\\3/"
    fi
}

# Print header
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}IMG Factory 1.5 - Searching for: ${YELLOW}'$SEARCH_TERM'${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"

# Show search parameters
echo -e "${PURPLE}Search Options:${NC}"
[[ -n "$IGNORE_CASE" ]] && echo -e "  ${GREEN}✓${NC} Case insensitive"
[[ -n "$WORD_ONLY" ]] && echo -e "  ${GREEN}✓${NC} Whole words only"
[[ -n "$COUNT_ONLY" ]] && echo -e "  ${GREEN}✓${NC} Count only"
[[ -n "$FILES_ONLY" ]] && echo -e "  ${GREEN}✓${NC} Files only"
[[ -n "$FILE_TYPE" ]] && echo -e "  ${GREEN}✓${NC} File type: $FILE_TYPE"
[[ ${#EXCLUDES[@]} -gt 0 ]] && echo -e "  ${GREEN}✓${NC} Custom excludes: ${EXCLUDES[*]}"
echo ""

# Execute search
if [[ -n "$FILE_TYPE" ]] || [[ ${#ALL_EXCLUDES[@]} -gt 0 ]]; then
    # Use find + grep for complex filtering
    FILES=$(eval "$FIND_CMD" 2>/dev/null)
    if [[ -n "$FILES" ]]; then
        echo "$FILES" | xargs $GREP_CMD $GREP_OPTIONS "$SEARCH_TERM" 2>/dev/null | colorize_output
        RESULT_CODE=${PIPESTATUS[1]}
    else
        RESULT_CODE=1
    fi
else
    # Use simple grep for basic search
    $GREP_CMD $GREP_OPTIONS "$SEARCH_TERM" . 2>/dev/null | colorize_output
    RESULT_CODE=${PIPESTATUS[0]}
fi

# Print results summary
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"

if [[ $RESULT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✓ Search completed - matches found${NC}"
    
    # Show quick cleanup suggestions for specific terms
    case "$SEARCH_TERM" in
        *"imgfactory_main"*|*"imgfactory_demo"*|*"ImgFactoryDemo"*)
            echo ""
            echo -e "${YELLOW}💡 Cleanup Suggestions:${NC}"
            echo -e "  ${RED}•${NC} Remove references to imgfactory_main.py (file doesn't exist)"
            echo -e "  ${RED}•${NC} Remove references to ImgFactoryDemo class (conflicts with IMGFactory)"
            echo -e "  ${RED}•${NC} Update imports to use imgfactory.py as main entry point"
            echo -e "  ${RED}•${NC} Consider removing Imgfactory_Demo.py entirely"
            ;;
    esac
else
    echo -e "${GREEN}✓ Search completed - no matches found${NC}"
fi

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"

exit $RESULT_CODE