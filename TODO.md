#this belongs in root /TODO.md - Version: 1
# X-Seti - October22 2025 - IMG Factory 1.5 TODO List

# IMG Factory 1.5 - TODO List

## High Priority

### 1. Tab System Issues
**Issue**: Multiple tabs open (IMG/COL), export_via.py, export.py and dump.py functions can't see the current selected tab.

**Tasks**:
- [ ] Fix tab detection in export functions
- [ ] Fix tab detection in dump functions
- [ ] Fix tab detection in export_via functions
- [ ] Add active tab tracking system
- [ ] Test with multiple IMG files open
- [ ] Test with COL files in different tabs

**Impact**: High - Affects core functionality

---

### 2. Export Function Issues
**Issue**: export.py functions export all files combined!! 12Mb file for each, should be single files.

**Problem**: Selecting 7 entries gives 7 combined files instead of 7 separate files.

**Tasks**:
- [ ] Fix export.py to export selected entries individually
- [ ] Add option to combine files if user wants
- [ ] Add "Export as single file" option
- [ ] Add "Export as separate files" option (default)
- [ ] Update export dialog with clear options
- [ ] Test with various file counts

**Expected Behavior**:
- Select 7 entries → Export 7 separate files
- Optional: "Combine into single COL" checkbox

**Impact**: High - Core export functionality

---

### 3. Dump Function Logic
**Issue**: dump should follow same logic as export - single or combined files.

**Tasks**:
- [ ] Update dump.py with same logic as export fix
- [ ] Add "Dump as single file" option
- [ ] Add "Dump as separate files" option (default)
- [ ] Match export.py behavior for consistency
- [ ] Update dump dialog

**Impact**: Medium-High - Consistency issue

---

### 4. COL Dialog Theme Issues
**Issue**: Background box on COL dialog is hardcoded, dark themes can't see text.

**Tasks**:
- [ ] Remove hardcoded background colors
- [ ] Connect COL dialogs to theme system
- [ ] Test with all themes (light/dark)
- [ ] Check text contrast in dark themes
- [ ] Update all COL-related dialogs
- [ ] Add theme change detection

**Files to Fix**:
- COL dialogs in components/
- COL analysis dialogs
- COL editor dialogs

**Impact**: Medium - Usability with dark themes

---

## Medium Priority

### 5. Import System Improvements

#### 5a. Import via IDE
**Status**: Partly Fixed - Aug7
**Issue**: import_via ide gives an error, no .ide file found or no files in .ide.

**Tasks**:
- [ ] Better error messages for missing IDE files
- [ ] Better error messages for empty IDE files
- [ ] Validate IDE file before import
- [ ] Show IDE file contents preview
- [ ] Add IDE file format validation

---

#### 5b. Folder Import Options
**Status**: TODO
**Request**: Add options for folder contents import.

**Tasks**:
- [ ] Create folder import dialog
- [ ] Add file type filters
- [ ] Add recursive/non-recursive option
- [ ] Add file preview list
- [ ] Add size estimation
- [ ] Add import order options
- [ ] Test with large folders

---

#### 5c. Text File List Import
**Status**: TODO
**Request**: Add import via textfile.txt list - modelname.dff, texturename.txd in any order.

**Tasks**:
- [ ] Create smart text file parser
- [ ] Auto-detect file types from extensions
- [ ] Handle mixed file types
- [ ] Handle paths (relative/absolute)
- [ ] Handle missing files gracefully
- [ ] Add validation before import
- [ ] Show import preview

**Example Input**:
```
vehicle.dff
vehicle.txd
wheel.dff
interior.dff
texture_pack.txd
```

**Function Requirements**:
- Smart enough to understand file contents
- No specific order required
- Mixed file types supported
- Skip missing files with warning

---

### 6. Drag and Drop Support
**Status**: TODO
**Request**: Drag and Drop files/folders onto imgfactory app to import.

**Tasks**:
- [ ] Enable drag-drop on main window
- [ ] Handle single file drops
- [ ] Handle multiple file drops
- [ ] Handle folder drops
- [ ] Show drop preview overlay
- [ ] Confirm before import
- [ ] Show progress during import
- [ ] Support all file types (DFF, TXD, COL, etc.)

**Impact**: Medium - Nice UX improvement

