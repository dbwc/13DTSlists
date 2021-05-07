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

    return render_template('home.html', students=student_list)


if __name__ == '__main__':
    app.run()
