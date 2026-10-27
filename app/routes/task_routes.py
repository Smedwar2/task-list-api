from flask import Blueprint, request, jsonify # organizes task routes into a blueprint
from ..models.task import Task # lets routes know about the Task model
from ..db import db # ask db for records
from .route_utilities import validate_model, create_model
from datetime import datetime
import os
import requests



task_bp = Blueprint("tasks", __name__) # attaches routes to the blueprint, which is then registered in __init__.py

@task_bp.get("/tasks") # register route getting all tasks, returns a list of dictionaries #flask connection to URL 
def get_all_tasks():

    sort_param = request.args.get("sort")

    if sort_param == "asc":
        tasks = db.session.query(Task).order_by(Task.title).all()
    elif sort_param == "desc":
        tasks = db.session.query(Task).order_by(Task.title.desc()).all()
    else:
        tasks = db.session.query(Task).all() # ask db for all tasks and store them in a variable to reuse later

    task_list = [task.to_dict() for task in tasks] # turn tasks from objects into a list of dictionaries using the to_dict method in the Task model
    return task_list # return response to the client as a list of dictionaries



@task_bp.get("/tasks/<int:task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    task_dict = task.to_dict()
    if task.goal_id is not None:
        task_dict["goal_id"] = task.goal_id
    return task_dict


@task_bp.post("/tasks")
def create_task():
    task_data = request.json
    if not task_data or "description" not in task_data:
        return jsonify({"details": "Invalid data"}), 400
    return create_model(Task, task_data)

@task_bp.put("/tasks/<int:task_id>")
def update_task(task_id): # update existing task by id, id makes id available in func
    task = validate_model(Task, task_id)# get task by id using helper function, returns None if not found
    
    task_data = request.json # gives info from the request body and stores it in a variable to reuse later
    task.title = task_data["title"] # replaces the title of the task with the new title from the request body
    task.description = task_data["description"] # replaces the description of the task with the new description from the request body
    db.session.commit() # confirms the changes to the db
    return "", 204, {"Content-Type": "application/json"}

@task_bp.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task) # tells db delete the task from the db
    db.session.commit()
    return "", 204, {"Content-Type": "application/json"}

@task_bp.patch("/tasks/<int:task_id>/mark_complete") # register route that accepts http patch requests to mark a task as complete using the task id as a parameter in the URL
def mark_complete_task(task_id): # receieves id
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now() # gives currebt time to the completed_at column in the db for the task with the given id
    slack_token = os.environ.get("SLACK_BOT_TOKEN") # get the slack token from the environment variable
    headers = {
    "Authorization": f"Bearer {slack_token}",
    "Content-Type": "application/json"
    } # authorizes slack to recieve the request and tells slack that the request body is in json format

    message_body = {
    "channel": "task-notifs",
    "text": f"Someone just completed the task {task.title}"
    } # creates a message to send to the slack channel with the task title

    db.session.commit() #confirms the changes to the db

# send message to slack channel using the requests library to make a POST request to the slack API with the message body and headers
    slack_response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers=headers,
        json=message_body
    )
    if not slack_response.json().get("ok"):
        print("Slack notification failed:", slack_response.json())

    return "", 204, {"Content-Type": "application/json"}

@task_bp.patch("/tasks/<int:task_id>/mark_incomplete")
def mark_incomplete_task(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None
    db.session.commit()
    return "", 204, {"Content-Type": "application/json"}