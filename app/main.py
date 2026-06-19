from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from models import UserLogin 
from auth import verify_password, create_access_token 
import os
from fastapi import File, UploadFile
from auth import get_current_user
from models import Document,Role,Permission, RoleCreate, PermissionCreate, AssignPermission,AssignRole
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

@app.get("/documents")
def get_all_documents(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    #  Permission Check 

    allowed = False

    for role in current_user.roles:
        for permission in role.permissions:
            if permission.name == "view_document":
                allowed = True
                break

    if not allowed:
        raise HTTPException(status_code=403,detail="You don't have permission to view documents" )

    documents = db.query(Document).all()
    print(documents)

    return {
        "total_documents": len(documents),
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "uploaded_by": doc.uploaded_by
            }
            for doc in documents
        ]
    }

@app.post("/roles")
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db)
):

    existing_role = db.query(Role).filter(Role.name == role.name).first()

    if existing_role:
        raise HTTPException(status_code=400,detail="Role already exists")
    db_role = Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    return {
        "message": "Role created successfully",
        "role": db_role.name
    }

@app.post("/permissions")
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db)
):

    existing_permission = db.query(Permission).filter(Permission.name == permission.name).first()

    if existing_permission:
        raise HTTPException(status_code=400,detail="Permission already exists")

    db_permission = Permission(name=permission.name)

    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)

    return {
        "message": "Permission created successfully",
        "permission": db_permission.name
    }

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

@app.post("/assign-role")
def assign_role(
    data: AssignRole,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")

  
    role = db.query(Role).filter(Role.id == data.role_id ).first()

    if not role:
        raise HTTPException(status_code=404,detail="Role not found")

    if role in user.roles:
        raise HTTPException(status_code=400,detail="User already has this role")

    # create bridge
    user.roles.append(role)

    db.commit()

    return {
        "message": f"{role.name} assigned to {user.username}"
    }

@app.post("/assign-permission")
def assign_permission(
    data: AssignPermission,
    db: Session = Depends(get_db)
):

    role = db.query(Role).filter(Role.id == data.role_id).first()

    if not role:
        raise HTTPException(status_code=404,detail="Role not found")

    permission = db.query(Permission).filter(Permission.id == data.permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=404,
            detail="Permission not found"
        )

    role.permissions.append(permission)
    db.commit()

    return {
        "message": f"{permission.name} assigned to {role.name}"
    }

@app.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    #Permission Checker 
    allowed = False
    for role in current_user.roles:
        print(f"Checking role: {role.name}")
        for permission in role.permissions:
            print(f"Checking permission: {permission.name}")
            if permission.name == "upload_document":
                allowed = True
                break

    if not allowed:
        raise HTTPException(status_code=403,detail="You don't have upload permission" )

    #Validate PDF 

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400,detail="Only PDF files are allowed")

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    db_doc = Document(
        filename=file.filename,
        uploaded_by=current_user.email
    )

    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    return {
        "message": "File uploaded successfully",
        "document_id": db_doc.id,
        "filename": db_doc.filename,
        "uploaded_by": current_user.email
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


from rag import remove_document_embeddings

@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # Permission Check 
    allowed = False
    for role in current_user.roles:
        for permission in role.permissions:
            if permission.name == "delete_document":
                allowed = True
                break
    if not allowed:
        raise HTTPException(status_code=403,detail="You do not have permission")

    #search 
    db_doc = db.query(Document).filter(Document.id == document_id).first()
    if not db_doc:
        raise HTTPException(status_code=404,detail="Document not found")

    # Delete from chroma

    deleted_chunks = remove_document_embeddings(document_id)

    # Delete from database

    db.delete(db_doc)
    db.commit()

    # Delete pdf
    file_path = f"uploads/{db_doc.filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
    return {
        "message": "Document deleted successfully",
        "filename": db_doc.filename,
        "chunks_deleted": deleted_chunks
    }