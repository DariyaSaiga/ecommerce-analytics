# 3d_model_fixed.py
# Full 7-step pipeline using Open3D (English output)
# Fixes voxel visualization: adaptive voxel_size + explicit cube visualization

import open3d as o3d
import numpy as np
import os
import copy
import sys

MODEL_FILENAME = "Dragon 2.5_ply.ply"  # <- change to your file if needed
OUTPUT_DIR = "3d_visual"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def safe_len(x):
    return len(x) if x is not None else 0

def center_and_scale_geometry(geom):
    """Center geometry at origin and scale to unit max extent for stable visualization."""
    try:
        bbox = geom.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        extent = bbox.get_extent().max()
        if extent > 0:
            geom.translate(-center)
            geom.scale(1.0 / extent, center=(0,0,0))
    except Exception:
        pass
    return geom

def create_voxel_cubes(voxel_grid, max_cubes=5000):
    """
    Convert an Open3D VoxelGrid to a list of small cube TriangleMesh objects for visualization.
    Limits number of cubes to max_cubes for performance.
    """
    voxels = voxel_grid.get_voxels()
    if len(voxels) == 0:
        return []

    voxel_size = voxel_grid.voxel_size
    origin = np.asarray(voxel_grid.origin)  # origin point

    # If too many voxels, sample indices uniformly to avoid performance issues
    if len(voxels) > max_cubes:
        indices = np.linspace(0, len(voxels)-1, max_cubes, dtype=int)
    else:
        indices = range(len(voxels))

    cubes = []
    half = voxel_size / 2.0
    for i in indices:
        v = voxels[i]
        # grid_index is a tuple of ints
        grid_index = np.array(v.grid_index, dtype=float)
        center = origin + grid_index * voxel_size + np.array([half, half, half])
        cube = o3d.geometry.TriangleMesh.create_box(width=voxel_size, height=voxel_size, depth=voxel_size)
        cube.compute_vertex_normals()
        # move cube so its center equals computed center
        cube.translate(center - np.array([half, half, half]))
        cube.paint_uniform_color([0.2, 0.7, 0.9])
        cubes.append(cube)
    return cubes

def adaptive_voxel_grid_from_pcd(pcd, initial_ratio=0.03, min_ratio=0.0005, attempts=8):
    """
    Try to create a VoxelGrid with an adaptive voxel_size based on pcd bbox.
    initial_ratio: voxel_size = bbox_max_extent * initial_ratio
    min_ratio: minimal allowed ratio to stop trying
    attempts: how many reductions to try
    Returns (voxel_grid, voxel_size) or (None, None) if failed
    """
    bbox = pcd.get_axis_aligned_bounding_box()
    max_extent = bbox.get_extent().max()
    if max_extent <= 0:
        return None, None

    ratio = initial_ratio
    for _ in range(attempts):
        voxel_size = max_extent * ratio
        if voxel_size <= 0:
            break
        vg = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=voxel_size)
        if len(vg.get_voxels()) > 0:
            return vg, voxel_size
        ratio = ratio / 2.0
        if ratio < min_ratio:
            break
    return None, None

# ================= STEP 1: Load and visualize original mesh =================
print("=" * 60)
print("STEP 1: LOADING AND VISUALIZATION")
print("=" * 60)

if not os.path.isfile(MODEL_FILENAME):
    sys.exit(f"Model file not found: {MODEL_FILENAME} (place it in the same folder)")

mesh = o3d.io.read_triangle_mesh(MODEL_FILENAME)
if mesh is None:
    sys.exit("Failed to read mesh. Check file and format.")

# Compute normals if missing
if not mesh.has_vertex_normals():
    try:
        mesh.compute_vertex_normals()
    except Exception:
        pass

print(f"Number of vertices: {safe_len(mesh.vertices)}")
print(f"Number of triangles: {safe_len(mesh.triangles)}")
print(f"Has colors: {mesh.has_vertex_colors()}")
print(f"Has normals: {mesh.has_vertex_normals()}")
print("\nWhat I understood:")
print("- This is the original 3D mesh loaded from the file.")
print("- Mesh is composed of vertices connected by triangles.")
print("- Normals improve lighting and rendering.")
print("Close the window to continue...")

# center and scale for stable viewing
mesh = center_and_scale_geometry(mesh)
o3d.visualization.draw_geometries([mesh], window_name="Step 1: Original Mesh", width=900, height=700)

# ================= STEP 2: Convert to point cloud =================
print("\n" + "=" * 60)
print("STEP 2: CONVERSION TO POINT CLOUD")
print("=" * 60)

# If mesh has triangles - sample uniformly; otherwise try to build from vertices
if safe_len(mesh.triangles) > 0:
    pcd = mesh.sample_points_uniformly(number_of_points=15000)
