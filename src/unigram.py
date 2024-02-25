import ngram as ngram_fun
import random

file_name = "unigram_table.bin"

# create unigram table, and save it to binary file

def fill_uni_gram(file, uni_gram):
    # read file line by line
    for line in file:

        # pass wiki doc tags
        if line.startswith("<doc") or line.startswith("</doc"):
            continue

        # preprocess line
        syllables = ngram_fun.preprocess(line)
        # print(syllables)
        # exit()

        # add_to_n_gram(uni_gram, syllables, n)
        ngram_fun.fill_gram(uni_gram, syllables, 1)

    # copy unigram to another
    orig_uni_gram = uni_gram.copy()

    # remove all n-grams with count less than 2000
    for key, value in list(uni_gram.items()):
        if value < 2000:
            del uni_gram[key]

    print("size of uni-gram non-zero: ", len(uni_gram))
    # write uni_gram to file as uni_gram_counts.bin
    ngram_fun.write_to_file(uni_gram, "unigram_counts.bin")

    return orig_uni_gram

def uni_gram_prob(uni_gram):
    # <syllable, count> -> <syllable, probability>
    # gt smoothing
    # calculate total count
    total_count = sum(uni_gram.values())

    # calculate frequency of frequencies
    freq_of_freq = {}

    for count in uni_gram.values():
        if count not in freq_of_freq:
            freq_of_freq[count] = 0
        freq_of_freq[count] += 1

    print("size of freq_of_freq: ", len(freq_of_freq))

    # calculate smoothed probabilities
    smoothed_uni_gram = {}
    for key, count in uni_gram.items():
        if count + 1 in freq_of_freq:
            smoothed_count = (count + 1) * freq_of_freq[count + 1] / freq_of_freq[count]
        else:
            smoothed_count = count
        smoothed_uni_gram[key] = smoothed_count / total_count

    return smoothed_uni_gram

def generate_random_sentence_unigram(uni_gram):
    # start with a random syllable
    current_syllable = random.choice(list(uni_gram.keys()))
    sentence = current_syllable
    dot_count = 0

    # senerate the rest of the sentence
    while not sentence.endswith(('.', '!', '?')) and len(sentence.split()) < 100:
        # get the next syllable
        next_syllables = sorted([(k, v) for k, v in uni_gram.items()], key=lambda x: x[1], reverse=True)[:5]
        
        # if there are no next syllables, break the loop
        if not next_syllables:
            break

        # choose the next syllable with weighted probabilities
        syllables, probabilities = zip(*[(k, v) for k, v in next_syllables])
        # print("syllables: ", syllables)

        next_syllable = random.choices(syllables, weights=probabilities, k=1)[0]

        # prevent adding spaces and dots consecutively
        if sentence.endswith(' ') and next_syllable == ' ' or sentence.endswith('.') and next_syllable == '.':
            continue

        # if next syllable is dot, increment dot_count
        if next_syllable == '.':
            dot_count += 1
            
        # add the next syllable to the sentence
        # if dot_count is not 3, do not add next syllable
        if dot_count != 3 and next_syllable != '.' or dot_count == 5 and next_syllable == '.':
            sentence += next_syllable

    return sentence

def create_unigram():

    file = open(ngram_fun.corpus_name, "r", encoding="utf-8")

    # create table from turkish syllabes
    uni_gram = ngram_fun.turkish_syllabes()

    # # write turkish syllabes to file
    # ngram_fun.write_to_file_txt(uni_gram, "turkish_syllabes.txt")
    # exit()

    uni_gram = fill_uni_gram(file, uni_gram)

    print("size of uni-gram table: ", len(uni_gram))
    print("calculating probabilities of uni-gram table...")

    uni_gram = uni_gram_prob(uni_gram)

    # write uni-gram table to file txt
    ngram_fun.write_to_file_txt(uni_gram, "uni_gram_table.txt")

    # write uni-gram table to file bin
    ngram_fun.write_to_file(uni_gram, file_name)



