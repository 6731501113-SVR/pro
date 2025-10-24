from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

#Database Connection Setup
app = Flask(__name__)
app.secret_key = 'my_secret_key_here'

def get_db_connection():
    return mysql.connector.connect(
        host="192.168.1.170",  
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

@app.route('/home2')
def home2():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM book")
        books = cursor.fetchall()
        return render_template("home2.html", books=books)


    except Exception as e:
        print(f"❌ Error fetching books: {e}")
        return render_template("home2.html", books=[], error=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/login', methods=['GET', 'POST'])
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
                #เก็บ session ของผู้ใช้
                session['user_id'] = user['USER_ID']
                session['user_name'] = user['FIRST_NAME']
                session['user_profile'] = user.get('USER_IMAGE', 'profile.jpg')

                flash(f"‼️ Welcome {user['FIRST_NAME']} ‼️", "success")
                return redirect('/')
            else:
                flash("‼️ Invalid email or password ‼️", "danger")

        except Error as e:
            flash(f"‼️ Database error: {e} ‼️", "danger")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("‼️ Logged out successfully ‼️", "info")
    return redirect(url_for('login'))

@app.route('/book')
def book():
    #เช็คว่า Login session อยู่รึเปล่า เดี๋ยวเอาไปใส่ตรงอื่น
    if 'user_id' not in session:
        flash("⚠️ Please log in first ⚠️", "warning")
        return redirect(url_for('login'))

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM book")
        books = cursor.fetchall()
        print("✅ BOOK data fetched:", books)  # ดูใน console
        return render_template("book.html", books=books)
    except Exception as e:
        print(f"❌ Database error: {e}")
        return render_template("book.html", books=[], error=str(e))
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
            flash(f"‼️ Error: {e} ‼️", "danger")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)
