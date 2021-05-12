from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

app = Flask(__name__)

bcrypt = Bcrypt(app)
app.secret_key = "ashjsrf77755kl%^$##"

DB_NAME = "13dts.db"


def create_connection(db_file):
    """create a connection to the sqlite db"""
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return None


def get_classes():
    con = create_connection(DB_NAME)
    query = "SELECT id, class_name" \
            " FROM tutor_classes ORDER BY class_name ASC"
    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line actually executes the query
    class_list = cur.fetchall()  # puts the results into a list usable in python
    con.close()
    return class_list


@app.route('/')
def render_homepage():
    # connect to the database
    con = create_connection(DB_NAME)
    query = "SELECT id, year_level, schl_id, surname, first_name, tutor_id, email" \
            " FROM students ORDER BY surname, first_name ASC"
    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line actually executes the query
    student_list = cur.fetchall()  # puts the results into a list usable in python
    con.close()

    class_list = get_classes()
    return render_template('home.html', students=student_list, classes=class_list, logged_in=is_logged_in())


@app.route('/class/<tutor_id>')
def render_class(tutor_id):
    # connect to the database
    con = create_connection(DB_NAME)
    query = "SELECT id, year_level, schl_id, surname, first_name, tutor_id, email" \
            " FROM students WHERE tutor_id=? ORDER BY surname, first_name ASC"
    cur = con.cursor()  # You need this line next
    cur.execute(query, (tutor_id, ))  # this line actually executes the query
    student_list = cur.fetchall()  # puts the results into a list usable in python

    query = "SELECT id, class_name" \
            " FROM tutor_classes WHERE id=?" \
            "ORDER BY class_name ASC"
    cur = con.cursor()  # You need this line next
    cur.execute(query, (tutor_id, ))  # this line actually executes the query
    tutor_classes = cur.fetchall()  # puts the results into a list usable in python
    print(tutor_classes)
    tutor_class = tutor_classes[0][1]
    con.close()

    class_list = get_classes()
    return render_template('class.html', students=student_list, classes=class_list, tutor_class=tutor_class, logged_in=is_logged_in())


@app.route('/login', methods=["GET", "POST"])
def render_login_page():
    if is_logged_in():
        return redirect('/')
    print(request.form)
    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = """SELECT id, fname, password FROM users WHERE email = ?"""
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()
        # if given the email is not in the database this will raise an error
        # would be better to find out how to see if the query return an empty resultset
        try:
            userid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+invalid+or+password+incorrect")

        # check if the password is incorrect for that email address

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

        session['email'] = email
        session['userid'] = userid
        session['firstname'] = firstname
        session['cart'] = []
        print(session)
        return redirect('/')

    return render_template('login.html', logged_in=is_logged_in())


@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    if is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters+or+more')

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DB_NAME)

        query = "INSERT INTO users (id, fname, lname, email, password) " \
                "VALUES(NULL,?,?,?,?)"

        cur = con.cursor()  # You need this line next
        try:
            cur.execute(query, (fname, lname, email, hashed_password))  # this line actually executes the query
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+is+already+used')

        con.commit()
        con.close()
        return redirect('/login')

    return render_template('signup.html', logged_in=is_logged_in())


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


if __name__ == '__main__':
    app.run()
