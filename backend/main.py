from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select, case, func
import schemas, models, crud
from database import SessionLocal, engine
from typing import List, Any
import chromadb
import logging
import shutil
import uuid
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import requests
import httpx
import os

models.Base.metadata.create_all(bind=engine)
embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name="text-embedding-ada-002")
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection_prompts = chroma_client.get_or_create_collection(name="Prompts", embedding_function=embedding_function)
collection_categories = chroma_client.get_collection(name="Categories", embedding_function=embedding_function)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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

def filter_chroma(results, threshold = 0.47):
    int_ids = [int(id_) for id_ in results["ids"][0]]
    distances = results["distances"][0]
    filtered_ids = [id_ for id_, distance in zip(int_ids, distances) if distance < threshold]

    return filtered_ids

@app.post("/arts/", response_model=schemas.Art)
async def create_art(prompt: str = Form(...), image: UploadFile = File(...), owner_id: int = Form(...), db: Session = Depends(get_db)): 
    file_extension = image.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    image_path = f"./images/{unique_filename}"

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    url_path = f"/images/{unique_filename}"
    db_art = models.Art(prompt=prompt, image=url_path, owner_id=owner_id)
    db.add(db_art)
    db.commit()
    db.refresh(db_art)

    collection_prompts.add(
        documents=[prompt],
        ids=[str(db_art.id)]
    )

    results = collection_categories.query(query_texts=[prompt], include=["distances", "documents"])
    print(results)
    filtered_ids = filter_chroma(results, 0.35)

    if(filtered_ids):
        associations = [{"art_id": db_art.id, "category_id": category_id} for category_id in filtered_ids]
        db.execute(models.art_categories.insert(), associations)
        db.commit()

    return db_art

@app.get("/arts/", response_model=List[schemas.Art])
async def read_arts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    arts = db.query(models.Art).offset(skip).limit(limit).all()
    return arts

@app.get("/search/", response_model=List[schemas.Art])
async def search_arts(query: str, db: Session = Depends(get_db)):
    results = collection_prompts.query(query_texts=[query], include=["distances"])  
    
    filtered_ids = filter_chroma(results)
    
    if not filtered_ids:
        return []
    order_case = case({id_: index for index, id_ in enumerate(filtered_ids)}, value=models.Art.id)
    arts = db.query(models.Art).filter(models.Art.id.in_(filtered_ids)).order_by(order_case).all()
    
    return arts

@app.post("/auth/google", response_model=schemas.User)
async def google_authenticate(
    access_token: str = Body(..., embed=True), 
    db: Session = Depends(get_db)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'})

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Google auth failed")

    google_user_info = response.json()
    
    user = db.query(models.User).filter(models.User.email == google_user_info["email"]).first()
    if user:
        user.google_id = google_user_info["id"]
        user.picture = google_user_info["picture"]
    else:
        user = models.User(
            email=google_user_info["email"],
            username=google_user_info["name"],
            picture=google_user_info["picture"],
            description="",
            google_id=google_user_info["id"],
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    return user

@app.get("/arts/dates/", response_model=List[str])
async def read_art_dates(db: Session = Depends(get_db)):
    art_dates = db.query(models.Art.date).all()
    print(art_dates)
    dates = [art_date[0].strftime("%Y-%m-%d %H:%M:%S") for art_date in art_dates]
    return dates

@app.get("/categories/top/", response_model=List[schemas.CategoryCount])
async def read_top_categories(db: Session = Depends(get_db)):
    categories_counts = (
        db.query(
            models.Category.name, 
            func.count(models.art_categories.c.art_id).label("count")
        )
        .join(models.art_categories, models.art_categories.c.category_id == models.Category.id)
        .group_by(models.Category.name)
        .order_by(func.count(models.art_categories.c.art_id).desc())
        .limit(10)
        .all()
    )

    categories = [category_count[0] for category_count in categories_counts]
    counts = [category_count[1] for category_count in categories_counts]

    response = [schemas.CategoryCount(name=category, count=count) for category, count in zip(categories, counts)]
    return response