#this belongs in methods/export_col_shared.py - Version: 8
# X-Seti - August16 2025 - IMG Factory 1.5 - Shared COL Export Functions

"""
Shared COL Export Functions - Clean COL model extraction and export
Used by: export, export_via, dump functions
Provides single/combined COL file creation with proper model extraction
FIXED: Tab switching support and robust file detection
"""

import os
import struct
from typing import List, Dict, Any, Optional, Tuple
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# extract_single_col_model
# extract_selected_col_models
# create_single_col_file
# create_combined_col_file
# save_col_models_with_options
# get_col_models_from_selection
# integrate_col_export_shared

def extract_single_col_model(col_file, model_index: int) -> Optional[Any]: #vers 1
    """Extract single model from COL file and create new COL file object

    Args:
        col_file: Source COL file object
        model_index: Index of model to extract

    Returns:
        New COL file object with single model or None if failed
    """
    try:
        if not hasattr(col_file, 'models') or not col_file.models:
            return None

        if model_index < 0 or model_index >= len(col_file.models):
            return None

        # Import COL classes
        try:
            from components.col_core_classes import COLFile
        except ImportError:
            return None

        # Create new COL file with single model
        new_col_file = COLFile()
        source_model = col_file.models[model_index]

        # Deep copy the model data
        new_model = _copy_col_model(source_model)
        if not new_model:
            return None

        new_col_file.models = [new_model]
        new_col_file.is_loaded = True

        return new_col_file

    except Exception as e:
        return None


def extract_selected_col_models(col_file, model_indices: List[int]) -> Optional[Any]: #vers 1
    """Extract multiple models from COL file and create new COL file object

    Args:
        col_file: Source COL file object
        model_indices: List of model indices to extract

    Returns:
        New COL file object with selected models or None if failed
    """
    try:
        if not hasattr(col_file, 'models') or not col_file.models:
            return None

        if not model_indices:
            return None

        # Import COL classes
        try:
            from components.col_core_classes import COLFile
        except ImportError:
            return None

        # Create new COL file with selected models
        new_col_file = COLFile()
        new_models = []

        for model_index in model_indices:
            if 0 <= model_index < len(col_file.models):
                source_model = col_file.models[model_index]
                new_model = _copy_col_model(source_model)
                if new_model:
                    new_models.append(new_model)

        if not new_models:
            return None

        new_col_file.models = new_models
        new_col_file.is_loaded = True

        return new_col_file

    except Exception as e:
        return None


def _copy_col_model(source_model) -> Optional[Any]: #vers 1
    """Create a deep copy of a COL model

    Args:
        source_model: Source COL model to copy

    Returns:
        New COL model object or None if failed
    """
    try:
        # Import COL classes
        try:
            from components.col_core_classes import COLModel, COLVersion
        except ImportError:
            return None

        # Create new model
        new_model = COLModel()

        # Copy basic properties
        new_model.name = getattr(source_model, 'name', '')
        new_model.model_id = getattr(source_model, 'model_id', 0)
        new_model.version = getattr(source_model, 'version', COLVersion.COL_1)

        # Copy bounding box
        if hasattr(source_model, 'bounding_box') and source_model.bounding_box:
            new_model.bounding_box = _copy_bounding_box(source_model.bounding_box)

        # Copy collision data
        new_model.spheres = getattr(source_model, 'spheres', []).copy()
        new_model.boxes = getattr(source_model, 'boxes', []).copy()
        new_model.vertices = getattr(source_model, 'vertices', []).copy()
        new_model.faces = getattr(source_model, 'faces', []).copy()
        new_model.face_groups = getattr(source_model, 'face_groups', []).copy()
        new_model.shadow_vertices = getattr(source_model, 'shadow_vertices', []).copy()
        new_model.shadow_faces = getattr(source_model, 'shadow_faces', []).copy()

        # Copy flags and other properties
        new_model.flags = getattr(source_model, 'flags', 0)
        new_model.sphere_count = getattr(source_model, 'sphere_count', 0)
        new_model.box_count = getattr(source_model, 'box_count', 0)
        new_model.face_count = getattr(source_model, 'face_count', 0)

        return new_model

    except Exception as e:
        return None


def _copy_bounding_box(source_bbox) -> Optional[Any]: #vers 1
    """Copy bounding box object

    Args:
        source_bbox: Source bounding box

    Returns:
        New bounding box object or None
    """
    try:
        from components.col_core_classes import BoundingBox, Vector3

        new_bbox = BoundingBox()
        new_bbox.center = Vector3(source_bbox.center.x, source_bbox.center.y, source_bbox.center.z)
        new_bbox.min = Vector3(source_bbox.min.x, source_bbox.min.y, source_bbox.min.z)
        new_bbox.max = Vector3(source_bbox.max.x, source_bbox.max.y, source_bbox.max.z)
        new_bbox.radius = source_bbox.radius

        return new_bbox

    except Exception:
        return None


