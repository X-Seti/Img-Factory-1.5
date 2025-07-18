#this belongs in methods/populate_col_table.py - Version: 2
# X-Seti - July16 2025 - IMG Factory 1.5 - Populate collision table

"""
Table Structure Functions
Handles table population and setup for COL files
"""

import os
from typing import Optional, Any
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

## Methods list.
# populate_col_table
# populate_col_table_enh


class IMGLoadThread():
    def populate_col_table(table: QTableWidget, col_file, file_name): #vers 4
        """Populate table with COL models using same format as IMG entries"""
        # Keep the same 7-column format as IMG files
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Offset", "Version", "Compression", "Status"
        ])

        if not col_file or not hasattr(col_file, 'models') or not col_file.models:
            # Show the file itself if no models
            table.setRowCount(1)

            try:
                file_size = os.path.getsize(col_file.file_path) if col_file and hasattr(col_file, 'file_path') and col_file.file_path else 0
                size_text = format_file_size(file_size)
            except:
                size_text = "Unknown"

            items = [
                (file_name, "COL", size_text, "0x0", "Unknown", "None", "No Models")
            ]

            for row, item_data in enumerate(items):
                for col, value in enumerate(item_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(row, col, item)

            print(f"DEBUG: COL file loaded but no models found")
            return

        # Show individual models in IMG entry format
        models = col_file.models
        table.setRowCount(len(models))

        print(f"DEBUG: Populating table with {len(models)} COL models")

        virtual_offset = 0x0  # Virtual offset for COL models

        for row, model in enumerate(models):
            try:
                # Name - use model name or generate one
                model_name = getattr(model, 'name', f"Model_{row}") if hasattr(model, 'name') and model.name else f"Model_{row}"
                table.setItem(row, 0, QTableWidgetItem(model_name))

                # Type - just "COL" (like IMG shows "DFF", "TXD", etc.)
                table.setItem(row, 1, QTableWidgetItem("COL"))

                # Size - estimate COL model size
                try:
                    model_size = estimate_col_model_size_bytes(model)
                    size_text = format_file_size(model_size)
                except:
                    size_text = "1 KB"
                table.setItem(row, 2, QTableWidgetItem(size_text))

                # Virtual offset (increment for each model)
                table.setItem(row, 3, QTableWidgetItem(f"0x{virtual_offset:X}"))
                virtual_offset += 1024  # Increment by 1KB for next model

                # Version - try to get COL version
                try:
                    if hasattr(model, 'version') and hasattr(model.version, 'name'):
                        version_text = model.version.name
                    elif hasattr(model, 'version') and hasattr(model.version, 'value'):
                        version_text = f"COL{model.version.value}"
                    else:
                        version_text = "COL"
                except:
                    version_text = "COL"
                table.setItem(row, 4, QTableWidgetItem(version_text))

                # Compression - COL models aren't typically compressed
                table.setItem(row, 5, QTableWidgetItem("None"))

                # Status - always Ready for COL models
                table.setItem(row, 6, QTableWidgetItem("Ready"))

                # Make all items read-only
                for col in range(7):
                    item = table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            except Exception as e:
                print(f"DEBUG: Error populating COL model {row}: {str(e)}")
                # Create fallback row (same as IMG error handling)
                table.setItem(row, 0, QTableWidgetItem(f"Model_{row}"))
                table.setItem(row, 1, QTableWidgetItem("COL"))
                table.setItem(row, 2, QTableWidgetItem("0 B"))
                table.setItem(row, 3, QTableWidgetItem("0x0"))
                table.setItem(row, 4, QTableWidgetItem("Unknown"))
                table.setItem(row, 5, QTableWidgetItem("None"))
                table.setItem(row, 6, QTableWidgetItem("Error"))

        print(f"DEBUG: Table populated with {len(models)} COL models (IMG format)")


    def populate_col_table_enh(main_window, col_file): #vers 2
        """Populate table using enhanced display manager"""
        try:
            from components.col_display import COLDisplayManager

            display_manager = COLDisplayManager(main_window)
            display_manager.populate_col_table(col_file)
            main_window.log_message("✅ Enhanced COL table populated")

        except Exception as e:
            main_window.log_message(f"❌ Enhanced table population failed: {str(e)}")
            raise


def populate_col_table(main_window, col_file: Any) -> None: #vers 4
    """Populate table with COL data using complete parser for real collision data"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return

        table = main_window.gui_layout.table

        # Use the new complete parser to get real collision data
        try:
            from components.col_parser_rebuild import parse_col_file_complete

            main_window.log_message("🔧 Using complete COL parser for real collision data")
            parsed_models = parse_col_file_complete(col_file.file_path, debug=True)

            if not parsed_models:
                main_window.log_message("⚠️ Complete parser found no models")
                table.setRowCount(0)
                return

            # Set row count
            table.setRowCount(len(parsed_models))

            # Populate rows with real parsed collision data
            for i, model in enumerate(parsed_models):
                try:
                    stats = model.get_collision_stats()

                    # Column 0: Model name
                    table.setItem(i, 0, create_table_item(model.name))

                    # Column 1: Type/Version
                    table.setItem(i, 1, create_table_item(model.version))

                    # Column 2: Size
                    if model.size_bytes < 1024:
                        size_text = f"{model.size_bytes} B"
                    else:
                        size_text = f"{model.size_bytes // 1024} KB"
                    table.setItem(i, 2, create_table_item(size_text))

                    # Column 3: Surfaces (spheres + boxes)
                    surface_count = stats['surface_count']
                    table.setItem(i, 3, create_table_item(str(surface_count)))

                    # Column 4: Vertices
                    vertex_count = stats['vertex_count']
                    table.setItem(i, 4, create_table_item(str(vertex_count)))

                    # Column 5: Collision (descriptive)
                    collision_parts = []
                    if stats['sphere_count'] > 0:
                        collision_parts.append(f"Spheres({stats['sphere_count']})")
                    if stats['box_count'] > 0:
                        collision_parts.append(f"Boxes({stats['box_count']})")
                    if stats['face_count'] > 0:
                        collision_parts.append(f"Mesh({stats['face_count']})")

                    collision_text = ", ".join(collision_parts) if collision_parts else "None"
                    table.setItem(i, 5, create_table_item(collision_text))

                    # Column 6: Status
                    if stats['total_elements'] > 0:
                        table.setItem(i, 6, create_table_item("✓ Loaded"))
                    else:
                        table.setItem(i, 6, create_table_item("⚠ Empty"))

                    main_window.log_message(f"✅ Model {i} ({model.name}): {stats}")

                except Exception as e:
                    main_window.log_message(f"⚠️ Error populating row {i}: {str(e)}")
                    # Fill with error data
                    table.setItem(i, 0, create_table_item(f"model_{i}"))
                    table.setItem(i, 1, create_table_item("ERROR"))
                    table.setItem(i, 2, create_table_item("0 B"))
                    table.setItem(i, 3, create_table_item("0"))
                    table.setItem(i, 4, create_table_item("0"))
                    table.setItem(i, 5, create_table_item("Parse Error"))
                    table.setItem(i, 6, create_table_item("❌ Error"))

            main_window.log_message(f"✅ COL table populated with real data: {len(parsed_models)} models")

        except ImportError:
            main_window.log_message("❌ Complete COL parser not available, using fallback")
            # Fallback to old method
            if not hasattr(col_file, 'models') or not col_file.models:
                table.setRowCount(0)
                return

            table.setRowCount(len(col_file.models))
            for i, model in enumerate(col_file.models):
                table.setItem(i, 0, create_table_item(getattr(model, 'name', f'model_{i}')))
                table.setItem(i, 1, create_table_item("COL"))
                table.setItem(i, 2, create_table_item("Unknown"))
                table.setItem(i, 3, create_table_item("0"))
                table.setItem(i, 4, create_table_item("0"))
                table.setItem(i, 5, create_table_item("No Parser"))
                table.setItem(i, 6, create_table_item("⚠ Limited"))

    except Exception as e:
        main_window.log_message(f"❌ Error populating COL table: {str(e)}")


def create_table_item(text: str) -> QTableWidgetItem: #vers 3
    """Create table item with proper formatting"""
    item = QTableWidgetItem(str(text))
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item

# Export functions
__all__ = [
    'populate_col_table',
    'populate_col_table_enh'
]

