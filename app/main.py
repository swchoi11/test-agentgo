from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def get_status():
    return {"status": "healthy"}

@app.get("/new")
def get_new_endpoint():
    return {"status": "new!!!"}