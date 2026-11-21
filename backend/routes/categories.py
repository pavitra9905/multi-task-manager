from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Category
from schemas import CategorySchema

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")


def category_to_dict(c):
    return {"id": c.id, "name": c.name}


def get_own_category(user_id, category_id):
    return Category.query.filter_by(id=category_id, user_id=user_id).first()


@categories_bp.get("")
@jwt_required()
def list_categories():
    user_id = int(get_jwt_identity())
    cats = Category.query.filter_by(user_id=user_id).order_by(Category.name).all()
    return jsonify([category_to_dict(c) for c in cats]), 200


@categories_bp.post("")
@jwt_required()
def create_category():
    user_id = int(get_jwt_identity())
    try:
        data = CategorySchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    name = data["name"].strip()
    if Category.query.filter_by(user_id=user_id, name=name).first():
        return jsonify({"error": "Category already exists."}), 409

    cat = Category(user_id=user_id, name=name)
    db.session.add(cat)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category already exists."}), 409
    return jsonify(category_to_dict(cat)), 201


@categories_bp.put("/<int:category_id>")
@jwt_required()
def update_category(category_id):
    user_id = int(get_jwt_identity())
    cat = get_own_category(user_id, category_id)
    if not cat:
        return jsonify({"error": "Category not found."}), 404

    try:
        data = CategorySchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    name = data["name"].strip()
    clash = Category.query.filter_by(user_id=user_id, name=name).first()
    if clash and clash.id != cat.id:
        return jsonify({"error": "Category already exists."}), 409

    cat.name = name
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category already exists."}), 409
    return jsonify(category_to_dict(cat)), 200


@categories_bp.delete("/<int:category_id>")
@jwt_required()
def delete_category(category_id):
    user_id = int(get_jwt_identity())
    cat = get_own_category(user_id, category_id)
    if not cat:
        return jsonify({"error": "Category not found."}), 404

    # Tasks in this category are kept; their category becomes empty.
    db.session.delete(cat)
    db.session.commit()
    return jsonify({"message": "Category deleted."}), 200