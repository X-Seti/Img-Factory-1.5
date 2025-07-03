#!/bin/bash
#this belongs in root /cleanup_conflicts.sh - Version: 1
# X-Seti - JULY01 2025 - IMG Factory 1.5 Conflict Cleanup Script
# Automated cleanup of conflicting references

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Backup directory
BACKUP_DIR="./backup_$(date +%Y%m%d_%H%M%S)"

# Function to print header
print_header() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}IMG Factory 1.5 - Conflict Cleanup Tool${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
}

# Function to create backup
create_backup() {
    echo -e "${YELLOW}Creating backup...${NC}"
    mkdir -p "$BACKUP_DIR"
    
    # Find all Python files and copy them
    find . -name "*.py" -not -path "./__pycache__/*" -not -path "./backup_*/*" | while read file; do
        # Create directory structure in backup
        dir_path=$(dirname "$file")
        mkdir -p "$BACKUP_DIR/$dir_path"
        cp "$file" "$BACKUP_DIR/$file"
    done
    
    echo -e "${GREEN}✓ Backup created in: $BACKUP_DIR${NC}"
}

# Function to analyze conflicts
analyze_conflicts() {
    echo -e "${PURPLE}Analyzing conflicts...${NC}"
    echo ""
    
    # Check for imgfactory_main references
    echo -e "${BLUE}1. Checking for 'imgfactory_main' references:${NC}"
    if ./findwithin.sh -c "imgfactory_main" | grep -q ":"; then
        ./findwithin.sh "imgfactory_main"
        echo ""
    else
        echo -e "${GREEN}  ✓ No references found${NC}"
    fi
    
    # Check for ImgFactoryDemo references
    echo -e "${BLUE}2. Checking for 'ImgFactoryDemo' class references:${NC}"
    if ./findwithin.sh -c "ImgFactoryDemo" | grep -q ":"; then
        ./findwithin.sh "ImgFactoryDemo"
        echo ""
    else
        echo -e "${GREEN}  ✓ No references found${NC}"
    fi
    
    # Check for imgfactory_demo references
    echo -e "${BLUE}3. Checking for 'imgfactory_demo' file references:${NC}"
    if ./findwithin.sh -c -i "imgfactory_demo" | grep -q ":"; then
        ./findwithin.sh -i "imgfactory_demo"
        echo ""
    else
        echo -e "${GREEN}  ✓ No references found${NC}"
    fi
    
    # Check for duplicate imports
    echo -e "${BLUE}4. Checking for duplicate import patterns:${NC}"
    if ./findwithin.sh -c "from.*imgfactory" | grep -q ":"; then
        ./findwithin.sh "from.*imgfactory"
        echo ""
    else
        echo -e "${GREEN}  ✓ No duplicate imports found${NC}"
    fi
}

# Function to fix launch script
fix_launch_script() {
    echo -e "${YELLOW}Fixing launch_imgfactory.py...${NC}"
    
    if [[ -f "launch_imgfactory.py" ]]; then
        # Replace imgfactory_main references with imgfactory
        sed -i.bak 's/imgfactory_main/imgfactory/g' launch_imgfactory.py
        
        # Update the required files list
        sed -i 's/"imgfactory_main.py"/"imgfactory.py"/g' launch_imgfactory.py
        
        # Remove references to non-existent files
        sed -i '/img_manager.py/d' launch_imgfactory.py
        sed -i '/img_creator.py/d' launch_imgfactory.py
        sed -i '/img_template_manager.py/d' launch_imgfactory.py
        sed -i '/img_validator.py/d' launch_imgfactory.py
        
        echo -e "${GREEN}  ✓ Updated launch_imgfactory.py${NC}"
    else
        echo -e "${RED}  ✗ launch_imgfactory.py not found${NC}"
    fi
}

# Function to remove conflicting files
remove_conflicting_files() {
    echo -e "${YELLOW}Removing conflicting files...${NC}"
    
    # List of files to remove
    CONFLICT_FILES=(
        "Imgfactory_Demo.py"
        "imgfactory_demo.py" 
        "imgfactory_main.py"
        "components/old/img_factory_integration.py"
        "components/old/img_creator.py"
    )
    
    for file in "${CONFLICT_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            echo -e "${RED}  • Removing: $file${NC}"
            rm "$file"
        else
            echo -e "${GREEN}  ✓ Already removed: $file${NC}"
        fi
    done
    
    # Remove old directory if empty
    if [[ -d "components/old" ]] && [[ -z "$(ls -A components/old)" ]]; then
        rmdir "components/old"
        echo -e "${GREEN}  ✓ Removed empty components/old directory${NC}"
    fi
}

# Function to fix imports in remaining files
fix_imports() {
    echo -e "${YELLOW}Fixing imports in remaining files...${NC}"
    
    # Find all Python files and fix imports
    find . -name "*.py" -not -path "./backup_*/*" -not -path "./__pycache__/*" | while read file; do
        if grep -q "imgfactory_main\|ImgFactoryDemo\|imgfactory_demo" "$file"; then
            echo -e "${BLUE}  • Fixing imports in: $file${NC}"
            
            # Fix imports
            sed -i.bak 's/from imgfactory_main/from imgfactory/g' "$file"
            sed -i 's/import imgfactory_main/import imgfactory/g' "$file"
            sed -i 's/imgfactory_main\./imgfactory./g' "$file"
            
            # Fix class references
            sed -i 's/ImgFactoryDemo/IMGFactory/g' "$file"
            
            # Fix file references
            sed -i 's/imgfactory_demo\.py/imgfactory.py/g' "$file"
            sed -i 's/Imgfactory_Demo\.py/imgfactory.py/g' "$file"
            
            # Remove .bak file if changes were made
            if [[ -f "$file.bak" ]]; then
                rm "$file.bak"
            fi
        fi
    done
}

