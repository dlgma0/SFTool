import json
# Read file contents
def read_file(file_name):
    try:
        with open(file_name, mode='r', encoding='utf-8') as file:
            contents = file.read()
            # print(contents)
            return contents
    except IOError:
        print('An error occurred while reading the file.')
    finally:
        if file:
            file.close()


# 定义个function，判断字符串是否有空，用来判断Clarification原来是否有值
def is_blank_str(strs):
    if strs is None or len(strs.strip()) == 0:
        return True
    else:
        return False


# Read file contents line by line and store each line to array.
def read_file_to_array(file_name):
    try:
        with open(file_name, mode='r', encoding='utf-8') as file:
            lines = []
            for line in file:
                if not is_blank_str(line):
                    lines.append(line.strip())
            # print(lines)
            return lines
    except IOError:
        print('An error occurred while reading the file.')
    finally:
        if file:
            file.close()


def read_string_to_array(content):
    final_array = []
    lines = content.split("\n")
    for line in lines:
        if not is_blank_str(line):
            final_array.append(line.strip())
    return final_array


def get_config(file, attr):
    with open(file, 'r') as f:
        # Load the JSON data into a Python dictionary
        data = json.load(f)
    try:
        result = data[attr]
    except KeyError:
        result = None
    return result

#
# myArray = read_file_to_array('TaskFields.txt')
# print(myArray)

# print(read_file('fc.txt'))