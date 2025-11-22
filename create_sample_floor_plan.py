"""
Utility script to create a sample floor plan for testing
"""

import cv2
import numpy as np

def create_sample_floor_plan(output_path: str = "sample_floor_plan.png"):
    """
    Create a simple rectangular floor plan with rooms
    
    Args:
        output_path: Path to save the floor plan image
    """
    # Create white background
    img = np.ones((800, 1000, 3), dtype=np.uint8) * 255
    
    # Draw outer walls (thick black lines)
    cv2.rectangle(img, (50, 50), (950, 750), (0, 0, 0), 8)
    
    # Draw inner walls
    # Vertical wall dividing left and right
    cv2.line(img, (500, 50), (500, 750), (0, 0, 0), 6)
    
    # Horizontal wall in left section
    cv2.line(img, (50, 400), (500, 400), (0, 0, 0), 6)
    
    # Horizontal wall in right section
    cv2.line(img, (500, 300), (950, 300), (0, 0, 0), 6)
    
    # Save the image
    cv2.imwrite(output_path, img)
    print(f"Sample floor plan created: {output_path}")
    print("This creates a simple 4-room layout:")
    print("  - Top-left room")
    print("  - Bottom-left room")
    print("  - Top-right room")
    print("  - Bottom-right room")


if __name__ == '__main__':
    create_sample_floor_plan()

