# KYC/AML Client Onboarding Screening Tool (synthetic data)

Simulates onboarding checks from the Deloitte Associate Analyst JD (KYC = Know Your Customer, AML = Anti-Money Laundering).

**Run:** `python3 01_generate_data.py` then `python3 02_screen_and_report.py`  (Python 3, pandas, openpyxl)

## What it does
- 200 synthetic client profiles (individual + corporate); fictional names, placeholder high-risk country codes (XA, XB) and a fictional 30-name watchlist.
- Checks: ID document expiry, address proof older than 90 days, corporate UBO (ultimate beneficial owner) declared, source of funds present.
- Fuzzy watchlist screening (difflib, token-sorted names, 0.85 threshold) that also catches reordered/typo'd names.
- Rule-based risk score -> Low/Medium/High and a recommended action (approve / return to client / escalate to Compliance / enhanced due diligence).
- Excel report + CSV audit log (`reports/`).

## Result (self-checked against hidden ground truth)
200 reviewed -> 52 exceptions incl. 16 watchlist escalations; 52/52 planted issues detected, 0 unplanted clients flagged; 147 approved.

## Interview talking points
- Thresholds trade false positives vs missed matches; a human in Compliance makes the final call.
- Risk scoring here is a simple, explainable rule set, not a real bank model.
- Synthetic data and placeholder jurisdictions only.
