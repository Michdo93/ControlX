from extensions import db
import json

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class ApiEndpoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    route = db.Column(db.String(128), unique=True)
    method = db.Column(db.String(10))
    command = db.Column(db.Text)
    parameters = db.Column(db.Text)
    description = db.Column(db.Text)
    display = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<ApiEndpoint '{self.name}' [{self.method} {self.route}]>"

    def get_parameter_list(self):
        """Returns the parameters as a Python list."""
        try:
            return json.loads(self.parameters) if self.parameters else []
        except json.JSONDecodeError:
            return []

    def formatted_command(self, param_dict):
        """Fills placeholders in the command with actual parameters."""
        try:
            return self.command.format(**param_dict)
        except KeyError as e:
            return f"Missing parameter: {e}"
