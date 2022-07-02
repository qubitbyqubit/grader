from flask import Flask, request
import json 
import pickle
import base64

app = Flask(__name__)

@app.post('/check_answers')
def check_answers(assignment_id, pickled_globals, assign_id_check, student_id_check):
	raise NotImplementedError('I have yet to address this. I am on it though. - Josh')

	# instantiates key
	# import key
	# answer_key = key.Key(f'keys/{assignment_id}.JSON', assign_id_check, student_id_check)

	# import dill
	# return pickled_globals.encode('ISO-8859-1')

	# return globals_dict


	# return 'Loaded key, globals were deserialized, and logic ready for comparing student data with key.'
	# data = request.form['req']
	# decoded_pickle = base64.b64decode(data)
	# new_func = pickle.loads(decoded_pickle)
	# print(type(new_func))

	# dic = json.loads(data)
	# print(dic)

	# response = {
	# 	"response": "Success"
	# }

	# return json.dumps(response)

@app.get('/notebook_id/<notebook_id>')
def verify_notebook(notebook_id):
	notebook_id_set = {"001", "002", "003"}
	if notebook_id in notebook_id_set:
		return "Valid notebook"
	else:
		return 'False'

@app.get('/check_id/<student_id>')
def verify_student(student_id):
	student_id_dict = {"0":"John", "1":"Bill","2":"Lucy","100":"Mary"}
	if student_id in student_id_dict:
		return student_id_dict[student_id]
	else:
		return 'False'

# Debug mode for local development
if __name__ == "__main__":
	app.run(debug=True)