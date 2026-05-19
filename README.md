# Finsnap

A full-stack web app that classifies bank transactions into spending categories using machine learning. Built on real transaction classification work done during a Bank Muscat internship, extended to support both Canadian and GCC merchants.

**Live demo:** [transaction-coach.vercel.app](https://transaction-coach.vercel.app)

---

## What It Does

- Paste a transaction description and amount — the ML model classifies it into a spending category instantly
- Upload a CSV of transactions to classify them all at once
- See a spending breakdown chart that updates in real time
- Accounts are personal — your transaction history persists across sessions
- Click any category badge to correct a misclassification — corrections are logged for future model retraining

---

## Tech Stack

**Frontend**
- React + Vite
- Recharts for the spending breakdown chart
- Papa Parse for CSV parsing
- Axios for API calls

**Backend**
- Python FastAPI
- JWT authentication with python-jose and bcrypt
- SQLAlchemy ORM

**Database**
- PostgreSQL

**Machine Learning**
- Scikit-learn MLP Classifier
- TF-IDF word and character n-gram features (3-5)
- Custom merchant lexicon features for GCC and Canadian merchants
- Trained on 30,000 synthetic transactions across 22 spending categories

**Deployment**
- Frontend: Vercel
- Backend + Database: Railway

---

## ML Model

The classification pipeline combines three feature types:

1. **Lexicon features** — custom merchant dictionaries built from real GCC and Canadian banking data. Counts unigram and bigram matches per category
2. **TF-IDF word n-grams** — captures transaction description patterns across 3-5 word sequences
3. **TF-IDF char n-grams** — captures character-level patterns useful for abbreviated merchant names
4. **Scaled transaction amount** — normalized absolute amount as an additional signal

The MLP achieves ~95% accuracy on test data and ~91% on out-of-sample merchants.

The feedback loop stores every user correction in a `corrections` table. These corrections can be used as additional training data to retrain the model and improve accuracy over time.

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

Requires a local PostgreSQL database:

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

Upload a CSV with these two columns:

```csv
description,amount
Tim Hortons,-4.50
Loblaws,-67.20
Toronto Hydro,-94.00
```

Negative amounts are expenses. The app handles both GCC merchants (Lulu Hypermarket, Ooredoo, Oman Air) and Canadian merchants (Tim Hortons, TTC, Rogers).

---

## Spending Categories

Groceries, Dining and Cafes, Shopping & Retail, Fuel and Transport, Housing and Utilities, Telecom, Medical and Health, Education, Entertainment and Leisure, Travel and Hotels, Bank Charges, Insurance, Savings and Investments, Loan Payments, Rent Payments, Charity Donations, Salary / Payroll, Other / Uncategorized

---

## Background

The ML model was originally built during a Business Intelligence internship at Bank Muscat (Summer 2025) to classify retail banking transactions for a Personal Finance Management tool. This project takes that work further — productionizing the model as a REST API and building a full-stack product on top of it.

---

## Project Structure

```
transaction-coach/
├── client/                  # React frontend
│   ├── src/
│   │   ├── pages/Auth.jsx   # Login / register screen
│   │   ├── services/api.js  # All API calls
│   │   ├── App.jsx          # Main app component
│   │   └── App.css          # Styles
│   └── .env                 # API URL config
└── server/                  # FastAPI backend
    ├── main.py              # Routes and ML pipeline
    ├── auth.py              # JWT auth helpers
    ├── database.py          # SQLAlchemy models
    ├── models/              # Saved ML artifacts
    └── data/                # Training data
```
