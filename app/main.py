import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db, add_record
from google.cloud import pubsub_v1
import json


app = FastAPI()

project_id = os.getenv("PROJECT_ID")
topic_id = os.getenv("TOPIC_ID")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

@app.post("/user")
async def simple_request(user_name: str, user_input: int, db: Session=Depends(get_db)):
    # vm으로 보낼 데이터
    message_data = {
        "user_name" : user_name,
        "user_input": user_input
    }

    data_bytes = json.dumps(message_data).encode("utf-8")

    # 토픽에 메시지 게시
    future = publisher.publish(topic_path, data=data_bytes)

    # 결과 확인
    message_id = future.result()

    print(message_id)

    # cloud sql에 저장
    add_record(user_name=user_name, user_input=user_input)
    

