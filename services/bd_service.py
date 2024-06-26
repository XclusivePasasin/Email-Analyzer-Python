from mysql.connector import connection, Error
import os 
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path('.env')
load_dotenv(dotenv_path)

def get_db_connection():
    try:
        Connection = connection.MySQLConnection(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return Connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
    
    
def check_generation_code_exists(generation_code):
    Connection = get_db_connection()
    if Connection is None:
        return False
    
    try:
        point = Connection.cursor()
        point.execute("SELECT COUNT(*) FROM Invoices WHERE Generation_Code = %s", (generation_code,))
        result = point.fetchone()
        return result[0] > 0
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if Connection.is_connected():
            point.close()
            Connection.close()

def InsertInformation(data_bd):
    Connection = get_db_connection()
    if Connection is None:
        return
    
    try:
        point = Connection.cursor()
        # Insert data into table
        sql = """
        INSERT INTO Invoices (
            Generation_Code,
            Control_Number,
            Receiver_Name,
            Issuer_Name,
            Issuer_Nit,
            Issuer_Nrc,
            Date,
            File_Path_JSON,
            File_Path_PDF
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """ 
        data = (
            data_bd['generation_code'],
            data_bd['control_number'],
            data_bd['receiver_name'],
            data_bd['issuer_name'],
            data_bd['issuer_nit'],
            data_bd['issuer_nrc'],
            data_bd['date'],
            data_bd['json_path'],
            data_bd['pdf_path']
        )
        point.execute(sql, data)
        Connection.commit()
        print("Data inserted successfully.")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if Connection.is_connected():
            point.close()
            Connection.close()

def get_all_invoices():
    Connection = get_db_connection()
    if Connection is None:
        return []
    
    try:
        point = Connection.cursor(dictionary=True)
        point.execute("SELECT * FROM Invoices")
        invoices = point.fetchall()
        return invoices
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if Connection.is_connected():
            point.close()
            Connection.close()