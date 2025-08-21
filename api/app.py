import os
import elasticapm
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from elasticapm.contrib.flask import ElasticAPM

# Configuration APM
app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': '3tier-crud-flask',
    'SERVER_URL': 'http://fleet01.heritage.africa:8200',  
    'ENVIRONMENT': 'production'
}

# Initialiser APM
apm = ElasticAPM(app)

DB_HOST = os.getenv("DB_HOST", "mysql")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "etudiants")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "apppass123")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

app = Flask(__name__)
CORS(app)  # CORS ouvert pour le frontend

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

@app.get("/healthz")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "error": str(e)}, 500

@app.get("/students")
def list_students():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, first_name, last_name, email, created_at FROM students ORDER BY id DESC")).mappings().all()
        return jsonify(list(rows))

@app.get("/students/<int:sid>")
def get_student(sid):
    with engine.connect() as conn:
        row = conn.execute(text("SELECT id, first_name, last_name, email, created_at FROM students WHERE id=:id"), {"id": sid}).mappings().first()
        if not row:
            return {"message": "Not found"}, 404
        return jsonify(dict(row))

@app.post("/students")
def create_student():
    data = request.get_json(force=True)
    required = ["first_name", "last_name", "email"]
    if any(k not in data or not str(data[k]).strip() for k in required):
        return {"message": "Champs requis: first_name, last_name, email"}, 400
    try:
        with engine.begin() as conn:
            res = conn.execute(
                text("""INSERT INTO students(first_name, last_name, email)
                        VALUES (:fn, :ln, :em)"""),
                {"fn": data["first_name"].strip(), "ln": data["last_name"].strip(), "em": data["email"].strip()}
            )
            sid = res.lastrowid
            row = conn.execute(text("SELECT id, first_name, last_name, email, created_at FROM students WHERE id=:id"), {"id": sid}).mappings().first()
        return jsonify(dict(row)), 201
    except IntegrityError:
        return {"message": "Email déjà utilisé"}, 409
    except SQLAlchemyError as e:
        return {"message": "Erreur SQL", "error": str(e)}, 500

@app.put("/students/<int:sid>")
def update_student(sid):
    data = request.get_json(force=True)
    fields = {k: v.strip() for k, v in data.items() if k in ["first_name", "last_name", "email"] and str(v).strip()}
    if not fields:
        return {"message": "Aucun champ à mettre à jour"}, 400
    sets = ", ".join([f"{k}=:{k}" for k in fields.keys()])
    fields["id"] = sid
    try:
        with engine.begin() as conn:
            res = conn.execute(text(f"UPDATE students SET {sets} WHERE id=:id"), fields)
            if res.rowcount == 0:
                return {"message": "Not found"}, 404
            row = conn.execute(text("SELECT id, first_name, last_name, email, created_at FROM students WHERE id=:id"), {"id": sid}).mappings().first()
        return jsonify(dict(row))
    except IntegrityError:
        return {"message": "Email déjà utilisé"}, 409

@app.delete("/students/<int:sid>")
def delete_student(sid):
    with engine.begin() as conn:
        res = conn.execute(text("DELETE FROM students WHERE id=:id"), {"id": sid})
        if res.rowcount == 0:
            return {"message": "Not found"}, 404
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
