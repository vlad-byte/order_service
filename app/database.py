import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models

site_packages_path = None
for path in sys.path:
    if 'site-packages' in path:
        site_packages_path = path
        break

if site_packages_path:
    print(f"Using site-packages: {site_packages_path}")



venv_path = "C:\\Users\\vl44e\\PycharmProjects\\datatest\\.venv\\Lib\\site-packages"
if venv_path not in sys.path:
    sys.path.append(venv_path)

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:123@localhost:5432/postgres"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    print("Сервис запущен")
except Exception as e:
    print(f"Ошибка запуска: {e}")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    models.Base.metadata.create_all(bind=engine)