import os


root_path = os.getcwd()


def write_json_to_file(file_name, template):
    file_path = os.path.join(root_path, file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)

    open(file_path, 'a').close()

    f = open(file_path, 'w')
    f.write(template.to_json())
    f.close()
