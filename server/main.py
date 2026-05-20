# fastapi stuff
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# pydantic for defining what request bodies look like
from pydantic import BaseModel

from typing import Optional
from datetime import datetime

# ml stuff
import joblib
import pandas as pd
import numpy as np
import re

# sqlalchemy session type for type hints
from sqlalchemy.orm import Session

# our db models and init function
from database import SessionLocal, User, Transaction, Correction, init_db

# auth helpers
from auth import hash_password, verify_password, create_token, get_current_user, get_db

app = FastAPI()

# lets react on localhost:5173 talk to this server
# in production change allow_origins to your actual frontend url
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# creates tables in postgres if they dont exist yet
# safe to run every startup
init_db()

# load all ml artifacts once when server starts
# doing it here means we dont reload on every request which would be slow
model = joblib.load("models/model.joblib")
word_vectorizer = joblib.load("models/word_vec.joblib")
char_vectorizer = joblib.load("models/char_vec.joblib")
scaler = joblib.load("models/scaler.joblib")
lexicons = joblib.load("models/lexicons.joblib")

# LabelEncoder sorts classes alphabetically — reconstruct the mapping here
# so the integer predictions from the model map back to readable strings
LABEL_MAP = {
    0: "Bank Charges",
    1: "Business or Freelance Income",
    2: "Charity Donations",
    3: "Dining and Cafes",
    4: "Education",
    5: "Entertainment and Leisure",
    6: "Fuel and Transport",
    7: "Government Services",
    8: "Government Support and Pensions",
    9: "Groceries",
    10: "Home Goods and Furniture",
    11: "Housing and Utilities",
    12: "Insurance",
    13: "Loan Payments",
    14: "Medical and Health",
    15: "Other / Uncategorized",
    16: "Rent Payments",
    17: "Salary / Payroll",
    18: "Savings and Investments",
    19: "Shopping & Retail",
    20: "Telecom",
    21: "Travel and Hotels",
    22: "Vehicle Loans and Fines",
}

STOP_WORDS = {"the", "at", "in", "of", "to", "a", "an", "and", "or", "for", "on", "with", "by", "from", "is", "it", "its"}

def update_lexicon(description: str, category: str):
    if category not in lexicons:
        return
    cleaned = clean_text(description)
    tokens = [w for w in cleaned.split() if len(w) > 1 and w not in STOP_WORDS]
    bigrams = generate_bigrams(tokens)
    existing_uni = set(lexicons[category]["unigrams"])
    existing_bi = set(lexicons[category]["bigrams"])
    new_uni = [t for t in tokens if t not in existing_uni]
    new_bi = [b for b in bigrams if b not in existing_bi]
    lexicons[category]["unigrams"].extend(new_uni)
    lexicons[category]["bigrams"].extend(new_bi)
    if new_uni or new_bi:
        joblib.dump(lexicons, "models/lexicons.joblib")


# lowercases text and strips everything thats not letters numbers or spaces
# must match exactly what was done during training
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# takes a list of tokens and returns adjacent pairs
# e.g. ["tim", "hortons"] -> ["tim hortons"]
def generate_bigrams(tokens):
    return [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)]


# builds the lexicon feature columns from the merchants dictionary
# counts how many words/bigrams in the description match each category lexicon
# must run before passing to model - these are 46 of the 2047 features
def extract_features(df, lexicons):
    feature_rows = []
    for row in df.itertuples(index=False):
        cleaned_text = row.cleaned_description
        tokens = [word for word in cleaned_text.split() if len(word) > 1]
        bigrams = set(generate_bigrams(tokens))
        features = {}
        for category, lexicon in lexicons.items():
            features[f"{category}_uni"] = sum(1 for w in tokens if w in lexicon["unigrams"])
            features[f"{category}_bi"] = sum(1 for p in bigrams if p in lexicon["bigrams"])
        feature_rows.append(features)
    return pd.DataFrame(feature_rows)


