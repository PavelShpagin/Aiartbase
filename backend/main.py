from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select, case
import schemas, models, crud
from database import SessionLocal, engine
from typing import List, Any
import chromadb
import logging
import shutil
import uuid
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os

models.Base.metadata.create_all(bind=engine)
embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name="text-embedding-ada-002")
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="Prompts", embedding_function=embedding_function)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(debug = True)

app.mount("/images", StaticFiles(directory="images"), name="images")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/arts/", response_model=schemas.Art)
async def create_art(prompt: str = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db)): 
    file_extension = image.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    image_path = f"./images/{unique_filename}"

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    url_path = f"/images/{unique_filename}"
    db_art = models.Art(prompt=prompt, image=url_path)
    db.add(db_art)
    db.commit()
    db.refresh(db_art)

    collection.add(
        documents=[prompt],
        ids=[str(db_art.id)]
    )

    return db_art

@app.get("/arts/", response_model=List[schemas.Art])
async def read_arts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    arts = db.query(models.Art).offset(skip).limit(limit).all()
    return arts

@app.get("/search/", response_model=List[schemas.Art])
async def search_arts(query: str, db: Session = Depends(get_db)):
    # Perform the query
    results = collection.query(query_texts=[query], include=["distances"])  
    
    print(results)

    # Extract IDs and distances from the results
    int_ids = [int(id_) for id_ in results["ids"][0]]
    distances = results["distances"][0]  # Assuming distances are structured similarly
    
    # Filter IDs by distance threshold
    filtered_ids = [id_ for id_, distance in zip(int_ids, distances) if distance < 0.47]
    
    if not filtered_ids:
        # Return an empty list or suitable response if no IDs meet the threshold
        return []
    # Order and filter the SQLAlchemy query by the filtered IDs
    order_case = case({id_: index for index, id_ in enumerate(filtered_ids)}, value=models.Art.id)
    arts = db.query(models.Art).filter(models.Art.id.in_(filtered_ids)).order_by(order_case).all()
    
    return arts