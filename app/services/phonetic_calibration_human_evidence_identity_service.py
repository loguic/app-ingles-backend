import hashlib
import json

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
    PhoneticCalibrationHumanEvidenceIdentity,
)


def build_phonetic_calibration_human_evidence_identity(
    agreements: list[PhoneticCalibrationHumanAgreement],
    rubric_version: str,
) -> PhoneticCalibrationHumanEvidenceIdentity:
    """Build a reproducible identity for human calibration evidence.

    Construye una identidad reproducible para la evidencia humana de calibración.
    """
    matching = [
        agreement
        for agreement in agreements
        if agreement.rubric_version == rubric_version
    ]
    if not matching:
        raise ValueError("Human evidence identity requires matching agreements")

    canonical_agreements = sorted(
        (
            agreement.model_dump(mode="json")
            for agreement in matching
        ),
        key=lambda item: item["sample_id"],
    )
    sample_ids = {agreement.sample_id for agreement in matching}

    canonical_payload = {
        "rubric_version": rubric_version,
        "agreements": canonical_agreements,
    }
    canonical_json = json.dumps(
        canonical_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    evidence_sha256 = hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

    return PhoneticCalibrationHumanEvidenceIdentity(
        rubric_version=rubric_version,
        sample_count=len(sample_ids),
        evidence_sha256=evidence_sha256,
    )
