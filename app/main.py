import os
from fastapi import FastAPI
from database import add_record
from database import Base, engine
from dotenv import load_dotenv
from google.cloud import pubsub_v1
import json


load_dotenv()

app = FastAPI()

project_id = os.getenv("PROJECT_ID")
topic_id = os.getenv("TOPIC_ID")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

@app.post("/user")
async def simple_request(user_name: str, number: int):
    # vm으로 보낼 데이터
    message_data = {
        "user_name" : user_name,
        "user_input": number
    }

    data_bytes = json.dumps(message_data).encode("utf-8")

    # 토픽에 메시지 게시
    future = publisher.publish(topic_path, data=data_bytes)

    # 결과 확인
    message_id = future.result()

    print(message_id)

    # cloud sql에 저장
    Base.metadata.create_all(bind=engine)
    new_record = add_record(user_name=user_name, user_input=number)
    return {"new_record": new_record}