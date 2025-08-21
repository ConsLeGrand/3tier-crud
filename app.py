# app.py
from flask import Flask, request, jsonify
import mysql.connector, os
import elasticapm
from elasticapm.contrib.flask import ElasticAPM

# Configuration APM
app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': '3tier-crud-flask',
    'SERVER_URL': 'http://fleet01.heritage.africa:8200',  
    'ENVIRONMENT': 'production'
}

# Initialiser APM
apm = ElasticAPM(app)


app = Flask(__name__)

db_config = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'user': os.getenv('DB_USER', 'user1'),
    'password': os.getenv('DB_PASS', 'pass123'),
    'database': os.getenv('DB_NAME', 'mydb')
}

def get_connection():
    return mysql.connector.connect(**db_config)

# Ensure table exists
with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    """)
    conn.commit()

@app.route("/api/add", methods=["POST"])
def add_person():
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO people (name) VALUES (%s)", (name,))
        conn.commit()
        return jsonify({"message": f"{name} added ✅"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/list", methods=["GET"])
def list_people():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM people")
        rows = cur.fetchall()
        return jsonify([{"id": r[0], "name": r[1]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
