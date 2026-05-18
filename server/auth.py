from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal, User

# secret key for signing JWT tokens — change this in production
SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
# token expires after 7 days
ACCESS_TOKEN_EXPIRE_DAYS = 7

# bcrypt password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# tells FastAPI where to get the token from
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ── Password helpers ────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)
# ── JWT token helpers ───────────────────────────────────────────────

def create_token(user_id: int) -> str:
    # creates a JWT token with user_id and expiry
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> int:
    # decodes JWT token and returns user_id
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ── Database session helper ─────────────────────────────────────────

def get_db():
    # creates a database session, closes it when done
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Get current user from token ─────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # called on every protected route — returns the logged in user
    user_id = decode_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user