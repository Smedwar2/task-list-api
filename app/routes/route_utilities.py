from flask import abort, jsonify
from ..db import db

def get_model_by_id(model, model_id):
    return db.session.get(model, model_id)

def validate_model(model, model_id):
    if not isinstance(model_id, int):
        abort(400, description="Invalid id")

    model_instance = get_model_by_id(model, model_id)

    if model_instance is None:
        response = jsonify({"details": f"{model.__name__} not found"})
        response.status_code = 404
        abort(response)

    return model_instance

def create_model(model, request_body):
    if not request_body or "title" not in request_body:
        response = jsonify({"details": "Invalid data"})
        response.status_code = 400
        abort(response)

    new_model = model.from_dict(request_body)
    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201