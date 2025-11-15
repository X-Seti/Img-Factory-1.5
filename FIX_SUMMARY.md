# IMG Factory 1.5 - Tab System & Validation Fix Summary
# X-Seti - November15 2025

## Overview
Fixed the "IMG file not loaded" bug and tab system issues where operations couldn't detect loaded files.

## Files Created

### 1. tab_system.py (Version 6)
**Location**: apps/methods/tab_system.py
**Changes**:
- `validate_tab_before_operation` (vers 3) - Now checks tab widget data directly
- `get_current_file_from_active_tab` (vers 2) - Gets data from tab widget, not current_img
- `get_tab_file_data` (vers 4) - Removed fallback to current_img
- `get_current_active_tab_info` (vers 2) - Uses tab widget exclusively

**Key Fix**: Validation now checks the actual tab widget data instead of main_window.current_img

### 2. file_validation.py (Version 1)
**Location**: apps/methods/file_validation.py
**Purpose**: Universal file validation that works with IMG, COL, and TXD files

**Functions**:
- `validate_img_file()` - For IMG-only operations
- `validate_col_file()` - For COL-only operations
- `validate_txd_file()` - For TXD-only operations
- `validate_any_file()` - For operations that work with any file type
- `get_selected_entries_for_operation()` - Validates AND gets selected entries

**Benefits**:
- ✅ Dynamic file type detection
- ✅ Proper error messages per file type
- ✅ Works with tab system automatically
- ✅ No more hardcoded "Current tab does not contain an IMG file"

### 3. fix_validation.py (Version 1)
**Location**: root/fix_validation.py
**Purpose**: Automated script to fix all 17 files with hardcoded validation

**What it does**:
1. Creates backups in apps/methods/old/validation_backup_[timestamp]
2. Adds import statement for file_validation
3. Replaces old validation pattern with new validation
4. Updates main_window.current_img references to img_file
5. Reports all changes made

### 4. VALIDATION_EXAMPLES.py
**Location**: Documentation file
**Purpose**: Shows before/after examples for each type of fix

## How to Apply Fixes

### Step 1: Install New Files
```bash
# Copy tab_system.py to methods folder
cp tab_system.py apps/methods/tab_system.py

# Copy file_validation.py to methods folder  
cp file_validation.py apps/methods/file_validation.py

# Copy fix script to root
cp fix_validation.py fix_validation.py
chmod +x fix_validation.py
```

### Step 2: Run Automated Fix
```bash
# Run the fix script
python3 fix_validation.py
```

**The script will**:
- Backup all 17 files before changes
- Add necessary imports
- Replace validation checks
- Update current_img references
- Show summary of changes

### Step 3: Manual Review Required
After running the script, manually check:

**Files that need get_selected_entries_for_operation():**
- apps/core/dump.py - dump_selected_function
- apps/core/remove.py - remove_selected_function
- apps/core/export_via.py - export functions (might also need validate_any_file)

**Files that might work with COL too:**
- apps/core/export_via.py - Use validate_any_file() instead
- apps/core/imgcol_*.py - Use validate_any_file() for IMG/COL operations

**Check operation names:**
The script extracts operation names from function names, but verify they make sense:
- export_selected_function → "Export Selected" ✓
- import_function → "Import" ✓
- etc.

### Step 4: Test Each Operation
Test the following operations with multiple tabs open:
- [ ] Export Selected (IMG tab)
- [ ] Export All (IMG tab)
- [ ] Import (IMG tab)
- [ ] Remove Selected (IMG tab)
- [ ] Dump Selected (IMG tab)
- [ ] Dump All (IMG tab)
- [ ] Export Via (IMG tab)
- [ ] Export Via (COL tab)
- [ ] Rebuild (IMG tab)
- [ ] Convert COL (IMG and COL tabs)
- [ ] Rename (IMG tab)
- [ ] Replace (IMG tab)

### Step 5: Verify Multi-Tab Behavior
1. Open 3+ IMG files in different tabs
2. Switch between tabs
3. Try operations - should work on ACTIVE tab only
4. Verify correct file is detected

## Files Fixed by Script

1. apps/core/core.py
2. apps/core/dump.py
3. apps/core/export_via.py
4. apps/core/rebuild.py
5. apps/core/remove.py
6. apps/core/remove_via.py
7. apps/core/rw_analysis_trigger.py
8. apps/core/imgcol_convert.py
9. apps/core/imgcol_rename.py
10. apps/core/imgcol_replace.py
11. apps/core/impotr.py
12. apps/core/rename.py
13. apps/core/save_entry.py
14. apps/methods/img_import_system.py

## Rollback Instructions

If issues occur, restore from backup:
```bash
# Find backup directory
ls -la apps/methods/old/validation_backup_*

# Restore specific file
cp apps/methods/old/validation_backup_TIMESTAMP/file.py apps/core/file.py

# Or restore all files
BACKUP_DIR="apps/methods/old/validation_backup_TIMESTAMP"
cp $BACKUP_DIR/*.py apps/core/
```

## Integration with Main App

The main imgfactory.py should already have tab_system integrated. Just ensure:

```python
# In imgfactory.py or main initialization
from apps.methods.tab_system import integrate_tab_system

# During startup
integrate_tab_system(self)
```

File validation is imported per-function, no global integration needed.

## Expected Behavior After Fixes

### Before Fix:
- Load IMG in tab 1
- Switch to tab 2  
- Press Export → ❌ "Current tab does not contain an IMG file"

### After Fix:
- Load IMG in tab 1
- Switch to tab 2
- Press Export → ✅ "No file is loaded in the active tab" (correct!)
- Switch back to tab 1
- Press Export → ✅ Works! Shows export dialog

### Multi-File Support:
- Load IMG in tab 1
- Load COL in tab 2
- Tab 1 active: Export works with IMG ✓
- Tab 2 active: Export shows "Wrong file type" ✓ (or works if operation supports COL)

## Troubleshooting

**Issue**: "Module file_validation not found"
**Fix**: Ensure file_validation.py is in apps/methods/

**Issue**: Operations still can't find file
**Fix**: Check that tab_system.py (Version 6) is installed and integrated

**Issue**: Wrong operation name in error messages
**Fix**: Edit the function and change the string in validate_img_file(main_window, "OPERATION_NAME")

**Issue**: Function needs selected entries but only validates file
**Fix**: Replace validate_img_file() with get_selected_entries_for_operation()

## Benefits of New System

✅ **Dynamic file type detection** - Works with IMG, COL, TXD automatically
✅ **Tab-aware** - Always checks ACTIVE tab, not stale references
✅ **Better error messages** - Shows actual file type vs required type
✅ **Multi-tab safe** - No more confusion with multiple files open
✅ **Cleaner code** - One-line validation instead of 3-4 lines
✅ **Future-proof** - Easy to add new file types

## Next Steps

After applying these fixes, the remaining TODO items are:
- Export combining files issue (separate fix needed)
- Dump logic to match export (separate fix needed)
- COL dialog theme issues (unrelated to validation)

## Notes

- The fix_validation.py script is conservative - it only replaces exact patterns
- Some functions may need manual adjustment after automated fix
- Always test in a development environment first
- Keep backups until all testing is complete

---
Last Updated: November 15, 2025
Version: 1
