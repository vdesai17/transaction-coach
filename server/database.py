from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime

# connection string to your local postgres database
# database stored on machine disk, not in memory
DATABASE_URL = "postgresql://localhost/transaction_coach"

# create the engine — this is the connection to the database
# like phone line to the database, but doesn't actually connect until we use it
engine = create_engine(DATABASE_URL)

# session factory — used to talk to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for all database models
Base = declarative_base()

# ── Tables ──────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, index=True)
    email    = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # stored as bcrypt hash
    created_at = Column(DateTime, default=datetime.utcnow)

    # one user has many transactions
    transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String, nullable=False)
    amount      = Column(Float, nullable=False)
    category    = Column(String, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    user        = relationship("User", back_populates="transactions")

class Correction(Base):
    __tablename__ = "corrections"

    id                = Column(Integer, primary_key=True, index=True)
    user_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_id    = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    original_category = Column(String, nullable=False)
    corrected_category = Column(String, nullable=False)
    created_at        = Column(DateTime, default=datetime.utcnow)

# create all tables in the database
def init_db():
    Base.metadata.create_all(bind=engine)