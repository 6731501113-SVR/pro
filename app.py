from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

#Database Connection Setup
app = Flask(__name__)
app.secret_key = 'my_secret_key_here'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  
        user="test",
        password="test",
        database="book"
    )

#ROUTES             
@app.route('/')
def index():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM book")
        books = cursor.fetchall()
        return render_template("index.html", books=books)


    except Exception as e:
        print(f"❌ Error fetching books: {e}")
        return render_template("index.html", books=[], error=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/login')
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE GMAIL = %s AND USER_PASSWORD = %s", (email, password))
            user = cursor.fetchone()

            if user:
                flash(f"✅ Welcome {user['FIRST_NAME']}!", "success")
                return redirect(url_for('p1'))  # ไปหน้าหลักหลังล็อกอิน
            else:
                flash("❌ Invalid email or password", "danger")

        except Error as e:
            flash(f"❌ Database error: {e}", "danger")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('login.html')

@app.route('/p1')
def p1():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM book")
        books = cursor.fetchall()
        print("✅ BOOK data fetched:", books)  # ดูใน console
        return render_template("p1.html", BAllrows=books)
    except Exception as e:
        print(f"❌ Database error: {e}")
        return render_template("p1.html", BAllrows=[], error=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM book WHERE BOOKID = %s", (book_id,))
        book = cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    if not book:
        return "Book not found", 404

    return render_template('book_detail.html', book=book)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gmail = request.form['gmail']
        password = request.form['password']
        birthday = request.form['birthday']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (FIRST_NAME, LAST_NAME, GMAIL, USER_PASSWORD, BIRTHDAY)
                VALUES (%s, %s, %s, %s, %s)
            """, (first_name, last_name, gmail, password, birthday))
            conn.commit()
            flash("✅ Register successful!", "success")
            return redirect(url_for('login'))
        except Error as e:
            flash(f"❌ Error: {e}", "danger")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)