else:
    print("Mesh has no triangles. Trying to build PointCloud from vertex list...")
    pts = np.asarray(mesh.vertices)
    if pts is None or pts.shape[0] == 0:
        # try to read as point cloud file fallback
        pcd = o3d.io.read_point_cloud(MODEL_FILENAME)
        if pcd is None or len(pcd.points) == 0:
            sys.exit("No usable geometry in file (no triangles and no points). Try another model or re-export triangulated mesh.")
    else:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(pts)

# ensure normals
if not pcd.has_normals():
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamKNN(knn=30))
    pcd.normalize_normals()

# center & scale point cloud (already scaled if we used mesh sample)
pcd = center_and_scale_geometry(pcd)

print(f"Number of points: {safe_len(pcd.points)}")
print(f"Has colors: {pcd.has_colors()}")
print(f"Has normals: {pcd.has_normals()}")
print("\nWhat I understood:")
print("- Point cloud is a set of points in 3D space without explicit connections.")
print("- It represents the surface by sampling points over the mesh.")
print("- This representation is useful for certain processing steps.")
print("Close the window to continue...")

o3d.visualization.draw_geometries([pcd], window_name="Step 2: Point Cloud", width=900, height=700)

# ================= STEP 3: Poisson surface reconstruction =================
print("\n" + "=" * 60)
print("STEP 3: SURFACE RECONSTRUCTION (Poisson)")
print("=" * 60)

pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.05, max_nn=30))
pcd.orient_normals_consistent_tangent_plane(30)

print("Running Poisson reconstruction (depth=8). This may take some seconds...")
try:
    mesh_poisson, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)
    print("Poisson reconstruction succeeded.")
except Exception as e:
    print("Poisson reconstruction failed with depth=8:", e)
    print("Retrying with depth=7...")
    mesh_poisson, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=7)

# Crop by original bounding box to remove far artifacts
bbox = pcd.get_axis_aligned_bounding_box()
mesh_poisson = mesh_poisson.crop(bbox)

# clean up
mesh_poisson.remove_degenerate_triangles()
mesh_poisson.remove_duplicated_triangles()
mesh_poisson.remove_duplicated_vertices()
mesh_poisson.remove_non_manifold_edges()
if not mesh_poisson.has_vertex_normals():
    mesh_poisson.compute_vertex_normals()

if not mesh_poisson.has_vertex_colors():
    mesh_poisson.paint_uniform_color([0.7, 0.7, 0.7])

print(f"Number of vertices after reconstruction: {safe_len(mesh_poisson.vertices)}")
print(f"Number of triangles: {safe_len(mesh_poisson.triangles)}")
print(f"Has colors: {mesh_poisson.has_vertex_colors()}")
print(f"Has normals: {mesh_poisson.has_vertex_normals()}")
print("\nWhat I understood:")
print("- Poisson reconstructs a smooth watertight surface from the point cloud.")
print("- It uses normals for orientation and generates a filled mesh.")
print("- Low-density regions are typically artifacts and may be removed.")
print("Close the window to continue...")

o3d.visualization.draw_geometries([mesh_poisson], window_name="Step 3: Poisson Mesh", width=900, height=700)

# ================= STEP 4: VOXELIZATION (fixed & robust) =================
print("\n" + "=" * 60)
print("STEP 4: VOXELIZATION")
print("=" * 60)

# Adaptive voxel grid creation
voxel_grid, used_voxel_size = adaptive_voxel_grid_from_pcd(pcd, initial_ratio=0.03, min_ratio=0.0005, attempts=10)
if voxel_grid is None:
    print("Adaptive voxelization failed (no voxels found). For safety, trying a small fixed voxel_size...")
    # fallback
    for vs in [0.02, 0.01, 0.005]:
        vg = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=vs)
        if len(vg.get_voxels()) > 0:
            voxel_grid = vg
            used_voxel_size = vs
            break

if voxel_grid is None or len(voxel_grid.get_voxels()) == 0:
    print("Voxelization produced no voxels. Please try a different voxel_size or a denser point cloud.")
    voxels = []
else:
    voxels = voxel_grid.get_voxels()
    print(f"Voxel size used: {used_voxel_size:.6f}")
    print(f"Number of voxels: {len(voxels)}")

# Visualize voxel grid. Some Open3D versions don't render VoxelGrid nicely,
# so convert to cubes for reliable visualization.
voxel_cubes = create_voxel_cubes(voxel_grid, max_cubes=2000) if voxel_grid is not None else []
if len(voxel_cubes) > 0:
    print(f"Displaying {len(voxel_cubes)} voxel cubes (limited for performance).")
    o3d.visualization.draw_geometries(voxel_cubes, window_name="Step 4: Voxel Grid (cubes)", width=900, height=700)
