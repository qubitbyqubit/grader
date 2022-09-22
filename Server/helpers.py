from canvas import submit_to_canvas

from email import contentmanager
from itertools import accumulate
import cloudpickle as pickle
import base64
import os
from numpy import greater 
import pandas as pd
import json

def structure_api(student_id, notebook_id, metadata, problems):
	api_dict = {
	"notebook_id" : notebook_id,
	"student_id" : student_id,
	"metadata": metadata,
	"problems":problems
	}
	return api_dict

def verify_student(user_id):
	df = pd.read_csv("student_data/canvas_student_data.csv")
	try:
		row = df[df['user_id'].str.contains(user_id)]
		first_name = row.iloc[0]['first_name']
		last_name = row.iloc[0]['last_name']
		name = f"{first_name} {last_name}"
	except:
		name = None
	return name

class get_assignment_key():
	def __init__(self, notebook_id):
		path_slug = "keys"
		if not os.path.exists(f"{path_slug}/{notebook_id}.JSON"):
			self.exists = None
		else:
			self.exists = True
			self.id = notebook_id
			try:
				with open(f"{path_slug}/{notebook_id}.JSON", 'r') as file:
					self.key_dict = json.load(file)
			except:
				raise Exception("Unable to open answer key")
			self.name = self.key_dict["notebook_name"]            
			self.expected_problems = self.load_problems()
			self.problem_key = self.key_dict["problems"]
			self.net_points = self.key_dict["net_points"]
			self.quiz_id = self.key_dict["quiz_id"]
			self.course_id = self.key_dict["course_id"]
			self.access_code = self.key_dict["access_code"]
			
	def load_problems(self):
		expected_problems = []
		for count, problem in enumerate(self.key_dict["problems"]):
			problem_struct = { 
				"problem_number": count,
				"variable_name": problem["func_name"],
				"variable_data": None,
				"grade_response": None
			  }
			expected_problems.append(problem_struct)
		return expected_problems

def attempt_problem(student_func, test_case):
	#TODO Implement a runtime watcher (in case student code loops forever)
	error_message = None
	try:
		result = student_func(*test_case)
	except Exception as e:
		result = None
		error_message = f"Runtime Error \n Exception: {e.message}, Arguments: {e.args}"
	# for future runtime watcher
	if False:
		error_message = f"Timeout Error. Your solution took too long to run (>2 minutes)"
	return (result, error_message)


def grade_test_case(student_prob, key_prob):
	response = ""
	for num, test_case in enumerate(key_prob["checking_data"]):
		student_func = student_prob["variable_data"]
		result, error_message = attempt_problem(student_func, tuple(test_case["inputs"]))
		if result == None:
			response += f'Failed on Test Case {num}'
			response += f"Function failed with error: {error_message}\n"
			return (0, (response, "r"))
		elif (result != test_case["output"]):
			line = [
			"-"*50,
			f'Failed on Test Case {num}'
			f'Your function ran, but it produced an unexpected result.',
			f'Test Inputs:{tuple(test_case["inputs"])}',
			f'Expected outputs: {test_case["output"]}',
			f'Received outputs: {result}',
			"-"*50]
			response += ("  \n").join(line)
			return (0, (response, "r"))
		else:
			response += f"\tPassed Test Case {num}!\n"
	return (1, (response, "g"))

def grade_equality_check(student_prob, key_prob):
	if (student_prob["variable_data"] in key_prob["checking_data"]):
		return (1, ("Correct!", "g"))
	else:
		return (0, ("Your solution is not in the answer key set.", "g"))


def grade(student_solutions, assignment_key):
	scores, grade_responses = [], []	
	# check lengths are the same
	assert(len(student_solutions) == len(assignment_key.problem_key))
	# Iterate through the student problems and the key problems 
	for student_prob, key_prob in zip(student_solutions, assignment_key.problem_key):
		comment = (f"Checking Question {key_prob['problem_number']}", "")
		grade_responses.append(comment)
		if student_prob["variable_data"] == None:
			# No variable found
			score, gr = 0, (f"Unable to find a variable called: {student_prob['variable_name']}", "r")
		else:
			# Determine checking type
			if key_prob["checking_type"] == "Test_Case":
				score, gr = grade_test_case(student_prob, key_prob)
			elif key_prob["checking_type"] == "Equality_Check":
				score, gr = grade_equality_check(student_prob, key_prob)
			else:
				score, gr = 0, (f"Server Error: Unknown check type: {key_prob['checking_type']}", '')
		scores.append(score) 
		grade_responses.append(gr)

	return (scores, grade_responses)
