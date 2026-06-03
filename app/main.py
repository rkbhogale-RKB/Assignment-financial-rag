from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from models import UserLogin 
from auth import verify_password, create_access_token 

from database import engine, Base, get_db
from models import User, UserCreate
from auth import hash_password

# create tables in the database when the app starts
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Financial Document Assignment API"
)

@app.get("/")
def root():
    return {"message": "API started"}


@app.post("/auth/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    
    # check if user already exists first
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    try:
        # hash the password before saving it to db
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hash_password(user.password)
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"message": "User registered successfully"}
        
    except Exception as e:
        db.rollback()
        print("Error saving user:", e) # print error to console for debugging
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.post("/auth/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    
    # 1. Look up the user by their email
    db_user = db.query(User).filter(User.email == user.email).first()
    
    # 2. Check if the user exists AND if the password matches the hashed one in the db
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    # 3. If they pass, create a token with their email inside it
    access_token = create_access_token(data={"sub": db_user.email})
    
    # 4. Give the token to the user
    return {"access_token": access_token, "token_type": "bearer"}