from sqlalchemy.orm import Session
import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, username=user.username, password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_arts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Art).offset(skip).limit(limit).all()

def create_art(db: Session, art: schemas.ArtCreate):
    db_art = models.Art(image=art.image, prompt=art.prompt)
    db.add(db_art)
    db.commit()
    db.refresh(db_art)
    return db_art

def create_user_art(db: Session, art: schemas.ArtCreate, user_id: int):
    db_art = models.Art(**art.dict(), owner_id=user_id)
    db.add(db_art)
    db.commit()
    db.refresh(db_art)
    return db_art
