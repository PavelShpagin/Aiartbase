from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select
import schemas, models, crud
from database import SessionLocal, engine
from typing import List, Any
import chromadb
import shutil
import uuid

models.Base.metadata.create_all(bind=engine)
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="Prompts")

app = FastAPI(debug = True)

app.mount("/images", StaticFiles(directory="images"), name="images")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/arts/", response_model=schemas.Art)
async def create_art(prompt: str = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db)): 
    # Generate a unique filename
    file_extension = image.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    image_path = f"./images/{unique_filename}"

    # Save the image to the filesystem
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Store a URL path in the Art model
    url_path = f"/images/{unique_filename}"
    db_art = models.Art(prompt=prompt, image=url_path)
    db.add(db_art)
    db.commit()
    db.refresh(db_art)

    # Add prompt to ChromaDB
    collection.add(
        documents=[prompt],
        ids=[str(db_art.id)]
    )

    return db_art

@app.get("/arts/", response_model=List[schemas.Art])
def read_arts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    arts = db.query(models.Art).offset(skip).limit(limit).all()
    return arts

@app.get("/search/", response_model=List[schemas.Art])
def search_arts(query: str, db: Session = Depends(get_db)):
    # Search in ChromaDB and get matching document IDs
    ids = collection.search(query)
    
    # Convert ids to integer list assuming they are stored as strings
    int_ids = [int(id_) for id_ in ids]
    
    # Query the Art table for matching IDs
    query = select(models.Art).where(models.Art.id.in_(int_ids))
    results = db.execute(query).scalars().all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No matching arts found")

    return results