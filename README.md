# Information Asset Register

## Overview

This project demonstrates the development of an Information Asset Register for a fictional organization.

The project supports information security governance by identifying, classifying and assessing information and associated assets.

A Python validation tool is included to automate data quality checks and CIA-based criticality assessment.

---

## Objectives

The project aims to:

- Identify organizational assets
- Assign asset ownership
- Classify information
- Assess Confidentiality, Integrity and Availability
- Calculate asset criticality
- Identify assets containing personal data
- Link assets to risk records
- Validate inventory data
- Automate GRC calculations

---

## Asset Categories

The register includes:

- Information
- Applications
- Infrastructure
- Endpoints
- Services

---

## CIA Assessment

Each asset receives a score from 1 to 5 for:

- Confidentiality
- Integrity
- Availability

The total CIA Score ranges from 3 to 15.

---

## Criticality Model

| CIA Score | Criticality |
|---:|---|
| 3–6 | Low |
| 7–10 | Medium |
| 11–13 | High |
| 14–15 | Critical |

---

## Automation

The Python script:

1. Reads the asset inventory
2. Validates mandatory fields
3. Validates CIA values
4. Validates classifications
5. Calculates CIA scores
6. Determines criticality
7. Reports validation errors
8. Generates a validated CSV file

---

## Technologies

- Python
- CSV
- Git
- GitHub
- Visual Studio Code

---

## Repository Structure

```text
Project-3-Asset-Register/
│
├── data/
│   └── asset_register.csv
│
├── docs/
│   ├── methodology.md
│   └── asset-management-policy.md
│
├── reports/
│   └── asset_register_report.md
│
├── src/
│   └── asset_register.py
│
├── output/
│   └── asset_register_validated.csv
│
├── .gitignore
└── README.md

GRC Value

The Asset Register provides a foundation for:

Information security risk assessment
Risk treatment
GDPR Data Mapping
Incident Response Planning
Vendor Risk Assessment
Business Impact Analysis
Business Continuity Planning

Methodology Note

The CIA scoring model and criticality thresholds are defined specifically for this demonstration project.

Organizations should define their own assessment criteria according to their business context and risk methodology.