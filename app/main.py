from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from models import UserLogin 
from auth import verify_password, create_access_token 
import os
from fastapi import File, UploadFile
from auth import get_current_user
from models import Document
from database import engine, Base, get_db
from models import User, UserCreate
from auth import hash_password
from models import SearchQuery 
from rag import search_documents 


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Financial Document Assignment API"
)

@app.get("/")
def root():
    return {"message": "API started"}


@app.post("/auth/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already present")
        
    try:
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hash_password(user.password)
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"message": "User added successfully"}
        
    except Exception as e:
        db.rollback()
        print("Error saving user:", e) # print error to console for debugging
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/auth/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    
    db_user = db.query(User).filter(User.email == form_data.username).first()
    
  
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
  
    access_token = create_access_token(data={"sub": db_user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


if not os.path.exists("uploads"):
    os.makedirs("uploads")

@app.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user) 
):
    
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

   
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # 3. Save the record in the database
    db_doc = Document(
        filename=file.filename,
        uploaded_by=current_user_email
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    return {
        "message": "File uploaded successfully!", 
        "document_id": db_doc.id,
        "filename": file.filename
    }


from models import Document
from rag import process_and_store_document 

@app.post("/rag/index-document/{document_id}")
def index_document(document_id: int, db: Session = Depends(get_db)):
    
    
    db_doc = db.query(Document).filter(Document.id == document_id).first()
    
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")

  
    file_path = f"uploads/{db_doc.filename}"

    try:
        num_chunks = process_and_store_document(file_path, document_id)
        return {
            "message": "Success! Document saved to Vector DB.",
            "chunks_created": num_chunks
        }
    except Exception as e:
        print("Error processing PDF for AI:", e)
        raise HTTPException(status_code=500, detail="Failed to process document")
    


@app.post("/rag/search")
def search_financial_documents(
    search: SearchQuery, 
    current_user_email: str = Depends(get_current_user)
):
    try:
       
        relevant_chunks = search_documents(search.query)
        
        return {
            "search_query": search.query,
            "results_found": len(relevant_chunks),
            "top_results": relevant_chunks
        }
    except Exception as e:
        print("Error during search:", e)
        raise HTTPException(status_code=500, detail="Failed to search the documents")