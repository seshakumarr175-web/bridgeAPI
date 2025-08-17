from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

# -------------------------------
# Database connection settings
# -------------------------------
server = 'sqldatabasedem.database.windows.net'   # e.g., mydbserver.database.windows.net
database = 'sampledb'
username = 'mysksql'                    # e.g., myuser@mydbserver
password = 'Sesha17@'
driver = '{ODBC Driver 17 for SQL Server}'    # Make sure this driver is installed

# Function to get connection
def get_db_connection():
    conn = pyodbc.connect(
        f'Driver={driver};'
        f'Server={server};'
        f'Database={database};'
        f'Uid={username};'
        f'Pwd={password};'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=30;'
    )
    return conn


# -------------------------------
# Endpoint to POST data
# -------------------------------
@app.route('/sendData', methods=['POST'])
def send_data():
    try:
        data = request.get_json()
        value = data.get("value")

        if not value:
            return jsonify({"status": "error", "message": "No value provided"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Messages' AND xtype='U')
            CREATE TABLE Messages (
                Id INT IDENTITY(1,1) PRIMARY KEY,
                Value NVARCHAR(255)
            )
        """)

        # Insert value
        cursor.execute("INSERT INTO Messages (Value) VALUES (?)", (value,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": f"Value '{value}' inserted"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# -------------------------------
# Endpoint to GET data
# -------------------------------
@app.route('/getData', methods=['GET'])
def get_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT Id, Value FROM Messages")
        rows = cursor.fetchall()

        data = [{"Id": row[0], "Value": row[1]} for row in rows]

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# -------------------------------
# Main Entry
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
