from database.mongo import characters_collection


def get_all_characters():
    return list(characters_collection.find())


def get_character_by_id(uniqueId):
    return characters_collection.find_one({"uniqueId": uniqueId})