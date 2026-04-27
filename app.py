from fastapi import FastAPI
from routes.chat_routes import router as chat_router
from routes.character_routes import router as character_routes

app = FastAPI(
    title="AI Girlfriend API",
    version="1.0"
)

app.include_router(chat_router)
app.include_router(character_routes)


@app.get("/")
def root():
    return {"message": "AI Girlfriend API Running"}