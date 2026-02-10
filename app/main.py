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
    # 1. Pub/Sub 메시지 게시
    message_data = {
        "user_name" : user_name,
        "user_input": user_input
    }
    data_bytes = json.dumps(message_data).encode("utf-8")
    future = publisher.publish(pubs_path, data=data_bytes)
    message_id = future.result()

    # 2. 결과 구독 (Pull 방식)
    # 💡 주의: VM이 처리하는 속도보다 Pull이 빠르면 결과가 없을 수 있습니다.
    response = subscriber.pull(
        request={"subscription": subs_path, "max_messages": 1},
        timeout=5.0
    )

    vm_output_raw = None
    for msg in response.received_messages: # 오타 수정 완료
        vm_output_raw = json.loads(msg.message.data.decode("utf-8"))
        subscriber.acknowledge(
            request={"subscription": subs_path, "ack_ids": [msg.ack_id]}
        )

    # 3. Cloud SQL에 저장
    # vm_output_raw가 dict라면 문자열로 변환하여 저장 (DB 컬럼이 String인 경우)
    vm_output_str = json.dumps(vm_output_raw) if vm_output_raw else None
    
    add_record(
        user_name=user_name, 
        user_input=user_input, 
        vm_output=vm_output_str, # 쉼표 추가 및 변수명 정리
        db=db
    )
    
    return {"vm_output": vm_output_raw}



    

