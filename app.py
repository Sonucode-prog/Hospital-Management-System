import module
module.create_tables()
from flask import Flask, render_template, request, redirect, url_for,session


app=None
def created_app():                                   
    app = Flask(__name__)
    app.secret_key = "sonu_unique_key_987654"
    app.debug=True
    app.app_context().push() 
    return app
app= created_app()


@app.route("/", methods=["GET","POST"])
def login():
    try:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            role = request.form.get("role")

            user = module.get_user(username, password)

            # Admin login
            if username=="admin" and password=="admin000" and role=="admin":
                return redirect(url_for("admin"))

            if user:
                role = user["role"]

                # Doctor login
                if role == "doctor":

                    if role == "doctor":
                        conn = module.host_get_db()
                        cur2 = conn.cursor()
                        cur2.execute("SELECT id FROM doctors WHERE user_id=?", (user["id"],))
                        doc = cur2.fetchone()

                        if doc:
                            session["doctor_id"] = doc["id"]
                            print("LOGIN doctor_id =", doc["id"])
                        else:
                            print("ERROR: doctor record not found in doctors table")

                        cur2.close()
                        return redirect(url_for("doctor"))



                # Patient login
                elif role == "patient":
                    conn = module.host_get_db()
                    cur2 = conn.cursor()
                    cur2.execute("SELECT id FROM patients WHERE user_id=?", (user["id"],))
                    pat = cur2.fetchone()

                    session["patient_id"] = pat["id"]
                    return redirect(url_for("patient_dash"))


            else:
                return "Invalid username or password"

        return render_template("login.html")

    except Exception as e:
        print("Error in /login route:", e)
        return "Something went wrong", 500


@app.route("/registration", methods=["GET","POST"])
def registration():
    
    try:
        if request.method == "POST":
            fullname = request.form.get("fullname")
            username = request.form.get("username")
            password = request.form.get("password")
            role     = request.form.get("role") 
            age      = request.form.get("age") or None
            gender   = request.form.get("gender") or None
            contact  = request.form.get("contact") or None
            blood_group = request.form.get("blood") or None
            height       = request.form.get("height") or None
            weight       = request.form.get("weight") or None
            
            module.insert_user_register(fullname, username, password, role, age,gender,contact, blood_group, height, weight)
            
            return redirect(url_for("login"))
        return render_template("registration.html")
    
    except Exception as e:
        print("Error in /registration route:", e)
        return "Something went wrong(Please change your username)",500


@app.route("/admin")
def admin():
    try:
        category = request.args.get("category")
        q = request.args.get("q", "")

        conn = module.host_get_db()
        curr = conn.cursor()

        # Always load appointments
        curr.execute("""
            SELECT 
                a.id,
                u1.fullname AS patient,
                u2.fullname AS doctor,
                d.department AS department,
                a.date,
                a.time,
                p.id AS patient_id
            FROM appointments a
            JOIN patients p       ON a.patient_id = p.id
            JOIN users u1         ON p.user_id = u1.id
            JOIN doctors d        ON a.doctor_id = d.id
            JOIN users u2         ON d.user_id = u2.id
            WHERE a.date >= date('now')
        """)
        appointments = curr.fetchall()

        # ========== NO SEARCH ==========
        if not q:
            doctors = module.get_all_doctors()
            patients = module.get_all_patients()

            curr.close()
            return render_template(
                "admin.html",
                doctors=doctors,
                patients=patients,
                appointments=appointments
            )

        # ========== WITH SEARCH ==========
        q = f"%{q}%"

        if category == "doctor":
            doctors = module.search_doctors(q)
            patients = module.get_all_patients()    # full list

        elif category == "patient":
            patients = module.search_patients(q)
            doctors = module.get_all_doctors()      # full list

        else:
            # fallback: show all
            doctors = module.get_all_doctors()
            patients = module.get_all_patients()

        curr.close()

        return render_template(
            "admin.html",
            doctors=doctors,
            patients=patients,
            appointments=appointments
        )

    except Exception as e:
        print("Error in /admin route:", e)
        return "Something went wrong", 500


@app.route("/add_doct", methods=["GET", "POST"])
def add_doct():
    
    try:
        if request.method == "POST":
            fullname=request.form.get("fullname")
            username=request.form.get("username")
            password = request.form.get("password")
            role="doctor"
            specialization=request.form.get("specialization")
            department=request.form.get("department")
            overview=request.form.get("overview")
            experience=request.form.get("experience")
            
            module.insert_doctor(fullname, username, password, role, specialization, department, overview, experience)
            return redirect(url_for("admin"))

        return render_template("add_doctor.html")
    except Exception as e:
        print("Error in /add_doctor route:", e)
        return "Something went wrong", 500

