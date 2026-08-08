# Asset Register Methodology

## 1. Purpose

This methodology defines how information and associated assets are identified, classified, owned and assessed.

The methodology supports information security governance and asset inventory management.

---

## 2. Asset Categories

The asset inventory includes:

- Information
- Applications
- Infrastructure
- Endpoints
- Services
- Physical assets

---

## 3. Asset Ownership

Each asset should have:

- Asset Owner
- Asset Custodian

The Asset Owner is accountable for the business value and security requirements of the asset.

The Custodian is responsible for operational or technical management.

---

## 4. CIA Assessment

Each asset is assessed according to:

### Confidentiality

The potential impact of unauthorized disclosure.

### Integrity

The potential impact of unauthorized modification or destruction.

### Availability

The potential impact of loss of availability.

Each dimension is scored from 1 to 5.

| Score | Meaning |
|---:|---|
| 1 | Low |
| 2 | Minor |
| 3 | Moderate |
| 4 | High |
| 5 | Critical |

---

## 5. CIA Score

The CIA Score is calculated as:

CIA Score = Confidentiality + Integrity + Availability

Minimum score:

3

Maximum score:

15

---

## 6. Criticality

| CIA Score | Criticality |
|---:|---|
| 3–6 | Low |
| 7–10 | Medium |
| 11–13 | High |
| 14–15 | Critical |

These thresholds are part of the project's defined assessment methodology.

They are not universal numerical thresholds prescribed by ISO.

---

## 7. Information Classification

The project uses:

- Public
- Internal
- Confidential
- Restricted

---

## 8. Personal Data

The register identifies whether an asset contains or processes personal data.

This information will support the future GDPR Data Mapping project.

---

## 9. Risk Mapping

Assets may be linked to risks using a Risk ID.

Example:

Asset:

AST-001

Risk:

RISK-001

This allows the Asset Register to support the organization's risk management process.

---

## 10. Review

Assets should be reviewed:

- Periodically
- After significant changes
- After ownership changes
- Following security incidents
- During risk assessment activities