"""
GRC validation engine for the Information Asset Register.

This module provides:
- CIA score calculation
- Asset criticality determination
- Asset governance validation
"""

from typing import Any


# ---------------------------------------------------------
# Criticality
# ---------------------------------------------------------

def determine_criticality(score: int) -> str:
    """
    Determine asset criticality based on the CIA score.

    CIA score range:
        3-6   -> Low
        7-10  -> Medium
        11-13 -> High
        14-15 -> Critical
    """

    if score >= 14:
        return "Critical"

    if score >= 11:
        return "High"

    if score >= 7:
        return "Medium"

    return "Low"


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def _is_empty(value: Any) -> bool:
    """Return True when a value is empty or missing."""

    if value is None:
        return True

    value = str(value).strip()

    return value == "" or value.lower() in {
        "nan",
        "none",
        "null",
    }


def _normalise(value: Any) -> str:
    """Convert a value to a normalised lowercase string."""

    if _is_empty(value):
        return ""

    return str(value).strip().lower()


def _parse_cia(value: Any) -> int | None:
    """Convert CIA rating to an integer."""

    try:
        number = int(value)

        if 1 <= number <= 5:
            return number

    except (TypeError, ValueError):
        pass

    return None


# ---------------------------------------------------------
# Asset validation
# ---------------------------------------------------------

def validate_asset(asset: dict) -> list[str]:
    """
    Validate a single information asset.

    Returns a list of governance findings.
    """

    findings = []

    asset_id = asset.get("asset_id")
    asset_name = asset.get("asset_name")
    owner = asset.get("owner")
    custodian = asset.get("custodian")
    status = asset.get("status")
    classification = asset.get(
        "information_classification"
    )

    confidentiality = _parse_cia(
        asset.get("confidentiality")
    )

    integrity = _parse_cia(
        asset.get("integrity")
    )

    availability = _parse_cia(
        asset.get("availability")
    )

    personal_data = _normalise(
        asset.get("personal_data")
    )

    backup_required = _normalise(
        asset.get("backup_required")
    )

    review_date = asset.get("review_date")

    # -----------------------------------------------------
    # Mandatory fields
    # -----------------------------------------------------

    if _is_empty(asset_id):
        findings.append(
            "[CRITICAL] Missing Asset ID"
        )

    if _is_empty(asset_name):
        findings.append(
            "[CRITICAL] Missing Asset Name"
        )

    if _is_empty(owner):
        findings.append(
            "[HIGH] Missing Asset Owner"
        )

    if _is_empty(custodian):
        findings.append(
            "[HIGH] Missing Asset Custodian"
        )

    if _is_empty(status):
        findings.append(
            "[MEDIUM] Missing Asset Status"
        )

    if _is_empty(classification):
        findings.append(
            "[HIGH] Missing Information Classification"
        )

    if _is_empty(review_date):
        findings.append(
            "[MEDIUM] Missing Review Date"
        )

    # -----------------------------------------------------
    # CIA validation
    # -----------------------------------------------------

    if confidentiality is None:
        findings.append(
            "[HIGH] Invalid Confidentiality rating "
            "(expected 1-5)"
        )

    if integrity is None:
        findings.append(
            "[HIGH] Invalid Integrity rating "
            "(expected 1-5)"
        )

    if availability is None:
        findings.append(
            "[HIGH] Invalid Availability rating "
            "(expected 1-5)"
        )

    # -----------------------------------------------------
    # Criticality checks
    # -----------------------------------------------------

    if (
        confidentiality is not None
        and integrity is not None
        and availability is not None
    ):

        cia_score = (
            confidentiality
            + integrity
            + availability
        )

        criticality = determine_criticality(
            cia_score
        )

        # Critical assets should have backup
        if criticality == "Critical":

            if backup_required not in {
                "yes",
                "true",
                "1",
            }:

                findings.append(
                    "[CRITICAL] Critical Asset Without Backup"
                )

            findings.append(
                "[HIGH] Enhanced Risk Review Required"
            )

    # -----------------------------------------------------
    # Privacy governance
    # -----------------------------------------------------

    if personal_data in {
        "yes",
        "true",
        "1",
    }:

        findings.append(
            "[MEDIUM] Privacy Review Required - "
            "Asset contains Personal Data"
        )

    return findings