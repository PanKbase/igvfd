"""Pure calculated-property helpers for PrimaryIslet."""

from __future__ import annotations

from typing import Any


def parse_purity_value(purity: list[str] | None) -> float | None:
    """Max numeric value parsed from purity[] strings."""
    if not purity:
        return None
    values: list[float] = []
    for item in purity:
        try:
            values.append(float(str(item).strip()))
        except (TypeError, ValueError):
            continue
    if not values:
        return None
    return max(values)


def coalesce_post_shipment_viability(
    post_shipment_viability_quantitative: float | None = None,
    post_shipment_islet_viability: float | None = None,
) -> float | None:
    if post_shipment_viability_quantitative is not None:
        return float(post_shipment_viability_quantitative)
    if post_shipment_islet_viability is not None:
        return float(post_shipment_islet_viability)
    return None


def islet_calc_bundle(properties: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        'purity_value': parse_purity_value(properties.get('purity')),
        'post_shipment_viability': coalesce_post_shipment_viability(
            properties.get('post_shipment_viability_quantitative'),
            properties.get('post_shipment_islet_viability'),
        ),
    }
    return {k: v for k, v in out.items() if v is not None}
