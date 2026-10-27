from flask import Blueprint, request
from ..models.goal import Goal
from ..db import db
from .route_utilities import validate_model, create_model
from ..models.task import Task

goal_bp = Blueprint("goals", __name__)

@goal_bp.post("/goals")
def create_goal():
    goal_data = request.json
    return create_model(Goal, goal_data)


@goal_bp.get("/goals")
def get_all_goals():
    goals = db.session.query(Goal).all()
    goals_list = [goal.to_dict() for goal in goals]
    return goals_list    

@goal_bp.get("/goals/<int:goal_id>")
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    return goal.to_dict()

@goal_bp.get("/goals/<int:goal_id>/tasks")
def get_tasks_for_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    goal_dict = goal.to_dict()
    goal_dict["tasks"] = []

    for task in goal.tasks:
        task_dict = task.to_dict()
        task_dict["goal_id"] = task.goal_id
        goal_dict["tasks"].append(task_dict)

    return goal_dict

@goal_bp.post("/goals/<int:goal_id>/tasks")
def add_tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.json

    if not request_body or "task_ids" not in request_body or not isinstance(request_body["task_ids"], list):
        return {"details": "Invalid data"}, 400

    task_ids = request_body["task_ids"]
    tasks = []

    for task_id in task_ids:
        task = validate_model(Task, task_id)
        tasks.append(task)

    goal.tasks = tasks
    db.session.commit()

    return {"id": goal.id, "task_ids": task_ids}, 200


@goal_bp.put("/goals/<int:goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    goal_data = request.json
    goal.title = goal_data["title"]
    db.session.commit()
    return "", 204, {"Content-Type": "application/json"}

@goal_bp.delete("/goals/<int:goal_id>")
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    db.session.delete(goal)
    db.session.commit()
    return "", 204, {"Content-Type": "application/json"}