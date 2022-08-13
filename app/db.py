from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///fastapi.db", echo=True)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()
