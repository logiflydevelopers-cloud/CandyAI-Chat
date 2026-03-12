from datetime import datetime
from bson import ObjectId

from database.mongo import db
from services.prompt_builder import build_character_prompt
from services.llm_service import chat


characters_collection = db["characters"]
sessions_collection = db["chat_sessions"]
conversations_collection = db["conversations"]
messages_collection = db["messages"]
tokens_collection = db["tokens"]


def process_chat(user_id, character_id, user_message):
    """
    Main chat handler
    """

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
    # 2️⃣ Find Conversation
    # =========================

    conversation = conversations_collection.find_one({
        "sessionId": session_id
    })

    if conversation:
        conversation_id = conversation["_id"]
    else:
        conversation_id = None

    # =========================
    # 3️⃣ Fetch Last Messages
    # =========================

    history = []
    message_doc_id = None

    if conversation_id:

        message_doc = messages_collection.find_one(
            {"conversationId": conversation_id},
            {"messages": {"$slice": -10}}   # fetch only last 10
        )

        if message_doc:

            message_doc_id = message_doc["_id"]
            messages = message_doc.get("messages", [])

            history = [
                {
                    "role": "assistant" if msg["sender"] == "bot" else "user",
                    "content": msg["text"]
                }
                for msg in messages
            ]

    # =========================
    # 4️⃣ Fetch Character
    # =========================

    character = characters_collection.find_one({
        "_id": character_object_id
    })

    if not character:
        raise ValueError(f"Character not found: {character_id}")

    # =========================
    # 5️⃣ Build System Prompt
    # =========================

    system_prompt = build_character_prompt(character)

    # =========================
    # 6️⃣ Call LLM
    # =========================

    ai_reply, usage = chat(system_prompt, history, user_message)

    # =========================
    # 7️⃣ Store Token Usage
    # =========================

    if message_doc_id:

        tokens_collection.update_one(
            {"messageId": message_doc_id},   # messages collection _id
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
    # 8️⃣ Update Session Timestamp
    # =========================

    sessions_collection.update_one(
        {"_id": session_id},
        {"$set": {"lastMessageAt": datetime.utcnow()}}
    )

    return ai_reply