"""
Validation engine for the GRC Information Asset Register.

The module provides:
- CIA score calculation
- Asset criticality determination
- Mandatory field validation
- CIA validation
- Governance checks
- Privacy checks
- Risk governance checks
- Data quality checks
"""

from typing import Any


# ============================================================
# Configuration
# ============================================================

ALLOWED_STATUSES = {
    "active",
    "inactive",
    "under review",
    "retired",
}

ALLOWED_CLASSIFICATIONS = {
    "public",
    "internal",
    "confidential",
    "restricted",
}

ALLOWED_BOOLEAN_VALUES = {
    "yes",
    "no",
    "true",
    "false",
    "1",
    "0",
}


# ============================================================
# Criticality
# ============================================================

def determine_criticality(score: int) -> str:
    """
    Determine asset criticality from the total CIA score.

    Score:
        3-6   = Low
        7-10  = Medium
        11-13 = High
        14-15 = Critical
    """

    if score >= 14:
        return "Critical"

    if score >= 11:
        return "High"

    if score >= 7:
        return "Medium"

    return "Low"


def calculate_cia_score(
    confidentiality: Any,
    integrity: Any,
    availability: Any,
) -> int | None:
    """
    Calculate the total CIA score.

    Returns None when one or more values are invalid.
    """

    values = [
        _parse_cia(confidentiality),
        _parse_cia(integrity),
        _parse_cia(availability),
    ]

    if any(value is None for value in values):
        return None

    return sum(values)


# ============================================================
# Helper functions
# ============================================================

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
    """Return a normalised lowercase string."""

    if _is_empty(value):
        return ""

    return str(value).strip().lower()


def _parse_cia(value: Any) -> int | None:
    """Validate and convert a CIA rating to an integer."""

    try:
        number = int(value)

        if 1 <= number <= 5:
            return number

    except (TypeError, ValueError):
        pass

    return None


# ============================================================
# Structured finding
# ============================================================

def _finding(
    asset_id: Any,
    severity: str,
    category: str,
    code: str,
    message: str,
    recommendation: str,
) -> dict:

    return {
        "Asset ID": str(asset_id) if not _is_empty(asset_id) else "UNKNOWN",
        "Severity": severity,
        "Category": category,
        "Code": code,
        "Finding": message,
        "Recommendation": recommendation,
    }


# ============================================================
# Detailed asset validation
# ============================================================

