from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from dbprofile import host, user, password
import os
from werkzeug.utils import secure_filename
from datetime import date


#Database Connection Setup
app = Flask(__name__)
app.secret_key = 'my_secret_key_here'
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    return mysql.connector.connect(
        host=host,  
        user=user,
        password=password,
        database="book"
    )
#File check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        print(f"❌ Error fetching books: {e} ❌")
        return render_template("index.html", books=[], error=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT * FROM book
                WHERE BOOKNAME LIKE %s OR WRITER LIKE %s
            """
            like_query = f"%{query}%"
            cursor.execute(sql, (like_query, like_query, like_query))
            results = cursor.fetchall()
        except Exception as e:
            flash(f"❌ error: {e} ❌", "danger")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("search_result.html", query=query, results=results)


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
        print(f"❌ Error fetching books: {e} ❌")
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
                #store user session
                session['user_id'] = user['USER_ID']
                session['user_name'] = user['FIRST_NAME']
                session['user_profile'] = user.get('USER_IMG', 'profile.jpg')

                flash(f"😎 Welcome {user['FIRST_NAME']} 😎", "success")
                return redirect('/')
            else:
                flash("‼️ Invalid email or password ‼️", "danger")

        except Error as e:
            flash(f"❌ Database error: {e} ❌", "danger")
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

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM book")
        books = cursor.fetchall()
        print("✅ BOOK data fetched: ", books, " ✅")  # look console
        return render_template("book.html", books=books)
    except Exception as e:
        print(f"❌ Database error: {e} ❌")
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

        # got book detail
        cursor.execute("SELECT * FROM book WHERE BOOKID = %s", (book_id,))
        book = cursor.fetchone()

        # got book score
        cursor.execute("""
            SELECT AVG(SCORE) AS avg_score, COUNT(*) AS total_review
            FROM review
            WHERE BOOKID = %s
        """, (book_id,))
        rating = cursor.fetchone()

        # got book review
        cursor.execute("""
            SELECT SCORE, REVIEW
            FROM review
            WHERE BOOKID = %s
            ORDER BY SCORE DESC
        """, (book_id,))
        reviews = cursor.fetchall()


    finally:
        cursor.close()
        conn.close()

    return render_template(
        'book_detail.html', 
        book=book,
        rating=rating,
        reviews=reviews
    )


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
            cursor = conn.cursor(dictionary=True, buffered=True)

            # check gmail already exist
            cursor.execute("SELECT GMAIL FROM users WHERE GMAIL = %s", (gmail,))
            existing = cursor.fetchone()

            if existing:
                flash("❌ Email already exists, please use another email. ❌", "danger")
                return redirect(url_for('register'))

            # if not exist → INSERT
            cursor.execute("""
                INSERT INTO users (FIRST_NAME, LAST_NAME, GMAIL, USER_PASSWORD, BIRTHDAY)
                VALUES (%s, %s, %s, %s, %s)
            """, (first_name, last_name, gmail, password, birthday))
            
            conn.commit()
            flash("✅ Register successful! ✅", "success")
            return redirect(url_for('login'))

        except Error as e:
            flash(f"❌ Database error: {e} ❌", "danger")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('register.html', date=date)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("⚠️ Please log in first ⚠️", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM users
            WHERE USER_ID = %s
        """, (user_id,))
        
        user = cursor.fetchone()

        if not user:
            flash("‼️ No user ‼️", "danger")
            return redirect(url_for('index'))

    except Exception as e:
        flash(f"❌ Error: {e} ❌", "danger")
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("profile.html", user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash("⚠️ Please log in first ⚠️", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gmail = request.form['gmail']
        birthday = request.form['birthday']

        # Password fields
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        profile_image = request.files.get('profile_image')
        filename = session.get('user_profile', 'profile.jpg')

        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        try:
            #update profile
            cursor.execute("""
                UPDATE users SET FIRST_NAME=%s, LAST_NAME=%s, GMAIL=%s, BIRTHDAY=%s, USER_IMG=%s
                WHERE USER_ID=%s
            """, (first_name, last_name, gmail, birthday, filename, user_id))
            conn.commit()

            #change password (optional)
            if old_password or new_password or confirm_password:
                cursor.execute("SELECT USER_PASSWORD FROM users WHERE USER_ID=%s", (user_id,))
                current_pw = cursor.fetchone()['USER_PASSWORD']

                if old_password != current_pw:
                    flash("❌ Old password is incorrect! ❌", "danger")
                    return redirect(url_for('edit_profile'))

                if new_password != confirm_password:
                    flash("❌ New passwords do not match! ❌", "danger")
                    return redirect(url_for('edit_profile'))

                cursor.execute("""
                    UPDATE users SET USER_PASSWORD=%s WHERE USER_ID=%s
                """, (new_password, user_id))
                conn.commit()
                flash("✅ Password changed successfully! ✅", "success")

            session['user_name'] = first_name
            session['user_profile'] = filename

            flash("✅ Profile updated successfully! ✅", "success")
            return redirect(url_for('profile'))

        except Error as e:
            flash(f"❌ Error: {e} ❌", "danger")


    cursor.execute("SELECT * FROM users WHERE USER_ID=%s", (user_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('edit_profile.html', user=user)

@app.route('/cart')
def cart():
    #Check login session
    if 'user_id' not in session:
        flash("⚠️ Please log in first ⚠️", "warning")
        return redirect(url_for('login'))
    
    # got cart from session (store as list of book_id)
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
    if 'user_id' not in session:
        flash("⚠️ Please log in first ⚠️", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart = session.get('cart', [])

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        #check borrowed or not
        cursor.execute("""
            SELECT * FROM `order`
            WHERE USER_ID = %s AND BOOKID = %s
        """, (user_id, book_id))
        existing_order = cursor.fetchone()

        if existing_order:
            flash("⚠️ You already borrow this book ⚠️", "warning")
            return redirect(url_for('book_detail', book_id=book_id))

        #check in cart or not
        if book_id in cart:
            flash("⚠️ already in cart ⚠️", "warning")
            return redirect(url_for('book_detail', book_id=book_id))

        #add to cart
        cart.append(book_id)
        session['cart'] = cart
        flash("✅ added ✅", "success")

    except Exception as e:
        flash(f"❌ error ❌: {e}", "danger")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/remove_from_cart/<int:book_id>')
def remove_from_cart(book_id):
    cart = session.get('cart', [])
    if book_id in cart:
        cart.remove(book_id)
        session['cart'] = cart
        flash("😱 Delete Successfully 🗑️", "info")
    else:
        flash("⚠️ No book here ⚠️", "warning")
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash("⚠️ Please log in first ⚠️", "warning")
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    if not cart:
        flash("⚠️ No book here ⚠️", "warning")
        return redirect(url_for('cart'))

    conn = None
    cursor = None

    # got book list from cart
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM book WHERE BOOKID IN (%s)" % ','.join(['%s'] * len(cart))
    cursor.execute(query, tuple(cart))
    books = cursor.fetchall()
    cursor.close()
    conn.close()

    # book fee 10 bath per book
    total_fee = len(books) * 10

    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            for book_id in cart:
                cursor.execute("""
                    INSERT INTO `order` (BOOKID, USER_ID, ORDER_DATE)
                    VALUES (%s, %s, CURRENT_TIMESTAMP())
                """, (book_id, session['user_id']))
            conn.commit()
            flash(f"✅ Borrowd! total Pay {total_fee} Bath ✅", "success")
            session.pop('cart', None)
            return redirect(url_for('my_books'))
        except Exception as e:
            flash(f"❌ error: {e} ❌", "danger")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('checkout.html', books=books, total_fee=total_fee)


@app.route('/my_book')
def my_books():
    #Check Login session
    if 'user_id' not in session:
        flash("⚠️ Please log in first ⚠️", "warning")
        return redirect(url_for('login'))

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # got data from order and join book
        cursor.execute("""
            SELECT b.*, o.ORDER_DATE
            FROM `order` o
            JOIN book b ON o.BOOKID = b.BOOKID
            WHERE o.USER_ID = %s
            ORDER BY o.ORDER_DATE DESC
        """, (session['user_id'],))

        books = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error fetching user books: {e} ❌")
        books = []
        flash("‼️ Can not load book ‼️", "danger")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return render_template('my_book.html', books=books)

@app.route('/preview/<int:book_id>')
def preview_book(book_id):
    
    folder_path = f"static/ebooks/{book_id}/"

    try:
        # got images
        images = []

        for file in sorted(os.listdir(folder_path))[:10]:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                images.append(f"/{folder_path}{file}")

        if len(images) == 0:
            flash("‼️ No preview pages found. ‼️", "danger")
            return redirect(url_for('book_detail', book_id=book_id))

    except:
        flash("‼️ Preview folder not found ‼️", "danger")
        return redirect(url_for('book_detail', book_id=book_id))

    return render_template("preview.html", book_id=book_id, images=images)



@app.route('/read/<int:book_id>')
def read_book(book_id):
    # check login session
    if 'user_id' not in session:
        flash("⚠️ Please log in first ⚠️", "warning")
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM book WHERE BOOKID = %s", (book_id,))
        book = cursor.fetchone()

        if not book:
            flash("‼️ not found this boo ‼️", "danger")
            return redirect(url_for('my_books'))

    finally:
        cursor.close()
        conn.close()

    # loading all images in folder
    folder_path = f"static/ebooks/{book_id}/"
    images = []

    try:
        for file in sorted(os.listdir(folder_path)):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                images.append(f"/{folder_path}{file}")

        if len(images) == 0:
            flash("‼️ No pages found. ‼️", "danger")
            return redirect(url_for('my_books'))

    except:
        flash("‼️ ebook folder not found ‼️", "danger")
        return redirect(url_for('my_books'))

    return render_template("read.html", book=book, images=images)

@app.route('/review/write/<int:book_id>', methods=['GET', 'POST'])
def write_review(book_id):
    if 'user_id' not in session:
        flash("⚠️ Please log in first ⚠️", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        score = request.form.get('score')
        review_text = request.form.get('review')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO review (BOOKID, SCORE, REVIEW)
                VALUES (%s, %s, %s)
            """, (book_id, score, review_text))
            conn.commit()

            flash("✅ Review submitted! ✅", "success")
            return redirect(url_for('book_detail', book_id=book_id))

        except Exception as e:
            flash(f"❌ Error: {e} ❌", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template("write_review.html", book_id=book_id)


@app.route('/return_book/<int:book_id>', methods=['POST'])
def return_book(book_id):
    if 'user_id' not in session:
        flash("⚠️ Please log in first ⚠️", "warning")
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # delete book from user in order
        cursor.execute("""
            DELETE FROM `order`
            WHERE USER_ID = %s AND BOOKID = %s
        """, (session['user_id'], book_id))

        conn.commit()

        if cursor.rowcount > 0:
            flash("✅ Returned 📗", "success")
        else:
            flash("⚠️ No data ⚠️", "warning")

    except Exception as e:
        flash(f"❌ error: {e} ❌", "danger")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('my_books'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
