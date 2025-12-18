from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Iterable, List, Sequence, Tuple

from shapely.geometry import Polygon as ShapelyPolygon

from .planner import RelationshipPlanner
from .solver import ConstraintSolver, NeutralPrimitive, SolveResult, mesh_from_primitive
from .schema import RelationshipDiagramSpec
from ..planner.bundle import GeometryBundle, PolygonFeature
from ..renderers import SvgRenderer


@dataclass(slots=True)
class ValidationReport:
    result: SolveResult
    errors: List[str]
    warnings: List[str]
    mesh_checksum: str | None = None


@dataclass(slots=True)
class DualRenderDiff:
    area_delta: float
    path_hash_a: str
    path_hash_b: str
    svg_hash_a: str
    svg_hash_b: str
    match: bool


def validate_relationship_spec(spec: RelationshipDiagramSpec) -> ValidationReport:
    solver = ConstraintSolver(spec)
    result = solver.solve()

    errors = [err.message for err in result.diagnostics.errors]
    warnings = [warn.message for warn in result.diagnostics.warnings]

    if spec.checks and len(result.diagnostics.check_results) < len(spec.checks):
        errors.append("checks block did not emit results for all clauses")

    errors.extend(_ifc_model_errors(result.primitives))

    checksum = mesh_checksum(result.primitives) if result.primitives else None
    return ValidationReport(result=result, errors=errors, warnings=warnings, mesh_checksum=checksum)


def mesh_checksum(primitives: Sequence[NeutralPrimitive]) -> str:
    digest = hashlib.sha256()
    for prim in sorted(primitives, key=lambda p: p.id):
        mesh = mesh_from_primitive(prim, to_meters=True)
        if mesh is None:
            continue
        digest.update(prim.id.encode("utf-8"))
        digest.update(mesh.vertices.round(6).tobytes())
        digest.update(mesh.faces.tobytes())
    return digest.hexdigest()


def dual_render_compare(bundle_a: GeometryBundle, bundle_b: GeometryBundle) -> DualRenderDiff:
    svg_renderer = SvgRenderer()
    svg_a = svg_renderer.render(bundle_a)
    svg_b = svg_renderer.render(bundle_b)
    path_hash_a = _bundle_path_hash(bundle_a.polygons)
    path_hash_b = _bundle_path_hash(bundle_b.polygons)
    svg_hash_a = hashlib.sha256(svg_a.encode("utf-8")).hexdigest()
    svg_hash_b = hashlib.sha256(svg_b.encode("utf-8")).hexdigest()
    area_delta = abs(_bundle_area(bundle_a.polygons) - _bundle_area(bundle_b.polygons))
    return DualRenderDiff(
        area_delta=area_delta,
        path_hash_a=path_hash_a,
        path_hash_b=path_hash_b,
        svg_hash_a=svg_hash_a,
        svg_hash_b=svg_hash_b,
        match=path_hash_a == path_hash_b and area_delta < 1e-6,
    )


def relationship_bundle(spec: RelationshipDiagramSpec) -> GeometryBundle:
    solver = ConstraintSolver(spec)
    result = solver.solve()
    planner = RelationshipPlanner(spec, result)
    planned = planner.plan()
    return next(view.bundle for view in planned if view.view == "plan")


def _bundle_path_hash(polygons: Iterable[PolygonFeature]) -> str:
    digest = hashlib.sha256()
    for feature in sorted(polygons, key=lambda f: f.id):
        digest.update(feature.id.encode("utf-8"))
        try:
            shape = feature.shape if isinstance(feature.shape, ShapelyPolygon) else ShapelyPolygon(feature.outer, feature.holes)
            bounds = shape.bounds
            digest.update(f"{bounds[0]:.3f},{bounds[1]:.3f},{bounds[2]:.3f},{bounds[3]:.3f}".encode("utf-8"))
            digest.update(f"{shape.area:.3f}".encode("utf-8"))
        except Exception:
            digest.update(_ring_bytes(feature.outer))
            for hole in feature.holes:
                digest.update(_ring_bytes(hole))
    return digest.hexdigest()


