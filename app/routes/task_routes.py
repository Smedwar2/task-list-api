from flask import Blueprint, request, jsonify #organizes task routes into a blueprint
from ..models.task import Task #lets routes know about the Task model
from ..db import db #ask db for records
from ..route_utilities import get_model_by_id



task_bp = Blueprint("tasks", __name__) #attaches routes to the blueprint, which is then registered in __init__.py

@task_bp.get("/tasks") #register route getting all tasks, returns a list of dictionaries #flask connection to URL 
def get_all_tasks():

    sort_param = request.args.get("sort")

    if sort_param == "asc":
        tasks = db.session.query(Task).order_by(Task.title).all()
    elif sort_param == "desc":
        tasks = db.session.query(Task).order_by(Task.title.desc()).all()
    else:
        tasks = db.session.query(Task).all() #ask db for all tasks and store them in a variable to reuse later

    task_list = [task.to_dict() for task in tasks] #turn tasks from objects into a list of dictionaries using the to_dict method in the Task model
    return task_list #return response to the client as a list of dictionaries


@task_bp.get("/tasks/<int:task_id>")
def get_one_task(task_id):
    task = get_model_by_id(Task, task_id) #helper function to get a task by id, returns None if not found
    if task is None:
        return {"details": "Task not found"}, 404
    return task.to_dict()


@task_bp.post("/tasks")
def create_task():
    task_data = request.json #read request body and store it in a variable to reuse later
    if not task_data or "title" not in task_data or "description" not in task_data: #check if the request body is missing required fields
        return jsonify({"details": "Invalid data"}), 400 

    new_task = Task.from_dict(task_data) #create a new Task object using the from_dict method in the Task model
    db.session.add(new_task) #save task to db
    db.session.commit() #confirms the changes to the db
    
    return jsonify(new_task.to_dict()), 201 #return task as a dictionary with a 201 status code to indicate that the task was created successfully

@task_bp.put("/tasks/<int:task_id>")
def update_task(task_id): #update existing task by id, id makes id available in func
    task = get_model_by_id(Task, task_id) #get task by id using helper function, returns None if not found
    if task is None:
        return {"details": "Task not found"}, 404
    
    task_data = request.json #gives info from the request body and stores it in a variable to reuse later
    task.title = task_data["title"] #replaces the title of the task with the new title from the request body
    task.description = task_data["description"] #replaces the description of the task with the new description from the request body
    db.session.commit() #confirms the changes to the db
    return "", 204, {"Content-Type": "application/json"}

@task_bp.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    task = get_model_by_id(Task, task_id) #get task by id using helper function, returns None if not found
    if task is None:
        return {"details": "Task not found"}, 404

    db.session.delete(task) #tells db delete the task from the db
    db.session.commit()
    return "", 204, {"Content-Type": "application/json"}