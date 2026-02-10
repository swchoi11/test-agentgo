import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db, add_record
from google.cloud import pubsub_v1
import json


app = FastAPI()

project_id = os.getenv("PROJECT_ID")
INPUT_TOPIC_ID = os.getenv("INPUT_TOPIC_ID")
OUTPUT_SUBS_ID = os.getenv("OUTPUT_SUBS_ID")

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

pubs_path = publisher.topic_path(project_id, INPUT_TOPIC_ID)
subs_path = subscriber.subscription_path(project_id, OUTPUT_SUBS_ID)


@app.post("/user")
async def simple_request(user_name: str, user_input: int, db: Session=Depends(get_db)):
    # cloud sql에 저장
    new_record = add_record(
        user_name=user_name,
        user_input=user_input,
        vm_output=None,
        db=db
    )
    
    # Pub/Sub 메시지 게시
    message_data = {
        "db_id": new_record.id,
        "user_name" : user_name,
        "user_input": user_input
    }
    data_bytes = json.dumps(message_data).encode("utf-8")
    publisher.publish(pubs_path, data=data_bytes)
    
    return {"status": "processing", "db_id": new_record.id}