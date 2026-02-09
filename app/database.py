import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from google.cloud.sql.connector import Connector, IPTypes

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

project_id = os.getenv("PROJECT_ID")
region = os.getenv("REGION")
instance_name = os.getenv("INSTANCE_NAME")

connector = Connector()

def getconn():
    conn = connector.connect(
        f"{project_id}:{region}:{instance_name}",
        "pg8000",
        user=db_user,
        password=db_password,
        db=db_name,
        ip_type=IPTypes.PRIVATE
    )
    return conn

engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Test(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    user_input = Column(Integer)
    vm_output = Column(String)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_record(user_name: str, user_input: int, db: Session):

    try:
        new_record = Test(user_name=user_name, user_input=user_input)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except Exception as e:
        db.rollback()
        print(e)
        raise e

