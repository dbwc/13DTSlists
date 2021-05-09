from flask import Flask, render_template
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

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
    return render_template('home.html', students=student_list, classes=class_list)


@app.route('/class/<tutor_id>')
def render_class(tutor_id):
    # connect to the database
    con = create_connection(DB_NAME)
    query = "SELECT id, year_level, schl_id, surname, first_name, tutor_id, email" \
            " FROM students WHERE tutor_id=? ORDER BY surname, first_name ASC"
    cur = con.cursor()  # You need this line next
    cur.execute(query, (tutor_id, ))  # this line actually executes the query
    student_list = cur.fetchall()  # puts the results into a list usable in python
    con.close()

    class_list = get_classes()
    return render_template('class.html', students=student_list, classes=class_list)


if __name__ == '__main__':
    app.run()
