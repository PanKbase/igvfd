"""Pure calculated-property helpers for HumanDonor (shared logic with MCP normalize)."""

from __future__ import annotations

from typing import Any

_AAB_FIELDS = ("aab_gada", "aab_iaa", "aab_ia2", "aab_znt8")
_AAB_LABELS = {
    "aab_gada": "GADA+",
    "aab_iaa": "IAA+",
    "aab_ia2": "IA2+",
    "aab_znt8": "ZNT8+",
}

_DATASET_CANONICAL = {
    "snatacseq": "snATACseq",
    "snatac-seq": "snATACseq",
    "histology": "Histology",
}


def _norm_token(value: str) -> str:
    return "".join(ch for ch in value.strip().lower().replace("_", "").replace("-", "").replace(" ", ""))


def normalize_dataset(name: str) -> str:
    token = _norm_token(name)
    if token in _DATASET_CANONICAL:
        return _DATASET_CANONICAL[token]
    # Preserve known casing for common names; otherwise return stripped original.
    known = {
        "genotyping": "Genotyping",
        "function": "Function",
        "imaging": "Imaging",
        "morphology": "Morphology",
        "hlatyping": "HLA_typing",
        "bcrseq": "BCRseq",
        "citeseq": "CITEseq",
        "flowcytometry": "Flow_cytometry",
        "scmultiome": "scMultiome",
        "tcrseq": "TCRseq",
        "scrnaseq": "scRNAseq",
        "rnaseq": "RNAseq",
        "snatacseq": "snATACseq",
        "atacseq": "ATAC-seq",
        "cytof": "CyTof",
        "massspec": "mass_spec",
        "imagingmassspec": "imaging_mass_spec",
        "codex": "CODEX",
        "wgbs": "WGBS",
    }
    return known.get(token, name)


def normalize_dataset_tissue(tissue: str) -> str:
    if tissue is None or str(tissue).strip() in {"", "-"}:
        return "unspecified"
    token = _norm_token(str(tissue))
    known = {
        "pancreas": "Pancreas",
        "islet": "Islet",
        "spleen": "Spleen",
        "lymph": "Lymph",
        "peripheralblood": "Peripheral_blood",
        "thymus": "Thymus",
        "unspecified": "unspecified",
    }
    return known.get(token, str(tissue))


def data_available_key(dataset: str, tissue: str) -> str:
    return f"{normalize_dataset(dataset)}|{normalize_dataset_tissue(tissue)}"


def data_available_keys(entries: list[dict[str, Any]] | None) -> list[str]:
    """Normalized dataset|tissue keys; scMultiome also expands to snATACseq/scRNAseq."""
    if not entries:
        return []
    keys: list[str] = []
    seen: set[str] = set()

    def _add(key: str) -> None:
        if key not in seen:
            seen.add(key)
            keys.append(key)

    for entry in entries:
        dataset = entry.get("dataset")
        tissue = entry.get("dataset_tissue")
        if not dataset or tissue is None:
            continue
        canon_ds = normalize_dataset(str(dataset))
        canon_tissue = normalize_dataset_tissue(str(tissue))
        _add(f"{canon_ds}|{canon_tissue}")
        if canon_ds == "scMultiome":
            _add(f"snATACseq|{canon_tissue}")
            _add(f"scRNAseq|{canon_tissue}")
    return keys


def data_available_datasets(entries: list[dict[str, Any]] | None) -> list[str]:
    if not entries:
        return []
    out: list[str] = []
    seen: set[str] = set()

    def _add(name: str) -> None:
        if name not in seen:
            seen.add(name)
            out.append(name)

    for entry in entries:
        dataset = entry.get("dataset")
        if not dataset:
            continue
        canon = normalize_dataset(str(dataset))
        _add(canon)
        if canon == "scMultiome":
            _add("snATACseq")
            _add("scRNAseq")
    return out


def data_available_tissues(entries: list[dict[str, Any]] | None) -> list[str]:
    if not entries:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        tissue = entry.get("dataset_tissue")
        if tissue is None:
            continue
        canon = normalize_dataset_tissue(str(tissue))
        if canon not in seen:
            seen.add(canon)
            out.append(canon)
    return out


def aab_fields_present(donor: dict[str, Any]) -> bool:
    return any(field in donor for field in _AAB_FIELDS)


def compute_aab_count(donor: dict[str, Any]) -> int | None:
    if not aab_fields_present(donor):
        return None
    return sum(1 for field in _AAB_FIELDS if donor.get(field) is True)


def compute_aab_tested(donor: dict[str, Any]) -> bool | None:
    if not aab_fields_present(donor):
        return None
    return True


def compute_aab_positive(donor: dict[str, Any]) -> bool | None:
    count = compute_aab_count(donor)
    if count is None:
        return None
    return count > 0


def compute_aab_summary(donor: dict[str, Any]) -> str | None:
    if not aab_fields_present(donor):
        return None
    positives = [_AAB_LABELS[field] for field in _AAB_FIELDS if donor.get(field) is True]
    if not positives:
        return "none positive"
    return ", ".join(positives)


def compute_age_group(age: float | int | None) -> str | None:
    if age is None:
        return None
    try:
        value = float(age)
    except (TypeError, ValueError):
        return None
    if value < 13:
        return "0-12"
    if value < 18:
        return "13-17"
    if value < 40:
        return "18-39"
    if value < 65:
        return "40-64"
    return "65+"


