from flask import Blueprint #organizes task routes into a blueprint
from ..models.task import Task #lets routes know about the Task model
from ..db import db #ask db for records



task_bp = Blueprint("tasks", __name__) #attaches routes to the blueprint, which is then registered in __init__.py

@task_bp.get("/tasks") #route getting all tasks, returns a list of dictionaries
def get_all_tasks():
    tasks = db.session.query(Task).all() #ask db for all tasks and store them in a variable to reuse later
    task_list = [task.to_dict() for task in tasks] #turn tasks from objects into a list of dictionaries using the to_dict method in the Task model
    return task_list #return response to the client as a list of dictionaries