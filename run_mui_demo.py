#!/usr/bin/env python3
"""
Launcher for Amiga MUI Demo Application
"""

import sys
import os
from pathlib import Path

def main():
    # Add the workspace to the Python path
    workspace_dir = Path(__file__).parent.resolve()
    if str(workspace_dir) not in sys.path:
        sys.path.insert(0, str(workspace_dir))
    
    # Import and run the MUI demo
    try:
        from apps.components.Img_Factory.mui_demo import main as mui_main
        print("Starting Amiga MUI Demo Application...")
        mui_main()
    except ImportError as e:
        print(f"Error importing MUI demo: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running MUI demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()