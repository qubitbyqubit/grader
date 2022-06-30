import requests

grader_url = ""

class create_grader:
	def __init__(self,glob, assignmentid):
		self.glob = glob

		# check to see if a valid notebook
		r = requests.get(f"http://127.0.0.1:5000/notebook_id/{assignmentid}")
		valid_notebook_id  = (r.text == "valid notebook")
		if valid_notebook_id:
			print("Grader ready!")
		else:
			print("Error with grader")


	def __call__(self):
		# This is run when answers should be checked
		# TODO
		return print("All questions look good!")


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


