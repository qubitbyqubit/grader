class TestCase():
    def __init__(self, inputs: list, expected_output, number : int, assignment_id: int):
        self.inputs = inputs
        self.outputs = expected_output
        self.num = number
        self.id = assignment_id

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

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
    def __init__(self, filename: str, readable=False):
        self.readable = readable
        DATA = self.load_information(filename)
        self.problems = DATA[0]

    def load_information(self, filename: str) -> list:

        if self.readable:
            print(f'Now processing the answer key with filename {filename}.')

        DATA = [[], None]
        import csv

        with open(filename, newline='') as file:
            if self.readable:
                print(f'File opened.')
            reader = csv.reader(file)
            data = list(reader)

        for i in range(1,len(data)):
            problem_tracker = 0
            
            if self.readable:
                print(f'Now processing {data[i]}.')
            
            if i == 1:
                if self.readable:
                    print(f'Found assignment_id: {data[i][0]}.')

                DATA[1] = data[i][0]
                self.id = data[i][0]

            if data[i][1] != '' and data[i][2] == '1':
                
                if self.readable:
                    print('New Problem detected!')

                problem_tracker += 1

                inputs = data[i][3].split(',')
                output = data[i][4]

                tc = TestCase(inputs, output, data[i][2], self.get_id())
                problem = Problem([tc],data[i][1], self.get_id())

                DATA[0].append(problem)

            elif data[i][1] == '' and data[i][2] != 1:
                if self.readable:
                    print('New TestCase found!')
                inputs = data[i][3].split(',')
                output = data[i][4]

                tc = TestCase(inputs, output, data[i][2], self.get_id())
                
                DATA[0][-1].add_tc(tc)

        if self.readable:
            print(f'Parsing complete.')
            print(f'Did you expect the following? (y,n)')
            print(DATA[0])

            ver = input()

            if ver.lower() != 'y':
                raise Exception('Parsing Unsuccessful. Something went wrong...')

            else:
                print(f'Loading successful. Ending function.')

        return DATA

    def get_id(self):
        return self.id
        
    def __str__(self):
        return (f'This is the key data for assignment {self.id}')