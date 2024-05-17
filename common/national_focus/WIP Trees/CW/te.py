import os
import re

# Define the input and output file paths
input_file = r"C:\Users\mikeg\Documents\Paradox Interactive\Hearts of Iron IV\mod\Riseofnations\common\national_focus\RON_Bhutan.txt"
output_file = r"C:\Users\mikeg\Documents\Paradox Interactive\Hearts of Iron IV\mod\Riseofnations\common\national_focus\WIP Trees\CW\extracted_ids.txt"

# Define a regular expression pattern to match the desired lines
pattern = re.compile(r'^\s*id\s*=\s*(\S+)')

# Create a list to store the matched ids
ids = []

# Read the input file and extract matching lines
with open(input_file, 'r') as file:
    for line in file:
        if 'focus = {' in line:
            continue
        match = pattern.search(line)
        if match:
            ids.append(match.group(1))

# Write the extracted ids to the output file
with open(output_file, 'w') as file:
    for id in ids:
        file.write(id + '\n')

print(f"Extracted {len(ids)} IDs and saved them to {output_file}")
