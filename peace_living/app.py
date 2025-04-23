from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'peace_living_secret'

# MySQL Config
db_config = {
    'host': 'localhost',
    'user': 'aayushis',
    'password': 'Toh5UBah',
    'database': 'aayushis'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        ac = 'ac' in request.form
        dining = 'dining' in request.form
        kitchen = 'kitchen' in request.form
        private = 'private' in request.form

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Student (Name, WantsAC, WantsDining, WantsKitchen, WantsPrivateBathroom)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, ac, dining, kitchen, private))
        conn.commit()
        cur.close()
        conn.close()
        flash('Student added successfully!')
        return redirect(url_for('add_student'))
    return render_template('add_student.html')

@app.route('/add_assignment', methods=['GET', 'POST'])
def add_assignment():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT StudentId, Name FROM Student")
    students = cur.fetchall()
    cur.execute("SELECT BuildingId, RoomNumber FROM Room")
    rooms = cur.fetchall()

    if request.method == 'POST':
        student_id = int(request.form['student'])
        building_id = request.form['building']
        room_number = int(request.form['room'])

        cur.execute("SELECT WantsAC, WantsDining, WantsKitchen, WantsPrivateBathroom FROM Student WHERE StudentId = %s", (student_id,))
        wants = cur.fetchone()

        cur.execute("SELECT HasAC, HasDining, HasKitchen, PrivateBathrooms FROM Room WHERE BuildingId = %s AND RoomNumber = %s", (building_id, room_number))
        has = cur.fetchone()

        if wants and has and all(w <= h for w, h in zip(wants, has)):
            try:
                cur.execute("INSERT INTO Assignment VALUES (%s, %s, %s)", (student_id, building_id, room_number))
                conn.commit()
                flash('Assignment added successfully!')
            except:
                flash('Student already assigned or invalid input.')
        else:
            flash('Room does not meet student preferences.')

        return redirect(url_for('add_assignment'))

    cur.close()
    conn.close()
    return render_template('add_assignment.html', students=students, rooms=rooms)

@app.route('/view_assignments')
def view_assignments():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT A.StudentId, S.Name, A.BuildingId, A.RoomNumber
        FROM Assignment A
        JOIN Student S ON A.StudentId = S.StudentId
        ORDER BY S.Name
    """)
    assignments = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('view_assignments.html', assignments=assignments)

@app.route('/view_rooms')
def view_rooms():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT BuildingId, RoomNumber, NumBedrooms FROM Room ORDER BY BuildingId")
    rooms = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('view_rooms.html', rooms=rooms)

@app.route('/available_rooms/<int:student_id>')
def available_rooms(student_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Get student preferences
    cur.execute("""
        SELECT WantsAC, WantsDining, WantsKitchen, WantsPrivateBathroom 
        FROM Student WHERE StudentId = %s
    """, (student_id,))
    wants = cur.fetchone()
    print("Student wants:", wants)  # Optional debug

    if not wants:
        cur.close()
        conn.close()
        return f"No student found with ID {student_id}", 404

    # Find matching rooms
    cur.execute("""
        SELECT BuildingId, RoomNumber, NumBedrooms 
        FROM Room
        WHERE HasAC >= %s AND HasDining >= %s AND HasKitchen >= %s AND PrivateBathrooms >= %s
    """, wants)

    matches = cur.fetchall()
    print("Room matches:", matches)  # Optional debug

    cur.close()
    conn.close()

    return render_template('available_rooms.html', matches=matches, student_id=student_id)


@app.route('/available_rooms')
def available_rooms_fallback():
    return redirect(url_for('select_student'))

@app.route('/roommate_matches/<int:student_id>')
def roommate_matches(student_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Get preferences
    cur.execute("""
        SELECT WantsAC, WantsDining, WantsKitchen, WantsPrivateBathroom 
        FROM Student WHERE StudentId = %s
    """, (student_id,))
    prefs = cur.fetchone()
    print("Student prefs:", prefs)

    if not prefs:
        cur.close()
        conn.close()
        return f"No student found with ID {student_id}", 404

    # Match students with identical preferences (excluding self)
    cur.execute("""
        SELECT StudentId, Name 
        FROM Student 
        WHERE StudentId != %s AND 
              WantsAC = %s AND WantsDining = %s AND WantsKitchen = %s AND WantsPrivateBathroom = %s
    """, (student_id, *prefs))

    matches = cur.fetchall()
    print("Matches:", matches)

    cur.close()
    conn.close()

    return render_template('roommate_matches.html', matches=matches, student_id=student_id)

@app.route('/roommate_matches')
def roommate_matches_fallback():
    return redirect(url_for('select_student'))

@app.route('/select_student')
def select_student():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT StudentId, Name FROM Student")
    students = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('select_student.html', students=students)


@app.route('/building_report')
def building_report():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT B.BuildingId,
               COUNT(DISTINCT R.RoomNumber) AS TotalRooms,
               SUM(R.NumBedrooms) AS TotalBedrooms,
               SUM(CASE WHEN R.NumBedrooms > (
                   SELECT COUNT(*) FROM Assignment A
                   WHERE A.BuildingId = R.BuildingId AND A.RoomNumber = R.RoomNumber) THEN 1 ELSE 0 END) AS RoomsAvailable,
               SUM(R.NumBedrooms - (
                   SELECT COUNT(*) FROM Assignment A
                   WHERE A.BuildingId = R.BuildingId AND A.RoomNumber = R.RoomNumber)) AS BedroomsAvailable
        FROM Room R
        JOIN Building B ON R.BuildingId = B.BuildingId
        GROUP BY B.BuildingId
    """)
    report = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('building_report.html', report=report)

@app.route('/complex_query')
def complex_query():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT S.Name, B.Name AS BuildingName, R.RoomNumber, R.NumBedrooms
        FROM Student S
        JOIN Assignment A ON S.StudentId = A.StudentId
        JOIN Room R ON A.RoomNumber = R.RoomNumber AND A.BuildingId = R.BuildingId
        JOIN Building B ON R.BuildingId = B.BuildingId
        WHERE S.WantsAC = 1 AND R.HasAC = 1 AND B.HasDining = 1
    """)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('complex_query.html', results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
