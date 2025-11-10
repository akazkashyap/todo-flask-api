from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)


# models
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    done = db.Column(db.Boolean, default=False)

with app.app_context():
        db.create_all()
        
# schema
class TodoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Todo
        load_instance = True
        include_pk = True

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)




# routes

@app.route("/", methods=['GET'])
def home():
    return jsonify({'message':'There is nothing visit /todos, /todo/id'})


@app.route('/todos', methods=['GET'])
def get_todos():
    todos_qs = Todo.query.all()
    todos = todos_schema.dump(todos_qs)
    return jsonify(todos)

@app.route("/todo/<int:id>", methods=['GET'])
def get_todo(id):
    todo_qs = db.session.get(Todo, id)
    if todo_qs:
        todo = todo_schema.dump(todo_qs)
        return jsonify(todo)
    else:
        return jsonify({"error":"not found"})
    

@app.route("/todos", methods=['POST'])
def create_todo():
    data = request.json
    
    try:
        new_todo = todo_schema.load(data, session=db.session) # with schema
    except Exception as e:
        return jsonify(e.messages), 404
    
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(todo_schema.dump(new_todo)), 201


@app.route("/todo/<int:id>", methods=['DELETE'])
def delete_todo(id):
    todo = db.session.get(Todo, id)
    if not todo :
        return jsonify({'error':'Todo not found'})
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message':'Deleted successfully'})


@app.route('/todo/<int:id>', methods=['PUT'])
def update_todo(id):
    todo = db.session.get(Todo, id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    data = request.json
    
    try:
        updated_todo = todo_schema.load(
            data, 
            instance=todo, 
            partial=True, 
            session=db.session
        )
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    db.session.commit()
    
    return jsonify(todo_schema.dump(updated_todo))


# entery point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=8000)