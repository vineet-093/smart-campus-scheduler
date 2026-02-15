# Integrated Campus Scheduling and Venue Conflict Resolution System

## 📌 Overview
The Integrated Campus Scheduling and Venue Conflict Resolution System is a full-stack web application designed to automate and streamline venue booking processes in educational institutions.

The system ensures conflict-free scheduling through automated time validation and introduces an admin approval workflow to maintain transparency and control.

---

## 🚀 Features

### 👤 User Features
- Select venue from dynamic dropdown
- Book venue with date & time selection
- Real-time conflict detection
- View upcoming bookings
- Update booking (resets to Pending)
- Delete booking

### 👨‍💼 Admin Features
- Password-protected Admin Mode
- Approve / Reject booking requests
- Delete bookings
- Only approved bookings block time slots

### ⚙️ System Features
- REST API-based architecture
- Conflict detection using time comparison logic
- Status tracking (Pending / Approved / Rejected)
- Responsive UI
- Full-stack integration

---

## 🏗️ Tech Stack

**Backend**
- Python
- Flask
- Flask-CORS
- SQLite
- Gunicorn (for deployment)

**Frontend**
- HTML
- CSS
- JavaScript

---

## 🔄 System Workflow

1. User submits a booking request.
2. Backend validates input and checks for time conflicts.
3. If no conflict, booking is stored as **Pending**.
4. Admin reviews request and approves or rejects it.
5. Approved bookings block that time slot from future requests.

---

## 📂 Project Structure
