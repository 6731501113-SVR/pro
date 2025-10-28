from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from dbprofile import host, user, password

#Database Connection Setup
app = Flask(__name__)
app.secret_key = 'my_secret_key_here'

def get_db_connection():
    return mysql.connector.connect(
        host=host,  
        user=user,
        password=password,
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


@app.route('/Licence')
def licence():
    return render_template('licence.html')

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

@app.route('/cart')
def cart():
    # ดึงตะกร้าจาก session (เก็บเป็น list ของ book_id)
    cart = session.get('cart', [])
    books = []
    if cart:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM book WHERE BOOKID IN (%s)" % ','.join(['%s'] * len(cart))
            cursor.execute(query, tuple(cart))
            books = cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('cart.html', books=books)

@app.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    cart = session.get('cart', [])
    if book_id not in cart:
        cart.append(book_id)
        session['cart'] = cart
        flash("✅ เพิ่มหนังสือลงตะกร้าแล้ว", "success")
    else:
        flash("⚠️ หนังสือนี้อยู่ในตะกร้าแล้ว", "warning")
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        flash("💳 ชำระเงินสำเร็จ ขอบคุณที่ใช้บริการ!", "success")
        session.pop('cart', None)
        return redirect(url_for('index'))
    return render_template('checkout.html')

@app.route('/my_books')
def my_books():
    if 'user_id' not in session:
        flash("⚠️ กรุณาเข้าสู่ระบบก่อน", "warning")
        return redirect(url_for('login'))
    # ตัวอย่าง: ดึงหนังสือที่ user ยืมไว้ (เชื่อมกับ DB จริงภายหลัง)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.* FROM borrowed_books bb
        JOIN book b ON bb.book_id = b.BOOKID
        WHERE bb.user_id = %s
    """, (session['user_id'],))
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('my_books.html', books=books)


if __name__ == "__main__":
    app.run(debug=True)
