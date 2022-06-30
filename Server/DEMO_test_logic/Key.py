class TestCase():
    def __init__(self, inputs: list, expected_output, number : int, assignment_id: int):
        self.inputs = self.transform_inputs(inputs)
        self.outputs = self.transform_output(expected_output)
        self.num = number
        self.id = assignment_id

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

    def transform_inputs(self, inputs: str):
        if len(inputs) == 0:
            raise Exception('No input variables found.')

        for i in range(len(inputs)):
            if inputs[i].isdigit():
                inputs[i] = int(inputs[i])

            elif inputs[i].lower == 'false':
                inputs[i] == False

            elif inputs[i].lower == 'True':
                inputs[i] == True 

            elif inputs[i][0] == '[' or inputs[i][-1] == ']':
                inputs[i] = inputs[i][1:len(inputs[i])-1].split(',')

            elif inputs[i][0] == '(' or inputs[i][-1] == ')':
                inputs[i] = tuple(inputs[i][1:len(inputs[i])-1].split(','))

            elif inputs[i][0] == '{' or inputs[i][-1] == '}':
                raise TypeError('Dictionary detected. No support available. please choose a new data type.')

            else:
                try:
                    inputs[i] = float(inputs[i])

                except:
                    pass

        return inputs

    def transform_output(self, output):
        if output.isdigit():
            return int(output)

        elif output.lower() == 'false':
            return False

        elif output.lower() == 'true':
            return True 

        elif output[0] == '[' or output[-1] == ']':
            return output[1:len(output)-1].split(',')

        elif output[0] == '(' or output[-1] == ')':
           return tuple(output[1:len(output)-1].split(','))

        elif output[0] == '{' or output[-1] == '}':
            raise TypeError('Dictionary detected. No support available. please choose a new data type.')

        else:
            try:
                output = float(output)

            except:
                print('Sequence of "_" separated strings detected.')

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
            reader = csv.reader(file,delimiter='\t')
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

                inputs = data[i][3].split('_')
                output = data[i][4]

                tc = TestCase(inputs, output, int(data[i][2]), self.get_id())
                problem = Problem([tc],int(data[i][1]), self.get_id())

                DATA[0].append(problem)

            elif data[i][1] == '' and data[i][2] != 1:
                if self.readable:
                    print('New TestCase found!')
                
                inputs = data[i][3].split('_')
                output = data[i][4]

                tc = TestCase(inputs, output, int(data[i][2]), self.get_id())

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