from flask import Flask, request
import json 
import cloudpickle as pickle
import base64
from helpers import grade, verify_student, get_assignment_key, structure_api
from idna import check_label

app = Flask(__name__)

@app.get('/verify/<notebook_id>/<student_id>')
def verify(notebook_id, student_id):
	# This checks for valid student_id and assignment
	student = verify_student(student_id)
	assignment_key = get_assignment_key(notebook_id)

	if (student is None or assignment_key.exists is None):

		data = structure_api(
			student_id=student, 
			notebook_id=assignment_key.exists,
			metadata=None,
			problems=None)
	else:
		data = structure_api(
			student_id=True, 
			notebook_id=True,
			metadata={
				"student_name": student,
				"notebook_name": assignment_key.name},
			problems=assignment_key.expected_problems
			)

	
	return json.dumps(data)

@app.post('/check/<notebook_id>/<student_id>')
def check(notebook_id, student_id):
	student = verify_student(student_id)
	assignment_key = get_assignment_key(notebook_id)

	if (student is None or assignment_key.exists is None):
		
		data = structure_api(
			student_id=student, 
			notebook_id=assignment_key.exists,
			metadata=None,
			problems=None)
	else:
		form_data = json.loads(request.form['client_data'])
		pickled_problems = base64.b64decode(form_data["problems"].encode('ascii'))
		student_solutions = pickle.loads(pickled_problems)
		data = structure_api(
			student_id=True, 
			notebook_id=True,
			metadata={
				"student_name": student,
				"notebook_name": assignment_key.name},
			problems = grade(student_solutions, assignment_key)
			)

	return json.dumps(data)

@app.post('/submit/<student_id>/<notebook_id>')
def submit(student_id, notebook_id):
	student = verify_student(student_id)
	assignment_key = get_assignment_key(notebook_id)
	
	if (student is None or assignment_key.exists is None):
		metadata = None
		graded_problems = None
	else:
		form_data = json.loads(request.form['client_data'])
		pickled_problems = base64.b64decode(form_data["problems"].encode('ascii'))
		b64_pickled = pickle.loads(pickled_problems)

		metadata = {"student_name": student,
					"notebook_name": assignment_key.name},
		graded_problems = grade(b64_pickled, assignment_key, submit=True)

	data = structure_api(student_id=student, 
						 notebook_id=assignment_key.id,
						 metadata=metadata,
						 problems=graded_problems)
	return json.dumps(data)


# Debug mode for local development
if __name__ == "__main__":
	app.run(debug=True)