@app.route("/p_history")
def p_history():
    try:
        patient_id = session.get("patient_id")

        # patient must be logged in
        if not patient_id:
            return redirect("/login")

        conn = module.host_get_db()
        cur = conn.cursor()

        # Get patient information
        cur.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        patient = cur.fetchone()

        if not patient:
            cur.close()
            conn.close()
            return "Patient not found"

        # Get patient full history
        cur.execute("""
            SELECT ph.*, d.fullname AS doctor_name, d.department
            FROM patient_history ph
            JOIN doctors d ON ph.doctor_id = d.id
            WHERE ph.patient_id = ?
            ORDER BY ph.id ASC
        """, (patient_id,))

        history = cur.fetchall()

        cur.close()
        conn.close()

        return render_template("patient_history.html",
                               patient=patient,
                               history=history)

    except Exception as e:
        print("ERROR in /p_history:", e)
        return "Error loading history"


@app.route("/doctor")
def doctor():
    doctor_id = session.get("doctor_id")
    
    doctors=module.get_all_doctors()
    upcoming = module.get_doctor_upcoming_appointments(doctor_id)
    assigned = module.get_assigned_patients(doctor_id)

    return render_template(
        "doctor.html",
        doctors=doctors,
        upcoming=upcoming,
        assigned=assigned
    )


@app.route("/patient_dash")
def patient_dash():
    patient_id = session["patient_id"]

    patient = module.get_patient_by_id(patient_id)
    departments = module.get_unique_departments()
    appointments = module.get_patient_appointments(patient_id)

    return render_template(
        "patient.html",
        patient=patient,
        departments=departments,
        upcoming=appointments
    )


@app.route("/doctor_profile/<int:doctor_id>")
def doctor_profile(doctor_id):
    try:
        conn = module.host_get_db()
        cur = conn.cursor()

        # Fetch doctor info
        cur.execute("""
            SELECT fullname, specialization, experience, department
            FROM doctors
            WHERE id=?
        """, (doctor_id,))
        doctor = cur.fetchone()

        # Fetch overview from departments table
        cur.execute("""
            SELECT overview FROM departments
            WHERE name=?
        """, (doctor["department"],))
        overview = cur.fetchone()

        return render_template(
            "prof_doctor.html",
            doctor=doctor,
            overview=overview["overview"],
            doctor_id=doctor_id
        )
    except Exception as e:
        print("ERROR in doctor_profile:", e)
        return "Error loading doctor profile"
    finally:
        if cur: cur.close()
        if conn: conn.close()   



@app.route("/edit_doct/<int:id>", methods=["GET","POST"])
def edit_doct(id):
    conn = module.host_get_db()
    curr = conn.cursor()

    # GET doctor row
    curr.execute("""
        SELECT d.*, u.fullname AS user_fullname, u.username 
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE d.id = ?
    """, (id,))
    doctor = curr.fetchone()

    if not doctor:
        curr.close()
        conn.close()
        return "Doctor not found", 404

    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]
        role     = "doctor"
        specialization = request.form["specialization"]
        department = request.form["department"]
        overview = request.form["overview"]
        experience = request.form["experience"]
        
        #UPDATE users table
        
        curr.execute("""
                UPDATE users
                SET fullname=?, username=?, password=?, role=?
                WHERE id=?
            """, (fullname, username, password, role ,doctor["user_id"]))

        # UPDATE doctors table
        curr.execute("""
            UPDATE doctors
            SET fullname=?, specialization=?, department=?, experience=?
            WHERE id=?
        """, (fullname, specialization, department, experience, id))

        # UPDATE users table name also
        curr.execute("""
            UPDATE users
            SET fullname=?
            WHERE id=?
        """, (fullname, doctor["user_id"]))

        # UPDATE departments table (if needed)
        curr.execute("""
            UPDATE departments
            SET overview=?
            WHERE name=?
        """, (overview, department))

        conn.commit()
        curr.close()
        conn.close()

        return redirect("/admin")

    curr.close()
    conn.close()

    return render_template("edit_doct.html", doctor=doctor)


