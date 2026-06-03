from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
# setting up bcrypt so passwords aren't stored in plain text
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

# A secret key to sign our tokens. In real life, put this in a .env file!
SECRET_KEY = "my_super_secret_beginner_key"
ALGORITHM = "HS256"

# ... (keep your existing hash_password and verify_password functions here) ...

def create_access_token(data: dict):
    # copy the data so we don't accidentally change the original
    to_encode = data.copy()
    
    # set the token to expire in 30 minutes so they have to log in again later
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    
    # create the actual JWT string
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt