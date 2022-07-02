import requests
import json

grader_url = ""

class create_grader:
	def __init__(self, glob, assignmentid, student_id):
		self.glob = glob
		self.assignment_id = assignmentid
		self.student_id = student_id
		
		# check to see if a valid notebook
		notebook_status = requests.get(f'http://127.0.0.1:5000/notebook_id/{self.get_assignment_id()}').text
		student_status = requests.get(f'http://127.0.0.1:5000/check_id/{self.get_student_id()}').text

		if notebook_status == 'False':
			raise Exception('Internal error.')

		elif student_status == 'False':
			raise Exception('Internal error.')

		else:
			self.notebook_id_check = True
			self.student_id_check = True
			print(f'Hello {student_status}! Grader is ready for assignment {self.get_assignment_id()}.')

	def __call__(self):
		# This is run when answers should be checked
		# How this happens:		1. get request the probem var_name(s) in this assignment from a generated key on the server (done)
		# 						2. we will pass self.glob into a search helper function that will find and create a new dict of ONLY the assignment's problems with method names as provided by the key.
		#						3. the student dictionary will then be pickled and decoded
		#						4. the decoded str will be sent via another post request to the server.
		#						5. the server will encode the object and depickle it.
		#						6. the server will grade the answers ont he backend.
		#						7. the server response, student_grades, will then be printed.
	
		r = requests.get(f'http://127.0.0.1:5000/problem_names/{self.get_notebook_id_check()}/{self.get_student_id_check()}/{self.get_assignment_id()}').text
		expected_problems = json.loads(r)
		
		raise NotImplementedError('Still working on this - Josh')


	def __send_answers(self):
		# TODO
		# Canvas API Integration
		sent = True
		return sent
	
	def __use_api(self, uri):
		# TODO
		try:
			request = requests.get(uri)
			return request
		except:
			raise ValueError("Something went wrong...")


	def submit(self):
		# Ask Student for their ID number
		given_id = input("What is your student ID?")

		# Verify that the ID number exists and get student name for the given ID number
		student_name = self.__use_api(f"{grader_url}/check_id/{given_id}")
		if student_name is not None:
			confirm = input(f"Confirm you are: {student_name} (Y/N)")
			if confirm in ["Y", "y", "Yes", "yes"]:
				valid_id = True
				if self.__send_answers():
					print("Success, Homework is Submitted!")
				else:
					print("Error, please try re-submitting.")
			else:
				# Student typed in an incorrect but valid ID number 
				# (possible vulnerability could this be used to search for other students IDs?)
				print("Submit Aborted")
		else:
			# Invalid Student ID
			print("Student ID not found")

	def get_student_id(self):
		return self.student_id

	def get_assignment_id(self):
		return self.assignment_id

	def get_notebook_id_check(self):
		return self.notebook_id_check

	def get_student_id_check(self):
		return self.student_id_check