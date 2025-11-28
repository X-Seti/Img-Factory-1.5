# IMG Factory 1.5 - Fix Summary

## November 29, 2025

### Fixed: Missing rebuild_img_file method in IMGFile class
- **Issue**: Error "'IMGFile' object has no attribute 'rebuild_img_file'" when importing new DFF models into IMG files
- **Root Cause**: The save_img_file() method was calling rebuild_img_file() but this method was missing from the IMGFile class
- **Solution**: Added the missing rebuild_img_file() method that calls the appropriate version-specific rebuild method (_rebuild_version1 or _rebuild_version2)
- **Files Modified**: 
  - /workspace/apps/methods/img_core_classes.py
  - /workspace/ChangeLog.md
- **Version Updates**:
  - save_img_file() method: vers 2
  - rebuild_img_file() method: vers 1
  - File version: 11

### Fixed: Import function conflicts
- **Issue**: Duplicate functions between core/impotr.py and core/import_via.py
- **Solution**: Created shared methods/common_functions.py module to consolidate duplicate functions
- **Files Modified**:
  - /workspace/apps/methods/common_functions.py (new)
  - /workspace/apps/core/impotr.py
  - /workspace/apps/core/import_via.py
  - /workspace/ChangeLog.md
