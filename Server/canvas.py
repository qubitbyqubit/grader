def submit_to_canvas(graded_questions, assignment_key, sis_id):
	# Get Question Score Custom Hashes
	question_scores = {} # Key : Value. prob_num (1 indexed) to prob_score
	for elem in graded_questions:
		prob_num = elem[3] + 1
		question_scores[prob_num] = elem[2]

	for i in range(len(question_scores)):
		question_scores[i+1] = hash_canvas(question_scores[i+1])

	#Let's get the quiz question information from canvas and extract all the question ids so we know what we're answering.
	# We need the questions object and IDs
	# if these url slugs dont change, they should be hard coded into the use_canvas_api function
	status_code, questions = use_canvas_api(f'https://qxq.instructure.com/api/v1/courses/{assignment_key.course_id}/quizzes/{assignment_key.quiz_id}/questions','GET')

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
	# loop through answers provided by student and the quiz_questions as recorded on canvas.
	for answer, question in zip(hashed_answers, quiz_questions): 
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

		else: # dont need this
			pass

	# Ok! We answered the quiz. Let's submit our work!
	form = {
		"attempt" : attempt,
		"validation_token" : val_token,
		"access_code" : assignment_key.access_code
	}

	response = use_canvas_api(f'https://qxq.instructure.com/api/v1/courses/{assignment_key.course_id}/quizzes/{assignment_key.quiz_id}/submissions/{session_id}/complete?as_user_id=sis_user_id:{sis_id}','POST-SUBMIT',form)


	'''
	This is bad code, response already returns a bool, return (response == 200)
	'''
	if response == 200:
		return True
	
	else:
		return False

	return (response == 200)

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

	'''
	Why is there an edge case for the 0 score?

	for a score for a score of 10 (which should not be possible)
	this would append to a list of hashed values numbers of 1, 2, 3, ... , 10
	'''
	
	if score == 0:
		return [private_hash[0]]

	else:
		hashes = []

		for i in range(1,score+1):
			hashes.append(str(private_hash[i]))

		return hashes

	# Cleaner version:
	hashes = [str(private_hash[i]) for i in score]


def use_canvas_api(url: str, method: str, form=None, sis_id=None,  assignment_key=None):
	'''
		Inputs: 
			url : str, 'https://...'
			method: str, HTTPS GET/POST and POST-SUBMIT as a string
			form: dict, Data that is needed for the requests to the Canvas API. Defaults to None.

		Outputs:
			json_resp: dict, JSON response from the server loaded a dictionary or str of the error message
	'''
	url_slug = "https://qxq.instructure.com/api/v1/courses/"
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