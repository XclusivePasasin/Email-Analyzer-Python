from mysql.connector import connection
from mysql.connector import Error
import os 
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path('.env')
load_dotenv(dotenv_path)

# Connection 
def InsertInformation(generation_code, control_number, receiver_name, issuer_name, issuer_nit, issuer_nrc, date):
    try:
        Connection = connection.MySQLConnection(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        point = Connection.cursor()
         # Insertar datos en la tabla
        Sql = """
        INSERT INTO Invoices (
            GenerationCode,
            ControlNumber,
            ReceiverName,
            IssuerName,
            IssuerNit,
            IssuerNrc,
            Date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """ 
        data = (
            generation_code,
            control_number,
            receiver_name,
            issuer_name,
            issuer_nit,
            issuer_nrc,
            date
        )
        cursor.execute(sql, data)
        conn.commit()
        print("Data inserted successfully.")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
            if conn.is_connected():
                cursor.close()
                conn.close()