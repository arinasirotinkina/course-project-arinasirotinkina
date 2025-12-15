P12 - IaC & Container Security: preliminary summary

Date: 2025-12-16

What was checked:
- Dockerfile: hadolint (report: EVIDENCE/P12/hadolint_report.json)
- IaC: checkov scan of `iac/` (report: EVIDENCE/P12/checkov_report.json)
- Image: trivy scan of built image `course-app:local` (report: EVIDENCE/P12/trivy_report.json)

Initial notes:
- Dockerfile uses `python:3.11-slim` (fixed tag), creates non-root `appuser`, and has a HEALTHCHECK — baseline hardening present.
- IaC: minimal `iac/deployment.yaml` added for P12 testing; Checkov will flag common issues if any.
- Trivy: image scanned — review `trivy_report.json` for vulnerabilities; plan to update base image / packages if critical findings exist.

Next steps:
- Run CI workflow `Security - IaC & Container (P12)` and inspect `EVIDENCE/P12` artifacts.
- Apply fixes for any HIGH/CRITICAL vulnerabilities from Trivy and re-run scans.
- Iterate on Checkov findings for IaC and enforce policies.
