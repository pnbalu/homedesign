# Floor Plan to 3D House Generator

A Python project that converts 2D floor plan images into 3D house models.

## Features

- **Automatic Wall Detection**: Uses computer vision techniques to detect walls from floor plan images
- **3D Model Generation**: Creates a 3D visualization of the house with walls and floor
- **Customizable Parameters**: Adjustable wall height and thickness
- **Multiple Output Formats**: Can display interactively or save to file

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 🖥️ Web UI (Recommended)

The easiest way to use the application is through the web interface:

```bash
streamlit run app.py
```

Or on Windows:
```bash
run_web_ui.bat
```

This will open a web browser with an interactive interface where you can:
- Upload floor plan images
- Adjust wall height and thickness with sliders
- Generate and view 3D models
- Download the results

### 🖥️ Desktop UI

For a native desktop application:

```bash
python ui_desktop.py
```

Or on Windows:
```bash
run_desktop_ui.bat
```

### 💻 Command Line Usage

#### Basic Usage

```bash
python floor_plan_to_3d.py path/to/floor_plan.png
```

#### Save Output to File

```bash
python floor_plan_to_3d.py path/to/floor_plan.png -o output_3d_model.png
```

#### Customize Wall Parameters

```bash
python floor_plan_to_3d.py path/to/floor_plan.png --wall-height 3.5 --wall-thickness 0.25
```

### Command Line Arguments

- `floor_plan`: Path to the floor plan image (required)
- `-o, --output`: Output path for 3D visualization (optional, displays interactively if not provided)
- `--wall-height`: Wall height in meters (default: 3.0)
- `--wall-thickness`: Wall thickness in meters (default: 0.2)

## How It Works

1. **Image Loading**: Loads and preprocesses the floor plan image
2. **Wall Detection**: Uses edge detection and Hough line transform to detect wall segments
3. **Coordinate Normalization**: Converts pixel coordinates to real-world scale (meters)
4. **3D Generation**: Creates 3D wall segments and floor plane
5. **Visualization**: Renders the 3D model using matplotlib

## Floor Plan Requirements

For best results, your floor plan image should:
- Have clear, distinct walls (black lines on white background work best)
- Be in a common image format (PNG, JPG, etc.)
- Have sufficient contrast between walls and empty space
- Be reasonably clean (minimal noise)

## Example

```python
from floor_plan_to_3d import FloorPlanTo3D

# Create converter
converter = FloorPlanTo3D(wall_height=3.0, wall_thickness=0.2)

# Generate 3D model
converter.generate_3d_model('my_floor_plan.png', output_path='3d_house.png')
```

## Dependencies

- `opencv-python`: Image processing and computer vision
- `numpy`: Numerical operations
- `matplotlib`: 3D visualization
- `streamlit`: Web UI framework (for web interface)
- `pillow`: Image processing (for UI)

## Future Enhancements

Potential improvements:
- Room detection and labeling
- Door and window detection
- Export to 3D file formats (OBJ, STL)
- Interactive 3D viewer
- More sophisticated wall detection algorithms
- Support for multi-story buildings

## License

This project is open source and available for use and modification.

