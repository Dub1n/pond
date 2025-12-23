from __future__ import annotations

IFC_REQUIREMENTS = {
    "ifcbeam": {"predefined": True, "material": True, "allowed_predefined": {"BEAM", "JOIST", "EDGEBEAM"}},
    "ifcmember": {"predefined": True, "material": True},
    "ifcslab": {"predefined": True, "material": True, "allowed_predefined": {"FLOOR"}},
    "ifcopeningelement": {"predefined": True, "material": False, "allowed_predefined": {"OPENING"}},
    "ifcfooting": {"predefined": True, "material": True},
}

__all__ = ["IFC_REQUIREMENTS"]
