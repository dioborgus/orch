from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import Swagger
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
Swagger(app)

# Define the Case model
class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.Integer, default=1)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_modify_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = db.Column(db.String(500), default="")
    ip_addresses = db.Column(db.String(200), default="")
    username = db.Column(db.String(100), default="")
    file_name = db.Column(db.String(100), default="")

# Define the Case schema
class CaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Case
        load_instance = True

case_schema = CaseSchema()
cases_schema = CaseSchema(many=True)

# Create the database
with app.app_context():
    db.create_all()

# Create a new case
@app.route('/api/cases', methods=['POST'])
def create_case():
    """
    Create a new case
    ---
    tags:
      - Cases
    parameters:
      - in: body
        name: body
        required: true
        description: Case details
        schema:
          type: object
          properties:
            title:
              type: string
              description: Title of the case
              example: Example Case
            severity:
              type: integer
              description: Severity level of the case (1-4)
              example: 2
            description:
              type: string
              description: Description of the case
              example: Detailed description of the case
            ip_addresses:
              type: string
              description: Associated IP addresses
              example: 192.168.1.1
            username:
              type: string
              description: Username related to the case
              example: user123
            file_name:
              type: string
              description: Related file name
              example: evidence.txt
    responses:
      201:
        description: Case created successfully
    """
    data = request.json
    title = data.get('title')
    severity = data.get('severity', 1)
    description = data.get('description', "")
    ip_addresses = data.get('ip_addresses', "")
    username = data.get('username', "")
    file_name = data.get('file_name', "")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    new_case = Case(
        title=title,
        severity=severity,
        description=description,
        ip_addresses=ip_addresses,
        username=username,
        file_name=file_name
    )
    db.session.add(new_case)
    db.session.commit()
    return case_schema.jsonify(new_case), 201

# Get all cases
@app.route('/api/cases', methods=['GET'])
def get_cases():
    """
    Get all cases
    ---
    tags:
      - Cases
    responses:
      200:
        description: List of all cases
        schema:
          type: array
          items:
            $ref: '#/definitions/Case'
    """
    all_cases = Case.query.all()
    return cases_schema.jsonify(all_cases)

# Get a single case by ID
@app.route('/api/cases/<int:id>', methods=['GET'])
def get_case(id):
    """
    Get a single case by ID
    ---
    tags:
      - Cases
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the case to retrieve
    responses:
      200:
        description: Case details
        schema:
          $ref: '#/definitions/Case'
    """
    case = Case.query.get_or_404(id)
    return case_schema.jsonify(case)

# Update a case
@app.route('/api/cases/<int:id>', methods=['PUT'])
def update_case(id):
    """
    Update a case by ID
    ---
    tags:
      - Cases
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the case to update
      - in: body
        name: body
        required: true
        description: Updated case details
        schema:
          type: object
          properties:
            title:
              type: string
              description: Updated title of the case
              example: Updated Case
            severity:
              type: integer
              description: Updated severity level
              example: 3
            description:
              type: string
              description: Updated description
              example: Updated description of the case
            ip_addresses:
              type: string
              description: Updated IP addresses
              example: 192.168.1.2
            username:
              type: string
              description: Updated username
              example: newuser123
            file_name:
              type: string
              description: Updated file name
              example: updated_evidence.txt
    responses:
      200:
        description: Case updated successfully
    """
    case = Case.query.get_or_404(id)
    data = request.json

    case.title = data.get('title', case.title)
    case.severity = data.get('severity', case.severity)
    case.description = data.get('description', case.description)
    case.ip_addresses = data.get('ip_addresses', case.ip_addresses)
    case.username = data.get('username', case.username)
    case.file_name = data.get('file_name', case.file_name)

    db.session.commit()
    return case_schema.jsonify(case)

# Delete a case
@app.route('/api/cases/<int:id>', methods=['DELETE'])
def delete_case(id):
    """
    Delete a case by ID
    ---
    tags:
      - Cases
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the case to delete
    responses:
      200:
        description: Case deleted successfully
    """
    case = Case.query.get_or_404(id)
    db.session.delete(case)
    db.session.commit()
    return jsonify({"message": "Case deleted"})

@app.route('/', methods=['GET'])
def homepage():
    return redirect(url_for('list_cases_ui'))

# Web UI for case listing
@app.route('/ui/cases', methods=['GET'])
def list_cases_ui():
    cases = Case.query.all()
    return render_template('cases_list.html', cases=cases)

# Web UI for single case view and edit
@app.route('/ui/cases/<int:id>', methods=['GET', 'POST'])
def view_case_ui(id):
    case = Case.query.get_or_404(id)

    if request.method == 'POST':
        case.description = request.form.get('description', case.description)
        db.session.commit()
        return redirect(url_for('list_cases_ui'))

    return render_template('case_view.html', case=case)

if __name__ == '__main__':
    app.run(debug=False)
