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

def submit_to_canvas(graded_questions, assignment_key, sis_id):
	# Get Question Score Custom Hashes
	question_scores = {} # Key : Value. prob_num (1 indexed) to prob_score
	for elem in graded_questions:
		prob_num = elem[3] + 1
		question_scores[prob_num] = elem[2]

	for i in range(len(question_scores)):
		question_scores[i+1] = hash_canvas(question_scores[i+1])

	#Let's get the quiz question information from canvas and extract all the question ids so we know what we're answering.
	questions = use_canvas_api(f'https://qxq.instructure.com/api/v1/courses/{assignment_key.course_id}/quizzes/{assignment_key.quiz_id}/questions','GET')

	if questions[0] == 200:
		quiz_questions = {} #id : answers
		for question in questions[1]:
   			quiz_questions[question['id']] = question['answers']
	
	else: 
		return questions[1]

	# #Ok so I've got my question ids and answers, im ready to start submitting. 
	# Let's work now on starting a quiz submission session.
	form = {
     	"access_code" : assignment_key.access_code
	}

	quiz_submission = use_canvas_api(f'https://qxq.instructure.com/api/v1/courses/{assignment_key.course_id}/quizzes/{assignment_key.quiz_id}/submissions?as_user_id=sis_user_id:{sis_id}','POST',form, sis_id=sis_id, assignment_key=assignment_key)

	if quiz_submission[0] == 200:
		quiz_submission = quiz_submission[1]

	else:
		return quiz_submission[1]

	#Change scores into a list of str(int) hashes.

	hashed_answers = []

	for problem in graded_questions:
		hashed_answers.append(hash_canvas(problem[2]))

	# ok, let's get some important info from the quiz_submission.

	session_id = None
	attempt = None
	val_token = None

	for session in quiz_submission['quiz_submissions']: 
   		
		if session['quiz_id'] == assignment_key.quiz_id:
			session_id = session['id']
			attempt = session['attempt']
			val_token = session['validation_token']

	canvas_readable = {}

	for answer, question in zip(hashed_answers,quiz_questions): # loop through answers provided by student and the quiz_questions as recorded on canvas.
		selected_ids = [] # store a place to see what answers the student provided
		
		for answer_choice in quiz_questions[question]:
			if answer_choice['text'] in answer:
				selected_ids.append(answer_choice['id'])

		canvas_readable[question] = selected_ids

	# Now, let's answer each question using an augmented for loop. 
	# Note the change in URL because we're adding each answer to our QS session
	for question in canvas_readable:
		
		form = {
			"attempt": attempt,
			"validation_token": val_token,
			"quiz_questions": [{
				"id": question,
				"flagged" : False,
				"answer": canvas_readable[question]
			}],
			'access_code' : assignment_key.access_code
		}
		
		response = use_canvas_api(f'https://qxq.instructure.com/api/v1/quiz_submissions/{session_id}/questions?as_user_id=sis_user_id:{sis_id}','POST',form)[0]

		if response != 200:
			return response[1]

		else:
			pass

	# Ok! We answered the quiz. Let's submit our work!
	form = {
		"attempt" : attempt,
		"validation_token" : val_token,
		"access_code" : assignment_key.access_code
	}

	response = use_canvas_api(f'https://qxq.instructure.com/api/v1/courses/{assignment_key.course_id}/quizzes/{assignment_key.quiz_id}/submissions/{session_id}/complete?as_user_id=sis_user_id:{sis_id}','POST-SUBMIT',form)

	if response == 200:
		return True
	
	else:
		return False

def hash_canvas(score: int):
	private_hash = {
		0 : -2691568277792965992,
		1 : 1395875967255624137,
		2 : 7754571846373957919,
		3 : 6264763353947146257,
		4 : -2016820986130583684,
		5 : 5006457216414624622,
		6 : -2911142595553320317,
		7 : 2384990490830577609,
		8 : -4260945184859472238,
		9 : -4634720110052923544,
		10 : 2429753604653725074
		}
	
	if score == 0:
		return [private_hash[0]]

	else:
		hashes = []

		for i in range(1,score+1):
			hashes.append(str(private_hash[i]))

		return hashes

def attempt_problem(student_func, test_case):
	#TODO Implement a runtime watcher (in case student code loops forever)
	error_message = None
	try:
		result = student_func(*test_case)
	except Exception as e:
		error_message = f"Exception: {e.message}, Arguments: {e.args}"
	return (result, error_message)

def grade(student_solutions, assignment_key, submit=False, sis_id=None):
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
		submit_attempt = submit_to_canvas(grade_responses, assignment_key, sis_id)
		if type(submit_attempt) == bool:
			if submit_attempt == True:
				return ("Submitted Successfully! You may login to Canvas to view your submission.", "g")
			elif submit_attempt == False:
				return ("Error submitting to canvas", "r")

		else:
			return (submit_attempt, "r")
	
	else:
		grade_responses.append((f"Final score: {points*1.0} of {assignment_key.net_points}: {points * 100 /assignment_key.net_points}%", 'b', None, student_prob["problem_number"]))
		return grade_responses

def use_canvas_api(url: str, method: str, form=None, sis_id=None,  assignment_key=None):
	'''
        Inputs: 
            url : str, 'https://...'
            method: str, HTTPS GET/POST and POST-SUBMIT as a string
			form: dict, Data that is needed for the requests to the Canvas API. Defaults to None.

        Outputs:
            json_resp: dict, JSON response from the server loaded a dictionary or str of the error message
    '''

	def get_user_id(sis_id):
		r = requests.get(f'https://qxq.instructure.com/api/v1/accounts/self/users?search_term={sis_id}',headers=headers)
		r = json.loads(r.content.decode('utf-8'))

		for user in r:
			if user['sis_user_id'] == sis_id:
				return user['id']

		return None

	import requests
	# Setup Authorization using GABBIE's Account Token
	headers = {"Authorization": "Bearer " + '18895~DvviabEteMj6Z0pk2Zgddh3LbR5Q82vGW1iqhvE0ZN0nlXQO4O3jNi8TiKnqxrn9'}
	
	# Make Request
	response = None
	if method == "GET":
		response = requests.get(url,headers=headers,json=form)

	elif method == "POST" or method == 'POST-SUBMIT':
		response = requests.post(url,headers=headers,json=form)

	# Handle Response
	if response.status_code == 200 and method != 'POST-SUBMIT':
		return (response.status_code, json.loads(response.content.decode('utf-8')))

	elif response.status_code == 200 and method == 'POST-SUBMIT':
		return response.status_code

	elif response.status_code == 409 and method == "POST" and (sis_id  != None and assignment_key != None):
		# troubleshoot
		user_id = get_user_id(sis_id)

		submissions = requests.get(f'https://qxq.instructure.com/api/v1/courses/{assignment_key.course_id}/quizzes/{assignment_key.quiz_id}/submissions', headers=headers)
		submissions = json.loads(submissions.content.decode('utf-8'))['quiz_submissions']

		matches = None

		for elem in submissions:
			if elem['user_id'] == user_id:
				matches = elem
				break

		if matches['workflow_state'] == 'complete' and elem['attempts_left'] == 0:
			return  (409, 'Code 409: Conflict. No more attempts allowed. Please contact your instructor to allow more attempts.')

		elif matches['workflow_state'] == 'untaken':
			return  (409, 'Code 409: Conflict. Autograder has detected potential cheating!')

	else:
		return (response.status_code, f"There was a {response.status_code} response from Canvas and could not diagnose the problem. Retry or please contact your instructor.")