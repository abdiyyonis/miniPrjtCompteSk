from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/compteur_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Modèles de Base de Données ---
class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    password = Column(String) # En vrai DevOps, on hacherait ce mot de passe !

class Counter(Base):
    __tablename__ = "counters"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, ForeignKey("users.username"))
    key_name = Column(String, index=True)
    click_count = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Modèle pour recevoir les requêtes JSON ---
class UserAuth(BaseModel):
    username: str
    password: str

# --- Routes API ---
@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.post("/register")
def register(user: UserAuth):
    db = SessionLocal()
    if db.query(User).filter(User.username == user.username).first():
        db.close()
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")
    new_user = User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.close()
    return {"message": "Compte créé ! Tu peux te connecter."}

@app.post("/login")
def login(user: UserAuth):
    db = SessionLocal()
    db_user = db.query(User).filter(User.username == user.username, User.password == user.password).first()
    db.close()
    if not db_user:
        raise HTTPException(status_code=400, detail="Identifiants incorrects")
    return {"username": db_user.username}

@app.post("/click/{key_name}")
def register_click(key_name: str, username: str = Header(None)):
    if not username or key_name not in ["space", "k"]:
        return {"error": "Invalide"}
    
    db = SessionLocal()
    counter = db.query(Counter).filter(Counter.key_name == key_name, Counter.username == username).first()
    if counter:
        counter.click_count += 1
    else:
        counter = Counter(username=username, key_name=key_name, click_count=1)
        db.add(counter)
    db.commit()
    db.close()
    return {"status": "ok"}

@app.get("/stats")
def get_stats(username: str = Header(None)):
    if not username:
        return {"space": 0, "k": 0}
    db = SessionLocal()
    counters = db.query(Counter).filter(Counter.username == username).all()
    db.close()
    stats = {"space": 0, "k": 0}
    for c in counters:
        stats[c.key_name] = c.click_count
    return stats

@app.post("/reset")
def reset_stats(username: str = Header(None)):
    db = SessionLocal()
    db.query(Counter).filter(Counter.username == username).delete()
    db.commit()
    db.close()
    return {"status": "ok"}