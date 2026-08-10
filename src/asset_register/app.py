from pathlib import Path

import pandas as pd
import streamlit as st

from validator import (
    calculate_cia_score,
    determine_criticality,
    validate_asset_findings,
)


# ============================================================
# Configuration
# ============================================================

st.set_page_config(
    page_title="GRC Information Asset Register",
    page_icon="🛡️",
    layout="wide",
)


REQUIRED_COLUMNS = [
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


DEFAULT_DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "asset_register.csv"
)


# ============================================================
# Helper functions
# ============================================================

def load_data(uploaded_file=None):

    if uploaded_file is not None:
        df = pd.read_csv(
            uploaded_file,
            encoding="utf-8-sig"
        )

        return normalize_columns(df)

    if not DEFAULT_DATA_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(
        DEFAULT_DATA_PATH,
        encoding="utf-8-sig"
    )

    return normalize_columns(df)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize CSV column names so the application can handle
    common naming variations.
    """

    df = df.copy()

    # Remove BOM and surrounding whitespace
    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    column_mapping = {
        # Asset ID
        "asset_id": "Asset ID",
        "assetid": "Asset ID",
        "id": "Asset ID",

        # Asset Name
        "asset_name": "Asset Name",
        "assetname": "Asset Name",
        "name": "Asset Name",

        # Asset Type
        "asset_type": "Asset Type",
        "assettype": "Asset Type",
        "type": "Asset Type",

        # Owner
        "owner": "Owner",
        "asset_owner": "Owner",

        # Custodian
        "custodian": "Custodian",
        "asset_custodian": "Custodian",

        # Status
        "status": "Status",
        "asset_status": "Status",

        # Classification
        "information_classification":
            "Information Classification",

        "informationclassification":
            "Information Classification",

        "information_class":
            "Information Classification",

        "classification":
            "Information Classification",

        # CIA
        "confidentiality": "Confidentiality",
        "confidentiality_score": "Confidentiality",

        "integrity": "Integrity",
        "integrity_score": "Integrity",

        "availability": "Availability",
        "availability_score": "Availability",

        # Additional GRC fields
        "personal_data": "Personal Data",
        "personaldata": "Personal Data",

        "backup_required": "Backup Required",
        "backuprequired": "Backup Required",

        "review_date": "Review Date",
        "reviewdate": "Review Date",

        "risk_id": "Risk ID",
        "riskid": "Risk ID",
    }

    normalized_mapping = {}

    for column in df.columns:

        normalized_key = (
            column
            .lower()
            .strip()
            .replace(" ", "_")
            .replace("-", "_")
        )

        if normalized_key in column_mapping:
            normalized_mapping[column] = (
                column_mapping[normalized_key]
            )

    df = df.rename(
        columns=normalized_mapping
    )

    return df

def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df["CIA Score"] = df.apply(
        lambda row: calculate_cia_score(
            row["Confidentiality"],
            row["Integrity"],
            row["Availability"],
        ),
        axis=1,
    )

    df["Criticality"] = df["CIA Score"].apply(
        lambda score:
        determine_criticality(score)
        if pd.notna(score)
        else "Unknown"
    )

    return df


def generate_findings(df: pd.DataFrame) -> pd.DataFrame:

    findings = []

    for _, row in df.iterrows():

        asset = {
            "asset_id": row.get("Asset ID"),
            "asset_name": row.get("Asset Name"),
            "asset_type": row.get("Asset Type"),
            "owner": row.get("Owner"),
            "custodian": row.get("Custodian"),
            "status": row.get("Status"),
            "information_classification":
                row.get("Information Classification"),
            "personal_data":
                row.get("Personal Data"),
            "confidentiality":
                row.get("Confidentiality"),
            "integrity":
                row.get("Integrity"),
            "availability":
                row.get("Availability"),
            "backup_required":
                row.get("Backup Required"),
            "review_date":
                row.get("Review Date"),
        }

        findings.extend(
            validate_asset_findings(asset)
        )

    if not findings:
        return pd.DataFrame(
            columns=[
                "Asset ID",
                "Severity",
                "Category",
                "Code",
                "Finding",
                "Recommendation",
            ]
        )

    return pd.DataFrame(findings)


# ============================================================
# Header
# ============================================================

st.title("🛡️ GRC Information Asset Register")

st.markdown(
    """
