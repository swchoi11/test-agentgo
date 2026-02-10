import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db, add_record
from google.cloud import pubsub_v1
import json


app = FastAPI()

project_id = os.getenv("PROJECT_ID")
INPUT_TOPIC_ID = os.getenv("INPUT_TOPIC_ID")
OUTPUT_TOPIC_ID = os.getenv("OUTPUT_TOPIC_ID")

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

pubs_path = publisher.topic_path(project_id, INPUT_TOPIC_ID)
subs_path = subscriber.subscription_path(project_id, OUTPUT_TOPIC_ID)


@app.post("/user")
async def simple_request(user_name: str, user_input: int, db: Session=Depends(get_db)):
    # vm으로 보낼 데이터
    message_data = {
        "user_name" : user_name,
        "user_input": user_input
    }

    data_bytes = json.dumps(message_data).encode("utf-8")
    future = publisher.publish(pubs_path, data=data_bytes)
    message_id = future.result()

    print(message_id)

    # 토픽에서 메시지 가져오기
    response = subscriber.pull(
        request={"subscription": subs_path, "max_messages":1},
        timeout=5.0
    )

    vm_output=None
    for msg in response.recieved_messages:
        vm_output = json.loads(msg.message.data.decode("utf-8"))
        subscriber.acknowledge(
            request={"subscription": subs_path, "ack_ids": [msg.ack_id]}
        )

    return {"vm_output": vm_output}






    # cloud sql에 저장
    add_record(user_name=user_name, user_input=user_input, db=db)
    

