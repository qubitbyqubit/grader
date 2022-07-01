class TestCase():
    def __init__(self, inputs: list, output, number : int, assignment_id: int):
        self.inputs = inputs
        self.outputs = output
        self.num = number
        self.id = assignment_id

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

    def get_num(self):
        return self.num

    def get_id(self):
        return self.id

    def __repr__(self):
        return (f'This test case supplies {self.get_inputs} as inputs and has an expected output of {self.get_outputs}.')

class Problem():
    def __init__(self, testcases: list[TestCase], number : int, assignment_id: int):
        self.testcases = testcases
        self.number = number
        self.id = assignment_id

    def get_testcases(self):
        return self.testcases[:]

    def get_number(self):
        return self.number

    def add_tc(self, tc: TestCase):
        if type(tc) != TestCase:
            raise TypeError('You can only add testcases!')

        else:
            testcases = self.get_testcases()
            testcases.append(tc)
            
            self.testcases = testcases

    def __repr__(self):
        return (f'This is problem {self.get_number()} for assignment {self.id} with {len(self.get_testcases())} test case(s)')

class Key():
    def __init__(self, filename: str):
        self.filename = filename

        try:
            data = self.load_information(self.filename)
            self.data = data
            self.id = data['id']
            print(f'Data retrieved and saved successfully.')

        except:
            raise Exception('Could not load the intended file. File not found.')
        
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

        n = 0 # check to see how many problems there are.
        while(True):
            n += 1
            if (f'problem{n}') not in data:
                n -= 1
                break

        if n == 0:
            raise Exception('No problem data found. Please check your JSON file.')
        
        print(f'Found {n} problems.')

        list_prob = []

        for prob_n in range(1,n+1):
            problem_data = data[f'problem{prob_n}']

            m = 0 # check to see how many test cases there are.
            while(True):
                m += 1
                if (f'tc{m}') not in problem_data:
                    m -= 1
                    break

            if m == 0:
                raise Exception('No test case data found. Please check your JSON file.')

            print()
            print(f'Found {m} test cases for problem {prob_n}.')

            prob_tcs = []
            
            for tc_n in range(1,m+1):
                tc_data = problem_data[f'tc{tc_n}']
                tc_inputs = tc_data['input']

                if type(tc_inputs) is str and tc_inputs[0:2] == 'f/':
                    tc_inputs = eval(tc_inputs[2:] + '()')

                elif type(tc_inputs) is list:
                    tc_inputs = self.PARSE_for_func(tc_inputs)

                prob_tcs.append(TestCase(tc_inputs, tc_data['output'], tc_n, self.get_id()))
                print(f'Test Case {tc_n} processed successfully.')

            list_prob.append(Problem(prob_tcs, prob_n, self.get_id()))
            print(f'Problem {prob_n} processed successfully.')

        return list_prob

    def PARSE_for_func(self, list):
        for i in range(len(list)):
            if type(list[i]) is str and list[i][0:2] == 'f/':
                list[i] = eval(list[i][2:] + '()')

            elif type(list[i]) is list:
                list[i] = self.PARSE_for_func(list[i])

        return list
        
    def get_id(self):
        return self.id

    def get_problems(self):
        return self.problems

    def __str__(self):
        return (f'This is the key data for assignment {self.id}')