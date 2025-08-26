#this belongs in components/ txd_editor.py - Version: 2
# X-Seti - August26 2025 - IMG Factory 1.5 -
#!/usr/bin/env python3
"""
Inspired by Paint.NET functionality

Todo:

Issue 2, Not displaying the textures (only I static pick background)
issue 3, show a thumbnail/alpha image in the texture list.
Issue 1, Load Dff file texture list, and compare against loaded txd.
issue 4, Sllow the GUI to use this json theme- the themer_settings.json

Save txd as SA, LC and VC, batch convertion for multiply txd's in a folder or img.

"""


import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import struct
import os
import io
import math
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import IntEnum
import threading
import requests
from urllib.parse import urlparse
from txd_editor import TXDEditor

# Previous TXD classes remain the same...
class RasterFormat(IntEnum):
    """RenderWare raster format constants"""
    DEFAULT = 0x0000
    C1555 = 0x0100
    C565 = 0x0200
    C4444 = 0x0300
    LUM8 = 0x0400
    C8888 = 0x0500
    C888 = 0x0600
    D16 = 0x0700
    D24 = 0x0800
    D32 = 0x0900
    C555 = 0x0A00
    AUTOMIPMAP = 0x1000
    PAL8 = 0x2000
    PAL4 = 0x4000
    MIPMAP = 0x8000

@dataclass
class Layer:
    """Image layer for editing"""
    name: str
    image: Image.Image
    visible: bool = True
    opacity: float = 1.0
    blend_mode: str = "normal"

@dataclass
class EditHistory:
    """Undo/Redo history entry"""
    action: str
    image_before: Image.Image
    image_after: Image.Image
    timestamp: float

class ImageUpscaler:
    """AI-based image upscaling using various methods"""

    @staticmethod
    def upscale_nearest(image: Image.Image, scale: int) -> Image.Image:
        """Simple nearest neighbor upscaling"""
        new_size = (image.width * scale, image.height * scale)
        return image.resize(new_size, Image.Resampling.NEAREST)

    @staticmethod
    def upscale_lanczos(image: Image.Image, scale: int) -> Image.Image:
        """Lanczos upscaling (good quality)"""
        new_size = (image.width * scale, image.height * scale)
        return image.resize(new_size, Image.Resampling.LANCZOS)

    @staticmethod
    def upscale_bicubic(image: Image.Image, scale: int) -> Image.Image:
        """Bicubic upscaling"""
        new_size = (image.width * scale, image.height * scale)
        return image.resize(new_size, Image.Resampling.BICUBIC)

    @staticmethod
    def upscale_esrgan_simulation(image: Image.Image, scale: int) -> Image.Image:
        """Simulated ESRGAN-style upscaling using advanced filtering"""
        # This is a simplified simulation - for real ESRGAN you'd need the actual model

        # First pass: Lanczos upscale
        new_size = (image.width * scale, image.height * scale)
        upscaled = image.resize(new_size, Image.Resampling.LANCZOS)

        # Apply sharpening filter to simulate AI enhancement
        upscaled = upscaled.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

        # Reduce noise
        upscaled = upscaled.filter(ImageFilter.MedianFilter(size=3))

        # Enhance details
        enhancer = ImageEnhance.Sharpness(upscaled)
        upscaled = enhancer.enhance(1.2)

        return upscaled

    @staticmethod
    def upscale_waifu2x_simulation(image: Image.Image, scale: int) -> Image.Image:
        """Simulated Waifu2x-style upscaling for anime/cartoon images"""
        # Convert to numpy for processing
        img_array = np.array(image)

        # Simple edge-preserving upscale simulation
        new_size = (image.width * scale, image.height * scale)
        upscaled = image.resize(new_size, Image.Resampling.LANCZOS)

        # Apply bilateral filter simulation (edge-preserving smoothing)
        upscaled = upscaled.filter(ImageFilter.SMOOTH_MORE)

        # Enhance contrast slightly
        enhancer = ImageEnhance.Contrast(upscaled)
        upscaled = enhancer.enhance(1.1)

        return upscaled

