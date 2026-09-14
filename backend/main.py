from flask import Flask, jsonify, request
from database import get_connection, get_service_history
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from services import check_all_services


app = Flask(__name__)
CORS(app)

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/services")
def services():
    return jsonify(check_all_services())

def scheduled_check():
    print("Running scheduled check...")
    check_all_services()

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_check, "interval", seconds=30)
scheduler.start()

@app.route("/api/alerts")
def alerts():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alerts ORDER BY triggered_at DESC")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)

@app.route("/api/services/<int:service_id>/history")
def service_history(service_id):
    days = request.args.get("days", default=90, type=int)
    return jsonify(get_service_history(service_id, days))

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)