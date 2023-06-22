from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)
app.config['MONGO_URI'] = 'mongodb://localhost/pythonreactdb'
mongo = PyMongo(app)

# Model
class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    @staticmethod
    def from_dict(data):
        return User(data['name'], data['email'], data['password'])

    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'password': self.password
        }

# DAO
class UserDAO:
    @staticmethod
    def create_user(user):
        result = mongo.db.users.insert_one(user.to_dict())
        inserted_id = str(result.inserted_id)
        return inserted_id

    @staticmethod
    def get_users():
        users = []
        for doc in mongo.db.users.find():
            user = User(
                doc['name'],
                doc['email'],
                doc['password']
            )
            user_dict = user.to_dict()
            user_dict['_id'] = str(doc['_id'])
            users.append(user_dict)
        return users

    @staticmethod
    def get_user(id):
        user = mongo.db.users.find_one({'_id': ObjectId(id)})
        if user:
            user_obj = User(
                user['name'],
                user['email'],
                user['password']
            )
            user_dict = user_obj.to_dict()
            user_dict['_id'] = str(user['_id'])
            return user_dict
        else:
            return {'message': 'User not found'}

    @staticmethod
    def delete_user(id):
        mongo.db.users.delete_one({'_id': ObjectId(id)})
        return {'msg': 'User deleted'}

    @staticmethod
    def update_user(id, data):
        mongo.db.users.update_one({'_id': ObjectId(id)}, {'$set': data})
        return {'msg': 'User updated'}

# Views
@app.route('/users', methods=['POST'])
def create_user_view():
    data = request.json
    user = User.from_dict(data)
    inserted_id = UserDAO.create_user(user)
    return jsonify(inserted_id)

@app.route('/users', methods=['GET'])
def get_users_view():
    users = UserDAO.get_users()
    return jsonify(users)

@app.route('/users/<id>', methods=['GET'])
def get_user_view(id):
    user = UserDAO.get_user(id)
    return jsonify(user)

@app.route('/users/<id>', methods=['DELETE'])
def delete_user_view(id):
    result = UserDAO.delete_user(id)
    return jsonify(result)

@app.route('/users/<id>', methods=['PUT'])
def update_user_view(id):
    data = request.json
    result = UserDAO.update_user(id, data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
