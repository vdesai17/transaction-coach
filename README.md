# Finsnap

**Automatically categorize your bank transactions using machine learning.**

Paste a transaction or upload a CSV — Finsnap classifies it into a spending category instantly, builds your spending breakdown, and learns from your corrections over time.

**Live demo:** https://finsnap-six.vercel.app

---

## The Problem

Bank statements are a wall of raw text. "LULU HYPERMARKET 0042 MUSCAT" and "TTC PRESTO TORONTO" tell you nothing about where your money actually went. Finsnap reads those descriptions and turns them into meaningful categories — Groceries, Dining, Transport, Rent — so you can see your spending at a glance.

---

## Features

- **Instant classification** — paste any transaction description and amount, get a category in under a second
- **CSV bulk upload** — classify an entire month of transactions at once
- **Live spending chart** — donut chart and monthly trend bar chart update as you add transactions
- **Month filter** — switch between months to compare spending
- **Correction loop** — click any category to correct it; the model learns from corrections immediately and can be fully retrained on demand
- **Personal accounts** — JWT authentication, your transaction history persists across sessions

---

## How the ML Works

The classifier combines four feature types per transaction:

1. **Merchant lexicons** — custom dictionaries of 3,333 merchants across Oman and Canada, built from real GCC and Canadian banking data. Each description is scored against unigram and bigram match counts per category.
2. **TF-IDF word n-grams** — captures word-level patterns in transaction descriptions (e.g. "tim hortons", "lulu hypermarket")
3. **TF-IDF character n-grams** — handles abbreviated and inconsistently formatted merchant names at the character level
4. **Scaled transaction amount** — the absolute amount is a meaningful signal (e.g. a $4 charge is rarely rent)

These features feed into a two-layer **MLP Classifier** (512 → 256 hidden units) trained on **30,000 synthetic transactions** across **23 spending categories**.

**Results:** 88% weighted F1 on the test set, 86% on validation.

### Feedback Loop

Two-tier learning from user corrections:

- **Instant (Option A):** When you correct a category, the merchant's tokens are immediately added to the right lexicon in memory. The very next classification of that merchant gets the corrected result — no retraining needed.
- **Full retrain (Option B):** Hit *Retrain Model* to re-fit the entire pipeline using the base training data plus all saved corrections (weighted 5× to ensure they stick). Runs as a background task — the model hot-swaps in memory when done.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React, Vite, Recharts, PapaParse, Axios |
| Backend | Python, FastAPI, SQLAlchemy, JWT auth |
| Database | PostgreSQL |
| ML | scikit-learn (MLPClassifier, TfidfVectorizer, StandardScaler, LabelEncoder) |
| Deployment | Vercel (frontend) · Railway (backend + database) |

---

## Background

The ML model was originally built during a **Business Intelligence internship at Bank Muscat (Summer 2025)** as part of a Personal Finance Management tool for retail banking customers. This project takes that work further — productionizing the model as a REST API, building a full-stack product on top of it, and adding a live feedback loop that lets the model improve from real user corrections.

---

## Running Locally

**Backend**

```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Requires PostgreSQL:

```bash
brew install postgresql@15
brew services start postgresql@15
createdb transaction_coach
```

**Frontend**

```bash
cd client
npm install
npm run dev
```

Create `client/.env`:

```
VITE_API_URL=http://127.0.0.1:8001
```

---

## CSV Format

```csv
description,amount,date
Tim Hortons,-4.50,2026-05-01
Loblaws,-67.20,2026-05-03
Toronto Hydro,-94.00,2026-05-05
```

Works with both GCC merchants (Lulu Hypermarket, Ooredoo, Oman Air) and Canadian merchants (Tim Hortons, TTC, Rogers). Date column is optional.

---

## Spending Categories

23 categories: Groceries · Dining and Cafes · Shopping & Retail · Home Goods and Furniture · Fuel and Transport · Housing and Utilities · Rent Payments · Telecom · Medical and Health · Education · Entertainment and Leisure · Travel and Hotels · Bank Charges · Insurance · Savings and Investments · Loan Payments · Vehicle Loans and Fines · Charity Donations · Government Services · Salary / Payroll · Business or Freelance Income · Government Support and Pensions · Other / Uncategorized

---

## Project Structure

```
transaction-coach/
├── client/                              # React frontend
│   └── src/
│       ├── pages/Auth.jsx               # Login / register
│       ├── services/api.js              # API calls
│       ├── App.jsx                      # Main app + charts
│       └── App.css                      # Styles
└── server/                              # FastAPI backend
    ├── main.py                          # Routes, ML pipeline, retrain logic
    ├── auth.py                          # JWT helpers
    ├── database.py                      # SQLAlchemy models
    ├── models/                          # Trained artifacts (loaded on startup)
    └── data/
        ├── multiple_var_testing.ipynb   # Training notebook
        └── transactions.csv             # 30k synthetic training transactions
```
