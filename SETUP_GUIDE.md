# ComplianceNav AI — Complete Setup Guide
# Backend (Railway) + Frontend (Lovable)
# From zero to live URL

---

## PART 1: LOCAL SETUP (VS Code)

### Step 1 — Set up the project

```bash
# Open VS Code terminal and run:

cd compliancenav-backend
python -m venv .venv

# Mac/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

---

### Step 2 — Add your API key

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder:
```
ANTHROPIC_API_KEY=sk-ant-your-real-key-here
```

Get your key from: https://console.anthropic.com

---

### Step 3 — Download regulatory documents

Download these 4 files into the `documents/` folder:

1. **PIPEDA.pdf**
   URL: https://laws-lois.justice.gc.ca/PDF/P-8.6.pdf
   Action: Download PDF directly → save as PIPEDA.pdf

2. **OSFI_E23.txt**
   URL: https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/model-risk-management-guideline
   Action: Select all text on page → paste into OSFI_E23.txt

3. **Bill_C27_AIDA.txt**
   URL: https://www.parl.ca/DocumentViewer/en/44-1/bill/C-27/first-reading
   Action: Copy Part 3 (Artificial Intelligence and Data Act) → paste into Bill_C27_AIDA.txt

4. **CIBC_AI.txt**
   URL: https://www.cibc.com/en/about-cibc/future-banking/ai.html
   Action: Select all text → paste into CIBC_AI.txt

Minimum to get started: PIPEDA.pdf + OSFI_E23.txt (2 files is enough to test)

---

### Step 4 — Build the FAISS vector store

```bash
python ingest.py
```

Expected output:
```
ComplianceNav AI — Ingestion Pipeline
1. Loading documents...  ✓ Loaded X pages from 4 file(s)
2. Chunking...           ✓ Created ~300 chunks (avg ~400 chars)
3. Building FAISS index...  ✓ FAISS index saved (300 vectors)
4. Verifying...
   [PIPEDA — Chunk 12] similarity=0.742
   [PIPEDA — Chunk 8]  similarity=0.698
✅ Done.
```

If you see "No results" in verification → your documents didn't load.
Check filenames match exactly (case-sensitive on Mac/Linux).

---

### Step 5 — Test locally

```bash
uvicorn main:app --reload --port 8000
```

Open: http://localhost:8000/docs

Try the /query endpoint with:
```json
{
  "question": "What are the consent requirements under PIPEDA?"
}
```

You should get a full JSON response with answer, sources, confidence, escalation fields.

---

## PART 2: DEPLOY TO RAILWAY

### Step 6 — Push to GitHub

```bash
# In your terminal (make sure you're in compliancenav-backend/)

git init
git add .
git commit -m "Initial ComplianceNav AI backend"

