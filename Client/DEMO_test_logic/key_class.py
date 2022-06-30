class TestCase():
    def __init__(self, inputs: dict, expected_output):
        self.inputs = inputs
        self.outputs = expected_output

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

    def __str__(self):
        return (f'This test case supplies {self.get_inputs} as inputs and has an expected output of {self.get_outputs}.')

class Problem():
    def __init__(self, testcases: list[TestCase], number : int):
        self.testcases = testcases
        self.number = number

    def get_testcases(self):
        return self.testcases

    def get_number(self):
        return self.number

    def __str__(self):
        return (f'This is problem {self.get_number()}.')

class Key():
    def __init__(self, filename: str, assignment_id: int):
        self.problems = self.load_information(filename)
        self.id = assignment_id

    def load_information(self, filename: str):
        # TODO
        raise NotImplementedError

    
