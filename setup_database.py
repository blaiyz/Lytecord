from src.server import db

def delete_db():
    for collection in db.db.list_collection_names():
        db.db.drop_collection(collection)
        
def create_indexes():
    db.create_indexes()