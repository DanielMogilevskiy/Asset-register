import csv
from pathlib import Path


REQUIRED_FIELDS = [
    "asset_id",
    "asset_name",
    "asset_type",
    "owner",
    "custodian",
    "status",
    "confidentiality",
    "integrity",
    "availability",
    "information_classification",
]


VALID_CLASSIFICATIONS = {
    "Public",
    "Internal",
    "Confidential",
    "Restricted",
}


VALID_STATUSES = {
    "Active",
    "Inactive",
    "Retired",
    "Under Review",
}


def calculate_cia_score(
    confidentiality: int,
    integrity: int,
    availability: int,
) -> int:
    """Calculate the total CIA score."""

    return (
        confidentiality
        + integrity
        + availability
    )


def determine_criticality(cia_score: int) -> str:
    """Determine asset criticality from CIA score."""

    if cia_score >= 14:
        return "Critical"

    if cia_score >= 11:
        return "High"

    if cia_score >= 7:
        return "Medium"

    return "Low"


def validate_asset(asset: dict) -> list[str]:
    """Validate one asset record."""

    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if not asset.get(field, "").strip():
            errors.append(
                f"Missing required field: {field}"
            )

    # Validate CIA values
    for field in [
        "confidentiality",
        "integrity",
        "availability",
    ]:
        try:
            value = int(asset[field])

            if not 1 <= value <= 5:
                errors.append(
                    f"{field} must be between 1 and 5"
                )

        except (ValueError, KeyError):
            errors.append(
                f"{field} must contain a number from 1 to 5"
            )

    # Validate classification
    if (
        asset.get("information_classification")
        not in VALID_CLASSIFICATIONS
    ):
        errors.append(
            "Invalid information classification"
        )

    # Validate status
    if asset.get("status") not in VALID_STATUSES:
        errors.append("Invalid asset status")

    return errors


def process_assets(input_file: Path):
    """Read, validate and enrich the asset register."""

    assets = []
    validation_errors = []

    with open(
        input_file,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for asset in reader:

            errors = validate_asset(asset)

            if errors:
                validation_errors.append(
                    {
                        "asset_id": asset.get(
                            "asset_id",
                            "UNKNOWN",
                        ),
                        "errors": errors,
                    }
                )

                continue

            confidentiality = int(
                asset["confidentiality"]
            )

            integrity = int(
                asset["integrity"]
            )

            availability = int(
                asset["availability"]
            )

            cia_score = calculate_cia_score(
                confidentiality,
                integrity,
                availability,
            )

            asset["cia_score"] = cia_score

            asset["criticality"] = (
                determine_criticality(cia_score)
            )

            assets.append(asset)

    return assets, validation_errors


def save_results(
    assets: list[dict],
    output_file: Path,
):
    """Save validated assets to a CSV file."""

    if not assets:
        return

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = list(assets[0].keys())

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(assets)