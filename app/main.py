from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.db.database import engine, Base
from app.models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Financial Document Management API"
)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "API is running"}