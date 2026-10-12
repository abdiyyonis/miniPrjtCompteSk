from fastapi import FastAPI
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Configuration DevOps : l'URL de la DB viendra de Docker plus tard
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/compteur_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle de la base de données
class Counter(Base):
    __tablename__ = "counters"
    key_name = Column(String, primary_key=True, index=True)
    click_count = Column(Integer, default=0)

# Création de la table
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.post("/click/{key_name}")
def register_click(key_name: str):
    if key_name not in ["space", "k"]:
        return {"error": "Touche non supportée"}
    
    db = SessionLocal()
    counter = db.query(Counter).filter(Counter.key_name == key_name).first()
    
    if counter:
        counter.click_count += 1
    else:
        counter = Counter(key_name=key_name, click_count=1)
        db.add(counter)
        
    db.commit()
    db.close()
    return {"status": "ok"}

@app.get("/stats")
def get_stats():
    db = SessionLocal()
    counters = db.query(Counter).all()
    db.close()
    return {c.key_name: c.click_count for c in counters}