import ngram as ngram_fun
import langdetect
import os

file_name = "turkish_dump"
output_file_name1 = "turkish_dump_input"
output_file_name2 = "turkish_dump_test"
preprocess_file_name = "turkish_dump_preprocessed"

# preprocess file to another file
file = open(file_name, "r", encoding="utf-8")
output_file = open(preprocess_file_name, "w", encoding="utf-8")

for line in file:
    # pass wiki doc tags
    if line.startswith("<") or line.startswith("</"):
        continue

    if line.startswith("!"):
        line = line[1:]

    # if line is empty, skip it
    if line == "\n":
        continue

    # if line is in English, skip it
    try:
        lan = langdetect.detect(line)
        if lan == "en":
            continue
    except:
        # print("error: ", line)
        continue

    # preprocess line
    syllables = ngram_fun.preprocess(line)
    # directly concatenate syllables
    line = "".join(syllables)
    output_file.write(line + "\n")
    
file.close()
output_file.close()


# read file
file = open(preprocess_file_name, "r", encoding="utf-8")

n = 95
m = 5

# calculate total number of lines
total_lines = sum(1 for line in file)
file.seek(0)  # reset file pointer to the beginning

# calculate number of lines for each output file
n_lines = total_lines * n // 100
m_lines = total_lines - n_lines

# create output files
output_file1 = open(output_file_name1, "w", encoding="utf-8")
output_file2 = open(output_file_name2, "w", encoding="utf-8")

# write to output files
for i, line in enumerate(file):
    if i < n_lines:
        output_file1.write(line)
    else:
        output_file2.write(line)

# close files
file.close()
output_file1.close()
output_file2.close()