def _bundle_area(polygons: Iterable[PolygonFeature]) -> float:
    area = 0.0
    for feature in polygons:
        if isinstance(feature.shape, ShapelyPolygon):
            area += feature.shape.area
            continue
        try:
            polygon = ShapelyPolygon(feature.outer, feature.holes)
            area += polygon.area
        except Exception:
            continue
    return area


def _ring_bytes(points: Sequence[Tuple[float, float]]) -> bytes:
    digest = hashlib.sha256()
    for x, y in points:
        digest.update(f"{x:.3f},{y:.3f}".encode("utf-8"))
    return digest.digest()


def _ifc_model_errors(primitives: Sequence[NeutralPrimitive]) -> List[str]:
    try:
        from diagramming.planner.exporters import IfcExporter
        import ifcopenshell
    except Exception as exc:  # pragma: no cover - dependency guard
        return [f"IFC validation skipped: {exc}"]

    exporter = IfcExporter()
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "model.ifc"
        exporter.export(primitives, path)
        model = ifcopenshell.open(path)

    errors: List[str] = []
    project = next(iter(model.by_type("IfcProject")), None)
    if project is None:
        errors.append("IFC validation: missing IfcProject")
        return errors

    units = list(getattr(project.UnitsInContext, "Units", []))
    length_units = [u for u in units if getattr(u, "UnitType", "") == "LENGTHUNIT"]
    angle_units = [u for u in units if getattr(u, "UnitType", "") == "PLANEANGLEUNIT"]
    if not any(getattr(u, "Prefix", "").upper() == "MILLI" for u in length_units):
        errors.append("IFC validation: project units must be millimetres")
    if not any(str(getattr(u, "Name", "")).lower() == "degree" for u in angle_units):
        errors.append("IFC validation: project plane angle unit must be degrees")

    contexts = {ctx.ContextIdentifier for ctx in model.by_type("IfcGeometricRepresentationSubContext")}
    if "Axis" not in contexts:
        errors.append("IFC validation: Axis context missing")
    if "Body" not in contexts:
        errors.append("IFC validation: Body context missing")

    def _has_mapped_representation(element, context: str = "Body") -> bool:
        reps = getattr(getattr(element, "Representation", None), "Representations", []) or []
        for rep in reps:
            if not rep.ContextOfItems or getattr(rep.ContextOfItems, "ContextIdentifier", "") != context:
                continue
            items = getattr(rep, "Items", []) or []
            if any(getattr(item, "is_a", lambda *_: False)("IfcMappedItem") for item in items):
                return True
        return False

    rel_voids = model.by_type("IfcRelVoidsElement")
    openings = {rel.RelatedOpeningElement for rel in rel_voids if rel.RelatedOpeningElement}

    type_links = list(model.by_type("IfcRelDefinesByType"))
    type_by_tag = {}
    for link in type_links:
        for related in getattr(link, "RelatedObjects", []) or []:
            tag = getattr(related, "Tag", None)
            if tag:
                type_by_tag[tag] = link.RelatingType

    products_by_tag = {}
    mapped_body_by_tag = {}
    template_counts: Dict[str, int] = {}
    template_for_guid: Dict[str, str] = {}
    prim_by_id = {prim.id: prim for prim in primitives}
    id_for_guid = {prim.guid: prim.id for prim in primitives if prim.guid}
    expected_void_pairs = set()
    for prim in primitives:
        template = (
            getattr(prim, "template_id", None)
            or (prim.metadata.get("template_id", prim.id) if prim.metadata else None)
            or prim.id
        )
        template_counts[template] = template_counts.get(template, 0) + 1
        if prim.guid:
            template_for_guid[prim.guid] = template
        for void_id in prim.voids:
            void_prim = prim_by_id.get(void_id)
            if void_prim and void_prim.guid:
                expected_void_pairs.add((prim.guid, void_prim.guid))

    for element in model.by_type("IfcElement"):
        reps = getattr(getattr(element, "Representation", None), "Representations", []) or []
        rep_contexts = {getattr(rep.ContextOfItems, "ContextIdentifier", "") for rep in reps if rep.ContextOfItems}
        type_name = element.is_a()
        predefined = getattr(element, "PredefinedType", None)
        tag = getattr(element, "Tag", None)
        if tag:
            products_by_tag[tag] = element
            mapped_body_by_tag[tag] = _has_mapped_representation(element, "Body")
        if predefined is None or str(predefined).upper() in {"", "NOTDEFINED"}:
            errors.append(f"IFC validation: element {element.GlobalId} missing predefined type ({type_name})")

        if type_name in {"IfcBeam", "IfcMember"} and not {"Axis", "Body"} <= rep_contexts:
            errors.append(f"IFC validation: {type_name} {element.GlobalId} missing Axis/Body representations")
        elif type_name == "IfcSlab" and "Body" not in rep_contexts:
            errors.append(f"IFC validation: slab {element.GlobalId} missing Body representation")
        elif type_name == "IfcOpeningElement" and "Body" not in rep_contexts:
            errors.append(f"IFC validation: opening {element.GlobalId} missing Body representation")
        elif "Body" not in rep_contexts:
            errors.append(f"IFC validation: element {element.GlobalId} missing Body representation")

        has_material = any(
            getattr(rel, "RelatingMaterial", None)
            and getattr(rel.RelatingMaterial, "is_a", lambda *_: False)(material_type)
            for rel in getattr(element, "HasAssociations", []) or []
            for material_type in (
                "IfcMaterialProfileSetUsage",
                "IfcMaterialProfileSet",
                "IfcMaterialLayerSetUsage",
                "IfcMaterialLayerSet",
            )
        )
        if type_name in {"IfcBeam", "IfcMember"} and not has_material:
            errors.append(f"IFC validation: {type_name} {element.GlobalId} missing MaterialProfileSet usage")
        if type_name == "IfcSlab" and not has_material:
            errors.append(f"IFC validation: slab {element.GlobalId} missing MaterialLayerSet usage")

        if type_name == "IfcOpeningElement" and element not in openings:
            errors.append(f"IFC validation: opening {element.GlobalId} is not linked by IfcRelVoidsElement")

    actual_void_pairs = set()
    for rel in rel_voids:
        host_tag = getattr(rel.RelatingBuildingElement, "Tag", None)
        opening_tag = getattr(rel.RelatedOpeningElement, "Tag", None)
        if host_tag and opening_tag:
            actual_void_pairs.add((host_tag, opening_tag))
    missing_pairs = []
    for host_guid, void_guid in expected_void_pairs:
        pair = (host_guid, void_guid)
        if pair in actual_void_pairs:
            continue
        host_label = id_for_guid.get(host_guid, host_guid)
        void_label = id_for_guid.get(void_guid, void_guid)
        missing_pairs.append(f"{host_label}->{void_label}")
    if missing_pairs:
        sample = "; ".join(sorted(missing_pairs)[:3])
        suffix = " …" if len(missing_pairs) > 3 else ""
        errors.append(f"IFC validation: missing IfcRelVoidsElement for {len(missing_pairs)} pairs ({sample}{suffix})")

    repeated_templates = {template for template, count in template_counts.items() if count > 1}
    mapped_required = {"IfcBeam", "IfcMember", "IfcSlab"}
    missing_types: set[str] = set()
    missing_mapped: set[str] = set()
    for tag, product in products_by_tag.items():
        template = template_for_guid.get(tag)
        if template is None or template not in repeated_templates:
            continue
        class_name = product.is_a()
        if class_name not in mapped_required:
            continue
        type_record = type_by_tag.get(tag)
        if not type_record or not getattr(type_record, "is_a", lambda *_: False)(f"{class_name}Type"):
            missing_types.add(template)
        if not mapped_body_by_tag.get(tag):
            missing_mapped.add(template)
    if missing_types:
        errors.append(f"IFC validation: repeated templates missing type definitions ({', '.join(sorted(missing_types))})")
    if missing_mapped:
        errors.append(f"IFC validation: repeated templates missing mapped Body representations ({', '.join(sorted(missing_mapped))})")

    return errors


__all__ = [
    "DualRenderDiff",
    "ValidationReport",
    "dual_render_compare",
    "mesh_checksum",
    "relationship_bundle",
    "validate_relationship_spec",
]