---

### 7. File Highlighting Issues
**Status**: TODO
**Issue**: Highlighting shows "28/28 files" when 10 already existed.

**Tasks**:
- [ ] Fix duplicate detection logic
- [ ] Show accurate "new vs existing" count
- [ ] Highlight only truly new files
- [ ] Update status message accuracy
- [ ] Test with various scenarios

**Expected**:
- Import 28 files, 10 exist → Show "18 new, 10 skipped"
- Highlight only the 18 new files

**Impact**: Low-Medium - Accuracy issue

---

### 8. Save Entry Function
**Status**: TODO
**Issue**: Fix the Save Entry function.

**Tasks**:
- [ ] Identify current Save Entry issues
- [ ] Fix save functionality
- [ ] Test with various file types
- [ ] Add error handling
- [ ] Add success feedback
- [ ] Update documentation

**Impact**: Medium - Important feature

---

### 9. Theme Switching
**Status**: TODO
**Request**: Theme switching from first page.

**Tasks**:
- [ ] Add theme selector to main page/toolbar
- [ ] Quick theme dropdown menu
- [ ] Show theme preview
- [ ] Apply theme immediately
- [ ] Remember theme selection
- [ ] Add keyboard shortcut

**Impact**: Low - Convenience feature

---

## Low Priority

### 10. Code Organization
**Status**: Planning
**Note**: Some files in components are shared functions, like img_core_classes, col_core_classes.

**Planned Split**:
- [ ] methods/img_entry_operations.py - Entry management (add, remove, get)
- [ ] methods/img_file_operations.py - File I/O operations  
- [ ] methods/img_detection.py - RW version detection
- [ ] methods/img_validation.py - File validation

**Important**: Before creating these files, check existing functions in methods/ to avoid duplicates.

**Impact**: Low - Code organization

---

## Future Features

### 11. DFF Texture to COL Material Mapping
**Status**: Idea Documented
**Priority**: Medium-High (when COL viewer is stable)

See: `components/col_viewer/TODO_DFF_TEXTURE_MAPPING.md`

**Summary**:
- Read DFF texture names
- Map to COL material IDs
- Auto-assign materials based on textures
- Visual validation of material assignments

**Estimated Time**: 2-3 weeks
**Dependencies**: COL viewer (✅ Complete)

---

### 12. Advanced COL Viewer Features
**Status**: Future Enhancement

**Possible Additions**:
- [ ] Color faces by material group
- [ ] Filter by material type
- [ ] Material statistics panel
- [ ] Export screenshot
- [ ] Measurement tools
- [ ] Wireframe/solid toggle
- [ ] Multiple model support
- [ ] Animation/rotation controls
- [ ] Lighting controls
- [ ] Export to OBJ format

---

### 13. Batch Processing Improvements
**Status**: Future Enhancement

**Ideas**:
- [ ] Batch COL material assignment
- [ ] Batch file validation
- [ ] Batch format conversion
- [ ] Progress reporting
- [ ] Error logging
- [ ] Undo/redo support

---

## Completed Tasks

See `ChangeLog.md` for complete history of fixed issues.

---

## Priority Legend

- 🔴 **High Priority** - Affects core functionality, needs immediate attention
- 🟡 **Medium Priority** - Important features, should be addressed soon
- 🟢 **Low Priority** - Nice to have, quality of life improvements
- 🔵 **Future** - Long-term enhancements, not blocking

---

## Task Assignment

When working on tasks:
1. ✅ Check for duplicate functions first
2. ✅ Follow naming conventions (no "Enhanced", "Fixed", etc.)
3. ✅ Keep files under 90k
4. ✅ Update version numbers in methods
5. ✅ Add proper headers to all files
6. ✅ Test thoroughly before marking complete
7. ✅ Update this TODO when completing tasks
8. ✅ Move completed items to ChangeLog.md

---

## Notes

- **No Patch Files** - Fix issues properly, not with patches
- **No Duplicates** - Check existing functions before creating new ones
- **Clean Code** - No fallback code, works or doesn't work
- **Proper Naming** - Simple, clear filenames
- **Documentation** - Keep docs updated

---

**Last Updated**: October 22, 2025
**Active Tasks**: 13 high/medium priority items
**Future Features**: 3 documented ideas
