import trimesh
import numpy as np
import csv
import os

# Load your 3D mesh (replace with the actual path to your .obj file)
mesh_file = r"baby.obj"  # Use raw string (r"") to avoid escape character issues

# Ensure that the file exists before trying to load
if not os.path.exists(mesh_file):
    print(f"Error: The file {mesh_file} does not exist.")
    exit()

try:
    mesh = trimesh.load(mesh_file)

    # If mesh is a Scene, extract the first mesh
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump()[0]  # Take the first mesh from the scene
    print(f"Mesh loaded successfully: {mesh}")
except Exception as e:
    print(f"Error loading mesh: {e}")
    exit()

# Function to get cross-section for specified planes
def get_cross_section(mesh, plane, coord_value):
    try:
        # Define plane origin and normal vector based on plane type
        if plane == 'xy':
            section = mesh.section(plane_origin=[0, 0, coord_value], plane_normal=[0, 0, 1])
        elif plane == 'xz':
            section = mesh.section(plane_origin=[0, coord_value, 0], plane_normal=[0, 1, 0])
        elif plane == 'yz':
            section = mesh.section(plane_origin=[coord_value, 0, 0], plane_normal=[1, 0, 0])
        else:
            raise ValueError(f"Invalid plane: {plane}. Use 'xy', 'xz', or 'yz'.")

        # Check if section is valid
        if section and hasattr(section, 'vertices'):
            return section.vertices
        else:
            print(f"No intersection found for plane {plane} at coordinate {coord_value}")
            return np.array([])
    except Exception as e:
        print(f"Error in getting cross-section for plane {plane} at {coord_value}: {e}")
        return np.array([])

# Function to generate and save cross-sections
def save_cross_sections(mesh, plane, step, output_dir):
    # Get the bounding box of the mesh
    min_coord, max_coord = mesh.bounds[0], mesh.bounds[1]
    print(f"Mesh bounds: min {min_coord}, max {max_coord}")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define slicing range based on the plane
    axis_index = {'xy': 2, 'xz': 1, 'yz': 0}[plane]  # Axis index for z, y, x respectively
    slice_min, slice_max = min_coord[axis_index], max_coord[axis_index]

    # Generate cross-sections
    for coord_value in np.arange(slice_min, slice_max, step):
        section_points = get_cross_section(mesh, plane, coord_value)
        if len(section_points) > 0:
            output_filename = os.path.join(output_dir, f'cross_section_{plane}_{coord_value:.2f}.csv')
            with open(output_filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['X', 'Y', 'Z'])  # Header
                writer.writerows(section_points)  # Write points
            print(f"Exported cross-section to {output_filename}")
        else:
            print(f"No points found for {plane} plane at {coord_value:.2f}")

# User input for plane, step size, and output directory
plane = input("Enter slicing plane (xy, xz, yz): ").strip().lower()
if plane not in ['xy', 'xz', 'yz']:
    print("Invalid plane! Please use 'xy', 'xz', or 'yz'.")
    exit()

try:
    step = float(input("Enter step size for slicing (e.g., 0.5): "))
    if step <= 0:
        raise ValueError("Step size must be positive.")
except ValueError as e:
    print(f"Invalid step size: {e}")
    exit()

output_dir = "cross_sections"

# Save cross-sections to separate CSV files
save_cross_sections(mesh, plane, step, output_dir)
