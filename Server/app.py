from flask import Flask
import json 
import cloudpickle as pickle
import base64

from idna import check_label

app = Flask(__name__)

@app.post('/grade_problems/<b64_pickled_student_functions>/<notebook_id_check>/<student_id_check>/<assignment_id>')
def grade_work(b64_pickled_student_functions, notebook_id_check, student_id_check, assignment_id):
	# 5. the server will load the pickled-base64 string (done)
	# 6. the server will grade the answers on the backend. (done)
	# 7. the server responds with graded_assignment that will then be printed (done).

	# step 5
	student_dict = pickle.loads(base64.b64decode(b64_pickled_student_functions.encode()))

	import key
	answer_key = key.Key(f'keys/{assignment_id}.JSON', notebook_id_check, student_id_check)

	# step 6
	graded_assignment = {}
	
	for problem in answer_key.get_problems():
		if problem.get_var_name() in student_dict and problem.get_check_type() == 'Test_Case':
			check_grades = []
			checking_data = problem.get_checking_data()

			n = 0
			n_pass = 0
			for test in checking_data:
				n += 1
				expected_output = test.get_outputs()
				input_dict = test.get_inputs()

				try:
					student_output = student_dict[problem.get_var_name()](*input_dict)

				except:
					check_grades.append('Exception! There was an error with your function contents.')
					continue

				if student_output != expected_output:
					check_grades.append(f'Failed test case {n}. Expected {expected_output} and got {student_output} with inputs {input_dict}.')

				else:
					check_grades.append(f'Passed test case {n}')
					n_pass += 1

			graded_assignment[f'Problem {problem.get_number()}: {(100* n_pass) // n}%'] = check_grades

		elif problem.get_var_name() in student_dict and problem.get_check_type() == 'Equality_Check':
			check_grades = []

			checking_data = problem.get_checking_data()

			n = 0
			n_pass = 0
			for test in checking_data:
				n += 1
				expected_sol = test.get_solution()
				
				try:
					student_output = student_dict[problem.get_var_name()]()

				except:
					check_grades.append('Exception! There was an error with your function contents.')
					continue

				if student_output != expected_output:
					check_grades.append(f'Failed equality test {n}. Expected {expected_sol} and got {student_output}.')

				else:
					check_grades.append(f'Passed equality check {n}')
					n_pass += 1
				
			graded_assignment[f'Problem {problem.get_number()}: {(100 * n_pass) // n}%'] = check_grades

	graded_assignment = json.dumps(graded_assignment)

	# step 7
	return graded_assignment
	

@app.get('/problem_names/<notebook_id_check>/<student_id_check>/<assignment_id>')
def prblem_names(notebook_id_check, student_id_check, assignment_id):
	# instantiates key and gets var_names in list
	import key
	answer_key = key.Key(f'keys/{assignment_id}.JSON', notebook_id_check, student_id_check)

	var_names = {}

	for problem in answer_key.get_problems():
		var_names[str(problem.get_number())] = problem.get_var_name()

	return json.dumps(var_names)

@app.get('/notebook_id/<notebook_id>')
def verify_notebook(notebook_id):
	notebook_id_set = {"001", "002", "003"}
	if notebook_id in notebook_id_set:
		return "Valid notebook"
	else:
		return 'False'

@app.get('/check_id/<student_id>')
def verify_student(student_id):
	student_id_dict = {"001":"Test Student Name", "1":"Bill","2":"Lucy","100":"Mary"}
	if student_id in student_id_dict:
		return student_id_dict[student_id]
	else:
		return 'False'

# Debug mode for local development
if __name__ == "__main__":
	app.run(debug=True)
	pass