def create_single_col_file(col_entry: Dict[str, Any], output_path: str) -> bool: #vers 1
    """Create single COL file from col_entry

    Args:
        col_entry: Dictionary with model info
        output_path: Path to save file

    Returns:
        True if file created successfully
    """
    try:
        if 'col_file' not in col_entry or 'index' not in col_entry:
            return False

        col_file = col_entry['col_file']
        model_index = col_entry['index']

        # Extract single model
        single_col_file = extract_single_col_model(col_file, model_index)
        if not single_col_file:
            return False

        # Save to file
        single_col_file.file_path = output_path
        return single_col_file.save_to_file(output_path)

    except Exception as e:
        return False


def create_combined_col_file(col_entries: List[Dict[str, Any]], output_path: str) -> bool: #vers 1
    """Create combined COL file from multiple col_entries

    Args:
        col_entries: List of col_entry dictionaries
        output_path: Path to save combined file

    Returns:
        True if file created successfully
    """
    try:
        if not col_entries:
            return False

        # Get source COL file and model indices
        col_file = col_entries[0]['col_file']
        model_indices = [entry['index'] for entry in col_entries if 'index' in entry]

        if not model_indices:
            return False

        # Extract selected models
        combined_col_file = extract_selected_col_models(col_file, model_indices)
        if not combined_col_file:
            return False

        # Save to file
        combined_col_file.file_path = output_path
        return combined_col_file.save_to_file(output_path)

    except Exception as e:
        return False


def save_col_models_with_options(main_window, col_entries: List[Dict[str, Any]],
                                export_folder: str, single_files: bool = True,
                                combined_file: bool = False, combined_name: str = "combined_models.col") -> Tuple[int, int]: #vers 3
    """Save COL models with export options - FIXED: Optimized performance

    Args:
        main_window: Main application window
        col_entries: List of COL model entries
        export_folder: Export destination folder
        single_files: Export as separate files
        combined_file: Export as combined file
        combined_name: Name for combined file

    Returns:
        Tuple of (success_count, failed_count)
    """
    try:
        if not col_entries:
            return 0, 0

        success_count = 0
        failed_count = 0

        # FIXED: Add progress tracking for performance
        total_operations = (len(col_entries) if single_files else 0) + (1 if combined_file else 0)
        current_operation = 0

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 Starting COL export: {total_operations} operations")

        # Export single files
        if single_files:
            # Create collision subfolder
            single_folder = os.path.join(export_folder, 'collision')
            os.makedirs(single_folder, exist_ok=True)

            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"📁 Exporting {len(col_entries)} individual models...")

            for i, col_entry in enumerate(col_entries):
                try:
                    current_operation += 1

                    model_name = col_entry.get('name', 'unknown.col')
                    if not model_name.endswith('.col'):
                        model_name += '.col'

                    output_path = os.path.join(single_folder, model_name)

                    # FIXED: Progress logging every 5 items to reduce spam
                    if i % 5 == 0 or i == len(col_entries) - 1:
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"🔄 Processing {i+1}/{len(col_entries)}: {model_name}")

                    # FIXED: Use optimized creation
                    if create_single_col_file(col_entry, output_path):
                        success_count += 1
                    else:
                        failed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"❌ Failed: {model_name}")

                except Exception as e:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Error creating {col_entry.get('name', 'unknown')}: {str(e)}")

        # Export combined file
        if combined_file:
            try:
                current_operation += 1
                combined_path = os.path.join(export_folder, combined_name)

                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"📦 Creating combined file: {combined_name}")

                if create_combined_col_file(col_entries, combined_path):
                    success_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"✅ Combined file created: {combined_name}")
                else:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Failed to create combined file: {combined_name}")

            except Exception as e:
                failed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Error creating combined file: {str(e)}")

        # FIXED: Final summary
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🏁 COL export complete: {success_count} success, {failed_count} failed")

        return success_count, failed_count

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error in save_col_models_with_options: {str(e)}")
        return 0, len(col_entries) if col_entries else 0


