"""
Example usage of the Floor Plan to 3D House Generator
"""

from floor_plan_to_3d import FloorPlanTo3D
import os

def example_basic():
    """Basic example of converting a floor plan to 3D"""
    print("Example: Basic Floor Plan to 3D Conversion")
    print("-" * 50)
    
    # Check if example floor plan exists
    floor_plan_path = "example_floor_plan.png"
    
    if not os.path.exists(floor_plan_path):
        print(f"Note: {floor_plan_path} not found.")
        print("Please provide a floor plan image to test.")
        print("\nYou can create a simple floor plan by:")
        print("1. Drawing walls as black lines on a white background")
        print("2. Saving as PNG or JPG")
        print("3. Running: python floor_plan_to_3d.py your_floor_plan.png")
        return
    
    # Create converter with default settings
    converter = FloorPlanTo3D(wall_height=3.0, wall_thickness=0.2)
    
    # Generate 3D model
    converter.generate_3d_model(floor_plan_path, output_path="output_3d_house.png")
    print("\nExample completed!")


def example_custom_parameters():
    """Example with custom wall parameters"""
    print("\nExample: Custom Wall Parameters")
    print("-" * 50)
    
    floor_plan_path = "example_floor_plan.png"
    
    if not os.path.exists(floor_plan_path):
        print(f"Note: {floor_plan_path} not found.")
        return
    
    # Create converter with custom settings
    converter = FloorPlanTo3D(wall_height=4.0, wall_thickness=0.3)
    
    # Generate 3D model
    converter.generate_3d_model(floor_plan_path, output_path="output_3d_house_custom.png")
    print("\nCustom example completed!")


if __name__ == '__main__':
    example_basic()
    # Uncomment to run custom example:
    # example_custom_parameters()

