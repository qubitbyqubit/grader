import requests
import json
import dill

grader_url = ""

class create_grader:
	def __init__(self, glob, assignmentid, student_id):
		self.glob = glob
		self.assignment_id = assignmentid
		self.student_id = student_id
		
		# check to see if a valid notebook
		r = requests.get(f"http://127.0.0.1:5000/notebook_id/{assignmentid}")
		valid_notebook_id  = (r.text == "valid notebook")
		
		if valid_notebook_id:
			print("Grader ready!")
		else:
			print(f"Error with grader")


	def __call__(self):
		# This is run when answers should be checked
		# TODO

		# what needs to happen: 1. we will use a get request to get how many probems there are in this assignment and what their var names are. 
		# 						2. we will pass self.glob and create a new dict of ONLY the assignment's problems as provided by the student.
		#						3. the student dictionary will then be pickled and decoded
		#						4. the decoded pickled obj will be sent via a post request to the server.
		#						5. the server will encode the object and depickle it.
		#						6. the server will grade the answers.
		
		raise NotImplementedError('Josh is still working on this. I have an idea.')


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

	def get_assignid(self):
		return self.assignment_id

	def get_student_id(self):
		return self.student_id