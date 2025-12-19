from __future__ import annotations

import datetime
import math
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.unit
import numpy as np

from ...relationships.solver import ComponentTransform, ConnectionHint, NeutralPrimitive


MM_TO_METERS = 0.001
LINEAR_CLASSES = {"ifcbeam", "ifcmember"}
SLAB_CLASSES = {"ifcslab"}


@dataclass(slots=True)
class IfcExportOptions:
    include_metadata: bool = True
    length_unit: str = "MILLIMETERS"


@dataclass(slots=True)
class TypeRecord:
    type_entity: Optional[ifcopenshell.entity_instance] = None
    body_representation: Optional[ifcopenshell.entity_instance] = None
    axis_representation: Optional[ifcopenshell.entity_instance] = None
    material_set: Optional[ifcopenshell.entity_instance] = None
    usage_kind: Optional[str] = None  # "profile" or "layer"
    psets: List[ifcopenshell.entity_instance] = field(default_factory=list)


class IfcExporter:
    """
    Emit an IFC 4.3 Reference View model from neutral CadQuery-backed primitives.
    Builds Axis + Body subcontexts, applies swept solids when possible, assigns
    material profile/layer usages, models openings, mapped items, and connection
    geometry, and preserves stable GUIDs throughout.
    """

    def __init__(self, options: Optional[IfcExportOptions] = None) -> None:
        self.options = options or IfcExportOptions()
        self._type_cache: Dict[str, TypeRecord] = {}
        self._profile_cache: Dict[Tuple[float, float], ifcopenshell.entity_instance] = {}
        self._material_cache: Dict[str, ifcopenshell.entity_instance] = {}
        self._seen_connections: set[Tuple[str, str, str, str]] = set()

    # ------------------------------------------------------------------ #
    def export(self, primitives: Sequence[NeutralPrimitive], out_path: Path) -> None:
        if not primitives:
            raise ValueError("No primitives to export")

        self._type_cache.clear()
        self._profile_cache.clear()
        self._material_cache.clear()
        self._seen_connections.clear()
        model, contexts, storey = self._bootstrap_model()
        primitives_by_id = {prim.id: prim for prim in primitives}
        reference_by_template: Dict[str, NeutralPrimitive] = {}
        products_by_ref: Dict[str, ifcopenshell.entity_instance] = {}

        for primitive in primitives:
            template = (
                getattr(primitive, "template_id", None)
                or (primitive.metadata.get("template_id") if primitive.metadata else None)
                or primitive.id
            )
            if template:
                existing = reference_by_template.get(template)
                if existing is None or getattr(existing, "origin", "clone") != "original" and getattr(primitive, "origin", "clone") == "original":
                    reference_by_template[template] = primitive
                reference_by_template.setdefault(template, primitive)
            class_lower = (primitive.class_name or "").lower()
            if class_lower == "ifcopeningelement":
                primitives_by_id[primitive.id] = primitive
                continue
            product = self._create_product(model, primitive)
            self._assign_spatial(model, product, storey)
            self._place_product(model, product, primitive, storey.ObjectPlacement)

            type_record = self._get_or_create_type(model, contexts, primitive)
            if type_record and type_record.type_entity is not None:
                ifcopenshell.api.run(
                    "type.assign_type",
                    model,
                    related_objects=[product],
                    relating_type=type_record.type_entity,
                )
            self._assign_representations(model, contexts, product, primitive, type_record)
            self._assign_materials(model, product, primitive, type_record)
            self._apply_predefined_type(product, primitive, type_record)
            self._assign_property_sets(model, product, primitive, type_record)

            products_by_ref[primitive.id] = product
            base_ref = primitive.metadata.get("component_id") if primitive.metadata else None
            if base_ref and base_ref not in products_by_ref:
                products_by_ref[base_ref] = product

        self._apply_openings(model, contexts, primitives_by_id, products_by_ref, reference_by_template, storey)
        self._apply_connections(model, primitives_by_id, products_by_ref)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        model.write(out_path)

    # ------------------------------------------------------------------ #
    def _bootstrap_model(self):
        model = self._create_ifc_file()
        project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject")
        self._set_guid(project, "project")
        units = self._build_units(model)
        ifcopenshell.api.run("unit.assign_unit", model, units=units)

        model_context = ifcopenshell.api.run(
            "context.add_context",
            model,
            context_type="Model",
            target_view="MODEL_VIEW",
        )
        axis_context = ifcopenshell.api.run(
            "context.add_context",
            model,
            context_type="Model",
            context_identifier="Axis",
            target_view="GRAPH_VIEW",
            parent=model_context,
        )
        body_context = ifcopenshell.api.run(
            "context.add_context",
            model,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model_context,
        )

        site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite", name="Site")
        self._set_guid(site, "site")
        building = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding", name="Building")
        self._set_guid(building, "building")
        storey = ifcopenshell.api.run(
            "root.create_entity",
            model,
            ifc_class="IfcBuildingStorey",
            name="Storey",
            predefined_type="ELEMENT",
        )
        self._set_guid(storey, "storey")

        self._ensure_placement(model, site, None)
        self._ensure_placement(model, building, site.ObjectPlacement)
        self._ensure_placement(model, storey, building.ObjectPlacement)

        ifcopenshell.api.run("aggregate.assign_object", model, relating_object=project, products=[site])
        ifcopenshell.api.run("aggregate.assign_object", model, relating_object=site, products=[building])
        ifcopenshell.api.run("aggregate.assign_object", model, relating_object=building, products=[storey])

        contexts = {"model": model_context, "axis": axis_context, "body": body_context}
        return model, contexts, storey

    def _build_units(self, model):
        length = ifcopenshell.api.run("unit.add_si_unit", model, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.run("unit.add_si_unit", model, unit_type="AREAUNIT", prefix="MILLI")
        volume = ifcopenshell.api.run("unit.add_si_unit", model, unit_type="VOLUMEUNIT", prefix="MILLI")
        angle = ifcopenshell.api.run("unit.add_conversion_based_unit", model, name="degree")
        return [length, area, volume, angle]

    # ------------------------------------------------------------------ #
    def _create_product(self, model, primitive: NeutralPrimitive):
        class_name = primitive.class_name or "IfcBuildingElementProxy"
        if not class_name.lower().startswith("ifc"):
            class_name = "IfcBuildingElementProxy"
        predefined = None
        if primitive.ifc and isinstance(primitive.ifc, dict):
            predefined = primitive.ifc.get("predefined_type")

        try:
            product = ifcopenshell.api.run(
                "root.create_entity",
                model,
                ifc_class=class_name,
                name=primitive.metadata.get("label") if primitive.metadata else primitive.id,
                predefined_type=predefined,
            )
        except Exception:
            product = ifcopenshell.api.run(
                "root.create_entity",
                model,
                ifc_class="IfcBuildingElementProxy",
                name=primitive.metadata.get("label") if primitive.metadata else primitive.id,
                predefined_type=None,
            )
        if predefined and hasattr(product, "PredefinedType"):
            try:
                product.PredefinedType = predefined
            except Exception:
                pass
        if not getattr(product, "Name", None):
            try:
                product.Name = primitive.id
            except Exception:
                pass
        if primitive.guid:
            try:
                product.GlobalId = ifcopenshell.guid.compress(str(uuid.UUID(primitive.guid)))
            except Exception:
                pass
        product.Tag = primitive.guid
        return product

    def _assign_spatial(self, model, product, storey):
        ifcopenshell.api.run(
            "spatial.assign_container",
            model,
            products=[product],
            relating_structure=storey,
        )

    def _place_product(self, model, product, primitive: NeutralPrimitive, parent_placement):
        placement = self._placement_from_transform(model, primitive.transform, parent_placement)
        product.ObjectPlacement = placement

    # ------------------------------------------------------------------ #
    def _get_or_create_type(
        self,
        model,
        contexts: Dict[str, ifcopenshell.entity_instance],
        primitive: NeutralPrimitive,
    ) -> Optional[TypeRecord]:
        key = self._type_key(primitive)
        if key in self._type_cache:
            return self._type_cache[key]

        type_class = self._type_class_for(primitive.class_name)
        record = TypeRecord()
        type_entity = None
        if type_class:
            predefined = None
            if primitive.ifc and isinstance(primitive.ifc, dict):
                predefined = primitive.ifc.get("predefined_type")
            type_entity = ifcopenshell.api.run(
                "root.create_entity",
                model,
                ifc_class=type_class,
                name=f"{primitive.class_name or 'Element'} type",
                predefined_type=predefined,
            )
            if predefined and hasattr(type_entity, "PredefinedType"):
                try:
                    type_entity.PredefinedType = predefined
                except Exception:
                    pass
            self._set_guid(type_entity, f"type::{key}")
            record.type_entity = type_entity

        record.body_representation = self._body_representation(model, contexts["body"], primitive, mapped=False)
        if record.body_representation is not None and record.type_entity is not None:
            ifcopenshell.api.run(
                "geometry.assign_representation",
                model,
                product=record.type_entity,
                representation=record.body_representation,
            )

        record.axis_representation = self._axis_representation(model, contexts["axis"], primitive, mapped=False)
        if record.axis_representation is not None and record.type_entity is not None:
            ifcopenshell.api.run(
                "geometry.assign_representation",
                model,
                product=record.type_entity,
                representation=record.axis_representation,
            )

        record.usage_kind, record.material_set = self._material_set_for_type(model, primitive, record.type_entity)
        record.psets = self._property_sets_for_type(model, record.type_entity, primitive)
        self._type_cache[key] = record
        return record

    def _assign_representations(
        self,
        model,
        contexts: Dict[str, ifcopenshell.entity_instance],
        product,
        primitive: NeutralPrimitive,
        type_record: Optional[TypeRecord],
    ) -> None:
        body_rep = None
        axis_rep = None
        if type_record and type_record.body_representation is not None:
            body_rep = ifcopenshell.api.run(
                "geometry.map_representation",
                model,
                representation=type_record.body_representation,
            )
        else:
            body_rep = self._body_representation(model, contexts["body"], primitive)

        if body_rep is not None:
            ifcopenshell.api.run("geometry.assign_representation", model, product=product, representation=body_rep)

        if type_record and type_record.axis_representation is not None:
            axis_rep = ifcopenshell.api.run(
                "geometry.map_representation",
                model,
                representation=type_record.axis_representation,
            )
        else:
            axis_rep = self._axis_representation(model, contexts["axis"], primitive)
        if axis_rep is not None:
            ifcopenshell.api.run("geometry.assign_representation", model, product=product, representation=axis_rep)

    def _assign_materials(
        self,
        model,
        product,
        primitive: NeutralPrimitive,
        type_record: Optional[TypeRecord],
    ) -> None:
        usage_kind = type_record.usage_kind if type_record else None
        if usage_kind == "profile":
            ifcopenshell.api.run(
                "material.assign_material",
                model,
                products=[product],
                type="IfcMaterialProfileSetUsage",
            )
        elif usage_kind == "layer":
            ifcopenshell.api.run(
                "material.assign_material",
                model,
                products=[product],
                type="IfcMaterialLayerSetUsage",
            )
        elif primitive.material:
            material = self._material_cache.get(primitive.material)
            if material is None:
                material = ifcopenshell.api.run("material.add_material", model, name=primitive.material)
                self._material_cache[primitive.material] = material
            ifcopenshell.api.run(
                "material.assign_material",
                model,
                products=[product],
                type="IfcMaterial",
                material=material,
            )

    def _assign_property_sets(
        self,
        model,
        product,
        primitive: NeutralPrimitive,
        type_record: Optional[TypeRecord],
    ) -> None:
        for pset in (type_record.psets if type_record else ()):
            ifcopenshell.api.run("pset.assign_pset", model, products=[product], pset=pset)
        auto_pset_name, auto_props = self._auto_pset(primitive)
        if auto_pset_name and auto_props:
            pset = ifcopenshell.api.run("pset.add_pset", model, product=product, name=auto_pset_name)
            ifcopenshell.api.run("pset.edit_pset", model, pset=pset, properties=auto_props)
        user_psets = []
        if primitive.ifc and isinstance(primitive.ifc, dict):
            user_psets = primitive.ifc.get("psets") or []
        for entry in user_psets:
            name = entry.get("name")
            props = entry.get("props") or {}
            if not name or not isinstance(props, Mapping):
                continue
            pset = ifcopenshell.api.run("pset.add_pset", model, product=product, name=name)
            ifcopenshell.api.run("pset.edit_pset", model, pset=pset, properties=props)

    def _apply_predefined_type(
        self,
        product,
        primitive: NeutralPrimitive,
        type_record: Optional[TypeRecord],
    ) -> None:
        predefined = primitive.ifc.get("predefined_type") if primitive.ifc else None
        if predefined and hasattr(product, "PredefinedType"):
            try:
                product.PredefinedType = predefined
            except Exception:
                pass
        if predefined and type_record and type_record.type_entity is not None and hasattr(
            type_record.type_entity, "PredefinedType"
        ):
            try:
                type_record.type_entity.PredefinedType = predefined
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    def _material_set_for_type(
        self,
        model,
        primitive: NeutralPrimitive,
        type_entity: Optional[ifcopenshell.entity_instance],
    ) -> Tuple[Optional[str], Optional[ifcopenshell.entity_instance]]:
        if type_entity is None:
            return None, None
        material_name = primitive.material or primitive.class_name or "Material"
        material = self._material_cache.get(material_name)
        if material is None:
            material = ifcopenshell.api.run("material.add_material", model, name=material_name)
            self._material_cache[material_name] = material

        class_lower = (primitive.class_name or "").lower()
        if class_lower in LINEAR_CLASSES:
            profile_dims = (primitive.size[2], primitive.size[1])
            profile_def = self._rectangle_profile(model, profile_dims[0], profile_dims[1])
            profile_set = ifcopenshell.api.run(
                "material.add_material_set",
                model,
                name=f"{material_name}-profiles",
                set_type="IfcMaterialProfileSet",
            )
            ifcopenshell.api.run(
                "material.add_profile",
                model,
                profile_set=profile_set,
                material=material,
                profile=profile_def,
            )
            ifcopenshell.api.run(
                "material.assign_material",
                model,
                products=[type_entity],
                type="IfcMaterialProfileSet",
                material=profile_set,
            )
            return "profile", profile_set

        if class_lower in SLAB_CLASSES:
            layer_set = ifcopenshell.api.run(
                "material.add_material_set",
                model,
                name=f"{material_name}-layers",
                set_type="IfcMaterialLayerSet",
            )
            layer = ifcopenshell.api.run(
                "material.add_layer",
                model,
                layer_set=layer_set,
                material=material,
            )
            ifcopenshell.api.run(
                "material.edit_layer",
                model,
                layer=layer,
                attributes={"LayerThickness": primitive.size[2]},
            )
            ifcopenshell.api.run(
                "material.assign_material",
                model,
                products=[type_entity],
                type="IfcMaterialLayerSet",
                material=layer_set,
            )
            return "layer", layer_set

        ifcopenshell.api.run(
            "material.assign_material",
            model,
            products=[type_entity],
            type="IfcMaterial",
            material=material,
        )
        return None, material

    def _property_sets_for_type(
        self,
        model,
        type_entity: Optional[ifcopenshell.entity_instance],
        primitive: NeutralPrimitive,
    ) -> List[ifcopenshell.entity_instance]:
        if type_entity is None:
            return []
        pset_name, props = self._auto_pset(primitive)
        if not pset_name or not props:
            return []
        pset = ifcopenshell.api.run("pset.add_pset", model, product=type_entity, name=pset_name)
        ifcopenshell.api.run("pset.edit_pset", model, pset=pset, properties=props)
        return [pset]

    # ------------------------------------------------------------------ #
    def _axis_representation(
        self, model, context, primitive: NeutralPrimitive, mapped: bool = True
    ) -> Optional[ifcopenshell.entity_instance]:
        class_lower = (primitive.class_name or "").lower()
        if class_lower not in LINEAR_CLASSES:
            return None
        length = primitive.size[0]
        orientation = self._orientation_axes(primitive)
        direction = self._axis_direction(primitive.transform.rotation[2], orientation=orientation)
        tx, ty, tz = primitive.transform.position
        half = length / 2.0
        start = (tx - direction[0] * half, ty - direction[1] * half, tz - direction[2] * half)
        end = (tx + direction[0] * half, ty + direction[1] * half, tz + direction[2] * half)
        axis = (
            (start[0] * MM_TO_METERS, start[1] * MM_TO_METERS, start[2] * MM_TO_METERS),
            (end[0] * MM_TO_METERS, end[1] * MM_TO_METERS, end[2] * MM_TO_METERS),
        )
        return ifcopenshell.api.run("geometry.add_axis_representation", model, context=context, axis=axis)

    def _body_representation(
        self, model, context, primitive: NeutralPrimitive, mapped: bool = True
    ) -> Optional[ifcopenshell.entity_instance]:
        profile_def, depth, placement_axes = self._profile_for_primitive(model, primitive)
        if profile_def is not None and depth > 0:
            depth_m = depth * MM_TO_METERS
            return ifcopenshell.api.run(
                "geometry.add_profile_representation",
                model,
                context=context,
                profile=profile_def,
                depth=depth_m,
                placement_zx_axes=placement_axes,
            )

        vertices, faces = self._tessellate(primitive)
        if not vertices or not faces:
            return None
        vertices_array = np.array([[v for v in vertices]], dtype=float)
        faces_array = [[[int(a) for a in face] for face in faces]]
        return ifcopenshell.api.run(
            "geometry.add_mesh_representation",
            model,
            context=context,
            vertices=vertices_array,
            faces=faces_array,
            force_faceted_brep=False,
        )

    def _profile_for_primitive(
        self, model, primitive: NeutralPrimitive
    ) -> Tuple[Optional[ifcopenshell.entity_instance], float, Tuple[Tuple[float, float, float], Tuple[float, float, float]]]:
        class_lower = (primitive.class_name or "").lower()
        profile = primitive.profile.lower()
        orientation = self._orientation_axes(primitive)
        axis_dir = self._axis_direction(primitive.transform.rotation[2], orientation=orientation)
        default_axes = (orientation[2], orientation[0])

        if profile == "rectangle":
            if class_lower in LINEAR_CLASSES:
                profile_def = self._rectangle_profile(model, primitive.size[2], primitive.size[1])
                placement_axes = (axis_dir, orientation[2])
                return profile_def, primitive.size[0], placement_axes
            profile_def = self._rectangle_profile(model, primitive.size[0], primitive.size[1])
            return profile_def, primitive.size[2], default_axes

        return None, 0.0, default_axes

    def _rectangle_profile(self, model, x_dim: float, y_dim: float) -> ifcopenshell.entity_instance:
        key = (round(x_dim, 6), round(y_dim, 6))
        if key in self._profile_cache:
            return self._profile_cache[key]
        position = model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((0.0, 0.0)))
        profile_def = model.createIfcRectangleProfileDef("AREA", None, position, x_dim, y_dim)
        self._profile_cache[key] = profile_def
        return profile_def

    # ------------------------------------------------------------------ #
    def _apply_openings(
        self,
        model,
        contexts: Dict[str, ifcopenshell.entity_instance],
        primitives: Dict[str, NeutralPrimitive],
        products: Dict[str, ifcopenshell.entity_instance],
        references: Dict[str, NeutralPrimitive],
        storey,
    ) -> None:
        for host_id, primitive in primitives.items():
            if not primitive.voids:
                continue
            host_product = products.get(host_id)
            if host_product is None:
                continue
            for void_id in primitive.voids:
                void_prim = primitives.get(void_id)
                if void_prim is None:
                    continue
                void_template = (
                    getattr(void_prim, "template_id", None)
                    or (void_prim.metadata.get("template_id") if void_prim.metadata else None)
                    or void_id
                )
                mapped_transform = self._opening_transform(primitive, void_template, references)
                predefined = void_prim.ifc.get("predefined_type") if void_prim.ifc else None
                opening = ifcopenshell.api.run(
                    "root.create_entity",
                    model,
                    ifc_class="IfcOpeningElement",
                    name=f"Opening:{void_id}",
                )
                self._set_guid(opening, f"opening::{host_id}::{void_id}")
                placement_transform = mapped_transform or void_prim.transform
                placement = self._placement_from_transform(model, placement_transform, storey.ObjectPlacement)
                opening.ObjectPlacement = placement
                if predefined and hasattr(opening, "PredefinedType"):
                    try:
                        opening.PredefinedType = predefined
                    except Exception:
                        pass
                rep = self._body_representation(model, contexts["body"], void_prim)
                if rep:
                    ifcopenshell.api.run("geometry.assign_representation", model, product=opening, representation=rep)
                self._assign_spatial(model, opening, storey)
                self._assign_property_sets(model, opening, void_prim, None)
                rel = model.createIfcRelVoidsElement(
                    self._guid(f"relvoid::{host_id}::{void_id}"),
                    RelatingBuildingElement=host_product,
                    RelatedOpeningElement=opening,
                )
                rel.Description = f"void {void_id}"
                try:
                    opening.Tag = void_prim.guid
                except Exception:
                    pass

    def _opening_transform(
        self,
        host: NeutralPrimitive,
        void_template: str,
        references: Dict[str, NeutralPrimitive],
    ) -> Optional[ComponentTransform]:
        host_template = (
            getattr(host, "template_id", None)
            or (host.metadata.get("template_id") if host.metadata else None)
            or host.id
        )
        base_host = references.get(host_template)
        base_void = references.get(void_template)
        if base_host is None or base_void is None:
            return None
        try:
            host_matrix = self._transform_matrix(base_host.transform)
            void_matrix = self._transform_matrix(base_void.transform)
            relative = np.linalg.inv(host_matrix) @ void_matrix
            target_matrix = self._transform_matrix(host.transform) @ relative
            return self._transform_from_matrix(target_matrix)
        except Exception:
            return None

    def _apply_connections(
        self,
        model,
        primitives: Dict[str, NeutralPrimitive],
        products: Dict[str, ifcopenshell.entity_instance],
    ) -> None:
        for prim_id, primitive in primitives.items():
            product = products.get(prim_id)
            if product is None:
                continue
            for hint in primitive.connections:
                target_product = products.get(hint.target)
                target_primitive = primitives.get(hint.target)
                if target_product is None or target_product == product:
                    continue
                key = tuple(sorted([prim_id, hint.target]) + [hint.subject_pos, hint.object_pos])
                if key in self._seen_connections:
                    continue
                self._seen_connections.add(key)
                geometry = self._connection_geometry(model, primitive, hint.subject_pos, target_primitive, hint.object_pos)
                rel = model.createIfcRelConnectsElements(
                    self._guid(f"connect::{prim_id}::{hint.target}::{hint.subject_pos}::{hint.object_pos}"),
                    RelatingElement=product,
                    RelatedElement=target_product,
                    ConnectionGeometry=geometry,
                )
                rel.Description = f"{hint.subject_pos}->{hint.object_pos}"

    def _connection_geometry(
        self,
        model,
        subject: NeutralPrimitive,
        subject_pos: str,
        target: Optional[NeutralPrimitive],
        object_pos: str,
    ):
        subject_axes = self._axes_from_pos(subject_pos)
        target_axes = self._axes_from_pos(object_pos)
        count = len(subject_axes)
        if count == 1:
            subj_plane = self._plane_from_face(model, subject, subject_axes[0])
            obj_plane = self._plane_from_face(model, target, target_axes[0]) if target and target_axes else None
            return model.createIfcConnectionSurfaceGeometry(subj_plane, obj_plane)
        if count == 2:
            subj_curve = self._curve_from_edges(model, subject, subject_axes)
            obj_curve = self._curve_from_edges(model, target, target_axes) if target and target_axes else None
            return model.createIfcConnectionCurveGeometry(subj_curve, obj_curve)
        point = self._point_from_axes(model, subject, subject_axes)
        obj_point = self._point_from_axes(model, target, target_axes) if target and target_axes else None
        return model.createIfcConnectionPointGeometry(point, obj_point)

    # ------------------------------------------------------------------ #
    def _transform_matrix(self, transform: ComponentTransform) -> np.ndarray:
        orientation = getattr(transform, "orientation", None)
        if orientation is None:
            angle = math.radians(transform.rotation[2] if transform.rotation else 0.0)
            orientation = (
                (math.cos(angle), math.sin(angle), 0.0),
                (-math.sin(angle), math.cos(angle), 0.0),
                (0.0, 0.0, 1.0),
            )
        matrix = np.eye(4, dtype=float)
        matrix[0:3, 0] = np.array(orientation[0])
        matrix[0:3, 1] = np.array(orientation[1])
        matrix[0:3, 2] = np.array(orientation[2])
        matrix[0:3, 3] = np.array(transform.position)
        return matrix

    def _transform_from_matrix(self, matrix: np.ndarray) -> ComponentTransform:
        position = (
            float(matrix[0, 3]),
            float(matrix[1, 3]),
            float(matrix[2, 3]),
        )
        orientation = (
            (float(matrix[0, 0]), float(matrix[1, 0]), float(matrix[2, 0])),
            (float(matrix[0, 1]), float(matrix[1, 1]), float(matrix[2, 1])),
            (float(matrix[0, 2]), float(matrix[1, 2]), float(matrix[2, 2])),
        )
        return ComponentTransform(position=position, rotation=(0.0, 0.0, 0.0), orientation=orientation)

    def _placement_from_transform(self, model, transform, parent_placement):
        tx, ty, tz = transform.position
        orientation = getattr(transform, "orientation", None)
        if orientation is None:
            angle = math.radians(transform.rotation[2] if transform.rotation else 0.0)
            x_dir = (math.cos(angle), math.sin(angle), 0.0)
            z_dir = (0.0, 0.0, 1.0)
        else:
            x_dir = orientation[0]
            z_dir = orientation[2]
        location = model.createIfcCartesianPoint((tx, ty, tz))
        axis2placement = model.createIfcAxis2Placement3D(
            location, model.createIfcDirection(z_dir), model.createIfcDirection(x_dir)
        )
        return model.createIfcLocalPlacement(RelativePlacement=axis2placement, PlacementRelTo=parent_placement)

    def _ensure_placement(self, model, element, parent):
        if element.ObjectPlacement is None:
            transform = type(
                "_PlacementTransform",
                (),
                {
                    "position": (0.0, 0.0, 0.0),
                    "rotation": (0.0, 0.0, 0.0),
                    "orientation": ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
                },
            )
            element.ObjectPlacement = self._placement_from_transform(model, transform, parent)

    def _plane_from_face(self, model, primitive: Optional[NeutralPrimitive], axis: Tuple[str, int]):
        if primitive is None:
            return None
        normal = self._face_normal(primitive, axis)
        point = self._face_point(primitive, axis)
        ref_dir = self._orthogonal_direction(normal)
        placement = model.createIfcAxis2Placement3D(
            model.createIfcCartesianPoint(point),
            model.createIfcDirection(normal),
            model.createIfcDirection(ref_dir),
        )
        return model.createIfcPlane(placement)

    def _curve_from_edges(self, model, primitive: Optional[NeutralPrimitive], axes: List[Tuple[str, int]]):
        if primitive is None:
            return None
        coords = self._edge_points(primitive, axes)
        return model.createIfcPolyline([model.createIfcCartesianPoint(pt) for pt in coords])

    def _point_from_axes(self, model, primitive: Optional[NeutralPrimitive], axes: List[Tuple[str, int]]):
        if primitive is None:
            return None
        coords = self._coordinate_from_axes(primitive, axes)
        return model.createIfcCartesianPoint(coords)

    # ------------------------------------------------------------------ #
    def _face_point(self, primitive: NeutralPrimitive, axis: Tuple[str, int]):
        ax, sign = axis
        orientation = self._orientation_axes(primitive)
        idx = {"x": 0, "y": 1, "z": 2}[ax]
        half = primitive.size[idx] / 2
        axis_vec = orientation[idx]
        offset = (axis_vec[0] * half * sign, axis_vec[1] * half * sign, axis_vec[2] * half * sign)
        tx, ty, tz = primitive.transform.position
        return (tx + offset[0], ty + offset[1], tz + offset[2])

    def _edge_points(self, primitive: NeutralPrimitive, axes: List[Tuple[str, int]]):
        remaining_axis = {"x", "y", "z"} - {axis for axis, _ in axes}
        if not remaining_axis:
            remaining_axis = {"x"}
        rem_axis = next(iter(remaining_axis))
        coords = []
        for value in (-0.5, 0.5):
            coord_axes = list(axes)
            coord_axes.append((rem_axis, 1 if value > 0 else -1))
            coords.append(self._coordinate_from_axes(primitive, coord_axes, span=True))
        return coords

    def _coordinate_from_axes(
        self, primitive: NeutralPrimitive, axes: List[Tuple[str, int]], span: bool = False
    ) -> Tuple[float, float, float]:
        orientation = self._orientation_axes(primitive)
        offsets = [0.0, 0.0, 0.0]
        for axis, sign in axes:
            idx = {"x": 0, "y": 1, "z": 2}[axis]
            half = primitive.size[idx] / 2
            axis_vec = orientation[idx]
            offsets[0] += axis_vec[0] * half * sign
            offsets[1] += axis_vec[1] * half * sign
            offsets[2] += axis_vec[2] * half * sign
        tx, ty, tz = primitive.transform.position
        return (tx + offsets[0], ty + offsets[1], tz + offsets[2])

    def _face_normal(self, primitive: NeutralPrimitive, axis: Tuple[str, int]) -> Tuple[float, float, float]:
        ax, sign = axis
        idx = {"x": 0, "y": 1, "z": 2}[ax]
        orientation = self._orientation_axes(primitive)
        axis_vec = orientation[idx]
        return (axis_vec[0] * sign, axis_vec[1] * sign, axis_vec[2] * sign)

    def _orthogonal_direction(self, normal: Tuple[float, float, float]) -> Tuple[float, float, float]:
        ref = (0.0, 0.0, 1.0)
        if abs(normal[0]) < 1e-6 and abs(normal[1]) < 1e-6:
            ref = (1.0, 0.0, 0.0)
        cross_x = normal[1] * ref[2] - normal[2] * ref[1]
        cross_y = normal[2] * ref[0] - normal[0] * ref[2]
        cross_z = normal[0] * ref[1] - normal[1] * ref[0]
        length = math.sqrt(cross_x ** 2 + cross_y ** 2 + cross_z ** 2)
        if length < 1e-9:
            return (1.0, 0.0, 0.0)
        return (cross_x / length, cross_y / length, cross_z / length)

    # ------------------------------------------------------------------ #
    def _axes_from_pos(self, pos_token: str) -> List[Tuple[str, int]]:
        axes: List[Tuple[str, int]] = []
        token = pos_token.strip()
        if len(token) % 2 != 0:
            return axes
        for i in range(0, len(token), 2):
            sign_char = token[i]
            axis = token[i + 1]
            sign = 1 if sign_char == "+" else -1
            axes.append((axis, sign))
        return axes

    def _orientation_axes(self, primitive: NeutralPrimitive) -> Tuple[Tuple[float, float, float], ...]:
        orientation = getattr(primitive.transform, "orientation", None)
        if orientation is None:
            angle = math.radians(primitive.transform.rotation[2]) if primitive.transform.rotation else 0.0
            return (
                (math.cos(angle), math.sin(angle), 0.0),
                (-math.sin(angle), math.cos(angle), 0.0),
                (0.0, 0.0, 1.0),
            )
        return orientation

    def _axis_direction(self, rotation_deg: float, *, orientation: Optional[Tuple[Tuple[float, float, float], ...]] = None) -> Tuple[float, float, float]:
        if orientation is not None:
            return orientation[0]
        angle = math.radians(rotation_deg)
        return (math.cos(angle), math.sin(angle), 0.0)

    def _type_key(self, primitive: NeutralPrimitive) -> str:
        predefined = ""
        if primitive.ifc and isinstance(primitive.ifc, dict):
            predefined = primitive.ifc.get("predefined_type") or ""
        params = tuple(sorted((primitive.profile_params or {}).items()))
        return "::".join(
            [
                primitive.template_id,
                primitive.class_name or "Proxy",
                primitive.profile,
                predefined,
                ",".join(str(round(dim, 4)) for dim in primitive.size),
                primitive.material or "",
                str(params),
            ]
        )

    def _type_class_for(self, class_name: Optional[str]) -> Optional[str]:
        if not class_name:
            return None
        mapping = {
            "ifcbeam": "IfcBeamType",
            "ifcmember": "IfcMemberType",
            "ifcslab": "IfcSlabType",
            "ifcfooting": "IfcFootingType",
            "ifcfastener": "IfcFastenerType",
        }
        return mapping.get(class_name.lower())

    def _set_guid(self, entity, seed: str) -> None:
        entity.GlobalId = self._guid(seed)

    def _guid(self, seed: str) -> str:
        return ifcopenshell.guid.compress(str(uuid.uuid5(uuid.UUID("6c7b3d9e-4f21-4b06-9fbf-2a6e2d6a8b2c"), seed)))

    @staticmethod
    def _create_ifc_file(version: str = "IFC4X3_ADD2") -> ifcopenshell.file:
        file = ifcopenshell.file(schema=version)
        now = datetime.datetime.now(datetime.UTC).astimezone().replace(microsecond=0)
        file.header.file_name.name = "/dev/null"
        file.header.file_name.time_stamp = now.isoformat()
        file.header.file_name.preprocessor_version = f"IfcOpenShell {ifcopenshell.version}"
        file.header.file_name.originating_system = "pond-diagramming"
        file.header.file_name.authorization = "Nobody"
        file.header.file_description.description = ("ViewDefinition[ReferenceView]",)
        return file

    def _auto_pset(self, primitive: NeutralPrimitive) -> Tuple[Optional[str], Dict[str, object]]:
        class_lower = (primitive.class_name or "").lower()
        mapping = {
            "ifcbeam": "Pset_BeamCommon",
            "ifcmember": "Pset_MemberCommon",
            "ifcslab": "Pset_SlabCommon",
            "ifcfooting": "Pset_FootingCommon",
            "ifcfastener": "Pset_FastenerCommon",
        }
        pset_name = mapping.get(class_lower, "Pset_ElementCommon")
        metadata = primitive.metadata or {}
        props: Dict[str, object] = {}
        reference = metadata.get("component_id") or primitive.id
        if reference:
            props["Reference"] = reference
        label = metadata.get("label") or metadata.get("id") or primitive.id
        if label:
            props["Name"] = label
        description = metadata.get("description")
        if description:
            props["Description"] = description
        elevation = metadata.get("elevation")
        if elevation is not None:
            props["Elevation"] = elevation
        material = primitive.material
        if material:
            props["Material"] = material
        return pset_name, props

    def _tessellate(self, primitive: NeutralPrimitive) -> tuple[list[list[float]], list[Sequence[int]]]:
        if primitive.solid is not None:
            try:
                vectors, faces = primitive.solid.tessellate(0.5)
                vertex_rows = [[vec.x, vec.y, vec.z] for vec in vectors]
                return vertex_rows, list(faces)
            except Exception:
                return [], []

        hx, hy, hz = (primitive.size[0] / 2, primitive.size[1] / 2, primitive.size[2] / 2)
        corners = [
            (-hx, -hy, -hz),
            (hx, -hy, -hz),
            (hx, hy, -hz),
            (-hx, hy, -hz),
            (-hx, -hy, hz),
            (hx, -hy, hz),
            (hx, hy, hz),
            (-hx, hy, hz),
        ]
        orientation = self._orientation_axes(primitive)
        tx, ty, tz = primitive.transform.position
        rotated = []
        for corner in corners:
            offset_x = corner[0] * orientation[0][0] + corner[1] * orientation[1][0] + corner[2] * orientation[2][0]
            offset_y = corner[0] * orientation[0][1] + corner[1] * orientation[1][1] + corner[2] * orientation[2][1]
            offset_z = corner[0] * orientation[0][2] + corner[1] * orientation[1][2] + corner[2] * orientation[2][2]
            rotated.append((tx + offset_x, ty + offset_y, tz + offset_z))
        faces = [
            (0, 1, 2),
            (0, 2, 3),
            (4, 5, 6),
            (4, 6, 7),
            (0, 1, 5),
            (0, 5, 4),
            (1, 2, 6),
            (1, 6, 5),
            (2, 3, 7),
            (2, 7, 6),
            (3, 0, 4),
            (3, 4, 7),
        ]
        return rotated, faces


__all__ = ["IfcExporter", "IfcExportOptions"]