else:
    print("No voxel cubes to display (empty voxel grid).")

# ================= STEP 5: ADD A PLANE =================
print("\n" + "=" * 60)
print("STEP 5: ADDING A PLANE")
print("=" * 60)

center = pcd.get_center()
bbox = pcd.get_axis_aligned_bounding_box()
bbox_size = bbox.get_extent()
plane_width = max(bbox_size[0], bbox_size[1]) * 0.8
plane_height = max(bbox_size[0], bbox_size[1]) * 0.8
plane_thickness = max(bbox_size) * 0.005 if max(bbox_size) > 0 else 0.01

plane_mesh = o3d.geometry.TriangleMesh.create_box(width=plane_width, height=plane_height, depth=plane_thickness)
plane_mesh.translate(center - np.array([plane_width/2, plane_height/2, plane_thickness/2]))
plane_mesh.compute_vertex_normals()
plane_mesh.paint_uniform_color([1.0, 0.2, 0.2])

print(f"Model center: {center}")
print(f"Plane dims: {plane_width:.4f} x {plane_height:.4f} x {plane_thickness:.4f}")
print("Close the window to continue...")

o3d.visualization.draw_geometries([pcd, plane_mesh], window_name="Step 5: Model + Plane", width=900, height=700)

# ================= STEP 6: SURFACE CLIPPING =================
print("\n" + "=" * 60)
print("STEP 6: SURFACE CLIPPING")
print("=" * 60)

points = np.asarray(pcd.points)
plane_origin = plane_mesh.get_center()
plane_normal = np.array([-1.0, 0.0, 0.0])  # we choose -X direction as normal

d = np.dot(points - plane_origin, plane_normal)
mask_keep = d <= 0.0
points_clipped = points[mask_keep]
pcd_clipped = o3d.geometry.PointCloud()
pcd_clipped.points = o3d.utility.Vector3dVector(points_clipped)

if pcd.has_colors():
    pcd_clipped.colors = o3d.utility.Vector3dVector(np.asarray(pcd.colors)[mask_keep])
if pcd.has_normals():
    pcd_clipped.normals = o3d.utility.Vector3dVector(np.asarray(pcd.normals)[mask_keep])
else:
    pcd_clipped.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamKNN(knn=30))

print(f"Points before clipping: {len(points)}")
print(f"Points after clipping: {len(points_clipped)}")
print(f"Points removed: {len(points) - len(points_clipped)}")
print("Close the window to continue...")

o3d.visualization.draw_geometries([pcd_clipped], window_name="Step 6: Clipped PointCloud", width=900, height=700)

# ================= STEP 7: COLOR GRADIENT & EXTREMA =================
print("\n" + "=" * 60)
print("STEP 7: WORKING WITH COLOR AND EXTREMES")
print("=" * 60)

pts_final = np.asarray(pcd_clipped.points)
if pts_final.shape[0] == 0:
    print("No points remaining after clipping — skipping step 7.")
    sys.exit(0)

axis_idx = 2  # Z axis by default (0:X,1:Y,2:Z)
vals = pts_final[:, axis_idx]
vmin = vals.min()
vmax = vals.max()
if vmax - vmin == 0:
    norm = np.zeros_like(vals)
else:
    norm = (vals - vmin) / (vmax - vmin)

# Create gradient (blue->green->yellow->red)
colors = np.zeros((len(norm), 3))
for i, t in enumerate(norm):
    colors[i] = [t, 1 - t, 0.5 * (1 - abs(0.5 - t) * 2)]

pcd_clipped.colors = o3d.utility.Vector3dVector(colors)

min_idx = np.argmin(vals)
max_idx = np.argmax(vals)
min_pt = pts_final[min_idx]
max_pt = pts_final[max_idx]

sphere_radius = max(bbox_size) * 0.02 if max(bbox_size) > 0 else 0.02
sphere_min = o3d.geometry.TriangleMesh.create_sphere(radius=sphere_radius)
sphere_min.translate(min_pt)
sphere_min.paint_uniform_color([0, 0, 1])
sphere_min.compute_vertex_normals()

sphere_max = o3d.geometry.TriangleMesh.create_sphere(radius=sphere_radius)
sphere_max.translate(max_pt)
sphere_max.paint_uniform_color([1, 0, 0])
sphere_max.compute_vertex_normals()

print(f"Min point (Z): {min_pt.tolist()}")
print(f"Max point (Z): {max_pt.tolist()}")
print(f"Height difference: {vmax - vmin:.6f}")
print("Close the window to finish...")

o3d.visualization.draw_geometries([pcd_clipped, sphere_min, sphere_max],
                                  window_name="Step 7: Gradient & Extrema", width=900, height=700)

print("\n" + "=" * 60)
print("ALL STEPS COMPLETED")
print("=" * 60)