# Create a new repo on github.com called: compliancenav-backend
# Then:
git remote add origin https://github.com/YOUR_USERNAME/compliancenav-backend.git
git branch -M main
git push -u origin main
```

IMPORTANT: The faiss_index/ folder must be committed.
Check your .gitignore — it should NOT include faiss_index/.

---

### Step 7 — Deploy on Railway

1. Go to https://railway.app and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `compliancenav-backend` repo
4. Railway auto-detects the Procfile and starts building

5. Add environment variable:
   - Go to your project → Variables tab
   - Add: ANTHROPIC_API_KEY = sk-ant-your-real-key-here

6. Wait for build to complete (~3-5 minutes first time)
   Railway installs requirements.txt and starts uvicorn

7. Click "Settings" → copy your Railway domain
   It will look like: https://compliancenav-backend-production.up.railway.app

8. Test it: visit https://your-railway-url.railway.app/health
   You should see: {"status": "ok", "service": "ComplianceNav AI"}

SAVE YOUR RAILWAY URL — you need it for Lovable.

---

## PART 3: BUILD FRONTEND ON LOVABLE

### Step 8 — Create Lovable project

1. Go to https://lovable.dev and sign in
2. Click "New Project"
3. Paste the ENTIRE prompt below into the first message box
4. Replace YOUR_RAILWAY_URL with your actual Railway URL before pasting

---

### LOVABLE PROMPT (copy everything between the lines)
---
Build a professional, modern web application called "ComplianceNav AI" — a responsible AI compliance agent for Canadian banking professionals.

DESIGN INSPIRATION: Clean, minimalist, trustworthy — inspired by Wealthsimple and Lemonade Insurance. Use lots of white space, a tight colour palette, bold confident typography, and subtle card shadows. The app should feel like a premium fintech product, not a generic tool.

COLOUR PALETTE:
- Primary: #1B3A5C (deep navy)
- Accent: #1A6B72 (teal)
- Background: #FAFAF8 (off-white)
- Card background: #FFFFFF
- Success/High confidence: #0F5C2E (dark green)
- Warning/Medium confidence: #7A4F00 (amber)
- Danger/Low confidence + escalation: #C0392B (red)
- Text primary: #1A1A2E
- Text secondary: #555555
- Border: #E8E8E8

TYPOGRAPHY:
- Use Inter font (import from Google Fonts)
- Hero heading: 2.8rem, weight 700, navy
- Section headings: 1.1rem, weight 600
- Body text: 0.95rem, weight 400, line-height 1.7
- Generous padding and white space throughout

LAYOUT: Single page app. No sidebar. Clean top navigation bar with logo and tagline.

---

BUILD THESE EXACT SECTIONS:

1. TOP NAV BAR
- Left: "ComplianceNav AI" logo text in navy (bold, 1.2rem) + small teal dot before it
- Right: "Built by Mahesh Kumar" in grey, small text
- White background, subtle bottom border, sticky

2. HERO SECTION
- Large heading: "AI-Powered Compliance Navigation"
- Subheading: "Instant answers from Canadian banking AI governance frameworks — PIPEDA, AIRAP, and OSFI — with built-in responsible AI safeguards."
- Three feature pills in a row (teal background, white text, rounded):
  "📋 Source Citations" | "🎯 Confidence Scoring" | "🔴 Human Escalation"
- Clean, centered, generous padding

3. RESPONSIBLE AI BADGES ROW
Three cards in a horizontal row, each with icon + title + 1-line description:
- Card 1: 📖 "Source Transparency" — "Every answer cites the exact document and section"
- Card 2: 🎯 "Confidence Calibration" — "Retrieval-adjusted scoring prevents overconfident AI"
- Card 3: 🔴 "Human Escalation" — "Material determinations trigger automatic human review"
Cards have white background, subtle shadow, rounded corners (12px), teal left border accent

4. EXAMPLE QUESTIONS ROW
Heading: "Try an example question"
5 clickable pills in a flex-wrap row:
- "What are PIPEDA's consent requirements?"
- "What does AIRAP require for high-risk AI models?"
- "How does OSFI E-23 define model risk?"
- "Is consent always required under PIPEDA?"
- "What are the penalties for a PIPEDA breach?"
Pills: light grey background (#F0EDE8), navy text, rounded-full, hover → teal background white text

5. QUERY INPUT SECTION
- Label: "Ask a compliance question" (bold, navy)
- Large textarea (4 rows), clean border, focus ring in teal
- "Ask ComplianceNav" button — full navy background, white text, bold, rounded-lg, hover darkens
- Loading state: button shows spinning indicator + "Analysing regulatory documents..."

6. RESPONSE SECTION (shown after submit, hidden initially)
Animate in with a smooth fade (opacity 0 → 1, translateY 8px → 0)

Show these elements in order:

A. ESCALATION BANNER (only if escalation_required = true)
Red background (#FFF0F0), red left border (4px), red icon 🔴
Bold "Human Review Required" heading
Escalation reason text below
Full width, prominent

B. CONFIDENCE BADGE
Inline badge with coloured background:
- HIGH: green background (#E8F5E9), green text, "✅ High Confidence"
- MEDIUM: amber background (#FFF8E1), amber text, "⚠️ Medium Confidence"
- LOW: red background (#FDECEA), red text, "❌ Low Confidence"
Show confidence_rationale as small italic grey text below the badge
If override_note exists, show it in small italic text with an ℹ️ icon

C. ANSWER BOX
White card, teal left border (4px), subtle shadow
Render answer text (it contains inline citations like [PIPEDA, S.4.3] — render as-is)

D. SOURCE CITATION PILLS
"📖 Sources cited:" label (bold, small)
For each source in sources array: teal background pill showing "document · section"
Flex-wrap row

E. RETRIEVAL TRANSPARENCY EXPANDER
Collapsed by default. Toggle with "🔬 View retrieval details" link in small grey text
When expanded: show each retrieved chunk with source, section, similarity score as a percentage bar

F. LEGAL DISCLAIMER
Small grey italic text, separated by a top border
Always visible at bottom of response

---

API INTEGRATION:

Backend URL: YOUR_RAILWAY_URL (replace with real URL)

On form submit, make a POST request to: {BACKEND_URL}/query
Headers: Content-Type: application/json
Body: { "question": "user's question here" }

The API returns this JSON structure — map it exactly to the UI above:
{
  "answer": string,
  "sources": [{ "document": string, "section": string, "relevance": string }],
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "confidence_rationale": string,
  "override_note": string | null,
  "escalation_required": boolean,
  "escalation_reason": string | null,
  "retrieved_chunks": [{ "source": string, "section": string, "similarity_score": number, "text_preview": string }],
  "disclaimer": string
}

Handle errors gracefully: if the API call fails, show a red error card saying "Unable to connect to the compliance engine. Please try again."

Show a skeleton loading state (grey animated bars) while waiting for the API response.

---

FOOTER:
- "ComplianceNav AI is for informational purposes only and does not constitute legal advice."
- "Built by Mahesh Kumar · AI Product Portfolio"
- Links: GitHub | LinkedIn
- Dark navy background, white text, centered

---

Make the entire app fully responsive for mobile.
Use Tailwind CSS for styling.
Use React hooks (useState, useEffect) for state management.
No authentication required — public access.
---

### Step 9 — Update the backend URL in Lovable

After Lovable generates the app:
1. Find the line with YOUR_RAILWAY_URL in the generated code
2. Replace with your actual Railway URL e.g.:
   https://compliancenav-backend-production.up.railway.app
3. Lovable auto-saves and redeploys

---

### Step 10 — Test end to end

1. Open your Lovable live URL
2. Click an example question
3. Verify you see: answer + sources + confidence badge
4. Click "Is consent always required under PIPEDA?" 
   → Should trigger the escalation banner (contains "consent required")
5. Click "🔬 View retrieval details" → verify chunks show with similarity scores

If the app loads but queries fail:
- Check Railway logs (Railway dashboard → Deployments → View logs)
- Check CORS: make sure allow_origins=["*"] is in main.py
- Check the Railway URL has no trailing slash

---

## PART 4: LINKEDIN POST (Post 5-7 days before interview)

SCREENSHOT THESE before posting:
1. The escalation banner being triggered
2. The source citation pills on a clean answer
3. The confidence badge (ideally HIGH confidence on a clear query)

Post text:
---
Canadian banks are deploying AI faster than compliance teams can keep up. That gap is a product problem — so I built a tool to address it.

ComplianceNav AI is a RAG-powered compliance agent that answers questions about PIPEDA, AIRAP, and OSFI model risk guidance — with three responsible AI features built into the architecture:

📋 Source citation — every answer shows exactly which document and section it drew from
🎯 Confidence scoring — retrieval-adjusted, not just LLM self-reported
🔴 Human escalation — material compliance determinations trigger automatic human review

The third feature is the important one. An AI agent that knows when to stop and route to a human isn't a limited product — it's a trustworthy one.

Try it: [your Lovable URL]
Code: [your GitHub URL]

Built in a weekend. Feedback welcome from anyone working at the intersection of AI governance and enterprise deployment.

#ResponsibleAI #AgenticAI #GenAI #FinancialServices #AIGovernance #CanadianBanking #ProductManagement
---
