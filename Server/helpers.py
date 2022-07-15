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

def submit_to_canvas(graded_questions):
	# Get Question Scores
	question_scores = {} # Key : Value. prob_num (1 indexed) to prob_score
	for elem in graded_questions:
		prob_num = elem[3] + 1
		question_scores[prob_num] = elem[2]

	return 'Not implemenmted but ready to talk with Canvas'
	
	# Ready to start working with API
	# TODO

def attempt_problem(student_func, test_case):
	#TODO Implement a runtime watcher (in case student code loops forever)
	error_message = None
	try:
		result = student_func(*test_case)
	except Exception as e:
		error_message = f"Exception: {e.message}, Arguments: {e.args}"
	return (result, error_message)

def grade(student_solutions, assignment_key, submit=False):

	grade_responses = []
	points = 0
	
	# check lengths are the same
	assert(len(student_solutions) == len(assignment_key.problem_key))

	# Iterate through the solution key and student problem and construct a grade
	# Response.
	for student_prob, key_prob in zip(student_solutions, assignment_key.problem_key):
		color_dict = {"correct":"g","incorrect":"r"}
		accumulated_points = 0
		reason = ""
		if student_prob["variable_data"] == None:
			# No variable found
			mark = "incorrect"
			reason = f"Unable to find a variable called: {student_prob['variable_name']}"
		else:
			# Valid variable found

			# Test case style of problem
			if key_prob["checking_type"] == "Test_Case":
				# Iterate through the test cases and check equality
				mark = "correct"
				for test_case in key_prob["checking_data"]:
					student_func = student_prob["variable_data"]
					result, error_message = attempt_problem(student_func, tuple(test_case["inputs"]))
					if result == None:
						if error_message == "timeout":
							reason =f"Your solution took too long to run (>1 minute)"
							mark = "incorrect"
						else:
							reason = f"Function failed with error: {error_message}"
							mark = "incorrect"
					else:
						if (result != test_case["output"]):
							
							line = [
							"-"*50, 
							f'Your function ran, but it produced an unexpected result.',
							f'Test Inputs:{tuple(test_case["inputs"])}',
							f'Expected outputs: {test_case["output"]}',
							f'Received outputs: {result}',
							"-"*50]
							reason = ("  \n").join(line)
							mark = "incorrect"
				
					if mark == "correct":
						accumulated_points += 1

			# Equality Check Type
			elif key_prob["checking_type"] == "Equality_Check":
				accumulated_points = 0

				if (student_prob["variable_data"] in key_prob["checking_data"]):
					mark = "correct"
					accumulated_points += 1
				else:
					reason = f"Your solution is not in the answer key set."
					mark = "incorrect"

			# Completion Check Type
			elif key_prob["checking_type"] == "Completion":
				mark = "correct"
				accumulated_points += 1
			else:
				raise Exception("Broken Key")

		# Record grade and remark for a given problem
		if mark == 'incorrect':
			remark = f'Problem {student_prob["problem_number"]} is {mark}: {accumulated_points*1.0} of {key_prob["points"]} points earned!\n{reason}\n{"-"*50}'
		elif mark =='correct':
			remark = f'Problem {student_prob["problem_number"]} is {mark}: {accumulated_points*1.0} of {key_prob["points"]} points earned!\n{"-"*50}'
		
		grade_responses.append((remark, color_dict[mark], accumulated_points, student_prob["problem_number"]))
		points += accumulated_points

	if submit:
		return submit_to_canvas(grade_responses)
		if successful_submit:
			return ("Submitted Successfully!", "g")
		else:
			return ("Error submitting to canvas", "r")
	
	else:
		grade_responses.append((f"Final score: {points*1.0} of {assignment_key.net_points}: {points * 100 /assignment_key.net_points}%", 'b', None, student_prob["problem_number"]))
		return grade_responses