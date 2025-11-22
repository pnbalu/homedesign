"""
Interactive Floor Plan Editor with Drag-and-Drop
Create floor plans by dragging and dropping objects
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageDraw, ImageTk
import os
from PIL import Image, ImageDraw, ImageTk


class FloorPlanEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Floor Plan Editor - Drag & Drop")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Canvas settings
        self.canvas_width = 1000
        self.canvas_height = 700
        self.grid_size = 20
        self.scale = 1.0  # 1 pixel = 0.1 meters (adjustable)
        
        # Drawing state
        self.current_tool = "wall"
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.walls = []  # List of (x1, y1, x2, y2) tuples
        self.rooms = []  # List of room rectangles
        self.doors = []  # List of door positions (x, y, width, door_id, angle)
        self.selected_door = None  # Currently selected door for resizing
        self.windows = []  # List of window positions (x, y, angle, wall_id)
        self.staircases = []  # List of staircase positions (x, y, width, height, direction)
        self.furniture = []  # List of furniture items (type, x, y, width, height, rotation, item_id)
        self.selected_furniture = None  # Currently selected furniture for moving
        self.dragging_furniture = False
        self.selected_furniture_type = None  # Currently selected furniture type
        self.show_measurements = True  # Show measurements/rulers
        self.measurement_scale = 1.0  # Scale factor for measurements
        
        # Canvas image (for saving)
        self.canvas_image = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
        self.canvas_draw = ImageDraw.Draw(self.canvas_image)
        
        self.setup_ui()
        self.draw_grid()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Tools
        left_panel = tk.Frame(main_frame, bg='#e0e0e0', width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Header
        header = tk.Label(
            left_panel,
            text="🏗️ Floor Plan Editor",
            font=('Arial', 14, 'bold'),
            bg='#1f77b4',
            fg='white',
            pady=10
        )
        header.pack(fill=tk.X)
        
        # Create tabbed interface for Tools and Furniture
        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tools Tab
        tools_tab = tk.Frame(notebook, bg='#e0e0e0')
        notebook.add(tools_tab, text="🛠️ Tools")
        
        # Tool buttons
        self.tool_buttons = {}
        tools = [
            ("wall", "🧱 Wall", "Draw walls by clicking and dragging"),
            ("room", "🚪 Room", "Draw rectangular rooms"),
            ("door", "🚪 Door", "Place doors on walls"),
            ("window", "🪟 Window", "Place windows on walls"),
            ("staircase", "🪜 Staircase", "Click and drag to create staircase"),
            ("erase", "🗑️ Erase", "Erase objects"),
        ]
        
        for tool_id, label, desc in tools:
            btn = tk.Button(
                tools_tab,
                text=label,
                command=lambda t=tool_id: self.set_tool(t),
                bg='#4CAF50' if tool_id == "wall" else '#2196F3',
                fg='white',
                font=('Arial', 10),
                relief=tk.RAISED,
                cursor='hand2',
                padx=10,
                pady=5
            )
            btn.pack(fill=tk.X, padx=5, pady=2)
            self.tool_buttons[tool_id] = btn
            
            # Tooltip
            tooltip = tk.Label(
                tools_tab,
                text=desc,
                font=('Arial', 8),
                bg='#e0e0e0',
                fg='#666',
                wraplength=180
            )
            tooltip.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Furniture Tab
        furniture_tab = tk.Frame(notebook, bg='#e0e0e0')
        notebook.add(furniture_tab, text="🪑 Furniture")
        
        # Furniture library with images
        self.furniture_types = {
            "sofa": {"name": "Sofa", "width": 80, "height": 40, "color": "#8B4513", "emoji": "🛋️"},
            "dining_table": {"name": "Dining Table", "width": 60, "height": 60, "color": "#654321", "emoji": "🍽️"},
            "bed": {"name": "Bed", "width": 60, "height": 80, "color": "#4169E1", "emoji": "🛏️"},
            "chair": {"name": "Chair", "width": 25, "height": 25, "color": "#8B4513", "emoji": "💺"},
            "desk": {"name": "Desk", "width": 50, "height": 30, "color": "#654321", "emoji": "🖥️"},
            "tv": {"name": "TV", "width": 40, "height": 25, "color": "#000000", "emoji": "📺"},
            "refrigerator": {"name": "Refrigerator", "width": 30, "height": 50, "color": "#C0C0C0", "emoji": "❄️"},
            "cabinet": {"name": "Cabinet", "width": 40, "height": 30, "color": "#8B4513", "emoji": "🗄️"},
            "bookshelf": {"name": "Bookshelf", "width": 30, "height": 50, "color": "#654321", "emoji": "📚"},
            "table": {"name": "Table", "width": 40, "height": 40, "color": "#8B4513", "emoji": "🪑"},
            "wardrobe": {"name": "Wardrobe", "width": 50, "height": 60, "color": "#654321", "emoji": "👔"},
            "bathtub": {"name": "Bathtub", "width": 50, "height": 30, "color": "#87CEEB", "emoji": "🛁"},
        }
        
        # Create furniture images
        self.furniture_images = {}
        self.create_furniture_images()
        
        # Furniture selection buttons with images
        self.furniture_buttons = {}
        furniture_canvas = tk.Canvas(furniture_tab, height=400, bg='#e0e0e0', highlightthickness=0)
        furniture_scrollbar = tk.Scrollbar(furniture_tab, orient="vertical", command=furniture_canvas.yview)
        furniture_scrollable = tk.Frame(furniture_canvas, bg='#e0e0e0')
        
        furniture_scrollable.bind(
            "<Configure>",
            lambda e: furniture_canvas.configure(scrollregion=furniture_canvas.bbox("all"))
        )
        
        furniture_canvas.create_window((0, 0), window=furniture_scrollable, anchor="nw")
        furniture_canvas.configure(yscrollcommand=furniture_scrollbar.set)
        
        for ftype, fdata in self.furniture_types.items():
            # Create button with image
            btn_frame = tk.Frame(furniture_scrollable, bg='#e0e0e0', relief=tk.RAISED, bd=2)
            btn_frame.pack(fill=tk.X, padx=2, pady=2)
            
            # Image
            if ftype in self.furniture_images:
                img_label = tk.Label(btn_frame, image=self.furniture_images[ftype], bg='#e0e0e0')
                img_label.pack(side=tk.LEFT, padx=5, pady=5)
                img_label.image = self.furniture_images[ftype]  # Keep reference
            
            # Text label
            text_label = tk.Label(
                btn_frame,
                text=f"{fdata['emoji']} {fdata['name']}",
                font=('Arial', 9),
                bg='#e0e0e0',
                fg='black'
            )
            text_label.pack(side=tk.LEFT, padx=5)
            
            # Make entire frame clickable
            btn_frame.bind("<Button-1>", lambda e, t=ftype: self.select_furniture_type(t))
            img_label.bind("<Button-1>", lambda e, t=ftype: self.select_furniture_type(t))
            text_label.bind("<Button-1>", lambda e, t=ftype: self.select_furniture_type(t))
            
            self.furniture_buttons[ftype] = btn_frame
        
        furniture_canvas.pack(side="left", fill="both", expand=True)
        furniture_scrollbar.pack(side="right", fill="y")
        
        # Actions section
        actions_frame = tk.LabelFrame(left_panel, text="Actions", font=('Arial', 11, 'bold'), bg='#e0e0e0')
        actions_frame.pack(fill=tk.X, padx=5, pady=10)
        
        btn_clear = tk.Button(
            actions_frame,
            text="🗑️ Clear All",
            command=self.clear_all,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.RAISED,
            cursor='hand2',
            padx=10,
            pady=5
        )
        btn_clear.pack(fill=tk.X, padx=5, pady=2)
        
        btn_save = tk.Button(
            actions_frame,
            text="💾 Save Floor Plan",
            command=self.save_floor_plan,
            bg='#FF9800',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.RAISED,
            cursor='hand2',
            padx=10,
            pady=5
        )
        btn_save.pack(fill=tk.X, padx=5, pady=2)
        
        btn_generate_3d = tk.Button(
            actions_frame,
            text="🏠 Generate 3D",
            command=self.generate_3d,
            bg='#9C27B0',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.RAISED,
            cursor='hand2',
            padx=10,
            pady=5
        )
        btn_generate_3d.pack(fill=tk.X, padx=5, pady=2)
        
        # Info section
        info_frame = tk.LabelFrame(left_panel, text="Info", font=('Arial', 11, 'bold'), bg='#e0e0e0')
        info_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.info_label = tk.Label(
            info_frame,
            text="Select a tool and start drawing!\n\nClick and drag to draw walls.",
            font=('Arial', 9),
            bg='#e0e0e0',
            fg='#333',
            justify=tk.LEFT,
            wraplength=180
        )
        self.info_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Right panel - Canvas
        right_panel = tk.Frame(main_frame, bg='#f0f0f0')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbars
        canvas_frame = tk.Frame(right_panel, bg='#f0f0f0')
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Canvas
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white',
            scrollregion=(0, 0, self.canvas_width, self.canvas_height),
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_motion)
        
        # Measurement labels
        self.measurement_labels = []
        
    def create_furniture_images(self):
        """Create simple furniture images programmatically"""
        for ftype, fdata in self.furniture_types.items():
            width = 60
            height = 60
            img = Image.new('RGB', (width, height), fdata['color'])
            draw = ImageDraw.Draw(img)
            
            # Draw simple furniture shape based on type
            if ftype == "sofa":
                # Draw sofa shape
                draw.rectangle([10, 20, 50, 40], fill='#654321', outline='black', width=2)
                draw.ellipse([15, 15, 25, 25], fill='#8B4513', outline='black')
                draw.ellipse([35, 15, 45, 25], fill='#8B4513', outline='black')
            elif ftype == "bed":
                # Draw bed shape
                draw.rectangle([10, 15, 50, 45], fill='#4169E1', outline='black', width=2)
                draw.rectangle([10, 10, 20, 15], fill='#1E90FF', outline='black')
            elif ftype == "chair":
                # Draw chair shape
                draw.rectangle([20, 25, 40, 45], fill='#8B4513', outline='black', width=2)
                draw.rectangle([20, 15, 25, 25], fill='#654321', outline='black')
            elif ftype == "dining_table":
                # Draw table shape
                draw.ellipse([15, 15, 45, 45], fill='#654321', outline='black', width=2)
                draw.rectangle([20, 20, 40, 40], fill='#8B4513', outline='black')
            elif ftype == "tv":
                # Draw TV shape
                draw.rectangle([15, 20, 45, 40], fill='#000000', outline='gray', width=2)
                draw.rectangle([20, 25, 40, 35], fill='#1a1a1a', outline='gray')
            elif ftype == "refrigerator":
                # Draw refrigerator shape
                draw.rectangle([20, 10, 40, 50], fill='#C0C0C0', outline='black', width=2)
                draw.line([30, 10, 30, 50], fill='black', width=1)
            elif ftype == "desk":
                # Draw desk shape
                draw.rectangle([10, 25, 50, 35], fill='#654321', outline='black', width=2)
                draw.rectangle([15, 35, 20, 45], fill='#8B4513', outline='black')
                draw.rectangle([40, 35, 45, 45], fill='#8B4513', outline='black')
            elif ftype == "cabinet":
                # Draw cabinet shape
                draw.rectangle([15, 20, 45, 40], fill='#8B4513', outline='black', width=2)
                draw.line([30, 20, 30, 40], fill='black', width=1)
            elif ftype == "bookshelf":
                # Draw bookshelf shape
                draw.rectangle([20, 10, 40, 50], fill='#654321', outline='black', width=2)
                draw.line([20, 20, 40, 20], fill='black', width=1)
                draw.line([20, 30, 40, 30], fill='black', width=1)
                draw.line([20, 40, 40, 40], fill='black', width=1)
            elif ftype == "table":
                # Draw table shape
                draw.ellipse([15, 15, 45, 45], fill='#8B4513', outline='black', width=2)
            elif ftype == "wardrobe":
                # Draw wardrobe shape
                draw.rectangle([15, 10, 45, 50], fill='#654321', outline='black', width=2)
                draw.line([30, 10, 30, 50], fill='black', width=1)
            elif ftype == "bathtub":
                # Draw bathtub shape
                draw.ellipse([10, 20, 50, 40], fill='#87CEEB', outline='black', width=2)
                draw.rectangle([15, 25, 45, 35], fill='#B0E0E6', outline='black')
            else:
                # Default rectangle
                draw.rectangle([10, 10, 50, 50], fill=fdata['color'], outline='black', width=2)
            
            # Convert to PhotoImage
            self.furniture_images[ftype] = ImageTk.PhotoImage(img)
        
    def draw_grid(self):
        """Draw grid on canvas with measurements"""
        # Clear previous measurements
        for label_id in self.measurement_labels:
            try:
                self.canvas.delete(label_id)
            except:
                pass
        self.measurement_labels = []
        
        # Draw grid
        for x in range(0, self.canvas_width, self.grid_size):
            self.canvas.create_line(x, 0, x, self.canvas_height, fill='#e0e0e0', width=1, tags='grid')
            # Add measurement labels every 5 grid units
            if x % (self.grid_size * 5) == 0 and self.show_measurements and x > 0:
                # Convert to meters (assuming 1 pixel = 0.1 meters)
                meters = (x * 0.1) / 100  # Convert to meters
                label = self.canvas.create_text(x, 5, text=f"{meters:.1f}m", font=('Arial', 7), fill='#666', tags='measurement')
                self.measurement_labels.append(label)
        
        for y in range(0, self.canvas_height, self.grid_size):
            self.canvas.create_line(0, y, self.canvas_width, y, fill='#e0e0e0', width=1, tags='grid')
            # Add measurement labels every 5 grid units
            if y % (self.grid_size * 5) == 0 and self.show_measurements and y > 0:
                meters = (y * 0.1) / 100  # Convert to meters
                label = self.canvas.create_text(5, y, text=f"{meters:.1f}m", font=('Arial', 7), fill='#666', tags='measurement')
                self.measurement_labels.append(label)
        
        self.canvas.tag_lower('grid')
        self.canvas.tag_lower('measurement')
        
        # Draw rulers on edges
        if self.show_measurements:
            self.draw_rulers()
    
    def draw_rulers(self):
        """Draw measurement rulers on canvas edges"""
        ruler_height = 20
        ruler_width = 20
        # Top ruler
        self.canvas.create_rectangle(0, 0, self.canvas_width, ruler_height, fill='#f0f0f0', outline='#ccc', tags='ruler')
        # Bottom ruler
        self.canvas.create_rectangle(0, self.canvas_height - ruler_height, self.canvas_width, self.canvas_height, fill='#f0f0f0', outline='#ccc', tags='ruler')
        # Left ruler
        self.canvas.create_rectangle(0, 0, ruler_width, self.canvas_height, fill='#f0f0f0', outline='#ccc', tags='ruler')
        # Right ruler
        self.canvas.create_rectangle(self.canvas_width - ruler_width, 0, self.canvas_width, self.canvas_height, fill='#f0f0f0', outline='#ccc', tags='ruler')
        
        self.canvas.tag_lower('ruler')
        
    def select_furniture_type(self, ftype):
        """Select a furniture type from the library"""
        self.selected_furniture_type = ftype
        self.current_tool = "furniture"
        
        # Update furniture button colors
        for f_id, btn_frame in self.furniture_buttons.items():
            if f_id == ftype:
                btn_frame.config(relief=tk.SUNKEN, bg='#4CAF50')
                for widget in btn_frame.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.config(bg='#4CAF50')
            else:
                btn_frame.config(relief=tk.RAISED, bg='#e0e0e0')
                for widget in btn_frame.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.config(bg='#e0e0e0')
        
        fname = self.furniture_types[ftype]["name"]
        fdata = self.furniture_types[ftype]
        self.info_label.config(text=f"Selected: {fname}\nSize: {fdata['width']/10:.1f}m × {fdata['height']/10:.1f}m\nClick on canvas to place it.\nClick and drag to move existing furniture.")
        
    def set_tool(self, tool):
        """Set the current drawing tool"""
        self.current_tool = tool
        # Update button colors
        for tool_id, btn in self.tool_buttons.items():
            if tool_id == tool:
                btn.config(bg='#4CAF50', relief=tk.SUNKEN)
            else:
                btn.config(bg='#2196F3', relief=tk.RAISED)
        
        # Update info
        tool_info = {
            "wall": "Click and drag to draw walls",
            "room": "Click and drag to create rectangular rooms",
            "door": "Click on a wall to place a door",
            "window": "Click on a wall to place a window",
            "staircase": "Click and drag to create a staircase",
            "furniture": "Select furniture from panel, then click to place",
            "erase": "Click on objects to erase them"
        }
        self.info_label.config(text=tool_info.get(tool, "Select a tool"))
        
        # If switching away from furniture, deselect furniture type
        if tool != "furniture":
            self.selected_furniture_type = None
            for btn in self.furniture_buttons.values():
                btn.config(bg='#E0E0E0', relief=tk.RAISED)
        
    def on_click(self, event):
        """Handle mouse click"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "erase":
            self.erase_at(x, y)
        elif self.current_tool == "furniture":
            # Check if clicking on existing furniture to move it
            items = self.canvas.find_overlapping(x - 10, y - 10, x + 10, y + 10)
            for item in items:
                tags = self.canvas.gettags(item)
                if 'furniture' in tags:
                    # Find which furniture this is
                    for i, (ftype, fx, fy, fw, fh, rot, fid) in enumerate(self.furniture):
                        if fid == item:
                            self.selected_furniture = i
                            self.dragging_furniture = True
                            self.start_x = x
                            self.start_y = y
                            return
            # Otherwise, place new furniture if type is selected
            if self.selected_furniture_type:
                self.add_furniture(self.selected_furniture_type, x, y)
        elif self.current_tool == "door":
            # Check if clicking on a door handle for resizing
            items = self.canvas.find_overlapping(x - 5, y - 5, x + 5, y + 5)
            for item in items:
                tags = self.canvas.gettags(item)
                if 'handle' in tags:
                    # Find which door this handle belongs to
                    for i, door_data in enumerate(self.doors):
                        if len(door_data) >= 6 and (item == door_data[4] or item == door_data[5]):
                            self.selected_door = i
                            self.drawing = True
                            self.start_x = x
                            self.start_y = y
                            return
            # Otherwise, place a new door
            self.add_door(x, y)
        else:
            self.drawing = True
            self.start_x = x
            self.start_y = y
            
    def on_drag(self, event):
        """Handle mouse drag"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Handle furniture dragging
        if self.dragging_furniture and self.selected_furniture is not None:
            furniture_data = self.furniture[self.selected_furniture]
            ftype, old_x, old_y, fw, fh, rot, fid = furniture_data
            
            # Calculate new position
            dx = x - self.start_x
            dy = y - self.start_y
            new_x = old_x + dx
            new_y = old_y + dy
            
            # Snap to grid
            new_x = round(new_x / self.grid_size) * self.grid_size
            new_y = round(new_y / self.grid_size) * self.grid_size
            
            # Update furniture position
            self.canvas.coords(fid, 
                new_x - fw/2, new_y - fh/2,
                new_x + fw/2, new_y + fh/2)
            
            # Update text position
            for item in self.canvas.find_withtag('furniture'):
                item_coords = self.canvas.coords(item)
                if len(item_coords) == 2:  # Text item
                    if abs(item_coords[0] - old_x) < 5 and abs(item_coords[1] - old_y) < 5:
                        self.canvas.coords(item, new_x, new_y)
            
            # Update furniture data
            self.furniture[self.selected_furniture] = (ftype, new_x, new_y, fw, fh, rot, fid)
            self.start_x = x
            self.start_y = y
            return
        
        if not self.drawing:
            return
            
        # Delete temporary drawings
        if hasattr(self, 'temp_line'):
            self.canvas.delete(self.temp_line)
            delattr(self, 'temp_line')
        if hasattr(self, 'temp_rect'):
            self.canvas.delete(self.temp_rect)
            delattr(self, 'temp_rect')
        
        # Handle door resizing
        if self.current_tool == "door" and self.selected_door is not None:
            door_data = self.doors[self.selected_door]
            door_x, door_y, door_width, door_id, handle1, handle2, angle = door_data
            
            # Calculate new width based on drag distance
            dx = x - self.start_x
            new_width = max(15, min(80, door_width + dx * 2))  # Min 15, max 80 pixels
            
            # Update door
            self.canvas.coords(door_id, 
                door_x - new_width/2, door_y - new_width/2,
                door_x + new_width/2, door_y + new_width/2)
            
            # Update handles
            handle_size = 5
            self.canvas.coords(handle1,
                door_x - new_width/2 - handle_size/2, door_y - handle_size/2,
                door_x - new_width/2 + handle_size/2, door_y + handle_size/2)
            self.canvas.coords(handle2,
                door_x + new_width/2 - handle_size/2, door_y - handle_size/2,
                door_x + new_width/2 + handle_size/2, door_y + handle_size/2)
            
            # Update door data
            self.doors[self.selected_door] = (door_x, door_y, new_width, door_id, handle1, handle2, angle)
            return
        
        # Draw temporary line/rectangle
        if self.current_tool == "wall":
            self.temp_line = self.canvas.create_line(
                self.start_x, self.start_y, x, y,
                fill='black', width=4, tags='temp'
            )
        elif self.current_tool == "room":
            # Ensure proper order for rectangle
            x1, x2 = min(self.start_x, x), max(self.start_x, x)
            y1, y2 = min(self.start_y, y), max(self.start_y, y)
            self.temp_rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='blue', width=2, tags='temp', dash=(5, 5)
            )
        elif self.current_tool == "staircase":
            # Ensure proper order for rectangle
            x1, x2 = min(self.start_x, x), max(self.start_x, x)
            y1, y2 = min(self.start_y, y), max(self.start_y, y)
            self.temp_rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='orange', width=2, tags='temp', dash=(3, 3)
            )
            
    def on_release(self, event):
        """Handle mouse release"""
        if not self.drawing:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Delete temporary drawing
        if hasattr(self, 'temp_line'):
            self.canvas.delete(self.temp_line)
        if hasattr(self, 'temp_rect'):
            self.canvas.delete(self.temp_rect)
        
        # Create permanent object
        if self.current_tool == "wall":
            if abs(x - self.start_x) > 5 or abs(y - self.start_y) > 5:  # Minimum length
                self.add_wall(self.start_x, self.start_y, x, y)
        elif self.current_tool == "room":
            # Check minimum size (both width and height must be > 20)
            if abs(x - self.start_x) > 20 and abs(y - self.start_y) > 20:  # Minimum size
                self.add_room(self.start_x, self.start_y, x, y)
        elif self.current_tool == "door":
            if self.selected_door is not None:
                # Finished resizing
                self.selected_door = None
            else:
                # This shouldn't happen as door is added on click
                pass
        elif self.current_tool == "window":
            self.add_window(x, y)
        elif self.current_tool == "staircase":
            # Check minimum size
            if abs(x - self.start_x) > 20 and abs(y - self.start_y) > 20:
                self.add_staircase(self.start_x, self.start_y, x, y)
        elif self.current_tool == "furniture":
            if self.dragging_furniture:
                self.dragging_furniture = False
                self.selected_furniture = None
        
        self.drawing = False
        
    def on_motion(self, event):
        """Handle mouse motion for cursor feedback"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        # Could add cursor changes or coordinate display here
        
    def add_wall(self, x1, y1, x2, y2):
        """Add a wall to the canvas with measurements"""
        # Snap to grid
        x1 = round(x1 / self.grid_size) * self.grid_size
        y1 = round(y1 / self.grid_size) * self.grid_size
        x2 = round(x2 / self.grid_size) * self.grid_size
        y2 = round(y2 / self.grid_size) * self.grid_size
        
        wall_id = self.canvas.create_line(x1, y1, x2, y2, fill='black', width=6, tags='wall')
        self.walls.append((x1, y1, x2, y2, wall_id))
        
        # Add measurement label
        if self.show_measurements:
            length = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            length_m = (length * 0.1) / 100  # Convert to meters
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            # Offset label perpendicular to wall
            dx = x2 - x1
            dy = y2 - y1
            if abs(dx) > abs(dy):
                label_y = mid_y - 15
                label_x = mid_x
            else:
                label_x = mid_x - 15
                label_y = mid_y
            
            measurement_id = self.canvas.create_text(
                label_x, label_y,
                text=f"{length_m:.2f}m",
                font=('Arial', 8, 'bold'),
                fill='blue',
                tags=('wall', 'measurement'),
                bg='white'
            )
            self.measurement_labels.append(measurement_id)
        
        # Update canvas image
        self.canvas_draw.line([(x1, y1), (x2, y2)], fill='black', width=6)
        
    def add_room(self, x1, y1, x2, y2):
        """Add a room rectangle - creates walls around the room"""
        # Ensure proper order
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        # Snap to grid
        x1 = round(x1 / self.grid_size) * self.grid_size
        y1 = round(y1 / self.grid_size) * self.grid_size
        x2 = round(x2 / self.grid_size) * self.grid_size
        y2 = round(y2 / self.grid_size) * self.grid_size
        
        # Check minimum size
        if abs(x2 - x1) < 20 or abs(y2 - y1) < 20:
            return  # Room too small
        
        # Create walls around the room (4 walls forming a rectangle)
        # Note: We create walls first so they appear on top
        # Top wall
        self.add_wall(x1, y1, x2, y1)
        # Bottom wall  
        self.add_wall(x1, y2, x2, y2)
        # Left wall
        self.add_wall(x1, y1, x1, y2)
        # Right wall
        self.add_wall(x2, y1, x2, y2)
        
        # Create a room rectangle for visual reference
        # This helps identify the room area
        try:
            room_id = self.canvas.create_rectangle(
                x1 + 3, y1 + 3, x2 - 3, y2 - 3,  # Slightly inset to show inside room
                outline='blue', width=1, tags='room', fill='lightblue', stipple='gray25'
            )
            # Ensure walls are on top
            self.canvas.tag_lower(room_id)
            # Raise all walls above the room
            for item in self.canvas.find_all():
                tags = self.canvas.gettags(item)
                if 'wall' in tags:
                    self.canvas.tag_raise(item)
            
            # Add room measurements
            if self.show_measurements:
                room_width = abs(x2 - x1)
                room_height = abs(y2 - y1)
                width_m = (room_width * 0.1) / 100
                height_m = (room_height * 0.1) / 100
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                measurement_text = f"{width_m:.2f}m × {height_m:.2f}m"
                room_measurement_id = self.canvas.create_text(
                    center_x, center_y,
                    text=measurement_text,
                    font=('Arial', 9, 'bold'),
                    fill='blue',
                    tags=('room', 'measurement'),
                    bg='white'
                )
                self.measurement_labels.append(room_measurement_id)
            
            self.rooms.append((x1, y1, x2, y2, room_id))
        except Exception as e:
            # If room rectangle creation fails, at least the walls are created
            print(f"Room rectangle creation warning: {e}")
            self.rooms.append((x1, y1, x2, y2, None))
        
    def add_door(self, x, y):
        """Add a door at the specified position"""
        # Default door width
        door_width = 30
        door_id = self.canvas.create_arc(
            x - door_width/2, y - door_width/2,
            x + door_width/2, y + door_width/2,
            start=0, extent=90, outline='brown', width=3, tags='door'
        )
        # Add resize handles (small squares at corners)
        handle_size = 5
        handle1 = self.canvas.create_rectangle(
            x - door_width/2 - handle_size/2, y - handle_size/2,
            x - door_width/2 + handle_size/2, y + handle_size/2,
            fill='red', outline='darkred', width=1, tags=('door', 'handle', 'left')
        )
        handle2 = self.canvas.create_rectangle(
            x + door_width/2 - handle_size/2, y - handle_size/2,
            x + door_width/2 + handle_size/2, y + handle_size/2,
            fill='red', outline='darkred', width=1, tags=('door', 'handle', 'right')
        )
        self.doors.append((x, y, door_width, door_id, handle1, handle2, 0))  # x, y, width, door_id, handle1, handle2, angle
        
    def add_window(self, x, y):
        """Add a window at the specified position"""
        window_size = 30
        window_id = self.canvas.create_rectangle(
            x - window_size/2, y - window_size/2,
            x + window_size/2, y + window_size/2,
            outline='cyan', width=2, tags='window', fill='lightblue'
        )
        self.windows.append((x, y, window_id))
        
    def add_furniture(self, ftype, x, y):
        """Add furniture at the specified position with image"""
        if ftype not in self.furniture_types:
            return
        
        fdata = self.furniture_types[ftype]
        width = fdata["width"]
        height = fdata["height"]
        color = fdata["color"]
        
        # Snap to grid
        x = round(x / self.grid_size) * self.grid_size
        y = round(y / self.grid_size) * self.grid_size
        
        # Create furniture rectangle with image
        if ftype in self.furniture_images:
            # Use image if available
            furniture_id = self.canvas.create_image(
                x, y,
                image=self.furniture_images[ftype],
                tags='furniture'
            )
        else:
            # Fallback to rectangle
            furniture_id = self.canvas.create_rectangle(
                x - width/2, y - height/2,
                x + width/2, y + height/2,
                outline='black', width=2, tags='furniture', fill=color
            )
        
        # Add label text with measurements
        label_text = f"{fdata['name']}\n{width/10:.1f}m × {height/10:.1f}m"
        text_id = self.canvas.create_text(
            x, y + height/2 + 10,
            text=label_text,
            font=('Arial', 7),
            fill='black',
            tags='furniture'
        )
        
        # Store furniture data: (type, x, y, width, height, rotation, main_id)
        self.furniture.append((ftype, x, y, width, height, 0, furniture_id))
        
    def add_staircase(self, x1, y1, x2, y2):
        """Add a staircase"""
        # Ensure proper order
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        # Snap to grid
        x1 = round(x1 / self.grid_size) * self.grid_size
        y1 = round(y1 / self.grid_size) * self.grid_size
        x2 = round(x2 / self.grid_size) * self.grid_size
        y2 = round(y2 / self.grid_size) * self.grid_size
        
        # Determine direction (which way stairs go)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        direction = "horizontal" if width > height else "vertical"
        
        # Create staircase rectangle
        stair_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='orange', width=2, tags='staircase', fill='#FFE4B5'
        )
        
        # Draw step lines to indicate stairs
        num_steps = max(3, min(10, int(max(width, height) / 15)))
        if direction == "horizontal":
            step_width = width / num_steps
            for i in range(1, num_steps):
                step_x = x1 + i * step_width
                self.canvas.create_line(
                    step_x, y1, step_x, y2,
                    fill='orange', width=1, tags='staircase'
                )
        else:
            step_height = height / num_steps
            for i in range(1, num_steps):
                step_y = y1 + i * step_height
                self.canvas.create_line(
                    x1, step_y, x2, step_y,
                    fill='orange', width=1, tags='staircase'
                )
        
        self.staircases.append((x1, y1, x2, y2, direction, stair_id))
        
    def erase_at(self, x, y):
        """Erase object at the specified position"""
        tolerance = 10
        items = self.canvas.find_overlapping(x - tolerance, y - tolerance, x + tolerance, y + tolerance)
        
        for item in items:
            tags = self.canvas.gettags(item)
            if 'temp' in tags:
                continue
                
            # Remove from lists
            if 'wall' in tags:
                for i, (wx1, wy1, wx2, wy2, wid) in enumerate(self.walls):
                    if wid == item:
                        self.walls.pop(i)
                        break
            elif 'room' in tags:
                for i, (rx1, ry1, rx2, ry2, rid) in enumerate(self.rooms):
                    if rid == item:
                        self.rooms.pop(i)
                        break
            elif 'door' in tags:
                for i, door_data in enumerate(self.doors):
                    if len(door_data) >= 4:
                        door_id = door_data[3]
                        # Check if item is the door arc or one of the handles
                        if door_id == item or (len(door_data) > 4 and (door_data[4] == item or door_data[5] == item)):
                            # Delete door and its handles
                            self.canvas.delete(door_id)
                            if len(door_data) > 4:
                                self.canvas.delete(door_data[4])  # handle1
                                self.canvas.delete(door_data[5])  # handle2
                            self.doors.pop(i)
                            break
                    elif len(door_data) >= 3 and door_data[2] == item:  # Old format fallback
                        self.canvas.delete(item)
                        self.doors.pop(i)
                        break
            elif 'window' in tags:
                for i, (wx, wy, wid) in enumerate(self.windows):
                    if wid == item:
                        self.windows.pop(i)
                        break
            elif 'staircase' in tags:
                for i, (sx1, sy1, sx2, sy2, sdir, sid) in enumerate(self.staircases):
                    if sid == item:
                        self.staircases.pop(i)
                        # Delete all staircase-related items
                        for stair_item in self.canvas.find_withtag('staircase'):
                            if self.canvas.gettags(stair_item) == ('staircase',):
                                self.canvas.delete(stair_item)
                        break
            elif 'furniture' in tags:
                # Find and remove furniture
                for i, (ftype, fx, fy, fw, fh, rot, fid) in enumerate(self.furniture):
                    if fid == item:
                        # Delete all furniture items (rectangle and text) at this position
                        for furn_item in self.canvas.find_withtag('furniture'):
                            item_coords = self.canvas.coords(furn_item)
                            if len(item_coords) >= 2:
                                if len(item_coords) >= 4:
                                    item_x = (item_coords[0] + item_coords[2]) / 2
                                    item_y = (item_coords[1] + item_coords[3]) / 2
                                else:
                                    item_x, item_y = item_coords[0], item_coords[1]
                                if abs(item_x - fx) < 5 and abs(item_y - fy) < 5:
                                    self.canvas.delete(furn_item)
                        self.furniture.pop(i)
                        return
            
            self.canvas.delete(item)
            
    def clear_all(self):
        """Clear all objects from canvas"""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear everything?"):
            self.canvas.delete("all")
            self.walls = []
            self.rooms = []
            self.doors = []
            self.windows = []
            self.staircases = []
            self.furniture = []
            self.measurement_labels = []
            self.canvas_image = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
            self.canvas_draw = ImageDraw.Draw(self.canvas_image)
            self.draw_grid()
            
    def save_floor_plan(self):
        """Save the floor plan as an image"""
        if not self.walls:
            messagebox.showwarning("Warning", "Please draw at least one wall before saving!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Floor Plan",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Recreate image with all walls
                img = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
                draw = ImageDraw.Draw(img)
                
                # Draw walls
                for x1, y1, x2, y2, _ in self.walls:
                    draw.line([(x1, y1), (x2, y2)], fill='black', width=6)
                
                # Draw rooms (as outlines)
                for x1, y1, x2, y2, _ in self.rooms:
                    draw.rectangle([(x1, y1), (x2, y2)], outline='blue', width=2)
                
                # Draw doors
                for door_data in self.doors:
                    if len(door_data) >= 3:
                        x, y = door_data[0], door_data[1]
                        door_width = door_data[2] if len(door_data) > 2 else 20
                        draw.arc(
                            [x - door_width/2, y - door_width/2, x + door_width/2, y + door_width/2],
                            start=0, end=90, fill='brown', width=3
                        )
                
                # Draw windows
                for x, y, _ in self.windows:
                    window_size = 30
                    draw.rectangle(
                        [x - window_size/2, y - window_size/2, x + window_size/2, y + window_size/2],
                        outline='cyan', fill='lightblue', width=2
                    )
                
                # Draw staircases
                for x1, y1, x2, y2, direction, _ in self.staircases:
                    draw.rectangle([(x1, y1), (x2, y2)], outline='orange', fill='#FFE4B5', width=2)
                    # Draw step lines
                    width = abs(x2 - x1)
                    height = abs(y2 - y1)
                    num_steps = max(3, min(10, int(max(width, height) / 15)))
                    if direction == "horizontal":
                        step_width = width / num_steps
                        for i in range(1, num_steps):
                            step_x = x1 + i * step_width
                            draw.line([(step_x, y1), (step_x, y2)], fill='orange', width=1)
                    else:
                        step_height = height / num_steps
                        for i in range(1, num_steps):
                            step_y = y1 + i * step_height
                            draw.line([(x1, step_y), (x2, step_y)], fill='orange', width=1)
                
                # Draw furniture
                for ftype, fx, fy, fw, fh, rot, fid in self.furniture:
                    fdata = self.furniture_types[ftype]
                    color = fdata["color"]
                    draw.rectangle(
                        [(fx - fw/2, fy - fh/2), (fx + fw/2, fy + fh/2)],
                        outline='black', fill=color, width=2
                    )
                
                img.save(file_path)
                messagebox.showinfo("Success", f"Floor plan saved to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save floor plan:\n{str(e)}")
                
    def generate_3d(self):
        """Generate 3D model from the current floor plan"""
        if not self.walls:
            messagebox.showwarning("Warning", "Please draw at least one wall before generating 3D model!")
            return
            
        # Save to temporary file first
        temp_path = "temp_floor_plan.png"
        try:
            # Create image
            img = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Draw only walls (for 3D generation)
            for x1, y1, x2, y2, _ in self.walls:
                draw.line([(x1, y1), (x2, y2)], fill='black', width=6)
            
            img.save(temp_path)
            
            # Import and use the 3D generator
            from floor_plan_to_3d import FloorPlanTo3D
            
            # Open 3D generator window
            import subprocess
            import sys
            
            # Create a simple 3D viewer window with all elements
            self.open_3d_viewer(temp_path, self.doors, self.windows, self.staircases, self.furniture, self.canvas_width, self.canvas_height)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate 3D model:\n{str(e)}")
            
    def open_3d_viewer(self, floor_plan_path, doors=None, windows=None, staircases=None, furniture=None, img_width=1000, img_height=700):
        """Open 3D viewer in a new window with doors, windows, staircases, and furniture"""
        if doors is None:
            doors = []
        if windows is None:
            windows = []
        if staircases is None:
            staircases = []
        if furniture is None:
            furniture = []
        # Create a new window for 3D visualization
        viewer_window = tk.Toplevel(self.root)
        viewer_window.title("3D House Model")
        viewer_window.geometry("1000x800")
        
        # Import here to avoid circular imports
        from floor_plan_to_3d import FloorPlanTo3D
        import matplotlib.pyplot as plt
        import numpy as np
        from mpl_toolkits.mplot3d import Axes3D
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        try:
            # Create converter
            converter = FloorPlanTo3D(wall_height=3.0, wall_thickness=0.2)
            
            # Load and process
            image = converter.load_floor_plan(floor_plan_path)
            walls = converter.detect_walls(image)
            normalized_walls, scale = converter.normalize_coordinates(walls, image.shape)
            
            # Create 3D visualization
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # Create floor
            floor = converter.create_3d_floor(image.shape, scale)
            floor_face = Poly3DCollection([floor], alpha=0.3, facecolor='gray', edgecolor='black')
            ax.add_collection3d(floor_face)
            
            # Create walls
            for x1, y1, x2, y2 in normalized_walls:
                wall_faces = converter.create_3d_wall(x1, y1, x2, y2, 3.0, 0.2)
                for face in wall_faces:
                    wall_poly = Poly3DCollection([face], alpha=0.7, facecolor='beige', 
                                                edgecolor='brown', linewidths=0.5)
                    ax.add_collection3d(wall_poly)
            
            # Convert scale for doors, windows, staircases - use same scale as walls
            # The scale from normalize_coordinates is already applied to walls
            # We need to convert pixel coordinates to the same normalized space
            estimated_house_width = 15.0  # meters
            img_scale = estimated_house_width / max(img_width, img_height)
            
            # Helper function to find nearest wall and position door/window on it
            def find_nearest_wall_point(px, py, walls_list):
                """Find the nearest point on any wall to the given point"""
                min_dist = float('inf')
                nearest_point = None
                wall_normal = None
                
                for wx1, wy1, wx2, wy2 in walls_list:
                    # Vector along wall
                    wall_dx = wx2 - wx1
                    wall_dy = wy2 - wy1
                    wall_len = np.sqrt(wall_dx**2 + wall_dy**2)
                    
                    if wall_len == 0:
                        continue
                    
                    # Normalize wall direction
                    wall_dx_norm = wall_dx / wall_len
                    wall_dy_norm = wall_dy / wall_len
                    
                    # Vector from wall start to point
                    to_point_dx = px - wx1
                    to_point_dy = py - wy1
                    
                    # Project onto wall direction
                    t = to_point_dx * wall_dx_norm + to_point_dy * wall_dy_norm
                    t = max(0, min(wall_len, t))  # Clamp to wall segment
                    
                    # Nearest point on wall
                    nearest_x = wx1 + t * wall_dx_norm
                    nearest_y = wy1 + t * wall_dy_norm
                    
                    # Distance to this point
                    dist = np.sqrt((px - nearest_x)**2 + (py - nearest_y)**2)
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_point = (nearest_x, nearest_y)
                        # Wall normal (perpendicular, pointing away from wall center)
                        wall_normal = (-wall_dy_norm, wall_dx_norm)
                
                return nearest_point, wall_normal
            
            # Create doors (3D openings in walls with door panels)
            import math
            for door_data in doors:
                # Handle both old format (x, y, id) and new format (x, y, width, id, ...)
                if len(door_data) >= 3:
                    door_x_pixel, door_y_pixel = door_data[0], door_data[1]
                    door_width_pixels = door_data[2] if len(door_data) > 2 else 30
                else:
                    door_x_pixel, door_y_pixel = door_data[0], door_data[1]
                    door_width_pixels = 30
                
                # Convert pixel coordinates to normalized coordinates (same as walls)
                door_x_norm = door_x_pixel * img_scale
                door_y_norm = door_y_pixel * img_scale
                
                # Find nearest wall and position door on it
                nearest_point, wall_normal = find_nearest_wall_point(door_x_norm, door_y_norm, normalized_walls)
                
                if nearest_point is None:
                    continue
                
                door_x, door_y = nearest_point
                
                # Convert pixel width to meters
                door_width = max(0.6, min(1.2, door_width_pixels * img_scale * 0.03))
                door_height = 2.1  # meters
                wall_thickness = 0.2  # meters
                
                # Position door on wall surface (slightly offset by wall thickness/2)
                if wall_normal:
                    offset_x = wall_normal[0] * wall_thickness / 2
                    offset_y = wall_normal[1] * wall_thickness / 2
                else:
                    offset_x = offset_y = 0
                
                # Create door opening (recessed into wall)
                door_opening = np.array([
                    [door_x - door_width/2 + offset_x, door_y + offset_y, 0],
                    [door_x + door_width/2 + offset_x, door_y + offset_y, 0],
                    [door_x + door_width/2 + offset_x, door_y + offset_y, door_height],
                    [door_x - door_width/2 + offset_x, door_y + offset_y, door_height]
                ])
                door_opening_poly = Poly3DCollection([door_opening], alpha=0.3, facecolor='#654321', edgecolor='#654321')
                ax.add_collection3d(door_opening_poly)
                
                # Create door panel (showing as partially open at 45 degrees)
                door_angle = 45  # degrees
                angle_rad = math.radians(door_angle)
                cos_a = math.cos(angle_rad)
                sin_a = math.sin(angle_rad)
                
                # Door panel rotates around left edge
                panel_left_x = door_x - door_width/2 + offset_x
                panel_left_y = door_y + offset_y
                panel_right_x = panel_left_x + door_width * cos_a
                panel_right_y = panel_left_y + door_width * sin_a
                
                door_panel = np.array([
                    [panel_left_x, panel_left_y, 0],
                    [panel_right_x, panel_right_y, 0],
                    [panel_right_x, panel_right_y, door_height],
                    [panel_left_x, panel_left_y, door_height]
                ])
                door_panel_poly = Poly3DCollection([door_panel], alpha=0.9, facecolor='#8B4513', edgecolor='#654321', linewidths=1)
                ax.add_collection3d(door_panel_poly)
            
            # Create windows (3D openings in walls)
            for window_data in windows:
                if len(window_data) >= 2:
                    window_x_pixel, window_y_pixel = window_data[0], window_data[1]
                else:
                    continue
                
                # Convert pixel coordinates to normalized coordinates
                window_x_norm = window_x_pixel * img_scale
                window_y_norm = window_y_pixel * img_scale
                
                # Find nearest wall and position window on it
                nearest_point, wall_normal = find_nearest_wall_point(window_x_norm, window_y_norm, normalized_walls)
                
                if nearest_point is None:
                    continue
                
                window_x, window_y = nearest_point
                
                window_width = 1.2  # meters
                window_height = 1.2  # meters
                window_bottom = 0.9  # meters from floor
                wall_thickness = 0.2  # meters
                
                # Position window on wall surface
                if wall_normal:
                    offset_x = wall_normal[0] * wall_thickness / 2
                    offset_y = wall_normal[1] * wall_thickness / 2
                else:
                    offset_x = offset_y = 0
                
                # Create window opening (recessed into wall)
                window_vertices = np.array([
                    [window_x - window_width/2 + offset_x, window_y + offset_y, window_bottom],
                    [window_x + window_width/2 + offset_x, window_y + offset_y, window_bottom],
                    [window_x + window_width/2 + offset_x, window_y + offset_y, window_bottom + window_height],
                    [window_x - window_width/2 + offset_x, window_y + offset_y, window_bottom + window_height]
                ])
                window_poly = Poly3DCollection([window_vertices], alpha=0.5, facecolor='lightblue', edgecolor='blue', linewidths=1)
                ax.add_collection3d(window_poly)
                
                # Add window frame (slightly raised from wall)
                frame_thickness = 0.05
                if wall_normal:
                    frame_offset_x = wall_normal[0] * (wall_thickness / 2 + frame_thickness)
                    frame_offset_y = wall_normal[1] * (wall_thickness / 2 + frame_thickness)
                else:
                    frame_offset_x = frame_offset_y = 0
                
                window_frame = np.array([
                    [window_x - window_width/2 + frame_offset_x, window_y + frame_offset_y, window_bottom],
                    [window_x + window_width/2 + frame_offset_x, window_y + frame_offset_y, window_bottom],
                    [window_x + window_width/2 + frame_offset_x, window_y + frame_offset_y, window_bottom + window_height],
                    [window_x - window_width/2 + frame_offset_x, window_y + frame_offset_y, window_bottom + window_height]
                ])
                window_frame_poly = Poly3DCollection([window_frame], alpha=0.7, facecolor='white', edgecolor='gray', linewidths=1)
                ax.add_collection3d(window_frame_poly)
            
            # Create staircases (3D stepped structure)
            for stair_x1, stair_y1, stair_x2, stair_y2, direction, _ in staircases:
                # Convert to scaled coordinates
                sx1 = stair_x1 * img_scale
                sy1 = stair_y1 * img_scale
                sx2 = stair_x2 * img_scale
                sy2 = stair_y2 * img_scale
                
                stair_width = abs(sx2 - sx1)
                stair_depth = abs(sy2 - sy1)
                stair_height = 3.0  # Total height
                num_steps = max(3, min(15, int(max(stair_width, stair_depth) / 0.3)))
                step_height = stair_height / num_steps
                
                if direction == "horizontal":
                    step_width = stair_width / num_steps
                    for i in range(num_steps):
                        step_x = sx1 + i * step_width
                        step_z = i * step_height
                        step_vertices = np.array([
                            [step_x, sy1, step_z],
                            [step_x + step_width, sy1, step_z],
                            [step_x + step_width, sy2, step_z],
                            [step_x, sy2, step_z],
                            [step_x, sy1, step_z + step_height],
                            [step_x + step_width, sy1, step_z + step_height],
                            [step_x + step_width, sy2, step_z + step_height],
                            [step_x, sy2, step_z + step_height]
                        ])
                        # Create step faces
                        step_faces = [
                            [step_vertices[0], step_vertices[1], step_vertices[2], step_vertices[3]],  # Bottom
                            [step_vertices[4], step_vertices[5], step_vertices[6], step_vertices[7]],  # Top
                            [step_vertices[0], step_vertices[1], step_vertices[5], step_vertices[4]],  # Front
                            [step_vertices[2], step_vertices[3], step_vertices[7], step_vertices[6]],  # Back
                        ]
                        for face in step_faces:
                            step_poly = Poly3DCollection([face], alpha=0.8, facecolor='#FFE4B5', edgecolor='orange')
                            ax.add_collection3d(step_poly)
                else:  # vertical
                    step_depth = stair_depth / num_steps
                    for i in range(num_steps):
                        step_y = sy1 + i * step_depth
                        step_z = i * step_height
                        step_vertices = np.array([
                            [sx1, step_y, step_z],
                            [sx2, step_y, step_z],
                            [sx2, step_y + step_depth, step_z],
                            [sx1, step_y + step_depth, step_z],
                            [sx1, step_y, step_z + step_height],
                            [sx2, step_y, step_z + step_height],
                            [sx2, step_y + step_depth, step_z + step_height],
                            [sx1, step_y + step_depth, step_z + step_height]
                        ])
                        # Create step faces
                        step_faces = [
                            [step_vertices[0], step_vertices[1], step_vertices[2], step_vertices[3]],  # Bottom
                            [step_vertices[4], step_vertices[5], step_vertices[6], step_vertices[7]],  # Top
                            [step_vertices[0], step_vertices[1], step_vertices[5], step_vertices[4]],  # Front
                            [step_vertices[2], step_vertices[3], step_vertices[7], step_vertices[6]],  # Back
                        ]
                        for face in step_faces:
                            step_poly = Poly3DCollection([face], alpha=0.8, facecolor='#FFE4B5', edgecolor='orange')
                            ax.add_collection3d(step_poly)
            
            # Create furniture (3D objects on floor)
            furniture_heights = {
                "sofa": 0.4, "dining_table": 0.75, "bed": 0.5, "chair": 0.4,
                "desk": 0.75, "tv": 0.6, "refrigerator": 1.8, "cabinet": 0.9,
                "bookshelf": 1.5, "table": 0.75, "wardrobe": 2.0, "bathtub": 0.5
            }
            
            for ftype, fx, fy, fw, fh, rot, fid in furniture:
                if ftype not in self.furniture_types:
                    continue
                
                # Convert pixel coordinates to normalized coordinates
                furniture_x = fx * img_scale
                furniture_y = fy * img_scale
                furniture_width = fw * img_scale * 0.03  # Convert to meters
                furniture_depth = fh * img_scale * 0.03  # Convert to meters
                furniture_height = furniture_heights.get(ftype, 0.5)  # Default height
                
                # Create 3D furniture box
                f_x1 = furniture_x - furniture_width/2
                f_x2 = furniture_x + furniture_width/2
                f_y1 = furniture_y - furniture_depth/2
                f_y2 = furniture_y + furniture_depth/2
                
                furniture_vertices = np.array([
                    [f_x1, f_y1, 0],           # Bottom corners
                    [f_x2, f_y1, 0],
                    [f_x2, f_y2, 0],
                    [f_x1, f_y2, 0],
                    [f_x1, f_y1, furniture_height],  # Top corners
                    [f_x2, f_y1, furniture_height],
                    [f_x2, f_y2, furniture_height],
                    [f_x1, f_y2, furniture_height]
                ])
                
                # Create furniture faces
                furniture_faces = [
                    [furniture_vertices[0], furniture_vertices[1], furniture_vertices[2], furniture_vertices[3]],  # Bottom
                    [furniture_vertices[4], furniture_vertices[5], furniture_vertices[6], furniture_vertices[7]],  # Top
                    [furniture_vertices[0], furniture_vertices[1], furniture_vertices[5], furniture_vertices[4]],  # Front
                    [furniture_vertices[2], furniture_vertices[3], furniture_vertices[7], furniture_vertices[6]],  # Back
                    [furniture_vertices[0], furniture_vertices[3], furniture_vertices[7], furniture_vertices[4]],  # Left
                    [furniture_vertices[1], furniture_vertices[2], furniture_vertices[6], furniture_vertices[5]],  # Right
                ]
                
                fdata = self.furniture_types[ftype]
                furniture_color = fdata["color"]
                
                for face in furniture_faces:
                    furn_poly = Poly3DCollection([face], alpha=0.8, facecolor=furniture_color, edgecolor='black', linewidths=0.5)
                    ax.add_collection3d(furn_poly)
            
            # Set axis properties
            ax.set_xlabel('X (meters)')
            ax.set_ylabel('Y (meters)')
            ax.set_zlabel('Z (meters)')
            ax.set_title('3D House Model from Floor Plan')
            
            # Set equal aspect ratio
            max_range = max([ax.get_xlim()[1] - ax.get_xlim()[0],
                            ax.get_ylim()[1] - ax.get_ylim()[0],
                            ax.get_zlim()[1] - ax.get_zlim()[0]])
            mid_x = (ax.get_xlim()[0] + ax.get_xlim()[1]) / 2
            mid_y = (ax.get_ylim()[0] + ax.get_ylim()[1]) / 2
            mid_z = (ax.get_zlim()[0] + ax.get_zlim()[1]) / 2
            ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
            ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2)
            ax.set_zlim(mid_z - max_range/2, mid_z + max_range/2)
            
            # Display in window
            canvas = FigureCanvasTkAgg(fig, viewer_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            import traceback
            error_msg = f"Error generating 3D model:\n{str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Error", error_msg)
            viewer_window.destroy()


def main():
    root = tk.Tk()
    app = FloorPlanEditor(root)
    root.mainloop()


if __name__ == '__main__':
    main()

