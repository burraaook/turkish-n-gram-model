import pickle

dirname = "ngram_tables/"

# function can be used for reading binary files

def read_binary(filename, num):
    ngram = {}
    with open(dirname + filename, 'rb') as f:
        ngram = pickle.load(f)
    
    # write it to txt file
    file_name = "file" + str(num) + ".txt"
    with open(file_name, 'w') as f:
        for key in ngram:
            f.write(str(key) + " " + str(ngram[key]) + "\n")

read_binary("trigram_table_0.bin", 0)
read_binary("trigram_table_1.bin", 1)
read_binary("trigram_table_2.bin", 2)
read_binary("trigram_table_3.bin", 3)


read_binary("bigram_table.bin", 4)

read_binary("unigram_table.bin", 5)