"""
Streamlit Web UI for Floor Plan to 3D House Generator
"""

import streamlit as st
import os
import tempfile
from floor_plan_to_3d import FloorPlanTo3D
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
import io
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Floor Plan to 3D House Generator",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #1565a0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏠 Floor Plan to 3D House Generator</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar for controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    wall_height = st.slider(
        "Wall Height (meters)",
        min_value=2.0,
        max_value=5.0,
        value=3.0,
        step=0.1,
        help="Height of the walls in the 3D model"
    )
    
    wall_thickness = st.slider(
        "Wall Thickness (meters)",
        min_value=0.1,
        max_value=0.5,
        value=0.2,
        step=0.05,
        help="Thickness of the walls in the 3D model"
    )
    
    st.markdown("---")
    st.header("ℹ️ Instructions")
    st.markdown("""
    1. Upload your floor plan image
    2. Adjust wall parameters if needed
    3. Click "Generate 3D Model"
    4. View and download the result
    
    **Tips:**
    - Best results with black walls on white background
    - PNG or JPG formats work best
    - Clear, high-contrast images work better
    """)

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.header("📤 Upload Floor Plan")
    
    uploaded_file = st.file_uploader(
        "Choose a floor plan image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload your floor plan image here"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Floor Plan", use_container_width=True)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            image.save(tmp_file.name)
            temp_path = tmp_file.name
        
        # Generate button
        if st.button("🚀 Generate 3D Model", type="primary"):
            with st.spinner("Generating 3D model... This may take a moment."):
                try:
                    # Create converter
                    converter = FloorPlanTo3D(
                        wall_height=wall_height,
                        wall_thickness=wall_thickness
                    )
                    
                    # Load and process floor plan
                    image = converter.load_floor_plan(temp_path)
                    walls = converter.detect_walls(image)
                    normalized_walls, scale = converter.normalize_coordinates(walls, image.shape)
                    
                    # Create 3D visualization directly
                    fig = plt.figure(figsize=(12, 10))
                    ax = fig.add_subplot(111, projection='3d')
                    
                    # Create floor
                    floor = converter.create_3d_floor(image.shape, scale)
                    floor_face = Poly3DCollection([floor], alpha=0.3, facecolor='gray', edgecolor='black')
                    ax.add_collection3d(floor_face)
                    
                    # Create walls
                    for x1, y1, x2, y2 in normalized_walls:
                        wall_faces = converter.create_3d_wall(x1, y1, x2, y2, wall_height, wall_thickness)
                        for face in wall_faces:
                            wall_poly = Poly3DCollection([face], alpha=0.7, facecolor='beige', 
                                                        edgecolor='brown', linewidths=0.5)
                            ax.add_collection3d(wall_poly)
                    
                    # Set axis properties
                    ax.set_xlabel('X (meters)', fontsize=10)
                    ax.set_ylabel('Y (meters)', fontsize=10)
                    ax.set_zlabel('Z (meters)', fontsize=10)
                    ax.set_title('3D House Model from Floor Plan', fontsize=14, fontweight='bold')
                    
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
                    
                    # Display result directly on screen
                    with col2:
                        st.header("🎨 3D Model Result")
                        st.pyplot(fig, use_container_width=True)
                        
                        # Save to buffer for download
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                        buf.seek(0)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download 3D Model",
                            data=buf,
                            file_name="3d_house_model.png",
                            mime="image/png"
                        )
                    
                    plt.close(fig)
                    
                    # Clean up temp files
                    os.unlink(temp_path)
                    
                    st.success(f"✅ 3D model generated successfully! Found {len(walls)} wall segments.")
                    
                except Exception as e:
                    st.error(f"❌ Error generating 3D model: {str(e)}")
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
    else:
        with col2:
            st.header("🎨 3D Model Result")
            st.info("👈 Upload a floor plan image to get started")
            
            # Show sample option
            if st.button("📋 Create Sample Floor Plan"):
                from create_sample_floor_plan import create_sample_floor_plan
                sample_path = "sample_floor_plan.png"
                create_sample_floor_plan(sample_path)
                st.success(f"✅ Sample floor plan created: {sample_path}")
                st.info("You can now upload this file or use it directly")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Built with ❤️ using Streamlit | Floor Plan to 3D House Generator</p>
    </div>
    """,
    unsafe_allow_html=True
)

