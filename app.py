import bcrypt
import hmac
import secrets
import os
import subprocess
import shlex
import re
from flask import Flask, render_template, request, redirect, session, jsonify, Response, url_for, flash, send_file
from flask_cors import CORS
from functools import wraps
from extensions import db
import io
import csv

# -------------------
# App Setup
# -------------------

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

CORS(app, origins=["http://localhost:5000"])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///controlx.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from models import User, ApiEndpoint

# -------------------
# Auth Helpers
# -------------------

def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return False

    if user.password.startswith('$2b$'):
        return bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
    return hmac.compare_digest(user.password, password)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not verify_password(auth.username, auth.password):
            return Response("Authentication required.", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated

def current_user():
    return User.query.filter_by(username=session.get('user')).first()

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = current_user()
        if not user or user.role != 'admin':
            return "Access denied", 403
        return f(*args, **kwargs)
    return decorated

# -------------------
# Web Routes
# -------------------

@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    endpoints = ApiEndpoint.query.all()
    return render_template('index.html', endpoints=endpoints, session=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and verify_password(user.username, password):
            session['user'] = user.username
            session['role'] = user.role
            return redirect('/')
        return 'Login failed'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# User Management

@app.route('/users')
@require_admin
def user_list():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route("/users/create", methods=["GET", "POST"])
@require_admin
def add_user():
    if request.method == "POST":
        pw_raw = request.form["password"].encode("utf-8")
        hashed_pw = bcrypt.hashpw(pw_raw, bcrypt.gensalt()).decode("utf-8")
        user = User(username=request.form["username"], role=request.form["role"], password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("User added successfully.")
        return redirect(url_for("user_list"))
    return render_template("user_form.html", action="Add", user=None)

@app.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
@require_admin
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.username = request.form["username"]
        user.role = request.form["role"]
        if request.form["password"]:
            pw_raw = request.form["password"].encode("utf-8")
            user.password = bcrypt.hashpw(pw_raw, bcrypt.gensalt()).decode("utf-8")
        db.session.commit()
        flash("User updated successfully.")
        return redirect(url_for("user_list"))
    return render_template("user_form.html", action="Edit", user=user)

@app.route("/users/delete/<int:user_id>")
@require_admin
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.")
    return redirect(url_for("user_list"))

# Endpoint Management

@app.route("/endpoints/create", methods=["GET", "POST"])
@require_admin
def add_endpoint():
    if request.method == "POST":
        try:
            route = request.form["route"]
            if not route.startswith("/"):
                route = "/" + route

            endpoint = ApiEndpoint(
                name=request.form["name"],
                route=route,
                method=request.form["method"],
                command=request.form["command"],
                parameters=request.form.get("parameters") or None,
                description=request.form.get("description") or None,
                display=request.form["display"] or None
            )

            db.session.add(endpoint)
            db.session.commit()

            flash("Endpoint added successfully.", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    return render_template("endpoint_form.html", action="Add", endpoint=None)

@app.route("/endpoints/edit/<int:endpoint_id>", methods=["GET", "POST"])
@require_admin
def edit_endpoint(endpoint_id):
    endpoint = db.session.get(ApiEndpoint, endpoint_id)
    if not endpoint:
        return jsonify({'error': 'Endpoint not found'}), 404

    if request.method == "POST":
        try:
            route = request.form["route"]
            if not route.startswith("/"):
                route = "/" + route

            endpoint.name = request.form["name"]
            endpoint.route = route
            endpoint.method = request.form["method"]
            endpoint.command = request.form["command"]
            endpoint.parameters = request.form.get("parameters") or None
            endpoint.description = request.form.get("description") or None
            endpoint.display = request.form["display"] or None

            db.session.commit()

            flash("Endpoint updated successfully.", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    return render_template("endpoint_form.html", action="Edit", endpoint=endpoint)

@app.route("/endpoints/delete/<int:endpoint_id>", methods=["POST"])
@require_admin
def delete_endpoint(endpoint_id):
    endpoint = db.session.get(ApiEndpoint, endpoint_id)
    if not endpoint:
        return jsonify({'error': 'Endpoint not found'}), 404

    db.session.delete(endpoint)
    db.session.commit()

    flash("Endpoint deleted successfully.", "success")
    return redirect(url_for("index"))

# CSV Import/Export

# Import CSV for ApiEndpoint
@app.route('/import_csv', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect('/')

    file = request.files['file']
    if file.filename == '':
        flash('Missing filename')
        return redirect('/')

    if not file.filename.endswith('.csv'):
        flash('Only CSV files are supported')
        return redirect('/')

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)

    imported = 0
    skipped = 0

    for row in reader:
        name = row['name'].strip()
        route = row['route'].strip()
        method = row.get('method', 'GET').strip().upper()
        command = row['command'].strip()
        parameters = row.get('parameters', '').strip()
        description = row.get('description', '').strip()
        display = row.get('display', '').strip()

        # Check for duplicate name or route
        exists = ApiEndpoint.query.filter(
            (ApiEndpoint.name == name) | (ApiEndpoint.route == route)
        ).first()
        if exists:
            skipped += 1
            continue

        ep = ApiEndpoint(
            name=name,
            route=route,
            method=method,
            command=command,
            parameters=parameters or None,
            description=description or None,
            display=int(display) if display.isdigit() else None
        )

        db.session.add(ep)
        imported += 1

    db.session.commit()
    flash(f"Imported {imported} endpoints. Skipped {skipped} due to duplicates.")
    return redirect('/')

# Export CSV fpor ApiEndpoint
@app.route('/export_csv')
def export_csv():
    endpoints = ApiEndpoint.query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'route', 'method', 'command', 'parameters', 'description', 'display'])

    for ep in endpoints:
        writer.writerow([
            ep.name,
            ep.route,
            ep.method,
            ep.command,
            ep.parameters or '',
            ep.description or '',
            ep.display if ep.display is not None else ''
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='api_endpoints.csv'
    )

# -------------------
# Dynamic API Handler (Catch-All)
# -------------------

@app.route("/api/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE"])
@require_auth
def dynamic_api_handler(subpath):
    full_route = f"/{subpath}"
    ep = ApiEndpoint.query.filter_by(route=full_route, method=request.method.upper()).first()
    if not ep:
        return jsonify({"error": f"No endpoint found for {request.method} {full_route}"}), 404

    params = request.get_json(force=True, silent=True) or {}
    result = execute_endpoint(ep, params)
    return jsonify(result)

# -------------------
# Command Execution
# -------------------

def execute_endpoint(ep: ApiEndpoint, params: dict):
    try:
        safe_params = {k: shlex.quote(str(v)) for k, v in params.items()}
        cmd = ep.command.format(**safe_params)

        if re.search(r"[;&|<>`$!\\]", cmd):
            return {"error": "Command contains forbidden shell characters."}

        env = os.environ.copy()
        if ep.display is not None:
            env["DISPLAY"] = f":{ep.display}"

        result = subprocess.run(["/bin/sh", "-c", cmd], capture_output=True, text=True, env=env)

        return {
            "command": cmd,
            "output": result.stdout.strip().splitlines(),
            "error": result.stderr.strip()
        }
    except Exception as e:
        return {"error": str(e)}

# -------------------
# Main
# -------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=False, host='0.0.0.0', port=5000)
