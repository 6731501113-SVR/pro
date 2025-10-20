import mysql.connector
from mysql.connector import Error

from app import get_db_connection

def test_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="test", # ลองใช้ root ก่อน
            password="test" # ลองว่างก่อน
        )
        
        if connection.is_connected():
            print("✅ MySQL Connected Successfully!")
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ MySQL Connection Error: {e}")
        return False
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM book")
books = cursor.fetchall()
print(books)

if __name__ == "__main__":
    test_mysql_connection()