@app.route("/edit_pati/<int:id>", methods=["GET","POST"])
def edit_pati(id):
    conn = module.host_get_db()
    curr = conn.cursor()

    if request.method == "POST":
        fullname = request.form["fullname"]
        
        age = request.form["age"]
        gender = request.form["gender"]
        contact = request.form["contact"]

        query = """
            UPDATE patients
            SET fullname = ?, age = ?, gender = ?, contact = ?
            WHERE id = ?
        """
        curr.execute(query, (fullname, age, gender, contact, id))
        conn.commit()

        curr.close()
        conn.close()

        return redirect("/admin")

    query = "SELECT * FROM patients WHERE id=?"
    curr.execute(query, (id,))
    data = curr.fetchone()
    curr.close()
    conn.close()

    return render_template("edit_pati.html", patient=data)


@app.route('/delete_patient/<int:id>')
def delete_patient(id):
    try:
        conn = module.host_get_db()
        curr = conn.cursor()

        #Find related user_id
        curr.execute("SELECT user_id FROM patients WHERE id=?", (id,))
        pat = curr.fetchone()

        if pat:
            user_id = int(pat["user_id"])

            curr.execute("DELETE FROM users WHERE id=?", (user_id,))

        conn.commit()

        return redirect("/admin")

    except Exception as e:
        print("DELETE ERROR:", e)
        return "Error deleting patient"

    finally:
        curr.close()
        conn.close()
        

@app.route('/delete_doctor/<int:id>')
def delete_doctor(id):
    try:
        conn = module.host_get_db()
        curr = conn.cursor()

        #Find related user_id
        curr.execute("SELECT user_id FROM doctors WHERE id=?", (id,))
        doc = curr.fetchone()

        if doc:
            user_id = doc["user_id"]

            #Delete from users (THIS will cascade & delete doctor automatically)
            curr.execute("DELETE FROM users WHERE id=?", (user_id,))

        conn.commit()

        return redirect("/admin")

    except Exception as e:
        print("DELETE ERROR:", e)
        return "Error deleting doctor"

    finally:
        curr.close()
        conn.close()
        
        
@app.route("/doctor_availability", methods=["GET", "POST"])
def doctor_availability():
    
    try:
        db = module.host_get_db()
        cur = db.cursor()

        #doctor ID from login session
        doctor_id = session.get("doctor_id")
        print("DEBUG doctor_id =", doctor_id)
        
        cur.execute("SELECT id, fullname FROM doctors")
        print("DOCTOR TABLE =", cur.fetchall())

        if doctor_id is None:
            return "Doctor not logged in", 401

        # Select date
        selected_date = request.args.get("date")

        # No date yet → show only date picker
        if not selected_date:
            return render_template("doctor_availability.html", date=None, slots=None)

        # Ensure row exists for this doctor and date
        cur.execute("""
            INSERT OR IGNORE INTO availability (doctor_id, date)
            VALUES (?, ?)
        """, (doctor_id, selected_date))
        db.commit()

        # Handle slot update
        if request.method == "POST":
            slot = request.form["slot"]  # morning/evening/afternoon
            cur.execute(f"""
                UPDATE availability
                SET {slot}_slot = 'available'
                WHERE doctor_id=? AND date=?
            """, (doctor_id, selected_date))
            db.commit()

        # Load availability for that doctor + date
        cur.execute("""
            SELECT morning_slot, evening_slot
            FROM availability
            WHERE doctor_id=? AND date=?
        """, (doctor_id, selected_date))

        slots = cur.fetchone()

        return render_template("doctor_availability.html",
                            date=selected_date,
                            slots=slots)
    except Exception as e:
        print("ERROR:", e)
        return "Error loading availability"
    finally:
        if cur: cur.close()
        if db: db.close()


