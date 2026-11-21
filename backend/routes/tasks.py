from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from extensions import db
from models import Task, Category
from schemas import TaskSchema, STATUSES, PRIORITIES

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")

EDITABLE_FIELDS = ("title", "description", "status", "priority", "due_date", "category_id")


def task_to_dict(t):
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "priority": t.priority,
        "due_date": t.due_date.isoformat() if t.due_date else None,
        "category": {"id": t.category.id, "name": t.category.name} if t.category else None,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }


def owns_category(user_id, category_id):
    if category_id is None:
        return True
    return Category.query.filter_by(id=category_id, user_id=user_id).first() is not None


def get_own_task(user_id, task_id):
    return Task.query.filter_by(id=task_id, user_id=user_id).first()


@tasks_bp.get("")
@jwt_required()
def list_tasks():
    user_id = int(get_jwt_identity())
    query = Task.query.filter_by(user_id=user_id)

    status = request.args.get("status")
    if status:
        if status not in STATUSES:
            return jsonify({"error": f"status must be one of {STATUSES}"}), 400
        query = query.filter_by(status=status)

    priority = request.args.get("priority")
    if priority:
        if priority not in PRIORITIES:
            return jsonify({"error": f"priority must be one of {PRIORITIES}"}), 400
        query = query.filter_by(priority=priority)

    category_id = request.args.get("category_id", type=int)
    if category_id is not None:
        query = query.filter_by(category_id=category_id)

    search = request.args.get("q", "").strip()
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([task_to_dict(t) for t in tasks]), 200


@tasks_bp.post("")
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    try:
        data = TaskSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if not owns_category(user_id, data.get("category_id")):
        return jsonify({"errors": {"category_id": ["Category not found."]}}), 400

    task = Task(
        user_id=user_id,
        title=data["title"].strip(),
        description=data.get("description"),
        status=data.get("status", "todo"),
        priority=data.get("priority", "medium"),
        due_date=data.get("due_date"),
        category_id=data.get("category_id"),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task_to_dict(task)), 201


@tasks_bp.get("/<int:task_id>")
@jwt_required()
def get_task(task_id):
    user_id = int(get_jwt_identity())
    task = get_own_task(user_id, task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404
    return jsonify(task_to_dict(task)), 200


@tasks_bp.put("/<int:task_id>")
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    task = get_own_task(user_id, task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404

    try:
        data = TaskSchema(partial=True).load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if "category_id" in data and not owns_category(user_id, data["category_id"]):
        return jsonify({"errors": {"category_id": ["Category not found."]}}), 400

    for field in EDITABLE_FIELDS:
        if field in data:
            setattr(task, field, data[field])
    if "title" in data:
        task.title = data["title"].strip()

    db.session.commit()
    return jsonify(task_to_dict(task)), 200


@tasks_bp.delete("/<int:task_id>")
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())
    task = get_own_task(user_id, task_id)
    if not task:
        return jsonify({"error": "Task not found."}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted."}), 200