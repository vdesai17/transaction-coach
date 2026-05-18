from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import re
from sqlalchemy.orm import Session
from database import SessionLocal, User, Transaction, Correction, init_db
from auth import hash_password, verify_password, create_token, get_current_user, get_db

app = FastAPI()

# allow React frontend to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# create database tables on startup if they don't exist
init_db()

# load model artifacts once on startup
model = joblib.load("models/model.joblib")
word_vectorizer = joblib.load("models/word_vec.joblib")
char_vectorizer = joblib.load("models/char_vec.joblib")
scaler = joblib.load("models/scaler.joblib")
lexicons = joblib.load("models/lexicons.joblib")

# ── Helper functions ─────────────────────────────────────────────────

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_bigrams(tokens):
    return [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)]

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

# ── Request schemas ──────────────────────────────────────────────────

class TransactionRequest(BaseModel):
    description: str
    amount: float

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class CorrectionRequest(BaseModel):
    transaction_id: int
    corrected_category: str

# ── Auth endpoints ───────────────────────────────────────────────────

@app.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    # check if email already exists
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # create new user with hashed password
    user = User(email=body.email, password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    # return a token so user is logged in immediately after registering
    return {"token": create_token(user.id), "email": user.email}

@app.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    # find user by email
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # return JWT token
    return {"token": create_token(user.id), "email": user.email}

# ── Routes ───────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Transaction Coach API is running"}

@app.post("/predict")
def predict(transaction: TransactionRequest):
    # no auth required — anyone can classify
    desc = transaction.description
    amt = transaction.amount
    cleaned = clean_text(desc)
    row_df = pd.DataFrame([{"cleaned_description": cleaned, "abs_amount": abs(amt)}])
    X_lex = extract_features(row_df, lexicons)
    X_word = pd.DataFrame(word_vectorizer.transform([cleaned]).toarray(), columns=word_vectorizer.get_feature_names_out())
    X_char = pd.DataFrame(char_vectorizer.transform([cleaned]).toarray(), columns=char_vectorizer.get_feature_names_out())
    X_amt = pd.DataFrame(scaler.transform(row_df[["abs_amount"]]), columns=["abs_amount"])
    X = pd.concat([X_lex.reset_index(drop=True), X_word.reset_index(drop=True), X_char.reset_index(drop=True), X_amt.reset_index(drop=True)], axis=1)
    pred = model.predict(X)
    return {"category": pred[0]}

@app.post("/transactions")
def save_transaction(transaction: TransactionRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # classify the transaction
    desc = transaction.description
    amt = transaction.amount
    cleaned = clean_text(desc)
    row_df = pd.DataFrame([{"cleaned_description": cleaned, "abs_amount": abs(amt)}])
    X_lex = extract_features(row_df, lexicons)
    X_word = pd.DataFrame(word_vectorizer.transform([cleaned]).toarray(), columns=word_vectorizer.get_feature_names_out())
    X_char = pd.DataFrame(char_vectorizer.transform([cleaned]).toarray(), columns=char_vectorizer.get_feature_names_out())
    X_amt = pd.DataFrame(scaler.transform(row_df[["abs_amount"]]), columns=["abs_amount"])
    X = pd.concat([X_lex.reset_index(drop=True), X_word.reset_index(drop=True), X_char.reset_index(drop=True), X_amt.reset_index(drop=True)], axis=1)
    pred = model.predict(X)
    category = pred[0]

    # save to database tied to this user
    t = Transaction(
        user_id=current_user.id,
        description=desc,
        amount=amt,
        category=category
    )
    db.add(t)
    db.commit()
    db.refresh(t)

    return {"id": t.id, "category": category, "description": desc, "amount": amt}

@app.get("/transactions")
def get_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # get all transactions for the logged in user
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return [{"id": t.id, "description": t.description, "amount": t.amount, "category": t.category, "created_at": t.created_at} for t in transactions]

@app.post("/feedback")
def submit_feedback(body: CorrectionRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # find the transaction
    transaction = db.query(Transaction).filter(
        Transaction.id == body.transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # save the correction
    correction = Correction(
        user_id=current_user.id,
        transaction_id=body.transaction_id,
        original_category=transaction.category,
        corrected_category=body.corrected_category
    )
    db.add(correction)

    # update the transaction's category to the corrected one
    transaction.category = body.corrected_category
    db.commit()

    return {"message": "Correction saved", "new_category": body.corrected_category}