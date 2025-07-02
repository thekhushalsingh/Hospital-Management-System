from flask import Flask, render_template, request, redirect, session, url_for, Response
import pyodbc

app = Flask(__name__)
app.secret_key = 'your_secret_key'

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=KHUSHAL\\SQLEXPRESS01;"
    "Database=HDB;"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    return pyodbc.connect(conn_str)

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC UserLogin ?, ?", username, password)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            session['username'] = username
            return redirect('/dashboard')
        else:
            msg = 'Invalid username or password.'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC RegisterUser ?, ?, ?", username, password, email)
        conn.commit()
        cursor.close()
        conn.close()
        msg = 'User registered successfully!'
    return render_template('register_user.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template('dashboard.html', username=session['username'])

@app.route('/check_availability', methods=['GET', 'POST'])
def check_availability():
    if 'username' not in session:
        return redirect('/')
    msg = ''
    if request.method == 'POST':
        room_id = request.form['room_id']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC CheckRoomAvailability ?, ?, ?", room_id, check_in, check_out)
        result = cursor.fetchone()
        if result:
            msg = f"Availability Status: {result[0]}"
        cursor.close()
        conn.close()
    return render_template('check_availability.html', msg=msg)

""" @app.route('/register_room', methods=['GET', 'POST'])
def register_room():
    if 'username' not in session:
        return redirect('/')
    msg = ''
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        price = request.form['price']
        status = request.form['status']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC RegisterRoom ?, ?, ?, ?", room_number, room_type, price, status)
        conn.commit()
        cursor.close()
        conn.close()
        msg = 'Room Registered Successfully!'
    return render_template('register_room.html', msg=msg)
""" 
@app.route('/register_room', methods=['GET', 'POST'])
def register_room():
    if 'username' not in session:
        return redirect('/')
    msg = ''
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        price = float(request.form['price'])
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if Room Number already exists
            cursor.execute("SELECT COUNT(*) FROM Rooms WHERE RoomNumber = ?", room_number)
            count = cursor.fetchone()[0]

            if count > 0:
                msg = "Room number already exists. Please choose a different room number."
            else:
                cursor.execute("EXEC RegisterRoom ?, ?, ?, ?", room_number, room_type, price, status)
                conn.commit()
                msg = "Room Registered Successfully!"

        except pyodbc.Error as e:
            msg = f"Database Error: {str(e)}"

        cursor.close()
        conn.close()

    return render_template('register_room.html', msg=msg)

@app.route('/make_reservation', methods=['GET', 'POST'])
def make_reservation():
    if 'username' not in session:
        return redirect('/')

    msg = ''
    rooms = []

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch available rooms for dropdown
    cursor.execute("SELECT RoomID, RoomNumber, RoomType FROM Rooms")
    rooms = cursor.fetchall()

    if request.method == 'POST':
        username = request.form['username']
        room_id = request.form['room_id']
        check_in = request.form['check_in']
        check_out = request.form['check_out']

        # Check user exists
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", username)
        user = cursor.fetchone()
        if not user:
            msg = f"Error: Username '{username}' does not exist. Please register user first."
            cursor.close()
            conn.close()
            return render_template('make_reservation.html', msg=msg, rooms=rooms)

        user_id = user[0]

        # Check room exists
        cursor.execute("SELECT COUNT(*) FROM Rooms WHERE RoomID = ?", room_id)
        room_exists = cursor.fetchone()[0]
        if not room_exists:
            msg = f"Error: Room ID '{room_id}' does not exist. Please register the room first."
            cursor.close()
            conn.close()
            return render_template('make_reservation.html', msg=msg, rooms=rooms)

        # Make reservation
        cursor.execute("EXEC MakeReservation ?, ?, ?, ?", user_id, room_id, check_in, check_out)
        conn.commit()
        msg = 'Reservation Successful!'

    cursor.close()
    conn.close()
    return render_template('make_reservation.html', msg=msg, rooms=rooms)

"""@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    if 'username' not in session:
        return redirect('/')
    msg = ''
    bill_details = ''
    if request.method == 'POST':
        username = request.form['username']
        room_number = request.form['room_number']
        conn = get_db_connection()
        cursor = conn.cursor()

        # Step 1: Get User ID from username
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", username)
        user_result = cursor.fetchone()
        if not user_result:
            msg = 'Error: Username not found.'
            cursor.close()
            conn.close()
            return render_template('generate_bill.html', msg=msg, bill_details=bill_details)
        user_id = user_result[0]

        # Step 2: Get Room ID from room number
        cursor.execute("SELECT RoomID FROM Rooms WHERE RoomNumber = ?", room_number)
        room_result = cursor.fetchone()
        if not room_result:
            msg = 'Error: Room Number not found.'
            cursor.close()
            conn.close()
            return render_template('generate_bill.html', msg=msg, bill_details=bill_details)
        room_id = room_result[0]

        # Step 3: Get Reservation ID for that user and room
        cursor.execute(""
            SELECT TOP 1 ReservationID FROM Reservations
            WHERE UserID = ? AND RoomID = ?
            ORDER BY ReservationID DESC
        "", user_id, room_id)
        reservation_result = cursor.fetchone()
        if not reservation_result:
            msg = 'Error: No reservation found for this user and room.'
            cursor.close()
            conn.close()
            return render_template('generate_bill.html', msg=msg, bill_details=bill_details)
        reservation_id = reservation_result[0]

        # Step 4: Generate Bill
        cursor.execute("EXEC GenerateBill ?", reservation_id)
        result = cursor.fetchone()
        if result:
            bill_details = f"Bill for User: {username}, Room: {room_number}\nTotal Amount: ₹{result[0]}"
            msg = 'Bill Generated Successfully!'
        else:
            msg = 'Error generating bill.'

        cursor.close()
        conn.close()

    return render_template('generate_bill.html', msg=msg, bill_details=bill_details)
    """
"""
@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    if 'username' not in session:
        return redirect('/')
    msg = ''
    bill_details = ''
    if request.method == 'POST':
        username = request.form['username']
        room_number = request.form['room_number']
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("EXEC GenerateBillByUserAndRoom ?, ?", username, room_number)
            result = cursor.fetchone()

            if result:
                bill_amount = result[0]
                bill_details = f"Bill Generated for User: {username}, Room: {room_number}\nTotal Amount: ₹{bill_amount:.2f}"
                msg = 'Bill Generated Successfully!'
            else:
                msg = 'Error: No bill details returned. Check reservation.'

        except pyodbc.Error as e:
            msg = f"Database Error: {str(e)}"

        cursor.close()
        conn.close()

    return render_template('generate_bill.html', msg=msg, bill_details=bill_details)

""" 
@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    if 'username' not in session:
        return redirect('/')
    msg = ''
    bill_details = ''
    if request.method == 'POST':
        username = request.form['username']
        room_number = request.form['room_number']
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("EXEC GenerateBillByUserAndRoom ?, ?", username, room_number)
            result = cursor.fetchone()

            if result and result[0] is not None:
                bill_amount = result[0]
                bill_details = f"Bill Generated for User: {username}, Room: {room_number}\nTotal Amount: ₹{bill_amount:.2f}"
                msg = 'Bill Generated Successfully!'
            else:
                msg = 'No bill generated. Check if reservation exists for this user and room.'

        except pyodbc.Error as e:
            msg = f"Database Error: {str(e)}"

        cursor.close()
        conn.close()

    return render_template('generate_bill.html', msg=msg, bill_details=bill_details)



@app.route('/download_bill', methods=['POST'])
def download_bill():
    bill_text = request.form['bill_text']
    return Response(
        bill_text,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=bill.txt"}
    )

@app.route('/update_status', methods=['GET', 'POST'])
def update_status():
    if 'username' not in session:
        return redirect('/')
    msg = ''
    if request.method == 'POST':
        reservation_id = request.form['reservation_id']
        new_status = request.form['new_status']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC UpdateReservationStatus ?, ?", reservation_id, new_status)
        conn.commit()
        cursor.close()
        conn.close()
        msg = 'Reservation Status Updated!'
    return render_template('update_status.html', msg=msg)

if __name__ == '__main__':
    app.run(debug=True)
