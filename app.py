from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3


def connect_db():
	conn = sqlite3.connect('database.db')
	return conn


def create_table():
	try:
		conn = connect_db()
		c = conn.cursor()
		conn.execute("""CREATE TABLE students (
			student_id INTEGER PRIMARY KEY NOT NULL,
			name TEXT NOT NULL,
			age TEXT NOT NULL,
			gender TEXT NOT NULL,
			email TEXT NOT NULL,
			phone TEXT NOT NUll
			);
		""")


		c.execute("INSERT INTO students (name, age, gender, email, phone) VALUES ('Badri', '37', 'Male', 'badriesebua@randatmail.com	', '734-554-433')")
		# c.execute("INSERT INTO students (name, age, gender, email, phone) VALUES ('Giorgi', '45', 'Male', 'Giorgi@randatmail.com	', '745-667-234')")
		# c.execute("INSERT INTO students (name, age, gender, email, phone) VALUES ('Ani', '78', 'Female', 'Ani@gmail.com	', '879-766-904')")
		# c.execute("INSERT INTO students (name, age, gender, email, phone) VALUES ('Luka', '56', 'Male', 'Luka@randatmail.com	', '239-346-265')")

		conn.commit()
		print("Student table created successfully")
	except:
		print("Student table creation failed - Maybe there is one already!")
	finally:
		conn.close()


def add_students(students):
	added_students = {}
	try:
		conn = connect_db()
		c = conn.cursor()
		c.execute("INSERT INTO students (name, age, gender, email, phone) VALUES (?, ?, ?, ?, ?)",
			(
			 	students['name'],
				students['age'], 
				students['gender'], 
				students['email'], 
				students['phone'])
			)

		conn.commit()
		added_students = get_student_by_id(c.lastrowid())
	except:
		conn.rollback()
	finally:
		conn.close()

	return added_students


def get_students():
	students = []
	try:
		conn = connect_db()
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		c.execute("SELECT * FROM students")
		rows = c.fetchall()

		for row in rows:
			student = {}
			student["student_id"] = row["student_id"]
			student["name"] = row["name"]
			student["age"] = row["age"]
			student["gender"] = row["gender"]
			student["email"] = row["email"]
			student["phone"] = row["phone"]
			students.append(student)

	except:
		students = []

	return students


def get_student_by_id(student_id):
	student = {}
	try:
		conn = connect_db()
		conn.row_factory = sqlite3.Row 
		c = conn.cursor()
		c.execute("SELECT * FROM students WHERE student_id=?", (student_id,))

		row = c.fetchone()

		student["student_id"] = row["student_id"]
		student["name"] = row["name"]
		student["age"] = row["age"]
		student["gender"] = row["gender"]
		student["email"] = row["email"]
		student["phone"] = row["phone"]

	except:
		student = {}
	
	return student


def delete_student(student_id):
	message = {}
	try:
		conn = connect_db()
		conn.execute("DELETE from students WHERE student_id = ?", (student_id,))
		conn.commit()
		message["status"] = "Student deleted successfully"
	except:
		conn.rollback()
		message["status"] = "Cannot delete student"
	finally:
		conn.close()

	return message


def change_student_data(student):
	changed_student = {}
	try:
		conn = connect_db()
		c = conn.cursor()
		c.execute("UPDATE students SET name=?, age=?, gender=?, email=?, phone=? WHERE student_id=?",  
			(
				student['name'], 
				student['age'], 
				student['gender'], 
				student['email'], 
				student['phone'],
				student['student_id']
			)
		)

		conn.commit()
		changed_student = get_student_by_id(student['student_id'])
	except:
		changed_student = {}
	finally:
		print(changed_student)
		return changed_student


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


"""
http://127.0.0.1:5000/ + 
	1)home/students - GET მეთოდის გამოყენებით ცხრილში არსებული ყველა მონაცემის სიის ამოღება.
	2)home/students/<student_id> - GET მეთოდის გამოყენებით ცხრილში არსებული ინდივიდუალური ელემენტის ამოღება, ამ ელემენტის id-ს გამოყენებით.
	3)home/students/add - POST მეთოდის გამოყენებით, მონაცემთა ბაზის ცხრილში ახალი ელემენტის დამატება.
	4)home/students/change - PUT მეთოდის გამოყენებით, არსებული მონაცემის განახლება ან ახლის დამატება.
	5)home/students/delete/<student_id> - DELETE მეთოდის გამოყენებით, მონაცემთა ბაზის ცრილში შემავალი ელემენტის წაშლა, მისი id-ს გამოყენებით.
""" 

@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html")


@app.route("/home/students", methods=['GET'])
def api_get_students():
	gs = get_students()
	return render_template("students.html", gs=gs)


@app.route('/home/students/add', methods=['POST'])
def api_add_student():
	student = request.get_json()
	return jsonify(add_students(student))


@app.route('/home/students/<student_id>', methods=['GET'])
def api_get_student_by_id(student_id):
	stid = get_student_by_id(student_id)
	return render_template("studentdata.html", stid=stid)


@app.route('/home/students/change', methods=['PUT'])
def api_change_student_data():
	# student = request.get_json()
	return jsonify(change_student_data(student))


@app.route('/home/students/delete/<student_id>',  methods = ['DELETE'])
def api_delete_student(student_id):
    return jsonify(delete_student(student_id))


if __name__ == "__main__":
	create_table()
	app.run(debug=True)