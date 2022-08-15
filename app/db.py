from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(
    "postgresql://postgres:password@host.docker.internal/fastapi_test",
    echo=True,
)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()
