# Hospital Room Availability Checking during Reservation

## Description
A Flask-based web application to manage hospital room availability and reservations.  
Backend: SQL Server with stored procedures.

## Features
- User Registration & Login
- Room Availability Check
- Room Registration with Types and Prices
- Make Reservations
- Generate Printable & Downloadable Bills
- Update Reservation Status (Check-in, Check-out)
- CSS-styled Dashboard

## Technologies
- Python Flask
- SQL Server
- Bootstrap (for front-end styling)
- pyodbc (for SQL Server connection)

## Setup
1. Import `hospital_reservation_schema.sql` into SQL Server.
2. Configure connection string inside `app.py` for your SQL Server instance.
3. Install Python dependencies:
   
## Structure

HospitalRoomReservation/
│
├── app.py
├── requirements.txt
├── README.md
├── hospital_reservation_schema.sql
│
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register_user.html
│   ├── register_room.html
│   ├── check_availability.html
│   ├── make_reservation.html
│   ├── generate_bill.html
│   └── update_status.html
│
└── .gitignore
