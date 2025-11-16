# With the function in this file, All URIs are formatted to the same format for namespace handling. (Preprocessing step)
import os

def format_kg_for_namespaces(input_file, intermediate_file):
    processed_lines = []
    with open(input_file, 'r') as file:
        for line in file:
            parts = line.strip().split()
            new_parts = []
            for part in parts:
                if part.startswith('<http://'):
                    if '#' not in part:
                        last_slash_index = part.rfind('/')
                        if last_slash_index > 0 and part[last_slash_index - 1] != '<' and '>' in part[last_slash_index:]:
                            new_part = part[:last_slash_index] + '#' + part[last_slash_index + 1:]
                        else:
                            new_part = part
                    else:
                        new_part = part
                else:
                    new_part = part
                new_parts.append(new_part)
            processed_line = ' '.join(new_parts) + '\n'
            processed_lines.append(processed_line)

    intermediate_dir = os.path.dirname(intermediate_file)
    if not os.path.exists(intermediate_dir):
        os.makedirs(intermediate_dir)

    with open(intermediate_file, 'w') as file:
        file.writelines(processed_lines)



def convert_hashes_to_slashes(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = [line.replace('#', '/') for line in lines]

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)