class ImageEditor:
    """Integrated image editor with Paint.NET-like features"""

    def __init__(self, parent, image: Image.Image, callback=None):
        self.parent = parent
        self.original_image = image.copy()
        self.current_image = image.copy()
        self.callback = callback

        # Editor state
        self.layers = [Layer("Background", image.copy())]
        self.current_layer = 0
        self.history = []
        self.history_index = -1
        self.max_history = 50

        # Tools
        self.current_tool = "select"
        self.brush_size = 5
        self.brush_color = (0, 0, 0, 255)
        self.selection_rect = None

        # Create editor window
        self.setup_editor_window()

    def setup_editor_window(self):
        """Setup the image editor window"""
        self.editor_window = tk.Toplevel(self.parent)
        self.editor_window.title("Image Editor")
        self.editor_window.geometry("1000x700")

        # Create main layout
        self.setup_editor_ui()

        # Load initial image
        self.update_canvas()

    def setup_editor_ui(self):
        """Setup editor UI"""
        # Menu bar
        self.setup_editor_menu()

        # Main container
        main_frame = ttk.Frame(self.editor_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - tools and layers
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)

        # Tools panel
        self.setup_tools_panel(left_panel)

        # Layers panel
        self.setup_layers_panel(left_panel)

        # Center - canvas
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas with scrollbars
        canvas_container = ttk.Frame(canvas_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.editor_canvas = tk.Canvas(canvas_container, bg='gray90')
        h_scroll = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.editor_canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.editor_canvas.yview)
        self.editor_canvas.config(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        self.editor_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)

        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)

        # Bind canvas events
        self.editor_canvas.bind("<Button-1>", self.on_canvas_click)
        self.editor_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.editor_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # Right panel - properties and effects
        right_panel = ttk.Frame(main_frame, width=200)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)

        self.setup_properties_panel(right_panel)
        self.setup_effects_panel(right_panel)

    def setup_editor_menu(self):
        """Setup editor menu"""
        menubar = tk.Menu(self.editor_window)
        self.editor_window.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Apply Changes", command=self.apply_changes)
        file_menu.add_command(label="Cancel", command=self.cancel_changes)
        file_menu.add_separator()
        file_menu.add_command(label="Export...", command=self.export_image)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy_selection)
        edit_menu.add_command(label="Paste", command=self.paste_selection)
        edit_menu.add_command(label="Clear", command=self.clear_selection)

        # Image menu
        image_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Image", menu=image_menu)
        image_menu.add_command(label="Resize...", command=self.resize_image)
        image_menu.add_command(label="Rotate 90° CW", command=lambda: self.rotate_image(90))
        image_menu.add_command(label="Rotate 90° CCW", command=lambda: self.rotate_image(-90))
        image_menu.add_command(label="Flip Horizontal", command=self.flip_horizontal)
        image_menu.add_command(label="Flip Vertical", command=self.flip_vertical)

        # Upscale submenu
        upscale_menu = tk.Menu(image_menu, tearoff=0)
        image_menu.add_cascade(label="Upscale", menu=upscale_menu)
        upscale_menu.add_command(label="2x Nearest", command=lambda: self.upscale_image("nearest", 2))
        upscale_menu.add_command(label="2x Lanczos", command=lambda: self.upscale_image("lanczos", 2))
        upscale_menu.add_command(label="2x ESRGAN-style", command=lambda: self.upscale_image("esrgan", 2))
        upscale_menu.add_command(label="2x Waifu2x-style", command=lambda: self.upscale_image("waifu2x", 2))
        upscale_menu.add_separator()
        upscale_menu.add_command(label="4x Nearest", command=lambda: self.upscale_image("nearest", 4))
        upscale_menu.add_command(label="4x Lanczos", command=lambda: self.upscale_image("lanczos", 4))
        upscale_menu.add_command(label="4x ESRGAN-style", command=lambda: self.upscale_image("esrgan", 4))

        # Filters menu
        filters_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Filters", menu=filters_menu)
        filters_menu.add_command(label="Blur", command=lambda: self.apply_filter("blur"))
        filters_menu.add_command(label="Sharpen", command=lambda: self.apply_filter("sharpen"))
        filters_menu.add_command(label="Edge Enhance", command=lambda: self.apply_filter("edge_enhance"))
        filters_menu.add_command(label="Emboss", command=lambda: self.apply_filter("emboss"))
        filters_menu.add_command(label="Find Edges", command=lambda: self.apply_filter("find_edges"))
        filters_menu.add_separator()
        filters_menu.add_command(label="Gaussian Blur...", command=self.gaussian_blur_dialog)
        filters_menu.add_command(label="Unsharp Mask...", command=self.unsharp_mask_dialog)

        # Adjustments menu
        adj_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Adjustments", menu=adj_menu)
        adj_menu.add_command(label="Brightness/Contrast...", command=self.brightness_contrast_dialog)
        adj_menu.add_command(label="Hue/Saturation...", command=self.hue_saturation_dialog)
        adj_menu.add_command(label="Color Balance...", command=self.color_balance_dialog)
        adj_menu.add_command(label="Auto Levels", command=self.auto_levels)
        adj_menu.add_command(label="Invert", command=self.invert_colors)

        # Bind shortcuts
        self.editor_window.bind('<Control-z>', lambda e: self.undo())
        self.editor_window.bind('<Control-y>', lambda e: self.redo())

    def setup_tools_panel(self, parent):
        """Setup tools panel"""
        tools_frame = ttk.LabelFrame(parent, text="Tools")
        tools_frame.pack(fill=tk.X, pady=(0, 5))

        # Tool buttons
        tools = [
            ("Select", "select", "🔲"),
            ("Brush", "brush", "🖌️"),
            ("Eraser", "eraser", "🧽"),
            ("Fill", "fill", "🪣"),
            ("Eyedropper", "eyedropper", "💧"),
            ("Text", "text", "📝")
        ]

        self.tool_var = tk.StringVar(value="select")

        for i, (name, tool, icon) in enumerate(tools):
            row, col = divmod(i, 2)
            btn = ttk.Radiobutton(tools_frame, text=f"{icon} {name}", variable=self.tool_var,
                                value=tool, command=lambda t=tool: self.set_tool(t))
            btn.grid(row=row, column=col, sticky=tk.W, padx=2, pady=1)

        # Brush settings
        brush_frame = ttk.LabelFrame(parent, text="Brush")
        brush_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(brush_frame, text="Size:").pack(anchor=tk.W, padx=5)
        self.brush_size_var = tk.IntVar(value=5)
        brush_scale = ttk.Scale(brush_frame, from_=1, to=50, variable=self.brush_size_var,
                              orient=tk.HORIZONTAL, command=self.on_brush_size_change)
        brush_scale.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Color picker
        color_frame = ttk.Frame(brush_frame)
        color_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Label(color_frame, text="Color:").pack(side=tk.LEFT)
        self.color_button = tk.Button(color_frame, width=3, height=1, bg="black",
                                    command=self.choose_color)
        self.color_button.pack(side=tk.RIGHT)

    def setup_layers_panel(self, parent):
        """Setup layers panel"""
        layers_frame = ttk.LabelFrame(parent, text="Layers")
        layers_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Layer list
        self.layers_listbox = tk.Listbox(layers_frame, height=6)
        self.layers_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.layers_listbox.bind('<<ListboxSelect>>', self.on_layer_select)

        # Layer buttons
        layer_buttons = ttk.Frame(layers_frame)
        layer_buttons.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Button(layer_buttons, text="Add", command=self.add_layer, width=8).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(layer_buttons, text="Delete", command=self.delete_layer, width=8).pack(side=tk.LEFT, padx=2)

        # Layer opacity
        ttk.Label(layers_frame, text="Opacity:").pack(anchor=tk.W, padx=5)
        self.opacity_var = tk.DoubleVar(value=1.0)
        opacity_scale = ttk.Scale(layers_frame, from_=0.0, to=1.0, variable=self.opacity_var,
                                orient=tk.HORIZONTAL, command=self.on_opacity_change)
        opacity_scale.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.update_layers_list()

    def setup_properties_panel(self, parent):
        """Setup properties panel"""
        props_frame = ttk.LabelFrame(parent, text="Properties")
        props_frame.pack(fill=tk.X, pady=(0, 5))

        # Image info
        self.info_labels = {}
        info_items = [("Size:", "size"), ("Mode:", "mode"), ("Layers:", "layers")]

        for i, (label, key) in enumerate(info_items):
            ttk.Label(props_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            info_label = ttk.Label(props_frame, text="-")
            info_label.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            self.info_labels[key] = info_label

        self.update_properties()

    def setup_effects_panel(self, parent):
        """Setup effects panel"""
        effects_frame = ttk.LabelFrame(parent, text="Quick Effects")
        effects_frame.pack(fill=tk.X)

        effects = [
            ("Blur", lambda: self.apply_filter("blur")),
            ("Sharpen", lambda: self.apply_filter("sharpen")),
            ("Emboss", lambda: self.apply_filter("emboss")),
            ("Invert", self.invert_colors),
            ("Auto Levels", self.auto_levels),
            ("Noise Reduction", self.reduce_noise)
        ]

        for i, (name, command) in enumerate(effects):
            ttk.Button(effects_frame, text=name, command=command).pack(fill=tk.X, padx=5, pady=2)

    def set_tool(self, tool):
        """Set current tool"""
        self.current_tool = tool

    def on_brush_size_change(self, value):
        """Handle brush size change"""
        self.brush_size = int(float(value))

    def choose_color(self):
        """Choose brush color"""
        color = colorchooser.askcolor(color=self.brush_color[:3])
        if color[0]:
            self.brush_color = tuple(int(c) for c in color[0]) + (255,)
            hex_color = f"#{int(color[0][0]):02x}{int(color[0][1]):02x}{int(color[0][2]):02x}"
            self.color_button.config(bg=hex_color)

    def on_canvas_click(self, event):
        """Handle canvas click"""
        x = self.editor_canvas.canvasx(event.x)
        y = self.editor_canvas.canvasy(event.y)

        if self.current_tool == "brush":
            self.start_brush_stroke(x, y)
        elif self.current_tool == "eraser":
            self.start_erase_stroke(x, y)
        elif self.current_tool == "fill":
            self.flood_fill(x, y)
        elif self.current_tool == "eyedropper":
            self.pick_color(x, y)

    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        x = self.editor_canvas.canvasx(event.x)
        y = self.editor_canvas.canvasy(event.y)

        if self.current_tool == "brush":
            self.continue_brush_stroke(x, y)
        elif self.current_tool == "eraser":
            self.continue_erase_stroke(x, y)

    def on_canvas_release(self, event):
        """Handle canvas release"""
        if self.current_tool in ["brush", "eraser"]:
            self.end_stroke()

    def start_brush_stroke(self, x, y):
        """Start brush stroke"""
        self.add_to_history("Brush stroke")
        self.last_brush_pos = (x, y)
        self.draw_brush_point(x, y)

    def continue_brush_stroke(self, x, y):
        """Continue brush stroke"""
        if hasattr(self, 'last_brush_pos'):
            self.draw_brush_line(self.last_brush_pos, (x, y))
            self.last_brush_pos = (x, y)

    def draw_brush_point(self, x, y):
        """Draw brush point"""
        layer = self.layers[self.current_layer]
        draw = ImageDraw.Draw(layer.image)

        # Convert canvas coordinates to image coordinates
        img_x = int(x)
        img_y = int(y)

        # Draw circle
        radius = self.brush_size // 2
        draw.ellipse([img_x - radius, img_y - radius, img_x + radius, img_y + radius],
                    fill=self.brush_color)

        self.update_canvas()

    def draw_brush_line(self, start, end):
        """Draw brush line"""
        layer = self.layers[self.current_layer]
        draw = ImageDraw.Draw(layer.image)

        # Convert coordinates
        x1, y1 = int(start[0]), int(start[1])
        x2, y2 = int(end[0]), int(end[1])

        # Draw line with brush size
        draw.line([x1, y1, x2, y2], fill=self.brush_color, width=self.brush_size)

        self.update_canvas()

    def end_stroke(self):
        """End brush/eraser stroke"""
        if hasattr(self, 'last_brush_pos'):
            del self.last_brush_pos

    def upscale_image(self, method: str, scale: int):
        """Upscale image using specified method"""
        self.add_to_history(f"Upscale {scale}x {method}")

        layer = self.layers[self.current_layer]

        try:
            if method == "nearest":
                upscaled = ImageUpscaler.upscale_nearest(layer.image, scale)
            elif method == "lanczos":
                upscaled = ImageUpscaler.upscale_lanczos(layer.image, scale)
            elif method == "esrgan":
                upscaled = ImageUpscaler.upscale_esrgan_simulation(layer.image, scale)
            elif method == "waifu2x":
                upscaled = ImageUpscaler.upscale_waifu2x_simulation(layer.image, scale)
            else:
                upscaled = ImageUpscaler.upscale_lanczos(layer.image, scale)

            layer.image = upscaled

            # Update all layers to match new size
            for other_layer in self.layers:
                if other_layer != layer:
                    other_layer.image = other_layer.image.resize(upscaled.size, Image.Resampling.LANCZOS)

            self.update_canvas()
            self.update_properties()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to upscale image: {e}")

    def apply_filter(self, filter_name: str):
        """Apply image filter"""
        self.add_to_history(f"Filter: {filter_name}")

        layer = self.layers[self.current_layer]

        try:
            if filter_name == "blur":
                filtered = layer.image.filter(ImageFilter.BLUR)
            elif filter_name == "sharpen":
                filtered = layer.image.filter(ImageFilter.SHARPEN)
            elif filter_name == "edge_enhance":
                filtered = layer.image.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_name == "emboss":
                filtered = layer.image.filter(ImageFilter.EMBOSS)
            elif filter_name == "find_edges":
                filtered = layer.image.filter(ImageFilter.FIND_EDGES)
            else:
                return

            layer.image = filtered
            self.update_canvas()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {e}")

    def brightness_contrast_dialog(self):
        """Show brightness/contrast adjustment dialog"""
        dialog = BrightnessContrastDialog(self.editor_window, self.layers[self.current_layer].image)
        if dialog.result:
            self.add_to_history("Brightness/Contrast")
            self.layers[self.current_layer].image = dialog.result
            self.update_canvas()

    def gaussian_blur_dialog(self):
        """Show gaussian blur dialog"""
        radius = simpledialog.askfloat("Gaussian Blur", "Enter blur radius:", initialvalue=2.0, minvalue=0.1, maxvalue=10.0)
        if radius:
            self.add_to_history("Gaussian Blur")
            layer = self.layers[self.current_layer]
            layer.image = layer.image.filter(ImageFilter.GaussianBlur(radius=radius))
            self.update_canvas()

    def unsharp_mask_dialog(self):
        """Show unsharp mask dialog"""
        dialog = UnsharpMaskDialog(self.editor_window, self.layers[self.current_layer].image)
        if dialog.result:
            self.add_to_history("Unsharp Mask")
            self.layers[self.current_layer].image = dialog.result
            self.update_canvas()

    def resize_image(self):
        """Resize image dialog"""
        current_size = self.layers[0].image.size
        dialog = ResizeDialog(self.editor_window, current_size)
        if dialog.result:
            self.add_to_history("Resize")
            new_size = dialog.result

            for layer in self.layers:
                layer.image = layer.image.resize(new_size, Image.Resampling.LANCZOS)

            self.update_canvas()
            self.update_properties()

    def rotate_image(self, angle: int):
        """Rotate image"""
        self.add_to_history(f"Rotate {angle}°")

        for layer in self.layers:
            layer.image = layer.image.rotate(angle, expand=True)

        self.update_canvas()
        self.update_properties()

    def flip_horizontal(self):
        """Flip image horizontally"""
        self.add_to_history("Flip Horizontal")

        for layer in self.layers:
            layer.image = layer.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

        self.update_canvas()

    def flip_vertical(self):
        """Flip image vertically"""
        self.add_to_history("Flip Vertical")

        for layer in self.layers:
            layer.image = layer.image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        self.update_canvas()

    def invert_colors(self):
        """Invert image colors"""
        self.add_to_history("Invert Colors")

        layer = self.layers[self.current_layer]
        layer.image = ImageOps.invert(layer.image.convert('RGB'))
        if layer.image.mode != self.original_image.mode:
            layer.image = layer.image.convert(self.original_image.mode)

        self.update_canvas()

    def auto_levels(self):
        """Auto adjust levels"""
        self.add_to_history("Auto Levels")

        layer = self.layers[self.current_layer]
        layer.image = ImageOps.autocontrast(layer.image)

        self.update_canvas()

    def reduce_noise(self):
        """Reduce image noise"""
        self.add_to_history("Noise Reduction")

        layer = self.layers[self.current_layer]
        # Apply median filter for noise reduction
        layer.image = layer.image.filter(ImageFilter.MedianFilter(size=3))

        self.update_canvas()

    def add_layer(self):
        """Add new layer"""
        name = simpledialog.askstring("New Layer", "Enter layer name:", initialvalue=f"Layer {len(self.layers) + 1}")
        if name:
            # Create transparent layer with same size as base
            base_size = self.layers[0].image.size
            new_layer = Layer(name, Image.new('RGBA', base_size, (0, 0, 0, 0)))
            self.layers.append(new_layer)
            self.update_layers_list()

    def delete_layer(self):
        """Delete current layer"""
        if len(self.layers) > 1 and self.current_layer > 0:
            del self.layers[self.current_layer]
            self.current_layer = min(self.current_layer, len(self.layers) - 1)
            self.update_layers_list()
            self.update_canvas()

    def on_layer_select(self, event):
        """Handle layer selection"""
        selection = self.layers_listbox.curselection()
        if selection:
            self.current_layer = selection[0]
            layer = self.layers[self.current_layer]
            self.opacity_var.set(layer.opacity)

    def on_opacity_change(self, value):
        """Handle layer opacity change"""
        if self.layers:
            self.layers[self.current_layer].opacity = float(value)
            self.update_canvas()

    def update_layers_list(self):
        """Update layers list"""
        self.layers_listbox.delete(0, tk.END)
        for i, layer in enumerate(self.layers):
            status = "👁" if layer.visible else "🚫"
            self.layers_listbox.insert(0, f"{status} {layer.name}")

        if self.layers:
            self.layers_listbox.selection_set(len(self.layers) - 1 - self.current_layer)

    def update_properties(self):
        """Update properties display"""
        if self.layers:
            base_layer = self.layers[0]
            self.info_labels["size"].config(text=f"{base_layer.image.width}x{base_layer.image.height}")
            self.info_labels["mode"].config(text=base_layer.image.mode)
            self.info_labels["layers"].config(text=str(len(self.layers)))

    def add_to_history(self, action: str):
        """Add action to history for undo/redo"""
        if len(self.history) >= self.max_history:
            self.history.pop(0)

        # Remove any history after current index (for new branch)
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]

        # Create history entry
        current_state = self.get_current_state()
        entry = EditHistory(action, self.get_current_state(), None, 0)
        self.history.append(entry)
        self.history_index = len(self.history) - 1

    def get_current_state(self) -> Image.Image:
        """Get current composite image state"""
        if not self.layers:
            return Image.new('RGBA', (100, 100), (255, 255, 255, 255))

        # Composite all visible layers
        base = self.layers[0].image.copy().convert('RGBA')

        for layer in self.layers[1:]:
            if layer.visible and layer.opacity > 0:
                layer_img = layer.image.copy().convert('RGBA')

                # Apply opacity
                if layer.opacity < 1.0:
                    alpha = layer_img.split()[-1]
                    alpha = alpha.point(lambda p: int(p * layer.opacity))
                    layer_img.putalpha(alpha)

                # Composite layer
                base = Image.alpha_composite(base, layer_img)

        return base

    def undo(self):
        """Undo last action"""
        if self.history_index > 0:
            self.history_index -= 1
            # Restore previous state
            self.restore_state(self.history[self.history_index].image_before)
            self.update_canvas()

    def redo(self):
        """Redo last undone action"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            # Restore next state
            self.restore_state(self.history[self.history_index].image_after)
            self.update_canvas()

    def restore_state(self, image: Image.Image):
        """Restore image state"""
        # For simplicity, just update the current layer
        # In a full implementation, you'd save/restore all layers
        if self.layers:
            self.layers[self.current_layer].image = image.copy()

    def update_canvas(self):
        """Update canvas display"""
        try:
            # Get composite image
            composite = self.get_current_state()

            # Convert to display format
            if composite.mode == 'RGBA':
                # Create checkerboard background for transparency
                bg = self.create_checkerboard(composite.size)
                display_img = Image.alpha_composite(bg, composite)
            else:
                display_img = composite.convert('RGB')

            # Convert to PhotoImage
            self.canvas_image = ImageTk.PhotoImage(display_img)

            # Update canvas
            self.editor_canvas.delete("all")
            self.editor_canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
            self.editor_canvas.config(scrollregion=self.editor_canvas.bbox("all"))

        except Exception as e:
            print(f"Error updating canvas: {e}")

    def create_checkerboard(self, size: Tuple[int, int], square_size: int = 10) -> Image.Image:
        """Create checkerboard background for transparency"""
        width, height = size
        img = Image.new('RGB', size, (255, 255, 255))
        draw = ImageDraw.Draw(img)

        for x in range(0, width, square_size * 2):
            for y in range(0, height, square_size * 2):
                # Draw gray squares in checkerboard pattern
                draw.rectangle([x, y, x + square_size, y + square_size], fill=(200, 200, 200))
                draw.rectangle([x + square_size, y + square_size,
                              x + square_size * 2, y + square_size * 2], fill=(200, 200, 200))

        return img

    def apply_changes(self):
        """Apply changes and close editor"""
        try:
            # Get final composite image
            result = self.get_current_state()

            # Convert back to original mode if needed
            if result.mode != self.original_image.mode:
                if self.original_image.mode == 'RGB' and result.mode == 'RGBA':
                    # Composite with white background
                    bg = Image.new('RGB', result.size, (255, 255, 255))
                    result = Image.alpha_composite(bg.convert('RGBA'), result).convert('RGB')
                else:
                    result = result.convert(self.original_image.mode)

            # Call callback with result
            if self.callback:
                self.callback(result)

            self.editor_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply changes: {e}")

    def cancel_changes(self):
        """Cancel changes and close editor"""
        self.editor_window.destroy()

    def export_image(self):
        """Export current image"""
        filename = filedialog.asksaveasfilename(
            title="Export Image",
            defaultextension=".png",
            filetypes=[
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg"),
                ("Bitmap Files", "*.bmp"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            try:
                result = self.get_current_state()
                result.save(filename)
                messagebox.showinfo("Success", f"Image exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export image: {e}")

class BrightnessContrastDialog:
    """Dialog for brightness/contrast adjustment"""

    def __init__(self, parent, image: Image.Image):
        self.original_image = image.copy()
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Brightness/Contrast")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        self.setup_dialog()

    def setup_dialog(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Preview
        preview_frame = ttk.LabelFrame(main_frame, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(padx=5, pady=5)

        # Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Brightness
        ttk.Label(controls_frame, text="Brightness:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.brightness_var = tk.DoubleVar(value=0)
        brightness_scale = ttk.Scale(controls_frame, from_=-100, to=100, variable=self.brightness_var,
                                   orient=tk.HORIZONTAL, command=self.update_preview)
        brightness_scale.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=2)

        # Contrast
        ttk.Label(controls_frame, text="Contrast:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.contrast_var = tk.DoubleVar(value=0)
        contrast_scale = ttk.Scale(controls_frame, from_=-100, to=100, variable=self.contrast_var,
                                 orient=tk.HORIZONTAL, command=self.update_preview)
        contrast_scale.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=2)

        controls_frame.grid_columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Reset", command=self.reset_values).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="OK", command=self.ok).pack(side=tk.RIGHT, padx=(0, 5))

        # Initial preview
        self.update_preview()

        # Wait for dialog
        self.dialog.wait_window()

    def update_preview(self, *args):
        """Update preview image"""
        try:
            # Apply brightness/contrast
            brightness = self.brightness_var.get() / 100.0
            contrast = (self.contrast_var.get() / 100.0) + 1.0

            # Brightness adjustment
            if brightness != 0:
                enhancer = ImageEnhance.Brightness(self.original_image)
                adjusted = enhancer.enhance(1.0 + brightness)
            else:
                adjusted = self.original_image.copy()

            # Contrast adjustment
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(adjusted)
                adjusted = enhancer.enhance(contrast)

            # Create thumbnail for preview
            preview_size = (150, 150)
            preview = adjusted.copy()
            preview.thumbnail(preview_size, Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            self.preview_photo = ImageTk.PhotoImage(preview)
            self.preview_label.config(image=self.preview_photo)

            # Store result
            self.current_result = adjusted

        except Exception as e:
            print(f"Error updating preview: {e}")

    def reset_values(self):
        """Reset to default values"""
        self.brightness_var.set(0)
        self.contrast_var.set(0)
        self.update_preview()

    def ok(self):
        """Accept changes"""
        self.result = self.current_result
        self.dialog.destroy()

    def cancel(self):
        """Cancel changes"""
        self.dialog.destroy()

class UnsharpMaskDialog:
    """Dialog for unsharp mask filter"""

    def __init__(self, parent, image: Image.Image):
        self.original_image = image.copy()
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Unsharp Mask")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_dialog()

    def setup_dialog(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Preview
        preview_frame = ttk.LabelFrame(main_frame, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(padx=5, pady=5)

        # Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Radius
        ttk.Label(controls_frame, text="Radius:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.radius_var = tk.DoubleVar(value=2.0)
        radius_scale = ttk.Scale(controls_frame, from_=0.1, to=10.0, variable=self.radius_var,
                               orient=tk.HORIZONTAL, command=self.update_preview)
        radius_scale.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=2)

        # Percent
        ttk.Label(controls_frame, text="Percent:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.percent_var = tk.DoubleVar(value=150)
        percent_scale = ttk.Scale(controls_frame, from_=50, to=500, variable=self.percent_var,
                                orient=tk.HORIZONTAL, command=self.update_preview)
        percent_scale.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=2)

        # Threshold
        ttk.Label(controls_frame, text="Threshold:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.threshold_var = tk.DoubleVar(value=3)
        threshold_scale = ttk.Scale(controls_frame, from_=0, to=20, variable=self.threshold_var,
                                  orient=tk.HORIZONTAL, command=self.update_preview)
        threshold_scale.grid(row=2, column=1, sticky=tk.EW, padx=(10, 0), pady=2)

        controls_frame.grid_columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="OK", command=self.ok).pack(side=tk.RIGHT, padx=(0, 5))

        # Initial preview
        self.update_preview()

        # Wait for dialog
        self.dialog.wait_window()

    def update_preview(self, *args):
        """Update preview"""
        try:
            radius = self.radius_var.get()
            percent = int(self.percent_var.get())
            threshold = int(self.threshold_var.get())

            # Apply unsharp mask
            filtered = self.original_image.filter(
                ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold)
            )

            # Create preview
            preview_size = (150, 150)
            preview = filtered.copy()
            preview.thumbnail(preview_size, Image.Resampling.LANCZOS)

            self.preview_photo = ImageTk.PhotoImage(preview)
            self.preview_label.config(image=self.preview_photo)

            self.current_result = filtered

        except Exception as e:
            print(f"Error updating preview: {e}")

    def ok(self):
        """Accept changes"""
        self.result = self.current_result
        self.dialog.destroy()

    def cancel(self):
        """Cancel changes"""
        self.dialog.destroy()

class ResizeDialog:
    """Dialog for resizing image"""

    def __init__(self, parent, current_size: Tuple[int, int]):
        self.current_size = current_size
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Resize Image")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_dialog()

    def setup_dialog(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Current size
        current_frame = ttk.LabelFrame(main_frame, text="Current Size")
        current_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(current_frame, text=f"Width: {self.current_size[0]} pixels").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(current_frame, text=f"Height: {self.current_size[1]} pixels").pack(anchor=tk.W, padx=5, pady=2)

        # New size
        new_frame = ttk.LabelFrame(main_frame, text="New Size")
        new_frame.pack(fill=tk.X, pady=(0, 10))

        # Width
        width_frame = ttk.Frame(new_frame)
        width_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(width_frame, text="Width:").pack(side=tk.LEFT)
        self.width_var = tk.IntVar(value=self.current_size[0])
        width_entry = ttk.Entry(width_frame, textvariable=self.width_var, width=10)
        width_entry.pack(side=tk.RIGHT)
        width_entry.bind('<KeyRelease>', self.on_width_change)

        # Height
        height_frame = ttk.Frame(new_frame)
        height_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(height_frame, text="Height:").pack(side=tk.LEFT)
        self.height_var = tk.IntVar(value=self.current_size[1])
        height_entry = ttk.Entry(height_frame, textvariable=self.height_var, width=10)
        height_entry.pack(side=tk.RIGHT)
        height_entry.bind('<KeyRelease>', self.on_height_change)

        # Maintain aspect ratio
        self.maintain_aspect = tk.BoolVar(value=True)
        ttk.Checkbutton(new_frame, text="Maintain aspect ratio",
                       variable=self.maintain_aspect).pack(anchor=tk.W, padx=5, pady=2)

        # Calculate aspect ratio
        self.aspect_ratio = self.current_size[0] / self.current_size[1]

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="OK", command=self.ok).pack(side=tk.RIGHT, padx=(0, 5))

        # Wait for dialog
        self.dialog.wait_window()

    def on_width_change(self, event):
        """Handle width change"""
        if self.maintain_aspect.get():
            try:
                width = self.width_var.get()
                height = int(width / self.aspect_ratio)
                self.height_var.set(height)
            except:
                pass

    def on_height_change(self, event):
        """Handle height change"""
        if self.maintain_aspect.get():
            try:
                height = self.height_var.get()
                width = int(height * self.aspect_ratio)
                self.width_var.set(width)
            except:
                pass

    def ok(self):
        """Accept changes"""
        try:
            width = self.width_var.get()
            height = self.height_var.get()

            if width > 0 and height > 0:
                self.result = (width, height)

        except:
            pass

        self.dialog.destroy()

    def cancel(self):
        """Cancel changes"""
        self.dialog.destroy()

# Enhanced TXD Editor with integrated image editor
class EnhancedTXDEditor(TXDEditor):
    """Enhanced TXD Editor with integrated image editing"""

    def __init__(self):
        super().__init__()

        # Add image editor button to toolbar
        self.add_editor_button()

    def add_editor_button(self):
        """Add image editor button to existing UI"""
        # Find the edit menu and add editor option
        edit_menu = self.menubar.children['!menu2']  # Edit menu
        edit_menu.add_separator()
        edit_menu.add_command(label="Edit in Image Editor...", command=self.open_image_editor)

    def open_image_editor(self):
        """Open integrated image editor"""
        if not self.current_texture:
            messagebox.showwarning("Warning", "No texture selected")
            return

        try:
            # Get current texture image
            image = ImageConverter.txd_to_pil(self.current_texture, self.current_mip_level)
            if not image:
                messagebox.showerror("Error", "Failed to get texture image")
                return

            # Open image editor
            editor = ImageEditor(self.root, image, self.on_image_edited)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image editor: {e}")

    def on_image_edited(self, edited_image: Image.Image):
        """Handle edited image from image editor"""
        try:
            # Check if size changed
            if edited_image.size != (self.current_texture.width, self.current_texture.height):
                result = messagebox.askyesnocancel(
                    "Size Changed",
                    f"Image size changed from {self.current_texture.width}x{self.current_texture.height} "
                    f"to {edited_image.size[0]}x{edited_image.size[1]}.\n\n"
                    f"Update texture size and regenerate mipmaps?"
                )

                if result is None:  # Cancel
                    return
                elif result:  # Yes, update size
                    self.current_texture.width = edited_image.size[0]
                    self.current_texture.height = edited_image.size[1]
                    # Regenerate mipmaps
                    self.generate_mipmaps_for_texture(self.current_texture, edited_image)
                else:  # No, resize image to match texture
                    edited_image = edited_image.resize(
                        (self.current_texture.width, self.current_texture.height),
                        Image.Resampling.LANCZOS
                    )

            # Convert back to texture format
            if ImageConverter.pil_to_txd(edited_image, self.current_texture, self.current_mip_level):
                self.status_var.set("Image editor changes applied")
                self.update_properties()
                self.update_image_display()
            else:
                messagebox.showerror("Error", "Failed to apply edited image")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply edited image: {e}")

def main():
    """Main entry point"""
    try:
        app = EnhancedTXDEditor()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()


