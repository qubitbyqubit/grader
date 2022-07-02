class Test_Case():
    def __init__(self, inputs, output):
        self.inputs = inputs
        self.outputs = output

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

    def __repr__(self):
        return (f'This test case supplies {self.get_inputs} as inputs and has an expected output of {self.get_outputs}.')

class Equality_Check():
    def __init__(self, solution):
        self.solution = solution
    
    def get_solution(self):
        return self.solution

    def __repr__(self):
        return (f'This equality check has an expected output of {self.get_solution()}.')

class Problem():
    def __init__(self, checking_data: list, number: int, check_type: str, var_name: str):
        self.checking_data = checking_data
        self.number = number
        self.check_type = check_type
        self.var_name = var_name

    def get_checking_data(self):
        return self.checking_data[:]

    def get_number(self):
        return self.number

    def get_check_type(self):
        return self.check_type
    
    def get_var_name(self):
        return self.var_name

    def __repr__(self):
        return (f'This is problem {self.get_number()} with function name {self.get_var_name()}, with {len(self.get_checking_data())} {self.get_check_type()}(s).')

class Key():
    def __init__(self, filename: str, valid_assignment_id, valid_student_id):
        self.filename = filename
        self.valid_student_id = valid_student_id
        self.valid_assignment_id = valid_assignment_id

        try:
            data = self.load_information(self.filename)
            self.data = data
            self.nb_id = data['notebook_id']
            print(f'Data retrieved and saved successfully.')

        except:
            raise Exception('Could not load the intended key.')
        
        try:
            key_data = self.process_data(data)
            self.problems = key_data

        except:
            raise Exception('Unable to process data at this time.')

        print()
        print(f'Key for assignment {self.get_id()} generated.')
        

    def load_information(self, filename: str) -> list:
        import json
        
        with open(filename, 'r') as file:
            print(f'Opening file with path: {filename}')
            data = json.load(file)
        
        return data

    def process_data(self, data: dict):
        print('Now processing data.')
        list_problems = []

        for problem in data['problems']:
            
            if problem['checking_type'] == 'Test_Case':
                list_tc = []

                for test_case in problem['checking_data']:
                    list_tc.append(Test_Case(test_case['input'],test_case['output']))

                list_problems.append(Problem(list_tc, problem["problem_number"], problem['func_type'], problem['func_name']))

            elif problem['checking_type'] == 'Equality_Check':
                list_ec = []

                for equality_check in problem['checking_data']:
                        list_ec.append(Equality_Check(equality_check['solution']))

                list_problems.append(Problem(list_ec, problem["problem_number"], problem['checking_type'], problem['func_name']))

        print('Data processed.')
        return list_problems

    def get_problems(self):
        return self.problems

    def __str__(self):
        return (f'This is the key data for assignment {self.nb_id}')