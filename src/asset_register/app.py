from pathlib import Path

import pandas as pd
import streamlit as st

from validator import determine_criticality
from validator import validate_asset


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="GRC Asset Register",
    page_icon="🛡️",
    layout="wide",
)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DEFAULT_DATA_FILE = (
    BASE_DIR / "data" / "asset_register.csv"
)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def calculate_asset_score(row):
    """Calculate CIA score for a dataframe row."""

    return (
        int(row["Confidentiality"])
        + int(row["Integrity"])
        + int(row["Availability"])
    )


def calculate_criticality(score):
    """Calculate criticality from CIA score."""

    return determine_criticality(score)


def validate_dataframe(df):
    """Validate all asset records."""

    findings = []

    for index, row in df.iterrows():

        asset = {
            "asset_id": str(row.get("Asset ID", "")),
            "asset_name": str(row.get("Asset Name", "")),
            "asset_type": str(row.get("Asset Type", "")),
            "owner": str(row.get("Owner", "")),
            "custodian": str(row.get("Custodian", "")),
            "status": str(row.get("Status", "")),
            "confidentiality": str(
                row.get("Confidentiality", "")
            ),
            "integrity": str(
                row.get("Integrity", "")
            ),
            "availability": str(
                row.get("Availability", "")
            ),
            "information_classification": str(
                row.get(
                    "Information Classification",
                    "",
                )
            ),
        }

        errors = validate_asset(asset)

        for error in errors:

            findings.append(
                {
                    "Row": index + 1,
                    "Asset ID": asset["asset_id"],
                    "Asset Name": asset["asset_name"],
                    "Finding": error,
                }
            )

    return findings


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🛡️ GRC Information Asset Register")

st.markdown(
    """
    **Information Security Asset Management Dashboard**

    Maintain, assess and review organisational information
    assets using Confidentiality, Integrity and Availability
    scoring.
    """
)

st.divider()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Data Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload Asset Register CSV",
    type=["csv"],
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.sidebar.success(
        "Uploaded asset register loaded."
    )

elif DEFAULT_DATA_FILE.exists():

    df = pd.read_csv(DEFAULT_DATA_FILE)

    st.sidebar.info(
        "Using default asset register."
    )

else:

    st.error(
        "No asset register found. "
        "Please upload a CSV file."
    )

    st.stop()


# ---------------------------------------------------------
# Data preparation
# ---------------------------------------------------------

required_columns = [
    "Asset ID",
    "Asset Name",
    "Asset Type",
    "Owner",
    "Custodian",
    "Status",
    "Information Classification",
    "Confidentiality",
    "Integrity",
    "Availability",
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error(
        "The following required columns are missing:"
    )

    st.write(missing_columns)

    st.stop()


# Calculate CIA score

df["CIA Score"] = df.apply(
    calculate_asset_score,
    axis=1,
)

# Calculate criticality

df["Criticality"] = df["CIA Score"].apply(
    calculate_criticality
)


# ---------------------------------------------------------
# Dashboard metrics
# ---------------------------------------------------------

total_assets = len(df)

critical_assets = len(
    df[df["Criticality"] == "Critical"]
)

high_assets = len(
    df[df["Criticality"] == "High"]
)

personal_data_assets = 0

if "Personal Data" in df.columns:

    personal_data_assets = len(
        df[
            df["Personal Data"]
            .astype(str)
            .str.lower()
            .isin(["yes", "true", "1"])
        ]
    )


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Assets",
        total_assets,
    )

with col2:

    st.metric(
        "Critical Assets",
        critical_assets,
    )

with col3:

    st.metric(
        "High-Risk Assets",
        high_assets,
    )

with col4:

    st.metric(
        "Personal Data Assets",
        personal_data_assets,
    )


st.divider()


# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

st.subheader("Asset Filters")

col1, col2, col3 = st.columns(3)


with col1:

    asset_types = [
        "All"
    ] + sorted(
        df["Asset Type"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_type = st.selectbox(
        "Asset Type",
        asset_types,
    )


with col2:

    criticality_options = [
        "All",
        "Critical",
        "High",
        "Medium",
        "Low",
    ]

    selected_criticality = st.selectbox(
        "Criticality",
        criticality_options,
    )


with col3:

    classifications = [
        "All"
    ] + sorted(
        df[
            "Information Classification"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    selected_classification = st.selectbox(
        "Information Classification",
        classifications,
    )


filtered_df = df.copy()


if selected_type != "All":

    filtered_df = filtered_df[
        filtered_df["Asset Type"]
        == selected_type
    ]


if selected_criticality != "All":

    filtered_df = filtered_df[
        filtered_df["Criticality"]
        == selected_criticality
    ]


if selected_classification != "All":

    filtered_df = filtered_df[
        filtered_df[
            "Information Classification"
        ]
        == selected_classification
    ]


# ---------------------------------------------------------
# Asset Register
# ---------------------------------------------------------

st.subheader("Asset Inventory")

display_columns = [
    "Asset ID",
    "Asset Name",
    "Asset Type",
    "Owner",
    "Status",
    "Information Classification",
    "Confidentiality",
    "Integrity",
    "Availability",
    "CIA Score",
    "Criticality",
]

available_columns = [
    column
    for column in display_columns
    if column in filtered_df.columns
]


st.dataframe(
    filtered_df[available_columns],
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Analytics
# ---------------------------------------------------------

st.divider()

st.subheader("Asset Analytics")

col1, col2 = st.columns(2)


with col1:

    st.markdown("### Assets by Criticality")

    criticality_counts = (
        df["Criticality"]
        .value_counts()
    )

    st.bar_chart(
        criticality_counts
    )


with col2:

    st.markdown("### Assets by Type")

    type_counts = (
        df["Asset Type"]
        .value_counts()
    )

    st.bar_chart(
        type_counts
    )


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

st.divider()

st.subheader("🔎 Data Quality Validation")

validation_findings = validate_dataframe(df)


if not validation_findings:

    st.success(
        "No validation issues detected."
    )

else:

    st.warning(
        f"{len(validation_findings)} "
        "validation issue(s) detected."
    )

    findings_df = pd.DataFrame(
        validation_findings
    )

    st.dataframe(
        findings_df,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Critical Assets
# ---------------------------------------------------------

st.divider()

st.subheader("🚨 Critical Assets")

critical_df = df[
    df["Criticality"] == "Critical"
]


if critical_df.empty:

    st.info(
        "No critical assets identified."
    )

else:

    st.dataframe(
        critical_df[available_columns],
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

st.subheader("📥 Export")

csv_data = df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="Download Validated Asset Register",
    data=csv_data,
    file_name="asset_register_validated.csv",
    mime="text/csv",
)