# this belongs in root/GUI_LAYOUT_RULES.md

# 🔒 IMG Factory 1.5 - GUI Layout Rules

## LOCKED STRUCTURE - DO NOT MODIFY

The GUI layout is **FINAL** and **LOCKED**. Any future modifications must follow these rules:

### ❌ PROHIBITED CHANGES
- **NEVER** change main window layout structure
- **NEVER** move left/right panel positions  
- **NEVER** change splitter orientations or proportions
- **NEVER** modify table + log vertical arrangement
- **NEVER** alter responsive button panel structure

### ✅ ALLOWED CHANGES
- Add new buttons to existing button groups
- Modify button labels, icons, or callbacks
- Add new action types for button theming
- Change button functionality/logic
- Add new groupboxes to right panel (append only)

### 📐 CURRENT LAYOUT STRUCTURE
```
┌─────────────────────────────────────────────────────────────────┐
│                    Main Window (1100x700)                      │
├─────────────────────────────┬───────────────────────────────────┤
│        Left Panel (66%)     │       Right Panel (33%)          │
│  ┌─────────────────────────┐ │  ┌─────────────────────────────┐  │
│  │    IMG Info Header      │ │  │    IMG Operations Group    │  │
│  ├─────────────────────────┤ │  ├─────────────────────────────┤  │
│  │                         │ │  │   Entry Operations Group   │  │
│  │    Entries Table (70%)  │ │  ├─────────────────────────────┤  │
│  │                         │ │  │   Filter & Search Group    │  │
│  ├─────────────────────────┤ │  └─────────────────────────────┘  │
│  │   Activity Log (30%)    │ │                                  │
│  └─────────────────────────┘ │                                  │
└─────────────────────────────┴───────────────────────────────────┘
```

### 🏗️ COMPONENT HIERARCHY (LOCKED)
```python
QMainWindow
├── QWidget (central)
│   └── QHBoxLayout (main)
│       ├── QWidget (left_panel) [66%]
│       │   └── QVBoxLayout
│       │       ├── QGroupBox (img_info)
│       │       └── QSplitter (vertical)
│       │           ├── QTableWidget (entries) [70%]
│       │           └── QTextEdit (log) [30%]
│       └── QWidget (right_panel) [33%]
│           └── QVBoxLayout
│               ├── QGroupBox (img_operations)
│               ├── QGroupBox (entry_operations)  
│               └── QGroupBox (filter_search)
```

### 🎯 BUTTON MODIFICATION GUIDE
When adding new buttons, use this pattern:
```python
# ✅ CORRECT: Add to existing group
self.img_buttons.append(new_button)

# ❌ WRONG: Create new layout structure  
new_layout = QHBoxLayout()  # DON'T DO THIS
```

### 📋 ENFORCEMENT
- All layout-related code has 🔒 LOCKED comments
- This file must be read before any GUI modifications
- Layout structure violations are considered critical bugs
- Only button content changes are permitted

**Last Layout Lock Date: June 26, 2025**
**Layout Version: 1.5.FINAL**
