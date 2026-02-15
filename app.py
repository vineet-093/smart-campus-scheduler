from datetime import datetime
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

from flask_cors import CORS
CORS(app)

# ======================================
# DATABASE INITIALIZATION
# ======================================

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venue TEXT,
        event_type TEXT,
        event_name TEXT,
        date TEXT,
        start_time TEXT,
        end_time TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

# Initialize DB when app starts
init_db()

# ======================================
# HOME ROUTE
# ======================================

@app.route("/")
def home():
    return "Smart Campus Scheduler Backend Running 🚀"

# ======================================
# STEP‑3: BOOKING ROUTE (Core Logic)
# ======================================

@app.route("/book", methods=["POST"])
def book():
    try:
        data = request.json

        # Basic validation
        required_fields = ["venue", "event_type", "event_name", "date", "start_time", "end_time"]

        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "status": "Error",
                    "message": f"{field} is required."
                }), 400

        venue = data["venue"]
        event_type = data["event_type"]
        event_name = data["event_name"]
        date = data["date"]
        start_time = data["start_time"]
        end_time = data["end_time"]

        new_start = datetime.strptime(start_time, "%H:%M")
        new_end = datetime.strptime(end_time, "%H:%M")


        # Time validation
        if new_start >= new_end:
            return jsonify({
                "status": "Error",
                "message": "Start time must be before end time."
            }), 400

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Fetch existing bookings
        cursor.execute("""
            SELECT start_time, end_time FROM bookings
            WHERE venue = ? AND date = ? AND status = 'Approved'
        """, (venue, date))

        existing_bookings = cursor.fetchall()

        # Conflict detection
        for booking in existing_bookings:
            existing_start = datetime.strptime(booking[0], "%H:%M")
            existing_end = datetime.strptime(booking[1], "%H:%M")


            if new_start < existing_end and new_end > existing_start:
                conn.close()
                return jsonify({
                    "success": False,
                    "message": "This time slot is already occupied. Please choose another slot."
                }), 400

        # Insert booking as Pending (not auto-approved)
        cursor.execute("""
            INSERT INTO bookings
            (venue, event_type, event_name, date, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (venue, event_type, event_name, date, start_time, end_time, "Pending"))


        conn.commit()
        booking_id = cursor.lastrowid
        conn.close()


        return jsonify({
            "id": booking_id,
            "venue": venue,
            "event_type": event_type,
            "event_name": event_name,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "status": "Pending"
        })


    except Exception as e:
        return jsonify({
            "status": "Error",
            "message": str(e)
        }), 500


@app.route("/bookings", methods=["GET"])
def view_bookings():

    status = request.args.get("status")
    venue = request.args.get("venue")
    date = request.args.get("date")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    query = "SELECT * FROM bookings WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if venue:
        query += " AND venue = ?"
        params.append(venue)

    if date:
        query += " AND date = ?"
        params.append(date)

    query += " ORDER BY date ASC, start_time ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    bookings = []

    for row in rows:
        bookings.append({
            "id": row[0],
            "venue": row[1],
            "event_type": row[2],
            "event_name": row[3],
            "date": row[4],
            "start_time": row[5],
            "end_time": row[6],
            "status": row[7]
        })

    return jsonify(bookings)

import json

@app.route("/venues", methods=["GET"])
def get_venues():
    with open("venues.json", "r") as file:
        venues = json.load(file)

    return jsonify(venues)

@app.route("/booking/<int:booking_id>", methods=["DELETE"])
def delete_booking(booking_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Booking not found."
        }), 404

    conn.close()

    return jsonify({
        "success": True,
        "message": "Booking deleted successfully."
    })



@app.route("/booking/<int:booking_id>", methods=["PUT"])
def update_booking(booking_id):
    data = request.json

    required_fields = ["venue", "event_type", "event_name", "date", "start_time", "end_time"]

    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                "success": False,
                "message": f"{field} is required."
            }), 400

    venue = data["venue"]
    event_type = data["event_type"]
    event_name = data["event_name"]
    date = data["date"]
    start_time = data["start_time"]
    end_time = data["end_time"]

    new_start = datetime.strptime(start_time, "%H:%M")
    new_end = datetime.strptime(end_time, "%H:%M")


    if new_start >= new_end:
        return jsonify({
            "success": False,
            "message": "Start time must be before end time."
        }), 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Check if booking exists
    cursor.execute("SELECT id FROM bookings WHERE id = ?", (booking_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Booking not found."
        }), 404

    # Conflict check against APPROVED bookings only (excluding itself)
    cursor.execute("""
        SELECT start_time, end_time FROM bookings
        WHERE venue = ?
        AND date = ?
        AND status = 'Approved'
        AND id != ?
    """, (venue, date, booking_id))

    existing_bookings = cursor.fetchall()

    for booking in existing_bookings:
        existing_start = datetime.strptime(booking[0], "%H:%M")
        existing_end = datetime.strptime(booking[1], "%H:%M")



        if new_start < existing_end and new_end > existing_start:
            conn.close()
            return jsonify({
                "success": False,
                "message": "Time conflict detected with approved booking."
            }), 400

    # Update booking and reset status to Pending
    cursor.execute("""
        UPDATE bookings
        SET venue=?, event_type=?, event_name=?, date=?, start_time=?, end_time=?, status='Pending'
        WHERE id=?
    """, (
        venue,
        event_type,
        event_name,
        date,
        start_time,
        end_time,
        booking_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Booking updated and set to Pending approval.",
        "id": booking_id,
        "venue": venue,
        "event_type": event_type,
        "event_name": event_name,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "status": "Pending"
    })


@app.route("/approve/<int:booking_id>", methods=["PUT"])
def approve_booking(booking_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings
        SET status='Approved'
        WHERE id=?
    """, (booking_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Booking not found."
        }), 404

    conn.close()

    return jsonify({
        "success": True,
        "message": "Booking approved."
    })


@app.route("/reject/<int:booking_id>", methods=["PUT"])
def reject_booking(booking_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings
        SET status='Rejected'
        WHERE id=?
    """, (booking_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Booking not found."
        }), 404

    conn.close()

    return jsonify({
        "success": True,
        "message": "Booking rejected."
    })



# ======================================
# RUN SERVER
# ======================================

if __name__ == "__main__":
    app.run(debug=True)
