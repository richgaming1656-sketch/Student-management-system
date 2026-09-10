from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            course TEXT,
            marks INTEGER
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():

    search = request.args.get("search", "")
    sort = request.args.get("sort", "id")

    allowed_sort = {
        "id": "id DESC",
        "name": "name ASC",
        "marks_high": "marks DESC",
        "marks_low": "marks ASC",
        "age": "age ASC"
    }

    order_by = allowed_sort.get(sort, "id DESC")

    conn = get_db()

    if search:
        students = conn.execute(f"""
            SELECT * FROM students
            WHERE name LIKE ?
            OR course LIKE ?
            ORDER BY {order_by}
        """, (
            f"%{search}%",
            f"%{search}%"
        )).fetchall()
    else:
        students = conn.execute(f"""
            SELECT * FROM students
            ORDER BY {order_by}
        """).fetchall()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    average_marks = conn.execute(
        "SELECT AVG(marks) FROM students"
    ).fetchone()[0]

    highest_marks = conn.execute(
        "SELECT MAX(marks) FROM students"
    ).fetchone()[0]

    lowest_marks = conn.execute(
        "SELECT MIN(marks) FROM students"
    ).fetchone()[0]

    pass_count = conn.execute(
        "SELECT COUNT(*) FROM students WHERE marks >= 35"
    ).fetchone()[0]

    fail_count = conn.execute(
        "SELECT COUNT(*) FROM students WHERE marks < 35"
    ).fetchone()[0]

    top_students = conn.execute("""
        SELECT * FROM students
        ORDER BY marks DESC
        LIMIT 3
    """).fetchall()

    topper = top_students[0] if top_students else None

    conn.close()

    if average_marks is None:
        average_marks = 0

    if highest_marks is None:
        highest_marks = 0

    if lowest_marks is None:
        lowest_marks = 0

    return render_template(
        "index.html",
        students=students,
        search=search,
        sort=sort,
        total_students=total_students,
        average_marks=round(average_marks, 2),
        highest_marks=highest_marks,
        lowest_marks=lowest_marks,
        pass_count=pass_count,
        fail_count=fail_count,
        top_students=top_students,
        topper=topper
    )


@app.route("/add", methods=["POST"])
def add_student():

    name = request.form["name"]
    age = request.form["age"]
    course = request.form["course"]
    marks = int(request.form["marks"])

    conn = get_db()

    conn.execute("""
        INSERT INTO students
        (name, age, course, marks)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        age,
        course,
        marks
    ))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<int:student_id>")
def edit_student(student_id):

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found", 404

    return render_template(
        "edit.html",
        student=student
    )


@app.route("/update/<int:student_id>", methods=["POST"])
def update_student(student_id):

    name = request.form["name"]
    age = request.form["age"]
    course = request.form["course"]
    marks = int(request.form["marks"])

    conn = get_db()

    conn.execute("""
        UPDATE students
        SET name = ?,
            age = ?,
            course = ?,
            marks = ?
        WHERE id = ?
    """, (
        name,
        age,
        course,
        marks,
        student_id
    ))

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":

    create_table()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
