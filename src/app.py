"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""


from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from .db import get_db_connection, init_db

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


# Initialize the database if needed
init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")



@app.get("/activities")
def get_activities():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities")
    activities = cur.fetchall()
    result = {}
    for act in activities:
        cur.execute("SELECT email FROM participants WHERE activity_name = ?", (act["name"],))
        participants = [row["email"] for row in cur.fetchall()]
        result[act["name"]] = {
            "description": act["description"],
            "schedule": act["schedule"],
            "max_participants": act["max_participants"],
            "participants": participants
        }
    conn.close()
    return result



@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities WHERE name = ?", (activity_name,))
    activity = cur.fetchone()
    if not activity:
        conn.close()
        raise HTTPException(status_code=404, detail="Activity not found")
    cur.execute("SELECT * FROM participants WHERE activity_name = ? AND email = ?", (activity_name, email))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Student is already signed up")
    cur.execute("SELECT COUNT(*) FROM participants WHERE activity_name = ?", (activity_name,))
    count = cur.fetchone()[0]
    if count >= activity["max_participants"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Activity is full")
    cur.execute("INSERT INTO participants (activity_name, email) VALUES (?, ?)", (activity_name, email))
    conn.commit()
    conn.close()
    return {"message": f"Signed up {email} for {activity_name}"}



@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities WHERE name = ?", (activity_name,))
    activity = cur.fetchone()
    if not activity:
        conn.close()
        raise HTTPException(status_code=404, detail="Activity not found")
    cur.execute("SELECT * FROM participants WHERE activity_name = ? AND email = ?", (activity_name, email))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
    cur.execute("DELETE FROM participants WHERE activity_name = ? AND email = ?", (activity_name, email))
    conn.commit()
    conn.close()
    return {"message": f"Unregistered {email} from {activity_name}"}
