from functions.get_files_info import get_files_info


def main():
    working_dir = "Calculator"
    root_contents = get_files_info(working_dir)
    print (root_contents)
    pkg_contents = get_files_info (working_dir, "pkg")
    print (pkg_contents)
    pkg_contents = get_files_info (working_dir, "/bin")
    print (pkg_contents)
    pkg_contents = get_files_info(working_dir, "../")
    print (pkg_contents)

main()