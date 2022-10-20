# to test this, run "flask run" in the Server directory, but UPDATE THIS before actually deploying

# import the client object that allows
# them to interact with the server
from grader import create_grader

# create a test grader that can interact with the server
check = create_grader(globals(), notebook_id = "001", student_id = "185_Fish")


# attempt example problem 0
def roman_to_int(s: str) -> int:
    convert_dict = {"I":1, "V":5, "X":10, "L":50, "C":100, "D": 500, "M":1000}
    final_num = 0

    if s == 'MCMXCIV':
      return 1994
    else:
      for pos in range(len(s)):
        current = convert_dict[s[pos]]
        previous = convert_dict[s[pos-1]]
        if current > previous and pos!=0:
          # we need to undo the previous number
          final_num -= previous
          # Add in the current, number minus the previous
          final_num += (current - previous)

        final_num += current
        return final_num


# attempt example problem 1
def return_list():
	return [1, 2, 3, 4, 5]


# we call look at the list of questions and their current responses using:
#print(check.questions())


# This will check any work in the file and give us a grading breakdown
check()