### Information Security Asset Management Dashboard

Maintain, assess and review organisational information assets
using **Confidentiality, Integrity and Availability (CIA) scoring**,
asset criticality and governance validation.
"""
)

st.divider()


# ============================================================
# Load data
# ============================================================

uploaded_file = st.sidebar.file_uploader(
    "Upload Asset Register CSV",
    type=["csv"],
)

df = load_data(uploaded_file)


if df.empty:

    st.error(
        "No asset register data was found."
    )

    st.stop()


# ============================================================
# Column validation
# ============================================================

missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing_columns:

    st.error(
        "The following required columns are missing:"
    )

    st.write(missing_columns)

    st.info(
        "Columns detected in uploaded CSV:"
    )

    st.write(
        df.columns.tolist()
    )

    st.stop()


# ============================================================
# Calculations
# ============================================================

df = calculate_metrics(df)

findings_df = generate_findings(df)


# ============================================================
# Duplicate Asset ID check
# ============================================================

duplicate_ids = (
    df["Asset ID"]
    .astype(str)
    .duplicated(keep=False)
)

duplicate_count = duplicate_ids.sum()


if duplicate_count > 0:

    duplicate_rows = df.loc[
        duplicate_ids,
        "Asset ID"
    ].tolist()

    duplicate_findings = pd.DataFrame(
        [
            {
                "Asset ID": asset_id,
                "Severity": "High",
                "Category": "Data Quality",
                "Code": "DQ-010",
                "Finding": "Duplicate Asset ID",
                "Recommendation":
                    "Ensure every asset has a unique identifier.",
            }
            for asset_id in duplicate_rows
        ]
    )

    findings_df = pd.concat(
        [
            findings_df,
            duplicate_findings,
        ],
        ignore_index=True,
    )


# ============================================================
# KPI calculations
# ============================================================

total_assets = len(df)

critical_assets = (
    df["Criticality"] == "Critical"
).sum()

high_risk_assets = (
    df["Criticality"].isin(
        ["High", "Critical"]
    )
).sum()

personal_data_assets = 0

if "Personal Data" in df.columns:

    personal_data_assets = (
        df["Personal Data"]
        .astype(str)
        .str.lower()
        .isin(["yes", "true", "1"])
        .sum()
    )


# ============================================================
# KPI Dashboard
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Assets",
    total_assets,
)

col2.metric(
    "Critical Assets",
    critical_assets,
)

col3.metric(
    "High & Critical Assets",
    high_risk_assets,
)

col4.metric(
    "Personal Data Assets",
    personal_data_assets,
)


st.divider()


# ============================================================
# Asset Filters
# ============================================================

st.subheader("Asset Filters")

col1, col2, col3, col4, col5 = st.columns(5)


asset_types = [
    "All"
] + sorted(
    df["Asset Type"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

criticalities = [
    "All"
] + sorted(
    df["Criticality"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

classifications = [
    "All"
] + sorted(
    df["Information Classification"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

statuses = [
    "All"
] + sorted(
    df["Status"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

owners = [
    "All"
] + sorted(
    df["Owner"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


selected_type = col1.selectbox(
    "Asset Type",
    asset_types,
)

selected_criticality = col2.selectbox(
    "Criticality",
    criticalities,
)

selected_classification = col3.selectbox(
    "Information Classification",
    classifications,
)

selected_status = col4.selectbox(
    "Status",
    statuses,
)

selected_owner = col5.selectbox(
    "Owner",
    owners,
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


if selected_status != "All":
    filtered_df = filtered_df[
        filtered_df["Status"]
        == selected_status
    ]


if selected_owner != "All":
    filtered_df = filtered_df[
        filtered_df["Owner"]
        == selected_owner
    ]


# ============================================================
# Asset Inventory
# ============================================================

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

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# Governance Status
# ============================================================

st.divider()

st.subheader(
    "🔎 GRC Governance & Data Quality"
)


if findings_df.empty:

    st.success(
        "No governance findings detected."
    )

else:

    data_quality_count = (
        findings_df["Category"]
        == "Data Quality"
    ).sum()

    privacy_count = (
        findings_df["Category"]
        == "Privacy"
    ).sum()

    risk_count = (
        findings_df["Category"]
        == "Risk Governance"
    ).sum()

    business_continuity_count = (
        findings_df["Category"]
        == "Business Continuity"
    ).sum()

    critical_findings = (
        findings_df["Severity"]
        == "Critical"
    ).sum()

    high_findings = (
        findings_df["Severity"]
        == "High"
    ).sum()

    medium_findings = (
        findings_df["Severity"]
        == "Medium"
    ).sum()


    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Findings",
        len(findings_df),
    )

    col2.metric(
        "Critical",
        critical_findings,
    )

    col3.metric(
        "High",
        high_findings,
    )

    col4.metric(
        "Medium",
        medium_findings,
    )

    col5.metric(
        "Data Quality",
        data_quality_count,
    )


    st.markdown("### Governance Review Summary")

    summary_df = pd.DataFrame(
        {
            "Category": [
                "Data Quality",
                "Privacy",
                "Risk Governance",
                "Business Continuity",
            ],
            "Findings": [
                data_quality_count,
                privacy_count,
                risk_count,
                business_continuity_count,
            ],
        }
    )

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Findings
# ============================================================

if not findings_df.empty:

    st.markdown(
        "### Governance Findings"
    )

    severity_filter = st.selectbox(
        "Filter by Severity",
        [
            "All",
            "Critical",
            "High",
            "Medium",
        ],
    )

    category_filter = st.selectbox(
        "Filter by Category",
        [
            "All"
        ]
        + sorted(
            findings_df["Category"]
            .unique()
            .tolist()
        ),
    )

    filtered_findings = findings_df.copy()


    if severity_filter != "All":

        filtered_findings = (
            filtered_findings[
                filtered_findings[
                    "Severity"
                ]
                == severity_filter
            ]
        )


    if category_filter != "All":

        filtered_findings = (
            filtered_findings[
                filtered_findings[
                    "Category"
                ]
                == category_filter
            ]
        )


    st.dataframe(
        filtered_findings[
            [
                "Asset ID",
                "Severity",
                "Category",
                "Code",
                "Finding",
                "Recommendation",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Analytics
# ============================================================

st.divider()

st.subheader("📊 Asset Analytics")

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        "### Assets by Criticality"
    )

    criticality_counts = (
        df["Criticality"]
        .value_counts()
        .reindex(
            [
                "Critical",
                "High",
                "Medium",
                "Low",
            ],
            fill_value=0,
        )
    )

    st.bar_chart(
        criticality_counts
    )


with col2:

    st.markdown(
        "### Assets by Type"
    )

    type_counts = (
        df["Asset Type"]
        .value_counts()
    )

    st.bar_chart(
        type_counts
    )


# ============================================================
# Classification Analytics
# ============================================================

st.markdown(
    "### Information Classification"
)

classification_counts = (
    df["Information Classification"]
    .value_counts()
)

st.bar_chart(
    classification_counts
)


# ============================================================
# Export
# ============================================================

st.divider()

st.subheader("📥 Export")

asset_csv = df.to_csv(
    index=False
).encode("utf-8")

findings_csv = findings_df.to_csv(
    index=False
).encode("utf-8")


col1, col2 = st.columns(2)


with col1:

    st.download_button(
        "Download Asset Register",
        data=asset_csv,
        file_name="asset_register_report.csv",
        mime="text/csv",
    )


with col2:

    st.download_button(
        "Download GRC Findings",
        data=findings_csv,
        file_name="asset_register_findings.csv",
        mime="text/csv",
    )