import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            service_id INT,
            service_name VARCHAR(100),
            status VARCHAR(20),
            status_code INT,
            response_time_ms INT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Table 'checks' created (or already exists).")

def get_service_history(service_id, days=90):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DATE(checked_at) AS day,
               SUM(status = 'up') AS up_count,
               COUNT(*) AS total_count
        FROM checks
        WHERE service_id = %s
          AND checked_at >= NOW() - INTERVAL %s DAY
        GROUP BY DATE(checked_at)
        ORDER BY day ASC
    """, (service_id, days))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    day_status = {}
    for row in rows:
        day_str = row["day"].strftime("%Y-%m-%d")
        if row["up_count"] == row["total_count"]:
            day_status[day_str] = "up"
        elif row["up_count"] == 0:
            day_status[day_str] = "down"
        else:
            day_status[day_str] = "degraded"

    from datetime import date, timedelta
    today = date.today()
    history = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        history.append({"date": d_str, "status": day_status.get(d_str, "no-data")})

    total_checks = sum(r["total_count"] for r in rows)
    total_up = sum(r["up_count"] for r in rows)
    uptime_pct = round((total_up / total_checks) * 100, 1) if total_checks > 0 else None

    return {"history": history, "uptime_pct": uptime_pct}

if __name__ == "__main__":
    create_table()