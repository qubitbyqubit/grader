from flask import Flask
app = Flask(__name__)


@app.get('/')
def index():
	return "nothing"

@app.get('/check_answers/<notebook_id>')
def check_answers(notebook_id):
	# Checking logic here
	print(notebook_id)
	return "this was a post"

@app.get('/notebook_id/<notebook_id>')
def verify_notebook(notebook_id):
	notebook_id_set = {"001", "002", "003"}
	if notebook_id in notebook_id_set:
		return "valid notebook"
	else:
		return "invalid notebook"

@app.get('/check_id/<student_id>')
def verify_student(student_id):
	student_id_dict = {"0":"John", "1":"Bill","2":"Lucy","100":"Mary"}
	if student_id in student_id_dict:
		return student_id_dict[student_id]
	else:
		return None

