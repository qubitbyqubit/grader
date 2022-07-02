from flask import Flask, request
import json 
import pickle
import base64

app = Flask(__name__)

example_return = {"notebook_id": True, 
  "student_id": True, 
  "problems": [
    {"problem_number": 1, 
      "variable_name": "var1", 
      "checking_type": "test_case", 
      "checking_data": [
        {"input": "III", "output": 3}, 
        {"input": "LVIII", "output": 58}, 
        {"input": "MCMXCIV", "output": 1994}]
    }, 
    {"problem_number": 2, 
      "variable_name": "var2", 
      "checking_type": "equality_check", 
      "checking_data": [
        {"solution": ["this", "is", "one", "solution"]}, 
        {"solution": ["this", "is", "another", "solution"]}]
    }
    ]
}

@app.post('/<notebook_id>/<student_id>')
def index(notebook_id, student_id):
	student_id_dict = {"0":"John", "1":"Bill","2":"Lucy","100":"Mary"}
	notebook_id_set = {"001", "002", "003"}
	valid_student = (student_id in student_id_dict)
	valid_notebook = (notebook_id in notebook_id_set)
	data = json.dumps(example_return)
	return data

@app.post('/check_answers/<assignment_id>/<pickled_globals>')
def check_answers(assignment_id, pickled_globals):

	# instantiates key
	import key
	answer_key = key.Key(f'keys/{assignment_id}.JSON')

	import dill
	return pickled_globals.encode('ISO-8859-1')

	return globals_dict


	return 'Loaded key, globals were deserialized, and logic ready for comparing student data with key.'
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
		# Return json object containing assignment information.
		return "valid notebook"
	else:
		return "invalid notebook"

@app.get('/check_id/<student_id>')
def verify_student(student_id):
	student_id_dict = {"0":"John", "1":"Bill","2":"Lucy","100":"Mary"}
	if student_id in student_id_dict:
		return student_id_dict[student_id]
	else:
		return

# Debug mode for local development
if __name__ == "__main__":
	app.run(debug=True)