# Function to validate cleanup
validate_cleanup() {
    echo -e "${PURPLE}Validating cleanup...${NC}"
    
    # Check if conflicts still exist
    CONFLICTS_FOUND=0
    
    echo -e "${BLUE}1. Checking remaining 'imgfactory_main' references:${NC}"
    if ./findwithin.sh -c "imgfactory_main" | grep -q ":"; then
        ./findwithin.sh -l "imgfactory_main"
        CONFLICTS_FOUND=1
    else
        echo -e "${GREEN}  ✓ All references cleaned${NC}"
    fi
    
    echo -e "${BLUE}2. Checking remaining 'ImgFactoryDemo' references:${NC}"
    if ./findwithin.sh -c "ImgFactoryDemo" | grep -q ":"; then
        ./findwithin.sh -l "ImgFactoryDemo"
        CONFLICTS_FOUND=1
    else
        echo -e "${GREEN}  ✓ All references cleaned${NC}"
    fi
    
    echo -e "${BLUE}3. Checking remaining 'imgfactory_demo' references:${NC}"
    if ./findwithin.sh -c -i "imgfactory_demo" | grep -q ":"; then
        ./findwithin.sh -l -i "imgfactory_demo"
        CONFLICTS_FOUND=1
    else
        echo -e "${GREEN}  ✓ All references cleaned${NC}"
    fi
    
    if [[ $CONFLICTS_FOUND -eq 0 ]]; then
        echo -e "${GREEN}✓ All conflicts resolved successfully!${NC}"
        return 0
    else
        echo -e "${RED}✗ Some conflicts remain - manual review needed${NC}"
        return 1
    fi
}

# Function to show project status
show_project_status() {
    echo -e "${PURPLE}Current Project Status:${NC}"
    echo ""
    
    echo -e "${BLUE}Main Files:${NC}"
    [[ -f "imgfactory.py" ]] && echo -e "${GREEN}  ✓ imgfactory.py (main entry point)${NC}" || echo -e "${RED}  ✗ imgfactory.py missing${NC}"
    [[ -f "launch_imgfactory.py" ]] && echo -e "${GREEN}  ✓ launch_imgfactory.py${NC}" || echo -e "${RED}  ✗ launch_imgfactory.py missing${NC}"
    
    echo ""
    echo -e "${BLUE}Component Files:${NC}"
    ls components/img_*.py 2>/dev/null | head -5 | while read file; do
        echo -e "${GREEN}  ✓ $(basename "$file")${NC}"
    done
    
    echo ""
    echo -e "${BLUE}GUI Files:${NC}"
    ls gui/*.py 2>/dev/null | head -3 | while read file; do
        echo -e "${GREEN}  ✓ $(basename "$file")${NC}"
    done
    
    echo ""
    echo -e "${BLUE}Theme Files:${NC}"
    ls themes/*.json 2>/dev/null | wc -l | xargs echo -e "${GREEN}  ✓" "themes available${NC}"
}

# Main execution
main() {
    print_header
    
    # Check if findwithin.sh exists
    if [[ ! -f "./findwithin.sh" ]]; then
        echo -e "${RED}Error: findwithin.sh not found. Please create it first.${NC}"
        exit 1
    fi
    
    # Make findwithin.sh executable
    chmod +x ./findwithin.sh
    
    echo -e "${YELLOW}This script will:${NC}"
    echo -e "  1. Create a backup of all Python files"
    echo -e "  2. Analyze current conflicts"
    echo -e "  3. Fix launch script references"
    echo -e "  4. Remove conflicting files"
    echo -e "  5. Fix imports in remaining files"
    echo -e "  6. Validate the cleanup"
    echo ""
    
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Cleanup cancelled.${NC}"
        exit 0
    fi
    
    echo ""
    
    # Execute cleanup steps
    create_backup
    echo ""
    
    analyze_conflicts
    echo ""
    
    fix_launch_script
    echo ""
    
    remove_conflicting_files
    echo ""
    
    fix_imports
    echo ""
    
    if validate_cleanup; then
        echo ""
        show_project_status
        echo ""
        echo -e "${GREEN}🎉 Cleanup completed successfully!${NC}"
        echo -e "${BLUE}Backup saved in: $BACKUP_DIR${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠️  Cleanup completed with warnings.${NC}"
        echo -e "${BLUE}Backup saved in: $BACKUP_DIR${NC}"
        echo -e "${YELLOW}Please review remaining conflicts manually.${NC}"
    fi
}

# Check for help option
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    print_header
    echo -e "${YELLOW}Usage: $0${NC}"
    echo ""
    echo "This script automatically cleans up IMG Factory 1.5 project conflicts by:"
    echo "  • Creating backups of all Python files"
    echo "  • Removing references to non-existent imgfactory_main.py"
    echo "  • Removing conflicting ImgFactoryDemo class references"
    echo "  • Fixing import statements"
    echo "  • Removing duplicate/conflicting files"
    echo ""
    echo "The script will ask for confirmation before making changes."
    echo ""
    exit 0
fi

# Run main function
main "$@"