from asset_register.validator import (
    calculate_cia_score,
    determine_criticality,
    validate_asset,
)


def test_cia_score():

    assert calculate_cia_score(
        5,
        5,
        5,
    ) == 15


def test_criticality():

    assert determine_criticality(15) == "Critical"
    assert determine_criticality(12) == "High"
    assert determine_criticality(9) == "Medium"
    assert determine_criticality(5) == "Low"


def test_invalid_cia_value():

    asset = {
        "asset_id": "TEST-001",
        "asset_name": "Test Asset",
        "asset_type": "Information",
        "owner": "Test Owner",
        "custodian": "Test Custodian",
        "status": "Active",
        "confidentiality": "8",
        "integrity": "5",
        "availability": "5",
        "information_classification": "Internal",
    }

    errors = validate_asset(asset)

    assert len(errors) > 0