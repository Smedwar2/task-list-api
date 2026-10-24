from flask import Blueprint, request, jsonify #organizes task routes into a blueprint
from ..models.task import Task #lets routes know about the Task model
from ..db import db #ask db for records



task_bp = Blueprint("tasks", __name__) #attaches routes to the blueprint, which is then registered in __init__.py

@task_bp.get("/tasks") #route getting all tasks, returns a list of dictionaries
def get_all_tasks():
    tasks = db.session.query(Task).all() #ask db for all tasks and store them in a variable to reuse later
    task_list = [task.to_dict() for task in tasks] #turn tasks from objects into a list of dictionaries using the to_dict method in the Task model
    return task_list #return response to the client as a list of dictionaries

@task_bp.post("/tasks")
def create_task():
    task_data = request.json #read request body and store it in a variable to reuse later
    if not task_data or "title" not in task_data or "description" not in task_data: #check if the request body is missing required fields
        return jsonify({"details": "Invalid data"}), 400 

    new_task = Task.from_dict(task_data) #create a new Task object using the from_dict method in the Task model
    db.session.add(new_task) #save task to db
    db.session.commit() #confirms the changes to the db
    
    return jsonify(new_task.to_dict()), 201 #return task as a dictionary with a 201 status code to indicate that the task was created successfully