def compute_pediatric(age: float | int | None) -> bool | None:
    if age is None:
        return None
    try:
        return float(age) < 18
    except (TypeError, ValueError):
        return None


def compute_sex_discordant(gender: str | None, genetic_sex: str | None) -> bool | None:
    if gender is None or genetic_sex is None:
        return None
    if gender == "-" or genetic_sex == "-":
        return None
    return gender != genetic_sex


def compute_label_hba1c_discordant(
    diabetes_status_description: str | None,
    derived_diabetes_status: str | None,
) -> bool | None:
    if not diabetes_status_description or not derived_diabetes_status:
        return None
    label = diabetes_status_description.strip().lower()
    derived = derived_diabetes_status.strip().lower()
    if label == "control without diabetes" and derived == "diabetes":
        return True
    diabetes_labels = {
        "type 1 diabetes",
        "type 2 diabetes",
        "diabetes unspecified",
        "monogenic diabetes",
        "gestational diabetes",
        "cystic fibrosis-related diabetes",
    }
    if label in diabetes_labels and derived == "normal":
        return True
    return False


def compute_dominant_genetic_ancestry(
    genetic_ethnicities: list[dict[str, Any]] | None,
) -> str | None:
    if not genetic_ethnicities:
        return None
    best_name = None
    best_pct = None
    for entry in genetic_ethnicities:
        if not isinstance(entry, dict):
            continue
        name = entry.get("ethnicity")
        if not name:
            continue
        pct = entry.get("percentage")
        if pct is None:
            if best_name is None and len(genetic_ethnicities) == 1:
                return str(name)
            if best_pct is None and best_name is None:
                best_name = str(name)
            continue
        try:
            pct_f = float(pct)
        except (TypeError, ValueError):
            continue
        if best_pct is None or pct_f > best_pct:
            best_pct = pct_f
            best_name = str(name)
    return best_name


def _grs_entry(genetic_risk_score: list[dict[str, Any]] | None, method: str) -> dict[str, Any] | None:
    if not genetic_risk_score:
        return None
    for entry in genetic_risk_score:
        if isinstance(entry, dict) and entry.get("method") == method:
            return entry
    return None


def compute_grs2_score(genetic_risk_score: list[dict[str, Any]] | None) -> float | None:
    entry = _grs_entry(genetic_risk_score, "GRS2")
    if not entry or entry.get("overall_score") is None:
        return None
    return float(entry["overall_score"])


def compute_grs2_normalized(genetic_risk_score: list[dict[str, Any]] | None) -> float | None:
    entry = _grs_entry(genetic_risk_score, "GRS2")
    if not entry or entry.get("normalized_score") is None:
        return None
    return float(entry["normalized_score"])


def compute_t2d_grs_score(genetic_risk_score: list[dict[str, Any]] | None) -> float | None:
    entry = _grs_entry(genetic_risk_score, "T2D_GRS_Mahajan")
    if not entry or entry.get("overall_score") is None:
        return None
    return float(entry["overall_score"])


def compute_t2d_grs_normalized(genetic_risk_score: list[dict[str, Any]] | None) -> float | None:
    entry = _grs_entry(genetic_risk_score, "T2D_GRS_Mahajan")
    if not entry or entry.get("normalized_score") is None:
        return None
    return float(entry["normalized_score"])


def _present(donor: dict[str, Any], field: str) -> bool:
    if field not in donor:
        return False
    value = donor[field]
    if value is None:
        return False
    if isinstance(value, (list, dict, str)) and len(value) == 0:
        return False
    return True


def compute_tier1_complete(donor: dict[str, Any]) -> bool:
    """True when all Tier 0 + Tier 1 schema fields are present."""
    tier0 = ("age", "center_donor_id", "lab", "living_donor", "taxa")
    tier1 = ("gender", "bmi", "diabetes_status", "diabetes_status_description")
    return all(_present(donor, field) for field in tier0 + tier1)


def donor_calc_bundle(properties: dict[str, Any]) -> dict[str, Any]:
    """Compute all HumanDonor calculated fields from a properties dict (for parity tests)."""
    entries = properties.get("data_available")
    out: dict[str, Any] = {
        "data_available_keys": data_available_keys(entries),
        "data_available_datasets": data_available_datasets(entries),
        "data_available_tissues": data_available_tissues(entries),
        "age_group": compute_age_group(properties.get("age")),
        "pediatric": compute_pediatric(properties.get("age")),
        "sex_discordant": compute_sex_discordant(
            properties.get("gender"), properties.get("genetic_sex")
        ),
        "label_hba1c_discordant": compute_label_hba1c_discordant(
            properties.get("diabetes_status_description"),
            properties.get("derived_diabetes_status"),
        ),
        "dominant_genetic_ancestry": compute_dominant_genetic_ancestry(
            properties.get("genetic_ethnicities")
        ),
        "grs2_score": compute_grs2_score(properties.get("genetic_risk_score")),
        "grs2_normalized": compute_grs2_normalized(properties.get("genetic_risk_score")),
        "t2d_grs_score": compute_t2d_grs_score(properties.get("genetic_risk_score")),
        "t2d_grs_normalized": compute_t2d_grs_normalized(properties.get("genetic_risk_score")),
        "tier1_complete": compute_tier1_complete(properties),
        "aab_count": compute_aab_count(properties),
        "aab_tested": compute_aab_tested(properties),
        "aab_positive": compute_aab_positive(properties),
        "aab_summary": compute_aab_summary(properties),
    }
    return {k: v for k, v in out.items() if v is not None}
