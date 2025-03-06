from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta

api = Blueprint("api", __name__, url_prefix="/api/v1")


@api.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


@api.route("/todos", methods=["GET"])
def get_todos():
    completed_filter = request.args.get("completed")
    window = request.args.get("window", type=int)

    query = Todo.query

    if completed_filter is not None:
        completed_filter = completed_filter.lower() == "true"
        query = query.filter_by(completed=completed_filter)

    if window is not None:
        cutoff_date = datetime.utcnow() + timedelta(days=window)
        query = query.filter(Todo.deadline_at <= cutoff_date)

    todos = query.all()
    return jsonify([todo.to_dict() for todo in todos])


@api.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify(todo.to_dict())


@api.route("/todos", methods=["POST"])
def create_todo():
    valid_fields = {"title", "description", "completed", "deadline_at"}

    if not request.is_json:
        return jsonify({"error": "Invalid JSON format"}), 400

    extra_fields = set(request.json.keys()) - valid_fields
    if extra_fields:
        return jsonify({"error": "Invalid fields present"}), 400

    if "title" not in request.json:
        return jsonify({"error": "Title is required"}), 400

    todo = Todo(
        title=request.json["title"],
        description=request.json.get("description"),
        completed=request.json.get("completed", False),
    )
    if "deadline_at" in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json["deadline_at"])

    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@api.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    valid_fields = {"title", "description", "completed", "deadline_at"}

    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    if not request.is_json:
        return jsonify({"error": "Invalid JSON format"}), 400

    extra_fields = set(request.json.keys()) - valid_fields
    if extra_fields:
        return jsonify({"error": "Invalid fields present"}), 400

    todo.title = request.json.get("title", todo.title)
    todo.description = request.json.get("description", todo.description)
    todo.completed = request.json.get("completed", todo.completed)
    todo.deadline_at = request.json.get("deadline_at", todo.deadline_at)

    db.session.commit()
    return jsonify(todo.to_dict()), 200


@api.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200

    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
