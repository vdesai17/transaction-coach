
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import re

app = FastAPI()

# Allow React frontend to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model artifacts once on startup
model = joblib.load("models/model.joblib")
word_vectorizer = joblib.load("models/word_vec.joblib")
char_vectorizer = joblib.load("models/char_vec.joblib")
scaler = joblib.load("models/scaler.joblib")
lexicons = joblib.load("models/lexicons.joblib")

# Helper functions
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

# Define what the request body looks like
class Transaction(BaseModel):
    description: str
    amount: float

@app.get("/")
def root():
    return {"status": "Transaction Coach API is running"}

@app.post("/predict")
def predict(transaction: Transaction):
    desc = transaction.description
    amt = transaction.amount

    cleaned = clean_text(desc)

    row_df = pd.DataFrame([{
        "cleaned_description": cleaned,
        "abs_amount": abs(amt)
    }])

    X_lex = extract_features(row_df, lexicons)
    X_word = pd.DataFrame(
        word_vectorizer.transform([cleaned]).toarray(),
        columns=word_vectorizer.get_feature_names_out()
    )
    X_char = pd.DataFrame(
        char_vectorizer.transform([cleaned]).toarray(),
        columns=char_vectorizer.get_feature_names_out()
    )
    X_amt = pd.DataFrame(
        scaler.transform(row_df[["abs_amount"]]),
        columns=["abs_amount"]
    )

    X = pd.concat([
        X_lex.reset_index(drop=True),
        X_word.reset_index(drop=True),
        X_char.reset_index(drop=True),
        X_amt.reset_index(drop=True)
    ], axis=1)

    pred = model.predict(X)
    return {"category": pred[0]}