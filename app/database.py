import os
from sqlalchemy import create_engine, Column, Integer, String, Datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")

db_url = f"postgresql+pg8000://{db_user}:{db_password}@/{db_name}?unix_sock=/cloudsql/{instance_connection_name}/.s.PGSQL.5432"

engine = create_engine(db_url, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Test(Base):
    __tablename__ = "test"
    id = Column(Intger, primary_key=True, index=True)
    user_name = Column(String)
    user_input = Column(Integer)
    vm_output = Column(String)

def add_record(user_name: str, user_input: int):

    db = SessionLocal()
    try:
        new_record = Test(user_name=user_name, user_input=user_input)

        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except Exception as e:
        db.rollback()
        print(str(e))
    finally:
        db.close()

    