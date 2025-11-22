"""
Test script to diagnose UI issues
"""

import sys

print("Testing imports...")
try:
    import tkinter as tk
    print("[OK] tkinter imported")
except Exception as e:
    print(f"[ERROR] tkinter import failed: {e}")
    sys.exit(1)

try:
    from tkinter import filedialog, messagebox, ttk
    print("[OK] tkinter modules imported")
except Exception as e:
    print(f"[ERROR] tkinter modules import failed: {e}")
    sys.exit(1)

try:
    from PIL import Image, ImageTk
    print("[OK] PIL imported")
except Exception as e:
    print(f"[ERROR] PIL import failed: {e}")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('TkAgg')
    print("[OK] matplotlib imported and backend set")
except Exception as e:
    print(f"[ERROR] matplotlib import failed: {e}")
    sys.exit(1)

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    print("[OK] matplotlib backend imported")
except Exception as e:
    print(f"[ERROR] matplotlib backend import failed: {e}")
    sys.exit(1)

try:
    from floor_plan_to_3d import FloorPlanTo3D
    print("[OK] FloorPlanTo3D imported")
except Exception as e:
    print(f"[ERROR] FloorPlanTo3D import failed: {e}")
    sys.exit(1)

print("\nAll imports successful. Testing basic Tkinter window...")
try:
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("400x300")
    label = tk.Label(root, text="If you see this, Tkinter is working!")
    label.pack(pady=50)
    print("[OK] Basic Tkinter window created")
    print("Closing test window in 2 seconds...")
    root.after(2000, root.destroy)
    root.mainloop()
    print("[OK] Tkinter mainloop completed")
except Exception as e:
    print(f"[ERROR] Tkinter test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[OK] All tests passed! The UI should work.")

