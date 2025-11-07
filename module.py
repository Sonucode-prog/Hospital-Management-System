import sqlite3

conn = sqlite3.connect('hospita.db')
curr=conn.cursor()




query='''
    CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'doctor', 'patient')) NOT NULL);
        '''
curr.execute(query)
conn.commit()

#doctors table
query='''
     CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        fullname TEXT NOT NULL,
        specialization TEXT NOT NULL,
        department TEXT NOT NULL,
        experience INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
        '''
curr.execute(query)
conn.commit()



# patients table
query='''
     CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        fullname TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        contact TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
        );
         '''
curr.execute(query)
conn.commit()



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
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        );
        '''
curr.execute(query)
conn.commit()



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
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    );
    '''
curr.execute(query)
conn.commit()



#Availability
query='''
      CREATE TABLE IF NOT EXISTS availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        morning_slot TEXT,
        afternoon_slot TEXT,
        evening_slot TEXT,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    );
    '''
curr.execute(query)
conn.commit()



#department
query='''
      CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        overview TEXT
    );
    '''
curr.execute(query)
conn.commit()

  
    
curr.close()
conn.close()