@app.route("/patient/book/<int:doctor_id>/<date>")
def patient_book(doctor_id, date):
    
    try:
        conn = module.host_get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT morning_slot, evening_slot 
            FROM availability
            WHERE doctor_id=? AND date=?
        """, (doctor_id, date))

        row = cur.fetchone()
        morning, evening = row

        return render_template("patient_book.html",
                            date=date,
                            doctor_id=doctor_id,
                            morning=morning,
                            evening=evening)
    except Exception as e:
        print("ERROR in /patient/book:", e)
        return "Error loading booking page"
    finally:
        if cur: cur.close()
        if conn: conn.close()    
    
    
@app.route("/confirm_booking", methods=["POST"])
def confirm_booking():
    try:
        doctor_id = request.form["doctor_id"]
        date = request.form["date"]
        time = request.form["slot"]
        patient_id = 10  # Example

        conn = module.host_get_db()
        cur = conn.cursor()

        # Save booking
        cur.execute("""
            INSERT INTO appointments (patient_id, doctor_id, date, time, department)
            VALUES (?, ?, ?, ?, 'General')
        """, (patient_id, doctor_id, date, time))

        conn.commit()

        return "Appointment Confirmed!"
    except Exception as e:
        print("ERROR in /confirm_booking:", e)
        return "Error confirming booking"   
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route("/department/<dept>")
def department_details(dept):
    try:
        conn = module.host_get_db()
        cur = conn.cursor()

        # Get department overview
        cur.execute("SELECT overview FROM departments WHERE name=?", (dept,))
        overview = cur.fetchone()

        # Get doctors in this department
        cur.execute("""
            SELECT id, fullname 
            FROM doctors 
            WHERE department=?
        """, (dept,))
        doctors = cur.fetchall()

        return render_template(
            "department_details.html",
            department=dept,
            overview=overview,
            doctors=doctors
        )
    except Exception as e:
        print("ERROR in /department/<dept>:", e)
        return "Error loading department details"
    
    finally:
        if cur: cur.close()
        if conn: conn.close()
    
@app.route("/check_availability/<int:doctor_id>", methods=["GET", "POST"])
def check_availability(doctor_id):
    try:
        conn = module.host_get_db()
        cur = conn.cursor()

        # Get doctor info
        cur.execute("SELECT fullname FROM doctors WHERE id=?", (doctor_id,))
        doctor = cur.fetchone()

        if doctor is None:
            return "Doctor not found", 404

        # Fetch all availability rows
        cur.execute("""
            SELECT id, date, morning_slot, evening_slot
            FROM availability
            WHERE doctor_id=?
            ORDER BY date ASC
        """, (doctor_id,))
        slots = cur.fetchall()

       # === BOOKING ===
        if request.method == "POST":
            slot_id = request.form.get("slot_id")
            date = request.form.get("date")
            time = request.form.get("time")

            patient_id = session.get("patient_id")

            if patient_id is None:
                return "Patient not logged in", 401

            # CHECK IF SLOT ALREADY BOOKED
            cur.execute("""
                SELECT id FROM appointments
                WHERE doctor_id=? AND date=? AND time=?
            """, (doctor_id, date, time))

            exists = cur.fetchone()

            if exists:
                # Slot already booked → show error popup
                return render_template(
                    "availability.html",
                    doctor=doctor,
                    slots=slots,
                    error=f"⚠ Slot {time} on {date} is already booked!"
                )

            #SAVE NEW APPOINTMENT
            cur.execute("""
                INSERT INTO appointments(patient_id, doctor_id, department, date, time)
                VALUES(?, ?, ?, ?, ?)
            """, (patient_id, doctor_id, doctor["fullname"], date, time))

            conn.commit()

            #Reload updated slots
            cur.execute("""
                SELECT id, date, morning_slot, evening_slot
                FROM availability
                WHERE doctor_id=?
                ORDER BY date ASC
            """, (doctor_id,))
            slots = cur.fetchall()

            success = f"✔ Appointment booked for {date} at {time}!"

            return render_template(
                "availability.html",
                doctor=doctor,
                slots=slots,
                success=success
            )


        # === DEFAULT GET ===
        return render_template("availability.html", doctor=doctor, slots=slots)

    except Exception as e:
        print("ERROR in /check_availability:", e)
        return "Error loading availability"

    finally:
        if cur: cur.close()
        if conn: conn.close()
        
@app.route("/cancel_appointment/<int:appointment_id>")
def cancel_appointment(appointment_id):
    try:
        patient_id = session.get("patient_id")
        if not patient_id:
            return "Patient not logged in", 401

        conn = module.host_get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM appointments 
            WHERE id=? AND patient_id=?
        """, (appointment_id, patient_id))
        
        appt = cur.fetchone()

        if not appt:
            return "Unauthorized", 403

        cur.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
        conn.commit()

        return redirect("/patient_dash?cancelled=1")

    except Exception as e:
        print("ERROR in /cancel_appointment:", e)
        return "Error cancelling appointment"

    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/doctor/update_history/<int:appointment_id>', methods=['GET', 'POST'])
