from fastapi import FastAPI
from routes.chat_routes import router as chat_router

app = FastAPI(
    title="AI Girlfriend API",
    version="1.0"
)

app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "AI Girlfriend API Running"}