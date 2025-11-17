from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pyrender
from PIL import Image
from trimesh.transformations import rotation_matrix

from ..planner.bundle import GeometryBundle


def render_orthographic_png(
    bundle: GeometryBundle,
    output_path: Path,
    image_size: int = 1024,
    distance_factor: float = 2.0,
    pitch_degrees: float = 45.0,
    yaw_degrees: float = -35.0,
) -> None:
    """
    Render an orthographic PNG of the bundle's canonical 3D scene.

    The camera looks toward the scene centre from a raised, angled position,
    avoiding perspective distortion while revealing extrusion depth.
    """

    if bundle.scene is None:
        raise ValueError("Geometry bundle does not contain a 3D scene; cannot render orthographic view.")

    scene = bundle.scene

    pyr_scene = pyrender.Scene(bg_color=[1.0, 1.0, 1.0, 0.0], ambient_light=[0.35, 0.35, 0.35])

    for node_name in scene.graph.nodes_geometry:
        transform, geometry_name = scene.graph[node_name]
        mesh = scene.geometry[geometry_name]
        pyr_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=False)
        pyr_scene.add(pyr_mesh, pose=transform)

    bounds = scene.bounds
    scene_min = bounds[0]
    scene_max = bounds[1]
    centre = (scene_min + scene_max) / 2.0
    extents = scene_max - scene_min

    horizontal_extent = float(np.max(extents[:2])) * 0.6
    horizontal_extent = max(horizontal_extent, 0.5)
    xmag = horizontal_extent
    ymag = horizontal_extent

    distance = float(np.max(extents[:2]) * distance_factor)
    eye = centre + np.array([0.0, -distance, distance])

    pose = np.eye(4)
    pose[:3, 3] = eye
    pose = pose @ rotation_matrix(np.deg2rad(pitch_degrees), [1.0, 0.0, 0.0])
    pose = pose @ rotation_matrix(np.deg2rad(yaw_degrees), [0.0, 0.0, 1.0])

    camera = pyrender.OrthographicCamera(
        xmag=xmag,
        ymag=ymag,
        znear=0.01,
        zfar=float(extents[2] + distance * 2.0),
    )
    pyr_scene.add(camera, pose=pose)

    light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
    pyr_scene.add(light, pose=pose)

    renderer = pyrender.OffscreenRenderer(viewport_width=image_size, viewport_height=image_size)
    color, _ = renderer.render(pyr_scene, flags=pyrender.RenderFlags.ALL_SOLID)
    renderer.delete()

    image = Image.fromarray(color)
    image.save(output_path)
