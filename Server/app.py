from flask import Flask, request
import json 
import pickle
import jsonpickle
app = Flask(__name__)


@app.get('/')
def index():
	return "nothing"

@app.post('/check_answers/')
def check_answers():
	data = request.form['req']
	dic = json.loads(data)
	print(dic)

	response = {
		"response": "Success"
	}

	return json.dumps(response)

@app.get('/notebook_id/<notebook_id>')
def verify_notebook(notebook_id):
	notebook_id_set = {"001", "002", "003"}
	if notebook_id in notebook_id_set:
		# Return json object containing info about the homework
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