def validate_asset_findings(asset: dict) -> list[dict]:
    """
    Perform detailed GRC validation on a single asset.

    Returns structured findings suitable for reporting.
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

    personal_data = _normalise(
        asset.get("personal_data")
    )

    backup_required = _normalise(
        asset.get("backup_required")
    )

    review_date = asset.get("review_date")

    confidentiality = _parse_cia(
        asset.get("confidentiality")
    )

    integrity = _parse_cia(
        asset.get("integrity")
    )

    availability = _parse_cia(
        asset.get("availability")
    )

    # --------------------------------------------------------
    # Mandatory fields
    # --------------------------------------------------------

    if _is_empty(asset_id):
        findings.append(
            _finding(
                asset_id,
                "Critical",
                "Data Quality",
                "DQ-001",
                "Missing Asset ID",
                "Assign a unique asset identifier.",
            )
        )

    if _is_empty(asset_name):
        findings.append(
            _finding(
                asset_id,
                "Critical",
                "Data Quality",
                "DQ-002",
                "Missing Asset Name",
                "Provide a descriptive asset name.",
            )
        )

    if _is_empty(owner):
        findings.append(
            _finding(
                asset_id,
                "High",
                "Data Quality",
                "DQ-003",
                "Missing Asset Owner",
                "Assign a business owner responsible for the asset.",
            )
        )

    if _is_empty(custodian):
        findings.append(
            _finding(
                asset_id,
                "High",
                "Data Quality",
                "DQ-004",
                "Missing Asset Custodian",
                "Assign a technical or operational custodian.",
            )
        )

    if _is_empty(status):
        findings.append(
            _finding(
                asset_id,
                "Medium",
                "Data Quality",
                "DQ-005",
                "Missing Asset Status",
                "Define the current lifecycle status.",
            )
        )

    if _is_empty(classification):
        findings.append(
            _finding(
                asset_id,
                "High",
                "Data Quality",
                "DQ-006",
                "Missing Information Classification",
                "Assign an approved information classification.",
            )
        )

    if _is_empty(review_date):
        findings.append(
            _finding(
                asset_id,
                "Medium",
                "Data Quality",
                "DQ-007",
                "Missing Review Date",
                "Define the next asset review date.",
            )
        )

    # --------------------------------------------------------
    # Classification validation
    # --------------------------------------------------------

    if not _is_empty(classification):

        if _normalise(classification) not in ALLOWED_CLASSIFICATIONS:
            findings.append(
                _finding(
                    asset_id,
                    "High",
                    "Data Quality",
                    "DQ-008",
                    "Invalid Information Classification",
                    "Use Public, Internal, Confidential or Restricted.",
                )
            )

    # --------------------------------------------------------
    # Status validation
    # --------------------------------------------------------

    if not _is_empty(status):

        if _normalise(status) not in ALLOWED_STATUSES:
            findings.append(
                _finding(
                    asset_id,
                    "Medium",
                    "Data Quality",
                    "DQ-009",
                    "Invalid Asset Status",
                    "Use an approved lifecycle status.",
                )
            )

    # --------------------------------------------------------
    # CIA validation
    # --------------------------------------------------------

    if confidentiality is None:
        findings.append(
            _finding(
                asset_id,
                "High",
                "Data Quality",
                "CIA-001",
                "Invalid Confidentiality Rating",
                "Set Confidentiality to a value from 1 to 5.",
            )
        )

    if integrity is None:
        findings.append(
            _finding(
                asset_id,
                "High",
                "Data Quality",
                "CIA-002",
                "Invalid Integrity Rating",
                "Set Integrity to a value from 1 to 5.",
            )
        )

    if availability is None:
        findings.append(
            _finding(
                asset_id,
                "High",
                "Data Quality",
                "CIA-003",
                "Invalid Availability Rating",
                "Set Availability to a value from 1 to 5.",
            )
        )

    # --------------------------------------------------------
    # CIA / Criticality governance
    # --------------------------------------------------------

    cia_score = calculate_cia_score(
        confidentiality,
        integrity,
        availability,
    )

    if cia_score is not None:

        criticality = determine_criticality(cia_score)

        # Critical assets require enhanced risk review
        if criticality == "Critical":

            findings.append(
                _finding(
                    asset_id,
                    "High",
                    "Risk Governance",
                    "RISK-001",
                    "Enhanced Risk Review Required",
                    "Review the asset in the organisational risk register.",
                )
            )

            if backup_required not in {
                "yes",
                "true",
                "1",
            }:

                findings.append(
                    _finding(
                        asset_id,
                        "Critical",
                        "Business Continuity",
                        "BC-001",
                        "Critical Asset Without Backup",
                        "Define and test an appropriate backup or recovery mechanism.",
                    )
                )

    # --------------------------------------------------------
    # Privacy governance
    # --------------------------------------------------------

    if personal_data in {
        "yes",
        "true",
        "1",
    }:

        findings.append(
            _finding(
                asset_id,
                "Medium",
                "Privacy",
                "PRIV-001",
                "Privacy Review Required",
                "Confirm GDPR processing requirements and data protection controls.",
            )
        )

    return findings


# ============================================================
# Backwards-compatible validation function
# ============================================================

def validate_asset(asset: dict) -> list[str]:
    """
    Backwards-compatible validation function.

    Returns findings as readable strings.
    """

    findings = validate_asset_findings(asset)

    return [
        f"[{item['Severity'].upper()}] {item['Finding']}"
        for item in findings
    ]