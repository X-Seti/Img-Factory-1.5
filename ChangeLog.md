#this belongs in root /ChangeLog.md - Version: 1
# X-Seti - October22 2025 - IMG Factory 1.5 ChangeLog

# IMG Factory 1.5 - ChangeLog - (New System)

Complete history of fixes, updates, and improvements.

---

## October 2025

### October 22, 2025 - COL Viewer Complete
**Added**:
- ✅ Complete COL 3D Viewer from scratch
- ✅ COL_Parser.py - Clean parser (no legacy bugs)
- ✅ COL_Materials.py - Material database (214 materials)
- ✅ col_viewer.py - OpenGL 3D viewport
- ✅ col_viewer_integration.py - Right-click integration
- ✅ Material groups organized by type
- ✅ Auto game detection (GTA III/VC/SA)
- ✅ Theme integration support
- ✅ Camera controls (orbit, pan, zoom)
- ✅ Complete documentation

**Features**:
- View COL files in 3D
- Show mesh, spheres, boxes, bounds
- Material names display
- Right-click context menu
- Theme-aware colors
- 3DS Max style controls

---

## September 2025

### September 4, 2025 - Dump Command Fix
**Fixed**:
- ✅ Dump command has been fixed
- ✅ Proper file dumping functionality
- ✅ Error handling improved

---

## August 2025

### August 26, 2025 - Rebuild System
**Fixed**:
- ✅ Rebuild system is fixed
- ✅ Rebuild all now works with menu
- ✅ Rebuild open tabs option
- ✅ Rebuild folder contents option
- ✅ Better progress feedback

---

### August 15, 2025 - Export & Dump Functions
**Fixed**:
- ✅ Fixed Export functions
- ✅ Fixed Dump functions
- ✅ Better error handling

**Removed**:
- ❌ Quick Export (replaced with improved Export)

---

### August 14, 2025 - IDE Editor & Menu
**Fixed**:
- ✅ IDE Editor - Updated and bugs fixed
- ✅ Menu Options fixed
- ✅ Better IDE file handling
- ✅ Improved menu navigation

---

### August 12, 2025 - COL Editor Core
**Fixed**:
- ✅ Col Editor - Core utility ready
- ✅ Collision system restored
- ✅ Collision system working
- ✅ Basic COL editing functional

**Note**: This was the foundation. October 2025 COL Viewer is complete rewrite.

---

### August 10, 2025 - Tab System
**Fixed**:
- ✅ Tab system for IMG's fixed
- ✅ Close first tab fixed
- ✅ Multiple tabs work properly
- ✅ Tab switching improved

---

### August 9, 2025 - Startup System
**Fixed**:
- ✅ Init startup order fixed
- ✅ Smoother IMG loading
- ✅ Better initialization sequence
- ✅ Reduced startup errors

---

### August 7, 2025 - Theme System Update
**Fixed**:
- ✅ Light/Dark theming system updated
- ✅ core/theme_integration.py improved

**Partial Fix**:
- 🔶 Import function needs work
- 🔶 import_via ide error handling
- 🔶 Still needs additional work (see TODO.md)

**Still Needs Work**:
- Theme system needs adjusting for other styles
- More theme variations needed

---

### August 6, 2025 - Multiple Fixes
**Fixed**:
- ✅ File Window Display List
- ✅ Status Window theming
- ✅ File Window Theming
- ✅ Reload function works again
- ✅ Status/Progress Bar fixed and moved to methods/Progressbar.py

**Removed**:
- ❌ Just Green Theme Base
- ❌ Rebuild_As removed from all files

**Added**:
- ✅ New theme functions
- ✅ Save Entry menu option
- ✅ Shared progressbar function

**Theme Changes**:
```json
// Added Save Entry with themed colors
{
  "text": "Save Entry...",
  "icon": "document-save-entry",
  "action": "save_img_entry",
  "color": "#E8F5E8"
}
```

---

### August 4, 2025 - Testing & Verification
**Checked**:
- ✅ Loading single IMG
- ✅ Loading multiple IMG
- ✅ Closing single IMG  
- ✅ Closing multiple IMG
- ✅ All core operations verified

---

## July 2025

