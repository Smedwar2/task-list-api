from .db import db

def get_model_by_id(model, model_id):
    return db.session.get(model, model_id)