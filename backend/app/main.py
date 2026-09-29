from fastapi import FastAPI

app = FastAPI(title="THE CLOCK IS RUNNING")

@app.get("/health")
def health():
    return {"status": "ok"}
