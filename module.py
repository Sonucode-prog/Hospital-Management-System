import sqlite3

def host_get_db():
    conn = sqlite3.connect('hospital.db')
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # enforce FK constraints
    return conn


def create_tables(): 
    conn=host_get_db()
    curr=conn.cursor()
    
    query='''
        CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin', 'doctor', 'patient')) NOT NULL);
            '''
    curr.execute(query)
    
    
    #doctors table
    query='''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fullname TEXT NOT NULL,
            specialization TEXT NOT NULL,
            department TEXT NOT NULL,
            experience INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
            '''
    curr.execute(query)



    # patients table
    query='''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fullname TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            contact TEXT,
            blood_group TEXT,
            height INTEGER,
            weight INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            '''
    curr.execute(query)


    #appointments
    query='''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            department TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT CHECK(status IN ('booked', 'cancelled', 'completed')) DEFAULT
            'booked',
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
            );
            '''
    curr.execute(query)



    # patients history
    query='''
        CREATE TABLE IF NOT EXISTS patient_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            visit_type TEXT,
            tests_done TEXT,
            diagnosis TEXT,
            prescription TEXT,
            medicines TEXT,
            visit_date TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
        );
        '''
    curr.execute(query)



    #Availability
    query = '''
    CREATE TABLE IF NOT EXISTS availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        morning_slot TEXT,
        evening_slot TEXT,

        UNIQUE(doctor_id, date),

        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
    );
   '''
    curr.execute(query)



    #department
    query='''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            overview TEXT
        );
        '''
    curr.execute(query)

  
    conn.commit()
    curr.close()
    conn.close()
    
def insert_user_register(fullname,username, password, role, age, gender, contact, blood_group, height, weight):
    
    try:
        conn = host_get_db()
        curr = conn.cursor()
        
        query='''
        INSERT into users(fullname,username, password, role)
        VALUES(?,?,?,?)'''
        
        curr.execute(query, (fullname,username, password, role))

        user_id=curr.lastrowid #Get newly created user.id
        
        query='''
        INSERT into patients(user_id, fullname, age, gender, contact, blood_group, height, weight)
        VALUES(?,?,?,?,?,?,?,?)'''
        
        curr.execute(query, (user_id, fullname, age, gender, contact, blood_group, height, weight))
        conn.commit()
        
    except Exception as e:
        print("DB INSERT ERROR:", e)
        raise e
    
    finally:
        if curr: curr.close()
        if conn: conn.close()
        
def insert_doctor(fullname, username, password, role, specialization, department, overview, experience):
    
    try:
        conn = host_get_db()
        curr = conn.cursor()
        
        query='''
        INSERT into users(fullname,username, password, role)
        VALUES(?,?,?,?)'''
        
        curr.execute(query, (fullname,username, password, role))
        
        user_id=curr.lastrowid #Get newly created user.id
        
        query='''
        INSERT into doctors (user_id, fullname, specialization, department, experience)
        VALUES(?,?,?,?,?)'''
        
        curr.execute(query, (user_id, fullname, specialization, department, experience))
        
        query='''
        INSERT into departments (username, name, overview)
        VALUES(?,?,?)'''
        
        curr.execute(query, (username, department, overview))
        conn.commit()
    except Exception as e:
        print("DB INSERT ERROR:", e)
        raise e
    
    finally:
        if curr: curr.close()
        if conn: conn.close()
    
    
def get_user(username, password):
    
    try:
        conn=host_get_db()
        curr=conn.cursor()
        curr.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        row=curr.fetchone()
        return row
    except Exception as e:
        print("DB INSERT ERROR:", e)
        raise e
    
    finally:
        if curr: curr.close()
        if conn: conn.close()
    
# ------------------------------
#  GET ALL DOCTORS
# ------------------------------
def get_all_doctors():
    conn = None
    curr = None
    try:
        conn = host_get_db()
        curr = conn.cursor()

        query = "SELECT id, fullname, department FROM doctors"
        curr.execute(query)
        return curr.fetchall()

    except Exception as e:
        print("DB ERROR in get_all_doctors():", e)
        return []

    finally:
        if curr: curr.close()
        if conn: conn.close()


# ------------------------------
#  GET ALL PATIENTS
# ------------------------------
def get_all_patients():
    conn = None
    curr = None
    try:
        conn = host_get_db()
        curr = conn.cursor()

        query = "SELECT id,fullname, age, gender FROM patients"
        curr.execute(query)
        return curr.fetchall()

    except Exception as e:
        print("DB ERROR in get_all_patients():", e)
        return []

    finally:
        if curr: curr.close()
        if conn: conn.close()


# ------------------------------
#  SEARCH DOCTORS
# ------------------------------
def search_doctors(q):
    conn = None
    curr = None
    try:
        conn = host_get_db()
        curr = conn.cursor()

        query = """
            SELECT id,fullname, department 
            FROM doctors 
            WHERE fullname LIKE ? OR department LIKE ?
        """
        curr.execute(query, (q, q))
        return curr.fetchall()

    except Exception as e:
        print("DB ERROR in search_doctors():", e)
        return []

    finally:
        if curr: curr.close()
        if conn: conn.close()


# ------------------------------
#  SEARCH PATIENTS
# ------------------------------
def search_patients(q):
    conn = None
    curr = None
    try:
        conn = host_get_db()
        curr = conn.cursor()

        query = """
            SELECT id,fullname, age, gender 
            FROM patients 
            WHERE fullname LIKE ?
        """
        curr.execute(query, (q,))
        return curr.fetchall()

    except Exception as e:
        print("DB ERROR in search_patients():", e)
        return []

    finally:
        if curr: curr.close()
        if conn: conn.close()
        
        
def get_unique_departments():
    try:
        conn = host_get_db()
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT department FROM doctors ORDER BY department ASC")
        data = cur.fetchall()
        return data

    except Exception as e:
        print("DB INSERT ERROR:", e)
        raise e
    
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
        
def get_patient_appointments(patient_id):
    conn = host_get_db()
    curr = conn.cursor()

    curr.execute("""
        SELECT a.id, d.fullname AS doctor, d.department, a.date, a.time
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.patient_id=? AND a.status='booked'
        ORDER BY a.date ASC
    """, (patient_id,))

    data = curr.fetchall()

    curr.close()
    conn.close()
    return data

def get_patient_by_id(patient_id):
    conn = host_get_db()
    curr = conn.cursor()

    curr.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
    row = curr.fetchone()

    curr.close()
    conn.close()
    return row

def get_doctor_upcoming_appointments(doctor_id):
    conn = host_get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            a.id,
            u.fullname AS patient,
            a.date,
            a.time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE a.doctor_id = ? 
          AND a.date >= date('now')
        ORDER BY a.date ASC
    """, (doctor_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_assigned_patients(doctor_id):
    conn = host_get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT 
            u.fullname,
            p.id AS patient_id
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE a.doctor_id = ?
    """, (doctor_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_doctor_by_id(doctor_id):
    conn = host_get_db()
    curr = conn.cursor()

    curr.execute("SELECT * FROM doctors WHERE id=?", (doctor_id,))
    row = curr.fetchone()

    curr.close()
    conn.close()
    return row