# helper that runs the full ml pipeline on a description and amount
# used by both /predict and /transactions so we dont repeat the code
def run_pipeline(desc: str, amt: float) -> str:
    cleaned = clean_text(desc)
    row_df = pd.DataFrame([{"cleaned_description": cleaned, "abs_amount": abs(amt)}])
    X_lex  = extract_features(row_df, lexicons)
    X_word = pd.DataFrame(word_vectorizer.transform([cleaned]).toarray(), columns=word_vectorizer.get_feature_names_out())
    X_char = pd.DataFrame(char_vectorizer.transform([cleaned]).toarray(), columns=char_vectorizer.get_feature_names_out())
    X_amt  = pd.DataFrame(scaler.transform(row_df[["abs_amount"]]), columns=["abs_amount"])
    X = pd.concat([
        X_lex.reset_index(drop=True),
        X_word.reset_index(drop=True),
        X_char.reset_index(drop=True),
        X_amt.reset_index(drop=True)
    ], axis=1)
    return LABEL_MAP[model.predict(X)[0].item()]


# what a transaction request body looks like
class TransactionRequest(BaseModel):
    description: str
    amount: float
    date: Optional[str] = None  # optional date string e.g. "2026-05-18"

# what a register request body looks like
class RegisterRequest(BaseModel):
    email: str
    password: str

# what a login request body looks like
class LoginRequest(BaseModel):
    email: str
    password: str

# what a correction request body looks like
class CorrectionRequest(BaseModel):
    transaction_id: int
    corrected_category: str


# health check - just confirms server is running
@app.get("/")
def root():
    return {"status": "Transaction Coach API is running"}


# creates a new user account
# hashes password before storing - never stores plain text
# returns a jwt token so user is logged in immediately
@app.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=body.email, password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_token(user.id), "email": user.email}


# verifies email and password, returns jwt token if correct
# 401 if email not found or password wrong
@app.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": create_token(user.id), "email": user.email}


# classifies a transaction without saving - no auth needed
# used for quick testing or anonymous classification
@app.post("/predict")
def predict(transaction: TransactionRequest):
    category = run_pipeline(transaction.description, transaction.amount)
    return {"category": category}


# classifies AND saves a transaction to the database
# requires auth - token must be in Authorization header
# ties the transaction to the logged in user
@app.post("/transactions")
def save_transaction(
    transaction: TransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # run ml pipeline to get category
    category = run_pipeline(transaction.description, transaction.amount)

    transaction_date = None
    if transaction.date:
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                transaction_date = datetime.strptime(transaction.date.strip(), fmt)
                break
            except ValueError:
                continue

    # save to db with user id so we can load it back later
    t = Transaction(
        user_id=current_user.id,
        description=transaction.description,
        amount=transaction.amount,
        category=category,
        date=transaction_date
    )
    db.add(t)
    db.commit()
    db.refresh(t)  # reload from db to get the auto generated id

    return {
        "id": t.id,
        "category": category,
        "description": transaction.description,
        "amount": transaction.amount,
        "date": transaction_date.strftime("%Y-%m-%d") if transaction_date else None
    }


# returns all transactions for the logged in user
# filters by user_id so users only see their own data
@app.get("/transactions")
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return [
        {
            "id": t.id,
            "description": t.description,
            "amount": t.amount,
            "category": LABEL_MAP.get(int(t.category), t.category) if t.category and t.category.isdigit() else t.category,
            "date": t.date.strftime("%Y-%m-%d") if t.date else None,
            "created_at": t.created_at
        }
        for t in transactions
    ]


# saves a correction when user clicks wrong category
# logs original and corrected category for model retraining later
# also updates the transaction itself so ui shows correct category
@app.post("/feedback")
def submit_feedback(
    body: CorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # find the transaction - also checks it belongs to this user
    transaction = db.query(Transaction).filter(
        Transaction.id == body.transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # log the correction to corrections table
    # this data can be used to retrain the model later
    correction = Correction(
        user_id=current_user.id,
        transaction_id=body.transaction_id,
        original_category=transaction.category,
        corrected_category=body.corrected_category
    )
    db.add(correction)

    # update the transaction too so it shows the right category
    transaction.category = body.corrected_category
    db.commit()

    # immediately boost the corrected category's lexicon with tokens from this description
    # so the next classification of the same merchant gets the right answer
    try:
        update_lexicon(transaction.description, body.corrected_category)
    except Exception:
        pass  # lexicon update is best-effort; correction is already saved to DB

    return {"message": "Correction saved", "new_category": body.corrected_category}


@app.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    t = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.query(Correction).filter(Correction.transaction_id == transaction_id).delete()
    db.delete(t)
    db.commit()
    return {"message": "Deleted"}