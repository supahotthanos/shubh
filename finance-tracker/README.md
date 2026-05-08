# Finance Tracker

> 📱 **No-server option:** [`standalone.html`](./standalone.html) is a single-file
> version that runs entirely in your phone's browser. Save the file, tap to open,
> done. Same features (PDF parsing, categorization, recommendations, monthly slots,
> budgets, charts) — all client-side, all data in localStorage. Password is the
> same. See bottom of this README for how to get it onto your phone.



A personal finance app that ingests **Amex PDF statements**, categorizes every charge,
generates a spending report with **specific dollar-amount cut recommendations**, tracks
spending **month-by-month**, and lets you set **forward-looking budgets** suggested
from your trailing 3-month average.

## What it does

- **Upload an Amex PDF** → transactions are parsed, categorized, and stored under that
  month's slot. Re-uploading the same month replaces it cleanly.
- **Dashboard** for the selected month: totals, category breakdown (donut chart), top
  merchants, recurring charges, budget bars, and a recommendations panel.
- **Recommendations** are concrete and dollar-amount-specific — e.g.
  - *"Cut coffee runs in half, save ~$24.00/mo"* (8 Starbucks @ $6 avg)
  - *"You're $18.00 over budget on Coffee"*
  - *"Swap 1 Uber/Lyft per week for transit, save ~$43.70/mo"*
  - *"Audit $42.97/mo in subscriptions"* (lists detected recurring services)
  - *"You paid $12.50 in fees — call Amex"*
- **Monthly slots**: every uploaded statement gets its own month bucket (`YYYY-MM`).
  The month dropdown lets you switch between them.
- **Budget tab**: set a monthly limit per category. The app suggests a budget for
  each category from your trailing 3-month average + a 5% buffer.
- **Trends tab**: month-over-month total spend bars + per-category line chart so you
  can see where you're trending up or down.
- **Recategorize** any transaction inline if the auto-classifier guessed wrong; the
  dashboard updates immediately.

## Architecture

```
finance-tracker/
├── backend/                FastAPI app
│   ├── main.py             API endpoints + static frontend serving
│   ├── pdf_parser.py       Amex PDF → transactions (pdfplumber + regex)
│   ├── categorizer.py      Rule-based merchant → category
│   ├── insights.py         Report builder + recommendations engine
│   ├── db.py               SQLite schema + connection helper
│   ├── requirements.txt
│   └── run.sh
├── frontend/               Single-page app, vanilla JS + Chart.js
│   ├── index.html
│   ├── app.js
│   └── style.css
└── data/
    └── finance.db          (auto-created on first run)
```

**Storage:** SQLite. Three tables — `statements` (one per month), `transactions`,
`budgets` (one row per category).

## Auth

The whole app is gated by a single password. Default: **`Shubh2007$`**.

Override it (recommended once you deploy somewhere) with an env var before starting:

```bash
FINANCE_PASSWORD='your-new-password' ./run.sh
```

A signed session cookie (HMAC over a 30-day expiry) is set on successful login. The
HMAC secret is auto-generated at `data/secret.key` on first run and is git-ignored.
There's a small (250 ms) sleep on bad login attempts to slow brute force.

## Run it

```bash
cd finance-tracker/backend
./run.sh
```

The script creates a venv, installs deps, and starts uvicorn on
[http://localhost:8000](http://localhost:8000). Open that URL in your browser — the
frontend is served from the same FastAPI app.

First time:
1. Hit **Budget** tab and set monthly limits (or skip, you can set them later).
2. Drop your Amex PDF into the upload box on the top bar.
3. Look at **Dashboard** for the report and recommendations.
4. Upload next month's statement when it arrives — it lands in a new month slot.

## API

| Method | Path                                  | Purpose |
|--------|---------------------------------------|---------|
| POST   | `/api/upload?period=YYYY-MM`          | Upload Amex PDF (period optional, auto-detected from statement) |
| GET    | `/api/months`                         | List all uploaded months |
| GET    | `/api/months/{period}`                | Full report for a month |
| GET    | `/api/months/{period}/transactions`   | Raw transactions for a month |
| DELETE | `/api/months/{period}`                | Delete a month |
| PATCH  | `/api/transactions/{id}`              | Recategorize a transaction |
| GET    | `/api/budgets`                        | Get budgets + category list |
| PUT    | `/api/budgets`                        | Replace all budgets |
| GET    | `/api/budgets/projection`             | Suggested budgets from 3-month avg |
| GET    | `/api/trend`                          | Month-over-month per-category totals |

## Notes on the Amex parser

Amex PDFs vary by card product. The parser uses pdfplumber to extract text, then
applies a per-line regex of the form `MM/DD[/YY] DESCRIPTION AMOUNT` to capture
charges. It detects the statement period from the *Closing Date* header and falls
back to the most common transaction month. Credits/payments (trailing `-` or
"AUTOPAY PAYMENT") are stored with negative amounts.

If your statement layout doesn't parse cleanly, every transaction can still be
edited from the **Transactions** tab.

## `standalone.html` — phone-friendly, no server

The file `standalone.html` is the entire app in a single HTML file. It uses
[pdf.js](https://mozilla.github.io/pdf.js/) (loaded from a CDN) to parse Amex
PDFs in the browser, ports the categorizer + insights logic to JS, and persists
everything to `localStorage` on your device. Same login password.

**Three ways to get it onto your phone:**

1. **Download the file directly** — open
   [the raw file on GitHub](https://raw.githubusercontent.com/supahotthanos/shubh/claude/finance-tracker-app-9BotE/finance-tracker/standalone.html)
   on your phone (long-press → Save). Then open it from your Files / Downloads
   app. iOS Safari and Android Chrome both support file:// URLs.
2. **Email/AirDrop it to yourself** — clone this repo, AirDrop `standalone.html`
   to your phone, open from Files.
3. **GitHub Pages** — in this repo, enable Pages on the `claude/finance-tracker-app-9BotE`
   branch with folder `/finance-tracker`. You'll get a URL like
   `https://supahotthanos.github.io/shubh/standalone.html` that you can bookmark
   and "Add to Home Screen" — looks and feels like a native app.

**Limits of the standalone version:**
- Data lives only in that browser, on that device. Use Settings → Export JSON
  to back it up; Import JSON to restore.
- The "password" is in source — anyone who can read the HTML can see it. It's a
  soft lock to keep someone who picks up your phone out of the data, not real
  security.
- Needs internet on first load (to fetch pdf.js + Chart.js from CDN). After that
  it works offline since browsers cache the libs.
