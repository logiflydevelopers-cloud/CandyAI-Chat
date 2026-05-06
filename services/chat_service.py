from datetime import datetime
from bson import ObjectId

from database.mongo import db
from services.prompt_builder import build_character_prompt
from services.llm_service import chat
from services.posthog_client import capture_event

characters_collection = db["characters"]
usercharacters_collection = db["usercharacters"]   # NEW
sessions_collection = db["chat_sessions"]
conversations_collection = db["conversations"]
messages_collection = db["messages"]
tokens_collection = db["chat_tokens"]


def process_chat(user_id, character_id, user_message, message_doc_id):
    """
    Main chat handler
    """

    character_object_id = ObjectId(character_id)
    message_doc_object_id = ObjectId(message_doc_id)

    # =========================
    # Find or Create Session
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
    # Find Conversation
    # =========================

    conversation = conversations_collection.find_one({
        "sessionId": session_id
    })

    conversation_id = conversation["_id"] if conversation else None

    # =========================
    # Fetch Last Messages
    # =========================

    history = []

    if conversation_id:
        message_doc = messages_collection.find_one(
            {"conversationId": conversation_id},
            {"messages": {"$slice": -10}}
        )

        if message_doc:
            messages = message_doc.get("messages", [])

            history = [
                {
                    "role": "assistant" if msg["sender"] == "bot" else "user",
                    "content": msg["text"]
                }
                for msg in messages
            ]

    # =========================
    # Fetch Character
    # =========================

    # First try main characters collection
    character = characters_collection.find_one({
        "_id": character_object_id
    })

    # If not found, try user characters collection
    if not character:
        character = usercharacters_collection.find_one({
            "_id": character_object_id
        })

    # Still not found
    if not character:
        raise ValueError(f"Character not found: {character_id}")

    # =========================
    # Build System Prompt
    # =========================

    system_prompt = build_character_prompt(character)

    # =========================
    # Call LLM
    # =========================

    try:
        ai_reply, usage = chat(system_prompt, history, user_message)

        capture_event(
            user_id=user_id,
            event="gpt_usage",
            properties={
                "message_id": str(message_doc_object_id),
                "character_id": str(character_object_id),

                "prompt_tokens": usage["prompt_tokens"],
                "completion_tokens": usage["completion_tokens"],
                "total_tokens": usage["total_tokens"],

                "model": "gpt-4.1-mini",
                "feature": "chat",
                "status": "success"
            }
        )

    except Exception as e:
        capture_event(
            user_id=user_id,
            event="gpt_error",
            properties={
                "error": str(e),
                "feature": "chat"
            }
        )
        raise

    # =========================
    # Store Token Usage
    # =========================

    tokens_collection.update_one(
        {"messageId": message_doc_object_id},
        {
            "$inc": {
                "promptTokens": usage["prompt_tokens"],
                "completionTokens": usage["completion_tokens"],
                "totalTokens": usage["total_tokens"]
            },
            "$set": {
                "updatedAt": datetime.utcnow()
            },
            "$setOnInsert": {
                "userId": user_id,
                "characterId": character_object_id,
                "createdAt": datetime.utcnow()
            }
        },
        upsert=True
    )

    # =========================
    # Update Session Timestamp
    # =========================

    sessions_collection.update_one(
        {"_id": session_id},
        {"$set": {"lastMessageAt": datetime.utcnow()}}
    )

    return ai_reply