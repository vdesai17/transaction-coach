# sqlalchemy is the python library that lets us talk to postgres
# without writing raw sql strings
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
import os

# address of our postgres database running locally
# format is: postgresql://host/database_name
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/transaction_coach")

# engine is the actual connection to postgres
# think of it like opening a phone line to the database
# doesnt connect until we actually run a query
engine = create_engine(DATABASE_URL)

# session factory - we use this to create database sessions
# each session is one conversation with the database
# autocommit=False means changes dont save until we call db.commit()
# autoflush=False means dont auto send queries before commit
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class that all our table classes inherit from
# tells sqlalchemy these classes represent database tables
Base = declarative_base()


# users table - one row per registered user
class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)  # auto increments
    email      = Column(String, unique=True, index=True, nullable=False)  # must be unique
    password   = Column(String, nullable=False)  # stored as bcrypt hash never plain text
    created_at = Column(DateTime, default=datetime.utcnow)  # auto set on creation

    # lets us do user.transactions to get all their transactions
    # back_populates links both sides of the relationship
    transactions = relationship("Transaction", back_populates="user")


# transactions table - one row per classified transaction
class Transaction(Base):
    __tablename__ = "transactions"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)  # links to users table
    description = Column(String, nullable=False)   # e.g. "Tim Hortons"
    amount      = Column(Float, nullable=False)    # e.g. -4.50
    category    = Column(String, nullable=False)   # e.g. "Dining and Cafes"
    created_at  = Column(DateTime, default=datetime.utcnow)

    # lets us do transaction.user to get the user who owns it
    user = relationship("User", back_populates="transactions")


# corrections table - stores every time a user fixes a wrong category
# this is our feedback loop data for retraining the model later
class Correction(Base):
    __tablename__ = "corrections"

    id                 = Column(Integer, primary_key=True, index=True)
    user_id            = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_id     = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    original_category  = Column(String, nullable=False)   # what model said
    corrected_category = Column(String, nullable=False)   # what user said it actually is
    created_at         = Column(DateTime, default=datetime.utcnow)


# reads all the classes above and creates the actual tables in postgres
# safe to call multiple times - only creates tables if they dont exist
def init_db():
    Base.metadata.create_all(bind=engine)