### July 31, 2025 - UI Improvements
**Changed**:
- ✅ Rebuild_As removed
- ✅ "Save Entries" seemed more logical
- ✅ Update_list renamed to refresh_table

**Old Code**:
```python
("Refresh", "update", "view-refresh", "#F9FBE7", "refresh_table")
```

**New Code**:
```json
{
  "text": "Refresh",
  "action": "update",
  "icon": "view-refresh",
  "color": "#F9FBE7"
}
```

**Reason**: Better naming convention, more logical structure

---

### July 2025 - Project Start
**Initialized**:
- ✅ IMG Factory 1.5 project started
- ✅ New changelog system
- ✅ Clean code approach
- ✅ No legacy bugs philosophy
- ✅ Proper documentation standards

---

## Version History Summary

### Version 1.5 (Current - October 2025)
**Major Features**:
- Complete COL 3D Viewer
- Material database (214 materials)
- Theme system improvements
- Better file operations
- Enhanced error handling
- Comprehensive documentation

**Line Count**: ~70KB of clean code for COL viewer alone
**Files Added**: 10+ new components
**Bugs Fixed**: 20+ issues resolved


### Version 1.0-1.4 (July-September 2025)
**Foundation Work**:
- Core IMG functionality
- Basic COL support
- Theme system foundation
- File operations
- UI improvements
- Menu system
- Tab management

---

## Statistics

### June 2025
- **Conception**: Img Factory 1.4 - X-Seti 
- **Successer to**: Img Factory 1.2 - MexUK
- **Revision**: Img Factory 1.3 (Patched) MexUK / X-Seti
- **Proof of conception**: Img Factory 1.4 was mean't to be a stand alone img editor: Plan and Simple.

### June 2025
- **Conception**: Img Factory 1.5 - X-Seti 
- **Proof of conception**: IMG Factory 1.5 main aim is to replace all existing gta tools.

### August 2025
- **Issues Fixed**: 15+
- **Features Added**: 10+
- **Code Cleaned**: Multiple files
- **Documentation**: Updated

### September 2025
- **Issues Fixed**: 5+
- **Features Added**: 3+

### October 2025  
- **Major Feature**: COL Viewer (complete)
- **Files Created**: 10+
- **Documentation**: 6 files
- **Materials Added**: 214 definitions

---

## Naming Conventions Applied
Throughout development, these rules have been enforced:

✅ **DO USE**:
- Simple, clear names
- Version numbers on methods
- Proper headers

❌ **DO NOT USE**:
- "Enhanced"
- "Fallback" 
- "Improved"
- "Fixed"
- "Fix"
- "Patch"
- "Patched"
- "Updated"
- "Integrated"
- "Clean"

**Reason**: Avoid confusion and duplication

---

## Known Issues (Moving to TODO)

Items from old changelog moved to TODO.md:
1. Tab system export/dump issues
2. Export combining files incorrectly
3. Dump function needs same logic as export
4. COL dialog hardcoded backgrounds
5. Import via IDE errors
6. Folder import options needed
7. Text file import needed
8. Drag and drop support
9. Highlighting function inaccuracy
10. Save Entry function issues
11. Theme switching from first page

See `TODO.md` for complete task list.

---

## Development Philosophy

**Established Standards**:
1. ✅ Clean code - no legacy bugs
2. ✅ No fallback code - works or doesn't
3. ✅ No patch files
4. ✅ Simple, clear naming
5. ✅ Check for duplicates first
6. ✅ Files under 90k
7. ✅ Proper version tracking
8. ✅ Complete documentation
9. ✅ User-first approach
10. ✅ Community-focused

---

## Contributors

**Primary Developer**: X-Seti (2025)
**Original COL Data**: Steve M., illspirit (2005)
**Community**: Testing and feedback

See `Credits.md` for complete attribution.

---

## Next Release

See `TODO.md` for planned features and fixes.

**Target Areas**:
- Tab system improvements
- Export/Dump fixes
- Theme system enhancements
- Import system improvements
- DFF texture mapping (future)

---

**Last Updated**: October 22, 2025
**Total Commits**: 100+ improvements
**Lines of Code**: 10,000+ (clean, documented)
**Community Impact**: Ongoing
