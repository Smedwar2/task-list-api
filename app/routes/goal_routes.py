from flask import Blueprint, request, jsonify
from ..models.goal import Goal
from ..db import db
from .route_utilities import get_model_by_id
from ..models.task import Task

goal_bp = Blueprint("goals", __name__)

@goal_bp.post("/goals")
def create_goal():
    goal_data = request.json

    if not goal_data or "title" not in goal_data:
        return jsonify({"details": "Invalid data"}), 400

    new_goal = Goal.from_dict(goal_data)
    db.session.add(new_goal)
    db.session.commit()

    return jsonify(new_goal.to_dict()), 201


@goal_bp.get("/goals")
def get_all_goals():
    goals = db.session.query(Goal).all()
    goals_list = [goal.to_dict() for goal in goals]
    return goals_list    

@goal_bp.get("/goals/<int:goal_id>")
def get_one_goal(goal_id):
    goal = get_model_by_id(Goal, goal_id)

    if goal is None:
        return {"details": "Goal not found"}, 404

    return goal.to_dict()

@goal_bp.get("/goals/<int:goal_id>/tasks")
def get_tasks_for_goal(goal_id):
    goal = get_model_by_id(Goal, goal_id)

    if goal is None:
        return {"details": "Goal not found"}, 404

    goal_dict = goal.to_dict()
    goal_dict["tasks"] = []

    for task in goal.tasks:
        task_dict = task.to_dict()
        task_dict["goal_id"] = task.goal_id
        goal_dict["tasks"].append(task_dict)

    return goal_dict

@goal_bp.post("/goals/<int:goal_id>/tasks")
def add_tasks_to_goal(goal_id):
    goal = get_model_by_id(Goal, goal_id)

    if goal is None:
        return {"details": "Goal not found"}, 404

    task_data = request.get_json()

    if not task_data or not isinstance(task_data.get("task_ids"), list):
        return {"details": "Invalid data"}, 400

    task_ids = task_data["task_ids"]

    tasks = []

    for task_id in task_ids:
        task = get_model_by_id(Task, task_id)

        if task is None:
            return {"details": "Task not found"}, 404

        tasks.append(task)
    goal.tasks = tasks
    db.session.commit()

    return {"id": goal.id, "task_ids": task_ids}, 200


@goal_bp.put("/goals/<int:goal_id>")
def update_goal(goal_id):
    goal = get_model_by_id(Goal, goal_id)

    if goal is None:
        return {"details": "Goal not found"}, 404

    goal_data = request.json
    goal.title = goal_data["title"]

    db.session.commit()

    return "", 204, {"Content-Type": "application/json"}

@goal_bp.delete("/goals/<int:goal_id>")
def delete_goal(goal_id):
    goal = get_model_by_id(Goal, goal_id)

    if goal is None:
        return {"details": "Goal not found"}, 404

    db.session.delete(goal)
    db.session.commit()

    return "", 204, {"Content-Type": "application/json"}