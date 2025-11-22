"""
Floor Plan to 3D House Generator
Converts a 2D floor plan image into a 3D house model
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import argparse
import os
from typing import List, Tuple, Optional


class FloorPlanTo3D:
    """Converts floor plan images to 3D house models"""
    
    def __init__(self, wall_height: float = 3.0, wall_thickness: float = 0.2):
        """
        Initialize the converter
        
        Args:
            wall_height: Height of walls in meters (default: 3.0m)
            wall_thickness: Thickness of walls in meters (default: 0.2m)
        """
        self.wall_height = wall_height
        self.wall_thickness = wall_thickness
        
    def load_floor_plan(self, image_path: str) -> np.ndarray:
        """Load and preprocess the floor plan image"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Floor plan image not found: {image_path}")
        
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return gray
    
    def detect_walls(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect walls in the floor plan using edge detection and line detection
        
        Returns:
            List of wall segments as (x1, y1, x2, y2) tuples
        """
        # Apply threshold to get binary image
        _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Apply morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Edge detection
        edges = cv2.Canny(binary, 50, 150)
        
        # Detect lines using HoughLinesP
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                               minLineLength=30, maxLineGap=10)
        
        walls = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Filter out very short lines
                length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                if length > 20:
                    walls.append((x1, y1, x2, y2))
        
        return walls
    
    def detect_rooms(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Detect rooms/contours in the floor plan
        
        Returns:
            List of room contours
        """
        # Apply threshold
        _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area
        rooms = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Minimum room area threshold
                rooms.append(contour)
        
        return rooms
    
    def normalize_coordinates(self, walls: List[Tuple], image_shape: Tuple[int, int]) -> Tuple[List, float]:
        """
        Normalize wall coordinates to real-world scale
        
        Returns:
            Normalized walls and scale factor
        """
        # Estimate scale (assuming image represents a typical house ~10-20m)
        # Use image dimensions to estimate scale
        img_height, img_width = image_shape
        estimated_house_width = 15.0  # meters
        scale = estimated_house_width / max(img_width, img_height)
        
        normalized_walls = []
        for x1, y1, x2, y2 in walls:
            nx1 = x1 * scale
            ny1 = y1 * scale
            nx2 = x2 * scale
            ny2 = y2 * scale
            normalized_walls.append((nx1, ny1, nx2, ny2))
        
        return normalized_walls, scale
    
    def create_3d_wall(self, x1: float, y1: float, x2: float, y2: float, 
                       height: float, thickness: float) -> List[np.ndarray]:
        """
        Create 3D vertices for a wall segment
        
        Returns:
            List of vertices for the wall faces
        """
        # Calculate wall direction
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx**2 + dy**2)
        
        if length == 0:
            return []
        
        # Normalize direction
        dx_norm = dx / length
        dy_norm = dy / length
        
        # Perpendicular direction for thickness
        perp_x = -dy_norm * thickness / 2
        perp_y = dx_norm * thickness / 2
        
        # Create 8 vertices for the wall box
        vertices = []
        
        # Bottom face vertices
        vertices.append([x1 + perp_x, y1 + perp_y, 0])
        vertices.append([x2 + perp_x, y2 + perp_y, 0])
        vertices.append([x2 - perp_x, y2 - perp_y, 0])
        vertices.append([x1 - perp_x, y1 - perp_y, 0])
        
        # Top face vertices
        vertices.append([x1 + perp_x, y1 + perp_y, height])
        vertices.append([x2 + perp_x, y2 + perp_y, height])
        vertices.append([x2 - perp_x, y2 - perp_y, height])
        vertices.append([x1 - perp_x, y1 - perp_y, height])
        
        # Define faces (6 faces of a box)
        faces = [
            [0, 1, 2, 3],  # Bottom
            [4, 5, 6, 7],  # Top
            [0, 1, 5, 4],  # Front
            [2, 3, 7, 6],  # Back
            [0, 3, 7, 4],  # Left
            [1, 2, 6, 5],  # Right
        ]
        
        wall_faces = []
        for face in faces:
            face_vertices = np.array([vertices[i] for i in face])
            wall_faces.append(face_vertices)
        
        return wall_faces
    
    def create_3d_floor(self, image_shape: Tuple[int, int], scale: float) -> np.ndarray:
        """Create a floor plane"""
        img_height, img_width = image_shape
        width = img_width * scale
        height = img_height * scale
        
        floor_vertices = np.array([
            [0, 0, 0],
            [width, 0, 0],
            [width, height, 0],
            [0, height, 0]
        ])
        
        return floor_vertices
    
    def generate_3d_model(self, image_path: str, output_path: Optional[str] = None) -> None:
        """
        Main method to generate 3D model from floor plan
        
        Args:
            image_path: Path to floor plan image
            output_path: Optional path to save 3D visualization
        """
        print(f"Loading floor plan from: {image_path}")
        image = self.load_floor_plan(image_path)
        
        print("Detecting walls...")
        walls = self.detect_walls(image)
        print(f"Found {len(walls)} wall segments")
        
        print("Normalizing coordinates...")
        normalized_walls, scale = self.normalize_coordinates(walls, image.shape)
        
        print("Creating 3D model...")
        # Create 3D visualization
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create floor
        floor = self.create_3d_floor(image.shape, scale)
        floor_face = Poly3DCollection([floor], alpha=0.3, facecolor='gray', edgecolor='black')
        ax.add_collection3d(floor_face)
        
        # Create walls
        for x1, y1, x2, y2 in normalized_walls:
            wall_faces = self.create_3d_wall(x1, y1, x2, y2, self.wall_height, self.wall_thickness)
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
        
        # Save or show
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"3D model saved to: {output_path}")
        else:
            plt.show()
        
        print("3D model generation complete!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Convert floor plan to 3D house model')
    parser.add_argument('floor_plan', type=str, help='Path to floor plan image')
    parser.add_argument('-o', '--output', type=str, default=None, 
                       help='Output path for 3D visualization (PNG)')
    parser.add_argument('--wall-height', type=float, default=3.0,
                       help='Wall height in meters (default: 3.0)')
    parser.add_argument('--wall-thickness', type=float, default=0.2,
                       help='Wall thickness in meters (default: 0.2)')
    
    args = parser.parse_args()
    
    converter = FloorPlanTo3D(wall_height=args.wall_height, 
                             wall_thickness=args.wall_thickness)
    converter.generate_3d_model(args.floor_plan, args.output)


if __name__ == '__main__':
    main()

