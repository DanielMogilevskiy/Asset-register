import argparse
from pathlib import Path

from .validator import process_assets
from .validator import save_results


def print_summary(
    assets,
    validation_errors,
):
    """Print a human-readable assessment summary."""

    print()
    print("=" * 45)
    print("       GRC ASSET REGISTER")
    print("            VALIDATOR")
    print("=" * 45)

    print()
    print(f"Valid assets:       {len(assets)}")
    print(
        f"Validation errors:  {len(validation_errors)}"
    )

    critical = sum(
        asset["criticality"] == "Critical"
        for asset in assets
    )

    high = sum(
        asset["criticality"] == "High"
        for asset in assets
    )

    medium = sum(
        asset["criticality"] == "Medium"
        for asset in assets
    )

    low = sum(
        asset["criticality"] == "Low"
        for asset in assets
    )

    print()
    print("Criticality")
    print("-" * 20)
    print(f"Critical: {critical}")
    print(f"High:     {high}")
    print(f"Medium:   {medium}")
    print(f"Low:      {low}")

    if validation_errors:

        print()
        print("Validation Issues")
        print("-" * 20)

        for item in validation_errors:

            print(
                f"\n{item['asset_id']}:"
            )

            for error in item["errors"]:
                print(f"  - {error}")

    print()


def main():
    """Main CLI entry point."""

    parser = argparse.ArgumentParser(
        description=(
            "Validate an information asset register "
            "and calculate CIA-based criticality."
        )
    )

    parser.add_argument(
        "--data",
        default="data/asset_register.csv",
        help="Path to the asset register CSV",
    )

    parser.add_argument(
        "--output",
        default="output/asset_register_validated.csv",
        help="Path for the validated output CSV",
    )

    args = parser.parse_args()

    input_file = Path(args.data)
    output_file = Path(args.output)

    if not input_file.exists():

        print(
            f"Error: input file not found: {input_file}"
        )

        return 1

    assets, validation_errors = process_assets(
        input_file
    )

    save_results(
        assets,
        output_file,
    )

    print_summary(
        assets,
        validation_errors,
    )

    print(
        f"Validated register saved to: {output_file}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())