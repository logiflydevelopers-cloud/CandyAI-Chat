from datetime import datetime
from bson import ObjectId

from database.mongo import db
from services.prompt_builder import build_character_prompt
from services.llm_service import chat


characters_collection = db["characters"]
sessions_collection = db["chat_sessions"]
messages_collection = db["messages"]
tokens_collection = db["tokens"]


def process_chat(user_id, character_id, user_message):
    """
    Main chat handler
    """

    # Convert character_id to ObjectId
    character_object_id = ObjectId(character_id)

    # =========================
    # 1️⃣ Find or Create Session
    # =========================

    session = sessions_collection.find_one({
        "userId": user_id,
        "characterId": character_object_id
    })

    if not session:

        session_data = {
            "userId": user_id,
            "characterId": character_object_id,
            "createdAt": datetime.utcnow(),
            "lastMessageAt": datetime.utcnow()
        }

        result = sessions_collection.insert_one(session_data)
        session_id = result.inserted_id

    else:
        session_id = session["_id"]

    # =========================
    # 2️⃣ Fetch Last Messages
    # =========================

    history_cursor = messages_collection.find(
        {"sessionId": session_id}
    ).sort("createdAt", -1).limit(20)

    history = [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in reversed(list(history_cursor))
    ]

    # =========================
    # 3️⃣ Fetch Character
    # =========================

    character = characters_collection.find_one({
        "_id": character_object_id
    })

    if not character:
        raise ValueError(f"Character not found: {character_id}")

    # =========================
    # 4️⃣ Build System Prompt
    # =========================

    system_prompt = build_character_prompt(character)

    # =========================
    # 5️⃣ Call LLM
    # =========================

    ai_reply, usage = chat(system_prompt, history, user_message)

    # =========================
    # 6️⃣ Store Token Usage
    # =========================

    tokens_collection.update_one(
    {"messageId": session_id},
    {
        "$inc": {
            "promptTokens": usage["prompt_tokens"],
            "completionTokens": usage["completion_tokens"],
            "totalTokens": usage["total_tokens"]
        },
        "$set": {"updatedAt": datetime.utcnow()},
        "$setOnInsert": {
            "userId": user_id,
            "characterId": character_object_id,
            "createdAt": datetime.utcnow()
        }
    },
    upsert=True
)
    # =========================
    # 7️⃣ Update Session Timestamp
    # =========================

    sessions_collection.update_one(
        {"_id": session_id},
        {"$set": {"lastMessageAt": datetime.utcnow()}}
    )

    return ai_reply