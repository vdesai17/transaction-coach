# jwt stuff for creating and reading tokens
from datetime import datetime, timedelta
from jose import JWTError, jwt

# passlib for hashing passwords with bcrypt
from passlib.context import CryptContext

# fastapi stuff for auth and error handling
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# sqlalchemy session type for type hints
from sqlalchemy.orm import Session

# our database connection and user model
from database import SessionLocal, User

# change this to something random and secret in production
# if someone gets this key they can forge tokens
SECRET_KEY = "your-secret-key-change-this"

# hashing algorithm used to sign the jwt
ALGORITHM = "HS256"

# how long before token expires and user needs to login again
ACCESS_TOKEN_EXPIRE_DAYS = 7

# sets up bcrypt as our password hashing algorithm
# deprecated="auto" means old hashes get upgraded automatically
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# tells fastapi to look for the token in the Authorization header
# format is: Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# takes a plain password and returns a bcrypt hash
# we slice to 72 chars because bcrypt has a max length
def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


# checks if a plain password matches a stored bcrypt hash
# returns True or False
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)


# creates a jwt token containing the user id and expiry time
# token looks like: eyJhbGci... (three base64 parts joined by dots)
def create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    # sub is short for subject - standard jwt field for who the token is about
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


# reads a jwt token and returns the user id inside it
# raises 401 if token is invalid or expired
def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# opens a database session and yields it to the route function
# yield means fastapi will close the session automatically when done
# this runs for every single request that needs db access
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# dependency that runs before any protected route
# reads token from header, decodes it, fetches user from db
# if anything fails it throws 401 and the route never runs
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user