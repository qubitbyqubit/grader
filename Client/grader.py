import requests
import json
import cloudpickle as pickle
import base64

class create_grader:
    
    '''
    The create_grader class creates a check object. This contacts the server to 
    verify the student and notebook id's. It loads in the problem information.
    
    Usage:
        check() - This triggers the __call__ method, which loads the questions
                    from the local scope and sends it over to the server for checking
                    it then prints out all the grading comments
        
        use_api() - This function is built to interface with the 
                    server and handles all HTTP errors
    '''
    
    def __init__(self, glob, notebook_id, student_id):
        self.glob = glob
        self.notebook_id = notebook_id
        self.student_id = student_id
        response = self.use_api(notebook_id, student_id)
        self.verify(response)
        self.problems = response["problems"]
        self.student_name = response["metadata"]["student_name"]
        self.notebook_name = response["metadata"]["notebook_name"]
        print(f'Hello {self.student_name}!')
        self.color_print(f'Grader is ready for assignment {self.notebook_name}.', "g")

    def __call__(self):              
        response = self.use_api(self.notebook_id, self.student_id,
                             method="check")
        self.verify(response)
        for grade_response, color, score, num in response["problems"]:
            self.color_print(grade_response, color)
            
            
    def use_api(self, notebook_id, student_id, method="verify"):
        '''
        Inputs: 
            student_id : Student SISID number
            notebook_id : Notebook unique identifier
            method : API method argument, verify, grade submit. Defaults to verify.

        Outputs:
            returns the JSON response from the server
        '''
        grader_url = "http://127.0.0.1:5000"
        # check if grading or verifying
        try:
            if method == "verify":
                r = requests.get(f'{grader_url}/verify/{notebook_id}/{student_id}')
            elif method in ["check", "submit"]:
                #pickle and base64 would go here
                try: 
                    pickled_problems = pickle.dumps(self.questions())
                    b64pickle = base64.b64encode(pickled_problems).decode('ascii')
                except:
                    raise Exception("Unable to convert homework problems")
                data = json.dumps({ "notebook_id" : self.notebook_id,
                                    "student_id" : self.student_id,
                                    "metadata": None,
                                    "problems": b64pickle})
                r = requests.post(f'{grader_url}/{method}/{notebook_id}/{student_id}',
                                  data={'client_data':data})
            else:
                raise Exception(f"Api method of {method} is not of: ['verify', 'check', 'submit']")
        except:
            raise Exception("Unable to reach grading server, are you connected to the internet?")

        # Error handling:
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception("There was an error with the grading server.")
        
        # Print out based on grading response
    def verify(self, response):
        if response["notebook_id"] == None:
            raise Exception("Invalid Notebook ID")
        if response["student_id"] == None:
            raise Exception("Invalid Student ID")
        return response
    
    def questions(self):
        # Loop through the global scope to find question variables
        for problem in self.problems:
            try:
                problem_data = self.glob[problem["variable_name"]]
            except:
                # Problem has either not been attempted or is not loaded into scope
                problem_data = None
            problem["variable_data"] = problem_data
        return self.problems
        
    def submit(self):
        # Ask Student for their ID number
        given_id = input("Enter your student ID to begin submitting your assignment: ")

        # Verify that the ID number is correct and get the student name for the given ID number
        if given_id == self.student_id:
            confirm = input(f"Confirm you are: {self.student_name} (Y/N)")
            if confirm in ["Y", "y", "Yes", "yes"]:
                response = self.use_api(self.student_id, self.notebook_id, method="submit")
                self.verify(response)
                self.color_print(response['problems'][0],response['problems'][1])
                
            else:
                # Student typed in an incorrect but valid ID number 
                # (possible vulnerability could this be used to search for other students IDs?)
                print("Submit Aborted.")
        else:
            # Invalid Student ID
            print("Student ID not found.")
            
    def color_print(self, text, color):
        if color == "g":
            print('\033[92m' + text + '\033[0m')
        elif color == "r":
            print('\033[91m' + text + '\033[0m')
        elif color == "b":
            print('\033[96m' + text + '\033[0m')
        else:
            print(text)