def get_col_models_from_selection(main_window) -> List[Dict[str, Any]]: #vers 4
    """Get COL models from current tab selection - FIXED: Comprehensive debugging
    
    Args:
        main_window: Main application window
        
    Returns:
        List of col_entry dictionaries for selected models
    """
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔍 === COL MODELS DEBUG START ===")
        
        # DEBUG: Check tab widget exists
        if not hasattr(main_window, 'main_tab_widget'):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No main_tab_widget attribute found!")
            return []
        
        # DEBUG: Tab info
        current_index = main_window.main_tab_widget.currentIndex()
        total_tabs = main_window.main_tab_widget.count()
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Tab info: Current={current_index}, Total={total_tabs}")
        
        if current_index == -1:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No active tab!")
            return []
        
        # DEBUG: Get current tab widget
        current_tab = main_window.main_tab_widget.widget(current_index)
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Current tab widget: {type(current_tab).__name__ if current_tab else 'None'}")
        
        if not current_tab:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Current tab widget is None!")
            return []
        
        # DEBUG: List ALL attributes of the tab
        if hasattr(main_window, 'log_message'):
            tab_attrs = [attr for attr in dir(current_tab) if not attr.startswith('_')]
            main_window.log_message(f"🔍 Tab attributes: {tab_attrs[:10]}...")  # Show first 10
        
        # DEBUG: Check for file objects
        file_object = None
        file_source = "none"
        
        # Method 1: Direct attributes
        if hasattr(current_tab, 'col_file') and current_tab.col_file:
            file_object = current_tab.col_file
            file_source = "tab.col_file"
        elif hasattr(current_tab, 'img_file') and current_tab.img_file:
            file_object = current_tab.img_file
            file_source = "tab.img_file"
        elif hasattr(current_tab, 'file_data') and current_tab.file_data:
            file_object = current_tab.file_data
            file_source = "tab.file_data"
        elif hasattr(current_tab, 'current_file') and current_tab.current_file:
            file_object = current_tab.current_file
            file_source = "tab.current_file"
        
        # Method 2: Scan all attributes
        if not file_object:
            for attr_name in dir(current_tab):
                if not attr_name.startswith('_'):
                    try:
                        attr_value = getattr(current_tab, attr_name)
                        if attr_value and hasattr(attr_value, 'models'):
                            file_object = attr_value
                            file_source = f"tab.{attr_name}"
                            break
                        elif attr_value and hasattr(attr_value, 'entries'):
                            file_object = attr_value
                            file_source = f"tab.{attr_name}"
                            break
                    except:
                        continue
        
        # DEBUG: File detection results
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 File detection: {file_source}")
            main_window.log_message(f"🔍 File object: {type(file_object).__name__ if file_object else 'None'}")
            
            if file_object:
                if hasattr(file_object, 'models'):
                    model_count = len(file_object.models) if file_object.models else 0
                    main_window.log_message(f"🔍 COL file with {model_count} models")
                elif hasattr(file_object, 'entries'):
                    entry_count = len(file_object.entries) if file_object.entries else 0
                    main_window.log_message(f"🔍 IMG file with {entry_count} entries")
                else:
                    main_window.log_message(f"🔍 Unknown file type")
        
        # DEBUG: Check main window references too
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 main_window.current_col: {type(main_window.current_col).__name__ if main_window.current_col else 'None'}")
            main_window.log_message(f"🔍 main_window.current_img: {type(main_window.current_img).__name__ if main_window.current_img else 'None'}")
        
        # If we found a COL file, process it
        if file_object and hasattr(file_object, 'models'):
            models = file_object.models
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Found COL file with {len(models) if models else 0} models")
            
            if models:
                all_col_entries = []
                for i, model in enumerate(models):
                    try:
                        model_name = getattr(model, 'name', f'model_{i}')
                        if not model_name.endswith('.col'):
                            model_name += '.col'
                        
                        col_entry = {
                            'name': model_name,
                            'type': 'COL_MODEL',
                            'model': model,
                            'index': i,
                            'col_file': file_object
                        }
                        all_col_entries.append(col_entry)
                    except Exception as e:
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"⚠️ Error processing model {i}: {str(e)}")
                
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ Created {len(all_col_entries)} COL entries")
                    main_window.log_message("🔍 === COL MODELS DEBUG END ===")
                return all_col_entries
        
        # If we get here, no COL file found
        if hasattr(main_window, 'log_message'):
            main_window.log_message("❌ No COL file found in current tab")
            main_window.log_message("🔍 === COL MODELS DEBUG END ===")
        return []

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error in get_col_models_from_selection: {str(e)}")
            main_window.log_message("🔍 === COL MODELS DEBUG END ===")
        return []


def integrate_col_export_shared(main_window) -> bool: #vers 1
    """Integrate COL export shared functions into main window

    Args:
        main_window: Main application window

    Returns:
        True if integration successful
    """
    try:
        # Add COL export functions to main window
        main_window.extract_single_col_model = lambda col_file, idx: extract_single_col_model(col_file, idx)
        main_window.extract_selected_col_models = lambda col_file, indices: extract_selected_col_models(col_file, indices)
        main_window.create_single_col_file = lambda entry, path: create_single_col_file(entry, path)
        main_window.create_combined_col_file = lambda entries, path: create_combined_col_file(entries, path)
        main_window.save_col_models_with_options = lambda entries, folder, single=True, combined=False, name="combined_models.col": save_col_models_with_options(main_window, entries, folder, single, combined, name)
        main_window.get_col_models_from_selection = lambda: get_col_models_from_selection(main_window)

        # Add convenience functions
        main_window.export_single_col_models = lambda entries, folder: save_col_models_with_options(main_window, entries, folder, single_files=True, combined_file=False)[0] > 0
        main_window.export_combined_col_file = lambda entries, folder, name="combined_models.col": save_col_models_with_options(main_window, entries, folder, single_files=False, combined_file=True, combined_name=name)[0] > 0

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ COL export shared functions integrated")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error integrating COL export shared functions: {str(e)}")
        return False


__all__ = [
    'extract_single_col_model',
    'extract_selected_col_models',
    'create_single_col_file',
    'create_combined_col_file',
    'save_col_models_with_options',
    'get_col_models_from_selection',
    'integrate_col_export_shared'
]
