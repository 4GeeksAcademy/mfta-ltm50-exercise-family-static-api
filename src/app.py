"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
# from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/members', methods=['GET'])
def handle_hello():
    # This is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    response_body = members
    return jsonify(response_body), 200


@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    print(f"Fetching member with ID: {id}")
    # print type of id
    if not isinstance(id, int):
        print(f"ID is not an integer: {id}")
    member = jackson_family.get_member(id)
    if member:
        return jsonify(member), 200
    else:
        return jsonify({"message": "Member not found"}), 404


@app.route('/members', methods=['POST'])
def add_member():
    """
    Body example:
        {
            "id": Int, # Optional, will be generated automatically
            "first_name": String,
            "age": Int,
            "lucky_numbers": []
        }
    """
    member_data = request.get_json()
    if not member_data:
        return jsonify({"message": "No data provided"}), 400
    for key in ["first_name", "age", "lucky_numbers"]:
        if key not in member_data:
            return jsonify({"message": f"Missing required field: {key}"}), 400
    # Ensure last_name is set to the family name
    member_data["last_name"] = jackson_family.last_name
    # Generate a new ID if not provided
    if "id" not in member_data:
        member_data["id"] = jackson_family._generate_id()
    else:
        # Ensure the ID is unique
        existing_member = jackson_family.get_member(member_data["id"])
        if existing_member:
            return jsonify({"message": "Member with this ID already exists"}), 400

    jackson_family.add_member(member_data)
    return jsonify(member_data), 200


@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """
    Deletes a member by ID
    """
    result = jackson_family.delete_member(member_id)
    if result is not None:
        return jsonify({"done": True}), 200
    else:
        return jsonify({"message": "Member not found"}), 404


# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
