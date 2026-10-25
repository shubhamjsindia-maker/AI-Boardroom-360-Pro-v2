# AI Boardroom 360 Pro — Phase 1 Alpha

A NEW independent Streamlit financial history application. This is **not** a replacement for the existing AI Boardroom 360 website.

## Working now
- Guided CA and Professional Analyst navigation
- Fictional Nova Manufacturing with 5 years of internally reconciled historical figures
- Downloadable blank/sample Excel workbooks; import a workbook in the specified normalized format
- Historical P&L, Balance Sheet, Cash Flow and Changes in Equity **simplified normalized presentations**
- Seven historical financial ratios, visual trend dashboard
- Eleven deterministic reconciliation checks per financial year
- Download draft historical financial PDF and Excel review files

## Not yet implemented — do not use for confidential client work
- Full Schedule III Division II disclosure presentation and linked notes
- Arbitrary annual report PDF extraction, source-page traceability, OCR
- Secure authentication, company isolation, multi-user approvals, immutable audit history
- Persistent database and document storage
- Gemini directors, forecasts, investment cases, shocks
- Audited certification or independent public-company figure verification

Financial data in the bundled Nova sample is entirely fictional. Uploaded data is not independently verified. This alpha runs in session memory and will not preserve imports when its session is lost.

## Deploy on Streamlit Community Cloud
1. Create a **new** GitHub repository such as `AI-Boardroom-360-Pro-v2`.
2. Upload all the files from this project, keeping `app.py`, `requirements.txt`, `core/`, `.streamlit/` and `tests/` in their correct paths.
3. Go to Streamlit Community Cloud → Create app → select new repository, branch `main`, main file `app.py`.
4. Deploy. Use only fictional or otherwise appropriate public data during demonstration.
5. Do **not** overwrite the current v1.x GitHub repository.

## Local developer instructions
```
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
streamlit run app.py
```

## Phase 1 development backlog
1. Complete Schedule III line-item taxonomy and published note disclosures
2. Digitally generated annual report PDF extraction with verifiable page references
3. Mapping Studio with configurable classifications and original-source details
4. Full cash-flow classifications and equity disclosures
5. Managed persistence and maker-checker enforcement
6. Source-reviewed real-company reference datasets
7. Expanded edge-case tests and production-grade export quality
