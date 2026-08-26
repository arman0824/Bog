# run this as per you wish to test the agent in the terminal using any specific tool and function call.


from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file


# this is one example
def main():
    working_directory = "calculator"
    print(run_python_file(working_directory, "main.py", ["3 + 5"]))
main()