def update_history(appointment_id):
    
    try:

        conn = module.host_get_db()
        cur = conn.cursor()

        # Fetch appointment + patient + doctor details
        cur.execute("""
            SELECT a.id, a.date, a.time, 
                p.fullname AS patient_name,
                d.fullname AS doctor_name,
                d.department,
                a.patient_id, a.doctor_id
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.id=?
        """, (appointment_id,))
        
        data = cur.fetchone()

        if request.method == "POST":
            visit_type = request.form.get("visit_type")
            tests_done = request.form.get("tests_done")
            diagnosis = request.form.get("diagnosis")
            prescription = request.form.get("prescription")
            medicines = request.form.get("medicines")

            # Insert history WITHOUT appointment_id
            cur.execute("""
                INSERT INTO patient_history(
                    patient_id, doctor_id, visit_type, tests_done, diagnosis, prescription, medicines
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data["patient_id"],
                data["doctor_id"],
                visit_type,
                tests_done,
                diagnosis,
                prescription,
                medicines
            ))

            # Remove appointment now that it's completed
            cur.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))

            conn.commit()
            return redirect("/doctor")

        return render_template("Update_patient.html", data=data)
    except Exception as e:
        print("ERROR in /update_history:", e)
        return "Error updating patient history" 
    finally:
        if cur: cur.close()
        if conn: conn.close()


        
@app.route('/doctor/cancel/<int:appointment_id>')
def doctor_cancel_appointment(appointment_id):

    try:
        conn = module.host_get_db()
        cur = conn.cursor()

        cur.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
        conn.commit()

        return redirect("/doctor")

    except Exception as e:
        print("CANCEL ERROR:", e)
        return "Error cancelling appointment"

    finally:
        cur.close()
        conn.close()

@app.route('/mark_complete/<int:appointment_id>')
def mark_complete(appointment_id):

    try:
        conn = module.host_get_db()
        cur = conn.cursor()

        # Get appointment info
        cur.execute("""
            SELECT patient_id, doctor_id, date, time
            FROM appointments
            WHERE id=?
        """, (appointment_id,))
        
        appt = cur.fetchone()

        if not appt:
            return "Appointment not found"

        patient_id = appt["patient_id"]
        doctor_id = appt["doctor_id"]

        # Insert into patient_history
        cur.execute("""
            INSERT INTO patient_history(patient_id, doctor_id, visit_type, diagnosis, prescription, visit_date)
            VALUES (?, ?, 'Completed Visit', NULL, NULL, date('now'))
        """, (patient_id, doctor_id))

        # Delete from appointments
        cur.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))

        conn.commit()
        return redirect("/doctor")

    except Exception as e:
        print("MARK COMPLETE ERROR:", e)
        return "Error marking complete"

    finally:
        cur.close()
        conn.close()
        
#for admin view the history of a patient
@app.route("/admin/patient_history/<int:patient_id>")
def admin_patient_history(patient_id):
    try:
        conn = module.host_get_db()
        cur = conn.cursor()

        # Get patient info
        cur.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        patient = cur.fetchone()

        if not patient:
            return "Patient not found"

        # Get full history
        cur.execute("""
            SELECT ph.*, d.fullname AS doctor_name, d.department
            FROM patient_history ph
            JOIN doctors d ON ph.doctor_id = d.id
            WHERE ph.patient_id = ?
            ORDER BY ph.id ASC
        """, (patient_id,))
        history = cur.fetchall()

        return render_template("patient_history.html",
                               patient=patient,
                               history=history)

    except Exception as e:
        print("ERROR in admin_patient_history:", e)
        return "Error loading patient history"

    finally:
        cur.close()
        conn.close()
        
#view of patient history through the doctor
@app.route("/doctor/patient_history/<int:patient_id>")
def doctor_patient_history(patient_id):
    try:
        conn = module.host_get_db()
        cur = conn.cursor()

        # Get patient info
        cur.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        patient = cur.fetchone()

        if not patient:
            return "Patient not found"

        # Get patient history
        cur.execute("""
            SELECT ph.*, d.fullname AS doctor_name, d.department
            FROM patient_history ph
            JOIN doctors d ON ph.doctor_id = d.id
            WHERE ph.patient_id = ?
            ORDER BY ph.id ASC
        """, (patient_id,))
        history = cur.fetchall()

        return render_template("patient_history.html",
                               patient=patient,
                               history=history)

    except Exception as e:
        print("ERROR in doctor_patient_history:", e)
        return "Error loading patient history"

    finally:
        cur.close()
        conn.close()
        
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")



    
    
if __name__ == "__main__":
    app.run(debug=True)
    
