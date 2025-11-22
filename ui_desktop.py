"""
Tkinter Desktop UI for Floor Plan to 3D House Generator
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
import os
import threading
from floor_plan_to_3d import FloorPlanTo3D
from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class FloorPlan3DApp:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("Floor Plan to 3D House Generator")
            self.root.geometry("1200x800")
            self.root.configure(bg='#f0f0f0')
            
            self.floor_plan_path = None
            self.converter = None
            
            self.setup_ui()
        except Exception as e:
            import traceback
            error_msg = f"Error initializing application:\n{str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            messagebox.showerror("Initialization Error", error_msg)
            raise
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#1f77b4', height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🏠 Floor Plan to 3D House Generator",
            font=('Arial', 20, 'bold'),
            bg='#1f77b4',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_frame, bg='#f0f0f0', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # File selection
        file_frame = tk.LabelFrame(left_panel, text="📤 Floor Plan Selection", 
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0')
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_select = tk.Button(
            file_frame,
            text="Select Floor Plan Image",
            command=self.select_floor_plan,
            bg='#1f77b4',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.RAISED,
            cursor='hand2',
            padx=10,
            pady=5
        )
        btn_select.pack(fill=tk.X, padx=5, pady=5)
        
        btn_sample = tk.Button(
            file_frame,
            text="Create Sample Floor Plan",
            command=self.create_sample,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10),
            relief=tk.RAISED,
            cursor='hand2',
            padx=10,
            pady=5
        )
        btn_sample.pack(fill=tk.X, padx=5, pady=5)
        
        btn_editor = tk.Button(
            file_frame,
            text="🏗️ Open Floor Plan Editor",
            command=self.open_editor,
            bg='#FF9800',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.RAISED,
            cursor='hand2',
            padx=10,
            pady=5
        )
        btn_editor.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_label = tk.Label(
            file_frame,
            text="No file selected",
            bg='#f0f0f0',
            fg='#666',
            font=('Arial', 9),
            wraplength=280,
            justify=tk.LEFT
        )
        self.file_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Parameters
        params_frame = tk.LabelFrame(left_panel, text="⚙️ Parameters", 
                                    font=('Arial', 12, 'bold'), bg='#f0f0f0')
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Wall Height
        tk.Label(
            params_frame,
            text="Wall Height (m):",
            bg='#f0f0f0',
            font=('Arial', 9)
        ).pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        self.wall_height_var = tk.DoubleVar(value=3.0)
        height_scale = tk.Scale(
            params_frame,
            from_=2.0,
            to=5.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.wall_height_var,
            bg='#f0f0f0',
            font=('Arial', 9)
        )
        height_scale.pack(fill=tk.X, padx=5, pady=2)
        
        self.height_label = tk.Label(
            params_frame,
            text="3.0 m",
            bg='#f0f0f0',
            font=('Arial', 9, 'bold')
        )
        self.height_label.pack(anchor=tk.W, padx=5)
        height_scale.config(command=lambda v: self.height_label.config(text=f"{float(v):.1f} m"))
        
        # Wall Thickness
        tk.Label(
            params_frame,
            text="Wall Thickness (m):",
            bg='#f0f0f0',
            font=('Arial', 9)
        ).pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        self.wall_thickness_var = tk.DoubleVar(value=0.2)
        thickness_scale = tk.Scale(
            params_frame,
            from_=0.1,
            to=0.5,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.wall_thickness_var,
            bg='#f0f0f0',
            font=('Arial', 9)
        )
        thickness_scale.pack(fill=tk.X, padx=5, pady=2)
        
        self.thickness_label = tk.Label(
            params_frame,
            text="0.2 m",
            bg='#f0f0f0',
            font=('Arial', 9, 'bold')
        )
        self.thickness_label.pack(anchor=tk.W, padx=5)
        thickness_scale.config(command=lambda v: self.thickness_label.config(text=f"{float(v):.2f} m"))
        
        # Generate button
        btn_generate = tk.Button(
            left_panel,
            text="🚀 Generate 3D Model",
            command=self.generate_3d,
            bg='#FF6B35',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.RAISED,
            cursor='hand2',
            padx=10,
            pady=15,
            state=tk.DISABLED
        )
        btn_generate.pack(fill=tk.X, pady=10)
        self.btn_generate = btn_generate
        
        # Status
        status_frame = tk.LabelFrame(left_panel, text="ℹ️ Status", 
                                    font=('Arial', 12, 'bold'), bg='#f0f0f0')
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=8,
            bg='#ffffff',
            font=('Courier', 9),
            wrap=tk.WORD
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log("Ready. Select a floor plan to begin.")
        
        # Right panel - Preview and Result
        right_panel = tk.Frame(main_frame, bg='#f0f0f0')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Floor Plan Preview Tab
        preview_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(preview_frame, text="📐 Floor Plan Preview")
        
        self.preview_label = tk.Label(
            preview_frame,
            text="No floor plan loaded",
            bg='#f0f0f0',
            font=('Arial', 12),
            fg='#666'
        )
        self.preview_label.pack(expand=True)
        
        # 3D Model Tab
        self.model_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.model_frame, text="🏠 3D Model")
        
        self.model_label = tk.Label(
            self.model_frame,
            text="Generate a 3D model to view it here",
            bg='#f0f0f0',
            font=('Arial', 12),
            fg='#666'
        )
        self.model_label.pack(expand=True)
        self.model_canvas = None
        
    def log(self, message):
        """Add message to status log"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def select_floor_plan(self):
        """Open file dialog to select floor plan"""
        file_path = filedialog.askopenfilename(
            title="Select Floor Plan Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.floor_plan_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.btn_generate.config(state=tk.NORMAL)
            self.log(f"Selected: {os.path.basename(file_path)}")
            self.load_preview(file_path)
            
    def create_sample(self):
        """Create a sample floor plan"""
        from create_sample_floor_plan import create_sample_floor_plan
        file_path = filedialog.asksaveasfilename(
            title="Save Sample Floor Plan",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                create_sample_floor_plan(file_path)
                self.floor_plan_path = file_path
                self.file_label.config(text=os.path.basename(file_path))
                self.btn_generate.config(state=tk.NORMAL)
                self.log(f"Created sample floor plan: {os.path.basename(file_path)}")
                self.load_preview(file_path)
                messagebox.showinfo("Success", "Sample floor plan created successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create sample: {str(e)}")
                
    def open_editor(self):
        """Open the floor plan editor"""
        try:
            import subprocess
            import sys
            # Open editor in a new process
            subprocess.Popen([sys.executable, "floor_plan_editor.py"])
            self.log("Floor plan editor opened in a new window")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open editor:\n{str(e)}")
                
    def load_preview(self, file_path):
        """Load and display floor plan preview"""
        try:
            image = Image.open(file_path)
            # Resize to fit preview
            image.thumbnail((600, 600), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo
        except Exception as e:
            self.log(f"Error loading preview: {str(e)}")
            
    def generate_3d(self):
        """Generate 3D model in a separate thread"""
        if not self.floor_plan_path:
            messagebox.showwarning("Warning", "Please select a floor plan first!")
            return
            
        # Disable button during generation
        self.btn_generate.config(state=tk.DISABLED)
        self.log("Starting 3D model generation...")
        
        # Run in separate thread to avoid freezing UI
        thread = threading.Thread(target=self._generate_3d_thread)
        thread.daemon = True
        thread.start()
        
    def _generate_3d_thread(self):
        """Thread function for 3D generation - does computation only"""
        try:
            wall_height = self.wall_height_var.get()
            wall_thickness = self.wall_thickness_var.get()
            
            self.log(f"Wall height: {wall_height}m, Thickness: {wall_thickness}m")
            
            # Create converter
            self.converter = FloorPlanTo3D(
                wall_height=wall_height,
                wall_thickness=wall_thickness
            )
            
            # Load and process (heavy computation in background thread)
            self.log("Loading floor plan...")
            image = self.converter.load_floor_plan(self.floor_plan_path)
            
            self.log("Detecting walls...")
            walls = self.converter.detect_walls(image)
            self.log(f"Found {len(walls)} wall segments")
            
            self.log("Normalizing coordinates...")
            normalized_walls, scale = self.converter.normalize_coordinates(walls, image.shape)
            
            # Store data for main thread to create visualization
            self.log("Preparing 3D data...")
            model_data = {
                'normalized_walls': normalized_walls,
                'scale': scale,
                'image_shape': image.shape,
                'wall_height': wall_height,
                'wall_thickness': wall_thickness
            }
            
            # Create visualization in main thread (matplotlib must be in main thread)
            self.root.after(0, self._create_3d_visualization, model_data)
            
            self.log("✅ 3D model generation complete!")
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            import traceback
            error_msg = f"Failed to generate 3D model:\n{str(e)}\n\n{traceback.format_exc()}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.root.after(0, lambda: self.btn_generate.config(state=tk.NORMAL))
    
    def _create_3d_visualization(self, model_data):
        """Create matplotlib visualization in main thread"""
        try:
            normalized_walls = model_data['normalized_walls']
            scale = model_data['scale']
            image_shape = model_data['image_shape']
            wall_height = model_data['wall_height']
            wall_thickness = model_data['wall_thickness']
            
            # Create matplotlib figure (MUST be in main thread)
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # Create floor
            floor = self.converter.create_3d_floor(image_shape, scale)
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection
            floor_face = Poly3DCollection([floor], alpha=0.3, facecolor='gray', edgecolor='black')
            ax.add_collection3d(floor_face)
            
            # Create walls
            for x1, y1, x2, y2 in normalized_walls:
                wall_faces = self.converter.create_3d_wall(x1, y1, x2, y2, wall_height, wall_thickness)
                for face in wall_faces:
                    wall_poly = Poly3DCollection([face], alpha=0.7, facecolor='beige', 
                                                edgecolor='brown', linewidths=0.5)
                    ax.add_collection3d(wall_poly)
            
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
            
            # Display in UI
            self._display_3d_model(fig)
            
        except Exception as e:
            import traceback
            error_msg = f"Failed to create visualization:\n{str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Visualization Error", error_msg)
            self.log(f"❌ Visualization error: {str(e)}")
            
    def _display_3d_model(self, fig):
        """Display 3D model in the UI"""
        # Clear previous canvas
        if self.model_canvas:
            self.model_canvas.get_tk_widget().destroy()
            
        # Create new canvas
        self.model_canvas = FigureCanvasTkAgg(fig, self.model_frame)
        self.model_canvas.draw()
        self.model_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.model_label.pack_forget()
        
        # Switch to 3D Model tab
        self.notebook.select(1)  # Switch to the 3D Model tab (index 1)


def main():
    try:
        root = tk.Tk()
        app = FloorPlan3DApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        error_msg = f"Error starting application:\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        # Try to show error in a message box if possible
        try:
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror("Application Error", error_msg)
        except:
            pass


if __name__ == '__main__':
    main()

