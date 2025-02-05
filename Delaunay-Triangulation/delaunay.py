"""
Delaunay Triangulation Combined Script
Combines steps (a), (b), (c), and (d) into a single executable script.
All images are saved in the directory: /Users/yudonglei/Desktop/section2_local/Delaunay-Triangulation

- (a) Generate and visualize the surface point clouds.
- (b) Perform 2D Delaunay triangulation on top & bottom surfaces.
- (c) Generate a 3D volume mesh using Delaunay tetrahedralization.
- (d) Extract the surface mesh from the volume mesh.

"""

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import Delaunay
from collections import Counter
from matplotlib import cm

# -----------------------
# SET OUTPUT DIRECTORY
# -----------------------
SAVE_DIR = "/Users/yudonglei/Desktop/section2_local/Delaunay-Triangulation"
os.makedirs(SAVE_DIR, exist_ok=True)

# -----------------------
# 1. Define Surface Functions
# -----------------------
def surface1(x, y):
    """Paraboloid surface: z = 2*(x^2 + y^2)"""
    return 2 * x**2 + 2 * y**2

def surface2(x, y):
    """Gaussian bump surface: z = 2 * exp(-(x^2 + y^2))"""
    return 2 * np.exp(-x**2 - y**2)

def triangle_area(x, y):
    return np.abs(np.cross(x[1:] - x[0], y[1:] - y[0])) / 2

# -----------------------
# 2. Generate Point Clouds (Step a)
# -----------------------
def generate_surface(num_points=100):
    """Generates a uniform grid of (x, y) and computes the corresponding z-values for two surfaces."""
    x = np.linspace(-1, 1, num_points)
    y = np.linspace(-1, 1, num_points)
    X, Y = np.meshgrid(x, y)
    Z1 = surface1(X, Y)
    Z2 = surface2(X, Y)
    return X, Y, Z1, Z2

def plot_surfaces(X, Y, Z1, Z2, save_path=None):
    """Plots both surfaces in 3D space."""
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_surface(X, Y, Z1, color='gray', alpha=0.3)
    ax.plot_surface(X, Y, Z2, cmap='viridis', edgecolor='none')

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([0, 4])
    ax.set_title("Closed Surface Visualization")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()

# -----------------------
# 3. Perform 2D Delaunay Triangulation (Step b)
# -----------------------
def generate_closed_surface(x_points=21, y_points=21):
    x = np.linspace(-1, 1, x_points)
    y = np.linspace(-1, 1, y_points)
    x, y = np.meshgrid(x, y)
    indices = surface1(x, y) <= surface2(x, y)
    n = indices.sum()
    x = x[indices]
    y = y[indices]
    
    triangles = Delaunay(np.c_[x, y]).simplices
    triangles = [v for v in triangles if not np.isclose(triangle_area(x[v], y[v]), 0)]
    
    edge_counter = Counter()
    for vertices in triangles:
        i1, i2, i3 = sorted(vertices)
        edge_counter.update([(i1, i2), (i2, i3), (i1, i3)])
    
    boundary = np.unique([edge for edge, count in edge_counter.items() if count == 1])
    inner = np.setdiff1d(np.arange(n), boundary)
    
    all_x = np.concatenate([x, x])
    all_y = np.concatenate([y, y])
    all_z = np.concatenate([surface1(x, y), surface2(x, y)])
    all_triangles = np.concatenate([triangles, [[i if i in boundary else i+n for i in v] for v in triangles]])
    
    return all_x, all_y, all_z, all_triangles

def plot_closed_surface(all_x, all_y, all_z, all_triangles, save_path):
    fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
    ax.plot_trisurf(all_x, all_y, all_z, triangles=all_triangles, cmap=cm.viridis, edgecolor="k")
    ax.set_title("Surface Mesh from Combining two surfaces")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()

# -----------------------
# 4. Generate 3D Volume Mesh (Step c)
# -----------------------
def generate_volume_points(num_x=51, num_y=51, num_z=21):
    """Generates a 3D point cloud within the volume bounded by the two surfaces."""
    x = np.linspace(-1, 1, num_x)
    y = np.linspace(-1, 1, num_y)
    z = np.linspace(0, 2, num_z)
    x, y, z = np.meshgrid(x, y, z)

    indices = np.logical_and(surface1(x, y) <= z, z <= surface2(x, y))
    x, y, z = x[indices], y[indices], z[indices]

    return np.c_[x, y, z]

def delaunay_volume_mesh(points):
    """Performs 3D Delaunay triangulation on the point cloud."""
    return Delaunay(points)

def extract_boundary_faces(tetrahedra):
    """Extracts faces that appear exactly once in the tetrahedral mesh."""
    face_counter = Counter()
    for vertices in tetrahedra:
        i1, i2, i3, i4 = sorted(vertices)
        face_counter.update([(i1, i2, i3), (i1, i2, i4), (i1, i3, i4), (i2, i3, i4)])

    boundary_faces = [face for face, count in face_counter.items() if count == 1]
    return np.array(boundary_faces)

# -----------------------
# 5. Extract Surface Mesh (Step d)
# -----------------------
def extract_surface_mesh(tetrahedra):
    """Extracts the external faces of the volume mesh."""
    return extract_boundary_faces(tetrahedra)

def plot_surface_mesh(points, surface_faces, save_path):
    """Plots the extracted surface mesh from the volume."""
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_trisurf(points[:, 0], points[:, 1], points[:, 2], triangles=surface_faces, cmap=cm.viridis, edgecolor='k')

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Extracted Surface Mesh from Volume Mesh")

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()

# -----------------------
# 6. Main Execution
# -----------------------
def main():
    # Step (a): Generate and visualize surfaces
    X, Y, Z1, Z2 = generate_surface(num_points=100)
    plot_surfaces(X, Y, Z1, Z2, save_path=f"{SAVE_DIR}/a_surface_plot.png")

    # Step (b): 2D Delaunay triangulation
    all_x, all_y, all_z, all_triangles = generate_closed_surface()
    plot_closed_surface(all_x, all_y, all_z, all_triangles, f"{SAVE_DIR}/b_closed_surface.png")
    print("Updated Step (b) - Closed Surface Generated.")

    # Step (c): 3D Volume Delaunay triangulation
    volume_points = generate_volume_points(num_x=51, num_y=51, num_z=21)
    tetra_mesh = delaunay_volume_mesh(volume_points)
    boundary_faces = extract_boundary_faces(tetra_mesh.simplices)
    plot_surface_mesh(volume_points, boundary_faces, f"{SAVE_DIR}/c_delaunay_volume_mesh.png")

    # Step (d): Extract surface mesh from volume
    surface_faces = extract_surface_mesh(tetra_mesh.simplices)
    plot_surface_mesh(volume_points, surface_faces, f"{SAVE_DIR}/d_surface_mesh_from_volume.png")

if __name__ == "__main__":
    main()
