import csv
from pathlib import Path


# Find the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Define input and output files
INPUT_FILE = BASE_DIR / "data" / "asset_register.csv"
OUTPUT_FILE = BASE_DIR / "output" / "asset_register_validated.csv"


# Fields that every asset should have
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


# Allowed values
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


def calculate_cia_score(confidentiality, integrity, availability):
    """
    Calculate the total CIA score.
    """

    return confidentiality + integrity + availability


def determine_criticality(cia_score):
    """
    Convert CIA score into asset criticality.
    """

    if cia_score >= 14:
        return "Critical"

    elif cia_score >= 11:
        return "High"

    elif cia_score >= 7:
        return "Medium"

    else:
        return "Low"


def validate_asset(asset):
    """
    Validate the quality of one asset record.
    """

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
        "availability"
    ]:

        try:

            value = int(asset[field])

            if value < 1 or value > 5:

                errors.append(
                    f"{field} must be between 1 and 5"
                )

        except (ValueError, KeyError):

            errors.append(
                f"{field} must contain a number from 1 to 5"
            )

    # Validate classification
    if asset.get("information_classification") not in VALID_CLASSIFICATIONS:

        errors.append(
            "Invalid information classification"
        )

    # Validate status
    if asset.get("status") not in VALID_STATUSES:

        errors.append(
            "Invalid asset status"
        )

    return errors


def process_assets():

    assets = []

    validation_errors = []

    # Open the original CSV
    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        # Process every asset
        for asset in reader:

            errors = validate_asset(asset)

            # If errors exist
            if errors:

                validation_errors.append(
                    {
                        "asset_id": asset.get(
                            "asset_id",
                            "UNKNOWN"
                        ),
                        "errors": errors,
                    }
                )

            # If the asset is valid
            else:

                confidentiality = int(
                    asset["confidentiality"]
                )

                integrity = int(
                    asset["integrity"]
                )

                availability = int(
                    asset["availability"]
                )

                # Calculate CIA
                cia_score = calculate_cia_score(
                    confidentiality,
                    integrity,
                    availability
                )

                # Add calculated values
                asset["cia_score"] = cia_score

                asset["criticality"] = determine_criticality(
                    cia_score
                )

                assets.append(asset)

    return assets, validation_errors


def save_results(assets):

    if not assets:
        return

    # Create output directory if necessary
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Use fields from the processed data
    fieldnames = list(assets[0].keys())

    # Create output CSV
    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(assets)


def print_summary(
    assets,
    validation_errors
):

    print()
    print("===================================")
    print("     GRC ASSET REGISTER")
    print("          VALIDATOR")
    print("===================================")

    print()

    print(
        f"Total valid assets: {len(assets)}"
    )

    print(
        f"Validation errors: {len(validation_errors)}"
    )

    # Count criticality levels
    critical = sum(
        1
        for asset in assets
        if asset["criticality"] == "Critical"
    )

    high = sum(
        1
        for asset in assets
        if asset["criticality"] == "High"
    )

    medium = sum(
        1
        for asset in assets
        if asset["criticality"] == "Medium"
    )

    low = sum(
        1
        for asset in assets
        if asset["criticality"] == "Low"
    )

    print()
    print("Criticality:")
    print(f"Critical: {critical}")
    print(f"High:     {high}")
    print(f"Medium:   {medium}")
    print(f"Low:      {low}")

    # Display validation errors
    if validation_errors:

        print()
        print("Validation issues:")

        for item in validation_errors:

            print()
            print(
                f"Asset: {item['asset_id']}"
            )

            for error in item["errors"]:

                print(
                    f"  - {error}"
                )

    print()
    print("Validated file:")
    print(OUTPUT_FILE)

    print()


def main():

    assets, validation_errors = process_assets()

    save_results(assets)

    print_summary(
        assets,
        validation_errors
    )


# Start the program
if __name__ == "__main__":
    main()