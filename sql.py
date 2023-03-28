import sqlite3
from dateutil.parser import parse
import os

# Obtener el directorio base del archivo actual
base_dir = os.path.dirname(os.path.abspath(__file__))

# Unir el directorio base con el nombre del archivo de la base de datos
db_path = os.path.join(base_dir, 'delegations.db')







def init_db():
    conn = sqlite3.connect("delegations.db",
                     detect_types=sqlite3.PARSE_DECLTYPES)

    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS delegations
                      (delegator TEXT PRIMARY KEY UNIQUE, hp_delegated REAL, date TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS max_op_count
                      (id INTEGER PRIMARY KEY, value INTEGER)''')

    conn.commit()
    conn.close()


def save_max_op_count(value):
    conn = sqlite3.connect("delegations.db",
                     detect_types=sqlite3.PARSE_DECLTYPES)

    cursor = conn.cursor()

    cursor.execute('''INSERT OR REPLACE INTO max_op_count VALUES (?, ?)''', (1, value))

    conn.commit()
    conn.close()


def get_saved_max_op_count():
    conn = sqlite3.connect("delegations.db",
                     detect_types=sqlite3.PARSE_DECLTYPES)

    cursor = conn.cursor()

    cursor.execute('''SELECT value FROM max_op_count WHERE id = ?''', (1,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None


def save_results_to_db(results):
    conn = sqlite3.connect("delegations.db",
                     detect_types=sqlite3.PARSE_DECLTYPES)

    cursor = conn.cursor()

    for result in results:
        cursor.execute('''SELECT * FROM delegations WHERE delegator = ?''', (result["Delegador"],))
        existing_record = cursor.fetchone()

        if existing_record:
            existing_date = parse(existing_record[2])
            new_date = parse(result["Fecha"])

            if new_date > existing_date:
                cursor.execute('''UPDATE delegations SET hp_delegated = ?, date = ? WHERE delegator = ?''',
                               (result["HP delegado"], result["Fecha"], result["Delegador"]))
        else:
            cursor.execute('''INSERT INTO delegations VALUES (?, ?, ?)''',
                           (result["Delegador"], result["HP delegado"], result["Fecha"]))

    conn.commit()
    conn.close()