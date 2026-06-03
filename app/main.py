from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# importing from our own files in the same folder
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