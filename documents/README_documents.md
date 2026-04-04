# Documents Folder

Place regulatory documents here before running ingest.py.
All documents below are publicly available — no login required.

## Required

| File name            | Source URL                                                    |
|----------------------|---------------------------------------------------------------|
| PIPEDA.pdf           | https://laws-lois.justice.gc.ca/PDF/P-8.6.pdf                |
| OSFI_E23.txt         | https://www.osfi-bsif.gc.ca — copy page text                 |
| Bill_C27_AIDA.txt    | https://www.parl.ca — copy Part 3 (AIDA) text                |
| CIBC_AI.txt          | https://www.cibc.com/en/about-cibc/future-banking/ai.html    |

## Steps

1. Download/copy each document into this folder with the filenames above
2. Run: python ingest.py
3. Confirm chunk count (expect 150–500 chunks)
4. Commit the generated faiss_index/ folder to GitHub
