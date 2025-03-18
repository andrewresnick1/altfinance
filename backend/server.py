from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.get("/jobs")
def get_jobs():
    conn = sqlite3.connect("mastercard_jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT country, job_count, timestamp FROM job_counts ORDER BY timestamp DESC LIMIT 50")
    data = [{"country": row[0], "job_count": row[1], "timestamp": row[2]} for row in cursor.fetchall()]
    conn.close()
    return {"jobs": data}

@app.get("/jobs/{country}")
def get_job_count(country: str):
    conn = sqlite3.connect("mastercard_jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT job_count, timestamp FROM job_counts WHERE country = ? ORDER BY timestamp DESC LIMIT 1", (country,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"country": country, "job_count": row[0], "timestamp": row[1]}
    return {"error": "No data found"}
